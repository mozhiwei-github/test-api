import time
import json
import allure
import random
import jsonpath
from pprint import pformat
from duba.api.user import user_info_api, modify_user_info_api, user_info_avatar_api
from duba.constants import VipTypeInfo, StatusCode
from duba.config import data_source
from interface_common.logger import logger
from interface_common import tcweblib
import duba.dubalib as dubalib

"""毒霸用户信息模块 业务流程测试"""


@allure.step("step1: 查询用户信息")
def modify_step_1(server_host, product, open_id, token, expected_res):
    logger.info("step1: 查询用户信息")
    # 发起查询用户详细信息请求
    res = user_info_api(server_host, product, open_id, token)
    # 校验用户详细信息结果
    nickname, avatar_url = check_user_info_result(res, expected_res)
    return nickname, avatar_url


@allure.step("step2: 获取用户头像库")
def modify_step_2(server_host, product, open_id, token, expected_res):
    logger.info("step2: 获取用户头像库")
    # 发起获取用户头像库请求
    res = user_info_avatar_api(server_host, product, open_id, token)
    # 校验获取用户头像库结果
    avatar_list = check_user_info_avatar_result(res, expected_res)
    return avatar_list


@allure.step("step3: 修改用户信息")
def modify_step_3(server_host, product, open_id, token, nickname, avatar_id, expected_res):
    logger.info("step3: 修改用户信息")
    # 发起修改用户信息请求
    res = modify_user_info_api(server_host, product, open_id, token, nickname, avatar_id)
    # 校验修改用户信息结果
    check_modify_user_info_result(res, expected_res)


@allure.step("step4: 用户信息查询校验")
def modify_step_4(server_host, product, open_id, token, expected_res, modify_info, query_sleep_seconds):
    logger.info("step4: 用户信息查询校验")
    # 等待N秒，再查询用户信息修改是否成功
    time.sleep(query_sleep_seconds)
    # 发起查询用户详细信息请求
    res = user_info_api(server_host, product, open_id, token)
    # 校验用户详细信息结果
    check_user_info_result(res, expected_res, modify_info)


def check_user_info_result(res, expected_res, modify_info=None):
    """
    校验用户详细信息结果
    @param res: 用户详细信息接口响应结果
    @param expected_res: 预期结果结构体 ExpectedResult
    @param modify_info: 已修改的用户信息
    @return:
    """
    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, \
        "[test_modify_user_info]用户详细信息接口请求失败 code=%d" % res.status_code

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "[test_modify_user_info]用户详细信息接口返回值校验失败"

    user_info = jsonpath.jsonpath(res_data, '$.data.user_info')[0]
    allure.attach(pformat(user_info), "用户详细信息")
    nickname = user_info["nickname"]
    avatar_url = user_info["avatar"]

    # 没有改动用户信息则不进行字段相关校验
    if modify_info is None:
        return nickname, avatar_url

    expected_nickname = modify_info["nickname"]
    expected_avatar_url = modify_info["avatar"]["url"]

    allure.attach(expected_nickname, "预期用户昵称")
    allure.attach(nickname, "实际用户昵称")
    allure.attach(expected_avatar_url, "预期用户头像")
    allure.attach(avatar_url, "实际用户头像")

    # 校验用户昵称是否修改成功
    assert nickname == expected_nickname, "用户昵称校验失败"
    # 校验用户头像是否修改成功
    assert avatar_url == expected_avatar_url, "用户头像校验失败"


def check_user_info_avatar_result(res, expected_res):
    """
    校验获取用户头像库结果
    @param res: 获取用户头像库接口响应结果
    @param expected_res: 预期结果结构体 ExpectedResult
    @return:
        avatar_list: 用户头像库列表
    """
    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, \
        "[test_modify_user_info]获取用户信息头像库接口请求失败 code=%d" % res.status_code

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "[test_modify_user_info]用户信息头像库接口返回值校验失败"

    avatar_list = jsonpath.jsonpath(res_data, '$.avatar_list')[0]
    assert avatar_list, "获取头像库列表字段失败"
    allure.attach(pformat(avatar_list), "头像库列表")

    assert len(avatar_list) > 0, "头像库列表为空"

    return avatar_list


def check_modify_user_info_result(res, expected_res):
    """
    校验修改用户信息结果
    @param res: 修改用户信息接口响应结果
    @param expected_res: 预期结果结构体 ExpectedResult
    @return:
    """
    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, "[test_modify_user_info]修改用户信息接口请求失败 code=%d" % res.status_code

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "[test_modify_user_info]用修改用户信息接口返回值校验失败"


