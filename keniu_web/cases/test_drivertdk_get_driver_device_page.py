import requests
import json
import allure
from asyncio.log import logger


@allure.epic('可牛资源站接口自动化测试')
@allure.feature('接口 - 驱动落地页 - /drivertdk/get_driver_device_page')
class TestFile:

    def setup_class(self):
        self.url = "/drivertdk/get_driver_device_page"
        self.headers = {'Content-Type': 'application/json'}
        self.payload = json.dumps({
            "driver_device_id": "404894031227689142",
            "common": {
                "app_id": "109",
                "tid1": 0,
                "tid2": 0,
                "tod1": 0,
                "tod2": 0,
                "spid": 0,
                "function_id": 0,
                "platform": "pc",
                "lang": "zh_CN"
            }
        })

    # 正常参数,driver_device_id="404894031227689142"
    @allure.story('正常参数,driver_device_id="404894031227689142"')
    def test01(self, case_config):
        host = case_config['params']['server_host']
        response = requests.request(
            "POST", host + self.url, headers=self.headers, data=self.payload)
        allure.attach("host-->", host)
        allure.attach("url-->", self.url)
        allure.attach("payload-->", self.payload)
        allure.attach("response.text-->", response.text)
        try:
            assert 200 == response.status_code
            assert 0 == response.json()['resp_common']['ret']
            assert 'ok' == response.json()['resp_common']['msg']
            assert '82801FB' in response.json()['tdk']['title']
        except Exception as e:
            logger.exception(e)
            raise Exception("接口返回不符合预期")

    # 请求体为空
    @allure.story('请求体为空')
    def test02(self, case_config):
        host = case_config['params']['server_host']
        payload = ""
        response = requests.request(
            "POST", host + self.url, headers=self.headers, data=payload)
        allure.attach("host-->", host)
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
    def test03(self, case_config):
        host = case_config['params']['server_host']
        payload = json.dumps({
            "common": {
                "app_id": "109",
                "tid1": 0,
                "tid2": 0,
                "tod1": 0,
                "tod2": 0,
                "spid": 0,
                "function_id": 0,
                "platform": "pc",
                "lang": "zh_CN"
            }
        })
        response = requests.request(
            "POST", host + self.url, headers=self.headers, data=payload)
        allure.attach("host-->", host)
        allure.attach("url-->", self.url)
        allure.attach("payload-->", payload)
        allure.attach("response.text-->", response.text)
        try:
            assert 200 == response.status_code
            assert 5001001 == response.json()['resp_common']['ret']
            assert 'server error' == response.json()[
                'resp_common']['msg']
        except Exception as e:
            logger.exception(e)
            raise Exception("接口返回不符合预期")

    # 无参数
    @allure.story('无参数')
    def test04(self, case_config):
        host = case_config['params']['server_host']
        payload = json.dumps({})
        response = requests.request(
            "POST", host + self.url, headers=self.headers, data=payload)
        allure.attach("host-->", host)
        allure.attach("url-->", self.url)
        allure.attach("payload-->", payload)
        allure.attach("response.text-->", response.text)
        try:
            assert 200 == response.status_code
            assert 5001001 == response.json()['resp_common']['ret']
            assert 'server error' == response.json()[
                'resp_common']['msg']
        except Exception as e:
            logger.exception(e)
            raise Exception("接口返回不符合预期")

    # 多参数
    @allure.story('多参数')
    def test05(self, case_config):
        host = case_config['params']['server_host']
        payload = json.dumps({
            "aaa": "bbb",
            "driver_device_id": "404894031227689142",
            "common": {
                "app_id": "109",
                "tid1": 0,
                "tid2": 0,
                "tod1": 0,
                "tod2": 0,
                "spid": 0,
                "function_id": 0,
                "platform": "pc",
                "lang": "zh_CN"
            }
        })
        response = requests.request(
            "POST", host + self.url, headers=self.headers, data=payload)
        allure.attach("host-->", host)
        allure.attach("url-->", self.url)
        allure.attach("payload-->", payload)
        allure.attach("response.text-->", response.text)
        try:
            assert 200 == response.status_code
            assert 0 == response.json()['resp_common']['ret']
            assert 'ok' == response.json()['resp_common']['msg']
            assert '82801FB' in response.json()['tdk']['title']
        except Exception as e:
            logger.exception(e)
            raise Exception("接口返回不符合预期")

# 正常参数,driver_device_id=0
    @allure.story('正常参数,driver_device_id=0')
    def test06(self, case_config):
        host = case_config['params']['server_host']
        payload = json.dumps({
            "driver_device_id": 0,
            "common": {
                "app_id": "109",
                "tid1": 0,
                "tid2": 0,
                "tod1": 0,
                "tod2": 0,
                "spid": 0,
                "function_id": 0,
                "platform": "pc",
                "lang": "zh_CN"
            }
        })
        response = requests.request(
            "POST", host + self.url, headers=self.headers, data=payload)
        allure.attach("host-->", host)
        allure.attach("url-->", self.url)
        allure.attach("payload-->", payload)
        allure.attach("response.text-->", response.text)
        try:
            assert 200 == response.status_code
            assert 5001001 == response.json()['resp_common']['ret']
            assert 'server error' == response.json()['resp_common']['msg']
        except Exception as e:
            logger.exception(e)
            raise Exception("接口返回不符合预期")

# 正常参数,driver_device_id为空
    @allure.story('正常参数,driver_device_id为空')
    def test07(self, case_config):
        host = case_config['params']['server_host']
        payload = json.dumps({
            "driver_device_id": "",
            "common": {
                "app_id": "109",
                "tid1": 0,
                "tid2": 0,
                "tod1": 0,
                "tod2": 0,
                "spid": 0,
                "function_id": 0,
                "platform": "pc",
                "lang": "zh_CN"
            }
        })
        response = requests.request(
            "POST", host + self.url, headers=self.headers, data=payload)
        allure.attach("host-->", host)
        allure.attach("url-->", self.url)
        allure.attach("payload-->", payload)
        allure.attach("response.text-->", response.text)
        try:
            assert 200 == response.status_code
            assert 4001001 == response.json()['resp_common']['ret']
            assert 'bad request' == response.json()[
                'resp_common']['msg']
        except Exception as e:
            logger.exception(e)
            raise Exception("接口返回不符合预期")
