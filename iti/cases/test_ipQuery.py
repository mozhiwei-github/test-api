from iti.api.api_ip import ApiIp
import allure


@allure.epic('威胁情报中心web')
@allure.feature('ip api测试')
class TestFile:
    def setup_class(self):
        # self.fq = ApiFile()
        pass

    # 查询ip,逆向
    @allure.story('查询黑样本ip')
    def test01_ip_query(self,object_key="46.82.174.69"):
        self.iq = ApiIp()
        r = self.iq.api_ip_query(object_key)
        assert 0 == r['result']['status']
        assert 'ok' == r['result']['msg']

    # 参数为空
    @allure.story('查询ip为空')
    def test02_ip_query(self,object_key=""):
        self.iq = ApiIp()
        r = self.iq.api_ip_query(object_key)
        assert 4006001 == r['result']['status']
        assert 'objectKey and objectId cannot both be empty' == r['result']['msg']

    # # ipv6 目前不支持IPV6
    # @allure.story('查询ip v6')
    # def test03_ip_query(self, object_key="fe80::8d8a:1059:c93:f9ac%4"):
    #     self.iq = ApiIp()
    #     r = self.iq.api_ip_query(object_key)
    #     assert 4007001 == r['result']['status']
    #     assert 'object not found' == r['result']['msg']