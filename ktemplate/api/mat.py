import json
from interface_common import http_request as req

"""素材相关api接口"""


def mat_search_v2_api(server_host, uid, token, keyword=None, page=1, size=20, sort=1, cat1=None, cat2=None, cat3=None,
                      attach_allure=True):
    """
    搜索-客户端使用
    @param server_host: 服务器地址
    @param uid: 用户uid
    @param token: 用户token
    @param keyword: 搜索词
    @param page: 页码，从1开始，未传默认为1
    @param size: 每页条数，1~100 为有效值，非有效值默认为10
    @param sort: 排序方式，1-综合排序，2-热门下载，3-最近更新
    @param cat1: 一级分类id
    @param cat2: 二级分类id
    @param cat3: 三级分类id
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "token": token,
            "uid": uid
        },
        "page": page,
        "size": size,
        "sort": sort,
    }

    if "keyword" != None:
        data["keyword"] = keyword.encode("utf-8").decode("latin1")
    if "cat1" != None:
        data["cat1"] = cat1
    if "cat2" != None:
        data["cat2"] = cat2
    if "cat3" != None:
        data["cat3"] = cat3

    res = req.request_type["application/json"](
        post_url=f"{server_host}/api/mat/search/v2",
        data=json.dumps(data, ensure_ascii=False),
        verify=False
    )

    req.log_handler(res, "搜索（客户端使用）", attach_allure)

    return res


def category_list_api(server_host, uid, token, attach_allure=True):
    """
    分类总览
    @param server_host: 服务器地址
    @param uid: 用户uid
    @param token: 用户token
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "token": token,
            "uid": uid
        }
    }

    res = req.request_type["application/json"](
        post_url=f"{server_host}/api/category/list",
        data=json.dumps(data, ensure_ascii=False),
        verify=False
    )

    req.log_handler(res, "分类总览", attach_allure)

    return res


def mat_list_v2_api(server_host, uid, token, ver="2", page=1, size=20, sort=1, cat1=None, cat2=None, cat3=None,
                    attach_allure=True):
    """
    获取分类素材列表-排序策略
    @param server_host: 服务器地址
    @param uid: 用户uid
    @param token: 用户token
    @param ver: 排序策略
    @param page: 页码，从1开始，未传默认为1
    @param size: 每页条数，1~100 为有效值，非有效值默认为10
    @param sort: 排序方式，1-综合排序，2-热门下载，3-最近更新
    @param cat1:
    @param cat2:
    @param cat3:
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "token": token,
            "uid": uid
        },
        "page": page,
        "size": size,
        "sort": sort,
    }

    if "cat1" != None:
        data["cat1"] = cat1
    if "cat2" != None:
        data["cat2"] = cat2
    if "cat3" != None:
        data["cat3"] = cat3
    if "ver" != None:
        data["ver"] = ver

    res = req.request_type["application/json"](
        post_url=f"{server_host}/api/mat/list/v2",
        data=json.dumps(data, ensure_ascii=False),
        verify=False
    )

    req.log_handler(res, "获取分类素材列表(排序策略)", attach_allure)

    return res


def mat_detail_api(server_host, uid, token, mat_id, attach_allure=True):
    """
    获取素材详细信息
    @param server_host: 服务器地址
    @param uid: 用户uid
    @param token: 用户token
    @param mat_id: 素材id
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "token": token,
            "uid": uid
        },
        "mat_id": mat_id
    }

    res = req.request_type["application/json"](
        post_url=f"{server_host}/api/mat/detail",
        data=json.dumps(data, ensure_ascii=False),
        verify=False
    )

    req.log_handler(res, "获取素材详细信息", attach_allure)

    return res


def mat_download_api(server_host, uid, token, mat_id, attach_allure=True):
    """
    素材下载
    @param server_host: 服务器地址
    @param uid: 用户uid
    @param token: 用户token
    @param mat_id: 素材id
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "token": token,
            "uid": uid
        },
        "mat_id": mat_id
    }

    res = req.request_type["application/json"](
        post_url=f"{server_host}/api/mat/download",
        data=json.dumps(data, ensure_ascii=False),
        verify=False
    )

    req.log_handler(res, "素材下载", attach_allure)

    return res
