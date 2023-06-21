import os
import json
import allure
import pytest
import jsonpath
from pprint import pformat
from duba.api.user import login_fortest_api, tourist_login_api
from duba.api.other import apollo_data_api
from duba.api.token import server_id_config_api
import duba.dubalib as dubalib
from duba.config import data_source
from duba.constants import (PayType, PayTypeInfo, ProductType, ProductTypeInfo, VipPaySetting, 
    VipPaySettingInfo, VipType, StatusCode, ServerHost, UserFirstOrderState,
    Pay_Settings_Show_Name,SHOW_KEYS_APOLLO,SHOW_KEYS_IF,SHOW_KEYS_DEVICE)
from interface_common import tcweblib
from interface_common.mongodb_operate import MongoDBOperate as mongdb
from interface_common.logger import logger
from interface_common.yaml_reader import YamlReader

"""
毒霸项目共用fixture
"""


def pytest_generate_tests(metafunc):
    # 获取命令行参数中测试用例配置
    case_config_str = metafunc.config.getoption("--caseconfig")
    if case_config_str is None:
        return
    case_config_data = json.loads(case_config_str)

    # 获取命令行参数中测试服地址
    test_server = metafunc.config.getoption("--testserver")

    # 测试用例函数地址
    node_id = metafunc.definition.nodeid
    node_name = node_id.split("/")[-1:][0]
    case_path = None

    in_case_config = False
    for case_config_key in case_config_data:
        case_config_name = os.path.split(case_config_key)[-1:][0]
        case_config_path = case_config_key.split(case_config_name)[0]
        # 匹配当前运行的用例是否存在参数配置
        if node_name.startswith(case_config_name):
            case_path = case_config_path + case_config_name
            in_case_config = True
            break
    if not in_case_config:
        logger.info("未找到 {0} 在测试用例配置参数中相关信息，caseconfig = \n{1}".format(node_id, pformat(case_config_data)))
        return

    # 获取配置参数中用例对应的yaml文件，并读取相关配置信息
    yaml_path = case_config_data[case_path]
    yaml_data = YamlReader.read_yaml(yaml_path)
    yaml_params = yaml_data["params"]

    if test_server:
        logger.info(f"检测到 testserver 参数，创建帐号、用户、支付相关接口地址改为：{test_server}")
        for origin_key in ['account_origin', 'user_origin', 'pay_origin']:
            if yaml_params.get(origin_key):
                yaml_params[origin_key] = test_server

    # 遍历用例涉及的fixture函数，使用配置信息中的参数值替换fixture的入参
    fixture_names = metafunc.fixturenames
    for fixture in fixture_names:
        # product_data fixture
        if fixture == "product_data" and "product_type" in yaml_params:
            product_type_list = yaml_params["product_type"]
            product_data_params = []
            for product_type in product_type_list:
                try:
                    product_type_item = ProductType[product_type]
                except Exception as e:
                    logger.exception("[conftest]ProductType[%s] error" % product_type)
                    raise e
                else:
                    product_data_params.append(product_type_item)

            # product_type 参数值为空时，设置为默认参数
            if len(product_data_params) == 0:
                product_data_params = ProductTypeInfo.keys()

            try:
                # product_data fixture 参数化
                metafunc.parametrize("product_data", product_data_params, indirect=True)
            except Exception as e:
                logger.exception("product_data parametrize error")
                raise e

        elif fixture == "get_pay_type_data" and "pay_type" in yaml_params:
            pay_type_list = yaml_params["pay_type"]
            pay_type_params = []
            for pay_type in pay_type_list:
                try:
                    pay_type_item = PayType[pay_type]
                except Exception as e:
                    logger.exception("[conftest]PayType[%s] error" % pay_type)
                    raise e
                else:
                    pay_type_params.append(pay_type_item)

            # pay_type 参数值为空时，设置为默认参数
            if len(pay_type_params) == 0:
                pay_type_params = [PayType.WECHAT_QRCODE]  # 目前服务端仅Mock了微信扫码支付的类型

            try:
                # get_pay_type_data fixture 参数化
                metafunc.parametrize("get_pay_type_data", pay_type_params, indirect=True)
            except Exception as e:
                logger.exception("get_pay_type_data parametrize error")
                raise e

        elif fixture in ["get_apollo_coin_setting", "get_apollo_user_token_setting",
                         "get_apollo_user_info_setting","get_apollo_settings_config"] and "user_origin" in yaml_params:
            user_origin = yaml_params["user_origin"]
            # user_origin 参数值为空时，设置为默认参数
            if not user_origin:
                user_origin = ServerHost.DEV1.value

            try:
                # fixture 参数化
                metafunc.parametrize(fixture, [user_origin], indirect=True)
            except Exception as e:
                logger.exception(f"{fixture} parametrize error")
                raise e

        elif fixture == "create_vip_account" and "user_identity" in yaml_params:
            account_origin = yaml_params["account_origin"]
            if not account_origin:
                account_origin = ServerHost.DEV1.value

            user_identity_list = yaml_params["user_identity"]
            user_identity_params = []
            for user_identity in user_identity_list:
                try:
                    user_identity_item = VipType[user_identity]
                except Exception as e:
                    logger.exception("[conftest]VipType[%s] error" % user_identity)
                    raise e
                else:
                    user_identity_params.append(user_identity_item)

            # user_identity 参数值为空时，设置为默认参数
            if len(user_identity_params) == 0:
                user_identity_params = VipType

            # 用户首单优惠状态
            user_first_order_state_list = [UserFirstOrderState.FIRST_ORDER.name]  # 默认创建用户时有首单优惠状态
            if "user_first_order_state" in yaml_params:  # 有首单优惠配置时读取配置信息
                user_first_order_state_list = yaml_params["user_first_order_state"]

            user_first_order_state_params = []
            for user_first_order_state in user_first_order_state_list:
                try:
                    user_first_order_state_item = UserFirstOrderState[user_first_order_state]
                except Exception as e:
                    logger.exception("[conftest]UserFirstOrderState[%s] error" % user_first_order_state)
                    raise e
                else:
                    user_first_order_state_params.append(user_first_order_state_item)

            # user_first_order_state 参数值为空数组时，设置为默认参数
            if len(user_first_order_state_params) == 0:
                user_first_order_state_params = UserFirstOrderState

            # 根据会员类型 m 和用户首单优惠状态 n，组合成 m * n 种fixture参数
            fixture_params = []
            for user_identity_param in user_identity_params:
                for user_first_order_state_param in user_first_order_state_params:
                    fixture_params.append((account_origin,user_identity_param, user_first_order_state_param))

            try:
                # create_vip_account fixture 参数化
                metafunc.parametrize("create_vip_account", fixture_params, indirect=True)
            except Exception as e:
                logger.exception("create_vip_account parametrize error")
                raise e

        elif fixture == "create_vip_account_v3" and "user_identity" in yaml_params:
            account_origin = yaml_params["account_origin"]
            fake_pay_origin = yaml_params["fake_pay_origin"]
            if not account_origin:
                account_origin = ServerHost.DEV1.value

            user_identity_list = yaml_params["user_identity"]
            user_identity_params = []
            for user_identity in user_identity_list:
                try:
                    user_identity_item = VipType[user_identity]
                except Exception as e:
                    logger.exception("[conftest]VipType[%s] error" % user_identity)
                    raise e
                else:
                    user_identity_params.append(user_identity_item)

            # user_identity 参数值为空时，设置为默认参数
            if len(user_identity_params) == 0:
                user_identity_params = VipType

            # 根据会员类型 m 和用户首单优惠状态 n，组合成 m * n 种fixture参数
            fixture_params = []
            for user_identity_param in user_identity_params:
                if user_identity_param in (VipType.NON_VIP,VipType.NOTLOGIN):
                    fixture_params.append((account_origin,fake_pay_origin, user_identity_param, 0))
                else:
                    for device_num in SHOW_KEYS_DEVICE:
                        fixture_params.append((account_origin,fake_pay_origin, user_identity_param, device_num))

            try:
                # create_vip_account fixture 参数化
                metafunc.parametrize("create_vip_account_v3", fixture_params, indirect=True)
            except Exception as e:
                logger.exception("create_vip_account_v3 parametrize error")
                raise e

        elif fixture == "create_tourist_account" and "gateway_origin" in yaml_params:
            gateway_origin = yaml_params["gateway_origin"]
            # gateway_origin 参数值为空时，设置为默认参数
            if not gateway_origin:
                gateway_origin = ServerHost.NEWVIP_DEV_GW.value

            try:
                # create_tourist_account fixture 参数化
                metafunc.parametrize("create_tourist_account", [gateway_origin], indirect=True)
            except Exception as e:
                logger.exception("create_tourist_account parametrize error")
                raise e

        elif fixture == "get_server_id_config" and "gateway_origin" in yaml_params:
            gateway_origin = yaml_params["gateway_origin"]
            # gateway_origin 参数值为空时，设置为默认参数
            if not gateway_origin:
                gateway_origin = ServerHost.NEWVIP_DEV_GW.value

            try:
                # get_server_id_config fixture 参数化
                metafunc.parametrize("get_server_id_config", [gateway_origin], indirect=True)
            except Exception as e:
                logger.exception("get_server_id_config parametrize error")
                raise e
        
        elif fixture == "case_config":
            try:
                metafunc.parametrize("case_config", [yaml_data], indirect=True)
            except Exception as e:
                logger.exception("case_config parametrize error")
                raise e

