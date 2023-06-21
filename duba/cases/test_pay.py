from urllib import parse
from urllib.parse import urlparse

import allure
import json
import jsonpath
import re
import time
import random
from pprint import pformat
import duba.dubalib as dubalib
from duba.api.coin import coin_info_api
from duba.api.user import user_info_api
from duba.api.pay import pay_api, pay_change_status_api, pay_order_result_api, sdk_pay_order_result_api, \
    pay_settings_api
from interface_common.utils import day_to_second, get_unix_timestamp
from duba.constants import VipTypeInfo, ProductType, PayOrderStatus, StatusCode, EntrustSetting, \
    PaySettingsShow, VipType, SHOW_KEYS_DEVICE
from duba.config import data_source
from interface_common import tcweblib
from interface_common.logger import logger

"""毒霸会员支付模块 业务流程测试 ———— 会员中心支付"""


@allure.step("{step_name}")
def get_pay_settings_step_sdk(step_name, server_host, product, open_id, token, server_id, expected_res,
                          show=[PaySettingsShow.SDK.value], is_upgrade=False):
    logger.info(step_name)
    # 发起获取会员中心套餐请求
    res = pay_settings_api(server_host, product, open_id, token, server_id, is_continuous=2, show=show, is_upgrade=is_upgrade)
    # 校验获取会员中心套餐结果
    pay_price_settings = check_pay_settings_result(res, expected_res)
    assert pay_price_settings, "验获取会员中心套餐结果异常"
    return pay_price_settings

@allure.step("{step_name}")
def get_pay_settings_step(step_name, server_host, product, open_id, token, server_id, expected_res,
                          vip_type, device_num, is_upgrade=False, is_entrust_setting=None):
    logger.info(step_name)
    # 发起获取会员中心套餐请求
    # res = pay_settings_api(server_host, product, open_id, token, server_id, show=show, is_upgrade=is_upgrade)
    res = dubalib.get_pay_settings(server_host, product, open_id, token, server_id, vip_type=vip_type,
                                   device_num=device_num, is_upgrade=is_upgrade, is_entrust_setting=is_entrust_setting)
    # 校验获取会员中心套餐结果
    pay_price_settings = res
    assert pay_price_settings, "验获取会员中心套餐结果异常"
    return pay_price_settings

@allure.step("{step_name}")
def pay_step(step_name, server_host, product, open_id, token, server_id, pay_setting_id, pay_channel, pay_type,
             pay_type_data, expected_res, fake_pay_origin=None, is_upgrade=False):
    logger.info(step_name)
    # 发起支付下单请求
    res = pay_api(server_host, product, open_id, token, server_id, pay_setting_id, pay_channel, pay_type,
                  is_upgrade=is_upgrade)
    # 校验支付下单结果
    check_result = check_pay_result(res, pay_type, pay_type_data, expected_res, fake_pay_origin)

    return check_result


@allure.step("{step_name}")
def pay_order_result_step(step_name, server_host, product, open_id, token, order_time, order_id, pay_channel, pay_type,
                          query_sleep_seconds, expected_res, expected_order_status):
    logger.info(step_name)
    # 等待N秒，再执行查询
    time.sleep(query_sleep_seconds)
    # 发起查询支付结果请求
    if product == ProductType.SDK.value:
        # 毒霸新会员sdk
        res = sdk_pay_order_result_api(server_host, open_id, token, order_id=order_id, pay_channel=pay_channel,
                                       pay_type=pay_type)
    else:
        # 毒霸新会员v2
        res = pay_order_result_api(server_host, product, open_id, token, order_time)
    # 校验查询支付结果
    check_order_result(res, expected_res, expected_order_status)


@allure.step("{step_name}")
def pay_change_status_step(step_name, server_host, order_id, expected_res):
    # 发起第三方支付请求
    logger.info(step_name)
    res = pay_change_status_api(server_host, order_id)
    # 校验第三方支付结果
    check_change_status_result(res, expected_res)


