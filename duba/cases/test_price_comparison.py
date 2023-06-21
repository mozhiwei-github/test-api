import allure
import json
import jsonpath
import time
import pytest
import duba.dubalib as dubalib
from pprint import pformat
from interface_common.mysql_operate import db
from duba.api.pay import pay_settings_api
from duba.constants import (VipType,VipTypeInfo,PayType, Pay_Settings_Show,Pay_Settings_Show_Name,StatusCode,
    SHOW_KEYS_APOLLO,SHOW_KEYS_IF,SHOW_KEYS_DEVICE,ProductType,UserFirstOrderState,UserFirstOrderStateInfo)
from interface_common.logger import logger

"""毒霸支付价格 展示校验测试"""


@allure.step("{step_name}")
def get_pay_settings_step(step_name, server_host, product, open_id, token, server_id, user_first_order_state,
                          user_vip_type):
    logger.info(step_name)
    is_continuous_name = ["非自动续费套餐", "续费套餐"]
    time_type = 0
    for is_continuous in [0,1]:
        for name in Pay_Settings_Show:
            is_del = Pay_Settings_Show[name]["show"][0]
            # 发起获取会员中心套餐请求
            res = pay_settings_api(server_host, product, open_id, token, server_id, is_continuous, time_type, [is_del],
                                   None, False, False)
            res_data = res.json()
            # 校验获取会员中心套餐结果
            check_pay_settings_result(is_continuous, is_del, name, user_first_order_state, user_vip_type, res_data)

            allure.attach(pformat(f"{res_data.get('pay_price_settings')}"), f"{name} ({is_continuous_name[is_continuous]})")

            time.sleep(0.3)


def get_pay_settings_byapi(server_host, product, open_id, token, server_id, user_first_order_state,
                          user_vip_type,showname,sence):
    """目前只有毒霸场景用"""
    time_type = 0
    
    step = f"step1:请求接口,查询{sence}场景的show配置"
    with allure.step(step):
        logger.info(step)
        # 接口返回的show配置
        if_data = dubalib.get_settings_config_byapi(server_host,"1517",showname)
        allure.attach(f"{if_data}","show配置内容")


    # 遍历不同设备数
    for i in range(len(if_data)):
        with allure.step(f"step{i+2}:校验设备数{if_data[i].get('device_num')}的套餐"):
            allure.attach(f"{if_data[i]}",f"设备数{if_data[i].get('device_num')}")
            # 遍历每个设备数配置的配置
            for j in range(1,len(SHOW_KEYS_IF)):

                is_del = if_data[i].get(SHOW_KEYS_IF[j])
                if not is_del: continue
                # 发起获取套餐请求,is_all=1 获取全部套餐
                res = pay_settings_api(server_host, product, open_id, token, server_id, 0, time_type, is_del,
                                        1, False, False)
                assert res.status_code == 200,"套餐接口请求失败"
                res_data = res.json()
                allure.attach(f"{res_data}", f"{SHOW_KEYS_IF[j]}-{is_del}返回内容")

                settings_data = res_data.get('pay_price_settings',[])

                # 校验套餐结果
                check_pay_settings_result(0, is_del, sence, user_first_order_state, user_vip_type, res_data)
                allure.attach("finished", f"接口内容与数据库内容核对完成")

                time.sleep(0.01)

def get_show_field(user_vip_type):
    # TODO 待定,占位
    map_show_field = {
        0:SHOW_KEYS_IF[0],
        2:SHOW_KEYS_IF[0],
        3:SHOW_KEYS_IF[0],
        5:SHOW_KEYS_IF[0],
        6:SHOW_KEYS_IF[0],
    }

def get_mysql_pay_setting(pay_setting_id):
    """获取毒霸mysql中会员价格方案表信息"""
    data = db.select_db(
        "SELECT id, order_price, current_price, price, new_user_price, is_continuous, is_del FROM pay_settings "
        f"WHERE id = {pay_setting_id}")
    assert data, "[dubalib]pay_settings表中未查询到id=%d套餐的相关信息" % pay_setting_id

    return data[0]


