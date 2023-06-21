import os
import json
import pytest
from pprint import pformat
from interface_common.logger import logger
from interface_common.yaml_reader import YamlReader

def pytest_generate_tests(metafunc):
    # 获取命令行参数中测试用例配置
    case_config_str = metafunc.config.getoption("--caseconfig")
    if case_config_str is None:
        return
    case_config_data = json.loads(case_config_str)

    # # 获取命令行参数中测试服地址
    # test_server = metafunc.config.getoption("--testserver")

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
        logger.info("未找到 {0} 在测试用例配置参数中相关信息，caseconfig = \n{1}".format(
            node_id, pformat(case_config_data)))
        return

    # 获取配置参数中用例对应的yaml文件，并读取相关配置信息
    yaml_path = case_config_data[case_path]
    yaml_data = YamlReader.read_yaml(yaml_path)
    yaml_params = yaml_data["params"]

    fixture_names = metafunc.fixturenames
    for fixture in fixture_names:
        if fixture == "case_config":
            try:
                metafunc.parametrize("case_config", [yaml_data], indirect=True)
            except Exception as e:
                logger.exception("case_config parametrize error")
                raise e


@pytest.fixture(scope="function")
def case_config(request):
    """获取自定义参数caseoption中测试用例配置"""
    return request.param
