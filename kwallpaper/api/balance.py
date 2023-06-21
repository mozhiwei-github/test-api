import json
from interface_common import http_request as req

"""壁纸钱包相关api接口"""


def get_balances_api(server_host, open_id, token, currency_ids, attach_allure=True):
    """
    获取钱包余额
    @param server_host: 服务器地址
    @param open_id: 用户open_id
    @param token: 用户token
    @param currency_ids: 货币id列表
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "open_id": open_id,
            "token": token,
        },
        "currency_ids": currency_ids
    }

    res = req.request_type["application/json"](
        post_url=f"{server_host}/balance/get_balances",
        data=json.dumps(data, ensure_ascii=False),
    )

    req.log_handler(res, "获取钱包余额", attach_allure)

    return res
