from iti.api.api_url import ApiUrl
import allure


@allure.epic('威胁情报中心web')
@allure.feature('url api测试')
class TestFile:
    def setup_class(self):
        # self.fq = ApiFile()
        pass

    # 查询URL
    @allure.story('查询黑样本URL')
    def test01_url_query(self,url="http://freedns.afraid.org/api/?action=getdyndns&sha=a30fa98efc092684e8d1c5cff797bcc613562978"):
        self.uq = ApiUrl()
        r = self.uq.api_url_query(url)
        assert 0 == r['result']['status']
        assert 'ok' == r['result']['msg']

    # # 参数为空
    # @allure.story('查询空URL')
    # def test02_url_query(self,url=""):
    #     self.uq = ApiUrl()
    #     r = self.uq.api_url_query(url)
    #     # assert 0 == r['result']['status']
    #     # assert 'ok' == r['result']['msg']
    #     assert 4007001 == r['result']['status']
    #     assert 'object not found' == r['result']['msg']