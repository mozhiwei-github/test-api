import json
from interface_common import http_request as req
from kwallpaper.constants import WallpaperPlatform

"""粉丝系统相关api接口"""


def fans_following_create_api(server_host, open_id, token, following_uid, attach_allure=True):
    """
    关注作者
    @param server_host: 服务器地址
    @param open_id: 用户open_id
    @param token: 用户token
    @param following_uid: 作者uid
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "token": token,
            "open_id": open_id
        },
        "following_uid": following_uid
    }

    res = req.request_type["application/json"](
        post_url=f"{server_host}/fans/following/create",
        data=json.dumps(data, ensure_ascii=False),
    )

    req.log_handler(res, "关注作者", attach_allure)

    return res


def fans_following_cancel_api(server_host, open_id, token, following_uid, attach_allure=True):
    """
    取消关注作者
    @param server_host: 服务器地址
    @param open_id: 用户open_id
    @param token: 用户token
    @param following_uid: 作者uid
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "token": token,
            "open_id": open_id
        },
        "following_uid": following_uid
    }

    res = req.request_type["application/json"](
        post_url=f"{server_host}/fans/following/cancel",
        data=json.dumps(data, ensure_ascii=False),
    )

    req.log_handler(res, "取消关注作者", attach_allure)

    return res


def fans_following_list_api(server_host, open_id, token, query_uid, limit=1000, cursor="", attach_allure=True):
    """
    查询关注人列表
    @param server_host: 服务器地址
    @param open_id: 用户open_id
    @param token: 用户token
    @param query_uid: 用户uid
    @param limit: 返回条数
    @param cursor: 游标
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "token": token,
            "open_id": open_id
        },
        "query_uid": query_uid,
        "limit": limit,
        "cursor": cursor
    }

    res = req.request_type["application/json"](
        post_url=f"{server_host}/fans/following/list",
        data=json.dumps(data, ensure_ascii=False),
    )

    req.log_handler(res, "查询关注人列表", attach_allure)

    return res
