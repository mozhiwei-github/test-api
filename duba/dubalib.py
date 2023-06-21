import random
import hashlib
import string
import jsonpath
import json
import time
import re
from enum import Enum, unique, IntEnum
import allure
from duba.api.coin import coin_info_api
from duba.api.user import user_info_api
from duba.api.pay import settings_config_api, pay_settings_api, pay_api, pay_change_status_api, pay_order_result_api, \
    sdk_pay_order_result_api
from interface_common.mysql_operate import db
from interface_common.utils import get_few_month_range, get_gbk2312, unix_timestamp_to_format_time, \
    get_spandays_month_range
from duba.constants import (ProductType, StatusCode, VipType, VipTypeInfo, EntrustSetting,
                            DIAMOND_VIP_PAY_SETTING_MONTH_LENGTH, SHOW_KEYS_IF,
                            SHOW_KEYS_DEVICE)
from interface_common.logger import logger
from interface_common.utils import get_unix_timestamp

CHINESE_NICKNAME_MAX_LEN = 8


def check_account(open_id, token):
    return len(open_id) == 33 or len(token) == 40


def create_server_id():
    # 随机生成server_id
    m = hashlib.md5()  # 创建Md5对象
    m.update(''.join(random.sample(string.ascii_letters + string.digits, 32)).encode('utf-8'))  # 生成加密串，其中n是要加密的字符串
    return m.hexdigest()  # 经过md5加密的字符串赋值


def has_coin_interface(product):
    """根据接口类型判断是否存在积分相关接口"""
    # 毒霸新会员sdk 无积分相关接口
    return product != ProductType.SDK.value


def get_user_info(server_host, product, open_id, token, attach_allure=True):
    """获取用户详细信息"""
    res = user_info_api(server_host, product, open_id, token, attach_allure=attach_allure)

    assert res.status_code == StatusCode.OK.value, "[dubalib]获取用户详细信息失败，code=%s" % res.status_code

    res_data = json.loads(res.text)
    user_info = jsonpath.jsonpath(res_data, '$.data.user_info')[0]
    try:
        device_info = jsonpath.jsonpath(res_data, '$.data.device_info')[0]
    except:
        device_info = None
    return user_info, device_info


def get_user_coin_info(server_host, product, open_id, token, attach_allure=True):
    """获取用户积分信息"""
    res = coin_info_api(server_host, product, open_id, token, attach_allure=attach_allure)

    assert res.status_code == StatusCode.OK.value, "[dubalib]获取用户积分信息失败，code=%s" % res.status_code

    res_data = json.loads(res.text)
    coin = jsonpath.jsonpath(res_data, '$.coin')[0]

    result = {
        "coin": coin
    }
    return result


def get_coin_by_vip_day_length(coin_setting, day_length):
    """根据套餐时长获取积分"""
    if day_length < 365:
        return jsonpath.jsonpath(coin_setting, '$.RechargeVIP.coin')[0]  # 充值一年内的套餐
    else:
        return jsonpath.jsonpath(coin_setting, '$.RechargeVIPAnnual.coin')[0]  # 充值一年及以上的套餐


def get_pay_setting_real_day_length(month_length, day_length):
    """获取VIP套餐赠送实际时长"""
    # 没有VIP套餐月数值时，采用天数
    if month_length == 0:
        return day_length

    return get_spandays_month_range(month_length)


def get_mysql_pay_setting(pay_setting_id):
    """获取毒霸mysql中会员价格方案表信息"""
    data = db.select_db(
        "SELECT month_length, day_length, vip_type FROM pay_settings WHERE id = {id}".format(id=pay_setting_id))
    assert data, "[dubalib]pay_settings表中未查询到id=%d套餐的相关信息" % pay_setting_id

    return data[0]


def get_nickname(forbid_words):
    """
    获取用户昵称
    @param forbid_words: 禁忌词列表
    @return:
    """

    while True:
        nickname = get_gbk2312(CHINESE_NICKNAME_MAX_LEN)

        for word_dict in forbid_words:
            if word_dict["forbid_word"] in nickname:
                logger.info("%s 字符串中含有禁忌词 %s" % (nickname, word_dict["forbid_word"]))
                continue

        return nickname


