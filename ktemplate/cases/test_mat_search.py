import json
import allure
import random
from pprint import pformat
from interface_common import tcweblib
from interface_common.logger import logger
from ktemplate.api.conf import conf_get_api
from ktemplate.api.mat import mat_search_v2_api
from ktemplate.constants import ExpectedResult

"""完美办公-素材搜索 业务流程测试"""


@allure.step("{step_name}")
def hot_search_step(step_name, server_host, uid, token, expected_res):
    """获取热门搜索配置"""
    logger.info(step_name)

    res = conf_get_api(server_host, uid, token, conf_code="miniHotSearch")

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"获取热门搜索配置请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "获取热门搜索配置返回值校验失败"

    hot_search_conf = res_data["data"]["content"].split(",")
    allure.attach(str(hot_search_conf), "热门搜索配置")
    assert len(hot_search_conf) > 0, "热门搜索配置为空"

    return hot_search_conf


@allure.step("{step_name}")
def default_search_step(step_name, server_host, uid, token, expected_res):
    """获取默认搜索配置"""
    logger.info(step_name)

    res = conf_get_api(server_host, uid, token, conf_code="mini-defaultSearch")

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"获取默认搜索配置请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "获取默认搜索配置返回值校验失败"

    default_search_conf = res_data["data"]["content"]
    allure.attach(str(default_search_conf), "默认搜索配置")
    assert default_search_conf, "默认搜索配置为空"

    return default_search_conf


@allure.step("{step_name}")
def mat_search_step(step_name, server_host, uid, token, keyword, expected_res):
    """素材搜索"""
    logger.info(step_name)

    res = mat_search_v2_api(server_host, uid, token, keyword, cat1=0)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"素材搜索请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "素材搜索返回值校验失败"

    cat_result_list = res_data["cat_results"]
    assert len(cat_result_list) > 0, "素材搜索结果分类为空"
    mat_list = res_data["list"]
    allure.attach(pformat(mat_list), "素材搜索结果列表")
    assert len(mat_list) > 0, "素材搜索结果列表为空"

    return cat_result_list, mat_list


@allure.epic('完美办公-素材搜索 业务流程测试')
@allure.feature('场景：创建账号->获取热门搜索配置->获取默认搜索配置->素材搜索')
class TestMatSearch(object):
    @allure.story("用例：创建账号->获取热门搜索配置->获取默认搜索配置->素材搜索 预期成功")
    @allure.description("""
        此用例是针对完美办公-素材搜索 创建账号->获取热门搜索配置->获取默认搜索配置->素材搜索 场景的测试
        Set up:
            1.创建账号
        step1: 获取热门搜索配置
            1.请求获取热门搜索配置接口
            2.校验获取热门搜索配置接口返回数据的结构和数值
            3.返回热门搜索词列表
        step2: 获取默认搜索配置
            1.请求获取默认搜索配置接口
            2.校验获取默认搜索配置接口返回数据的结构和数值
            3.返回默认搜索词列表
        step3: 素材搜索
            1.随机选择一个热门/默认搜索词，请求素材搜索接口
            2.校验素材搜索接口返回数据的结构和数值
    """)
    def test_mat_search_success(self, create_account, case_config):
        server_origin = case_config["params"]["server_origin"]

        # 获取会员账号的 uid 与 token
        account_info = create_account
        uid = account_info["uid"]
        token = account_info["token"]
        vip_type = account_info["vip_type"]

        allure.dynamic.title(f"创建账号->获取热门搜索配置->获取默认搜索配置->素材搜索（{vip_type.value}） 预期成功")

        # step1: 获取热门搜索配置
        step_1_expected_res = ExpectedResult()
        hot_search_conf = hot_search_step("step1: 获取热门搜索配置", server_origin, uid, token, step_1_expected_res)

        # step2: 获取默认搜索配置
        step_2_expected_res = ExpectedResult()
        default_search_conf = default_search_step("step2: 获取默认搜索配置", server_origin, uid, token, step_2_expected_res)

        search_keyword = random.choice(hot_search_conf + [default_search_conf])

        # step3: 素材搜索
        step_3_expected_res = ExpectedResult()
        mat_search_step("step3: 素材搜索", server_origin, uid, token, search_keyword, step_3_expected_res)
