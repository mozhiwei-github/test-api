import json
from interface_common import http_request as req

"""用户相关api接口"""


def user_info_api(server_host, uid, token, attach_allure=True):
    """
    获取用户信息
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
        post_url=f"{server_host}/api/user/info",
        data=json.dumps(data, ensure_ascii=False),
        verify=False
    )

    req.log_handler(res, "获取用户信息", attach_allure)

    return res


def user_favorite_ids_api(server_host, uid, token, attach_allure=True):
    """
    获取用户所有收藏素材ID
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
        post_url=f"{server_host}/api/user/favorite/ids",
        data=json.dumps(data, ensure_ascii=False),
        verify=False
    )

    req.log_handler(res, "获取用户所有收藏素材ID", attach_allure)

    return res


def user_favorite_list_api(server_host, uid, token, cat1, page=1, size=20, attach_allure=True):
    """
    获取用户收藏记录
    @param server_host: 服务器地址
    @param uid: 用户uid
    @param token: 用户token
    @param cat1: 一级分类id
    @param page: 页码，从1开始，未传默认为1
    @param size: 每页条数，1~100 为有效值，非有效值默认为10
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "token": token,
            "uid": uid
        },
        "cat1": cat1,
        "page": page,
        "size": size,
    }

    res = req.request_type["application/json"](
        post_url=f"{server_host}/api/user/favorite/list",
        data=json.dumps(data, ensure_ascii=False),
        verify=False
    )

    req.log_handler(res, "获取用户收藏记录", attach_allure)

    return res


def user_favorite_add_api(server_host, uid, token, mat_id, attach_allure=True):
    """
    添加收藏素材
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
        post_url=f"{server_host}/api/user/favorite/add",
        data=json.dumps(data, ensure_ascii=False),
        verify=False
    )

    req.log_handler(res, "添加收藏素材", attach_allure)

    return res


def user_favorite_remove_api(server_host, uid, token, mat_id, attach_allure=True):
    """
    取消收藏素材
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
        post_url=f"{server_host}/api/user/favorite/remove",
        data=json.dumps(data, ensure_ascii=False),
        verify=False
    )

    req.log_handler(res, "取消收藏素材", attach_allure)

    return res


def user_downloads_api(server_host, uid, token, cat1, page=1, size=20, attach_allure=True):
    """
    获取用户下载记录
    @param server_host: 服务器地址
    @param uid: 用户uid
    @param token: 用户token
    @param cat1: 一级分类id
    @param page: 页码，从1开始，未传默认为1
    @param size: 每页条数，1~100 为有效值，非有效值默认为10
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "token": token,
            "uid": uid
        },
        "cat1": cat1,
        "page": page,
        "size": size,
    }

    res = req.request_type["application/json"](
        post_url=f"{server_host}/api/user/downloads",
        data=json.dumps(data, ensure_ascii=False),
        verify=False
    )

    req.log_handler(res, "获取用户下载记录", attach_allure)

    return res
