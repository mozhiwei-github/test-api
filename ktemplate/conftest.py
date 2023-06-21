import os
import json
import pytest
from pprint import pformat
from interface_common.logger import logger
from interface_common.yaml_reader import YamlReader
from ktemplate.constants import VipType

"""
完美办公项目共用fixture
"""


def pytest_generate_tests(metafunc):
    # 获取命令行参数中测试用例配置
    case_config_str = metafunc.config.getoption("--caseconfig")
    if case_config_str is None:
        return
    case_config_data = json.loads(case_config_str)

    # 测试用例函数地址
    node_id = metafunc.definition.nodeid
    node_name = node_id.split("/")[-1:][0]
    case_path = None

    in_case_config = False
    for case_config_key in case_config_data:
        case_config_name = os.path.split(case_config_key)[-1:][0]
        case_config_path = case_config_key.split(case_config_name)[0]
        # 匹配当前运行的用例是否存在参数配置
        if node_name.startswith(case_config_name):
            case_path = case_config_path + case_config_name
            in_case_config = True
            break
    if not in_case_config:
        logger.info("未找到 {0} 在测试用例配置参数中相关信息，caseconfig = \n{1}".format(node_id, pformat(case_config_data)))
        return

    # 获取配置参数中用例对应的yaml文件，并读取相关配置信息
    yaml_path = case_config_data[case_path]
    yaml_data = YamlReader.read_yaml(yaml_path)
    yaml_params = yaml_data["params"]

    # 遍历用例涉及的fixture函数，使用配置信息中的参数值替换fixture的入参
    fixture_names = metafunc.fixturenames
    for fixture in fixture_names:
        if fixture == "case_config":
            try:
                metafunc.parametrize("case_config", [yaml_data], indirect=True)
            except Exception as e:
                logger.exception("case_config parametrize error")
                raise e
        elif fixture == "create_account" and "user_identity" in yaml_params:
            user_identity_list = yaml_params["user_identity"]
            user_identity_params = []
            for user_identity in user_identity_list:
                try:
                    user_identity_item = VipType[user_identity]
                except Exception as e:
                    logger.exception("[conftest]VipType[%s] error" % user_identity)
                    raise e
                else:
                    user_identity_params.append(user_identity_item)

            # user_identity 参数值为空时，设置为默认参数
            if len(user_identity_params) == 0:
                user_identity_params = VipType

            try:
                # create_account fixture 参数化
                metafunc.parametrize("create_account", user_identity_params, indirect=True)
            except Exception as e:
                logger.exception("create_account parametrize error")
                raise e


@pytest.fixture(scope="function")
def case_config(request):
    """获取自定义参数caseoption中测试用例配置"""
    return request.param


@pytest.fixture(scope="function")
def create_account(request):
    """
    创建完美办公账号
    @param request:
    @return:
        uid: 用户uid
        token: 用户token
        vip_type: 会员等级枚举成员，例：VipType.NON_VIP
    """
    vip_type = request.param  # 会员等级枚举成员

    # TODO: 待服务端解决登录Mock问题后，改为实际的创建账号逻辑
    if vip_type == VipType.GUEST:
        result = {
            "uid": "",
            "token": "",
        }
    else:
        result = {
            "uid": "3514893495805",
            "token": "60d29812-3325ffa6dfd-384b7638c79cef32_5457c6",
        }

    result["vip_type"] = vip_type

    yield result
