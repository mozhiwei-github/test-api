from iti.api.api_domain import ApiDomain
import allure

@allure.epic('威胁情报中心web')
@allure.feature('domain api测试')
class TestFile:
    def setup_class(self):
        # self.fq = ApiFile()
        pass

    # 查询Domain,逆向
    @allure.story('查询黑样本domain')
    def test01_domain_query(self,object_key="xred.mooo.com"):
        self.dq = ApiDomain()
        r = self.dq.api_domain_query(object_key)
        assert 0 == r['result']['status']
        assert 'ok' == r['result']['msg']

    # 参数为空
    @allure.story('查询domain为空')
    def test02_domain_query(self,object_key=""):
        self.dq = ApiDomain()
        r = self.dq.api_domain_query(object_key)
        assert 0 == r['result']['status']
        assert 'ok' == r['result']['msg']

    # 查询domain,正向
    @allure.story('查询白样本domain')
    def test03_domain_query(self, object_key="www.baidu.com"):
        self.dq = ApiDomain()
        r = self.dq.api_domain_query(object_key)
        assert 0 == r['result']['status']
        assert 'ok' == r['result']['msg']

    # 查询domain,未知
    @allure.story('查询未知样本domain')
    def test04_domain_query(self, object_key="www.dnf999.com"):
        self.dq = ApiDomain()
        r = self.dq.api_domain_query(object_key)
        assert 0 == r['result']['status']
        assert 'ok' == r['result']['msg']