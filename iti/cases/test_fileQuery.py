import pytest
import allure
from iti.api.api_file import ApiFile



@allure.epic('威胁情报中心web')
@allure.feature('文件api测试')
class TestFile:
    def setup_class(self):
        # self.fq = ApiFile()
        pass

    @allure.story('验证黑样本MD5')
    # 查询MD5
    def test01_file_query(self,object_key='cb3a3530626caaec092ccf115314e25d'):
        self.fq = ApiFile()
        r = self.fq.api_file_query(object_key)
        assert 0 == r['result']['status']
        assert 'ok' == r['result']['msg']

    # 无匹配情报
    @allure.story('验证无匹配情报')
    def test02_file_query(self,object_key='cb3a3530626caaec092ccf115314e251'):
        self.fq = ApiFile()
        r = self.fq.api_file_query(object_key)
        assert 4007001 == r['result']['status']
        assert 'object not found' == r['result']['msg']

    # md5为空
    @allure.story('验证MD5为空')
    def test03_file_query(self,object_key=''):
        self.fq = ApiFile()
        r = self.fq.api_file_query(object_key)
        assert 4006001 == r['result']['status']
        assert 'objectKey and objectId cannot both be empty' == r['result']['msg']

    # 查询SHA1
    @allure.story('验证黑样本SHA1')
    def test04_file_query(self,object_key='4a5dafa883b71daa3551170abfef30340e599199'):
        self.fq = ApiFile()
        r = self.fq.api_file_query(object_key)
        assert 0 == r['result']['status']
        assert 'ok' == r['result']['msg']

    # 查询SHA256
    @allure.story('验证黑样本SHA256')
    def test05_file_query(self,object_key='e9a12b356d3b6ff8264c3681d3a0614032a642acc537fc96a07008a9a6eb311f'):
        self.fq = ApiFile()
        r = self.fq.api_file_query(object_key)
        assert 0 == r['result']['status']
        assert 'ok' == r['result']['msg']