def get_forbid_nickname(forbid_words):
    """
    获取含有禁忌词的用户昵称
    @param forbid_words: 禁忌词列表
    @return:
    """
    while True:
        forbid_word_info = random.choice(forbid_words)
        forbid_word = forbid_word_info["forbid_word"]
        # 剔除禁忌词中可能存在的符号
        forbid_word = re.sub(r"[^\w]", "", forbid_word)
        forbid_word_length = len(forbid_word)
        # 禁忌词不超过用户昵称时继续后续步骤，超过则重新选择禁忌词
        if forbid_word_length < CHINESE_NICKNAME_MAX_LEN:
            break
        elif forbid_word_length == CHINESE_NICKNAME_MAX_LEN:
            return forbid_word

    # 将禁忌词插入到随机生成的中文字符串中的随机位置
    random_chinese = get_gbk2312(CHINESE_NICKNAME_MAX_LEN - forbid_word_length)
    insert_index = random.randint(0, len(random_chinese))
    forbid_nickname = "".join([random_chinese[:insert_index], forbid_word, random_chinese[insert_index:]])
    return forbid_nickname


def get_next_vip_type(before_vip_type, setting_vip_type):
    """
    获取用户购买套餐后的应得等级
    @param before_vip_type: 用户原vip会员等级
    @param setting_vip_type: 用户购买的vip套餐会员等级
    @return:
    """
    # 用户原vip会员层级
    before_vip_level = VipTypeInfo[VipType(before_vip_type)]["level"]
    # 用户购买的vip套餐会员层级
    setting_vip_level = VipTypeInfo[VipType(setting_vip_type)]["level"]

    if before_vip_level < setting_vip_level:
        # 套餐vip等级大于原用户vip等级时，用户新vip等级应为套餐vip等级
        return setting_vip_type
    else:
        # 套餐vip等级小于原用户vip等级时，用户vip等级不变
        return before_vip_type


def get_mysql_continuous_info(open_id):
    """获取毒霸mysql中用户自动续费信息表信息"""
    command = f'SELECT continuous_type, contract_id, is_continuous FROM new_duba_continuous WHERE open_id = "{open_id}"'
    data = db.select_db(command)
    assert data, "[dubalib]new_duba_continuous表中未查询到open_id=%s的自动续费信息" % open_id

    return data[0]


def set_mysql_continuous_deductions_time(open_id):
    """修改毒霸mysql中用户自动续费信息表下次扣费时间"""
    next_deductions_time = unix_timestamp_to_format_time(time.time() + 60 * 60 * 24)
    command = f'UPDATE new_duba_continuous SET next_deductions_time = "{next_deductions_time}" WHERE open_id = "{open_id}"'
    db.execute_db(command)


def get_mysql_deductions_info(open_id):
    """获取毒霸mysql中微信自动扣费订单表信息"""
    command = f'SELECT deductions_time, deductions_type, is_pay, pay_channel, contract_id, order_id FROM new_duba_deductions WHERE open_id = "{open_id}"'
    data = db.select_db(command)
    assert data, "[dubalib]new_duba_deductions表中未查询到open_id=%s的微信自动扣费订单" % open_id

    return data[0]


def get_filtered_pay_settings(pay_setting_list, is_entrust_setting=None, is_diamond_setting=None, vip_type=None):
    """根据签约类型过滤套餐列表"""

    def pay_setting_filter(pay_setting):
        result = True
        if is_entrust_setting is not None:
            result = result and pay_setting["is_entrust_setting"] == is_entrust_setting.value

        # if vip_type is not None:
        #     result = result and pay_setting["vip_type"] == str(vip_type.value)

        if is_diamond_setting is not None:
            if is_diamond_setting:
                result = result and pay_setting["month_length"] >= DIAMOND_VIP_PAY_SETTING_MONTH_LENGTH
            else:
                result = result and pay_setting["month_length"] < DIAMOND_VIP_PAY_SETTING_MONTH_LENGTH

        return result

    return list(filter(pay_setting_filter, pay_setting_list))


def get_settings_config_byapi(server_host, tryno, name):
    """获取支付套餐show配置"""
    res = settings_config_api(server_host, tryno, name)
    assert res.status_code == StatusCode.OK.value, "[conftest]获取毒霸套餐show值配置请求失败 code=%s" % res.status_code

    res_data = json.loads(res.text)
    settings_config = jsonpath.jsonpath(res_data, '$.data')[0]

    return settings_config


