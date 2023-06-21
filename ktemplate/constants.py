from enum import Enum, unique
from duba.constants import StatusCode

"""完美办公项目常量"""


@unique
class ServerHost(Enum):
    """服务器地址"""
    TEST_OFFICE = "http://test-loveoffice.zhhainiao.com"  # 完美办公测试服地址


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
class VipType(Enum):
    """会员类型"""
    GUEST = "游客"  # 游客
    NON_VIP = "非会员"  # 非会员
    COMMON_VIP = "普通会员"  # 普通会员
    LIFETIME_VIP = "终身会员"  # 终身会员
