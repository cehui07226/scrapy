# coding:utf-8
import argparse
import json
import time
from downloader import *
from eph import SOPAC
from reorganize import reorganize_binary, reorganize_gps_rinex, copy_rinex_from_remote_server
from report import make_reports

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
        # ***************************************************
        history_download_time_hour = config.getint('APPLICATION', 'HISTORY_DOWNLOAD_TIME_HOUR')
        history_download_time_min = config.getint('APPLICATION', 'HISTORY_DOWNLOAD_TIME_MIN')
        # ***************************************************
        loop_interval = config.getint('APPLICATION', 'LOOP_SLEEP_INTERVAL')
        days_before = config.getint('APPLICATION', 'DAYS_BEFORE')
        # ***************************************************
        if_reorganize = config.getint('REORGANIZE', 'ENABLE_REORGANIZE')
        if_report = config.getint('REPORT', 'ENABLE_REPORT')
        # ***************************************************
        start_eph_hour = config.getint('EPH', 'START_DOWNLOAD_HOUR')
        start_eph_min = config.getint('EPH', 'START_DOWNLOAD_MIN')
        # ***************************************************
        start_copy_rinex_hour = config.getint('REMOTE_GPS_RINEX', 'START_COPY_RINEX_HOUR')
        start_copy_rinex_min = config.getint('REMOTE_GPS_RINEX', 'START_COPY_RINEX_MIN')
        if_copy_remote_gps_rinex = config.getint('REMOTE_GPS_RINEX', 'ENABLE')
        # ***************************************************
        with open('stations.json', 'r') as file_pointer:
            all_stations = json.load(file_pointer)
            file_pointer.close()
        sorted(all_stations)
        try:
            if(hour == start_copy_rinex_hour) and (minute == start_copy_rinex_min):
                date_to_copy = now - timedelta(days=1)
                if if_copy_remote_gps_rinex:
                    copy_rinex_from_remote_server(date_to_copy)
            if (hour == start_download_time_hour) and (minute == start_down_time_min):
                download_date = now - timedelta(days=1)
                for stn in all_stations:
                    print os.linesep + stn.get('mark') + " " + str(now) + "  >>> "
                    download_station(download_date, **stn)
                if if_reorganize:
                    reorganize_gps_rinex(download_date)
                    reorganize_binary(download_date)
                if if_report:
                    make_reports(download_date)
            if (hour == start_eph_hour) and (minute == start_eph_min):
                igs_eph_cycle = config.getint('EPH', 'IGS_CYCLE')
                auto_date = now - timedelta(days=1)
                igs_date = now - timedelta(days=igs_eph_cycle)
                try:
                    sop = SOPAC()
                    sop.login()
                    yr = now.year
                    igs_doy = day_of_year(yr, igs_date.month, igs_date.day)
                    auto_doy = day_of_year(yr, auto_date.month, auto_date.day)
                    eph_save_dir = config.get('EPH', 'EPH_DIR')
                    auto_eph_save_path = os.path.join(eph_save_dir, 'auto' + auto_doy + '0.' + str(dt.year)[2:] + 'n')
                    igs_eph_save_path = os.path.join(eph_save_dir, sop.gen_igs_name(year, int(igs_doy)))
                    if not os.path.exists(eph_save_dir):
                        os.makedirs(eph_save_dir)
                    if not os.path.exists(auto_eph_save_path):
                        sop.get_brdc(yr, auto_doy, eph_save_dir)
                    if not os.path.exists(igs_eph_save_path):
                        sop.get_sp3(yr, igs_doy, eph_save_dir, sop.gen_igs_name(yr, int(igs_doy)).replace('.Z', ''))

                except:
                    print traceback.format_exc()
            if (hour == history_download_time_hour) and (minute == history_download_time_min):
                for j in range(1, days_before + 1):
                    current_date = now - timedelta(days=(days_before + 1 - j))
                    for stn in all_stations:
                        print os.linesep + stn.get('mark') + " " + str(current_date) + "  >>> "
                        try:
                            download_station(current_date, **stn)
                        except:
                            print traceback.format_exc()
                    if if_reorganize:
                        reorganize_gps_rinex(current_date)
                        reorganize_binary(current_date)
                    if if_report:
                        make_reports(current_date)
        except:
            print traceback.format_exc()
        time.sleep(loop_interval * 60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--ndays', type=int, help='days before today.')
    # 0 for False, 1 for True
    parser.add_argument('-o', '--organize', type=int, default=0, help='reorganize gps rinex data? 0: YES 1: NO Default: 0')
    parser.add_argument('-r', '--report', type=int, default=0, help='generate reorganized rinex usability report json file? 0: YES 1: NO Default: 0')
    parser.add_argument('-doy', '--doy', type=int, help='day of year. format: 020')
    parser.add_argument('-d', '--date', type=str, help='date. format: YYYYMMDD')
    parser.add_argument('-s', '--scrapy', type=int, default=0, help='download gps receiver binary data? 0: YES 1: NO Default: 0')
    parser.add_argument('-e', '--eph', type=int, default=0, help='download eph file? 0: YES 1: NO Default: 0')
    parser.add_argument('-c', '--copy', type=int, default=0, help="copy remote rinex file 'to' localhost? 0: YES 1: NO Default: 0")
    # 需要下载的日期集合
    dates = []

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
        print traceback.format_exc()
    if not len(dates):
        print "dates number is 0, exit 0."
        parser.print_help()
    else:
        print "{0} days to process.".format(len(dates))
        print "Beginning..."
        # 是否需要整理数据
        if_organize_data = args.organize
        if_make_report = args.report
        if_download_eph = args.eph
        if_download_data = args.scrapy
        if_copy_remote_rinex = args.copy
       
        with open('stations.json', 'r') as fp:
            stations = json.load(fp)
        sorted(stations)
        for dt in dates:
            if if_copy_remote_rinex:
                try:
                    copy_rinex_from_remote_server(dt)
                except:
                    print traceback.format_exc()
            if if_download_data:
                for station in stations:
                    try:
                        download_station(dt, **station)
                    except:
                        traceback.format_exc()
            if if_download_eph:
                config = ConfigParser()
                config.read('settings.ini')
                try:
                    sopac = SOPAC()
                    sopac.login()
                    year = dt.year
                    doy = day_of_year(year, dt.month, dt.day)
                    eph_dir = config.get('EPH', 'EPH_DIR')
                    auto_eph_path = os.path.join(eph_dir, 'auto' + day_of_year(dt.year, dt.month, dt.day) + '0.' + str(dt.year)[2:] + 'n')
                    auto_igs_path = os.path.join(eph_dir, sopac.gen_igs_name(year, int(doy)).replace('.Z', ''))
                    if not os.path.exists(eph_dir):
                        os.makedirs(eph_dir)
                    if not os.path.exists(auto_eph_path):
                        sopac.get_brdc(year, doy, eph_dir)
                    if not os.path.exists(auto_igs_path):
                        sopac.get_sp3(year, doy, eph_dir, sopac.gen_igs_name(year, int(doy)))
                except:
                    print traceback.format_exc()
            if if_organize_data:
                try:
                    reorganize_gps_rinex(dt)
                    reorganize_binary(dt)
                except:
                    print traceback.format_exc()
            if if_make_report:
                try:
                    make_reports(dt)
                except:
                    print traceback.format_exc()






