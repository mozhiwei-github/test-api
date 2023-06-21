import json
from interface_common.utils import get_uuid
from interface_common import http_request as req
from duba.config import data_source
from duba.api import get_dev1_headers, get_default_headers, get_wechat_pay_sign
from duba.constants import ProductType, OrderType, SDKOrderType, ServerHost

"""支付相关api接口"""


def pay_settings_api(server_host, product, open_id, token, server_id, is_continuous=1, time_type=0, show=[1],
                     is_all=None, is_upgrade=False, attach_allure=True):
    """
    获取支付套餐
    http://apix.kisops.com/project/484/interface/api/15087
    @param server_host: 服务器地址
    @param product: 接口版本
    @param open_id: 用户open_id
    @param token: 用户token
    @param server_id: 客户端serverId
    @param is_continuous: 1为续费套餐，0为非自动续费套餐
    @param time_type: 按年和月区分套餐，1为年，2为月，3为按次，0则不进行区分
    @param show: 展示套餐类型，1为会员中心套餐 40为超级会员[升级] 其他值见于api文档
    @param is_all: 1为忽略is_continuous值，返回全部套餐
    @param is_upgrade: 是否为升级到目标套餐，此时请求 common 中必须带用户授权信息
    @param  attach_allure True打印请求数据的日志，否则不打印
    @return:
    """
    # 毒霸新会员v2的获取支付套餐接口使用的为v3接口版本
    if product == ProductType.V2.value:
        product = ProductType.V3.value

    data = {
        "common": {
            "server_id": server_id,
            "token": token,
            "open_id": open_id
        },
        "token": token,
        "open_id": open_id,
        "is_continuous": is_continuous,
        "time_type": time_type,
        "show": show
    }

    if is_all is not None:
        data["is_all"] = is_all
    if is_upgrade:
        data["is_upgrade"] = 1

    raw_data = json.dumps(data, ensure_ascii=False)

    res = req.request_type["application/json"](
        post_url="%s/api/%s/pay/settings" % (server_host, product),
        data=raw_data,
        headers=get_default_headers(product, raw_data)
    )

    req.log_handler(res, "获取支付套餐", attach_allure)

    return res


def get_pay_params(open_id, token, server_id, pay_setting_id, pay_channel, pay_type, uuid, pay_from, show_from,
                   order_from, is_first_order, is_upgrade, wx_oauth_code):
    """支付（下单）/权益支付（下单）接口请求参数构造"""
    data = {
        "common": {
            "server_id": server_id,
            "token": token,
            "open_id": open_id,
            "uuid": uuid
        },
        "pay_setting_id": pay_setting_id,
        "pay_from": pay_from,
        "pay_channel": pay_channel,
        "show_from": show_from,
        "pay_type": pay_type,
        "order_from": order_from
    }

    if is_first_order is not None:  # TODO: 根据用户当前状态匹配 is_first_order
        data["is_first_order"] = is_first_order
    if is_upgrade:
        data["is_upgrade"] = 1
    if wx_oauth_code is not None:
        data["wx_oauth_code"] = wx_oauth_code
    return data


def pay_api(server_host, product, open_id, token, server_id, pay_setting_id, pay_channel, pay_type, uuid=get_uuid(),
            pay_from=0, show_from=0, order_from=1, is_first_order=None, is_upgrade=False, wx_oauth_code=None):
    """
    支付（下单）
    http://apix.kisops.com/project/484/interface/api/14499
    @param server_host: 服务器地址
    @param product: 接口版本
    @param open_id: 用户open_id
    @param token: 用户token
    @param server_id: 客户端serverId
    @param pay_setting_id: 支付配置套餐id
    @param pay_channel: 支付渠道,1为微信,2为支付宝
    @param pay_type: 支付类型
            wx_web: 微信内调起jsapi支付
            web_entrust: 微信纯签约方式下单
            wx_qrcode: 微信二维码支付
            alipay_qrcode: 支付宝二维码支付
            alipay_cyclepaysign: 支付宝周期扣款（支付并签约）
    @param uuid:
    @param pay_from: 0为会员中心支付,1为免广告落地页（不输入该参数则默认为0）
    @param show_from: 界面展示来源
    @param order_from: 下单来源，1：PC下的单
    @param is_first_order: 是否有首单优惠套餐，传了该参数则会进行校验，不传则不校验直接改变价格（1:首单套餐优惠校验）
    @param is_upgrade: 1为升级到该套餐
    @param wx_oauth_code: 微信授权时拿到的 code 值，支付方式为 wx_web 时有效
    @return:
    """
    data = get_pay_params(open_id, token, server_id, pay_setting_id, pay_channel, pay_type, uuid, pay_from, show_from,
                          order_from, is_first_order, is_upgrade, wx_oauth_code)

    raw_data = json.dumps(data, ensure_ascii=False)

    res = req.request_type["application/json"](
        post_url="%s/api/%s/pay" % (server_host, product),
        data=raw_data,
        headers=get_default_headers(product, raw_data)
    )

    req.log_handler(res, "支付下单")

    return res


