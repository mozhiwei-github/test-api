from enum import Enum, unique, IntEnum


class ServerHost(Enum):
    """服务器地址"""
    NEWVIP_DEV_GW = "http://newvip-dev-gw.duba.net"  # 网关地址
    FAKE_PAY_SERVER = "http://fakepayserver.aix-test-k8s.iweikan.cn"  # 虚拟支付服务地址
    DEV1 = "http://newvip-dev1.duba.net"  # DEV1测试环境地址
    DEV2 = "http://newvip-dev2.duba.net"  # DEV2测试环境地址
    DEV3 = "http://62.234.196.151"  # DEV3测试环境地址


@unique
class VipType(Enum):
    # 测试的会员等级，sdk目前代码不统一，0(普通会员)暂时不适用
    NOTLOGIN = -1  # 未登录
    NON_VIP = 0  # 非会员
    # FREE_VIP = 1  # 体验会员(该类型未上线)
    NORMAL_VIP = 2  # 付费会员
    DIAMOND_VIP = 3  # 钻石会员
    # SUPER_VIP = 5  # 超级会员
    SUPER_TPL_VIP = 6  # 超级会员

# 会员等级相关信息
VipTypeInfo = {
    VipType.NOTLOGIN: {
        "name": "未登录",
        "type": VipType.NOTLOGIN,
        "level": -1  # 会员层次：钻石会员 > 超级会员 > 付费会员 > 体验会员 > 非会员 > 未登录
    },
    VipType.NON_VIP: {
        "name": "非会员",
        "type": VipType.NON_VIP,
        "level": 0  # 会员层次：钻石会员 > 超级会员 > 付费会员 > 体验会员 > 非会员
    },
    # VipType.FREE_VIP: {
    #     "name": "体验会员",
    #     "type": VipType.FREE_VIP,
    #     "level": 1
    # },
    VipType.NORMAL_VIP: {
        "name": "普通会员",
        "type": VipType.NORMAL_VIP,
        "level": 2
    },
    VipType.DIAMOND_VIP: {
        "name": "钻石会员",
        "type": VipType.DIAMOND_VIP,
        "level": 4
    },
    # VipType.SUPER_VIP: {
    #     "name": "超级会员",
    #     "type": VipType.SUPER_VIP,
    #     "level": 3
    # },
    VipType.SUPER_TPL_VIP: {
        "name": "超级会员",
        "type": VipType.SUPER_TPL_VIP,
        "level": 3
    }
}

# 钻石会员套餐（终身）月份长度
DIAMOND_VIP_PAY_SETTING_MONTH_LENGTH = 1200


@unique
class PayChannel(Enum):
    """支付渠道"""
    WECHAT = 1  # 微信
    ALIPAY = 2  # 支付宝


@unique
class PayType(Enum):
    """支付类型"""
    WECHAT_WEB = "wx_web"  # 微信内调起jsapi支付
    WECHAT_WEB_ENTRUST = "web_entrust"  # 微信纯签约方式下单
    WECHAT_QRCODE = "wx_qrcode"  # 微信二维码支付
    ALIPAY_QRCODE = "alipay_qrcode"  # 支付宝二维码支付
    ALIPAY_CYCLEPAYSIGN = "alipay_cyclepaysign"  # 支付宝周期扣款（支付并签约）


"""支付类型对应详细信息"""
PayTypeInfo = {
    # TODO: 补充wx_web的信息
    PayType.WECHAT_WEB_ENTRUST: {
        "type": PayType.WECHAT_WEB_ENTRUST,
        "pay_channel": PayChannel.WECHAT,
        "url_key": "entrust_url"
    },
    PayType.WECHAT_QRCODE: {
        "type": PayType.WECHAT_QRCODE,
        "pay_channel": PayChannel.WECHAT,
        "url_key": "wxqrcode_url"
    },
    PayType.ALIPAY_QRCODE: {
        "type": PayType.ALIPAY_QRCODE,
        "pay_channel": PayChannel.ALIPAY,
        "url_key": "alipayqrcode_url"
    },
    PayType.ALIPAY_CYCLEPAYSIGN: {
        "type": PayType.ALIPAY_CYCLEPAYSIGN,
        "pay_channel": PayChannel.ALIPAY,
        "url_key": "alipay_cyclepaysign_url"
    }
}