def check_pay_settings_result(is_continuous, is_del, is_del_name, user_first_order_state, user_vip_type, res):
    """对比pay_settings接口数据和数据库数据"""
    pay_price_settings = res.get('pay_price_settings')
    assert pay_price_settings, f"{is_del}套餐数据异常, msg:{res['resp_common']['msg']}"

    for data in pay_price_settings:
        pay_setting_id = data["id"]
        db_result = get_mysql_pay_setting(pay_setting_id)
        # 当new_user_price不为空and用户首单and非vip，选择new_user_price
        if db_result["new_user_price"] != "" and user_first_order_state.value is False and user_vip_type.value in (0,-1):
            assert int(db_result["new_user_price"]) / 100 == data["current_price"], \
                f"{is_del_name}数据库对比校验失败 db:{db_result}, pay_price_settings:{data}"
        # 当order_price不为0，选择order_price
        elif db_result["order_price"] != 0:
            assert db_result["order_price"] / 100 == data["current_price"], \
                f"{is_del_name}数据库对比校验失败 db:{db_result}, pay_price_settings:{data}"
        else:
            assert db_result["current_price"] / 100 == data["current_price"], \
                f"{is_del_name}数据库对比校验失败 db:{db_result}, pay_price_settings:{data}"

        assert db_result["price"] / 100 == data["price"] and \
            db_result["is_continuous"] == data["is_continuous"], f"{is_del_name}数据库对比校验失败 db:{db_result}," \
                                                            f" pay_price_settings:{data}"
    

