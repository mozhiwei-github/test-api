import json
from interface_common import http_request as req
from kwallpaper.constants import PackageScene

"""壁纸支付相关api接口"""


def vip_settings_by_show_api(server_host, attach_allure=True):
    """
    获取动态壁纸分类列表
    @param server_host: 服务器地址
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {}

    res = req.request_type["application/json"](
        post_url=f"{server_host}/v1/payment/vip/settings_by_show",
        data=json.dumps(data, ensure_ascii=False),
    )

    req.log_handler(res, "获取动态壁纸分类列表", attach_allure)

    return res


def payment_packages_api(server_host, open_id, token, scene=PackageScene.RECHARGE_FISH, attach_allure=True):
    """
    获取支付套餐
    @param server_host: 服务器地址
    @param open_id: 用户open_id
    @param token: 用户token
    @param scene: 场景字符串
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {
        "common": {
            "open_id": open_id,
            "token": token
        },
        "scene": scene.value
    }

    res = req.request_type["application/json"](
        post_url=f"{server_host}/v1/payment/packages",
        data=json.dumps(data, ensure_ascii=False),
    )

    req.log_handler(res, "获取支付套餐", attach_allure)

    return res
