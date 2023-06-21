from enum import Enum, unique, IntEnum
from duba.constants import StatusCode

"""壁纸项目常量"""

CMS_CRYPTO_KEY = b"Ssklajf123JKSDF"


@unique
class ServerHost(Enum):
    """服务器地址"""
    TEST_PC_WP = "http://test-pcwallpaper3.zhhainiao.com"  # PC壁纸测试服地址
    CMS = "http://wprmmgr.aix-test-k8s.iweikan.cn"  # 后台管理地址


@unique
class RespData(Enum):
    # 通用响应预期结果
    COMMON = {
        "resp_common": {
            "ret": 0,
            "msg": "ok",
        }
    }


# 响应结果校验结构体
class ExpectedResult:
    def __init__(self, status_code=StatusCode.OK.value, res_data=RespData.COMMON.value, check_remaining_res=True):
        self.status_code = status_code
        self.res_data = res_data
        self.check_remaining_res = check_remaining_res


@unique
class UserType(IntEnum):
    """用户类型"""
    COMMON_USER = 0  # 普通用户
    SIGNED_USER = 1  # 签约用户
    ROBOT_USER = 2  # 机器人用户
    SIGNED_AUTHOR = 3  # 签约作者用户
    ORIGINAL_PAINTER = 4  # 原创画师


@unique
class VipType(IntEnum):
    """会员类型"""
    NON_VIP = 0  # 非会员
    COMMON_VIP = 1  # 普通会员
    LIFETIME_VIP = 2  # 终身会员


@unique
class PackageScene(Enum):
    """支付套餐场景"""
    RECHARGE_FISH = "recharge_fish"  # 鱼干充值


@unique
class CmsUserFishScene(IntEnum):
    """管理后台用户鱼干场景id"""
    SEND_BACK = 3000  # 运营退还小鱼干
    DEDUCT = 3001  # 运营扣除小鱼干


@unique
class CurrencyType(IntEnum):
    CNY = 1  # 人民币
    FISH = 2  # 小鱼干
    INGOT = 3  # 元宝


# 鱼干展示数量和存储数值比率
FISH_AMOUNT_RATE = 100


@unique
class WallpaperPayType(IntEnum):
    """壁纸付费类型"""
    FREE = 0  # 免费
    VIP_FREE = 1  # VIP免费
    AD = 2  # 广告壁纸


@unique
class WallpaperType(IntEnum):
    """壁纸类型"""
    LIVE = 0  # 动态壁纸
    SCENE = 1  # 场景壁纸
    STATIC = 2  # 静态壁纸


@unique
class WallpaperPlatform(IntEnum):
    """壁纸平台类型"""
    PC = 1  # PC端
    MOBILE = 2  # 移动端
