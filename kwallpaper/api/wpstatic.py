import json
from interface_common import http_request as req

"""静态壁纸相关api接口"""


def wpstatic_index_api(server_host, open_id, token, offset=0, count=60, attach_allure=True):
    """
    获取静态壁纸首页
    @param server_host: 服务器地址
    @param open_id: 用户open_id
    @param token: 用户token
    @param offset: 偏移量，从0开始
    @param count: 每次获取的条数
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "token": token,
            "open_id": open_id
        },
        "offset": offset,
        "count": count,
    }

    res = req.request_type["application/json"](
        post_url=f"{server_host}/wallpaper/static/index",
        data=json.dumps(data, ensure_ascii=False)
    )

    req.log_handler(res, "获取静态壁纸首页", attach_allure)

    return res


def wpstatic_cate_nav_api(server_host, open_id, token, attach_allure=True):
    """
    获取静态壁纸分类导航
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
        }
    }

    res = req.request_type["application/json"](
        post_url=f"{server_host}/wallpaper/static/cate_nav_v2",
        data=json.dumps(data, ensure_ascii=False)
    )

    req.log_handler(res, "获取静态壁纸分类导航", attach_allure)

    return res


def wpstatic_list_api(server_host, open_id, token, cate_id=None, tag_id=None, sort_type=2, page=1, page_size=24,
                      display_name="", attach_allure=True):
    """
    获取静态壁纸列表
    @param server_host: 服务器地址
    @param open_id: 用户open_id
    @param token: 用户token
    @param cate_id: 分类ID
    @param tag_id: 标签ID，如果同时传分类ID和标签ID，将示为两个筛选条件同时成立
    @param sort_type: 排序模式，1.时间倒序，2热度倒序，3评级倒序，4下载量倒序
    @param page: 默认起始为1
    @param page_size: 默认页大小为24
    @param display_name: allure报告和log中显示的接口名称
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "token": token,
            "open_id": open_id
        },
        "cate_id": cate_id,
        "tag_id": tag_id,
        "sort_type": sort_type,
        "page": page,
        "page_size": page_size,
    }

    res = req.request_type["application/json"](
        post_url=f"{server_host}/wallpaper/static/list",
        data=json.dumps(data, ensure_ascii=False)
    )

    interface_name = display_name or "获取静态壁纸列表"
    req.log_handler(res, interface_name, attach_allure)

    return res
