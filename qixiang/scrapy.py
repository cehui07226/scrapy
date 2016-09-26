# coding:utf-8
import argparse
import json
import time
from downloader import *


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def loop_main():
    config = ConfigParser()
    while True:
        config.read('settings.ini')
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        start_download_time_hour = config.getint('APPLICATION', 'START_DOWNLOAD_TIME_HOUR')
        start_down_time_min = config.getint('APPLICATION', 'START_DOWNLOAD_TIME_MIN')
        history_download_time_hour = config.getint('APPLICATION', 'HISTORY_DOWNLOAD_TIME_HOUR')
        history_download_time_min = config.getint('APPLICATION', 'HISTORY_DOWNLOAD_TIME_MIN')
        loop_interval = config.getint('APPLICATION', 'LOOP_SLEEP_INTERVAL')
        days_before = config.getint('APPLICATION', 'DAYS_BEFORE')
        with open('stations.json', 'r') as file_pointer:
            all_stations = json.load(file_pointer)
            file_pointer.close()
        sorted(all_stations)
        try:
            if (hour == start_download_time_hour) and (minute == start_down_time_min):
                download_date = now - timedelta(days=1)
                for stn in all_stations:
                    print os.linesep + stn.get('mark') + " " + str(now) + "  >>> "
                    download_station(download_date, **stn)
            if (hour == history_download_time_hour) and (minute == history_download_time_min):
                for j in range(1, days_before + 1):
                    current_date = now - timedelta(days=(days_before + 1 - j))
                    for stn in all_stations:
                        print os.linesep + stn.get('mark') + " " + str(current_date) + "  >>> "
                        try:
                            download_station(current_date, **stn)
                        except:
                            print traceback.format_exc()

        except:
            traceback.format_exc()
        time.sleep(loop_interval * 60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--ndays', type=int, help='days before today.')
    # 0 for False, 1 for True
    parser.add_argument('-doy', '--doy', type=int, help='day of year, three letter like 032')
    parser.add_argument('-d', '--date', type=str, help='the date string like yyyymmdd')
    # 需要下载的日期集合
    dates = []
    # 是否需要整理数据
    args = parser.parse_args()
    try:
        if args.doy is not None:
            year = datetime.now().year
            dates.append(doy_to_date(year, args.doy))
        elif args.ndays is not None:
            for i in range(1, args.ndays + 1):
                c_date = datetime.now() - timedelta(days=(args.ndays + 1 - i))
                dates.append(c_date)
        elif args.date is not None:
            year = int(args.date[:4])
            month = int(args.date[4:6])
            day = int(args.date[6:])
            dates.append(datetime(year, month, day, 0, 0, 0))
        else:
            print "Looping... DO NOT close the application."
            loop_main()
            print "For more command arguments, see the help below."
            parser.print_help()
    except:
        traceback.format_exc()
    if not len(dates):
        print "dates number is 0, exit 0."
        parser.print_help()
    else:
        print "{0} days to process.".format(len(dates))
        print "Beginning..."
        with open('stations.json', 'r') as fp:
            stations = json.load(fp)
        sorted(stations)
        for dt in dates:
            for station in stations:
                try:
                    download_station(dt, **station)
                except:
                    traceback.format_exc()
