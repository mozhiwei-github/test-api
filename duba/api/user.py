import json
from duba.config import data_source
from duba.api import get_default_headers
from interface_common import http_request as req
from duba.constants import ServerHost, VipType, UserLoginType, ProductType, UserFirstOrderState

"""用户相关api接口"""


def user_info_api(server_host, product, open_id, token, return_permission=0, return_permission_vip=0,
                  return_expire_info=0, attach_allure=True):
    """
    获取用户详细信息
    @param server_host: 服务器地址
    @param product: 接口版本
    @param open_id: 用户open_id
    @param token: 用户token
    @param return_permission: 是否返回用户购买的权限信息 1-返回
    @param return_permission_vip: 是否返回格式化后的权益会员标识 1-返回
    @param return_expire_info: 是否返回用户过期信息 1-返回用户过期信息
    @param attach_allure: 是否显示日志到allure报告中
    @return:
    """
    data = {
        "common": {
            "token": token,
            "open_id": open_id,
            "web_version": 7,
        },
        "return_permission": return_permission,
        "return_permission_vip": return_permission_vip,
        "return_expire_info": return_expire_info,
        "need_device_count": True
    }

    raw_data = json.dumps(data, ensure_ascii=False)

    res = req.request_type["application/json"](
        post_url="%s/api/%s/user/userInfo" % (server_host, product),
        data=raw_data,
        headers=get_default_headers(product, raw_data)
    )

    req.log_handler(res, "获取用户详细信息", attach_allure)

    return res


def modify_user_info_api(server_host, product, open_id, token, nickname, avatar_id):
    """
    修改用户信息接口
    @param server_host: 服务器地址
    @param product: 接口版本
    @param open_id: 用户open_id
    @param token: 用户token
    @param nickname: 用户昵称，只能修改，不能删除（昵称空字符串会导致客户端异常）
    @param avatar_id: 用户头像（当前只能编辑为头像库中的图片id eg: "avatar1", "avatar2", "avatar3"）
    @return:
    """
    data = {
        "common": {
            "token": token,
            "open_id": open_id
        },
        "nickname": nickname,
        "avatar_id": avatar_id
    }

    raw_data = json.dumps(data)

    res = req.request_type["application/json"](
        post_url="%s/api/%s/user/modifyInfo" % (server_host, product),
        data=raw_data,
        headers=get_default_headers(product, raw_data)
    )

    req.log_handler(res, "修改用户信息")

    return res


def user_info_avatar_api(server_host, product, open_id, token):
    """
    用户修改信息 - 头像库接口
    @param server_host: 服务器地址
    @param product: 接口版本
    @param open_id: 用户open_id
    @param token: 用户token
    @return:
    """
    data = {
        "common": {
            "token": token,
            "open_id": open_id
        }
    }

    raw_data = json.dumps(data)

    res = req.request_type["application/json"](
        post_url="%s/api/%s/user/modifyInfo/avatar" % (server_host, product),
        data=raw_data,
        headers=get_default_headers(product, raw_data)
    )

    req.log_handler(res, "获取用户头像库")

    return res


def login_fortest_api(server_host, vip_type, add_user_extend_order_cnt=UserFirstOrderState.FIRST_ORDER):
    """
    创建会员账号
    @param server_host: 服务器地址
    @param vip_type: vip类型
                0 -- 非会员
                1 -- 体验会员
                2 -- 普通会员
                3 -- 钻石会员
                5 -- 超级会员
            "add_user_extend_order_cnt": True  True为非首单用户(自动创建一笔订单)，不加为首单用户
            "register_frm":3, //1: qq, 2:wechat, 3:mobile
            "mobile":"13143106993"  //register_frm = 3  的时候需要mobile
            //添加会员权益，具体对应：http://apix.kisops.com/project/484/interface/api/17447
            "add_permissions": [
                {
                    "permission": "data_recovery",
                    "add_service_expire_time":300
                },
                {
                    "permission": "sj_recovery",
                    "add_service_expire_time":20
            }
        ]
    @param add_user_extend_order_cnt True为非首单用户(自动创建一笔订单)，不加为首单用户
    @return:
    """

    if vip_type == VipType.NON_VIP.value:
        data = {}
    else:
        data = {
            "add_user_vip": {
                "type": vip_type,
                "add_time": 3000,
                "mode": "simple"
            }
        }

    if add_user_extend_order_cnt.value:
        data["add_user_extend_order_cnt"] = add_user_extend_order_cnt.value

    res = req.request_type["application/json"](
        post_url="%s/api/v2/user/login_fortest" % server_host,
        headers=data_source.newvip_dev2_headers,
        data=json.dumps(data)
    )

    req.log_handler(res, "创建会员账号")

    return res


def tourist_login_api(server_host, product, server_id=None):
    """
    创建游客账号
    @param server_host: 服务器地址
    @param product: 接口版本
    @param server_id: 客户端serverId
    @return:
    """
    import duba.dubalib as dubalib
    if server_id is None:
        server_id = dubalib.create_server_id()

    data = {
        "common": {
            "server_id": server_id
        }
    }

    raw_data = json.dumps(data, ensure_ascii=False)

    res = req.request_type["application/json"](
        post_url="%s/api/%s/tourist/login" % (server_host, product),
        data=raw_data,
        headers=get_default_headers(product, raw_data)
    )

    req.log_handler(res, "创建游客账号")

    return res


def user_login_api(server_host, product, server_id, login_type, login_token=None, tryno=None, vip_version=None):
    """
    用户登录
    http://apix.kisops.com/project/484/interface/api/15498
    @param server_host: 服务器地址
    @param product: 接口版本
    @param server_id: 登陆时客户端的毒霸 svrid（携带该参数可用于💻设备限制）
    @param login_type: 登陆类型
    @param login_token: 快速登录用的token（用户之前登录时获得的 token）
    @param tryno: 渠道号
    @param vip_version: 客户端版本
    @return:
    """
    data = {
        "common": {
            "server_id": server_id
        },
        "login_type": login_type.value
    }

    if login_type == UserLoginType.OPEN_ID_AND_TOKEN:
        data["login_token"] = login_token

    if tryno is not None:
        data["common"]["tryno"] = tryno
    if vip_version is not None:
        data["common"]["vip_version"] = vip_version

    # 毒霸新会员v2的用户登录接口使用的为v3接口版本
    if product == ProductType.V2.value:
        product = ProductType.V3.value

    raw_data = json.dumps(data, ensure_ascii=False)

    res = req.request_type["application/json"](
        post_url="%s/api/%s/user/login" % (server_host, product),
        data=raw_data,
        headers=get_default_headers(product, raw_data)
    )

    req.log_handler(res, "用户登录")

    return res


def user_token_api(server_host, product, open_id, token, server_id):
    """
    刷新用户token
    @param server_host: 服务器地址
    @param product: 接口版本
    @param open_id: 用户open_id
    @param token: 用户token
    @param server_id: 登陆时客户端的毒霸 svrid（携带该参数可用于💻设备限制）
    @return:
    """
    data = {
        "common": {
            "server_id": server_id,
            "open_id": open_id,
            "token": token
        },
        "return_user_info": True
    }

    raw_data = json.dumps(data, ensure_ascii=False)

    res = req.request_type["application/json"](
        post_url="%s/api/%s/user/token" % (server_host, product),
        data=raw_data,
        headers=get_default_headers(product, raw_data)
    )

    req.log_handler(res, "刷新用户token")

    return res
