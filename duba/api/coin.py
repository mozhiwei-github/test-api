import json
from duba.config import data_source
from duba.api import get_default_headers
from interface_common import http_request as req

"""积分相关api接口"""


def coin_info_api(server_host, product, open_id, token, attach_allure=True):
    """
    获取积分信息
    @param server_host: 服务器地址
    @param product: 接口版本
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

    raw_data = json.dumps(data, ensure_ascii=False)

    res = req.request_type["application/json"](
        post_url="%s/api/%s/coin/info" % (server_host, product),
        data=raw_data,
        headers=get_default_headers(product, raw_data)
    )

    req.log_handler(res, "获取积分信息", attach_allure)

    return res