@pytest.fixture(scope="function")
def case_config(request):
    """获取自定义参数caseoption中测试用例配置"""
    return request.param


@pytest.fixture(scope="session")
def product_data(request):
    """获取接口版本"""
    product_type = request.param
    product_info = ProductTypeInfo[product_type]
    yield product_info


@pytest.fixture(scope="session")
def get_pay_type_data(request):
    """
    获取支付类型
    @param request:
    @return:
        paytype: 支付类型枚举成员
        paytype_info: 支付类型对应详细信息
    """
    paytype = request.param
    try:
        paytype_info = PayTypeInfo[paytype]
    except Exception as e:
        logger.error("[conftest]获取支付类型失败 error = {}".format(e))
        paytype_info = None
    assert paytype_info, "[conftest]获取支付类型失败"
    yield paytype, paytype_info


# 会员VIP套餐列表
VIP_PAY_SETTING_LIST = [
    VipPaySetting.VIP_CENTER_ONE_MONTH,
    VipPaySetting.VIP_CENTER_SIX_MONTH,
    VipPaySetting.VIP_CENTER_ONE_YEAR,
    # VipPaySetting.VIP_CENTER_ALL_LIFE  # TODO: 待调试
]


@pytest.fixture(scope="session", params=VIP_PAY_SETTING_LIST)
def get_vip_pay_setting(request):
    """获取会员套餐"""
    vip_pay_setting = request.param
    vip_pay_setting_info = VipPaySettingInfo[vip_pay_setting]
    yield vip_pay_setting_info


