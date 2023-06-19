# 毒霸接口自动化测试

## 基本信息

测试平台地址：[http://auto.cf.com/dubatest.html](http://auto.cf.com/dubatest.html)

代码仓库：[http://autotest.cf.com:10101/summary/tc%2Ftcwebapitest.git](http://autotest.cf.com:10101/summary/tc%2Ftcwebapitest.git)

日志目录：log

报告目录：Outputs

---

## 环境与依赖

- python 3.9
- pip

### 安装依赖
```bash
pip install -r requirements.txt
```

---

## 脚本运行接口测试

接口测试任务类型
- 毒霸：duba-interface
- 元气壁纸：kwallpaper-interface
- 完美办公：ktemplate-interface

测试服配置文件：`<项目目录>/config/config.yml`

### 运行毒霸项目测试服1的全部用例

```bash
python run_interface_test.py duba-interface -c dev1/
```

### 运行毒霸项目测试服1的指定用例并生成html报告

```bash
python run_interface_test.py duba-interface -c dev1/test_pay_success.yml,dev1/test_tourist_pay_failure.yml -g
```

### 运行毒霸项目全部用例并启动报告服务

```bash
python run_interface_test.py duba-interface -c dev1/ -s
```

## 容器化运行接口测试

### 环境

- docker
- docker-compose

### 构建镜像

```bash
sudo docker build -t duba/interface:v1.0.0 -t duba/interface:latest .
```

### 使用最新镜像运行毒霸项目全部用例

```bash
sudo INTERFACE_IMAGE_VERSION="latest" INTERFACE_RUN_PARAMS="duba-interface -c dev1" docker-compose up
```

### 使用指定镜像运行指定用例

```bash
sudo INTERFACE_IMAGE_VERSION="v1.0.0" INTERFACE_RUN_PARAMS="duba-interface -c dev1/test_equipment_restrictions.yml" docker-compose up
```

### 复制容器内报告至当前目录

```bash
sudo docker cp <container-name>:/data/interface/Outputs ./
```