import json
from duba.api import get_default_headers
from interface_common import http_request as req

"""游客账号相关api接口"""


def tourist_login_api(server_host, product, server_id):
    """
    创建游客账号接口
    @param server_host: 服务器地址
    @param product: 接口版本
    @param server_id: 毒霸 svrid
    @return:
    """
    data = {
        "common": {
            "server_id": server_id
        }
    }

    raw_data = json.dumps(data)

    res = req.request_type["application/json"](
        post_url="%s/api/%s/tourist/login" % (server_host, product),
        data=raw_data,
        headers=get_default_headers(product, raw_data)

    )

    req.log_handler(res, "创建游客账号")

    return res


def tourist_bind_api(server_host, product, open_id, token, tourist_open_id):
    """
    绑定游客账号接口
    @param server_host: 服务器地址
    @param product: 接口版本
    @param open_id: 用户open_id
    @param token: 用户token
    @param tourist_open_id: 游客用户open_id
    @return:
    """
    data = {
        "common": {
            "open_id": open_id,
            "token": token
        },
        "tourist_open_id": tourist_open_id
    }

    raw_data = json.dumps(data)

    res = req.request_type["application/json"](
        post_url="%s/api/%s/tourist/bind" % (server_host, product),
        data=raw_data,
        headers=get_default_headers(product, raw_data)

    )

    req.log_handler(res, "绑定游客账号")

    return res


def tourist_bind_info_api(server_host, product, open_id, token):
    """
    游客绑定信息接口
    @param server_host: 服务器地址
    @param product: 接口版本
    @param open_id: 用户open_id
    @param token: 用户token
    @return:
    """
    data = {
        "common": {
            "open_id": open_id,
            "token": token
        }
    }

    raw_data = json.dumps(data)

    res = req.request_type["application/json"](
        post_url="%s/api/%s/tourist/bindInfo" % (server_host, product),
        data=raw_data,
        headers=get_default_headers(product, raw_data)

    )

    req.log_handler(res, "游客绑定信息")

    return res
