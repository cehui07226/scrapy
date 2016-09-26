# coding:utf-8
import sys
from datetime import datetime, timedelta

import requests


def day_of_year(year, month, day):
    try:
        year = int(year)
        month = int(month)
        day = int(day)
        start_date = datetime(year, 1, 1)
        date = datetime(year, month, day)
        delta = date - start_date
        return str(delta.days + 1).rjust(3, '0')
    except Exception as e:
        sys.stderr.write(e.message)


def doy_to_date(year, doy):
    if doy <= 0 or doy > 366:
        raise ValueError(u'错误的年积日')
    date_start_of_year = datetime(year, 1, 1)
    new_date = date_start_of_year + timedelta(days=(doy - 1))
    return new_date


def format_date_string(dt):
    return dt.strftime('%Y%m%d')


def get_system_name(ip):
    """
    根据netrs接收机地址，使用其编程接口: http://192.168.123.200/prog/Show?SystemName
    获得接收机标识：GTCH，格式：SystemName name=GTCH\n
    """
    url = "http://" + ip + "/prog/Show?SystemName"
    try:
        req = requests.get(url)
        content = req.content
        req.close()
        return content.split('=')[1].strip()
    except:
        return ""