@allure.epic("毒霸套餐展示校验测试")
@allure.feature('场景： 请求套餐接口->查询数据库或Apollo对比数据')
class TestPriceComparison(object):
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.story("用例： 请求获取套餐接口->查询数据库对比数据")
    @allure.description("""
    此用例是针对用于套餐展示的接口的测试
    Set up:
        1.创建不同类型的会员账号
        2.随机生成server id
    step1: 校验各个场景的套餐价格
        1.请求套餐接口 
        2.通过接口返回的id查询数据库做对比   
        
    测试用的套餐:
        1.会员中心套餐
        2.数据恢复、照片恢复、手机恢复的兼容老会员的落地页
        3.pdf转word套餐
        4.广告净化套餐
        5.隐私清理套餐
        6.数据恢复、照片恢复、手机恢复的新落地页
        7.PDF转WORD/PDF转换（毒霸）
        8.C盘瘦身
        9.PDF转换（极光独立版）
        10.金山看图
        11.PDF转换（极光独立版）（web版）
    """)
    @allure.title("")
    def test_pay_setting_price_comparison(self, product_data, create_vip_account, case_config):
        gateway_origin = case_config["params"]["gateway_origin"]

        product = product_data["product"]

        # 获取会员账号的 open_id 与 token
        account_info = create_vip_account
        open_id = account_info["open_id"]
        token = account_info["token"]
        user_vip_type = account_info["vip_type"]
        user_vip_name = VipTypeInfo[user_vip_type]["name"]
        user_first_order_state = account_info["user_first_order_state"]
        user_first_order_state_name = UserFirstOrderStateInfo[user_first_order_state]
        # 创建随机客户端server id
        server_id = dubalib.create_server_id()

        allure.dynamic.title(
            f"毒霸新会员{product} {user_vip_name}用户 {user_first_order_state_name}"
        )

        # step1: 校验各个场景的套餐价
        get_pay_settings_step("step1: 校验各个场景的套餐价格", gateway_origin, product, open_id, token, server_id,
                              user_first_order_state, user_vip_type)


    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("用例： 请求获取套餐show配置接口->查询Apollo对比数据")
    @allure.description("""
    此用例是针对套餐配置接口在不同场景的测试
    Set up:
        1.请求apollo接口,获取pay_settings_config的内容
    step1: 请求show配置接口 
    step2: 核对接口返回的show与apollo内容是否一致   
    测试场景：
        # 会员中心
        Home
        # 会员中心
        Home2
        # 会员中心升级页面
        Upgrade
        # 新版广告拦截
        AdCharge2
        # 新版广告拦截 B测
        AdChargeB
        # 毒霸垃圾清理独立支付页
        CleanJunkFiles
        # 系统碎片清理王独立支付页
        CleanKingCharge
        # 系统碎片清理王独立支付页 B测
        CleanKingChargeB
        # 金山手机数据恢复独立支付页
        DataHuifuCharge
        # 文档修复独立支付页
        DocFixCharge
        # 驱动管理王
        DriverCharge
        # 驱动管理王 B测
        DriverChargeB
        # 毒霸看图独立支付页
        FastPicCharge
        # 文件夹加密
        FileProtect
        # 文件粉碎独立支付页
        FileShredCharge
        # 文件粉碎独立支付页
        FileShredChargeB
        # 流程图独立支付页
        FlowChart
        # 新版-数据恢复独立支付页
        HuifuCharge2
        # 新版-pdf独立支付页
        PdfCharge2
        # 金山账号恢复独立支付页
        PpCharge
        # 新版-超级隐私独立支付页
        PrivacyCharge2
        # 新版-超级隐私独立支付页 B测
        PrivacyChargeB
        # 原流程图独立支付页
        Processon
        # 录屏大师独立支付页
        ScreenRecordCharge
        # 截图独立支付页
        ScreenShot
        # 问题软件安装拦截 独立支付页
        SoftwareCharge
        # C盘瘦身独立支付页
        SystemSlimCharge
        # C盘瘦身独立支付页 B测
        SystemSlimChargeB
        # 文字转语音独立支付页
        Text2Voice
        # 毒霸软件卸载王独立支付页
        SoftwareUninstaller
        # 服务播报
        DataReport
        # 一键批量升级软件
        BatchUpgradeSoftWare
        # 礼品卡
        GiftCard
        # 自动清理加速
        AutoCleanSpeedup
        # 礼品卡无忧服务
        GiftCardRsHappy
        # 钻石会员套餐
        DiamondVIP
        # 钻石会员无忧服务
        RsHappyDiamondVIP
        # 智能降温
        SmartCooling
    """)
    @allure.title("")
    def test_settings_config_comparison(self, get_apollo_settings_config,get_settings_sences,case_config):
        server_host = case_config["params"]["user_origin"]
        name,desc = get_settings_sences
        allure.dynamic.title(f"{desc} 场景")
        apollo_data = get_apollo_settings_config.get(name,[])

        with allure.step(f"step1:请求接口,查询{desc}场景的show配置"):
            if_data = dubalib.get_settings_config_byapi(server_host,"1517",name)
            allure.attach(pformat(f"{if_data}"),f"{desc}场景返回内容")
        
        with allure.step("step2:核对接口返回的show与apollo内容是否一致 "):
            assert len(if_data) == len(apollo_data)
            # 不同设备数，有不同配置
            for i in range(len(if_data)):
                allure.attach(f"{apollo_data[i]}",f"设备数{apollo_data[i]['DeviceNum']}")
                # 遍历每个设备数配置的配置
                for j in range(1,len(SHOW_KEYS_APOLLO)):
                    if apollo_data[i].get(SHOW_KEYS_APOLLO[j]) is not None:
                        assert if_data[i][SHOW_KEYS_IF[j]] == apollo_data[i][SHOW_KEYS_APOLLO[j]]
                        allure.attach(f"{if_data[i][SHOW_KEYS_IF[j]]} == {apollo_data[i][SHOW_KEYS_APOLLO[j]]}",
                            f"{SHOW_KEYS_IF[j]} == {SHOW_KEYS_APOLLO[j]}内容对比")

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("用例： 请求获取套餐接口->查询数据库对比数据")
    @allure.description("""
    此用例是针对用于套餐展示的接口的测试
    Set up:
        1.创建不同类型的会员账号
        2.随机生成server id
    step1: 校验各个场景的套餐价格
        1.请求套餐接口 
        2.对比接口与数据库中同一个套餐的价格   
        
    测试场景：
    
    """)
    @allure.title("")
    def test_pay_setting_price_comparison_v3(self, create_vip_account_v3,get_settings_sences, case_config):
        gateway_origin = case_config["params"]["gateway_origin"]

        product = ProductType.V2.value
        showname,sence = get_settings_sences

        # 获取会员账号的 open_id 与 token
        account_info = create_vip_account_v3
        logger.info(account_info)
        open_id = account_info["open_id"]
        token = account_info["token"]
        user_vip_type = account_info["vip_type"]
        user_vip_name = VipTypeInfo[user_vip_type]["name"]
        device_num = account_info["device_num"]
        user_first_order_state = account_info["user_first_order_state"]
        user_first_order_state_name = UserFirstOrderStateInfo[user_first_order_state]

        # 创建随机客户端server id
        server_id = dubalib.create_server_id()

        allure.dynamic.title(
            f"毒霸{product}-{user_vip_name}({device_num}台)-{sence}-{user_first_order_state_name}"
        )

        get_pay_settings_byapi(gateway_origin, product, open_id, token, server_id,
                              user_first_order_state, user_vip_type,showname,sence)
        
        