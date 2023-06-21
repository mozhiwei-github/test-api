import time
import json
import allure
import random
from pprint import pformat
from xml.etree import ElementTree
import duba.dubalib as dubalib
from interface_common import tcweblib
from interface_common.logger import logger
from interface_common.utils import get_unix_timestamp
from duba.config import data_source
from duba.constants import VipTypeInfo, StatusCode, EntrustSetting, ContractStatus, VipType, SHOW_KEYS_DEVICE
from duba.cases.test_pay import get_pay_settings_step, pay_step, coin_info_step, user_info_step, \
    check_change_status_result
from duba.api.pay import pay_contractorder_pay_api, wxpay_deduction_trigger_api, papay_deletecontract_api, \
    pay_settings_api

"""毒霸会员支付模块 业务流程测试 ———— 纯签约会员支付"""


@allure.step("{step_name}")
def get_pay_settings_duli_step(step_name, gateway_origin, product, open_id, token, server_id, expected_res):
    logger.info(step_name)
    # 只有独立支付页才有签约类型套餐
    show = [916]
    res = pay_settings_api(gateway_origin, product, open_id, token, server_id, show=show)
    res_data = res.json()
    allure.attach(f"{expected_res.res_data}", f"套餐预期返回")
    allure.attach(f"{res_data}", f"套餐实际返回")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "获取套餐异常"
    allure.attach(f"{res_data}", f"{show}套餐返回内容")
    pay_price_settings = res_data.get("pay_price_settings", None)
    assert pay_price_settings, "获取pay_price_settings异常"
    # 过滤出纯签约套餐
    filtered_pay_price_settings = dubalib.get_filtered_pay_settings(pay_price_settings,
                                                                    is_entrust_setting=EntrustSetting.ENTRUST)
    assert filtered_pay_price_settings, "会员中心未找到纯签约套餐"
    return filtered_pay_price_settings

@allure.step("{step_name}")
def pay_change_status_step(step_name, server_host, order_id, expected_res, contract_id):
    # 发起支付并签约请求
    logger.info(step_name)
    res = pay_contractorder_pay_api(server_host, order_id, contract_id)

    # 校验支付签约结果
    check_change_status_result(res, expected_res)


@allure.step("{step_name}")
def continuous_info_step(step_name, open_id, expected_contract_status, query_sleep_seconds):
    logger.info(step_name)
    # 等待N秒，再执行查询
    time.sleep(query_sleep_seconds)
    # 获取用户自动续费信息表信息
    continuous_info = dubalib.get_mysql_continuous_info(open_id)
    # 校验自动续费信息
    check_continuous_info_result(continuous_info, expected_contract_status)


@allure.step("{step_name}")
def wxpay_deduction_trigger_step(step_name, server_host, product, open_id, expected_res):
    logger.info(step_name)
    # 触发签约自动续费前需修改下次扣费时间，模拟到达扣费时间
    dubalib.set_mysql_continuous_deductions_time(open_id)

    # 触发签约扣费（微信）
    res = wxpay_deduction_trigger_api(server_host, product, open_id)
    # 校验触发签约扣费结果
    check_wxpay_deduction_trigger_result(res, expected_res)


@allure.step("{step_name}")
def deductions_info_step(step_name, open_id, query_sleep_seconds, pay_channel, deduction_timestamp,
                         deductions_time_diff_seconds):
    logger.info(step_name)
    # 等待N秒，再执行查询
    time.sleep(query_sleep_seconds)
    # 查询微信自动扣费订单表信息
    deductions_info = dubalib.get_mysql_deductions_info(open_id)
    # 校验微信自动扣费订单信息
    check_deductions_info_result(deductions_info, pay_channel, deduction_timestamp, deductions_time_diff_seconds)


@allure.step("{step_name}")
def delete_contract_step(step_name, server_host, mch_id, app_id, contract_id, expected_res):
    logger.info(step_name)
    # 自动续费解约
    res = papay_deletecontract_api(server_host, mch_id, app_id, contract_id)
    # 校验自动续费解约结果
    check_delete_contract_result(res, expected_res)


def check_continuous_info_result(continuous_info, expected_contract_status):
    """
    校验自动续费信息
    @param continuous_info: 查询到的自动续费信息结果
    @param expected_contract_status: 预期签约状态枚举成员 ContractStatus
    @return:
    """
    logger.info("自动续费信息结果 continuous_info = %s" % pformat(continuous_info))
    allure.attach(pformat(continuous_info), "自动续费信息结果")

    is_continuous = continuous_info["is_continuous"]
    allure.attach(str(expected_contract_status.value), "预期签约状态")
    allure.attach(str(is_continuous), "实际签约状态")
    logger.info("预期签约状态: %s" % expected_contract_status.value)
    logger.info("实际签约状态: %s" % is_continuous)
    assert is_continuous == expected_contract_status.value, "签约状态校验失败"


