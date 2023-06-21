import json
from interface_common import http_request as req
from kwallpaper.constants import WallpaperPlatform

"""人气作者相关api接口"""


def pc_popularity_author_list_api(server_host, open_id, token, limit=100, cursor="", attach_allure=True):
    """
    PC人气作者列表
    @param server_host: 服务器地址
    @param open_id: 用户open_id
    @param token: 用户token
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
        "limit": limit,
        "cursor": cursor
    }

    res = req.request_type["application/json"](
        post_url=f"{server_host}/pc/popularity/author/list",
        data=json.dumps(data, ensure_ascii=False),
    )

    req.log_handler(res, "PC人气作者列表", attach_allure)

    return res
