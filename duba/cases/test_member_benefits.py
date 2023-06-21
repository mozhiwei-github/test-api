import re
import time
import json
import pytest
import allure
import jsonpath
from pprint import pformat
from duba.api.other import apollo_data_api
from duba.api.service import service_get_api, service_order_result_api
from duba import dubalib
from duba.config import data_source
from duba.constants import VipTypeInfo, StatusCode, PermissionPaySetting, PermissionPaySettingInfo, VipType
from interface_common import tcweblib
from duba.api.pay import pay_change_status_api, service_pay_api
from interface_common.logger import logger


def check_all_permission(server_host, all_permission_list):
    """校验所有权限与Apollo上的数据是否一致"""
    # 把all_permission_list转成list，方便排序
    all_permission_list = all_permission_list.split(",")

    res = apollo_data_api(server_host, "permission.yaml", "ALLPermission")

    expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"个人中心所展示的权限Apollo配置请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "个人中心所展示的权限Apollo配置接口返回值校验失败"

    apollo_permission_list = sorted([i["name"] for i in res_data["data"]])
    sorted_all_permission_list = sorted(all_permission_list)
    allure.attach(str(apollo_permission_list), "预期个人中心所展示的权限列表")
    allure.attach(str(sorted_all_permission_list), "实际个人中心所展示的权限列表")

    return apollo_permission_list == sorted_all_permission_list


def check_user_permission(server_host, user_permission_list, user_identity, permission_name="用户所拥有的权限"):
    """校验用户权限与Apollo上的数据是否一致"""
    # 判断是否为普通用户
    if user_identity != VipType.NON_VIP:
        res = apollo_data_api(server_host, "permission.yaml", "VIPPermission")

        expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        allure.attach(str(expected_res.status_code), "预期Http状态码")
        allure.attach(str(res.status_code), "实际Http状态码")
        assert res.status_code == expected_res.status_code, f"{permission_name}Apollo配置请求失败 code={res.status_code}"

        res_data = json.loads(res.text)
        allure.attach(pformat(expected_res.res_data), "预期响应结果")
        allure.attach(pformat(res_data), "实际响应结果")
        analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
        assert analysis_result, f"{permission_name}Apollo配置接口返回值校验失败"

        apollo_permission_list = sorted(res_data["data"])
    else:
        apollo_permission_list = []

    if user_permission_list != "":
        user_permission_list = user_permission_list.split(",")

    sorted_user_permission_list = sorted(user_permission_list)

    allure.attach(str(apollo_permission_list), f"预期{permission_name}列表")
    allure.attach(str(sorted_user_permission_list), f"实际{permission_name}列表")

    return apollo_permission_list == sorted_user_permission_list


def check_user_all_permission(server_host, user_all_permission_list, user_identity):
    """
       校验用户所有权限与Apollo上的数据是否一致
       (会员用户比普通用户多一个一对一的权限，121svr)
    """
    # 判断是否为普通用户
    if user_identity == VipType.NON_VIP:
        return user_all_permission_list == ""
    else:
        if "121svr" not in user_all_permission_list:
            return False
        else:
            tmp = user_all_permission_list.split(",")
            tmp.remove("121svr")  # 剔除多出的121svr权限再做对比
            return check_user_permission(server_host, ','.join(tmp), user_identity, "个人中心展示用的所拥有的权限")


