import json
import allure
from pprint import pformat
from interface_common import tcweblib
from interface_common.logger import logger
from kwallpaper.api.ugc import ugc_is_likes_api, ugc_likes_paper_api, ugc_likes_paper_list_api
from kwallpaper.cases.test_fish_pay import get_user_info, wplive_index_step, get_filtered_wplive_items
from kwallpaper.constants import ExpectedResult, WallpaperPlatform

"""壁纸-动态壁纸点赞 业务流程测试"""


@allure.step("{step_name}")
def is_likes_step(step_name, server_host, open_id, token, wplive_items, expected_res):
    """查找未点赞壁纸"""
    logger.info(step_name)

    for item in wplive_items:
        wid = item["wid"]
        wname = item["wname"]
        wtype = item["wtype"]
        allure.attach(pformat(item), "壁纸信息")
        res = ugc_is_likes_api(server_host, open_id, token, wtype, wid)

        allure.attach(str(expected_res.status_code), "预期Http状态码")
        allure.attach(str(res.status_code), "实际Http状态码")
        assert res.status_code == expected_res.status_code, f"查询是否点赞过壁纸 {wname} 请求失败 code={res.status_code}"

        res_data = json.loads(res.text)
        allure.attach(pformat(expected_res.res_data), "预期响应结果")
        allure.attach(pformat(res_data), "实际响应结果")
        analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
        assert analysis_result, f"查询是否点赞过壁纸 {wname} 返回值校验失败"

        if res_data["data"][0]["is_likes"] == 0:
            allure.attach(pformat(item), "查找到未点赞动态壁纸信息")
            return item

    return None


@allure.step("{step_name}")
def likes_paper_step(step_name, server_host, open_id, token, wid, wtype, like_wp, expected_res):
    """点赞/取消点赞壁纸"""
    logger.info(step_name)

    if like_wp:
        action = "点赞壁纸"
    else:
        action = "取消点赞壁纸"

    res = ugc_likes_paper_api(server_host, open_id, token, wtype, wid, like=like_wp)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"{action}请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, f"{action}返回值校验失败"


@allure.step("{step_name}")
def likes_paper_list_step(step_name, server_host, open_id, token, wallpaper_platform, expected_res, expected_wid=None,
                          unexpected_wid=None):
    """校验用户点赞过的壁纸"""
    logger.info(step_name)

    res = ugc_likes_paper_list_api(server_host, open_id, token, wallpaper_platform=wallpaper_platform)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"点赞壁纸请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "点赞壁纸返回值校验失败"

    liked_wp_list = res_data["data"]["list"]
    allure.attach(str(liked_wp_list), "已点赞壁纸列表")

    if expected_wid:
        allure.attach(str(expected_wid), "预期已点赞壁纸")

        assert liked_wp_list, "已点赞壁纸列表为空"

        assert len([wp for wp in liked_wp_list if wp["id"] == expected_wid]) > 0, "已点赞壁纸列表校验失败"

    if unexpected_wid:
        allure.attach(str(unexpected_wid), "预期取消点赞壁纸")

        if not liked_wp_list:
            return

        assert len([wp for wp in liked_wp_list if wp["id"] == unexpected_wid]) == 0, "已点赞壁纸列表校验失败"


@allure.epic('壁纸-动态壁纸点赞 业务流程测试')
@allure.feature('场景：创建账号->获取动态壁纸列表->查询未点赞壁纸->点赞壁纸->校验用户点赞过的壁纸->取消点赞壁纸->再次校验用户点赞过的壁纸')
class TestWPLiveLike(object):
    @allure.story("用例：创建账号->获取动态壁纸列表->查询未点赞壁纸->点赞壁纸->校验用户点赞过的壁纸->取消点赞壁纸->再次校验用户点赞过的壁纸 预期成功")
    @allure.description("""
        此用例是针对壁纸-动态壁纸点赞 创建账号->获取动态壁纸列表->查询未点赞壁纸->点赞壁纸->校验用户点赞过的壁纸->取消点赞壁纸->再次校验用户点赞过的壁纸 场景的测试
        Set up:
            1.创建毒霸账号
        step1: 获取动态壁纸列表
            1.请求获取动态壁纸列表接口
            2.校验获取动态壁纸列表接口返回数据的结构和数值
        step2: 查询未点赞壁纸
            1.请求查询未点赞壁纸接口
            2.校验查询未点赞壁纸接口返回数据的结构和数值
            3.返回用户未点赞壁纸的信息
        step3: 点赞壁纸
            1.请求点赞壁纸接口
            2.校验点赞壁纸接口返回数据的结构和数值
        step4: 校验用户点赞过的壁纸
            1.请求点赞壁纸列表接口
            2.校验点赞壁纸列表接口返回数据的结构和数值
            3.校验点赞壁纸列表是否存在用户点赞的壁纸
        step5: 取消点赞壁纸
            1.请求取消点赞壁纸接口
            2.校验取消点赞壁纸接口返回数据的结构和数值
        step6: 再次校验用户点赞过的壁纸
            1.请求用户点赞壁纸列表接口
            2.校验用户点赞壁纸列表接口返回数据的结构和数值
            3.校验用户点赞壁纸列表是否移除用户取消点赞的壁纸
    """)
    @allure.title("创建账号->获取动态壁纸列表->查询未点赞壁纸->点赞壁纸->校验用户点赞过的壁纸->取消点赞壁纸->再次校验用户点赞过的壁纸 预期成功")
    def test_wplive_like_success(self, create_account, case_config):
        server_origin = case_config["params"]["server_origin"]

        # 获取会员账号的 open_id 与 token
        account_info = create_account
        open_id = account_info["open_id"]
        token = account_info["token"]

        # step1: 获取动态壁纸列表
        step_1_expected_res = ExpectedResult()
        wplive_data = wplive_index_step("step1: 获取动态壁纸列表", server_origin, open_id, token, step_1_expected_res)

        wplive_items = wplive_data["items"]
        assert wplive_items is not None, "动态壁纸列表为空"
        # 获取打乱后的动态壁纸列表
        filtered_wplive_items = get_filtered_wplive_items(wplive_items, shuffle=True)

        # step2: 查询未点赞壁纸
        step_2_expected_res = ExpectedResult()
        wp_info = is_likes_step("step2: 查询未点赞壁纸", server_origin, open_id, token, filtered_wplive_items,
                                step_2_expected_res)
        assert wp_info, "查找未点赞动态壁纸失败"

        wid = wp_info["wid"]
        wtype = wp_info["wtype"]

        # step3: 点赞壁纸
        step_3_expected_res = ExpectedResult()
        likes_paper_step("step3: 点赞壁纸", server_origin, open_id, token, wid, wtype, True, step_3_expected_res)

        # step4: 校验用户点赞过的壁纸
        step_4_expected_res = ExpectedResult()
        likes_paper_list_step("step4: 校验用户点赞过的壁纸", server_origin, open_id, token, WallpaperPlatform.PC.value,
                              step_4_expected_res, expected_wid=wid)

        # step5: 取消点赞壁纸
        step_5_expected_res = ExpectedResult()
        likes_paper_step("step5: 取消点赞壁纸", server_origin, open_id, token, wid, wtype, False, step_5_expected_res)

        # step6: 再次校验用户点赞过的壁纸
        step_6_expected_res = ExpectedResult()
        likes_paper_list_step("step6: 再次校验用户点赞过的壁纸", server_origin, open_id, token, WallpaperPlatform.PC.value,
                              step_6_expected_res, unexpected_wid=wid)
