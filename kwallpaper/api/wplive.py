import json
from interface_common import http_request as req

"""动态壁纸相关api接口"""


def wplive_index_api(server_host, open_id, token, offset=0, count=20, attach_allure=True):
    """
    获取动态壁纸首页
    @param server_host: 服务器地址
    @param open_id: 用户open_id
    @param token: 用户token
    @param offset:
    @param count:
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
        post_url=f"{server_host}/v20526/wplive/index",
        data=json.dumps(data, ensure_ascii=False)
    )

    req.log_handler(res, "获取动态壁纸首页", attach_allure)

    return res


def wplive_list_newest_api(server_host, open_id, token, wtype_support=1, encrypt_support="none_encrypt",
                           resolution_support=0, page=1, page_size=24, attach_allure=True):
    """
    获取最新动态壁纸列表
    @param server_host: 服务器地址
    @param open_id: 用户open_id
    @param token: 用户token
    @param wtype_support: 0:只取动态壁纸，1:动态壁纸跟scene一起取
    @param encrypt_support: 加密壁纸支持，first_encrypt_method ：加密壁纸，none_encrypt 或者空则取无加密的壁纸
    @param resolution_support: 0: 所有分辨率壁纸, 1: 小于1080P分辨率的壁纸
    @param page: 默认起始为1
    @param page_size: 默认页大小为24
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "token": token,
            "open_id": open_id
        },
        "wtype_support": wtype_support,
        "encrypt_support": encrypt_support,
        "resolution_support": resolution_support,
        "page": page,
        "page_size": page_size,
    }

    res = req.request_type["application/json"](
        post_url=f"{server_host}/wplive/list/newest",
        data=json.dumps(data, ensure_ascii=False)
    )

    req.log_handler(res, "获取最新动态壁纸列表", attach_allure)

    return res


def wplive_cate_nav_api(server_host, open_id, token, attach_allure=True):
    """
    获取动态壁纸分类导航
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
        post_url=f"{server_host}/wallpaper/live/cate_nav_v2",
        data=json.dumps(data, ensure_ascii=False)
    )

    req.log_handler(res, "获取动态壁纸分类导航", attach_allure)

    return res


def wplive_v20903_list_api(server_host, open_id, token, cate_id=None, tag_id=None, sort_type=2, resolution_support=0,
                           wtype_support=1, encrypt_support="none_encrypt", page=1, page_size=24, display_name="",
                           attach_allure=True):
    """
    获取动态壁纸列表(分类+标签)
    @param server_host: 服务器地址
    @param open_id: 用户open_id
    @param token: 用户token
    @param cate_id: 分类ID
    @param tag_id: 标签ID，如果同时传分类ID和标签ID，将示为两个筛选条件同时成立
    @param sort_type: 排序模式，1.时间倒序，2热度倒序，3评级倒序，4下载量倒序
    @param resolution_support: 	0: 所有分辨率壁纸, 1: 小于1080P分辨率的壁纸
    @param wtype_support: 0:只取动态壁纸，1:动态壁纸跟scene一起取
    @param encrypt_support: 加密壁纸支持，first_encrypt_method ：加密壁纸，none_encrypt 或者空则取无加密的壁纸
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
        "resolution_support": resolution_support,
        "wtype_support": wtype_support,
        "encrypt_support": encrypt_support,
        "page": page,
        "page_size": page_size,
    }

    res = req.request_type["application/json"](
        post_url=f"{server_host}/v20903/wplive/list",
        data=json.dumps(data, ensure_ascii=False)
    )

    interface_name = display_name or "获取动态壁纸列表"
    req.log_handler(res, interface_name, attach_allure)

    return res
