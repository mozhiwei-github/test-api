import json
import random
import allure
from pprint import pformat
from interface_common import tcweblib
from interface_common.logger import logger
from kwallpaper.api.balance import get_balances_api
from kwallpaper.api.cms import cms_update_user_fish_api
from kwallpaper.api.payment import payment_packages_api
from kwallpaper.api.user import user_info_api, hasbuy_wp_api, user_buy_wp_api, user_own_wp_api
from kwallpaper.api.wplive import wplive_index_api
from kwallpaper.constants import ExpectedResult, CmsUserFishScene, CurrencyType, WallpaperPayType, WallpaperPlatform

"""壁纸-鱼干支付 业务流程测试"""


@allure.step("{step_name}")
def fish_pay_step(step_name, server_host, open_id, token, expected_res):
    logger.info(step_name)
    # 发起获取鱼干套餐请求
    res = payment_packages_api(server_host, open_id, token)
    # 校验获取鱼干套餐请求结果
    check_fish_packages_result(res, expected_res)


def check_fish_packages_result(res, expected_res):
    """
    校验获取鱼干套餐结果
    @param res: 鱼干套餐接口响应结果
    @param expected_res: 预期结果结构体 ExpectedResult
    @return:
    """
    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"获取鱼干套餐接口请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "获取鱼干套餐接口返回值校验失败"

    # packages = jsonpath.jsonpath(res_data, '$.packages')[0]


@allure.step("{step_name}")
def add_fish_step(step_name, server_origin, open_id, token, cms_origin, uid, scene, fish_amount, balance_expected_res,
                  cms_expected_res):
    logger.info(step_name)
    # 获取钱包余额
    balance_res = get_balances_api(server_origin, open_id, token, currency_ids=[CurrencyType.FISH.value])
    balance_fish_amount = check_balance_result(balance_res, balance_expected_res, CurrencyType.FISH)

    # 发起修改鱼干数的请求
    res = cms_update_user_fish_api(cms_origin, uid, scene, fish_amount)
    # 校验修改鱼干数请求结果
    check_update_user_fish_result(res, cms_expected_res)

    # 再次获取钱包余额
    new_balance_res = get_balances_api(server_origin, open_id, token, currency_ids=[CurrencyType.FISH.value])
    expected_fish_amount = balance_fish_amount + fish_amount
    new_balance_fish_amount = check_balance_result(new_balance_res, balance_expected_res, CurrencyType.FISH,
                                                   expected_fish_amount)

    return new_balance_fish_amount


def check_update_user_fish_result(res, expected_res):
    """
    校验修改鱼干数响应结果
    @param res: 修改鱼干数接口响应结果
    @param expected_res: 预期结果结构体 ExpectedResult
    @return:
    """
    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"修改鱼干数接口请求失败 code={res.status_code}"

    try:
        res_data = json.loads(res.text)
        allure.attach(pformat(expected_res.res_data), "预期响应结果")
        allure.attach(pformat(res_data), "实际响应结果")
        analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
        assert analysis_result, "修改鱼干数接口返回值校验失败"
    except Exception as e:
        logger.exception(e)
        allure.attach(res.text, "实际响应结果")
        assert isinstance(res.text, dict), "获取鱼干套餐接口响应结果解析失败"
        return


def check_balance_result(res, expected_res, currency_type, expected_fish_amount=None):
    """
    校验获取钱包余额响应结果
    @param res: 获取钱包余额接口响应结果
    @param expected_res: 预期结果结构体 ExpectedResult
    @param currency_type: 货币类型
    @param expected_fish_amount: 预期钱包鱼干余额
    @return:
    """
    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"获取钱包余额请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "获取钱包余额返回值校验失败"

    balance_list = res_data["balances"]
    balance_amount = None
    for balance in balance_list:
        if balance["currency"]["id"] == currency_type.value:
            balance_amount = balance["amount"]
            break

    assert balance_amount is not None, "获取钱包余额失败"
    allure.attach(str(balance_amount), "实际钱包余额")

    if expected_fish_amount is not None:
        allure.attach(str(expected_fish_amount), "预期钱包鱼干余额")

        assert balance_amount == expected_fish_amount, "钱包鱼干余额校验失败"

    return balance_amount


@allure.step("{step_name}")
def get_user_info(step_name, server_host, open_id, token, expected_res):
    logger.info(step_name)
    # 获取用户信息
    res = user_info_api(server_host, open_id, token)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"获取用户信息请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "获取用户信息返回值校验失败"

    return res_data["user_info"]


