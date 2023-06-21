import json
import allure
import random
from pprint import pformat
from interface_common import tcweblib
from interface_common.logger import logger
from ktemplate.api.user import user_favorite_ids_api, user_favorite_add_api, user_favorite_remove_api, \
    user_favorite_list_api
from ktemplate.cases.test_mat_list import category_list_step, mat_list_step
from ktemplate.constants import ExpectedResult

"""完美办公-素材收藏 业务流程测试"""


@allure.step("{step_name}")
def user_favorite_ids_step(step_name, server_host, uid, token, expected_res):
    """获取用户所有收藏素材ID"""
    logger.info(step_name)

    res = user_favorite_ids_api(server_host, uid, token)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"获取用户所有收藏素材ID请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "获取用户所有收藏素材ID返回值校验失败"

    favorite_id_list = res_data["list"]
    allure.attach(str(favorite_id_list), "用户所有收藏素材ID")

    return favorite_id_list


@allure.step("{step_name}")
def user_favorite_add_step(step_name, server_host, uid, token, mat_id, expected_res):
    """添加收藏素材"""
    logger.info(step_name)

    res = user_favorite_add_api(server_host, uid, token, mat_id)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"添加收藏素材请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "添加收藏素材返回值校验失败"


@allure.step("{step_name}")
def user_favorite_remove_step(step_name, server_host, uid, token, mat_id, expected_res):
    """取消收藏素材"""
    logger.info(step_name)

    res = user_favorite_remove_api(server_host, uid, token, mat_id)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"取消收藏素材请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "取消收藏素材返回值校验失败"


@allure.step("{step_name}")
def user_favorite_list_step(step_name, server_host, uid, token, cat1, expected_res):
    """获取用户收藏记录"""
    logger.info(step_name)

    res = user_favorite_list_api(server_host, uid, token, cat1)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"获取用户收藏记录请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "获取用户收藏记录返回值校验失败"

    fav_info_list = res_data["fav_infos"]
    allure.attach(pformat(fav_info_list), "用户收藏记录")

    return fav_info_list


def get_not_favorite_mat_list(mat_list, favorite_id_list):
    """
    获取未收藏素材列表
    @param mat_list: 素材列表
    @param favorite_id_list: 用户所有收藏素材ID列表
    @return:
    """
    not_favorite_mat_list = []
    for mat in mat_list:
        if mat["id"] not in favorite_id_list:
            not_favorite_mat_list.append(mat)
    return not_favorite_mat_list


@allure.epic('完美办公-素材收藏 业务流程测试')
@allure.feature('场景：创建账号->获取分类总览->获取分类素材列表->获取用户所有收藏素材ID->添加收藏素材->获取用户收藏记录->取消收藏素材')
class TestMatFavorite(object):
    @allure.story("用例：创建账号->获取分类总览->获取分类素材列表->获取用户所有收藏素材ID->添加收藏素材->获取用户收藏记录->取消收藏素材 预期成功")
    @allure.description("""
        此用例是针对完美办公-素材收藏 创建账号->获取分类总览->获取分类素材列表->获取用户所有收藏素材ID->添加收藏素材->获取用户收藏记录->取消收藏素材 场景的测试
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
        step3: 获取用户所有收藏素材ID
            1.请求获取用户所有收藏素材ID接口
            2.校验获取用户所有收藏素材ID接口返回数据的结构和数值
            3.根据用户所有收藏素材ID过滤出用户未收藏分类素材列表
        step4: 添加收藏素材
            1.随机选择一个用户未收藏分类素材，请求添加收藏素材接口
            2.校验添加收藏素材接口返回数据的结构和数值
        step5: 获取用户收藏记录
            1.请求获取用户收藏记录接口
            2.校验获取用户收藏记录接口返回数据的结构和数值
            3.校验刚才添加收藏的素材是否在用户收藏记录中
        step6: 取消收藏素材
            1.请求取消收藏素材接口
            2.校验取消收藏素材接口返回数据的结构和数值
    """)
    def test_mat_favorite_success(self, create_account, case_config):
        server_origin = case_config["params"]["server_origin"]

        # 获取会员账号的 uid 与 token
        account_info = create_account
        uid = account_info["uid"]
        token = account_info["token"]
        vip_type = account_info["vip_type"]

        allure.dynamic.title(f"创建账号->获取分类总览->获取分类素材列表->获取用户所有收藏素材ID->添加收藏素材->获取用户收藏记录->取消收藏素材（{vip_type.value}） 预期成功")

        # step1: 获取分类总览
        step_1_expected_res = ExpectedResult()
        category_list = category_list_step("step1: 获取分类总览", server_origin, uid, token, step_1_expected_res)

        cat1_info = random.choice(category_list)
        cat1 = cat1_info["id"]
        cat2_info = random.choice(cat1_info["list"])
        cat3_info = random.choice(cat2_info["list"])

        # step2: 获取分类素材列表
        step_2_expected_res = ExpectedResult()
        mat_list = mat_list_step("step2: 获取分类素材列表", server_origin, uid, token, cat1, cat2_info["id"],
                                 cat3_info["id"], step_2_expected_res)

        # step3: 获取用户所有收藏素材ID
        step_3_expected_res = ExpectedResult()
        favorite_id_list = user_favorite_ids_step("step3: 获取用户所有收藏素材ID", server_origin, uid, token, step_3_expected_res)

        not_favorite_mat_list = get_not_favorite_mat_list(mat_list, favorite_id_list)
        assert not_favorite_mat_list, "用户未收藏素材列表为空"

        mat_id = random.choice(not_favorite_mat_list)["id"]

        # step4: 添加收藏素材
        step_4_expected_res = ExpectedResult()
        user_favorite_add_step("step4: 添加收藏素材", server_origin, uid, token, mat_id, step_4_expected_res)

        # step5: 获取用户收藏记录
        step_5_expected_res = ExpectedResult()
        fav_info_list = user_favorite_list_step("step5: 获取用户收藏记录", server_origin, uid, token, cat1, step_5_expected_res)
        assert len([mat for mat in fav_info_list if mat["mat_id"] == mat_id]) == 1, "用户收藏记录未找到收藏素材"

        # step6: 取消收藏素材
        step_6_expected_res = ExpectedResult()
        user_favorite_remove_step("step6: 取消收藏素材", server_origin, uid, token, mat_id, step_6_expected_res)