def service_pay_api(server_host, product, open_id, token, server_id, pay_setting_id, pay_channel, pay_type,
                    uuid=get_uuid(), pay_from=0, show_from=0, order_from=1, is_first_order=None, is_upgrade=None,
                    wx_oauth_code=None):
    """
    权益支付（下单）,post_url与pay_api不一致，其他一致
    @return:
    """
    data = get_pay_params(open_id, token, server_id, pay_setting_id, pay_channel, pay_type, uuid, pay_from, show_from,
                          order_from, is_first_order, is_upgrade, wx_oauth_code)

    raw_data = json.dumps(data, ensure_ascii=False)

    res = req.request_type["application/json"](
        post_url="%s/api/%s/service/pay" % (server_host, product),
        data=raw_data,
        headers=get_default_headers(product, raw_data)
    )

    req.log_handler(res, "权益支付下单")

    return res


def pay_change_status_api(server_host, out_trade_no, status=1):
    """
    修改订单状态
    @param server_host: 服务器地址
    @param out_trade_no: 订单号
    @param status: 订单状态
    @return:
    """
    data = {
        "out_trade_no": out_trade_no,
        "status": status
    }

    res = req.request_type["application/json"](
        post_url="%s/pay/changestatus" % server_host,
        data=json.dumps(data, ensure_ascii=False),
        headers=data_source.fake_pay_server_headers
    )

    req.log_handler(res, "修改订单状态")

    return res


def pay_contractorder_pay_api(server_host, out_trade_no, contract_id):
    """
    支付并签约
    @param server_host: 服务器地址
    @param out_trade_no: 订单号
    @param contract_id: 签约协议号
    @return:
    """
    data = {
        "out_trade_no": out_trade_no,
        "contract_id": contract_id
    }

    res = req.request_type["application/json"](
        post_url="%s/pay/contractorder/pay" % server_host,
        data=json.dumps(data, ensure_ascii=False),
        headers=data_source.fake_pay_server_headers
    )

    req.log_handler(res, "支付并签约")

    return res


def pay_order_result_api(server_host, product, open_id, token, start_time, order_type=OrderType.PAY.value):
    """
    通用支付结果
    毒霸新会员v2 http://apix.kisops.com/project/484/interface/api/40581
    @param server_host: 服务器地址
    @param product: 接口版本
    @param open_id: 用户open_id
    @param token: 用户token
    @param start_time: 查询开始时间（UNIX时间戳）
    @param order_type: 订单类型 "pay" 会员, "service" 权益会员
    @return:
    """
    # 毒霸新会员v2的通用支付结果接口使用的为v3接口版本
    if product == ProductType.V2.value:
        product = ProductType.V3.value

    data = {
        "common": {
            "token": token,
            "open_id": open_id
        },
        "type": order_type,
        "starttime": start_time
    }

    raw_data = json.dumps(data, ensure_ascii=False)

    res = req.request_type["application/json"](
        post_url="%s/api/%s/pay/order_result" % (server_host, product),
        data=raw_data,
        headers=get_default_headers(product, raw_data)
    )

    req.log_handler(res, "获取通用支付结果")

    return res


