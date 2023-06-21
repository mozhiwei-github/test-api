import time
import uuid
import random
import calendar
import datetime
import arrow

"""常用功能函数"""


def get_unix_timestamp(millisecond=False):
    """
    获取当前时间戳
    @param millisecond: 是否返回毫秒级时间戳（13位）
    @return: 10位或13位整数的时间戳
    """
    if millisecond:
        return int(time.time() * 1000)
    return int(time.time())


def unix_timestamp_to_format_time(timestamp, millisecond=False):
    """
    时间戳转为格式化时间
    @param timestamp: 时间戳
    @param millisecond: 是否为毫秒时间戳
    @return: 格式化后的时间字符串
    """
    if millisecond:
        timestamp = timestamp / 1000
    # 转换成localtime
    time_local = time.localtime(timestamp)
    # 转换成新的时间格式(年-月-日 时:分:秒)
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return dt


def format_time_to_unix_timstamp(format_time, millisecond=False):
    """
    格式化时间转时间戳
    @param format_time: 格式化时间字符串
    @param millisecond: 是否返回毫秒级时间戳（13位）
    @return: 10位或13位整数的时间戳
    """
    # 转换成时间数组
    time_array = time.strptime(format_time, "%Y-%m-%d %H:%M:%S")
    # 转换成时间戳
    timestamp = time.mktime(time_array)
    if millisecond:
        return int(timestamp * 1000)
    return int(timestamp)


def day_to_second(day):
    """
    天数转秒数
    @param day: 天数
    @return: 秒数
    """
    return day * 24 * 60 * 60


def get_uuid(length=32):
    """
    随机生成uuid（最大32位）
    @param length: uuid长度
    @return: uuid字符串
    """
    return uuid.uuid4().hex[:length]


def get_month_range(year=None, month=None):
    """
    获取某个月的天数
    @param year: 月所在年份
    @param month: 月份
    @return:
        month_range: 天数
    """
    # 不传年份月份时，按当前时间所在月份计算
    if not year and not month:
        today = datetime.datetime.today()
        year = today.year
        month = today.month
    month_range = calendar.monthrange(year, month)[1]
    return month_range


def get_few_month_range(month_count, year=None, month=None):
    """
    获取连续N个月的天数
    @param month_count: 连续的月数量
    @param year: 开始计算的年份
    @param month: 开始计算的月份
    @return:
        month_range: 天数
    """
    month_range = 0
    # 不传年份月份时，按当前时间所在月份开始计算
    if not year and not month:
        today = datetime.datetime.today()
        year = today.year
        month = today.month
    # 循环添加N个月每月天数
    for i in range(month_count):
        cur_month_range = get_month_range(year, month)
        month_range += cur_month_range
        next_month = month + 1
        # 月份
        if next_month > 12:
            month = next_month % 12
            year += 1
        else:
            month = next_month
    return month_range

def get_spandays_month_range(month_count):
    """
    获取连续N个月的天数
    @param month_count: 连续的月数量
    @param year: 开始计算的年份
    @param month: 开始计算的月份
    @return:
        month_range: 天数
    """
    # 不传年份月份时，按当前时间所在月份开始计算
    today = arrow.now()
    aftertime = today.shift(months=month_count)
    month_range = (aftertime-today).days
    return month_range


def get_gbk2312(length=1):
    """
    获取随机中文字符串
    @param length: 字符串长度
    @return:
    """
    gbk_str = ""
    for i in range(length):
        head = random.randint(0xb0, 0xf7)
        body = random.randint(0xa1, 0xf9)
        val = f'{head:x} {body:x}'
        gbk_str += bytes.fromhex(val).decode('gb2312')
    return gbk_str


if __name__ == '__main__':
    print(get_unix_timestamp())
    print(get_unix_timestamp(millisecond=True))

    print(unix_timestamp_to_format_time(1642818108))
    print(unix_timestamp_to_format_time(1611287176178, millisecond=True))

    print(day_to_second(365))

    print(get_uuid(10))

    print(get_month_range())
    print(get_month_range(2024, 2))

    print(get_few_month_range(12))
    print(get_few_month_range(12, year=2024, month=1))

    print(get_gbk2312(5))

    print(format_time_to_unix_timstamp("2021-02-18 16:05:28"))
    print(format_time_to_unix_timstamp("2021-02-18 16:05:28", True))