def check_wxpay_deduction_trigger_result(res, expected_res):
    """
    校验触发签约扣费结果
    @param res: 触发签约扣费接口响应结果
    @param expected_res: 预期结果结构体 ExpectedResult
    @return:
    """
    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, "[test_pay_contract]触发签约扣费接口状态码错误 code=%d" % res.status_code

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "[test_pay_contract]校验触发签约扣费结果返回值失败"


def check_deductions_info_result(deductions_info, pay_channel, deduction_timestamp, deductions_time_diff_seconds):
    """
    校验微信自动扣费订单信息
    @param deductions_info: 微信自动扣费订单表信息
    @param pay_channel: 支付渠道
    @param deduction_timestamp: 自动扣费时间
    @param deductions_time_diff_seconds: 自动扣费时间误差值
    @return:
    """
    logger.info("微信自动扣费订单表信息 deductions_info = %s" % pformat(deductions_info))
    allure.attach(pformat(deductions_info), "微信自动扣费订单表信息")

    expected_pay_status = 1  # 预期订单支付状态：0为未支付, 1为已支付
    is_pay = deductions_info["is_pay"]
    allure.attach(str(expected_pay_status), "预期订单支付状态")
    allure.attach(str(is_pay), "实际订单支付状态")
    assert is_pay == expected_pay_status, "订单支付状态校验失败"

    order_pay_channel = deductions_info["pay_channel"]
    allure.attach(str(order_pay_channel), "订单支付渠道")
    assert order_pay_channel == pay_channel, "订单支付渠道校验失败"

    order_deductions_datetime = deductions_info["deductions_time"]
    order_deductions_timestamp = int(time.mktime(order_deductions_datetime.timetuple()))
    allure.attach(str(order_deductions_timestamp), "预期订单扣费时间")
    allure.attach(str(deduction_timestamp), "实际订单扣费时间")
    assert abs(order_deductions_timestamp - deduction_timestamp) <= deductions_time_diff_seconds, "订单扣费时间校验失败"


def check_delete_contract_result(res, expected_res):
    """
    校验自动续费解约结果
    @param res: 自动续费解约接口响应结果
    @param expected_res: 预期结果结构体 ExpectedResult
    @return:
    """
    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, "[test_pay_contract]自动续费解约接口状态码错误 code=%d" % res.status_code

    logger.info("自动续费解约接口响应结果 res = %s" % res.text)
    allure.attach(res.text, "自动续费解约接口响应结果")

    expected_result_code = expected_res.res_data["result_code"]

    try:
        root = ElementTree.fromstring(res.text)
        result_code_element = root.find('result_code')
        assert result_code_element is not None, "自动续费解约结果返回值 result_code 为空"

        allure.attach(expected_result_code, "预期result_code")
        allure.attach(result_code_element.text, "实际result_code")

        assert expected_result_code in result_code_element.text, "校验自动续费解约结果返回值 result_code 失败"
    except Exception as e:
        assert res.text == "xml", "自动续费解约结果返回值不是xml格式"


@allure.epic("毒霸会员支付模块 业务流程测试")
@allure.feature('场景：获取会员中心套餐->支付下单->支付并签约->签约结果查询校验->积分校验->用户VIP信息校验->触发签约自动续费'
                '->查询自动续费结果->自动续费提前解约->查询签约状态')
