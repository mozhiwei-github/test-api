import json
import allure
import random
from pprint import pformat
from interface_common import tcweblib
from interface_common.logger import logger
from ktemplate.api.mat import category_list_api, mat_list_v2_api, mat_detail_api
from ktemplate.constants import ExpectedResult

"""完美办公-素材列表 业务流程测试"""


@allure.step("{step_name}")
def category_list_step(step_name, server_host, uid, token, expected_res):
    """获取分类总览"""
    logger.info(step_name)

    res = category_list_api(server_host, uid, token)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"获取分类总览请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "获取分类总览返回值校验失败"

    category_list = res_data["list"]
    allure.attach(str(category_list), "分类总览列表")
    assert len(category_list) > 0, "分类总览列表为空"

    return category_list


@allure.step("{step_name}")
def mat_list_step(step_name, server_host, uid, token, cat1, cat2, cat3, expected_res):
    """获取分类素材列表"""
    logger.info(step_name)

    res = mat_list_v2_api(server_host, uid, token, cat1=cat1, cat2=cat2, cat3=cat3)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"获取分类素材列表请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "获取分类素材列表返回值校验失败"

    mat_list = res_data["list"]
    allure.attach(str(mat_list), "分类素材列表")
    assert len(mat_list) > 0, "分类素材列表为空"

    return mat_list


@allure.step("{step_name}")
def mat_detail_step(step_name, server_host, uid, token, mat_id, expected_res):
    """获取素材详细信息"""
    logger.info(step_name)

    res = mat_detail_api(server_host, uid, token, mat_id)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"获取素材详细信息请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "获取素材详细信息返回值校验失败"

    cat_info = res_data["info"]
    allure.attach(pformat(cat_info), "素材详细信息")
    assert cat_info, "素材详细信息为空"

    return cat_info


@allure.epic('完美办公-素材列表 业务流程测试')
@allure.feature('场景：创建账号->获取分类总览->获取分类素材列表->获取素材详细信息')
class TestMatList(object):
    @allure.story("用例：创建账号->获取分类总览->获取分类素材列表->获取素材详细信息 预期成功")
    @allure.description("""
        此用例是针对完美办公-素材列表 创建账号->获取分类总览->获取分类素材列表->获取素材详细信息 场景的测试
        Set up:
            1.创建账号
        step1: 获取分类总览
            1.请求获取分类总览接口
            2.校验获取分类总览接口返回数据的结构和数值
            3.返回分类总览列表
        step2: 获取分类素材列表
            1.随机选择分类，请求获取分类素材列表接口
            2.校验获取分类素材列表接口返回数据的结构和数值
            3.返回分类素材列表
        step3: 获取素材详细信息
            1.随机选择一个分类素材，请求获取素材详细信息接口
            2.校验获取素材详细信息接口返回数据的结构和数值
    """)
    def test_mat_list_success(self, create_account, case_config):
        server_origin = case_config["params"]["server_origin"]

        # 获取会员账号的 uid 与 token
        account_info = create_account
        uid = account_info["uid"]
        token = account_info["token"]
        vip_type = account_info["vip_type"]

        allure.dynamic.title(f"创建账号->获取分类总览->获取分类素材列表->获取素材详细信息（{vip_type.value}） 预期成功")

        # step1: 获取分类总览
        step_1_expected_res = ExpectedResult()
        category_list = category_list_step("step1: 获取分类总览", server_origin, uid, token, step_1_expected_res)

        cat1_info = random.choice(category_list)
        cat2_info = random.choice(cat1_info["list"])
        cat3_info = random.choice(cat2_info["list"])

        # step2: 获取分类素材列表
        step_2_expected_res = ExpectedResult()
        mat_list = mat_list_step("step2: 获取分类素材列表", server_origin, uid, token, cat1_info["id"], cat2_info["id"],
                                 cat3_info["id"], step_2_expected_res)

        mat_id = random.choice(mat_list)["id"]

        # step3: 获取素材详细信息
        step_3_expected_res = ExpectedResult()
        mat_detail_step("step3: 获取素材详细信息", server_origin, uid, token, mat_id, step_3_expected_res)
