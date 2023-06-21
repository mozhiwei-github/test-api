import json
import allure
from pprint import pformat
from interface_common import tcweblib
from interface_common.logger import logger
from kwallpaper.api.wpstatic import wpstatic_cate_nav_api, wpstatic_list_api, wpstatic_index_api
from kwallpaper.constants import ExpectedResult

"""壁纸-静态壁纸分类导航 业务流程测试"""


@allure.step("{step_name}")
def wpstatic_index_step(step_name, server_host, open_id, token, expected_res):
    """获取静态壁纸首页"""
    logger.info(step_name)

    res = wpstatic_index_api(server_host, open_id, token)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"获取静态壁纸首页请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "获取静态壁纸首页返回值校验失败"

    return res_data["data"]


@allure.step("{step_name}")
def wpstatic_cate_nav_step(step_name, server_host, open_id, token, expected_res):
    """获取静态壁纸分类导航"""
    logger.info(step_name)

    res = wpstatic_cate_nav_api(server_host, open_id, token)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"获取静态壁纸分类导航请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "获取静态壁纸分类导航返回值校验失败"

    return res_data["data"]


@allure.step("{step_name}")
def wpstatic_list_by_cate_step(step_name, server_host, open_id, token, cate_nav_list, expected_res):
    """获取各分类静态壁纸列表"""
    logger.info(step_name)

    for cate_nav in cate_nav_list:
        cate_id = cate_nav.get("cid", None)
        tag_id = cate_nav.get("tid", None)
        cate_nav_name = cate_nav.get("cname", None) or cate_nav.get("tname", "")
        display_name = f"获取{cate_nav_name}分类静态壁纸列表"
        res = wpstatic_list_api(server_host, open_id, token, cate_id, tag_id, display_name=display_name)

        allure.attach(str(expected_res.status_code), "预期Http状态码")
        allure.attach(str(res.status_code), "实际Http状态码")
        assert res.status_code == expected_res.status_code, f"{display_name}请求失败 code={res.status_code}"

        res_data = json.loads(res.text)
        allure.attach(pformat(expected_res.res_data), "预期响应结果")
        allure.attach(pformat(res_data), "实际响应结果")
        analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
        assert analysis_result, f"{display_name}返回值校验失败"

        assert res_data["data"]["list"], f"{cate_nav_name}分类静态壁纸列表为空"

    return


@allure.epic('壁纸-静态壁纸分类导航 业务流程测试')
@allure.feature('场景：创建账号->获取静态壁纸首页->获取静态壁纸分类导航->获取各分类静态壁纸列表')
class TestWallpaperStaticNav(object):
    @allure.story("用例：创建账号->获取静态壁纸首页->获取静态壁纸分类导航->获取各分类静态壁纸列表 预期成功")
    @allure.description("""
        此用例是针对壁纸-静态壁纸分类导航 创建账号->获取静态壁纸首页->获取静态壁纸分类导航->获取各分类静态壁纸列表 场景的测试
        Set up:
            1.创建毒霸账号
        step1: 获取静态壁纸首页
            1.请求获取静态壁纸首页接口
            2.校验获取静态壁纸首页接口返回数据的结构和数值
        step2: 获取静态壁纸分类导航
            1.请求获取静态壁纸分类导航接口
            2.校验获取静态壁纸分类导航接口返回数据的结构和数值
        step3: 获取各分类静态壁纸列表
            1.根据分类导航数据依次请求获取各分类静态壁纸列表接口
            2.校验获取各分类静态壁纸列表接口返回数据的结构和数值
    """)
    @allure.title("创建账号->获取静态壁纸首页->获取静态壁纸分类导航->获取各分类静态壁纸列表 预期成功")
    def test_wpstatic_nav_success(self, create_account, case_config):
        server_origin = case_config["params"]["server_origin"]

        # 获取会员账号的 open_id 与 token
        account_info = create_account
        open_id = account_info["open_id"]
        token = account_info["token"]

        # step1: 获取静态壁纸首页
        step_1_expected_res = ExpectedResult()
        wpstatic_index_list = wpstatic_index_step("step1: 获取静态壁纸首页", server_origin, open_id, token, step_1_expected_res)

        assert wpstatic_index_list, "静态壁纸首页为空"

        # step2: 获取静态壁纸分类导航
        step_2_expected_res = ExpectedResult()
        wpstatic_cate_list = wpstatic_cate_nav_step("step2: 获取静态壁纸分类导航", server_origin, open_id, token,
                                                    step_2_expected_res)
        assert wpstatic_cate_list, "静态壁纸分类导航为空"

        # step3: 获取各分类静态壁纸列表
        step_3_expected_res = ExpectedResult()
        wpstatic_list_by_cate_step("step3: 获取各分类静态壁纸列表", server_origin, open_id, token, wpstatic_cate_list,
                                   step_3_expected_res)
