import pytest
import allure
import jsonpath
from pprint import pformat
from interface_common import tcweblib
import duba.dubalib as dubalib
from duba.config import data_source
from duba.constants import VipTypeInfo, StatusCode
from duba.api.tourist import tourist_bind_info_api, tourist_bind_api, tourist_login_api

"""毒霸游客账号 业务流程测试"""

TMP_DATA = {}


@allure.epic('毒霸游客账号 业务流程测试')
@allure.feature('场景：游客账号->创建游客->游客绑定->游客绑定查询')
class TestGuestAccount(object):
    @allure.story('1.创建游客')
    def test_create_account(self, product_data, case_config):
        gateway_origin = case_config["params"]["gateway_origin"]

        product = product_data["product"]

        allure.dynamic.description(
            '\t1.使用随机server_id生成游客账号\n'
            '\t2.校验游客账号接口返回数据的结构和数值\n'
            '\t3.校验已绑定的server id是否能创建游客账号\n'
        )
        allure.dynamic.title(f'创建游客_{product}')
        allure.dynamic.link("http://apix.kisops.com/project/750/interface/api/36501")

        with allure.step("step1：请求创建游客账号接口"):
            expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.create_account_res_data)
            res = tourist_login_api(gateway_origin, product, dubalib.create_server_id())

            assert res.status_code == expected_res.status_code

        with allure.step("step2：校验创建游客账号接口返回值"):
            res_data = res.json()
            allure.attach(pformat(expected_res.res_data), "预期响应结果")
            allure.attach(pformat(res_data), "实际响应结果")

            analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
            if not analysis_result:
                assert "校验创建游客账号失败" == 1
            else:
                allure.attach('接口返回结构符合预期', '接口返回结构实际结果')

            open_id = jsonpath.jsonpath(res_data, '$.data.user_info.open_id')[0]
            token = jsonpath.jsonpath(res_data, '$.data.token')[0]
            allure.attach(str(open_id) + " " + str(token), 'account返回结果')
            if not dubalib.check_account(open_id, token):
                assert "account与预期不符" == 1
                raise Exception("创建游客账号异常")
            else:
                TMP_DATA.update({"open_id_%s" % product: open_id})
                TMP_DATA.update({"token_%s" % product: token})

        with allure.step("step3：校验创建已绑定的游客"):
            binded_expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.binded_account_data)
            binded_res = tourist_login_api(gateway_origin, product, server_id="571148c501956a58592e39ad00029e56")

            binded_res_data = binded_res.json()
            allure.attach(pformat(binded_expected_res.res_data), "预期响应结果")
            allure.attach(pformat(binded_res_data), "实际响应结果")

            analysis_result = tcweblib.matchd_result(binded_expected_res.res_data, binded_res_data)
            assert analysis_result, "已绑定游客校验失败"

    @allure.story('2.游客绑定信息')
    def test_guest_bind_info(self, product_data, create_vip_account, case_config):
        gateway_origin = case_config["params"]["gateway_origin"]

        product = product_data["product"]

        allure.dynamic.description('\t1.创建正式用户与游客绑定\n')
        allure.dynamic.link("http://apix.kisops.com/project/750/interface/api/36511")

        open_id = TMP_DATA["open_id_%s" % product]

        account_info = create_vip_account
        vip_open_id = account_info["open_id"]
        vip_token = account_info["token"]
        user_identity = account_info["vip_type"]
        allure.dynamic.title(f'游客绑定信息 接口：{product} 用户：{VipTypeInfo[user_identity]["name"]}')

        if dubalib.check_account(vip_open_id, vip_token):
            with allure.step("step1：绑定游客账号接口"):
                expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
                # 绑定游客账号
                res = tourist_bind_api(gateway_origin, product, vip_open_id, vip_token, open_id)

                assert res.status_code == expected_res.status_code

            with allure.step("step2：校验绑定游客账号接口返回值"):
                res_data = res.json()
                allure.attach(pformat(expected_res.res_data), "预期响应结果")
                allure.attach(pformat(res_data), "实际响应结果")
                analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
                if not analysis_result:
                    assert "请求返回与预期不符" == 1
                else:
                    allure.attach(pformat(res_data), '接口返回结果')
                    allure.attach('接口返回结构符合预期', '接口返回结构实际结果')

            TMP_DATA.update({"vip_open_id_%s" % product: vip_open_id})
            TMP_DATA.update({"vip_token_%s" % product: vip_token})

        else:
            assert "vip_account与预期不符" == 1
            raise Exception("创建VIP账号异常")

    @allure.story('3.游客绑定查询')
    def test_check_bind_info(self, product_data, case_config):
        gateway_origin = case_config["params"]["gateway_origin"]

        product = product_data["product"]

        allure.dynamic.title(f'游客绑定查询 接口：{product}')
        allure.dynamic.description(
            '\t1.通过游客的openid和token查询绑定的正式用户信息\n'
            '\t2.校验正式用户信息能否与记录匹配的上\n'
        )
        allure.dynamic.link("http://apix.kisops.com/project/750/interface/api/36506")

        vip_open_id = TMP_DATA["vip_open_id_%s" % product]
        vip_token = TMP_DATA["vip_token_%s" % product]
        open_id = TMP_DATA["open_id_%s" % product]
        token = TMP_DATA["token_%s" % product]

        with allure.step("step1：绑定游客账号接口"):
            expected_res = data_source.ExpectedResult(StatusCode.OK.value, data_source.common_res_data)
            res = tourist_bind_info_api(gateway_origin, product, open_id, token)

            assert res.status_code == expected_res.status_code

        with allure.step("step2：校验绑定游客账号接口返回值"):
            res_data = res.json()
            allure.attach(pformat(expected_res.res_data), "预期响应结果")
            allure.attach(pformat(res_data), "实际响应结果")
            # 校验返回数据结构
            analysis_result = tcweblib.matchd_result(expected_res.res_data, res_data)
            # 校验openid和token
            res_open_id = jsonpath.jsonpath(res_data, '$.data.bind_info.open_id')[0]
            res_token = jsonpath.jsonpath(res_data, '$.data.bind_info.token')[0]

            allure.attach(vip_open_id, "vip_open_id")
            allure.attach(vip_token, "vip_token")
            if not analysis_result or res_open_id != vip_open_id or res_token != vip_token:
                assert "请求返回与预期不符" == 1
            else:
                allure.attach(pformat(res_data), '绑定游客账号返回结果')
