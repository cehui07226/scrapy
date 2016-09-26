# coding:utf-8
import os
import shutil
import traceback

from configparser import ConfigParser

import teqc
from tools import *


def reorganize_gps_rinex(dt):
    config = ConfigParser()
    config.read('settings.ini')
    dir_keys = config.options('GPS_RINEX_DIRS')
    year = str(dt.year)
    doy = day_of_year(dt.year, dt.month, dt.day)
    for key in dir_keys:
        session_dir = config.get('GPS_RINEX_DIRS', key)
        if not os.path.exists(session_dir):
            continue
        # /5/2016/304
        source_rinex_directory = os.path.join(session_dir, year, doy)
        if not os.path.exists(source_rinex_directory):
            continue
        # /5/2016/304/gtch
        site_dirs = os.listdir(source_rinex_directory)
        for site_dir in site_dirs:
            abs_site_dir = os.path.join(source_rinex_directory, site_dir)
            if not os.path.exists(abs_site_dir):
                continue
            files = os.listdir(abs_site_dir)
            # 查找rinex观测文件
            for rinex_file in files:
                if rinex_file.upper().endswith(year[2:] + 'O'):
                    rinex_file_path = os.path.join(abs_site_dir, rinex_file)
                    copy_rinex(rinex_file_path, year, doy)


def copy_rinex(path, year, doy):
    if os.path.exists(path):
        config = ConfigParser()
        config.read('settings.ini')
        year = str(year)
        dest_rinex_directory = config.get('REORGANIZE', 'GPS_RINEX_DIRECTORY')
        directory, filename = os.path.split(path)
        try:
            interval = teqc.get_rinex_interval(path)
            if interval is not None:
                save_dir = os.path.join(dest_rinex_directory, str(interval), year, doy)
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                save_path = os.path.join(save_dir, filename)
                copy_flag = False
                if os.path.exists(save_path):
                    if os.path.getsize(save_path) < os.path.getsize(path):
                        copy_flag = True
                else:
                    copy_flag = True
                if copy_flag:
                    shutil.copy(path, save_path)
                    print str(datetime.now()) + " >>> copied " + path
        except:
            print traceback.format_exc()


def copy_rinex_from_remote_server(dt):
    """
    拷贝数据存储软件存储在52服务器上的rinex到本地存储目录
    :param dt: 需要拷贝数据所对应的时间，精确到天
    :param flag: 指示是否删除源数据
    :return:
    """
    year = str(dt.year)
    doy = day_of_year(dt.year, dt.month, dt.day)
    config = ConfigParser()
    config.read('settings.ini')
    mapped_rinex_dir = config.get('REMOTE_GPS_RINEX', 'MAPPED_DIR')
    if_delete_source = config.getint('REMOTE_GPS_RINEX', 'DELETE_SOURCE')
    dest_rinex_dir = os.path.join(config.get('REMOTE_GPS_RINEX', 'COPY_TO'), year, doy)
    source_rinex_directory = os.path.join(mapped_rinex_dir, year, doy)
    if not (os.path.exists(source_rinex_directory) and os.path.isdir(source_rinex_directory)):
        return
    site_dirs = [item for item in os.listdir(source_rinex_directory)]
    for site_dir in site_dirs:
        abs_site_dir = os.path.join(source_rinex_directory, site_dir)
        if not (os.path.exists(abs_site_dir) and os.path.isdir(abs_site_dir)):
            continue
        source_files = [item for item in os.listdir(abs_site_dir) if item.upper().endswith(year[2:] + 'O')]
        for source_file in source_files:
            dest_site_dir = os.path.join(dest_rinex_dir, site_dir)
            if not os.path.exists(dest_site_dir):
                os.makedirs(dest_site_dir)
            dest_save_path = os.path.join(dest_site_dir, source_file)
            if not os.path.exists(dest_save_path):
                try:
                    source_file_path = os.path.join(abs_site_dir, source_file)
                    shutil.copy(source_file_path, dest_save_path)
                    if if_delete_source:
                        shutil.rmtree(abs_site_dir, ignore_errors=True)
                except:
                    print traceback.format_exc()


def reorganize_binary(dt):
    config = ConfigParser()
    config.read('settings.ini')
    BINARY_LOCAL_DIRECTORY = config.get('GPS_BIN_DIR', 'BINARY_LOCAL_DIRECTORY')
    year = str(dt.year)
    doy = day_of_year(dt.year, dt.month, dt.day)
    bin_directory = os.path.join(BINARY_LOCAL_DIRECTORY, year, doy)
    dest_rinex_directory = config.get('REORGANIZE', 'GPS_RINEX_DIRECTORY')

    if os.path.exists(bin_directory):
        files = [os.path.join(bin_directory, bin_file) for bin_file in os.listdir(bin_directory) if bin_file.__contains__('.T0')]
        for bin_file_path in files:
            try:
                interval, _ = teqc.trimble_to_rinex(year, bin_file_path, bin_directory)
                directory, filename = os.path.split(bin_file_path)
                name, suffix = filename.split('.')
                rinex_name = name.upper() + '.' + year[2:] + 'o'
                obs_path = os.path.join(bin_directory, rinex_name)
                obs_save_dir = os.path.join(dest_rinex_directory, str(interval), year, doy)
                save_rinex_name = name.upper()[:7] + '0.' + year[2:] + 'o'
                obs_save_path = os.path.join(obs_save_dir, save_rinex_name)
                move_flag = False
                if interval is not None:
                    if os.path.exists(obs_save_path):
                        coord2 = teqc.get_rinex_coordinate(obs_save_path)
                        coord1 = teqc.get_rinex_coordinate(obs_path)
                        
                        if teqc.is_coord_equal(coord1, coord2) and os.path.getsize(obs_path) != os.path.getsize(obs_save_path):
                            move_flag = True
                    else:
                        move_flag = True
                        if not os.path.exists(obs_save_dir):
                            os.makedirs(obs_save_dir)
                    if move_flag:
                        shutil.move(obs_path, obs_save_path)
                    else:
                        os.remove(obs_path)
            except:
                print traceback.format_exc()
