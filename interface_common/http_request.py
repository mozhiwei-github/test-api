# -*- coding:utf-8
import json
import allure
import requests
from pprint import pformat
from interface_common.logger import logger
from requests_toolbelt.multipart.encoder import MultipartEncoder


class HTTPRequest:
    """如果有SSL、重定向等问题，参数后面再加"""

    @staticmethod
    def post_by_form(post_url=None,
                     data=None,
                     cookies=None,
                     headers=None,
                     verify=None):
        """
        :param post_url: 请求的url
        :param data: 字典格式的数据
        :param cookies: cookies
        :param headers: headers
        :param verify: 是否对SSL证书进行验证
        """
        if headers is None:
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        if post_url is not None:
            res = requests.post(url=post_url,
                                data=data,
                                cookies=cookies,
                                headers=headers,
                                verify=verify)
            return res
        else:
            raise Exception("post_url is None")

    @staticmethod
    def post_by_form_data(post_url=None,
                          data=None,
                          cookies=None,
                          headers=None,
                          verify=None):
        """
        :param data:
        带文件：
        data={'field0': 'value', 'field1': 'value',
            'field2': ('filename', open('file.py', 'rb'), 'text/plain'),
            'field3': ('filename2', open('file2.py', 'rb'), 'application/octet-stream')}
        不带文件：
        fields={'field0': 'value', 'field1': 'value'}
        :param post_url: 请求的url
        :param cookies: cookies
        :param headers: headers
        :param verify: 是否对SSL证书进行验证
        """
        m = MultipartEncoder(fields=data)
        if headers is not None:
            headers["Content-Type"] = m.content_type
        else:
            headers = {'Content-Type': m.content_type}
        if post_url is not None:
            res = requests.post(url=post_url,
                                data=m,
                                cookies=cookies,
                                headers=headers,
                                verify=verify)
            return res
        else:
            raise Exception("post_url is None")

    @staticmethod
    def post_by_json(post_url=None,
                     data=None,
                     cookies=None,
                     headers=None,
                     json_data=None,
                     verify=None):
        """
        :param post_url: 请求的url
        :param data: 字典格式的数据
        :param cookies: cookies
        :param headers: headers
        :param json_data: json格式的数据
        :param verify: 是否对SSL证书进行验证
        """

        if headers is None:
            headers = {'Content-Type': 'application/json'}
        if post_url is not None:
            if json_data is not None:
                res = requests.post(url=post_url,
                                    json=json_data,
                                    headers=headers,
                                    cookies=cookies,
                                    verify=verify)
                return res
            else:
                res = requests.post(url=post_url,
                                    data=data,
                                    headers=headers,
                                    cookies=cookies,
                                    verify=verify)
                return res
        else:
            raise Exception("post_url is None")

    @staticmethod
    def post_by_xml(post_url=None,
                    data=None,
                    cookies=None,
                    headers=None,
                    verify=None):
        """
        :param post_url: 请求的url
        :param data: 字典格式的数据
        :param cookies: cookies
        :param headers: headers
        :param verify: 是否对SSL证书进行验证
        """

        if headers is None:
            headers = {'Content-Type': 'application/xml'}
        if post_url is not None:
            res = requests.post(url=post_url,
                                data=data,
                                headers=headers,
                                cookies=cookies,
                                verify=verify)
            return res
        else:
            raise Exception("post_url is None")

    @staticmethod
    def post_by_binary(post_url=None,
                       files=None,
                       cookies=None,
                       headers=None,
                       verify=None):
        """
        :param files: 例如 {'file': open('report.txt', 'rb')}
        :param post_url: 请求的url
        :param cookies: cookies
        :param headers: headers
        :param verify: 是否对SSL证书进行验证
        """
        if headers is None:
            headers = {'Content-Type': 'binary'}
        if post_url is not None:
            res = requests.post(url=post_url,
                                files=files,
                                headers=headers,
                                cookies=cookies,
                                verify=verify)
            return res
        else:
            raise Exception("post_url is None")

    @staticmethod
    def request_get(get_url=None,
                    data=None,
                    headers=None,
                    verify=None):
        """
        :param get_url: 请求的url
        :param data: 字典格式的数据
        :param headers: headers
        :param verify: 是否对SSL证书进行验证
        """
        if get_url is not None:
            res = requests.get(url=get_url,
                               params=data,
                               headers=headers,
                               verify=verify)
            return res
        else:
            raise Exception("get_url is None")

    @staticmethod
    def request_head(url):
        """
        向网页发出 HEAD 请求，并返回 HTTP 标头
        @param url: 请求的url
        @return:
        """
        res = requests.head(url)
        return res


"""根据不同类型，返回函数地址"""
request_type = {
    "application/x-www-form-urlencoded": HTTPRequest.post_by_form,
    "multipart/form-data": HTTPRequest.post_by_form_data,
    "application/json": HTTPRequest.post_by_json,
    "application/xml": HTTPRequest.post_by_xml,
    "binary": HTTPRequest.post_by_binary
}


def log_handler(res, interface_name, attach_allure=True, decode_res_data=True):
    """
    接口日志处理
    @param res: 接口响应结果
    @param interface_name: 接口名称
    @param attach_allure: 是否显示日志到allure报告中
    @param decode_res_data: 是否解析响应结果并输出至日志
    @return:
    """
    if res.request.body:
        try:
            request_body_format = pformat(json.loads(res.request.body))
        except:
            request_body_format = res.request.body
    else:
        request_body_format = ""
    request_headers_format = pformat(dict(res.request.headers))
    logger.info("{0}接口url: {1}".format(interface_name, res.request.url))
    logger.info("{0}接口请求参数: \n{1}".format(interface_name, request_body_format))
    logger.info("{0}接口请求headers: \n{1}".format(interface_name, request_headers_format))
    if attach_allure:
        allure.attach(res.request.url, "{0}接口url".format(interface_name))
        allure.attach(request_body_format, "{0}接口请求参数".format(interface_name))
        allure.attach(request_headers_format, "{0}接口请求headers".format(interface_name))

    if not decode_res_data:
        return

    try:
        res_data = json.loads(res.text)
    except Exception as e:
        res_data = res.text

    logger.info("{name}接口状态码：{status_code}，响应结果：\n{res_data}".format(
        name=interface_name,
        status_code=res.status_code,
        res_data=pformat(res_data)
    ))

# if __name__ == "__main__":
#     import hashlib, time
#
#     time_stamp = str(time.time()).split(".")[0]
#     token = "unique_salt" + time_stamp
#     md5hash = hashlib.md5(token.encode())
#     verifyToken = str(md5hash.hexdigest())
#     print(HTTPRequest.post_by_form_data("http://store.liebao.cn/manage/protected/extensions/uploadify/uploadextension.php",
#                                          {
#         'Filename': "1.jpg",
#         'type': "3",
#         'token': verifyToken,
#         'timestamp': time_stamp,
#         'Filedata': ("1.jpg", open(r"C:\Users\kingsoft.kingsoft-PC\Pictures\1.jpg", 'rb'), 'application/octet-stream'),
#         'Upload': 'Submit Query'
#     }
#     ).text)
