import json
from duba.config import data_source
from duba.api import get_default_headers
from interface_common import http_request as req

"""设备限制相关api接口"""


def server_id_list_api(server_host, product, open_id, token, attach_allure=True):
    """
    获取用户设备绑定列表
    @param server_host: 服务器地址
    @param product: 接口版本
    @param open_id: 用户open_id
    @param token: 用户token
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "open_id": open_id,
            "token": token
        }
    }

    raw_data = json.dumps(data, ensure_ascii=False)

    res = req.request_type["application/json"](
        post_url="%s/api/%s/token/serverid/list" % (server_host, product),
        data=raw_data,
        headers=get_default_headers(product, raw_data)
    )

    req.log_handler(res, "获取用户设备绑定列表", attach_allure)

    return res


def server_id_config_api(server_host, product, attach_allure=True):
    """
    获取设备限制的配置信息（sdk目前代码不统一，0(普通会员)暂时不适用）
    @param server_host: 服务器地址
    @param product: 接口版本
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """
    data = {}

    raw_data = json.dumps(data, ensure_ascii=False)

    res = req.request_type["application/json"](
        post_url="%s/api/%s/token/serverid/config" % (server_host, product),
        data=raw_data,
        headers=get_default_headers(product, raw_data)
    )

    req.log_handler(res, "获取设备限制的配置信息", attach_allure)

    return res


def server_id_unbind_api(server_host, product, open_id, token, op_server_id, attach_allure=True):
    """
    移除设备绑定记录
    @param server_host: 服务器地址
    @param product: 接口版本
    @param open_id: 用户open_id
    @param token: 用户token
    @param op_server_id: 要解除限制的设备 server_id
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """
    data = {
        "common": {
            "open_id": open_id,
            "token": token
        },
        "op_server_id": op_server_id,
        "op_status": "action"
    }

    raw_data = json.dumps(data, ensure_ascii=False)

    res = req.request_type["application/json"](
        post_url="%s/api/%s/token/serverid/unbind" % (server_host, product),
        data=raw_data,
        headers=get_default_headers(product, raw_data)
    )

    req.log_handler(res, "移除设备绑定记录", attach_allure)

    return res
