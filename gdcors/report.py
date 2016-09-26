# coding:utf-8
from configparser import ConfigParser
from tools import *
from datetime import datetime
import json
import os
from meta import RinexMeta
import traceback
import io


def make_reports(dt):
    if not isinstance(dt, datetime):
        raise TypeError(dt)
    year = str(dt.year)
    doy = day_of_year(dt.year, dt.month, dt.day)
    config = ConfigParser()
    config.read('settings.ini')
    eph_dir = config.get('EPH', 'EPH_DIR')
    auto_filename = 'auto' + doy + '0.' + year[2:] + 'n'
    auto_path = os.path.join(eph_dir, auto_filename)
    if not os.path.exists(auto_path):
        print "EPH {0} does not exists.".format(auto_path)
        return
    with open('stations.json', 'r') as fp:
        stations_json = json.load(fp)
        fp.close()
    try:
        stations = [(int(station.get('id')), station.get('mark')) for station in stations_json]
    except:
        print traceback.format_exc()
        return
    gps_report_root_dir = config.get('REPORT', 'GPS_REPORT_DIR')
    gps_rinex_root_dir = config.get('REORGANIZE', 'GPS_RINEX_DIRECTORY')
    if not os.path.exists(gps_rinex_root_dir):
        print "The rinex root directory {0} does not exists.".format(gps_rinex_root_dir)
        return
    rinex_dirs = [os.path.join(gps_rinex_root_dir, session_dir) for session_dir in os.listdir(gps_rinex_root_dir)
                  if (os.path.isdir(os.path.join(gps_rinex_root_dir, session_dir)) and str.isdigit(str(session_dir)))]
    reports = [{"id": stn[0], "mark": stn[1], "usability": []} for stn in stations]
    for rinex_dir in rinex_dirs:
        source_dir = os.path.join(rinex_dir, year, doy)        
        if not os.path.exists(source_dir):
            continue
        rinex_files = [os.path.join(source_dir, item) for item in os.listdir(source_dir) if item.upper().__contains__('0.' + year[2:] + 'O')]
        for rinex_file in rinex_files:
            try:
                meta = RinexMeta.get_rinex_meta(year, rinex_file, auto_path)
                _, name = os.path.split(rinex_file)
                mark = name[:4].upper()
                for report in reports:
                    if report.get('mark').upper() == mark:
                        report['usability'].append(meta.to_json_str())
                        break
            except:
                print traceback.format_exc()
    gps_report_save_dir = os.path.join(gps_report_root_dir, year)
    if not os.path.exists(gps_report_save_dir):
        os.makedirs(gps_report_save_dir)
    gps_report_save_path = os.path.join(gps_report_save_dir, doy + ".json")
    content = json.dumps(reports, sort_keys=True, ensure_ascii=False)
    with io.open(gps_report_save_path, 'w', encoding='utf-8') as fp:
        fp.write(content)

