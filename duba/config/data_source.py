headers = {
    'Content-Type': 'application/json',
    'Host': 'newvip.duba.net',
    'X-Cf-Debug-Key': '6323b064bf'
}

fake_pay_server_headers = {
    "Content-Type": "application/json",
    "Host": "fakepayserver.aix-test-k8s.iweikan.cn"
}

newvip_dev2_headers = {
    'Content-Type': 'application/json',
    'X-Cm-Admin-Auth': 'ff657a9f4f80ffaa'
}

wxpay_deduction_trigger_headers = {
    'Content-Type': 'application/json',
    'X-Cm-Admin-Auth': '98ae341851b6e4fa'
}

"""游客账号数据"""
create_account_res_data = {
    "resp_common": {
        "ret": 0,
        "msg": "ok"
    },
    "data": {
        "user_info": {
            "address": "",
            "avatar": "",
            "birthday": "",
            "education": 0,
            "email": "",
            "sign": "",
            "gender": 0,
            "profession": 0,
            "vip_type": "",
            "vip_ex_date": 0,
            "is_continuous": "",
            "is_tourist": True
        }
    }
}

binded_account_data = {
    "resp_common": {
        "ret": 4906002,
        "msg": "tourist already binded"
    }
}

# 通用响应预期结果
common_res_data = {
    "resp_common": {
        "ret": 0,
        "msg": "ok",
    }
}

# 游客账号支付下单预期结果
tourist_pay_res_data = {
    "resp_common": {
        "ret": 4101004,
        "msg": "ban for tourist user",
    }
}

# 修改为禁忌词用户昵称预期结果
forbid_nickname_res_data = {
    "resp_common": {
        "ret": 4909002,
        "msg": "forbid user nickname",
    }
}

# 自动续费解约预期结果
delete_contract_res_data = {
    "result_code": "SUCCESS"
}

# 用户绑定设备超出限制预期结果
token_out_of_limit_res_data = {
    "resp_common": {
        "ret": 5903006,
        "msg": "user token out of limit",
    }
}


# 响应结果校验结构体
class ExpectedResult:
    def __init__(self, status_code, res_data, check_remaining_res=True):
        self.status_code = status_code
        self.res_data = res_data
        self.check_remaining_res = check_remaining_res


"""权限模块"""
get_permission = {
    "permission_info": {},
    "permission_list": "",
    "permission_code": "",
    "permission_code_status": 0
}
