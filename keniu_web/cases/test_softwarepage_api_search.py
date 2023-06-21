import requests
import json
import allure
from asyncio.log import logger


@allure.epic('可牛资源站接口自动化测试')
@allure.feature('接口 - 搜索列表 - /softwarepage/api/search')
class TestFile:

    def setup_class(self):
        self.url = "/softwarepage/api/search"
        self.headers = {'Content-Type': 'application/json'}
        self.payload = json.dumps({
            "keyword": "微信",
            "page": 1,
            "page_size": 50,
            "common": {
                "uid": "",
                "token": "",
                "app_id": "",
                "request_id": "",
                "channel": "",
                "version": "",
                "device_id": "",
                "platform": "pc",
                "lang": "zh_CN"
            }
        })

    # 正常参数
    @allure.story('正常参数,keyword=微信')
    def test01(self,case_config):
        host = case_config['params']['server_host']
        response = requests.request("POST", host + self.url, headers=self.headers, data=self.payload)
        allure.attach("host-->",host)
        allure.attach("url-->", self.url)
        allure.attach("payload-->", self.payload)
        allure.attach("response.text-->", response.text)
        try:
            assert 200 == response.status_code
            assert 0 == response.json()['resp_common']['ret']
            assert 'ok' == response.json()['resp_common']['msg']
            assert 0 < len(response.json()['items'])
            assert 70005042 == response.json()['items'][0]['soft_id']
            assert "微信" == response.json()['items'][0]['soft_name']
        except Exception as e:
            logger.exception(e)
            raise Exception("接口返回不符合预期")

    
    # 请求体为空
    @allure.story('请求体为空')
    def test02(self,case_config):
        host = case_config['params']['server_host']
        payload = ""
        response = requests.request("POST", host + self.url, headers=self.headers, data=payload)
        allure.attach("host-->",host)
        allure.attach("url-->", self.url)
        allure.attach("payload-->", payload)
        allure.attach("response.text-->", response.text)
        try:
            assert 200 == response.status_code
            assert 4001001 == response.json()['resp_common']['ret']
            assert 'bad request' == response.json()['resp_common']['msg']
        except Exception as e:
            logger.exception(e)
            raise Exception("接口返回不符合预期")

    # 少参数
    @allure.story('少参数')
    def test03(self,case_config):
        host = case_config['params']['server_host']
        payload = json.dumps({
            "common": {
                "uid": "",
                "app_id": "",
                "request_id": "",
                "channel": "",
                "version": "",
                "device_id": "",
                "platform": "pc",
                "lang": "zh_CN"
            }
        })
        response = requests.request("POST", host + self.url, headers=self.headers, data=payload)
        allure.attach("host-->",host)
        allure.attach("url-->", self.url)
        allure.attach("payload-->", payload)
        allure.attach("response.text-->", response.text)
        try:
            assert 200 == response.status_code
            assert 4003001 == response.json()['resp_common']['ret']
            assert 'request params error' == response.json()['resp_common']['msg']
        except Exception as e:
            logger.exception(e)
            raise Exception("接口返回不符合预期")

    # 无参数
    @allure.story('无参数')
    def test04(self,case_config):
        host = case_config['params']['server_host']
        payload = json.dumps({})
        response = requests.request("POST", host + self.url, headers=self.headers, data=payload)
        allure.attach("host-->",host)
        allure.attach("url-->", self.url)
        allure.attach("payload-->", payload)
        allure.attach("response.text-->", response.text)
        try:
            assert 200 == response.status_code
            assert 4003001 == response.json()['resp_common']['ret']
            assert 'request params error' == response.json()['resp_common']['msg']
        except Exception as e:
            logger.exception(e)
            raise Exception("接口返回不符合预期")

    # 多参数
    @allure.story('多参数')
    def test05(self,case_config):
        host = case_config['params']['server_host']
        payload = json.dumps({
            "aaa":"bbb",
            "keyword": "微信",
            "page": 1,
            "page_size": 50,
            "common": {
                "uid": "",
                "token": "",
                "app_id": "",
                "request_id": "",
                "channel": "",
                "version": "",
                "device_id": "",
                "platform": "pc",
                "lang": "zh_CN"
            }
        })
        response = requests.request("POST", host + self.url, headers=self.headers, data=payload)
        allure.attach("host-->",host)
        allure.attach("url-->", self.url)
        allure.attach("payload-->", payload)
        allure.attach("response.text-->", response.text)
        try:
            assert 200 == response.status_code
            assert 0 == response.json()['resp_common']['ret']
            assert 'ok' == response.json()['resp_common']['msg']
            assert 0 < len(response.json()['items'])
            assert 70005042 == response.json()['items'][0]['soft_id']
            assert "微信" == response.json()['items'][0]['soft_name']
        except Exception as e:
            logger.exception(e)
            raise Exception("接口返回不符合预期")