@unique
class ProductType(Enum):
    """接口版本类型"""
    V2 = "v2"
    SDK = "sdk"
    V3 = "v3"


"""接口版本类型对应详细信息"""
ProductTypeInfo = {
    ProductType.V2: {
        "type": ProductType.V2,
        "product": ProductType.V2.value
    },
    ProductType.SDK: {
        "type": ProductType.SDK,
        "product": ProductType.SDK.value
    }
}


@unique
class ProductID(IntEnum):
    """产品ID"""
    DUBA = 0  # 毒霸
    DG = 2  # 驱动精灵
    DAOHANG = 9  # 导航
    WALLPAPER = 10  # 元气壁纸
    PDF_STANDALONE = 13  # PDF独立版


"""产品ID对应详细信息"""
ProductInfo = {
    ProductID.DUBA: {
        "secret": "2536179c73102b3a1ccccdad81bb95f0"
    },
    ProductID.DG: {
        "secret": "cc5da34f9b01909f06624229a343a0ae"
    },
    ProductID.DAOHANG: {
        "secret": "3e48b22ca31d2be4d3f1410bea5fd852"
    },
    ProductID.WALLPAPER: {
        "secret": "62f41a4f880463cdc347556c15598999"
    },
    ProductID.PDF_STANDALONE: {
        "secret": "ca41346e78d6f11bfcfebc72463c8d2e"
    },
}


@unique
class VipPaySetting(Enum):
    """会员支付套餐类型"""
    VIP_CENTER_ONE_MONTH = 14  # 会员中心套餐 1个月 非连续包时段 会员类型：付费会员 NORMAL_VIP
    VIP_CENTER_SIX_MONTH = 29  # 会员中心套餐 6个月 非连续包时段 会员类型：付费会员 NORMAL_VIP
    VIP_CENTER_ONE_YEAR = 16  # 会员中心套餐 12个月 非连续包时段 会员类型：付费会员 NORMAL_VIP
    VIP_CENTER_ALL_LIFE = 61  # 会员中心套餐 终身 非连续包时段 会员类型：钻石会员 DIAMOND_VIP
    VIP_CENTER_ONE_MONTH_CONT = 198  # 会员中心套餐 1个月 连续包时段 会员类型：付费会员 NORMAL_VIP
    VIP_CENTER_SIX_MONTH_CONT = 150  # 会员中心套餐 6个月 连续包时段 会员类型：付费会员 NORMAL_VIP
    VIP_CENTER_ONE_YEAR_CONT = 19  # 会员中心套餐 12个月 连续包时段 会员类型：付费会员 NORMAL_VIP
    VIP_CENTER_ALL_LIFE_CONT = 62  # 会员中心套餐 终身 连续包时段 会员类型：钻石会员 DIAMOND_VIP


"""会员支付套餐类型对应详细信息"""
VipPaySettingInfo = {
    VipPaySetting.VIP_CENTER_ONE_MONTH: {
        "name": "1个月VIP套餐（非连续）",
        "type": VipPaySetting.VIP_CENTER_ONE_MONTH,
        "pay_setting_id": VipPaySetting.VIP_CENTER_ONE_MONTH.value
    },
    VipPaySetting.VIP_CENTER_SIX_MONTH: {
        "name": "6个月VIP套餐（非连续）",
        "type": VipPaySetting.VIP_CENTER_SIX_MONTH,
        "pay_setting_id": VipPaySetting.VIP_CENTER_SIX_MONTH.value
    },
    VipPaySetting.VIP_CENTER_ONE_YEAR: {
        "name": "12个月VIP套餐（非连续）",
        "type": VipPaySetting.VIP_CENTER_ONE_YEAR,
        "pay_setting_id": VipPaySetting.VIP_CENTER_ONE_YEAR.value
    },
    VipPaySetting.VIP_CENTER_ALL_LIFE: {
        "name": "终身VIP套餐（非连续）",
        "type": VipPaySetting.VIP_CENTER_ALL_LIFE,
        "pay_setting_id": VipPaySetting.VIP_CENTER_ALL_LIFE.value
    }
}