@allure.step("{step_name}")
def wplive_index_step(step_name, server_host, open_id, token, expected_res):
    logger.info(step_name)
    # 获取动态壁纸首页
    res = wplive_index_api(server_host, open_id, token)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"获取动态壁纸首页请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "获取动态壁纸首页返回值校验失败"

    return res_data["data"]


@allure.step("{step_name}")
def has_buy_step(step_name, server_host, open_id, token, wplive_items, expected_res):
    """查找未购买壁纸"""
    logger.info(step_name)

    for item in wplive_items:
        wid = item["wid"]
        wname = item["wname"]
        wtype = item["wtype"]
        allure.attach(pformat(item), "壁纸信息")
        # 查询用户是否购买过壁纸
        res = hasbuy_wp_api(server_host, open_id, token, wid, wtype)

        allure.attach(str(expected_res.status_code), "预期Http状态码")
        allure.attach(str(res.status_code), "实际Http状态码")
        assert res.status_code == expected_res.status_code, f"获取是否购买过壁纸 {wname} 请求失败 code={res.status_code}"

        res_data = json.loads(res.text)
        allure.attach(pformat(expected_res.res_data), "预期响应结果")
        allure.attach(pformat(res_data), "实际响应结果")
        analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
        assert analysis_result, f"获取是否购买过壁纸 {wname} 返回值校验失败"

        if res_data["data"]["is_buy"] == 0:
            allure.attach(pformat(item), "查找到未购买动态壁纸信息")
            return item

    return None


def get_filtered_wplive_items(items, ptype=None, shuffle=False):
    """
    获取过滤后的动态壁纸列表
    @param items:
    @param ptype: 壁纸付费类型 WallpaperPayType
    @param shuffle: 打乱列表
    @return:
    """
    result = []

    for item in items:
        if ptype is not None and item["ptype"] != ptype:
            continue

        result.append({
            "wid": item["wid"],
            "wname": item["wname"],
            "wtype": item["wtype"],
            "ptype": item["ptype"],
            "price": item["price"],
        })

    # 打乱列表
    if shuffle:
        random.shuffle(result)

    return result


@allure.step("{step_name}")
def buy_step(step_name, server_host, open_id, token, wid, wtype, expected_res):
    """购买壁纸"""
    logger.info(step_name)

    res = user_buy_wp_api(server_host, open_id, token, wid, wtype)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"购买壁纸请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "购买壁纸返回值校验失败"


@allure.step("{step_name}")
def user_own_wp_step(step_name, server_host, open_id, token, wallpaper_platform, expected_res, expected_wid=None):
    """用户已购买过的壁纸"""
    logger.info(step_name)

    res = user_own_wp_api(server_host, open_id, token, wallpaper_platform=wallpaper_platform)

    allure.attach(str(expected_res.status_code), "预期Http状态码")
    allure.attach(str(res.status_code), "实际Http状态码")
    assert res.status_code == expected_res.status_code, f"查询用户已购买过的壁纸请求失败 code={res.status_code}"

    res_data = json.loads(res.text)
    allure.attach(pformat(expected_res.res_data), "预期响应结果")
    allure.attach(pformat(res_data), "实际响应结果")
    analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
    assert analysis_result, "查询用户已购买过的壁纸返回值校验失败"

    payed_wp_list = res_data["data"]["list"]
    allure.attach(str(payed_wp_list), "已购买壁纸列表")

    if expected_wid is None:
        return

    assert payed_wp_list, "已购买壁纸列表为空"

    has_expected_wp = False
    for wp in payed_wp_list:
        if wp["id"] == expected_wid:
            has_expected_wp = True
            break

    allure.attach(str(expected_wid), "预期已购买壁纸")
    assert has_expected_wp, "已购买壁纸列表校验失败"