@pytest.fixture(scope="function")
def create_tourist_account(request, product_data):
    """创建游客账号"""
    server_host = request.param
    product = product_data["product"]

    if product == ProductType.SDK.value:
        pytest.xfail("毒霸新会员%s 无创建游客接口" % product)

    res = tourist_login_api(server_host, product)

    assert res.status_code == StatusCode.OK.value

    analysis_result = tcweblib.matchd_result(data_source.create_account_res_data, json.loads(res.text))
    assert analysis_result
    allure.attach(str(res.text), '接口返回结果')

    open_id = jsonpath.jsonpath(json.loads(res.text), '$.data.user_info.open_id')[0]
    token = jsonpath.jsonpath(json.loads(res.text), '$.data.token')[0]

    allure.attach("open_id = %s, token = %s" % (open_id, token), "用户信息")
    assert dubalib.check_account(open_id, token)

    yield open_id, token


@pytest.fixture(scope="function")
def create_vip_account(request):
    """
    创建会员账号
    @param request:
    @return:
        open_id: 用户open_id
        token: 用户token
        vip_type: 会员等级枚举成员，例：VipType.NON_VIP
    """
    server_host, vip_type, user_first_order_state = request.param  # 会员等级枚举成员、用户首单状态枚举成员
    if vip_type == VipType.NOTLOGIN:
        yield {
            "open_id": "",
            "token": "",
            "vip_type": vip_type,
            "user_first_order_state": UserFirstOrderState.FIRST_ORDER
        }
        return

    res = login_fortest_api(server_host, vip_type.value, user_first_order_state)
    assert res.status_code == StatusCode.OK.value, "创建会员账号接口请求失败，code=%s" % res.status_code

    res_data = json.loads(res.text)
    open_id = jsonpath.jsonpath(res_data, '$.data.user_info.open_id')[0]
    token = jsonpath.jsonpath(res_data, '$.data.token')[0]
    allure.attach("open_id = %s, token = %s" % (open_id, token), "用户信息")

    check_res = dubalib.check_account(open_id, token)
    assert check_res, "会员账号open_id与token校验失败"

    yield {
        "open_id": open_id,
        "token": token,
        "vip_type": vip_type,
        "user_first_order_state": user_first_order_state
    }