@allure.step("{step_name}")
def search_user_permission_step(step_name, server_host, product, open_id, token, expected_res, pay_setting=None):
    logger.info(step_name)
    # 用户权限查询
    res = service_get_api(server_host, product, open_id, token)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"用户权限查询接口请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "用户权限查询接口返回值校验失败"

    result = res_data["data"]
    # 是否校验其他相应结果
    if not expected_res.check_remaining_res or not pay_setting:
        return result

    permission_list = jsonpath.jsonpath(res_data, '$.data.permission_list')[0]
    user_all_permission_list = jsonpath.jsonpath(res_data, '$.data.user_all_permission_list')[0]
    allure.attach(str(permission_list), "用户购买的权限列表")
    allure.attach(str(user_all_permission_list), "个人中心展示用的所拥有的权限列表")
    assert permission_list == user_all_permission_list, "用户购买的权限列表校验失败"

    pay_setting_key = PermissionPaySettingInfo[pay_setting]["key"]
    permission_info = jsonpath.jsonpath(res_data, '$.data.permission_info')[0]
    pay_setting_key_list = [pay_setting_key]
    permission_info_key_list = list(permission_info.keys())
    allure.attach(str(pay_setting_key_list), "预期权限对应key列表")
    allure.attach(str(permission_info_key_list), "实际权限对应key列表")
    assert pay_setting_key_list == permission_info_key_list

    return result


@allure.step("{step_name}")
def check_default_permission_step(step_name, server_host, res_data, user_identity):
    logger.info(step_name)
    allure.attach(pformat(res_data), '用户权限接口返回结果')
    analysis_result = tcweblib.matchd_result(data_source.get_permission, res_data)
    assert analysis_result, "校验默认用户权限失败"

    user_permission_list = jsonpath.jsonpath(res_data, '$.user_permission_list')[0]
    user_all_permission_list = jsonpath.jsonpath(res_data, '$.user_all_permission_list')[0]
    all_permission_list = jsonpath.jsonpath(res_data, '$.all_permission_list')[0]

    assert check_all_permission(server_host, all_permission_list), "个人中心所展示的权限列表校验失败"
    assert check_user_permission(server_host, user_permission_list, user_identity), "用户所拥有的权限列表校验失败"
    assert check_user_all_permission(server_host, user_all_permission_list, user_identity), "个人中心展示用的所拥有的权限列表校验失败"


@allure.step("{step_name}")
def service_pay_step(step_name, server_host, product, open_id, token, server_id, pay_setting_id, pay_channel,
                     pay_type_value, expected_res):
    logger.info(step_name)
    res = service_pay_api(server_host, product, open_id, token, server_id, pay_setting_id, pay_channel, pay_type_value)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"权益支付（下单）接口请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "权益支付（下单）接口返回值校验失败"

    return res_data


@allure.step("{step_name}")
def check_service_pay_step(step_name, server_host, res_data):
    logger.info(step_name)

    order_id = jsonpath.jsonpath(res_data, '$.order_id')[0]
    allure.attach(order_id, "订单ID")
    # 校验支付链接格式
    url = jsonpath.jsonpath(res_data, '$.wxqrcode_url')[0]
    url_match = re.match(r'%s/pay/h5/(\w+)' % server_host, url)

    allure.attach(url, "支付Url")
    assert url_match, "支付链接格式校验失败"

    return order_id


@allure.step("{step_name}")
def pay_change_status_step(step_name, server_host, order_id):
    logger.info(step_name)
    order_res = pay_change_status_api(server_host, order_id)

    allure.attach(order_id, "order_id")
    allure.attach(str(order_res.status_code), "Http状态码")
    allure.attach(order_res.request.body, "请求参数")
    assert order_res.status_code == StatusCode.OK.value

    try:
        analysis_result = tcweblib.matchd_result(data_source.common_res_data, order_res.json())
        assert analysis_result
        allure.attach(pformat(order_res.json()), "返回结果")
    except Exception as e:
        allure.attach(pformat(data_source.common_res_data), "预期结果")
        allure.attach(pformat(order_res.json()), "实际结果")
        raise Exception("第三方支付接口返回值校验失败")


@allure.step("{step_name}")
def service_order_result_step(step_name, server_host, product, open_id, token, order_id, pay_channel, pay_type,
                              query_sleep_seconds, expected_res):
    logger.info(step_name)
    # 数据库写入需要等待
    time.sleep(query_sleep_seconds)
    res = service_order_result_api(server_host, product, open_id, token, order_id, pay_channel, pay_type)
    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"权益支付（下单）接口请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "权益支付（下单）接口返回值校验失败"

    pay_status = jsonpath.jsonpath(res_data, '$.data.status')[0]
    expected_pay_status = 0
    allure.attach(str(expected_pay_status), "预期权益支付结果")
    allure.attach(str(pay_status), "实际权益支付结果")
    assert pay_status == expected_pay_status, "权益支付结果校验失败"


