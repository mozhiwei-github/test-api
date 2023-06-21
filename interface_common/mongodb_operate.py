# -*- coding:utf-8 -*-
import requests

"""MongoDB数据库相关操作"""

DB_ADD = "http://autotest.cf.com/interface/addtcdb"  # 添加接口
DB_FIND = "http://autotest.cf.com/interface/findtcdb"  # 查询接口
DB_UPDATE = "http://autotest.cf.com/interface/uptcdb"  # 更新接口
DB_DELETE = "http://autotest.cf.com/interface/deltcdbbyid"  # 更新接口
TOKEN = "a7d21ba9cccf4aba817dfb66f0c3950b"


class MongoDBOperate:
    @staticmethod
    def add_data(db_data=dict):
        """
        插入数据
        :param db_data: 需要上传的数据，数据类型为dict
        :return: res.text
        """
        db_data.update({"token": TOKEN})
        res = requests.post(url=DB_ADD, json=db_data)
        return res

    @staticmethod
    def find_data(db_data=dict, skip=0, limit=1000000):
        """
        查找数据
        :param db_data: 需要查询的数据，数据类型为dict
        :param skip: 起始条数
        :param limit:返回总条数
        :return:直接返回数据库结果，包括数据或异常
        """
        db_data.update({"token": TOKEN})
        res = requests.post(
            url=DB_FIND + "?skip=%s&limit=%s" % (skip, limit),
            json=db_data
        )
        return res

    @staticmethod
    def update_data(condition=dict, db_data=dict):
        """
        更新数据
        @param condition:
        @param db_data:
        @return:
        """
        db_data = {"condition": condition, "setvalue": db_data}
        db_data.update({"token": TOKEN})
        res = requests.post(url=DB_UPDATE, json=db_data)
        return res

    @staticmethod
    def del_data(_id=str):
        """
        删除数据
        @param _id:
        @return:
        """
        db_data = {"_id": _id, "token": TOKEN}
        res = requests.post(url=DB_DELETE, json=db_data)
        return res