@allure.step("{step_name}")
def coin_info_step(step_name, server_host, product, open_id, token, before_coin, get_apollo_coin_setting, day_length,
                   expected_res):
    logger.info(step_name)
    coin_setting_count = dubalib.get_coin_by_vip_day_length(get_apollo_coin_setting, day_length)
    # 发起积分查询请求
    res = coin_info_api(server_host, product, open_id, token)
    # 校验积分查询结果
    check_coin_info_result(res, before_coin, coin_setting_count, expected_res)


@allure.step("{step_name}")
def user_info_step(step_name, server_host, product, open_id, token, before_user_info, day_length, setting_vip_type,
                   pay_timestamp, vip_ex_date_diff_seconds, expected_res):
    logger.info(step_name)
    # 发起查询用户详细信息请求
    res = user_info_api(server_host, product, open_id, token)
    # 校验用户详细信息结果
    check_user_info_result(res, before_user_info, day_length, setting_vip_type, pay_timestamp, vip_ex_date_diff_seconds,
                           expected_res)


def check_pay_settings_result(res, expected_res):
    """
    检验会员中心套餐结果
    @param res: 获取会员中心套餐接口响应结果
    @param expected_res: 预期结果结构体 ExpectedResult
    @return:
    """
    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, "[test_pay]获取会员中心套餐接口状态码错误 code=%d" % res.status_code

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "[test_pay]校验获取会员中心套餐结果返回值失败"

    pay_price_settings = res_data["pay_price_settings"]
    allure.attach(pformat(pay_price_settings), "会员中心套餐列表")

    assert len(pay_price_settings) > 0, "[test_pay]会员中心套餐列表为空"

    return pay_price_settings


def check_pay_result(res, pay_type, pay_type_data, expected_res, fake_pay_origin):
    """
    校验支付下单结果
    @param res: 支付下单接口响应结果
    @param pay_type: 支付类型
    @param pay_type_data: 支付类型对应详细信息
    @param expected_res: 预期结果结构体 ExpectedResult
    @param fake_pay_origin: 第三方支付接口地址
    @return:
        order_id: 订单号
        url: 支付链接
    """
    result = {
        "order_id": None,
        "url": None
    }

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, "[test_pay]支付下单接口状态码错误 code=%d" % res.status_code

    pay_res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(pay_res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, pay_res_data)
    assert analysis_result, "[test_pay]校验%s支付下单返回值失败" % pay_type

    # 预期错误的用例不需要校验其他响应结果
    if not expected_res.check_remaining_res:
        return result

    order_id = jsonpath.jsonpath(pay_res_data, '$.order_id')[0]
    allure.attach(order_id, '订单号')
    # 校验订单号格式
    assert re.fullmatch(r'\w{32}', order_id), "[test_pay]订单号校验失败"

    # 获取支付链接
    url = jsonpath.jsonpath(pay_res_data, '$.%s' % pay_type_data["url_key"])[0]
    allure.attach(url, '支付链接')
    # 校验支付链接格式
    # weixin://wxpay/bizpayurl?pr=R8ttWCtzz
    # http://fakepayserver.aix-test-k8s.iweikan.cn/pay/contractorder/h5?out_trade_no=25a4092e09f07e29b67f3ccd9d8771b2&contract_id=4321xusz2vkSficl
    url_match = re.match(r'(.+/pay/contractorder/h5\?\w+|weixin\://wxpay/bizpayurl\?pr=\w+|.+/pay/h5/\w+)', url)
    assert url_match, "[test_pay]支付链接格式校验失败"

    try:
        # 签约支付才有contract_id
        contract_id = parse.parse_qs(urlparse(url).query)["contract_id"][0]
    except:
        contract_id = None

    result["order_id"] = order_id
    result["url"] = url
    result["contract_id"] = contract_id

    return result