def get_showkey_viptype(vip_type):
    if isinstance(vip_type,Enum):
        vip_type = vip_type.value
    if vip_type == VipType.NORMAL_VIP.value:
        return "normal_show"
    # if vip_type in (VipType.SUPER_TPL_VIP.value,VipType.SUPER_VIP.value):
    if vip_type == VipType.SUPER_TPL_VIP.value:
        return "super_show"
    if vip_type == VipType.DIAMOND_VIP.value:
        return "diamond_vip_show"
    return None


def get_pay_settings(server_host, product, open_id, token, server_id, vip_type, device_num, is_upgrade,
                     is_entrust_setting):
    #  获取会员中心show配置
    showconfig = get_settings_config_byapi(server_host, "1517", "Home")
    # 根据会员类型及设备数，找到对应的show值
    device_data = showconfig[SHOW_KEYS_DEVICE.index(device_num)]
    strkey = get_showkey_viptype(vip_type)
    show = device_data.get(strkey)
    assert show, f"{device_data}-{strkey}-{vip_type} show config is empty"

    # 发起获取套餐请求,is_all=1 获取全部套餐
    res = pay_settings_api(server_host, product, open_id, token, server_id, show=show, is_all=1, is_upgrade=is_upgrade)
    res_data = res.json()
    allure.attach(f"{res_data}", f"{show}套餐返回内容")
    pay_price_settings = res_data.get("pay_price_settings")
    assert pay_price_settings, "获取套餐异常"

    # 过滤出非纯签约套餐
    filtered_pay_price_settings = get_filtered_pay_settings(pay_price_settings, vip_type=vip_type,
                                                            is_entrust_setting=is_entrust_setting)
    assert filtered_pay_price_settings, "过滤出非签约套餐异常"

    return pay_price_settings


def pay_vip_order(server_host, fake_pay_origin, product, open_id, token, server_id, vip_type, device_num, pay_channel,
                  pay_type,
                  is_upgrade, is_entrust_setting=EntrustSetting.NOT_ENTRUST):
    """
    创建会员账号
    @param request:
    @return:
        open_id: 用户open_id
        token: 用户token
        vip_type: 会员等级枚举成员，例：VipType.NON_VIP
    """
    # 发起获取套餐请求,is_all=1 获取全部套餐
    pay_price_settings = get_pay_settings(server_host, product, open_id, token, server_id, vip_type, device_num,
                                          is_upgrade,
                                          is_entrust_setting=is_entrust_setting)

    pay_setting = pay_price_settings[0]
    logger.info(f"选取套餐 {pay_setting['id']}({pay_setting['name']})")

    # 发起下单请求
    order_time = get_unix_timestamp() - 2000  # 由于测试本机时间可能出现偏差，强行提前2秒记录订单开始时间
    res = pay_api(server_host, product, open_id, token, server_id, pay_setting["id"], pay_channel, pay_type,
                  is_upgrade=is_upgrade)
    res_data = res.json()
    allure.attach(f"{res_data}", f"{pay_setting['id']}套餐下单结果")
    order_id = res_data.get("order_id")

    # 发起第三方支付请求
    res = pay_change_status_api(fake_pay_origin, order_id)
    res_data = res.json()
    allure.attach(f"{res_data}", f"{order_id}订单Mock支付")

    # 查询支付结果
    for i in range(3):
        time.sleep(1)
        res_data = get_pay_order_result(server_host, product, open_id, token, order_time, order_id, pay_channel,
                                        pay_type)
        allure.attach(f"{res_data}", f"{order_id}订单支付结果")
        if res_data.get("data", {}).get("status") == 0:
            return True

    return False


def get_pay_order_result(server_host, product, open_id, token, order_time, order_id, pay_channel, pay_type):
    # 发起查询支付结果请求
    if product == ProductType.SDK.value:
        # 毒霸新会员sdk
        res = sdk_pay_order_result_api(server_host, open_id, token, order_id=order_id, pay_channel=pay_channel,
                                       pay_type=pay_type)
    else:
        # 毒霸新会员v2
        res = pay_order_result_api(server_host, product, open_id, token, order_time)

    return res.json()
