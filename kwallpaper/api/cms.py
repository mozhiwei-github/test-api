import json
from interface_common import http_request as req
from kwallpaper.constants import CmsUserFishScene
from kwallpaper.utils import get_cms_headers

"""壁纸后台相关api接口"""


def cms_live_categories_api(server_host, attach_allure=True):
    """
    获取动态壁纸分类列表
    @param server_host: 服务器地址
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """

    data = {}

    res = req.request_type["application/json"](
        post_url=f"{server_host}/wallpaper/live/categories",
        data=json.dumps(data, ensure_ascii=False),
        headers=get_cms_headers(data)
    )

    req.log_handler(res, "获取动态壁纸分类列表", attach_allure)

    return res


def cms_update_user_fish_api(server_host, uid, scene, amount, attach_allure=True):
    """
    修改用户鱼干数
    @param server_host: 服务器地址
    @param uid: 用户id
    @param scene: 操作的场景
    @param amount: 鱼干数量的100倍
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """
    # delta 负数为扣除，整数为增加，值为实际数量的100倍
    if scene == CmsUserFishScene.DEDUCT:
        delta = -amount
    else:
        delta = amount

    data = {
        "uid": uid,
        "scene_id": scene.value,
        "delta": delta,
    }

    json_data = json.dumps(data, ensure_ascii=False)

    res = req.request_type["application/json"](
        post_url=f"{server_host}/v1/update/user/fish",
        data=json_data,
        headers=get_cms_headers(json_data)
    )

    req.log_handler(res, "修改用户鱼干数", attach_allure)

    return res