def check_order_result(res, expected_res, expected_order_status=None):
    """
    检验支付结果
    @param res: 查询支付结果接口响应结果
    @param expected_res: 预期结果结构体 ExpectedResult
    @param expected_order_status: 预期订单状态
    @return:
    """
    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, "[test_pay]查询支付结果接口状态码错误 code=%d" % res.status_code

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "[test_pay]校验查询支付结果返回值失败"

    # 存在预期订单状态时才检验支付结果字段
    if expected_order_status is None:
        return

    order_status = jsonpath.jsonpath(res_data, "$.data.status")[0]
    allure.attach(str(expected_order_status), "预期支付结果")
    allure.attach(str(order_status), "实际支付结果")

    assert order_status == expected_order_status, "[test_pay]支付结果校验失败"


def check_change_status_result(res, expected_res):
    """
    校验第三方支付结果
    @param res: 第三方支付接口响应结果
    @param expected_res: 预期结果结构体 ExpectedResult
    @return:
    """
    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, "[test_pay]第三方支付接口请求失败 code=%d" % res.status_code

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "[test_pay]第三方支付接口返回值校验失败"


def check_coin_info_result(res, before_coin, coin_setting_count, expected_res):
    """
    校验积分查询结果
    @param res: 积分查询接口响应结果
    @param before_coin: 购买套餐前用户积分数量
    @param coin_setting_count: 套餐对应赠送积分数量
    @param expected_res: 预期结果结构体 ExpectedResult
    @return:
    """
    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, "[test_pay]积分接口请求失败 code=%d" % res.status_code

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "[test_pay]积分接口返回值校验失败"
    allure.attach(res.text, "返回结果")

    # 预期错误的用例不需要校验其他响应结果
    if not expected_res.check_remaining_res:
        return

    coin = jsonpath.jsonpath(res_data, '$.coin')[0]
    allure.attach(str(before_coin), "原有积分")
    allure.attach(str(coin), "现有积分")
    allure.attach(str(coin_setting_count), "套餐对应奖励积分数")

    assert coin - before_coin == coin_setting_count, "用户积分校验失败"


def check_user_info_result(res, before_user_info, day_length, setting_vip_type, pay_timestamp, vip_ex_date_diff_seconds,
                           expected_res):
    """
    校验用户详细信息结果
    @param res: 用户详细信息接口响应结果
    @param before_user_info: 购买套餐前用户详细信息
    @param day_length: 套餐天数
    @param setting_vip_type: 套餐VIP等级
    @param pay_timestamp: 支付时间戳
    @param expected_res: 预期结果结构体 ExpectedResult
    @return:
    """
    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, "[test_pay]用户详细信息接口请求失败 code=%d" % res.status_code

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "[test_pay]用户详细信息接口返回值校验失败"

    # 预期错误的用例不需要校验其他响应结果
    if not expected_res.check_remaining_res:
        return

    user_info = jsonpath.jsonpath(res_data, '$.data.user_info')[0]
    allure.attach(pformat(user_info), "用户详细信息")

    before_vip_ex_date = before_user_info["vip_ex_date"]  # 原vip过期时间
    before_vip_type = int(before_user_info["vip_type"])  # 原vip等级
    vip_ex_date = user_info["vip_ex_date"]  # 现vip过期时间
    vip_type = int(user_info["vip_type"])  # 现vip等级
    allure.attach(str(before_vip_ex_date), "原VIP过期时间")
    allure.attach(str(vip_ex_date), "现VIP过期时间")
    allure.attach(str(before_vip_type), "原VIP等级")
    allure.attach(str(setting_vip_type), "套餐VIP等级")
    allure.attach(str(vip_type), "现VIP等级")
    # VIP等级校验
    new_vip_type = dubalib.get_next_vip_type(before_vip_type, setting_vip_type)  # 获取用户购买vip套餐后的应得等级
    allure.attach(str(new_vip_type), "预期VIP等级")
    assert vip_type == new_vip_type, "用户VIP等级校验失败"

    # VIP时长校验
    if before_vip_ex_date == 0:  # 非会员的VIP过期时间为0，替换为订单支付时间再进行计算
        before_vip_ex_date = pay_timestamp
    second_length = day_to_second(day_length)
    allure.attach("天数={days} | 秒数={seconds}".format(days=day_length, seconds=second_length), "套餐VIP时长")
    assert abs((vip_ex_date - before_vip_ex_date) - second_length) <= vip_ex_date_diff_seconds, "用户VIP时长校验失败"


