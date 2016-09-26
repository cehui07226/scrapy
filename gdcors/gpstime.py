#!coding:utf-8
# /usr/bin/python
from datetime import datetime, tzinfo, timedelta


def gpsdoy(year, month, day):
    """
    :return day of year
    :param year:
    :param month:
    :param day:
    :return:
    """
    return (datetime(year, month, day) - datetime(year, 1, 1)).days + 1


def gpsweek(year, doy):
    """
    Calculate the gps week. eg. 18241: 1824 is the gps week, 1 is the 2th day in the week.
    :param year:
    :param doy:
    :return:gps_week
    """
    day = (year - 1 - 1980) // 4 + 1 + (year - 1980) * 365 + doy - 6
    week = day // 7
    weekday = day % 7
    gpsweek = str(week) + str(weekday)
    return int(gpsweek)


class __GMT(tzinfo):
    delta = timedelta(hours=0)

    def utcoffset(self, dt):
        return self.delta

    def tzname(self, dt):
        return "GMT+0"

    def dst(self, dt):
        return self.delta


def gpsnow():
    return datetime.now(__GMT())