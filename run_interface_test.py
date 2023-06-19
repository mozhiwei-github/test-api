import os
import json
import pytest
from interface_common.logger import logger
from interface_common.yaml_reader import YamlReader

"""毒霸接口测试用例启动文件"""


def run_with_yaml(yaml_list, serve, generate, project, test_server):
    file_path = os.path.abspath(os.path.dirname(__file__))
    interface_path = os.path.join(file_path, project["root_path"])
    config_path = os.path.join(interface_path, project["config_path"])
    case_yaml_dict = {}

    # 遍历传入的文件列表，拼接出实际运行的用例文件和 caseconfig 参数
    for yaml_full_name in yaml_list:
        yaml_name_info = yaml_full_name.split('/', 1)
        if len(yaml_name_info) == 1:
            yaml_group = yaml_full_name
            yaml_name = None
        else:
            yaml_group, yaml_name = yaml_name_info

        yaml_path_list = []
        # 当传入用例参数为 "配置目录名/" 时，读取目录下所有的用例配置文件
        if not yaml_name:
            group_path = os.path.join(config_path, yaml_group)
            if not os.path.exists(group_path):
                continue

            for filename in os.listdir(group_path):
                group_yaml_name = os.path.join(group_path, filename)
                yaml_path_list.append(group_yaml_name)
        else:
            yaml_path_list.append(os.path.join(yaml_group, yaml_name))  # TODO 为何不拼接完整路径?

        for group_yaml_path in yaml_path_list:
            yaml_path = os.path.join(config_path, group_yaml_path)    # TODO 该操作不是应该在上一个循环就处理掉?
            yaml_data = YamlReader.read_yaml(yaml_path)

            path_params = [os.path.join(project["root_path"], project["case_path"], yaml_data["file"])]
            case_class = yaml_data["class"]
            case_func = yaml_data["case"]
            case_desc = yaml_data["desc"]
            logger.info(f"用例：{case_desc}")
            if case_class:
                path_params.append(case_class)
            if case_func:
                path_params.append(case_func)
            case_path = "::".join(path_params)
            case_yaml_dict[case_path] = yaml_path

    if not case_yaml_dict:
        logger.info("案例列表为空，退出执行")
        return

    allure_attach_path = os.path.join("Outputs", "allure")
    allure_html_path = os.path.join("Outputs", "report")
    allure_absolute_path = os.path.join(file_path, allure_attach_path)
    if os.path.exists(allure_absolute_path):
        for file in os.listdir(allure_absolute_path):
            os.remove(os.path.join(allure_absolute_path, file))

    pytest_args = [
        '-s',
        '-q',
        # '-n=8',
        # '--tb=no',
        '--tb=short',
        *case_yaml_dict.keys(),
        '--alluredir=%s' % allure_attach_path,
        '--caseconfig={}'.format(json.dumps(case_yaml_dict))
    ]

    if test_server:
        pytest_args.append(f'--testserver={test_server}')

    pytest.main(pytest_args)

    if os.listdir(allure_absolute_path):
        # 存在generate参数，生成html报告
        if generate:
            logger.info("生成allure html报告中...")
            os.system("allure generate %s -o %s" % (allure_attach_path, allure_html_path))

        # 存在serve参数，启动本地服务查看html报告
        if serve:
            logger.info("启动allure报告服务中...")
            os.system("allure serve %s" % allure_attach_path)
    else:
        logger.info("allure日志目录为空")


if __name__ == "__main__":
    import argparse

    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yml")
    reader = YamlReader()
    config_data = reader.read_yaml(config_path)

    parser = argparse.ArgumentParser("For Interface Test Automation")
    parser.add_argument("project", choices=config_data.keys(), help="项目名称")
    parser.add_argument("-c", "--conf", help="测试用例文件列表（*.yml），多个文件用英文逗号分隔。", required=True)
    parser.add_argument("-s", "--serve", action='store_true',
                        help="是否以allure服务形式查看报告。（需本机已安装allure命令）")
    parser.add_argument("-g", "--generate", action='store_true',
                        help="是否生成allure html报告。（需本机已安装allure命令）")
    parser.add_argument("-ts", "--testserver", help="测试服务器地址（废弃）")
    args = parser.parse_args()

    conf_list = []
    if args.conf:
        # 前端传过来的 conf 参数为用逗号分隔的多个文件名字符串
        conf_list = args.conf.split(",")

    run_with_yaml(conf_list, args.serve, args.generate, config_data[args.project], args.testserver)
