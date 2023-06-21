import json
from interface_common import http_request as req
from kwallpaper.constants import WallpaperPlatform

"""UGC相关api接口"""


def ugc_is_likes_api(server_host, open_id, token, wtype, wid, attach_allure=True):
    """
    是否点赞过壁纸
    @param server_host: 服务器地址
    @param open_id: 用户open_id
    @param token: 用户token
    @param wtype: 壁纸id
    @param wid: 壁纸类型，0：动态壁纸 ， 1：场景壁纸，2: 静态壁纸
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "token": token,
            "open_id": open_id
        },
        "winfos": [{
            "wtype": wtype,
            "wid": wid
        }]
    }

    res = req.request_type["application/json"](
        post_url=f"{server_host}/v1/ugc/is_likes",
        data=json.dumps(data, ensure_ascii=False),
    )

    req.log_handler(res, "是否点赞过壁纸", attach_allure)

    return res


def ugc_likes_paper_api(server_host, open_id, token, wtype, wid, like=True, attach_allure=True):
    """
    点赞/取消点赞壁纸
    @param server_host: 服务器地址
    @param open_id: 用户open_id
    @param token: 用户token
    @param wtype: 壁纸id
    @param wid: 壁纸类型，0：动态壁纸 ， 1：场景壁纸，2: 静态壁纸
    @param like: 是否为点赞壁纸
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    # action: 0:点赞，1:取消赞
    if like:
        action = 0
        title = "点赞壁纸"
    else:
        action = 1
        title = "取消点赞壁纸"

    data = {
        "common": {
            "token": token,
            "open_id": open_id
        },
        "wtype": wtype,
        "wid": wid,
        "action": action
    }

    res = req.request_type["application/json"](
        post_url=f"{server_host}/v1/ugc/likes/paper",
        data=json.dumps(data, ensure_ascii=False),
    )

    req.log_handler(res, title, attach_allure)

    return res


def ugc_likes_paper_list_api(server_host, open_id, token, wtype_support=1, page=1, page_size=50,
                             wallpaper_platform=WallpaperPlatform.PC.value, attach_allure=True):
    """
    获取点赞壁纸列表
    @param server_host: 服务器地址
    @param open_id: 用户open_id
    @param token: 用户token
    @param wtype_support: 	0:只取动态壁纸。1:动态壁纸跟scene一起取，2: scene壁纸，3: 静态壁纸
    @param page: 页数，默认为1
    @param page_size: 每页大小，默认为24
    @param wallpaper_platform: 1-pc 2-mobile 默认为PC
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "token": token,
            "open_id": open_id
        },
        "wtype_support": wtype_support,
        "page": page,
        "page_size": page_size,
        "wallpaper_platform": wallpaper_platform
    }

    res = req.request_type["application/json"](
        post_url=f"{server_host}/v1/ugc/likes/paper/list",
        data=json.dumps(data, ensure_ascii=False),
    )

    req.log_handler(res, "获取点赞壁纸列表", attach_allure)

    return res