# 正常参数,keyword为空
    @allure.story('正常参数,keyword为空')
    def test06(self,case_config):
        host = case_config['params']['server_host']
        payload = json.dumps({
            "keyword": "",
            "page": 1,
            "page_size": 50,
            "common": {
                "uid": "",
                "token": "",
                "app_id": "",
                "request_id": "",
                "channel": "",
                "version": "",
                "device_id": "",
                "platform": "pc",
                "lang": "zh_CN"
            }
        })
        response = requests.request("POST", host + self.url, headers=self.headers, data=payload)
        allure.attach("host-->",host)
        allure.attach("url-->", self.url)
        allure.attach("payload-->", payload)
        allure.attach("response.text-->", response.text)
        try:
            assert 200 == response.status_code
            assert 4003001 == response.json()['resp_common']['ret']
            assert 'request params error' == response.json()['resp_common']['msg']
        except Exception as e:
            logger.exception(e)
            raise Exception("接口返回不符合预期")

# 正常参数,keyword为不存在软件
    @allure.story('正常参数,keyword为不存在软件')
    def test07(self,case_config):
        host = case_config['params']['server_host']
        payload = json.dumps({
            "keyword": "asdfasdf",
            "page": 1,
            "page_size": 50,
            "common": {
                "uid": "",
                "token": "",
                "app_id": "",
                "request_id": "",
                "channel": "",
                "version": "",
                "device_id": "",
                "platform": "pc",
                "lang": "zh_CN"
            }
        })
        response = requests.request("POST", host + self.url, headers=self.headers, data=payload)
        allure.attach("host-->",host)
        allure.attach("url-->", self.url)
        allure.attach("payload-->", payload)
        allure.attach("response.text-->", response.text)
        try:
            assert 200 == response.status_code
            assert 0 == response.json()['resp_common']['ret']
            assert 'ok' == response.json()['resp_common']['msg']
            assert 0 == len(response.json()['items'])
        except Exception as e:
            logger.exception(e)
            raise Exception("接口返回不符合预期")

# 正常参数,keyword为英文
    @allure.story('正常参数,keyword为英文')
    def test07(self,case_config):
        host = case_config['params']['server_host']
        payload = json.dumps({
            "keyword": "mail",
            "page": 1,
            "page_size": 50,
            "common": {
                "uid": "",
                "token": "",
                "app_id": "",
                "request_id": "",
                "channel": "",
                "version": "",
                "device_id": "",
                "platform": "pc",
                "lang": "zh_CN"
            }
        })
        response = requests.request("POST", host + self.url, headers=self.headers, data=payload)
        allure.attach("host-->",host)
        allure.attach("url-->", self.url)
        allure.attach("payload-->", payload)
        allure.attach("response.text-->", response.text)
        try:
            assert 200 == response.status_code
            assert 0 == response.json()['resp_common']['ret']
            assert 'ok' == response.json()['resp_common']['msg']
            assert 0 < len(response.json()['items'])
        except Exception as e:
            logger.exception(e)
            raise Exception("接口返回不符合预期")

# 正常参数,keyword为中英文混合
    @allure.story('正常参数,keyword为中英文混合')
    def test08(self,case_config):
        host = case_config['params']['server_host']
        payload = json.dumps({
            "keyword": "zip解压缩",
            "page": 1,
            "page_size": 50,
            "common": {
                "uid": "",
                "token": "",
                "app_id": "",
                "request_id": "",
                "channel": "",
                "version": "",
                "device_id": "",
                "platform": "pc",
                "lang": "zh_CN"
            }
        })
        response = requests.request("POST", host + self.url, headers=self.headers, data=payload)
        allure.attach("host-->",host)
        allure.attach("url-->", self.url)
        allure.attach("payload-->", payload)
        allure.attach("response.text-->", response.text)
        try:
            assert 200 == response.status_code
            assert 0 == response.json()['resp_common']['ret']
            assert 'ok' == response.json()['resp_common']['msg']
            assert 0 < len(response.json()['items'])
        except Exception as e:
            logger.exception(e)
            raise Exception("接口返回不符合预期")

# 正常参数,keyword为乱码
    @allure.story('正常参数,keyword为乱码')
    def test09(self,case_config):
        host = case_config['params']['server_host']
        payload = json.dumps({
            "keyword": "&^._$",
            "page": 1,
            "page_size": 50,
            "common": {
                "uid": "",
                "token": "",
                "app_id": "",
                "request_id": "",
                "channel": "",
                "version": "",
                "device_id": "",
                "platform": "pc",
                "lang": "zh_CN"
            }
        })
        response = requests.request("POST", host + self.url, headers=self.headers, data=payload)
        allure.attach("host-->",host)
        allure.attach("url-->", self.url)
        allure.attach("payload-->", payload)
        allure.attach("response.text-->", response.text)
        try:
            assert 200 == response.status_code
            assert 0 == response.json()['resp_common']['ret']
            assert 'ok' == response.json()['resp_common']['msg']
            assert 0 == len(response.json()['items'])
        except Exception as e:
            logger.exception(e)
            raise Exception("接口返回不符合预期")