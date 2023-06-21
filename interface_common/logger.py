import os
import time
import logging

"""日志相关配置"""

BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# 日志文件夹路径（不存在则创建）
LOG_PATH = os.path.join(BASE_PATH, "log")
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)


class Logger:
    def __init__(self):
        runtime = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        logfile = os.path.join(LOG_PATH, "{}.log".format(runtime))

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        # 日志输出格式
        self.formater = logging.Formatter('[%(asctime)s][%(filename)s %(lineno)d][%(levelname)s]: %(message)s')

        # 日志文件处理器
        self.file_handler = logging.FileHandler(logfile, mode='a+', encoding="UTF-8")
        self.file_handler.setLevel(logging.INFO)
        self.file_handler.setFormatter(self.formater)

        # 日志终端处理器
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setLevel(logging.DEBUG)
        self.stream_handler.setFormatter(self.formater)

        # 将日志处理器添加到logger中
        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.stream_handler)


logger = Logger().logger

if __name__ == '__main__':
    logger.info("info message test")
    logger.debug("debug message test")
