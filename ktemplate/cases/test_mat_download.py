import json
import allure
import random
from pprint import pformat
from datetime import datetime
from interface_common import tcweblib
from interface_common.logger import logger
from interface_common.http_request import HTTPRequest, log_handler
from ktemplate.api.mat import mat_download_api
from ktemplate.api.user import user_downloads_api
from ktemplate.cases.test_mat_list import category_list_step, mat_list_step
from ktemplate.constants import ExpectedResult

"""完美办公-素材下载 业务流程测试"""


@allure.step("{step_name}")
def mat_download_step(step_name, server_host, uid, token, mat_id, expected_res):
    """素材下载"""
    logger.info(step_name)

    res = mat_download_api(server_host, uid, token, mat_id)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"素材下载请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "素材下载返回值校验失败"

    download_url = res_data["url"]
    allure.attach(str(download_url), "素材下载链接")
    assert download_url, "素材下载链接为空"

    return download_url


@allure.step("{step_name}")
def mat_download_url_step(step_name, url, expected_res):
    """请求素材下载链接"""
    logger.info(step_name)

    res = HTTPRequest.request_get(url)
    log_handler(res, "请求素材下载链接", attach_allure=True, decode_res_data=False)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"素材下载链接请求失败 code={res.status_code}"

    allure.attach(pformat(dict(res.headers)), "素材下载链接响应Headers")

    content_type = res.headers["Content-Type"]
    allure.attach(str(content_type), "素材文件类型")
    assert content_type != "application/xml", "素材文件类型检验异常"

    content_length = res.headers["Content-Length"]
    allure.attach(str(content_length), "素材文件大小")
    assert int(content_length) >= 5120, "素材文件大小检验异常"

    content_md5 = res.headers["Content-MD5"]
    allure.attach(str(content_md5), "素材文件MD5")
    assert content_md5, "素材文件MD5为空"


@allure.step("{step_name}")
def user_downloads_step(step_name, server_host, uid, token, cat1, expected_res):
    """获取用户下载记录"""
    logger.info(step_name)

    res = user_downloads_api(server_host, uid, token, cat1)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"获取用户下载记录请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "获取用户下载记录返回值校验失败"

    download_info_list = res_data["download_infos"]
    allure.attach(pformat(download_info_list), "用户下载记录")

    return download_info_list


@allure.epic('完美办公-素材下载 业务流程测试')
@allure.feature('场景：创建账号->获取分类总览->获取分类素材列表->素材下载->请求素材下载链接->获取用户下载记录')
class TestMatDownload(object):
    @allure.story("用例：创建账号->获取分类总览->获取分类素材列表->素材下载->请求素材下载链接->获取用户下载记录 预期成功")
    @allure.description("""
        此用例是针对完美办公-素材下载 创建账号->获取分类总览->获取分类素材列表->素材下载->请求素材下载链接->获取用户下载记录 场景的测试
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
        step3: 素材下载
            1.随机选择一个分类素材，请求素材下载接口
            2.校验素材下载接口返回数据的结构和数值
            3.返回素材下载链接
        step4: 请求素材下载链接
            1.请求素材下载链接
            2.校验素材下载链接返回数据的结构和数值
        step5: 获取用户下载记录
            1.请求获取用户下载记录接口
            2.校验获取用户下载记录接口返回数据的结构和数值
            3.校验刚才下载的素材是否在用户下载记录中
    """)
    def test_mat_download_success(self, create_account, case_config):
        server_origin = case_config["params"]["server_origin"]

        # 获取会员账号的 uid 与 token
        account_info = create_account
        uid = account_info["uid"]
        token = account_info["token"]
        vip_type = account_info["vip_type"]

        allure.dynamic.title(f"创建账号->获取分类总览->获取分类素材列表->素材下载->请求素材下载链接->获取用户下载记录（{vip_type.value}） 预期成功")

        # step1: 获取分类总览
        step_1_expected_res = ExpectedResult()
        category_list = category_list_step("step1: 获取分类总览", server_origin, uid, token, step_1_expected_res)

        cat1_info = random.choice(category_list)
        cat1 = cat1_info["id"]
        cat2_info = random.choice(cat1_info["list"])
        cat3_info = random.choice(cat2_info["list"])

        # step2: 获取分类素材列表
        step_2_expected_res = ExpectedResult()
        download_time = datetime.now()
        mat_list = mat_list_step("step2: 获取分类素材列表", server_origin, uid, token, cat1, cat2_info["id"],
                                 cat3_info["id"], step_2_expected_res)

        mat_id = random.choice(mat_list)["id"]

        # step3: 素材下载
        step_3_expected_res = ExpectedResult()
        download_url = mat_download_step("step3: 素材下载", server_origin, uid, token, mat_id, step_3_expected_res)

        # step4: 请求素材下载链接
        step_4_expected_res = ExpectedResult()
        mat_download_url_step("step4: 请求素材下载链接", download_url, step_4_expected_res)

        # step5: 获取用户下载记录
        step_5_expected_res = ExpectedResult()
        download_info_list = user_downloads_step("step5: 获取用户下载记录", server_origin, uid, token, cat1,
                                                 step_5_expected_res)
        # 在下载记录中查找刚才下载的素材
        match_mat_list = []
        for mat in download_info_list:
            # 下载时间差（秒）
            download_time_diff = (datetime.strptime(mat["download_time"], "%Y-%m-%d %H:%M:%S") - download_time).seconds
            if mat["mat_id"] == mat_id and download_time_diff <= 60:
                match_mat_list.append(mat)

        assert len(match_mat_list) > 0, "用户下载记录未找到下载素材"