@allure.epic("毒霸会员支付模块 业务流程测试")
@allure.feature('场景：获取会员中心套餐->支付下单->查询支付结果->第三方支付->支付结果查询校验->积分校验->用户VIP信息校验')
class TestPay(object):
    # @pytest.mark.skip("测试其他用例，跳过此用例")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.story("用例：获取会员中心套餐->支付下单->查询支付结果->第三方支付->支付结果查询校验->积分校验->用户VIP信息校验 预期成功")
    @allure.description("""
    此用例是针对SDK会员 获取会员中心套餐->支付下单->查询支付结果->第三方支付->支付结果查询校验->积分校验->用户VIP信息校验 场景的测试
    Set up:
        1.创建不同类型的会员账号
        2.随机生成server id
        3.获取用户初始积分、VIP信息
    step1: 获取会员中心套餐
        1.请求获取会员中心套餐接口
        2.校验获取会员中心套餐接口返回数据的结构和数值
        3.获取会员中心套餐列表
    step2: 支付下单
        1.根据配置套餐ID支付下单
        2.校验支付下单接口返回数据的结构和数值
        3.获取订单id
    step3: 查询支付结果
        1.请求查询支付结果接口
        2.校验第三方支付接口返回数据的结构和数值
        3.校验支付结果是否为未支付
    step4: 第三方支付（Mock）
        1.根据订单id进行第三方支付
        2.校验第三方支付接口返回数据的结构和数值
    step5: 支付结果查询校验
        1.请求查询支付结果接口
        2.校验第三方支付接口返回数据的结构和数值
        3.校验支付结果是否为支付成功
    step6: 积分校验
        1.获取用户当前积分
        2.校验用户积分接口返回数据的结构和数值
        3.获取apollo上的积分配置
        4.根据套餐时长校验用户积分增长与配置是否一致
    step7: 用户VIP信息校验
        1.获取用户当前详细信息
        2.校验用户详细信息接口返回数据的结构和数值
        3.校验用户VIP时长是否与套餐一致
        4.校验用户VIP等级是否正确
    """)
    # 设置默认标题
    @allure.title("获取会员中心套餐->支付下单->查询支付结果->第三方支付->支付结果查询校验->积分校验->用户VIP信息校验 预期成功")
    def test_pay_success(self, product_data, create_vip_account, get_pay_type_data, get_apollo_coin_setting,
                         case_config):
        pay_origin = case_config["params"]["pay_origin"]
        gateway_origin = case_config["params"]["gateway_origin"]
        fake_pay_origin = case_config["params"]["fake_pay_origin"]
        query_sleep_seconds = case_config["params"]["query_sleep_seconds"]
        vip_ex_date_diff_seconds = case_config["params"]["vip_ex_date_diff_seconds"]

        product = product_data["product"]

        # 获取会员账号的 open_id 与 token
        account_info = create_vip_account
        open_id = account_info["open_id"]
        token = account_info["token"]
        user_vip_type = account_info["vip_type"]
        user_vip_name = VipTypeInfo[user_vip_type]["name"]
        # 创建随机客户端server id
        server_id = dubalib.create_server_id()

        pay_type, pay_type_data = get_pay_type_data
        pay_type_value = pay_type.value
        pay_channel = pay_type_data["pay_channel"].value

        # 获取初始用户详细信息
        before_user_info, device_info = dubalib.get_user_info(gateway_origin, product, open_id, token, attach_allure=False)
        logger.info("用户详细信息 user_info = %s" % before_user_info)
        # 获取初始用户积分信息
        # before_coin = None
        # if dubalib.has_coin_interface(product):  # 毒霸新会员sdk 无积分相关接口
        #     before_user_coin_info = dubalib.get_user_coin_info(gateway_origin, product, open_id, token,
        #                                                        attach_allure=False)
        #     before_coin = before_user_coin_info["coin"]
        #     logger.info("积分信息 coin = %s" % before_coin)

        # step1: 获取会员中心套餐
        step_1_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        pay_price_settings = get_pay_settings_step_sdk("step1: 获取会员中心套餐", gateway_origin, product, open_id, token,
                                                   server_id, step_1_expected_res)

        # 过滤出非纯签约套餐
        filtered_pay_price_settings = dubalib.get_filtered_pay_settings(pay_price_settings,
                                                                        is_entrust_setting=EntrustSetting.NOT_ENTRUST)
        assert filtered_pay_price_settings, "会员中心未找到非纯签约套餐"
        # 从非纯签约套餐列表随机选择一个套餐
        pay_setting = random.choice(filtered_pay_price_settings)
        pay_setting_id = pay_setting["id"]
        pay_setting_name = pay_setting["name"]
        logger.info("套餐id = %d" % pay_setting_id)
        logger.info("套餐名称 name = %s" % pay_setting_name)

        allure.dynamic.title(
            "毒霸新会员{product} {user_vip_name}用户 {pay_setting_name} {pay_type}支付".format(product=product,
                                                                                      pay_type=pay_type_value,
                                                                                      user_vip_name=user_vip_name,
                                                                                      pay_setting_name=pay_setting_name)
        )

        # 获取数据库中VIP套餐相关信息
        pay_setting_info = dubalib.get_mysql_pay_setting(pay_setting_id)
        setting_vip_type = int(pay_setting_info["vip_type"])  # 会员类型
        month_length = pay_setting_info["month_length"]  # 套餐月数
        day_length = pay_setting_info["day_length"]  # 套餐天数
        real_day_length = dubalib.get_pay_setting_real_day_length(month_length, day_length)
        logger.info("套餐等级 vip_type = %d" % setting_vip_type)
        logger.info("套餐天数 month_length = %d" % month_length)
        logger.info("套餐天数 day_length = %d" % day_length)
        logger.info("实际套餐天数 real_day_length = %d" % real_day_length)

        # step2: 支付下单
        order_timestamp = get_unix_timestamp()
        step_2_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        check_result = pay_step("step2: 支付下单", pay_origin, product, open_id, token, server_id, pay_setting_id,
                                pay_channel, pay_type_value, pay_type_data, step_2_expected_res, fake_pay_origin)
        order_id = check_result["order_id"]

        # step3: 查询支付结果
        step_3_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        no_pay_order_status = PayOrderStatus.ORDER_NOT_PAY.value
        pay_order_result_step("step3: 查询支付结果", gateway_origin, product, open_id, token, order_timestamp, order_id,
                              pay_channel, pay_type_value, query_sleep_seconds, step_3_expected_res,
                              no_pay_order_status)

        # step4: 第三方支付
        step_4_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        pay_change_status_step("step4: 第三方支付", fake_pay_origin, order_id, step_4_expected_res)
        pay_timestamp = get_unix_timestamp()

        # step5: 支付结果查询校验
        step_5_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        success_order_status = PayOrderStatus.ORDER_PAY_SUCCESS.value
        pay_order_result_step("step5: 支付结果查询校验", gateway_origin, product, open_id, token, order_timestamp, order_id,
                              pay_channel, pay_type_value, query_sleep_seconds, step_5_expected_res,
                              success_order_status)

        # step6: 积分校验（毒霸新会员sdk 无积分相关接口）
        # if dubalib.has_coin_interface(product):
        #     step_6_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        #     coin_info_step("step6: 积分校验", pay_origin, product, open_id, token, before_coin, get_apollo_coin_setting,
        #                    real_day_length, step_6_expected_res)
        # else:
        with allure.step("step6: 积分校验（跳过）"):
            allure.attach("积分功能下线", "积分功能下线")

        # step7: 用户VIP信息校验
        step_7_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        user_info_step("step7: 用户VIP信息校验", gateway_origin, product, open_id, token, before_user_info, real_day_length,
                       setting_vip_type, pay_timestamp, vip_ex_date_diff_seconds, step_7_expected_res)

    @allure.severity(allure.severity_level.BLOCKER)
    @allure.story("用例：获取会员中心套餐->支付下单->查询支付结果->第三方支付->支付结果查询校验->积分校验->用户VIP信息校验 预期成功")
    @allure.description("""
        此用例是针对毒霸V2会员 获取会员中心套餐->支付下单->查询支付结果->第三方支付->支付结果查询校验->积分校验->用户VIP信息校验 场景的测试
        Set up:
            1.创建不同类型的会员账号
            2.随机生成server id
            3.获取用户初始积分、VIP信息
        step1: 获取会员中心套餐
            1.请求获取会员中心套餐接口
            2.校验获取会员中心套餐接口返回数据的结构和数值
            3.获取会员中心套餐列表
        step2: 支付下单
            1.根据配置套餐ID支付下单
            2.校验支付下单接口返回数据的结构和数值
            3.获取订单id
        step3: 查询支付结果
            1.请求查询支付结果接口
            2.校验第三方支付接口返回数据的结构和数值
            3.校验支付结果是否为未支付
        step4: 第三方支付（Mock）
            1.根据订单id进行第三方支付
            2.校验第三方支付接口返回数据的结构和数值
        step5: 支付结果查询校验
            1.请求查询支付结果接口
            2.校验第三方支付接口返回数据的结构和数值
            3.校验支付结果是否为支付成功
        step6: 积分校验
            1.获取用户当前积分
            2.校验用户积分接口返回数据的结构和数值
            3.获取apollo上的积分配置
            4.根据套餐时长校验用户积分增长与配置是否一致
        step7: 用户VIP信息校验
            1.获取用户当前详细信息
            2.校验用户详细信息接口返回数据的结构和数值
            3.校验用户VIP时长是否与套餐一致
            4.校验用户VIP等级是否正确
        """)
    # 设置默认标题
    @allure.title("获取会员中心套餐->支付下单->查询支付结果->第三方支付->支付结果查询校验->积分校验->用户VIP信息校验 预期成功")
    def test_pay_v2_success(self, product_data, create_vip_account_v3, get_pay_type_data, get_apollo_coin_setting,
                         case_config):
        pay_origin = case_config["params"]["pay_origin"]
        gateway_origin = case_config["params"]["gateway_origin"]
        fake_pay_origin = case_config["params"]["fake_pay_origin"]
        query_sleep_seconds = case_config["params"]["query_sleep_seconds"]
        vip_ex_date_diff_seconds = case_config["params"]["vip_ex_date_diff_seconds"]

        product = product_data["product"]

        # 获取会员账号的 open_id 与 token
        account_info = create_vip_account_v3
        open_id = account_info["open_id"]
        token = account_info["token"]
        user_vip_type = account_info["vip_type"]
        user_vip_name = VipTypeInfo[user_vip_type]["name"]
        # 创建随机客户端server id
        server_id = dubalib.create_server_id()

        pay_type, pay_type_data = get_pay_type_data
        pay_type_value = pay_type.value
        pay_channel = pay_type_data["pay_channel"].value

        # 获取初始用户详细信息
        before_user_info, device_info = dubalib.get_user_info(gateway_origin, product, open_id, token,
                                                              attach_allure=False)
        logger.info("用户详细信息 user_info = %s" % before_user_info)
        # 获取初始用户积分信息
        # before_coin = None
        # if dubalib.has_coin_interface(product):  # 毒霸新会员sdk 无积分相关接口
        #     before_user_coin_info = dubalib.get_user_coin_info(gateway_origin, product, open_id, token,
        #                                                        attach_allure=False)
        #     before_coin = before_user_coin_info["coin"]
        #     logger.info("积分信息 coin = %s" % before_coin)

        # 如果是非会员，则随机给予设备数
        vip_type = int(before_user_info["vip_type"])

        if not device_info and vip_type == VipType.NON_VIP.value:
            device_num = random.choice(SHOW_KEYS_DEVICE)
        else:
            device_num = device_info["device_num"]

        if vip_type == VipType.NON_VIP.value:
            vip_type = VipType.NORMAL_VIP.value

        # step1: 获取会员中心套餐
        step_1_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        pay_price_settings = get_pay_settings_step("step1: 获取会员中心套餐", gateway_origin, product, open_id, token,
                                                   server_id, step_1_expected_res, vip_type, device_num)

        # 过滤出非纯签约套餐
        filtered_pay_price_settings = dubalib.get_filtered_pay_settings(pay_price_settings,
                                                                        is_entrust_setting=EntrustSetting.NOT_ENTRUST)
        assert filtered_pay_price_settings, "会员中心未找到非纯签约套餐"
        # 从非纯签约套餐列表随机选择一个套餐
        pay_setting = random.choice(filtered_pay_price_settings)
        pay_setting_id = pay_setting["id"]
        pay_setting_name = pay_setting["name"]
        logger.info("套餐id = %d" % pay_setting_id)
        logger.info("套餐名称 name = %s" % pay_setting_name)

        allure.dynamic.title(
            "毒霸新会员{product} {user_vip_name}用户 {pay_setting_name} {pay_type}支付".format(product=product,
                                                                                      pay_type=pay_type_value,
                                                                                      user_vip_name=user_vip_name,
                                                                                      pay_setting_name=pay_setting_name)
        )

        # 获取数据库中VIP套餐相关信息
        pay_setting_info = dubalib.get_mysql_pay_setting(pay_setting_id)
        setting_vip_type = int(pay_setting_info["vip_type"])  # 会员类型
        month_length = pay_setting_info["month_length"]  # 套餐月数
        day_length = pay_setting_info["day_length"]  # 套餐天数
        real_day_length = dubalib.get_pay_setting_real_day_length(month_length, day_length)
        logger.info("套餐等级 vip_type = %d" % setting_vip_type)
        logger.info("套餐天数 month_length = %d" % month_length)
        logger.info("套餐天数 day_length = %d" % day_length)
        logger.info("实际套餐天数 real_day_length = %d" % real_day_length)

        # step2: 支付下单
        order_timestamp = get_unix_timestamp()
        step_2_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        check_result = pay_step("step2: 支付下单", pay_origin, product, open_id, token, server_id, pay_setting_id,
                                pay_channel, pay_type_value, pay_type_data, step_2_expected_res, fake_pay_origin)
        order_id = check_result["order_id"]

        # step3: 查询支付结果
        step_3_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        no_pay_order_status = PayOrderStatus.ORDER_NOT_PAY.value
        pay_order_result_step("step3: 查询支付结果", gateway_origin, product, open_id, token, order_timestamp, order_id,
                              pay_channel, pay_type_value, query_sleep_seconds, step_3_expected_res,
                              no_pay_order_status)

        # step4: 第三方支付
        step_4_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        pay_change_status_step("step4: 第三方支付", fake_pay_origin, order_id, step_4_expected_res)
        pay_timestamp = get_unix_timestamp()

        # step5: 支付结果查询校验
        step_5_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        success_order_status = PayOrderStatus.ORDER_PAY_SUCCESS.value
        pay_order_result_step("step5: 支付结果查询校验", gateway_origin, product, open_id, token, order_timestamp, order_id,
                              pay_channel, pay_type_value, query_sleep_seconds, step_5_expected_res,
                              success_order_status)

        # step6: 积分校验（毒霸新会员sdk 无积分相关接口）
        # if dubalib.has_coin_interface(product):
        #     step_6_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        #     coin_info_step("step6: 积分校验", pay_origin, product, open_id, token, before_coin, get_apollo_coin_setting,
        #                    real_day_length, step_6_expected_res)
        # else:
        with allure.step("step6: 积分校验（跳过）"):
            allure.attach("积分功能下线", "积分功能下线")

        # step7: 用户VIP信息校验
        step_7_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        user_info_step("step7: 用户VIP信息校验", gateway_origin, product, open_id, token, before_user_info, real_day_length,
                       setting_vip_type, pay_timestamp, vip_ex_date_diff_seconds, step_7_expected_res)

    # @pytest.mark.skip("测试其他用例，跳过此用例")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.story("用例：游客账号支付下单 预期失败")
    @allure.description("""
        此用例是针对毒霸会员 游客账号 获取会员中心套餐->支付下单 场景的测试
        Set up:
            1.创建游客账号
            2.随机生成server id
        step1: 获取会员中心套餐
            1.请求获取会员中心套餐接口
            2.校验获取会员中心套餐接口返回数据的结构和数值
            3.获取会员中心套餐列表
        step2: 支付下单
            1.根据配置套餐ID支付下单
            2.校验支付下单接口返回数据的结构和数值
        """)
    @allure.title("游客账号 获取会员中心套餐->支付下单 预期失败")
    def test_tourist_pay_failure(self, product_data, create_tourist_account, get_pay_type_data, case_config):
        pay_origin = case_config["params"]["pay_origin"]
        gateway_origin = case_config["params"]["gateway_origin"]

        product = product_data["product"]

        # 获取游客账号的 open_id 和 token
        open_id, token = create_tourist_account

        # 创建随机客户端server id
        server_id = dubalib.create_server_id()

        pay_type, pay_type_data = get_pay_type_data
        pay_type_value = pay_type.value
        pay_channel = pay_type_data["pay_channel"].value

        # step1: 获取会员中心套餐
        step_1_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        pay_price_settings = get_pay_settings_step("step1: 获取会员中心套餐", gateway_origin, product, open_id, token,
                                                   server_id, expected_res=step_1_expected_res,
                                                   vip_type=VipType.NORMAL_VIP.value, device_num=1)

        # 从会员中心套餐列表随机选择一个套餐
        pay_setting = random.choice(pay_price_settings)
        pay_setting_id = pay_setting["id"]
        pay_setting_name = pay_setting["name"]
        logger.info("套餐id pay_setting_id = %d" % pay_setting_id)
        logger.info("套餐名称 pay_setting_name = %s" % pay_setting_name)

        allure.dynamic.title(
            "毒霸新会员{product} 游客账号 {pay_setting_name} {pay_type}支付".format(product=product,
                                                                         pay_type=pay_type_value,
                                                                         pay_setting_name=pay_setting_name)
        )

        # 获取数据库中VIP套餐相关信息
        pay_setting_info = dubalib.get_mysql_pay_setting(pay_setting_id)
        setting_vip_type = int(pay_setting_info["vip_type"])  # 套餐等级
        month_length = pay_setting_info["month_length"]  # 套餐月数
        day_length = pay_setting_info["day_length"]  # 套餐天数
        real_day_length = dubalib.get_pay_setting_real_day_length(month_length, day_length)
        logger.info("套餐等级 vip_type = %d" % setting_vip_type)
        logger.info("套餐天数 month_length = %d" % month_length)
        logger.info("套餐天数 day_length = %d" % day_length)
        logger.info("实际套餐天数 real_day_length = %d" % real_day_length)

        # step2: 支付下单
        step_2_expected_result = data_source.ExpectedResult(StatusCode.OK.value, data_source.tourist_pay_res_data,
                                                            check_remaining_res=False)
        pay_step("step2: 支付下单", pay_origin, product, open_id, token, server_id, pay_setting_id, pay_channel,
                 pay_type_value, pay_type_data, step_2_expected_result)
