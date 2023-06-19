FROM python:3.9-alpine

ADD . /data/interface
WORKDIR /data/interface

# 设置为上海时区
RUN echo "Asia/Shanghai" > /etc/timezone
# 配置pip阿里源
RUN pip3 config set global.index-url http://mirrors.aliyun.com/pypi/simple
RUN pip3 config set install.trusted-host mirrors.aliyun.com
# 安装python依赖
RUN python3 -m pip install --no-cache-dir -r requirements.txt

CMD python3 run_interface_test.py