@unique
class PermissionPaySetting(Enum):
    """权益会员类型"""
    PDF_CONVERT_WEB = 187


"""权益会员类型对应详细信息"""
PermissionPaySettingInfo = {
    PermissionPaySetting.PDF_CONVERT_WEB: {
        "type": PermissionPaySetting.PDF_CONVERT_WEB,
        "pay_setting_id": VipPaySetting.VIP_CENTER_ALL_LIFE.value,
        "key": "pdf_convert_web"
    }
}


@unique
class OrderType(Enum):
    """订单类型"""
    PAY = "pay"  # 会员
    SERVICE = "service"  # 权益会员


@unique
class SDKOrderType(Enum):
    """支付的业务模块"""
    PAY = "pay"  # 套餐下单
    REWARD = "reward"  # 打赏下单


@unique
class PaySettingsShow(Enum):
    """支付套餐类型"""
    VIP_CENTER = 1  # 会员中心套餐
    SUPER_VIP = 40  # 超级会员[升级]
    SDK = 226  # SDK套餐


@unique
class PayOrderStatus(Enum):
    """支付订单状态"""
    ORDER_PAY_SUCCESS = 0  # 成功
    ORDER_NOT_FOUND = 7001005  # "order not found"
    ORDER_PAY_CLOSE = 7001003  # "pay close"
    ORDER_NOT_PAY = 7001002  # "not pay"
    ORDER_PAY_FAIL = 7001001  # "pay fail"


@unique
class EntrustSetting(Enum):
    """纯签约套餐选项"""
    ENTRUST = 1  # 可以发起纯签约
    NOT_ENTRUST = 2  # 不可发起纯签约


@unique
class ContractStatus(Enum):
    """会员签约状态"""
    UNCONTRACTED = 0  # 未签约
    CONTRACTED = 1  # 签约中
    CONTRACT_EXPIRED = 13  # 已解约


@unique
class UserLoginType(Enum):
    """
    用户登录类型

    v3 的登陆接口在 vip 用户登陆设备数量超过限制时：
        1.返回报错信息（resp_common.ret）
        2.返回当前 vip 用户已经登录的设备列表用于用户操作（device_list）
    """
    WECHAT_JSSDK = 1  # 微信JSSDK登录
    PHONE_NUMBER = 2  # 手机号登录
    CHEETAH_ACCOUNT = 3  # 猎豹账号系统登录
    OPEN_ID_AND_TOKEN = 4  # open_id+token 快速登录
    DUBA_DESK_IOS = 5  # 元气壁纸iOS登录
    PDF_LARK = 6  # 极光PDF飞书应用登录


@unique
class UserFirstOrderState(Enum):
    """用户首单状态"""
    FIRST_ORDER = False  # 用户有首单优惠
    NON_FIRST_ORDER = True  # 用户没有首单优惠

UserFirstOrderStateInfo = {
    UserFirstOrderState.FIRST_ORDER:"首单",
    UserFirstOrderState.NON_FIRST_ORDER:"非首单",
}

@unique
class StatusCode(Enum):
    """Http状态码"""
    OK = 200
    MOVED_PERMANENTLY = 301
    FOUND = 302
    NOT_MODIFIED = 304
    BAD_REQUIRED = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504


# pay_settings各个展示场景的对应值
Pay_Settings_Show = {
    "会员中心套餐": {
        "show": [1]
    },
    "数据恢复、照片恢复、手机恢复的兼容老会员的落地页": {
        "show": [4]
    },
    "pdf转word套餐": {
        "show": [6]
    },
    "广告净化套餐": {
        "show": [7]
    },
    "隐私清理套餐": {
        "show": [30]
    },
    "数据恢复、照片恢复、手机恢复的新落地页": {
        "show": [34]
    },
    "PDF转WORD/PDF转换（毒霸）": {
        "show": [36]
    },
    "C盘瘦身": {
        "show": [37]
    },
    "PDF转换（极光独立版）": {
        "show": [39]
    },
    "金山看图": {
        "show": [42]
    },
    "PDF转换（极光独立版）（web版）": {
        "show": [44]
    }
}