@allure.epic('壁纸-鱼干支付 业务流程测试')
@allure.feature('场景：创建账号->获取鱼干套餐->获取动态壁纸列表->查找未购买动态壁纸->后台增加鱼干数->购买壁纸->校验用户购买过的壁纸')
class TestFishPay(object):
    @allure.story("用例：创建账号->获取鱼干套餐->获取动态壁纸列表->查找未购买动态壁纸->后台增加鱼干数->购买壁纸->校验用户购买过的壁纸 预期成功")
    @allure.description("""
        此用例是针对壁纸-鱼干支付 创建账号->获取鱼干套餐->获取动态壁纸列表->查找未购买动态壁纸->后台增加鱼干数->购买壁纸->校验用户购买过的壁纸 场景的测试
        Set up:
            1.创建毒霸账号
        step1: 获取鱼干套餐
            1.请求获取鱼干套餐接口
            2.校验获取鱼干套餐接口返回数据的结构和数值
            3.获取鱼干套餐列表
        step2: 获取动态壁纸列表
            1.请求获取动态壁纸列表接口
            2.校验获取动态壁纸列表接口返回数据的结构和数值
            3.过滤出付费动态壁纸列表
        step3: 查找未购买动态壁纸
            1.根据付费动态壁纸列表依次查询用户是否购买过该壁纸
            2.校验是否已购买过壁纸接口返回数据的结构和数值
            3.返回用户未购买过的壁纸信息
        step4: 后台增加鱼干数
            1.请求获取钱包余额接口
            2.请求管理后台增加鱼干接口根据壁纸价格增加鱼干
            3.校验增加鱼干接口返回数据的结构和数值
            4.再次请求获取钱包余额接口
            5.校验余额数值是否正确
        step5: 购买壁纸
            1.请求购买壁纸接口
            2.校验购买壁纸接口返回数据的结构和数值
        step6: 校验用户购买过的壁纸
            1.请求用户已购买过的壁纸接口
            2.校验用户已购买过的壁纸接口返回数据的结构和数值
            3.校验刚才购买的壁纸是否在已购买壁纸列表中
    """)
    @allure.title("创建账号->获取鱼干套餐->获取动态壁纸列表->查找未购买动态壁纸->后台增加鱼干数->购买壁纸->校验用户购买过的壁纸 预期成功")
    def test_fish_pay_success(self, create_account, case_config):
        server_origin = case_config["params"]["server_origin"]
        cms_origin = case_config["params"]["cms_origin"]

        # 获取会员账号的 open_id 与 token
        account_info = create_account
        open_id = account_info["open_id"]
        token = account_info["token"]

        # 获取用户信息
        expected_user_info_res = ExpectedResult()
        user_info = get_user_info("获取用户信息", server_origin, open_id, token, expected_user_info_res)
        uid = user_info["uid"]

        # step1: 获取鱼干套餐
        step_1_expected_res = ExpectedResult()
        fish_pay_step("step1: 获取鱼干套餐", server_origin, open_id, token, step_1_expected_res)

        # step2: 获取动态壁纸列表
        step_2_expected_res = ExpectedResult()
        wplive_data = wplive_index_step("step2: 获取动态壁纸列表", server_origin, open_id, token, step_2_expected_res)

        wplive_items = wplive_data["items"]
        assert wplive_items is not None, "动态壁纸列表为空"
        # 获取需付费的动态壁纸列表
        filtered_wplive_items = get_filtered_wplive_items(wplive_items, ptype=WallpaperPayType.VIP_FREE.value,
                                                          shuffle=True)
        assert filtered_wplive_items, "未找到付费动态壁纸列表"

        # step3: 查找未购买壁纸
        step_3_expected_res = ExpectedResult()
        wp_info = has_buy_step("step3: 查找未购买动态壁纸", server_origin, open_id, token, filtered_wplive_items,
                               step_3_expected_res)
        assert wp_info, "查找未购买付费动态壁纸失败"

        # step4: 后台增加鱼干数
        step_4_balance_expected_res = ExpectedResult()
        step_4_cms_expected_res = ExpectedResult()
        add_fish_amount = wp_info["price"]
        add_fish_step("step4: 后台增加鱼干数", server_origin, open_id, token, cms_origin, uid, CmsUserFishScene.SEND_BACK,
                      add_fish_amount, step_4_balance_expected_res, step_4_cms_expected_res)

        # step5: 购买壁纸
        step_5_expected_res = ExpectedResult()
        buy_step("step5: 购买壁纸", server_origin, open_id, token, wp_info["wid"], wp_info["wtype"], step_5_expected_res)

        # step6: 校验用户购买过的壁纸
        step_6_expected_res = ExpectedResult()
        user_own_wp_step("step6: 校验用户购买过的壁纸", server_origin, open_id, token, WallpaperPlatform.PC.value,
                         step_6_expected_res, wp_info["wid"])
