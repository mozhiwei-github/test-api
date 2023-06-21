import pymysql
from interface_common.logger import logger

"""MySQL数据库相关操作"""

# TODO: 数据库配置写入配置文件中；不同环境对应不同配置
# DB_CONF = {
#     "host": "gz-cdb-drwjswdl.sql.tencentcdb.com",
#     "port": 61428,
#     "user": "new_duba",
#     "password": "guw1wlftal0yn88ehxagdyosu2pumb",
#     "db": "new_duba"
# }
DB_CONF = {
    "host": "gz-cdb-koa3usz3.sql.tencentcdb.com",
    "port": 61307,
    "user": "new_duba_test",
    "password": "wb2nz78wzy58sb6iflqgu7v96a279irr",
    "db": "new_duba_test"
}


class MysqlDB:
    def __init__(self, db_conf=DB_CONF):
        # 通过字典拆包传递配置信息，建立数据库连接
        self.conn = pymysql.connect(**db_conf, autocommit=True)
        # 通过 cursor() 创建游标对象，并让查询结果以字典格式输出
        self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    def __del__(self):  # 对象资源被释放时触发，在对象即将被删除时的最后操作
        # 关闭游标
        self.cur.close()
        # 关闭数据库连接
        self.conn.close()

    def select_db(self, sql, values=None):
        """查询"""
        try:
            # 检查连接是否断开，如果断开就进行重连
            self.conn.ping(reconnect=True)
            # 使用 execute() 执行sql
            self.cur.execute(sql, values)
            # 使用 fetchall() 获取查询结果
            data = self.cur.fetchall()
            return data
        except Exception as e:
            logger.error("MySQL查询出现错误，错误原因：{}".format(e))
            raise e

    def execute_db(self, sql, values=None):
        """更新/新增/删除"""
        try:
            # 检查连接是否断开，如果断开就进行重连
            self.conn.ping(reconnect=True)
            # 使用 execute() 执行sql
            self.cur.execute(sql, values)
            # 提交事务
            self.conn.commit()
        except Exception as e:
            logger.error("操作MySQL出现错误，错误原因：{}".format(e))
            # 回滚所有更改
            self.conn.rollback()
            raise e


try:
    db = MysqlDB(DB_CONF)
except Exception as e:
    logger.error("数据库链接失败 error = {}".format(e))
    raise Exception("数据库链接失败")
