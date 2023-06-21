import json
from interface_common import http_request as req
from kwallpaper.constants import WallpaperPlatform

"""用户相关api接口"""


def user_info_api(server_host, open_id, token, attach_allure=True):
    """
    获取用户信息
    @param server_host: 服务器地址
    @param open_id: 用户open_id
    @param token: 用户token
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "token": token,
            "open_id": open_id
        },
        "login_info": {}
    }

    res = req.request_type["application/json"](
        post_url=f"{server_host}/v1/user/info",
        data=json.dumps(data, ensure_ascii=False),
    )

    req.log_handler(res, "获取用户信息", attach_allure)

    return res


def user_own_wp_api(server_host, open_id, token, wtype_support=1, wallpaper_platform=WallpaperPlatform.PC.value, page=1,
                    page_size=50, attach_allure=True):
    """
    用户已购买过的壁纸
    @param server_host: 服务器地址
    @param open_id: 用户open_id
    @param token: 用户token
    @param wtype_support: 0:只取动态壁纸的购买记录，1：支持动态跟场景一起取
    @param wallpaper_platform: 1-pc 2-mobile 默认为PC
    @param page: 页数，默认为1
    @param page_size: 每页大小，默认为24
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "token": token,
            "open_id": open_id
        },
        "wtype_support": wtype_support,
        "wallpaper_platform": wallpaper_platform,
        "page": page,
        "page_size": page_size
    }

    res = req.request_type["application/json"](
        post_url=f"{server_host}/v1/user/own/wp",
        data=json.dumps(data, ensure_ascii=False),
    )

    req.log_handler(res, "用户已购买过的壁纸", attach_allure)

    return res


def hasbuy_wp_api(server_host, open_id, token, wid, wtype, attach_allure=True):
    """
    是否购买过壁纸
    @param server_host: 服务器地址
    @param open_id: 用户open_id
    @param token: 用户token
    @param wid: 壁纸id
    @param wtype: 壁纸类型，0：动态壁纸，1：场景壁纸
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "token": token,
            "open_id": open_id
        },
        "wid": wid,
        "wtype": wtype
    }

    res = req.request_type["application/json"](
        post_url=f"{server_host}/v1/hasbuy/wp",
        data=json.dumps(data, ensure_ascii=False),
    )

    req.log_handler(res, "是否购买过壁纸", attach_allure)

    return res


def user_buy_wp_api(server_host, open_id, token, wid, wtype, attach_allure=True):
    """
    购买壁纸
    @param server_host: 服务器地址
    @param open_id: 用户open_id
    @param token: 用户token
    @param wid: 壁纸id
    @param wtype: 壁纸类型，0：动态壁纸，1：场景壁纸
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "token": token,
            "open_id": open_id
        },
        "wid": wid,
        "wtype": wtype
    }

    res = req.request_type["application/json"](
        post_url=f"{server_host}/v1/user/buy/wp",
        data=json.dumps(data, ensure_ascii=False),
    )

    req.log_handler(res, "购买壁纸", attach_allure)

    return res
