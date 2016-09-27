# coding:utf-8
import os
import traceback
from ftplib import FTP

from configparser import ConfigParser

import netck
from tools import *


def netrs_download(address, name, date_str, save_dir):
    cp = ConfigParser()
    cp.read('settings.ini')
    FTP_TIMEOUT = cp.getint('FTP', 'FTP_TIMEOUT')
    FTP_PORT = cp.getint('FTP', 'FTP_PORT')
    FTP_DEBUG_LEVEL = cp.getint('FTP', 'FTP_DEBUG_LEVEL')
    ftp = FTP()
    ftp.set_debuglevel(FTP_DEBUG_LEVEL)
    try:
        ymStr = date_str[:6]
        year = date_str[:4]
        month = date_str[4:6]
        day = date_str[6:]
        doy = day_of_year(year, month, day)
        ftp.connect(address, FTP_PORT, FTP_TIMEOUT)
        ftp.login()
        ftp.cwd(ymStr)
        files = ftp.nlst()
        for item in files:
            filename = item.split()[-1]
            if (filename.endswith('.T00')) and (name.upper() in filename.upper()) and (date_str in filename):
                remote_file_size = ftp.size(filename)
                suffix = filename.split('.')[0][-1].lower()
                save_file_name = name.lower() + doy + suffix + '.' + filename.split('.')[-1]
                save_path = os.path.join(save_dir, save_file_name)
                if not os.path.exists(save_dir):
                    os.mkdir(save_dir)
                if (not os.path.exists(save_path)) or remote_file_size > os.path.getsize(save_path):
                    print(u"Downloading: {0}, save to {1}".format(filename, save_file_name))
                    fp = open(save_path, 'wb')
                    cmd = 'RETR' + ' ' + filename
                    ftp.retrbinary(cmd, fp.write)
                    fp.close()
                    print(u"{0} downloaded.".format(save_file_name))
                else:
                    print(u"File: {0} is existed.".format(save_file_name))
    except:
        print traceback.format_exc()
    finally:
        try:
            ftp.quit()
        except:
            pass
        del ftp


def netr9_download(address, name, section_name, date_str, save_dir):
    cp = ConfigParser()
    cp.read('settings.ini')
    FTP_TIMEOUT = cp.getint('FTP', 'FTP_TIMEOUT')
    FTP_PORT = cp.getint('FTP', 'FTP_PORT')
    FTP_DEBUG_LEVEL = cp.getint('FTP', 'FTP_DEBUG_LEVEL')
    NETR9_ROOT_DIRECTORY = cp.get('NETR9', 'NETR9_ROOT_DIRECTORY')
    ftp = FTP()
    ftp.set_debuglevel(FTP_DEBUG_LEVEL)
    try:
        ftp.connect(address, FTP_PORT, FTP_TIMEOUT)
        ftp.login()
        year = date_str[:4]
        month = date_str[4:6]
        day = date_str[6:]
        doy = day_of_year(year, month, day)
        ftp.cwd(NETR9_ROOT_DIRECTORY + '/' + section_name + '/' + year + '/' + month + '/' + day)
        files = ftp.nlst()
        for item in files:
            filename = item.split()[-1]
            if ('.T0' in filename.upper()) and (name.upper() in filename.upper()):
                remote_file_size = ftp.size(filename)
                suffix = filename.split('.')[0][-1].lower()
                save_file_name = name.lower() + doy + suffix + '.' + filename.split('.')[-1]
                save_path = os.path.join(save_dir, save_file_name)
                if not os.path.exists(save_dir):
                    os.mkdir(save_dir)
                if (not os.path.exists(save_path)) or remote_file_size > os.path.getsize(save_path):
                    print(u"Downloading: {0}, save to {1}".format(filename, save_file_name))
                    fp = open(save_path, 'wb')
                    cmd = 'RETR' + ' ' + filename
                    ftp.retrbinary(cmd, fp.write)
                    fp.close()
                    print(u"{0} downloaded.".format(save_file_name))
                else:
                    print(u"File: {0} is existed.".format(save_file_name))
    except:
        traceback.format_exc()
    finally:
        try:
            ftp.quit()
        except:
            traceback.format_exc()
        del ftp