@pytest.fixture(scope="function")
def create_vip_account_v3(request):
    """
    创建会员账号new
    因后端不少场景会校验会员账户的订单信息，所以直接生成的会员用户无法校验通过
    所以改成先生成一个非会员账户，然后购买对应的会员套餐
    @param request:
    @return:
        open_id: 用户open_id
        token: 用户token
        vip_type: 会员等级枚举成员，例：VipType.NON_VIP
    """
    server_host,fake_pay_origin, vip_type, device_num = request.param  # 会员等级枚举成员、用户首单状态枚举成员
    if vip_type == VipType.NOTLOGIN:
        yield {
            "open_id": "",
            "token": "",
            "vip_type": vip_type,
            "device_num": 0,
            "user_first_order_state": UserFirstOrderState.FIRST_ORDER
        }
        return


    server_id = dubalib.create_server_id()

    res = login_fortest_api(server_host, VipType.NON_VIP.value)
    assert res.status_code == StatusCode.OK.value, "创建会员账号接口请求失败，code=%s" % res.status_code

    res_data = res.json()
    open_id = jsonpath.jsonpath(res_data, '$.data.user_info.open_id')[0]
    token = jsonpath.jsonpath(res_data, '$.data.token')[0]
    allure.attach("open_id = %s, token = %s" % (open_id, token), "用户信息")

    check_res = dubalib.check_account(open_id, token)
    assert check_res, "会员账号open_id与token校验失败"

    if vip_type not in (VipType.NON_VIP,VipType.NOTLOGIN):
        # 创建非会员账号，需要找到对应套餐并支付
        pay_result = dubalib.pay_vip_order(server_host,fake_pay_origin, "v2", open_id, token, server_id, vip_type,device_num, 1, PayType.WECHAT_QRCODE.value,
                    0)
        assert pay_result,"创建账号并支付下单失败"
        user_first_order_state = UserFirstOrderState.NON_FIRST_ORDER

    else:
        user_first_order_state = UserFirstOrderState.FIRST_ORDER

    yield {
        "open_id": open_id,
        "token": token,
        "vip_type": vip_type,
        "device_num": device_num,
        "user_first_order_state": user_first_order_state,
        "server_id": server_id,
    }