@allure.epic("毒霸用户信息模块 业务流程测试")
@allure.feature('场景：查询用户信息->获取用户头像库->修改用户信息->用户信息查询校验')
class TestModifyUserInfo(object):
    # @pytest.mark.skip("测试其他用例，跳过此用例")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("用例：查询用户信息->获取用户头像库->修改用户信息->用户信息查询校验 预期成功")
    @allure.description("""
        此用例是针对毒霸会员 查询用户信息->获取用户头像库->修改用户信息->用户信息查询校验 场景的测试
        Set up:
            1.创建会员账号
            2.获取禁忌词列表
        Step1: 查询用户信息
            1.获取用户详细信息
            2.校验用户详细信息接口返回数据的结构和数值
        Step2: 获取用户头像库
            1.请求获取用户头像库接口
            2.校验获取用户头像库接口返回数据的结构和数值
            3.获取用户头像库列表
        Step3: 修改用户信息
            1.使用随机生成的用户名和随机从头像库列表中选择的头像修改用户信息
            2.校验修改用户信息接口返回数据的结构和数值
        Step4: 用户信息查询校验
            1.再次获取用户详细信息
            2.校验用户详细信息接口返回数据的结构和数值
            3.校验用户信息是否修改成功
        """)
    @allure.title("查询用户信息->获取用户头像库->修改用户信息->用户信息查询校验 预期成功")
    def test_modify_success(self, product_data, create_vip_account, get_forbid_words, case_config):
        gateway_origin = case_config["params"]["gateway_origin"]
        query_sleep_seconds = case_config["params"]["query_sleep_seconds"]

        product = product_data["product"]

        # 获取会员账号的 open_id 与 token
        account_info = create_vip_account
        open_id = account_info["open_id"]
        token = account_info["token"]
        user_vip_type = account_info["vip_type"]
        user_vip_name = VipTypeInfo[user_vip_type]["name"]

        allure.dynamic.title("毒霸新会员{product} {user_vip_name}用户".format(product=product, user_vip_name=user_vip_name))

        # step1: 查询用户信息
        step_1_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        modify_step_1(gateway_origin, product, open_id, token, step_1_expected_res)

        # step2: 获取用户头像库
        step_2_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        avatar_list = modify_step_2(gateway_origin, product, open_id, token, step_2_expected_res)

        # 随机选择一个头像库列表中的头像
        avatar = random.choice(avatar_list)
        # 随机生成一个用户昵称
        nickname = dubalib.get_nickname(get_forbid_words)
        # step3: 修改用户信息
        step_3_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        modify_step_3(gateway_origin, product, open_id, token, nickname, avatar["id"], step_3_expected_res)

        modify_info = {
            "nickname": nickname,
            "avatar": avatar
        }
        # step4: 用户信息查询校验
        step_4_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        modify_step_4(gateway_origin, product, open_id, token, step_4_expected_res, modify_info, query_sleep_seconds)

    # @pytest.mark.skip("测试其他用例，跳过此用例")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("用例：查询用户信息->获取用户头像库->修改用户信息->用户信息查询校验 预期失败（用户昵称存在禁忌词）")
    @allure.description("""
        此用例是针对毒霸会员 查询用户信息->获取用户头像库->修改用户信息->用户信息查询校验 场景的测试
        Set up:
            1.创建会员账号
            2.获取禁忌词列表
        Step1: 查询用户信息
            1.获取用户详细信息
            2.校验用户详细信息接口返回数据的结构和数值
        Step2: 获取用户头像库
            1.请求获取用户头像库接口
            2.校验获取用户头像库接口返回数据的结构和数值
            3.获取用户头像库列表
        Step3: 修改用户信息
            1.使用随机生成含有禁忌词的用户昵称和随机从头像库列表中选择的头像修改用户信息
            2.校验修改用户信息接口返回数据的结构和数值
        Step4: 用户信息查询校验
            1.再次获取用户详细信息
            2.校验用户详细信息接口返回数据的结构和数值
            3.校验用户信息是否修改成功
        """)
    @allure.title("查询用户信息->获取用户头像库->修改用户信息->用户信息查询校验 预期失败（用户昵称存在禁忌词）")
    def test_modify_forbid_failure(self, product_data, create_vip_account, get_forbid_words, case_config):
        gateway_origin = case_config["params"]["gateway_origin"]
        query_sleep_seconds = case_config["params"]["query_sleep_seconds"]

        product = product_data["product"]

        # 获取会员账号的 open_id 与 token
        account_info = create_vip_account
        open_id = account_info["open_id"]
        token = account_info["token"]
        user_vip_type = account_info["vip_type"]
        user_vip_name = VipTypeInfo[user_vip_type]["name"]

        allure.dynamic.title("毒霸新会员{product} {user_vip_name}用户 用户昵称存在禁忌词".format(product=product,
                                                                                 user_vip_name=user_vip_name))

        # step1: 查询用户信息
        step_1_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        before_nickname, before_avatar_url = modify_step_1(gateway_origin, product, open_id, token, step_1_expected_res)

        # step2: 获取用户头像库
        step_2_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        avatar_list = modify_step_2(gateway_origin, product, open_id, token, step_2_expected_res)

        # 随机选择一个头像库列表中的头像
        avatar = random.choice(avatar_list)
        # 随机生成一个含有禁忌词的用户昵称
        nickname = dubalib.get_forbid_nickname(get_forbid_words)
        # step3: 修改用户信息
        step_3_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.forbid_nickname_res_data)
        modify_step_3(gateway_origin, product, open_id, token, nickname, avatar["id"], step_3_expected_res)

        modify_info = {
            "nickname": before_nickname,
            "avatar": {
                "url": before_avatar_url
            }
        }
        # step4: 用户信息查询校验
        step_4_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
        modify_step_4(gateway_origin, product, open_id, token, step_4_expected_res, modify_info, query_sleep_seconds)