def pdb318_download(address, name, year, doy, save_dir):
    cp = ConfigParser()
    cp.read('settings')
    cp.read('settings.ini')
    FTP_TIMEOUT = cp.getint('FTP', 'FTP_TIMEOUT')
    FTP_PORT = cp.getint('FTP', 'FTP_PORT')
    FTP_DEBUG_LEVEL = cp.getint('FTP', 'FTP_DEBUG_LEVEL')
    PDB318_ROOT_DIRECTORY = cp.get('BDS', 'PDB318_ROOT_DIRECTORY')
    USERNAME = cp.get('BDS', 'PDB318_USERNAME')
    PASSWORD = cp.get('BDS', 'PDB318_PASSWORD')
    ftp = FTP()
    ftp.set_debuglevel(FTP_DEBUG_LEVEL)
    try:
        ftp.connect(address, FTP_PORT, FTP_TIMEOUT)
        ftp.login(USERNAME, PASSWORD)
        ftp.cwd(PDB318_ROOT_DIRECTORY + '/' + year + '/' + doy)
        files = ftp.nlst()
        for item in files:
            filename = item.split()[-1]
            if ('.RAW' in filename.upper()) and (name.upper() in filename.upper()):
                remote_file_size = ftp.size(filename)
                suffix = filename.split('.')[0][-1].lower()
                save_file_name = name.lower() + doy + suffix + '.' + filename.split('.')[-1]
                save_path = os.path.join(save_dir, save_file_name)
                if not os.path.exists(save_dir):
                    os.mkdir(save_dir)
                if (not os.path.exists(save_path)) or remote_file_size > os.path.getsize(save_path):
                    print(u"Downloading: {0}, save to {1}".format(filename, save_file_name))
                    fp = open(save_path, 'wb')
                    cmd = 'RETR' + ' ' + filename
                    ftp.retrbinary(cmd, fp.write)
                    fp.close()
                    print(u"{0} downloaded.".format(save_file_name))
                else:
                    print(u"File: {0} is existed.".format(save_file_name))
    except Exception as e:
        sys.stderr.write(u"Panda: {0} raise an exception {1} when downloading.".format(name, e))
    finally:
        try:
            ftp.quit()
        except Exception as e:
            sys.stderr.write(e.message)
        del ftp


def download_station(dt, **stn):
    ymdStr = format_date_string(dt)
    mark = stn.get('mark')
    year = str(dt.year)
    doy = day_of_year(dt.year, dt.month, dt.day)
    cp = ConfigParser()
    cp.read('settings.ini')
    BINARY_LOCAL_DIRECTORY = cp.get('GPS_BIN_DIR', 'BINARY_LOCAL_DIRECTORY')
    RAW_DIRECTORY = cp.get('BDS', 'PDB318_RAW_DIRECTORY')
    for receiver in stn.get("receivers"):
        sections = receiver.get('sections')
        receiver_type = receiver.get('type')
        address = receiver.get('address')
        if not netck.net_check(address):
            print " >>> {0}'s Receiver: {1} disconnected, address is: {2}".format(mark, receiver_type, address)
            continue
        is_enable = receiver.get('enable')
        if not is_enable:
            print "{0}'s receiver: {1} disabled for some reason.".format(mark, address)
            continue
        if receiver_type == 'NETRS':
            enable_netrs = cp.getint('NETRS', 'ENABLE_DOWNLOAD')
            if not enable_netrs:
                print "{0}'s receiver: {1} was disabled in global setting file.".format(mark, address)
                continue
            save_dir = os.path.join(BINARY_LOCAL_DIRECTORY, year, doy)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            for section in sections:
                netrs_download(address, mark, ymdStr, save_dir)

        elif receiver_type == 'NETR9':
            for section in sections:
                section_name = section.get('name')
                suffix = section.get('suffix')
                enable_netr9 = cp.getint('NETR9', 'ENABLE_DOWNLOAD')
                if not enable_netr9:
                    print "{0}'s receiver: {1} was disabled in global setting file.".format(mark, receiver_type)
                    continue
                save_dir = os.path.join(BINARY_LOCAL_DIRECTORY, year, doy)
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                netr9_download(address, mark, section_name, ymdStr, save_dir)

        elif receiver_type == 'NETR5':
            enable_netr5 = cp.getint('NETR9', 'ENABLE_DOWNLOAD')
            if not enable_netr5:
                print "{0}'s receiver: {1} was disabled in global setting file.".format(mark, receiver_type)
                continue
            save_dir = os.path.join(BINARY_LOCAL_DIRECTORY, year, doy)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            for section in sections:
                suffix = section.get('suffix')
                section_name = section.get('name')
                netr9_download(address, mark, section_name, ymdStr, save_dir)

        elif receiver_type == 'PDB318':
            enable_pdb318 = cp.getint('BDS', 'ENABLE_DOWNLOAD')
            if not enable_pdb318:
                print "{0}'s receiver: {1} was disabled in global setting file.".format(mark, receiver_type)
                continue
            save_dir = os.path.join(RAW_DIRECTORY, year, doy)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            for section in sections:
                pdb318_download(address, mark, year, doy, save_dir)