@pytest.fixture(scope="session")
def get_apollo_pay_setting(request):
    """获取毒霸apollo的pay_settings信息"""
    server_host = request.param

    res = apollo_data_api(server_host, namespace="application", key="pay-settings")
    assert res.status_code == StatusCode.OK.value, "[conftest]获取毒霸apollo的pay_setting信息失败 code=%s" % res.status_code

    res_data = json.loads(res.text)
    pay_setting = jsonpath.jsonpath(res_data, '$.data')[0]

    yield pay_setting


@pytest.fixture(scope="session")
def get_apollo_settings_config(request):
    """获取毒霸apollo的pay_settings_config信息(默认取1517渠道)"""
    server_host = request.param

    res = apollo_data_api(server_host, namespace="pay_settings_config.yaml")
    assert res.status_code == StatusCode.OK.value, "[conftest]获取毒霸apollo的pay_settings_config信息失败 code=%s" % res.status_code

    res_data = json.loads(res.text)
    # 从返回内容中获取1517的配置
    pay_setting = jsonpath.jsonpath(res_data, '$.data.DeviceUpgradeShowByScene.Tryno-1517')[0]
    allure.attach(pformat(f"{pay_setting}"),f"返回内容")

    yield pay_setting


@pytest.fixture(scope="session")
def get_apollo_coin_setting(request):
    """获取毒霸apollo的coin信息"""
    server_host = request.param

    res = apollo_data_api(server_host, namespace="coin.yaml")
    assert res.status_code == StatusCode.OK.value, "[conftest]获取毒霸apollo的coin信息请求失败 code=%s" % res.status_code

    res_data = json.loads(res.text)
    coin_setting = jsonpath.jsonpath(res_data, '$.data')[0]

    yield coin_setting


@pytest.fixture(scope="session")
def get_apollo_user_token_setting(request):
    """获取毒霸apollo的user_token信息"""
    server_host = request.param

    res = apollo_data_api(server_host, namespace="user_token.yaml")
    assert res.status_code == StatusCode.OK.value, "[conftest]获取毒霸apollo的user_token信息请求失败 code=%s" % res.status_code

    res_data = json.loads(res.text)
    coin_setting = jsonpath.jsonpath(res_data, '$.data')[0]

    yield coin_setting


@pytest.fixture(scope="session")
def get_apollo_user_info_setting(request):
    """获取毒霸apollo的user_info信息"""
    server_host = request.param

    res = apollo_data_api(server_host, namespace="user_info.yaml")
    assert res.status_code == StatusCode.OK.value, "[conftest]获取毒霸apollo的user_info信息请求失败 code=%s" % res.status_code

    res_data = json.loads(res.text)
    coin_setting = jsonpath.jsonpath(res_data, '$.data')[0]

    yield coin_setting


@pytest.fixture(scope="session")
def get_forbid_words():
    """获取禁忌词列表"""
    res = mongdb.find_data({
        "data": {
            "Table_Name": "ForbidWords"
        }
    })

    assert res.status_code == StatusCode.OK.value, "获取禁忌词列表失败 code=%d" % res.status_code

    forbid_words = json.loads(res.text)

    yield forbid_words


@pytest.fixture(scope="session")
def get_server_id_config(request, product_data):
    """获取设备限制的配置信息"""
    server_host = request.param
    product = product_data["product"]

    # sdk目前代码不统一，0(普通会员)暂时不适用
    if product == ProductType.SDK.value:
        product = ProductType.V2.value

    res = server_id_config_api(server_host, product)
    assert res.status_code == StatusCode.OK.value, f"[conftest]获取设备限制的配置信息请求失败 code={res.status_code}"

    server_id_limit_config = res.json().get('server_id_limit_config')
    allure.attach(pformat(server_id_limit_config), "设备限制的配置信息")

    yield server_id_limit_config


@pytest.fixture(scope="session",params=Pay_Settings_Show_Name.items())
def get_settings_sences(request):
    """获取毒霸会员套餐场景列表"""
    yield request.param

@pytest.fixture(scope="session",params=SHOW_KEYS_DEVICE)
def get_device_num(request):
    """获取毒霸会员套餐场景列表"""
    yield request.param