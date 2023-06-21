import json
import hmac
import hashlib

from kwallpaper.constants import CMS_CRYPTO_KEY, FISH_AMOUNT_RATE

"""壁纸项目工具函数"""


def get_cms_access_token(data):
    """
    获取壁纸后端api用于鉴权的 X-cf-Access-Token
    @param data: http请求body
    @return:
    """
    if isinstance(data, str):
        data_str = data
    else:
        data_str = json.dumps(data)
    return hmac.new(CMS_CRYPTO_KEY, data_str.encode("utf-8"), hashlib.md5).hexdigest()


def get_cms_headers(data):
    """
    获取壁纸后端api的headers
    @param data: http请求body
    @return:
    """
    headers = {
        'X-cf-Access-Token': get_cms_access_token(data)
    }
    return headers


def fish_count_2_amount(fish_count):
    """
    鱼干展示数量转存储数量
    @param fish_count: 鱼干展示数量
    @return:
    """
    return fish_count * FISH_AMOUNT_RATE


def fish_amount_2_count(fish_amount):
    """
    鱼干存储数量转展示数量
    @param fish_amount: 鱼干展示数量
    @return:
    """
    return fish_amount / FISH_AMOUNT_RATE