@allure.epic('毒霸权益会员 核心流程测试')
@allure.feature('场景：权益会员->用户权限查询->校验用户权益下单')
class TestPermission(object):
    @allure.story('用例：用户权限查询->校验默认用户权限')
    def test_user_permission(self, product_data, create_vip_account, case_config):
        user_origin = case_config["params"]["user_origin"]
        gateway_origin = case_config["params"]["gateway_origin"]

        product = product_data["product"]
        allure.dynamic.description(
            "\t1.通过用户权限查询的接口，获取用户的所有权限情况\n"
            "\t2.校验用户的所有权限情况\n"
            "\t  1)user_permission_list: 用户VIP身份赋予的权限\n"
            "\t  2)permission_list 用户单独购买的权限\n"
            "\t  3)user_all_permission_list 除了身份赋予的权限，还包括单独购买的权限\n"
        )
        allure.dynamic.link("http://apix.kisops.com/project/484/interface/api/17447")

        account_info = create_vip_account
        open_id = account_info["open_id"]
        token = account_info["token"]
        user_identity = account_info["vip_type"]
        allure.dynamic.title(f'用户权限查询 接口：{product_data["product"]} 用户：{VipTypeInfo[user_identity]["name"]}')

        step_1_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data,
                                                         check_remaining_res=False)
        res_data = search_user_permission_step(f"step1：请求用户权限查询{product}接口", gateway_origin, product, open_id,
                                               token, step_1_expected_res)

        check_default_permission_step("step2：校验默认用户权限", user_origin, res_data, user_identity)

    @allure.story('用例：权益下单->权益支付->查询权益支付结果->校验用户权益')
    def test_change_user_permission(self, product_data, create_vip_account, case_config, get_pay_type_data):
        gateway_origin = case_config["params"]["gateway_origin"]
        pay_origin = case_config["params"]["pay_origin"]
        fake_pay_origin = case_config["params"]["fake_pay_origin"]
        query_sleep_seconds = case_config["params"]["query_sleep_seconds"]
        permission_pay_setting = case_config["params"]["permission_pay_setting"]

        product = product_data["product"]
        allure.dynamic.description(
            "\t1.通过权益下单接口下单，获取订单号\n"
            "\t2.通过权益支付接口对该订单进行支付\n"
            "\t3.通过查询权益支付的接口，获取权益支付的结果\n"
            "\t4.最后查询用户的权限，校验用户的各个权限列表\n"
        )
        account_info = create_vip_account
        open_id = account_info["open_id"]
        token = account_info["token"]
        user_identity = account_info["vip_type"]

        pay_setting = PermissionPaySetting[permission_pay_setting]

        allure.dynamic.title(f'检验用户权益下单 接口：{product_data["product"]} 用户：{VipTypeInfo[user_identity]["name"]}')

        # 创建随机客户端server id
        server_id = dubalib.create_server_id()

        # 获取支付类型
        pay_type, pay_type_data = get_pay_type_data
        pay_type_value = pay_type.value
        pay_channel = pay_type_data["pay_channel"].value

        step_1_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        res_data = service_pay_step(f"step1：请求权益下单{product}接口", pay_origin, product, open_id, token, server_id,
                                    pay_setting.value, pay_channel, pay_type_value, step_1_expected_res)

        order_id = check_service_pay_step("step2：校验权益下单结果", fake_pay_origin, res_data)

        pay_change_status_step("step3：权益支付", fake_pay_origin, order_id)

        step_4_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        service_order_result_step("step4：查询权益支付结果", gateway_origin, product, open_id, token, order_id, pay_channel,
                                  pay_type, query_sleep_seconds, step_4_expected_res)

        step_5_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        search_user_permission_step("step5：校验用户权益", gateway_origin, product, open_id, token, step_5_expected_res,
                                    pay_setting)
