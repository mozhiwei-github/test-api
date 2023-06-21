import time
import allure
import json
import jsonpath
import random
from duba.config import data_source
from pprint import pformat
import duba.dubalib as dubalib
from duba.constants import VipTypeInfo, UserLoginType, StatusCode, PaySettingsShow, EntrustSetting, VipType, ProductType
from interface_common.logger import logger
from interface_common import tcweblib
from duba.api.token import server_id_list_api, server_id_unbind_api
from duba.api.user import user_login_api, user_token_api
from duba.cases.test_pay import get_pay_settings_step, pay_step, pay_change_status_step
from duba.cases.test_pay_contract import pay_change_status_step as pay_contract_change_status_step

"""毒霸设备限制 业务逻辑测试"""


@allure.step("{step_name}")
def user_cycle_login_step(step_name, server_host, product, token, login_limit_count, expected_success_res,
                          expected_failure_res, binded_server_id_list, tryno=None, vip_version=None):
    logger.info(step_name)
    allure.attach(str(login_limit_count), "用户最多绑定设备个数")
    allure.attach(pformat(binded_server_id_list), "用户已绑定设备列表")
    # 循环绑定设备至上限
    res_server_ids = []
    for index in range(login_limit_count + 1):
        server_id = dubalib.create_server_id()
        if index < login_limit_count:
            binded_server_id_list.append(server_id)
        # 请求用户登录接口（用户设备绑定）
        res = user_login_api(server_host, product, server_id, UserLoginType.OPEN_ID_AND_TOKEN, token, tryno=tryno,
                             vip_version=vip_version)

        if index == login_limit_count:  # 超出绑定设备上限时的响应结果
            expected_res = expected_failure_res
        else:  # 未超出绑定设备上限时的响应结果
            expected_res = expected_success_res

        # 校验用户登录结果
        res_server_ids = check_user_login_result(res, expected_res, index)

    # 校验已绑定设备id列表
    allure.attach(pformat(binded_server_id_list), "预期已绑定设备id列表")
    assert sorted(res_server_ids) == sorted(binded_server_id_list), "已绑定设备id列表校验失败"

    return binded_server_id_list


