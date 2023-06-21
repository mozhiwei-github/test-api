import random
import requests
import iti.api
from iti.tool.tool import Tool


class ApiCve:
    # 1 初始化
    def __init__(self):
        self.path = "/api/v1/vulnerability"
        date = Tool.get_header_date()
        signature_nonce = ''.join(random.sample(iti.api.signature_dict, 12))
        self.headers = {
            'accept': '*/*',
            'content-type': 'application/json',
            'x-api-signature-nonce': signature_nonce,
            'x-api-date': date
        }
        string_to_sign = Tool.get_string_to_sign("POST", self.path, self.headers, "")
        signature = Tool.get_signature(string_to_sign, iti.api.secret_key)
        authorization = Tool.format_authorization(iti.api.access_key, signature)
        self.headers['Authorization'] = authorization

    # 2 漏洞查询接口
    def api_cve_query(self, object_key):
        body = '{"object_key":"' + object_key + '","limit":100,"offset":0}'
        resp = requests.post(iti.api.host + self.path, data=body, headers=self.headers, verify=True)
        try:
            return resp.json()
        except:
            return resp
