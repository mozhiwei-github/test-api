import json
from duba.config import data_source
from duba.constants import ServerHost
from interface_common import http_request as req

"""其他api接口"""


def apollo_data_api(server_host, namespace, key=None):
    """
    获取毒霸Apollo配置 （http://portal.apollo.zhhainiao.com/config.html?#/appid=pure_duba）
    @param server_host: 服务器地址
    @param namespace: 集合名称（yaml集合需要带.yaml后缀）
    @param key: 键名（缺省时返回集合下所有数据）
    @return:
    """
    # dev1没有Apollo配置接口，改用dev2的
    if server_host == ServerHost.DEV1.value:
        server_host = ServerHost.DEV2.value

    data = {"namespace": namespace}

    if key is not None:
        data["key"] = key

    res = req.request_type["application/json"](
        post_url="%s/api/apollo/data" % server_host,
        data=json.dumps(data, ensure_ascii=False),
        headers=data_source.headers
    )

    req.log_handler(res, "获取毒霸Apollo配置")

    return res