class TestPayContract(object):
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.story("用例：获取会员中心套餐->支付下单->支付并签约->签约结果查询校验->积分校验->用户VIP信息校验->触发签约自动续费->查询自动续费结果->自动续费提前解约->查询签约状态 预期成功")
    @allure.description("""
        此用例是针对毒霸会员 获取会员中心套餐->支付下单->支付并签约->签约结果查询校验->积分校验->用户VIP信息校验->触发签约自动续费->查询自动续费结果->自动续费提前解约->查询签约状态 场景的测试
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
            3.获取订单id和签约协议号
        step3: 支付并签约（Mock）
            1.根据订单id和签约协议号进行支付并签约
            2.校验支付并签约接口返回数据的结构和数值
        step4: 签约结果查询校验
            1.根据open_id获取毒霸mysql中用户自动续费信息表信息
            2.校验签约状态是否为签约中
        step5: 积分校验
            1.获取用户当前积分
            2.校验用户积分接口返回数据的结构和数值
            3.获取apollo上的积分配置
            4.根据套餐时长校验用户积分增长与配置是否一致
        step6: 用户VIP信息校验
            1.获取用户当前详细信息
            2.校验用户详细信息接口返回数据的结构和数值
            3.校验用户VIP时长是否与套餐一致
            4.校验用户VIP等级是否正确
        step7: 触发签约自动续费
            1.修改用户自动续费信息表的下次扣费时间
            2.请求触发签约自动续费（微信）接口
        step8: 查询自动续费结果
            1.根据open_id获取毒霸mysql中微信自动扣费订单表信息
            2.校验订单支付状态是否为已支付
            3.校验订单渠道和订单扣费时间是否与预期一致
        step9: 自动续费提前解约
            1.请求自动续费解约接口
            2.校验自动续费解约接口返回数据的结构和数值
        step10: 查询签约状态
            1.根据open_id获取毒霸mysql中用户自动续费信息表信息
            2.校验签约状态是否为已解约
    """)
    @allure.title("获取会员中心套餐->支付下单->支付并签约->签约结果查询校验->积分校验->用户VIP信息校验->触发签约自动续费->查询自动续费结果->自动续费提前解约->查询签约状态 预期成功")
    def test_pay_contract_success(self, product_data, create_vip_account_v3, get_pay_type_data, get_apollo_coin_setting,
                                  case_config):
        pay_origin = case_config["params"]["pay_origin"]
        gateway_origin = case_config["params"]["gateway_origin"]
        fake_pay_origin = case_config["params"]["fake_pay_origin"]
        query_sleep_seconds = case_config["params"]["query_sleep_seconds"]
        vip_ex_date_diff_seconds = case_config["params"]["vip_ex_date_diff_seconds"]
        deductions_time_diff_seconds = case_config["params"]["deductions_time_diff_seconds"]
        mch_id = case_config["params"]["mch_id"]
        app_id = case_config["params"]["app_id"]

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
        before_coin = None
        if dubalib.has_coin_interface(product):  # 毒霸新会员sdk 无积分相关接口
            before_user_coin_info = dubalib.get_user_coin_info(gateway_origin, product, open_id, token,
                                                               attach_allure=False)
            before_coin = before_user_coin_info["coin"]
            logger.info("积分信息 coin = %s" % before_coin)

        # step1: 获取会员中心套餐
        step_1_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        # pay_price_settings = get_pay_settings_step("step1: 获取会员中心套餐", gateway_origin, product, open_id, token,
        #                                            server_id, step_1_expected_res, vip_type, device_num, is_entrust_setting=EntrustSetting.ENTRUST)
        pay_price_settings = get_pay_settings_duli_step("step1: 获取会员中心套餐", gateway_origin, product, open_id, token, server_id, step_1_expected_res)

        # 从纯签约套餐列表随机选择一个套餐
        pay_setting = random.choice(pay_price_settings)
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
        setting_vip_type = int(pay_setting_info["vip_type"])  # 套餐等级
        month_length = pay_setting_info["month_length"]  # 套餐月数
        day_length = pay_setting_info["day_length"]  # 套餐天数
        real_day_length = dubalib.get_pay_setting_real_day_length(month_length, day_length)
        logger.info("套餐等级 vip_type = %d" % setting_vip_type)
        logger.info("套餐天数 month_length = %d" % month_length)
        logger.info("套餐天数 day_length = %d" % day_length)
        logger.info("实际套餐天数 real_day_length = %d" % real_day_length)

        # step2: 支付下单
        step_2_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        check_result = pay_step("step2: 支付下单", pay_origin, product, open_id, token, server_id, pay_setting_id,
                                pay_channel, pay_type_value, pay_type_data, step_2_expected_res, fake_pay_origin)
        order_id = check_result["order_id"]
        contract_id = check_result["contract_id"]

        # step3: 支付并签约
        step_3_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        pay_change_status_step("step3: 支付并签约", fake_pay_origin, order_id, step_3_expected_res, contract_id)
        pay_timestamp = get_unix_timestamp()

        # step4: 签约结果查询校验
        expected_contract_status = ContractStatus.CONTRACTED
        continuous_info_step("step4: 签约结果查询校验", open_id, expected_contract_status, query_sleep_seconds)

        # step5: 积分校验（毒霸新会员sdk 无积分相关接口）
        # if dubalib.has_coin_interface(product):
        #     step_5_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        #     coin_info_step("step5: 积分校验", pay_origin, product, open_id, token, before_coin, get_apollo_coin_setting,
        #                    real_day_length, step_5_expected_res)
        # else:
        #     with allure.step("step5: 积分校验（跳过）"):
        #         allure.attach("product = %s" % product, "毒霸新会员sdk 无积分相关接口")

        # step6: 用户VIP信息校验
        step_6_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        user_info_step("step6: 用户VIP信息校验", gateway_origin, product, open_id, token, before_user_info, real_day_length,
                       setting_vip_type, pay_timestamp, vip_ex_date_diff_seconds, step_6_expected_res)

        # step7: 触发签约自动续费（微信）
        step_7_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        wxpay_deduction_trigger_step("step7: 触发签约自动续费（微信）", pay_origin, product, open_id, step_7_expected_res)
        deduction_timestamp = get_unix_timestamp()

        # step8: 查询自动续费结果
        deductions_info_step("step8: 查询自动续费结果", open_id, query_sleep_seconds, pay_channel, deduction_timestamp,
                             deductions_time_diff_seconds)

        # step9: 自动续费提前解约
        step_9_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.delete_contract_res_data)
        delete_contract_step("step9: 自动续费提前解约", fake_pay_origin, mch_id, app_id, contract_id, step_9_expected_res)

        # step10: 查询签约状态
        expected_contract_status = ContractStatus.CONTRACT_EXPIRED
        continuous_info_step("step10: 查询签约状态", open_id, expected_contract_status, query_sleep_seconds)
