from asyncio.log import logger
from iti.api.api_cve import ApiCve
import allure
from pprint import pformat

@allure.epic('威胁情报中心web')
@allure.feature('漏洞api测试')
class TestFile:
    def setup_class(self):
        # self.fq = ApiFile()
        pass

    # 查询cve开头的漏洞编号
    @allure.story('查询CVE开头的漏洞编号')
    def test01_cve_query(self,object_key="CVE-2021-44228"):
        self.cq = ApiCve()
        r = self.cq.api_cve_query(object_key)
        try:
            assert 0 == r['result']['status']
            assert 'ok' == r['result']['msg']
        except Exception as e:
            logger.exception(e)
            allure.attach(r,"实际接口返回")
            raise Exception("接口返回异常")

    # 参数为空
    @allure.story('查询漏洞编号为空')
    def test02_cve_query(self,object_key=""):
        self.cq = ApiCve()
        r = self.cq.api_cve_query(object_key)
        try:
            assert 4006001 == r['result']['status']
            assert 'objectKey and objectId cannot both be empty' == r['result']['msg']
        except Exception as e:
            logger.exception(e)
            allure.attach(r,"实际接口返回")
            raise Exception("接口返回异常")

    # 查询cnnvd开头的漏洞编号
    @allure.story('查询CNNVD开头的漏洞编号')
    def test03_cve_query(self, object_key="CNNVD-202112-799"):
        self.cq = ApiCve()
        r = self.cq.api_cve_query(object_key)
        try:
            assert 0 == r['result']['status']
            assert 'ok' == r['result']['msg']
        except Exception as e:
            logger.exception(e)
            allure.attach(r,"实际接口返回")
            raise Exception("接口返回异常")

    # 查询cve开头的漏洞编号，且无匹配数据
    @allure.story('查询CVE开头的漏洞编号，且无匹配样本')
    def test04_cve_query(self, object_key="CNNVD-1-1"):
        self.cq = ApiCve()
        r = self.cq.api_cve_query(object_key)
        try:
            assert 4007001 == r['result']['status']
            assert 'object not found' == r['result']['msg']
        except Exception as e:
            logger.exception(e)
            allure.attach(r,"实际接口返回")
            raise Exception("接口返回异常")

    # 查询cve开头的漏洞编号，且格式错误
    @allure.story('查询CVE开头的漏洞编号，且格式错误')
    def test05_cve_query(self, object_key="CNNVD-x-"):
        self.cq = ApiCve()
        r = self.cq.api_cve_query(object_key)
        try:
            assert 4007001 == r['result']['status']
            assert 'object not found' == r['result']['msg']
        except Exception as e:
            logger.exception(e)
            allure.attach(r,"实际接口返回")
            raise Exception("接口返回异常")

    # 查询cve开头的漏洞编号，且格式错误2
    @allure.story('查询CNNVD开头的漏洞编号，且格式错误')
    def test06_cve_query(self, object_key="CNNVD"):
        self.cq = ApiCve()
        r = self.cq.api_cve_query(object_key)
        try:
            assert 4007001 == r['result']['status']
            assert 'object not found' == r['result']['msg']
        except Exception as e:
            logger.exception(e)
            allure.attach(r,"实际接口返回")
            raise Exception("接口返回异常")

    # 查询cnnvd开头的漏洞编号，且小写
    @allure.story('查询CNNVD开头的漏洞编号，且小写')
    def test07_cve_query(self, object_key="cnnvd-202112-799"):
        self.cq = ApiCve()
        r = self.cq.api_cve_query(object_key)
        try:
            assert 4007001 == r['result']['status']
            assert 'object not found' == r['result']['msg']
        except Exception as e:
            logger.exception(e)
            allure.attach(r,"实际接口返回")
            raise Exception("接口返回异常")

    # 查询cve开头的漏洞编号，且小写
    @allure.story('查询CVE开头的漏洞编号，且小写')
    def test08_cve_query(self, object_key="cve-2021-44228"):
        self.cq = ApiCve()
        r = self.cq.api_cve_query(object_key)
        try:
            assert 4007001 == r['result']['status']
            assert 'object not found' == r['result']['msg']
        except Exception as e:
            logger.exception(e)
            allure.attach(r,"实际接口返回")
            raise Exception("接口返回异常")