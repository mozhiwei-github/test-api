import json
import random
import allure
from pprint import pformat
from interface_common import tcweblib
from interface_common.logger import logger
from kwallpaper.api.fans import fans_following_create_api, fans_following_cancel_api, fans_following_list_api
from kwallpaper.api.popularity import pc_popularity_author_list_api
from kwallpaper.cases.test_fish_pay import get_user_info
from kwallpaper.constants import ExpectedResult

"""壁纸-动态壁纸点赞 业务流程测试"""


@allure.step("{step_name}")
def popularity_author_list_step(step_name, server_host, open_id, token, expected_res):
    """PC人气作者列表"""
    logger.info(step_name)

    res = pc_popularity_author_list_api(server_host, open_id, token)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"PC人气作者列表请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "PC人气作者列表返回值校验失败"

    author_list = res_data["author_list"]
    allure.attach(pformat(author_list), "PC人气作者列表")
    return author_list


def get_filtered_author_list(author_list, is_following=None, shuffle=False, following_list=None):
    """
    获取过滤后的人气作者列表
    @param author_list: 人气作者列表
    @param is_following: 是否关注
    @param shuffle: 是否打乱列表
    @param following_list: 关注人列表
    @return:
    """
    result = []
    if following_list is not None:
        following_id_list = [i["uid"] for i in following_list]

    for author in author_list:
        if is_following is not None and following_id_list is not None:
            if is_following != (str(author["uid"]) in following_id_list):
                continue

        result.append(author)

    if shuffle:
        random.shuffle(result)

    return result


@allure.step("{step_name}")
def fans_following_create_step(step_name, server_host, open_id, token, uid, expected_res):
    """关注作者"""
    logger.info(step_name)

    res = fans_following_create_api(server_host, open_id, token, uid)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"关注作者请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "关注作者返回值校验失败"


@allure.step("{step_name}")
def fans_following_list_step(step_name, server_host, open_id, token, uid, expected_res, expected_uid=None,
                             unexpected_uid=None):
    """查询关注人列表"""
    logger.info(step_name)

    res = fans_following_list_api(server_host, open_id, token, uid)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"查询关注人列表请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "查询关注人列表返回值校验失败"

    following_list = res_data["following_list"]
    allure.attach(pformat(following_list), "关注人列表")

    if expected_uid:
        allure.attach(str(expected_uid), "预期关注作者UID")

        assert following_list, "关注人列表为空"

        assert len([i for i in following_list if i["uid"] == expected_uid]) > 0, "关注人列表校验失败"

    if unexpected_uid:
        allure.attach(str(unexpected_uid), "预期取消关注作者UID")

        if not following_list:
            return

        assert len([i for i in following_list if i["uid"] == unexpected_uid]) == 0, "关注人列表校验失败"

    return following_list


@allure.step("{step_name}")
def fans_following_cancel_step(step_name, server_host, open_id, token, uid, expected_res):
    """取消关注作者"""
    logger.info(step_name)

    res = fans_following_cancel_api(server_host, open_id, token, uid)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"取消关注作者请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "取消关注作者返回值校验失败"


@allure.epic('壁纸-人气作者专区关注 业务流程测试')
@allure.feature('场景：创建账号->获取PC人气作者列表->关注作者->查询关注人列表->取消关注作者->再次查询关注人列表')
class TestPopularityAuthorFollow(object):
    @allure.story("用例：创建账号->获取PC人气作者列表->关注作者->查询关注人列表->取消关注作者->再次查询关注人列表 预期成功")
    @allure.description("""
        此用例是针对壁纸-人气作者专区关注 创建账号->获取PC人气作者列表->关注作者->查询关注人列表->取消关注作者->再次查询关注人列表 场景的测试
        Set up:
            1.创建毒霸账号
        step1: 获取PC人气作者列表
            1.请求获取PC人气作者列表接口
            2.校验获取PC人气作者列表接口返回数据的结构和数值
            3.返回用户未关注作者的信息
        step2: 关注作者
            1.请求关注作者接口
            2.校验关注作者接口返回数据的结构和数值
        step3: 查询关注人列表
            1.请求查询关注人列表接口
            2.校验查询关注人列表接口返回数据的结构和数值
            3.校验关注人列表是否存在用户关注的作者
        step4: 取消关注作者
            1.请求取消关注作者接口
            2.校验取消关注作者接口返回数据的结构和数值
        step5: 再次查询关注人列表
            1.请求查询关注人列表接口
            2.校验查询关注人列表接口返回数据的结构和数值
            3.校验关注人列表是否移除用户取消关注的作者
    """)
    @allure.title("创建账号->获取PC人气作者列表->关注作者->查询关注人列表->取消关注作者->再次查询关注人列表 预期成功")
    def test_popularity_author_follow_success(self, create_account, case_config):
        server_origin = case_config["params"]["server_origin"]

        # 获取会员账号的 open_id 与 token
        account_info = create_account
        open_id = account_info["open_id"]
        token = account_info["token"]

        # 获取用户信息
        expected_user_info_res = ExpectedResult()
        user_info = get_user_info("获取用户信息", server_origin, open_id, token, expected_user_info_res)
        uid = str(user_info["uid"])

        # 获取关注人列表
        expected_following_list_res = ExpectedResult()
        my_following_list = fans_following_list_step("获取关注人列表", server_origin, open_id, token, uid,
                                                     expected_following_list_res)

        # step1: 获取PC人气作者列表
        step_1_expected_res = ExpectedResult()
        author_list = popularity_author_list_step("step1: 获取PC人气作者列表", server_origin, open_id, token,
                                                  step_1_expected_res)

        assert author_list is not None, "PC人气作者列表为空"
        # 获取打乱后的未关注作者列表
        filtered_author_list = get_filtered_author_list(author_list, is_following=False, shuffle=True,
                                                        following_list=my_following_list)
        assert filtered_author_list, "获取未关注作者列表失败"

        author_uid = str(filtered_author_list[0]["uid"])
        # step2: 关注作者
        step_2_expected_res = ExpectedResult()
        fans_following_create_step("step2: 关注作者", server_origin, open_id, token, author_uid, step_2_expected_res)

        # step3: 查询关注人列表
        step_3_expected_res = ExpectedResult()
        fans_following_list_step("step3: 查询关注人列表", server_origin, open_id, token, uid, step_3_expected_res,
                                 expected_uid=author_uid)

        # step4: 取消关注作者
        step_4_expected_res = ExpectedResult()
        fans_following_cancel_step("step4: 取消关注作者", server_origin, open_id, token, author_uid, step_4_expected_res)

        # step5: 再次查询关注人列表
        step_5_expected_res = ExpectedResult()
        fans_following_list_step("step5: 再次查询关注人列表", server_origin, open_id, token, uid, step_5_expected_res,
                                 unexpected_uid=author_uid)