def check_user_login_result(res, expected_res, index):
    """
    校验用户登录结果
    @param res: 用户登录接口响应结果
    @param expected_res: 预期结果结构体 ExpectedResult
    @param index: 遍历的索引下标
    @return:
    """
    times = index + 1

    allure.attach(str(expected_res.status_code), f"第{times}次用户设备绑定 预期Http状态码")
    allure.attach(str(res.status_code), f"第{times}次用户设备绑定 实际Http状态码")
    assert res.status_code == expected_res.status_code, f"[test_equipment_restrictions]用户登录接口请求失败 code={res.status_code}"

    res_data = res.json()
    allure.attach(pformat(expected_res.res_data), f"第{times}次用户设备绑定 预期响应结果")
    allure.attach(pformat(res_data), f"第{times}次用户设备绑定 实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "[test_equipment_restrictions]用户登录接口返回值校验失败"

    res_server_ids = jsonpath.jsonpath(res_data, '$..server_id')
    if res_server_ids:
        allure.attach(pformat(res_server_ids), "已绑定设备id列表")
        return res_server_ids
    else:
        return []


@allure.step("{step_name}")
def user_token_step(step_name, server_host, product, open_id, token, server_id_list, expected_success_res,
                    expected_failure_res):
    logger.info(step_name)

    # 循环使用已绑定的server id刷新token
    for index, server_id in enumerate(server_id_list):
        res = user_token_api(server_host, product, open_id, token, server_id)

        check_user_token_result(res, expected_success_res, index, expected_token=token)

    # 使用非绑定的server id刷新token
    random_server_id = dubalib.create_server_id()
    allure.attach(str(random_server_id), "【使用非绑定的server id刷新token】")
    res = user_token_api(server_host, product, open_id, token, random_server_id)

    check_user_token_result(res, expected_failure_res, 0, expected_server_id_list=server_id_list)


def check_user_token_result(res, expected_res, index, expected_token=None, expected_server_id_list=None):
    """
    刷新用户token
    @param res: 刷新用户token接口响应结果
    @param expected_res: 预期结果结构体 ExpectedResult
    @param index: 遍历的索引下标
    @param expected_token: 预期用户token
    @param expected_server_id_list: 预期已绑定设备id列表
    @return:
    """
    times = index + 1

    allure.attach(str(expected_res.status_code), f"第{times}次刷新用户token 预期Http状态码")
    allure.attach(str(res.status_code), f"第{times}次刷新用户token 实际Http状态码")
    assert res.status_code == expected_res.status_code, f"[test_equipment_restrictions]刷新用户token接口请求失败 code={res.status_code}"

    res_data = res.json()
    allure.attach(pformat(expected_res.res_data), f"第{times}次刷新用户token 预期响应结果")
    allure.attach(pformat(res_data), f"第{times}次刷新用户token 实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "[test_equipment_restrictions]刷新用户token接口返回值校验失败"

    if expected_token:
        res_token = jsonpath.jsonpath(res_data, '$.token')[0]
        allure.attach(expected_token, "预期用户token")
        allure.attach(res_token, "实际用户token")

        assert res_token == expected_token, "用户token校验失败"

    if expected_server_id_list:
        res_server_ids = jsonpath.jsonpath(res_data, '$..server_id')
        allure.attach(pformat(expected_server_id_list), "预期已绑定设备id列表")
        allure.attach(pformat(res_server_ids), "实际已绑定设备id列表")

        assert sorted(res_server_ids) == sorted(expected_server_id_list), "已绑定设备id列表校验失败"


@allure.step("{step_name}")
def server_id_list_step(step_name, server_host, product, open_id, token, server_id_list, expected_res):
    logger.info(step_name)
    # 请求获取用户设备绑定列表接口
    res = server_id_list_api(server_host, product, open_id, token)
    # 校验获取用户设备绑定列表响应
    check_server_id_list_result(res, expected_res, server_id_list=server_id_list)


def check_server_id_list_result(res, expected_res, server_id_list=None, unbind_server_id=None):
    """
    校验获取用户设备绑定列表响应
    @param res: 获取用户设备绑定列表接口响应结果
    @param expected_res: 预期结果结构体 ExpectedResult
    @param server_id_list: 预期设备绑定id列表
    @param unbind_server_id: 移除的绑定设备id
    @return:
    """
    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, "[test_equipment_restrictions]获取用户设备绑定列表接口请求失败 code=%d" % res.status_code

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "[test_equipment_restrictions]获取用户设备绑定列表接口返回值校验失败"

    res_server_ids = jsonpath.jsonpath(res_data, '$..server_id')
    if server_id_list:
        allure.attach(pformat(server_id_list), "预期已绑定设备id列表")
        allure.attach(pformat(res_server_ids), "实际已绑定设备id列表")

        assert sorted(res_server_ids) == sorted(server_id_list), "已绑定设备id列表校验失败"

    if unbind_server_id:
        allure.attach(str(unbind_server_id), "移除的绑定设备id")
        allure.attach(pformat(res_server_ids), "已绑定设备id列表")
        assert unbind_server_id not in res_server_ids, "设备id移除校验失败"


@allure.step("{step_name}")
def server_id_unbind_step(step_name, server_host, product, open_id, token, unbind_server_id, expected_unbind_res,
                          expected_list_res):
    logger.info(step_name)
    # 请求移除设备绑定记录接口
    res = server_id_unbind_api(server_host, product, open_id, token, unbind_server_id)
    # 校验移除设备绑定记录响应
    check_server_id_unbind_result(res, expected_unbind_res)

    # 请求获取用户设备绑定列表接口
    server_id_list_res = server_id_list_api(server_host, product, open_id, token)
    # 校验获取用户设备绑定列表响应
    check_server_id_list_result(server_id_list_res, expected_list_res, unbind_server_id=unbind_server_id)


def check_server_id_unbind_result(res, expected_res):
    """校验移除设备绑定记录响应"""
    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, "[test_equipment_restrictions]移除设备绑定记录接口请求失败 code=%d" % res.status_code

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "[test_equipment_restrictions]移除设备绑定记录接口返回值校验失败"


@allure.epic('毒霸设备限制 业务逻辑测试')
class TestEquipmentRestrictions(object):
    @allure.feature(
        '场景：获取会员中心套餐->支付下单->第三方支付->付费会员设备绑定限制->获取升级超级会员套餐->支付下单->第三方支付/支付并签约->超级会员设备绑定限制->会员刷新token限制->获取设备列表->移除绑定设备')
    @allure.story(
        "用例：获取会员中心套餐->支付下单->第三方支付->付费会员设备绑定限制->获取升级超级会员套餐->支付下单->第三方支付/支付并签约->超级会员设备绑定限制->会员刷新token限制->获取设备列表->移除绑定设备")
    @allure.description("""
        Step up:
            1.创建非会员账号
            2.获取设备限制的配置信息
            3.获取apollo配置中的渠道号和客户端版本
            4.获取会员中心套餐
            5.随机选择付费非签约会员套餐下单
            6.第三方支付(Mock)
        step4: 付费会员设备绑定限制
            1.会员用户绑定多个server id直至上限
            2.校验会员绑定设备的上限以及返回绑定server id列表的准确性
        step5: 获取升级超级会员套餐
            1.请求获取升级超级会员套餐接口
            2.校验获取升级超级会员套餐接口返回数据的结构和数值
            3.获取升级超级会员套餐列表
        step6: 支付下单
            1.随机选择超级会员套餐进行支付下单
            2.校验支付下单接口返回数据的结构和数值
            3.获取订单id和签约协议号
        step7: 第三方支付/支付并签约（Mock）
            1.根据订单id和签约协议号进行第三方支付/支付并签约
            2.校验第三方支付/支付并签约接口返回数据的结构和数值
        step8: 超级会员设备绑定限制
            1.会员用户绑定多个server id直至上限
            2.校验会员绑定设备的上限以及返回绑定server id列表的准确性
        step9: 会员刷新token限制
            1.通过绑定的server id列表进行token刷新
            2.校验非绑定server id的刷新结果
        step10: 获取设备列表
            1.请求获取设备列表接口
            2.校验获取设备列表接口返回绑定设备列表信息是否一致
        step11: 移除绑定设备
            1.请求移除绑定设备记录接口
            2.校验设备列表，确认设备移除情况
    """)
    @allure.link("http://apix.kisops.com/project/484/interface/api/15498")
    @allure.title(
        "获取会员中心套餐->支付下单->第三方支付->付费会员设备绑定限制->获取升级超级会员套餐->支付下单->第三方支付/支付并签约->超级会员设备绑定限制->会员刷新token限制->获取设备列表->移除绑定设备 预期成功")
    def test_equipment_restrictions_success(self, product_data, create_vip_account_v3, case_config,
                                            get_server_id_config,
                                            get_apollo_user_token_setting, get_apollo_user_info_setting,
                                            get_pay_type_data):
        pay_origin = case_config["params"]["pay_origin"]
        gateway_origin = case_config["params"]["gateway_origin"]
        fake_pay_origin = case_config["params"]["fake_pay_origin"]

        product = product_data["product"]

        tryno = str(get_apollo_user_info_setting["VipType2to5Compatibility"]["Satisfy"]["MustTryno"])
        vip_version = str(get_apollo_user_token_setting["UserDeviceLimitVipCompatibility"]["LessThanVipVersion"])
        logger.info(f"客户端渠道号tryno={tryno} vip_version={vip_version}")

        # 获取会员账号的 open_id 与 token
        account_info = create_vip_account_v3
        open_id = account_info["open_id"]
        token = account_info["token"]
        # device_num = account_info["device_num"]
        user_vip_type = account_info["vip_type"]
        user_vip_name = VipTypeInfo[user_vip_type]["name"]

        # 创建随机客户端server id
        # server_id = dubalib.create_server_id()

        # 获取支付类型
        pay_type, pay_type_data = get_pay_type_data
        pay_type_value = pay_type.value
        pay_channel = pay_type_data["pay_channel"].value

        # 获取初始用户详细信息
        before_user_info, before_device_info = dubalib.get_user_info(gateway_origin, product, open_id, token,
                                                                     attach_allure=False)
        logger.info(f"用户初始详细信息 user_info = {before_user_info}")
        normal_vip_type = int(before_user_info["vip_type"])
        normal_vip_name = VipTypeInfo[VipType(normal_vip_type)]["name"]
        device_num = before_device_info["device_num"]
        logger.info(f"用户当前会员信息 vip_name = {normal_vip_name} vip_type = {normal_vip_type}")

        # 获取付费会员最多绑定的设备数
        if product == ProductType.SDK.value:
            normal_login_limit_count = get_server_id_config[str(normal_vip_type)]["server_id_limit"]
        else:
            normal_login_limit_count = before_device_info["device_num"]
        logger.info(f"{normal_vip_name}最多绑定设备数：{normal_login_limit_count}")
        if normal_vip_type >= VipType.NORMAL_VIP.value:
            normal_login_limit_count = normal_login_limit_count - 1
            logger.info(f"创建付费时候会员本身已经绑定一个设备号,所以最多绑定设备数减1,最终为{normal_login_limit_count}")

        # step4: 会员设备绑定限制
        binded_server_id_list = [account_info["server_id"]]
        step_4_expected_success_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        step_4_expected_failure_res = data_source.ExpectedResult(StatusCode.OK.value,
                                                                 data_source.token_out_of_limit_res_data)
        normal_server_id_list = user_cycle_login_step(f"step4: {normal_vip_name}设备绑定限制", gateway_origin, product, token,
                                                      normal_login_limit_count, step_4_expected_success_res,
                                                      step_4_expected_failure_res, binded_server_id_list, tryno,
                                                      vip_version)

        # step5: 获取升级超级会员套餐
        if normal_vip_type == VipType.DIAMOND_VIP.value:  # 砖石会员为最高级别会员无法再升级无需测试以下操作
            return

        step_5_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        super_pay_price_settings = get_pay_settings_step("step5: 获取升级超级会员套餐", gateway_origin, product, open_id, token,
                                                         random.choice(normal_server_id_list), step_5_expected_res,
                                                         vip_type=normal_vip_type, device_num=device_num,
                                                         is_upgrade=True)
        # 随机选择一个超级会员套餐
        super_pay_setting = random.choice(super_pay_price_settings)
        super_pay_setting_id = super_pay_setting["id"]
        super_pay_setting_name = super_pay_setting["name"]
        is_entrust_setting = super_pay_setting["is_entrust_setting"]
        logger.info(f"套餐id = {super_pay_setting_id}")
        logger.info(f"套餐名称 name = {super_pay_setting_name}")
        logger.info(f"套餐签约类型 is_entrust_setting = {is_entrust_setting}")

        allure.dynamic.title(
            f'毒霸新会员{product} {user_vip_name}用户 升级{super_pay_setting_name}（超级会员） 使用{pay_type_value}支付')

        # 获取数据库中VIP套餐相关信息
        pay_setting_info = dubalib.get_mysql_pay_setting(super_pay_setting_id)
        setting_vip_type = int(pay_setting_info["vip_type"])  # 套餐等级
        month_length = pay_setting_info["month_length"]  # 套餐月数
        day_length = pay_setting_info["day_length"]  # 套餐天数
        real_day_length = dubalib.get_pay_setting_real_day_length(month_length, day_length)
        logger.info(f"套餐等级 vip_type = {setting_vip_type}")
        logger.info(f"套餐月数 month_length = {month_length}")
        logger.info(f"套餐天数 day_length = {day_length}")
        logger.info(f"实际套餐天数 real_day_length = {real_day_length}")

        # step6: 支付下单
        step_6_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        super_check_result = pay_step("step6: 支付下单", pay_origin, product, open_id, token, random.choice(normal_server_id_list),
                                      super_pay_setting_id, pay_channel, pay_type_value, pay_type_data,
                                      step_6_expected_res, fake_pay_origin, is_upgrade=True)
        super_order_id = super_check_result["order_id"]
        super_contract_id = super_check_result["contract_id"]

        if is_entrust_setting == EntrustSetting.NOT_ENTRUST.value:  # 不可发起纯签约套餐
            # step7: 第三方支付
            step_7_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
            pay_change_status_step("step7: 第三方支付", fake_pay_origin, super_order_id, step_7_expected_res)
        else:  # 可以发起纯签约套餐
            # step7: 支付并签约
            step_7_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
            pay_contract_change_status_step("step7: 支付并签约", fake_pay_origin, super_order_id, step_7_expected_res,
                                            super_contract_id)

        # 等待N秒后查询
        time.sleep(0.5)

        # 获取当前用户详细信息
        super_user_info, super_device_info = dubalib.get_user_info(gateway_origin, product, open_id, token,
                                                                   attach_allure=False)
        logger.info("用户当前详细信息 user_info = %s" % super_user_info)
        super_vip_type = int(super_user_info["vip_type"])
        super_vip_name = VipTypeInfo[VipType(super_vip_type)]["name"]
        logger.info(f"用户当前会员等级 vip_type = {super_vip_type}")
        logger.info(f"用户当前会员名称 vip_name = {super_vip_name}")

        # 获取钻石/超级会员最多绑定的设备数
        if product == ProductType.SDK.value:
            super_login_limit_count = get_server_id_config[str(super_vip_type)]["server_id_limit"]
        else:
            super_login_limit_count = super_device_info["device_num"]
        logger.info(f"{super_vip_name}最多绑定设备数：{super_login_limit_count}")

        remaining_login_limit_count = super_login_limit_count - len(normal_server_id_list)
        logger.info(f"目前剩余可绑定设备数：{remaining_login_limit_count}")

        # step8: 会员设备绑定限制
        step_8_expected_success_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        step_8_expected_failure_res = data_source.ExpectedResult(StatusCode.OK.value,
                                                                 data_source.token_out_of_limit_res_data)
        super_server_id_list = user_cycle_login_step(f"step8: {super_vip_name}设备绑定限制", gateway_origin, product, token,
                                                     remaining_login_limit_count, step_8_expected_success_res,
                                                     step_8_expected_failure_res, normal_server_id_list)

        # step9: 会员刷新token限制
        step_9_expected_success_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        step_9_expected_failure_res = data_source.ExpectedResult(StatusCode.OK.value,
                                                                 data_source.token_out_of_limit_res_data)
        user_token_step("step9: 会员刷新token限制", gateway_origin, product, open_id, token, super_server_id_list,
                        step_9_expected_success_res, step_9_expected_failure_res)

        # step10: 获取设备列表
        step_10_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        server_id_list_step("step10: 获取设备列表", gateway_origin, product, open_id, token, super_server_id_list,
                            step_10_expected_res)

        # step11: 移除绑定设备
        # 随机选择一个待移除的绑定设备id
        if len(super_server_id_list) > 1:
            unbind_server_id = random.choice(super_server_id_list)

            step_11_expected_unbind_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
            step_11_expected_list_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
            server_id_unbind_step("step11: 移除绑定设备", gateway_origin, product, open_id, token, unbind_server_id,
                                  step_11_expected_unbind_res, step_11_expected_list_res)
        else:
            logger.info(f"目前绑定设备数为0，不做移除绑定设备测试")

    @allure.feature('场景：【兼容外网版本】会员设备绑定限制->会员刷新token限制->获取设备列表->移除绑定设备')
    @allure.story("用例：【兼容外网版本】会员设备绑定限制->会员刷新token限制->获取设备列表->移除绑定设备")
    @allure.description("""
            Step up:
                1.创建不同类型的会员账号
                2.获取设备限制的配置信息
                3.获取apollo配置中的外网版本会员最大设备绑定数
            step1: 会员设备绑定限制
                1.会员用户绑定多个server id直至上限
                2.校验会员绑定设备的上限以及返回绑定server id列表的准确性
            step2: 会员刷新token限制
                1.通过绑定的server id列表进行token刷新
                2.校验非绑定server id的刷新结果
            step3: 获取设备列表
                1.请求获取设备列表接口
                2.校验获取设备列表接口返回绑定设备列表信息是否一致
            step4: 移除绑定设备
                1.请求移除绑定设备记录接口
                2.校验设备列表，确认设备移除情况
        """)
    @allure.link("http://apix.kisops.com/project/484/interface/api/15498")
    @allure.title("【兼容外网版本】会员设备绑定限制->会员刷新token限制->获取设备列表->移除绑定设备 预期成功")
    def test_extranet_equipment_restrictions_success(self, product_data, create_vip_account, case_config,
                                                     get_apollo_user_token_setting):
        gateway_origin = case_config["params"]["gateway_origin"]

        product = product_data["product"]

        # 获取外网版本会员设备绑定限制
        max_bind_num = get_apollo_user_token_setting["UserDeviceLimitVipCompatibility"]["MaxNum"]
        logger.info(f"外网版本会员最多绑定设备数：{max_bind_num}")

        # 获取会员账号的 open_id 与 token
        account_info = create_vip_account
        open_id = account_info["open_id"]
        token = account_info["token"]
        user_vip_type = account_info["vip_type"]
        user_vip_name = VipTypeInfo[user_vip_type]["name"]

        allure.dynamic.title(f'【兼容外网版本】毒霸新会员{product} {user_vip_name}用户')

        # step1: 会员设备绑定限制
        binded_server_id_list = []
        step_1_expected_success_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        step_1_expected_failure_res = data_source.ExpectedResult(StatusCode.OK.value,
                                                                 data_source.token_out_of_limit_res_data)
        super_server_id_list = user_cycle_login_step(f"step1: 会员设备绑定限制", gateway_origin, product, token,
                                                     max_bind_num, step_1_expected_success_res,
                                                     step_1_expected_failure_res, binded_server_id_list)

        # step2: 会员刷新token限制
        step_2_expected_success_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        step_2_expected_failure_res = data_source.ExpectedResult(StatusCode.OK.value,
                                                                 data_source.token_out_of_limit_res_data)
        user_token_step("step2: 会员刷新token限制", gateway_origin, product, open_id, token, super_server_id_list,
                        step_2_expected_success_res, step_2_expected_failure_res)

        # step3: 获取设备列表
        step_3_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        server_id_list_step("step3: 获取设备列表", gateway_origin, product, open_id, token, super_server_id_list,
                            step_3_expected_res)

        # step4: 移除绑定设备
        if len(super_server_id_list) > 1:
            # 随机选择一个待移除的绑定设备id
            unbind_server_id = random.choice(super_server_id_list)

            step_4_expected_unbind_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
            step_4_expected_list_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
            server_id_unbind_step("step4: 移除绑定设备", gateway_origin, product, open_id, token, unbind_server_id,
                                  step_4_expected_unbind_res, step_4_expected_list_res)
