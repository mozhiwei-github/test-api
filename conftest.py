from interface_common.logger import logger

"""
pytest全局共用fixture
"""


def pytest_addoption(parser):
    """pytest自定义命令行参数"""
    parser.addoption("--caseconfig", action="store", type=str, help="测试用例配置")
    parser.addoption("--testserver", action="store", type=str, help="测试服地址")


def runtest_hook_exception(multicall, phase):
    """
    各阶段异常钩子共用处理
    @param multicall:
    @param phase: 阶段名称
    @return:
    """
    try:
        multicall.execute()
    except AssertionError as e:  # 捕获断言异常写入日志
        logger.exception('[{phase}]检验错误: {exception}'.format(phase=phase, exception=e))
        raise e
    except Exception as e:  # 捕获其他异常写入日志
        logger.exception('[{phase}]运行错误: {exception}'.format(phase=phase, exception=e))
        raise e


def pytest_runtest_setup(__multicall__):
    """pytest设置阶段钩子"""
    runtest_hook_exception(__multicall__, "setup")


def pytest_runtest_call(__multicall__):
    """pytest调用阶段钩子"""
    runtest_hook_exception(__multicall__, "runtest")


def pytest_runtest_teardown(__multicall__):
    """pytest卸载阶段钩子"""
    runtest_hook_exception(__multicall__, "teardown")
