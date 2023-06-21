import json
from interface_common import http_request as req

"""运营配置相关api接口"""


def conf_get_api(server_host, uid, token, conf_code, attach_allure=True):
    """
    获取配置项
    @param server_host: 服务器地址
    @param uid: 用户uid
    @param token: 用户token
    @param conf_code: 配置code
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "token": token,
            "uid": uid
        },
        "conf_code": conf_code
    }

    res = req.request_type["application/json"](
        post_url=f"{server_host}/api/conf/get",
        data=json.dumps(data, ensure_ascii=False),
        verify=False
    )

    req.log_handler(res, "获取配置项", attach_allure)

    return res