def sdk_pay_order_result_api(server_host, open_id, token, order_type=SDKOrderType.PAY.value, order_id=None,
                             pay_channel=None, pay_type=None, identify=None):
    """
    支付结果（毒霸新会员sdk）
    毒霸新会员sdk http://apix.kisops.com/project/750/interface/api/39681
    @param server_host: 服务器地址
    @param open_id: 用户open_id
    @param token: 用户token
    @param order_type: 支付的业务模块（"pay": 套餐下单, "reward": 打赏下单）
    @param order_id: 订单id, 在 pay 场景下必须
    @param pay_channel: 下单时使用的 pay_channel 参数
    @param pay_type: 下单时使用的 pay_type 参数
    @param identify: 在 reward 场景下有效, 是打赏订单的标识
    @return:
    """

    data = {
        "common": {
            "token": token,
            "open_id": open_id
        },
        "order_id": order_id,
        "pay_channel": pay_channel,
        "pay_type": pay_type,
        "type": order_type,
    }

    if identify is not None:
        data["identify"] = identify

    raw_data = json.dumps(data, ensure_ascii=False)

    res = req.request_type["application/json"](
        post_url="%s/api/%s/pay/order_result" % (server_host, ProductType.SDK.value),
        data=raw_data,
        headers=get_default_headers(ProductType.SDK.value, raw_data)
    )

    req.log_handler(res, "获取支付结果（SDK）")

    return res


def wxpay_deduction_trigger_api(server_host, product, open_id):
    """
    触发签约扣费（微信）
    @param server_host: 服务器地址
    @param product: 接口版本
    @param open_id: 用户open_id
    @return:
    """
    # 毒霸新会员sdk的触发签约扣费接口使用的为v2接口版本
    if product == ProductType.SDK.value:
        product = ProductType.V2.value

    data = {"open_id": open_id}

    res = req.request_type["application/json"](
        post_url="%s/api/%s/pay/wxpay/deduction/trigger" % (server_host, product),
        data=json.dumps(data, ensure_ascii=False),
        headers=data_source.wxpay_deduction_trigger_headers
    )

    req.log_handler(res, "触发签约扣费（微信）")

    return res


def papay_deletecontract_api(server_host, mch_id, app_id, contract_id, contract_termination_remark="test",
                             version="1.0", key="75B77BE260747BD30D01FFDB7F2FF887"):
    """
    自动续费解约
    @param server_host: 服务器地址
    @param product: 接口版本
    @param mch_id: 服务器对应的 mch_id
    @param app_id: 服务器对应的 appid
    @param contract_id: 委托代扣协议id
    @return:
    """
    data = {
        "appid": app_id,
        "mch_id": mch_id,
        "contract_id": contract_id,
        "contract_termination_remark": contract_termination_remark,
        "version": version,
    }

    # 计算微信支付签名
    sign = get_wechat_pay_sign(data, key)

    data["sign"] = sign

    # 将 data 转换为 xml 格式
    xml_content = ''.join([f"<{key}>{data[key]}</{key}>" for key in data.keys()])
    xml_data = f"<xml>{xml_content}</xml>"

    res = req.request_type["application/xml"](
        post_url="%s/papay/deletecontract" % server_host,
        data=xml_data
    )

    req.log_handler(res, "自动续费解约")

    return res


def settings_config_api(server_host, tryno, name, attach_allure=True):
    """
    获取支付套餐show配置,目前只有毒霸在用
    http://apix.kisops.com/project/484/interface/api/56866
    @param server_host: 服务器地址
    @param tryno: 客户端tryno
    @param name: 配置的场景名
    @param attach_allure True打印请求数据的日志,否则不打印
    @return:
    """

    data = {
        "common": {
            "tryno": tryno
        },
        "type": "device_upgrade_show",
        "name": name
    }

    raw_data = json.dumps(data, ensure_ascii=False)

    res = req.request_type["application/json"](
        post_url="%s/api/%s/pay/settings/config" % (server_host, ProductType.V3.value),
        data=raw_data,
        headers=get_default_headers(ProductType.V3.value, raw_data)
    )

    req.log_handler(res, "获取支付套餐show配置", attach_allure)

    return res