# 从/api/v3/pay/settings/config接口获取各个场景show值, 请求时name参数如下所列
Pay_Settings_Show_Name = {
    # 会员中心
    "Home":"会员中心",
    # 会员中心B测
    "Home2":"会员中心B测",
    # 因为会员中心升级页面，前端是新的路由，所以要引用Home
    "Upgrade":"会员中心升级页面",
    # 新版广告拦截
    "AdCharge2":"新版广告拦截",
    # 新版广告拦截 B测
    "AdChargeB":"新版广告拦截B测",
    # 毒霸垃圾清理独立支付页
    "CleanJunkFiles":"毒霸垃圾清理独立支付页",
    # 系统碎片清理王独立支付页
    "CleanKingCharge":"系统碎片清理王独立支付页",
    # 系统碎片清理王独立支付页 B测
    "CleanKingChargeB":"系统碎片清理王独立支付页B测",
    # 金山手机数据恢复独立支付页，不上线
    # "DataHuifuCharge":"金山手机数据恢复独立支付页",
    # 文档修复独立支付页
    "DocFixCharge":"文档修复独立支付页",
    # 驱动管理王
    "DriverCharge":"驱动管理王",
    # 驱动管理王 B测
    "DriverChargeB":"驱动管理王B测",
    # 毒霸看图独立支付页
    "FastPicCharge":"毒霸看图独立支付页",
    # 文件夹加密
    "FileProtect":"文件夹加密",
    # 文件粉碎独立支付页
    "FileShredCharge":"文件粉碎独立支付页",
    # 文件粉碎独立支付页
    "FileShredChargeB":"文件粉碎独立支付页B测",
    # 流程图独立支付页
    "FlowChart":"流程图独立支付页",
    # 新版-数据恢复独立支付页
    "HuifuCharge2":"新版-数据恢复独立支付页",
    # 新版-pdf独立支付页
    "PdfCharge2":"新版-pdf独立支付页",
    # 金山账号恢复独立支付页，不上线
    # "PpCharge":"金山账号恢复独立支付页",
    # 新版-超级隐私独立支付页
    "PrivacyCharge2":"新版-超级隐私独立支付页",
    # 新版-超级隐私独立支付页 B测
    "PrivacyChargeB":"新版-超级隐私独立支付页B测",
    # 原流程图独立支付页
    "Processon":"原流程图独立支付页",
    # 录屏大师独立支付页
    "ScreenRecordCharge":"录屏大师独立支付页",
    # 截图独立支付页
    "ScreenShot":"截图独立支付页",
    # 问题软件安装拦截 独立支付页
    "SoftwareCharge":"问题软件安装拦截独立支付页",
    # C盘瘦身独立支付页
    "SystemSlimCharge":"C盘瘦身独立支付页",
    # C盘瘦身独立支付页 B测
    "SystemSlimChargeB":"C盘瘦身独立支付页B测",
    # 文字转语音独立支付页
    "Text2Voice":"文字转语音独立支付页",
    # 毒霸软件卸载王独立支付页
    # "SoftwareUninstaller":"毒霸软件卸载王独立支付页",
    # 服务播报
    "DataReport":"服务播报",
    # 一键批量升级软件
    "BatchUpgradeSoftWare":"一键批量升级软件",
    # 礼品卡
    "GiftCard":"礼品卡",
    # 自动清理加速
    "AutoCleanSpeedup":"自动清理加速",
    # 礼品卡无忧服务
    "GiftCardRsHappy":"礼品卡无忧服务",
    # 钻石会员套餐
    "DiamondVIP":"钻石会员套餐",
    # 钻石会员无忧服务
    "RsHappyDiamondVIP":"钻石会员无忧服务",
    # 智能降温
    "SmartCooling":"智能降温独立支付页",
}

# 不同设备数下的配置字段一致，如apollo_keys所列,实际接口返回的字段是用下划线分隔的
# apollo配置的字段名
SHOW_KEYS_APOLLO = ["DeviceNum","NormalShow","UpgradeShow","SuperShow","CouponShow","DiamondVipShow"]
# 接口返回的字段名,相对位置与上面对应
SHOW_KEYS_IF = ["device_num","normal_show","upgrade_show","super_show","coupon_show","diamond_vip_show"]
# 配置内容按设备数分类，有1，3，5，10四种设备数配置
SHOW_KEYS_DEVICE = [1,3,5,10]