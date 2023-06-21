import random
import requests
import iti.api
from iti.tool.tool import Tool


class ApiUrl:
    # 1 初始化
    def __init__(self):
        self.path = "/api/v1/url"
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

    # 2 url查询接口
    def api_url_query(self, url):
        body = '{"object_key":"' + url + '","limit":100,"offset":0}'
        resp = requests.post(iti.api.host + self.path, data=body, headers=self.headers, verify=True)
        return resp.json()
