import hmac
import hashlib
from duba.config import data_source
from duba.constants import ProductID, ProductInfo, ServerHost, ProductType


def get_dev1_headers(data, product=ProductID.DUBA):
    """
    获取dev1测试服headers
    (dev1测试服没有 X-CF-DeBug-key 请求头, 要用 X-Cf-Productid 和 X-Cf-Authorization)
    @param data: http请求内容
    @param product: 产品ID枚举成员 ProductID
    @return:
    """
    key = ProductInfo[product]["secret"]
    authorization = hmac.new(key.encode("utf-8"), data.encode("utf-8"), 'MD5').hexdigest()

    headers = {
        "X-Cf-Productid": str(product.value),
        "X-Cf-Authorization": authorization,
        "X-Cf-Gray-Key": "1615"
    }

    return headers


def get_default_headers(product, data):
    """
    获取默认请求头
    @param server_host: 服务器地址
    @param data: http请求内容
    @return:
    """
    # dev1测试服没有 X-CF-DeBug-key 请求头, 要用 X-Cf-Productid 和 X-Cf-Authorization
    # if server_host == ServerHost.DEV1.value:
    #     return get_dev1_headers(data)
    # return data_source.headers


    # 如果是sdk的话，就固定用2就好了
    if product == ProductType.SDK.value:
        product_id = ProductID.DG
    else:
        product_id = ProductID.DUBA

    return get_dev1_headers(data, product_id)


def get_wechat_pay_sign(data, key):
    """
    获取微信支付签名
    https://pay.weixin.qq.com/wiki/doc/api/wxpay_v2/papay/chapter2_4.shtml
    https://pay.weixin.qq.com/wiki/doc/api/wxpay_v2/jiekouguize/tool.shtml
    @param data: 请求内容
    @return:
    """
    sign_data = '&'.join([f"{key}={data[key]}" for key in sorted(data.keys())])
    sign_data = f"{sign_data}&key={key}"

    md5lib = hashlib.md5()
    md5lib.update(sign_data.encode('utf-8'))
    sign = md5lib.hexdigest().upper()

    return sign
