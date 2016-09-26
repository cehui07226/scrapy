# coding:utf-8
import json
import os
import traceback
from datetime import datetime, date
from glob import glob


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, o)


class RinexMeta(object):
    def __init__(self, start, end, hour, interval, percent, mp1, mp2, slip, size):
        self._start = start
        self._end = end
        self._hour = hour
        self._interval = interval
        self._percent = percent
        self._mp1 = mp1
        self._mp2 = mp2
        self._slip = slip
        self._size = size

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value):
        self._start = value

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value):
        self._end = value

    @property
    def hour(self):
        return self._hour

    @hour.setter
    def hour(self, value):
        self._hour = value

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, value):
        self._interval = value

    @property
    def percent(self):
        return self._percent

    @percent.setter
    def percent(self, value):
        self._percent = value

    @property
    def mp1(self):
        return self._mp1

    @mp1.setter
    def mp1(self, value):
        self._mp1 = value

    @property
    def mp2(self):
        return self._mp2

    @mp2.setter
    def mp2(self, value):
        self._mp2 = value

    @property
    def slip(self):
        return self._slip

    @slip.setter
    def slip(self, value):
        self._slip = value

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value

    def to_json_str(self):
        result = json.dumps({'start': self.start,
                             'end': self.end,
                             'hour': self.hour,
                             'interval': self.interval,
                             'percent': self.percent,
                             'mp1': self.mp1,
                             'mp2': self.mp2,
                             'slip': self.slip,
                             'size': self.size
                             }, sort_keys=True, cls=DateTimeEncoder)
        return result

    @staticmethod
    def get_rinex_meta(year, obs_path, nav_path):
        meta = None
        if os.path.exists(obs_path):
            try:
                year = str(year)
                directory, filename = os.path.split(obs_path)
                name, suffix = filename.split('.')
                result_filename = name + '.' + year[2:] + 'S'
                os.system('sed.exe -i /RCV\s*CLOCK\s*OFFS\s*APPL/d ' + obs_path)
                os.system('teqc.exe +qc -nav ' + nav_path + ' ' + obs_path)
                result_path = os.path.abspath(os.path.join(directory, result_filename))
                size = os.path.getsize(obs_path)
                meta = RinexMeta.from_s_file(result_path, size)
                os.remove(result_path)
                to_delete_temp_files = [sed_temp for sed_temp in glob("sed*") if not sed_temp.__contains__('.')]
                for sed in to_delete_temp_files:
                    os.remove(sed)
            except:
                print traceback.format_exc()
        return meta

    def __str__(self):
        return self.to_json_str()

    @staticmethod
    def from_json_str(json_str):
        decoded_json = json.loads(json_str)
        meta = None
        try:
            start = datetime.strptime(decoded_json.get('start'), "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(decoded_json.get('end'), "%Y-%m-%d %H:%M:%S")
            hour = decoded_json.get('hour')
            interval = decoded_json.get('interval')
            percent = decoded_json.get('percent')
            mp1 = decoded_json.get('mp1')
            mp2 = decoded_json.get('mp2')
            slip = decoded_json.get('slip')
            size = decoded_json.get('size')
            meta = RinexMeta(start, end, hour, interval, percent, mp1, mp2, slip, size)
        except:
            pass
        return meta

    @staticmethod
    def from_s_file(s_file_path, size):
        meta = None
        if os.path.exists(s_file_path):
            with open(s_file_path, 'r') as fp:
                lines = fp.readlines()
                line_count = len(lines)
                for i in range(line_count):
                    line = lines[i].strip()
                    if line.__contains__("hrs"):
                        result_line = lines[i+1]
                        fields = result_line.split()
                        start_year = 2000 + int(fields[1])
                        start_month = int(fields[2])
                        start_day = int(fields[3])
                        start_hour = int(fields[4].split(':')[0])
                        start_minute = int(fields[4].split(':')[1])
                        start = datetime(start_year, start_month, start_day, start_hour, start_minute, 0)
                        end_year = 2000 + int(fields[5])
                        end_month = int(fields[6])
                        end_day = int(fields[7])
                        end_hour = int(fields[8].split(':')[0])
                        end_minute = int(fields[8].split(':')[1])
                        end = datetime(end_year, end_month, end_day, end_hour, end_minute, 0)
                        hour = float(fields[9])
                        interval = int(fields[10])
                        percent = float(fields[13])
                        mp1 = float(fields[14])
                        mp2 = float(fields[15])
                        slip = int(fields[16])
                        meta = RinexMeta(start, end, hour, interval, percent, mp1, mp2, slip, size)
                        break
                fp.close()
        return meta
