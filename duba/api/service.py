import json
from duba.config import data_source
from duba.api import get_default_headers
from interface_common import http_request as req

"""权益会员/权限模块相关api接口"""


def service_get_api(server_host, product, open_id, token, all_permission=1, user_permission=1, attach_allure=True):
    """
    用户权限查询
    @param server_host: 服务器地址
    @param product: 接口版本
    @param open_id: 用户open_id
    @param token: 用户token
    @param all_permission: 0-不返回; 1-返回个人中心所有权限
    @param user_permission: 0-不返回; 1-返回用户拥有权限
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "open_id": open_id,
            "token": token
        },
        "return_all_permission": all_permission,
        "return_user_permission": user_permission
    }

    raw_data = json.dumps(data, ensure_ascii=False)

    res = req.request_type["application/json"](
        post_url="%s/api/%s/service/get" % (server_host, product),
        data=raw_data,
        headers=get_default_headers(product, raw_data)
    )

    req.log_handler(res, "用户权限查询", attach_allure)

    return res


def service_order_result_api(server_host, product, open_id, token, order_id, pay_channel, pay_type, attach_allure=True):
    """
    查询权益会员支付结果
    @param server_host: 服务器地址
    @param product: 接口版本
    @param open_id: 用户open_id
    @param token: 用户token
    @param order_id:
    @param pay_channel:
    @param pay_type:
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "open_id": open_id,
            "token": token
        },
        "order_id": order_id,
        "pay_channel": pay_channel,
        "pay_type": pay_type.value
    }

    raw_data = json.dumps(data, ensure_ascii=False)

    res = req.request_type["application/json"](
        post_url="%s/api/%s/service/order_result" % (server_host, product),
        data=raw_data,
        headers=get_default_headers(product, raw_data)
    )

    req.log_handler(res, "查询权益会员支付结果", attach_allure)

    return res
