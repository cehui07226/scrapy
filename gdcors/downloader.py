# coding:utf-8
import gc
import os
import traceback
import urllib2
from ftplib import FTP

from configparser import ConfigParser

import netck
from tools import *


def netrs_download_http(url, save_path):
    try:
        print(u"Downloading: {0}".format(url))
        req = urllib2.urlopen(url, timeout=15)
        with open(save_path, 'wb') as fp:
            fp.write(req.read())
            fp.close()
        req.close()
        gc.collect()
        print(u"URL: {0} downloaded.".format(url))
    except:
        pass


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
                suffix = filename.split('.')[0][-1].lower()
                save_file_name = name.lower() + doy + suffix + '.' + filename.split('.')[-1]
                save_path = os.path.join(save_dir, save_file_name)
                if not os.path.exists(save_dir):
                    os.mkdir(save_dir)
                print(u"Downloading: {0}, save to {1}".format(filename, save_file_name))
                fp = open(save_path, 'wb')
                cmd = 'RETR' + ' ' + filename
                ftp.retrbinary(cmd, fp.write)
                fp.close()
                print(u"{0} downloaded.".format(save_file_name))
    except Exception as e:
        raise e
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
        print traceback.format_exc()
    finally:
        try:
            ftp.quit()
        except:
            print traceback.format_exc()
        del ftp


def gnss_download(address, name, section, section_suffix, date_str, save_dir):
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
        ftp.cwd(NETR9_ROOT_DIRECTORY + '/' + section + '/' + year + '/' + month + '/' + day)
        files = ftp.nlst()
        for item in files:
            filename = item.split()[-1]
            if '.T0' in filename.upper():
                remote_file_size = ftp.size(filename)
                save_file_name = name.lower() + filename[4:8] + section_suffix + '.' + filename.split('.')[-1]
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
                    gnss_upload(save_path, name, year, day_of_year(year, month, day))
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


def gnss_upload(path_to_upload, name, year, doy):
    cp = ConfigParser()
    cp.read('settings.ini')
    FTP_TIMEOUT = cp.getint('FTP', 'FTP_TIMEOUT')
    FTP_PORT = cp.getint('FTP', 'FTP_PORT')
    FTP_DEBUG_LEVEL = cp.getint('FTP', 'FTP_DEBUG_LEVEL')
    GNSS_SERVER_ADDR = cp.get('GNSS', 'GNSS_SERVER_ADDR')
    GNSS_USERNAME = cp.get('GNSS', 'GNSS_USERNAME')
    GNSS_PASSWORD = cp.get('GNSS', 'GNSS_PASSWORD')
    GNSS_REMOTE_DIRECTORY = cp.get('GNSS', 'GNSS_REMOTE_DIRECTORY')
    if not (os.path.exists(path_to_upload) and os.path.isfile(path_to_upload)):
        sys.stderr.write(u"File {0} to upload, not exist!".format(path_to_upload))
        return
    ftp = FTP()
    ftp.set_debuglevel(FTP_DEBUG_LEVEL)
    try:
        ftp.connect(GNSS_SERVER_ADDR, FTP_PORT, FTP_TIMEOUT)
        ftp.login(GNSS_USERNAME, GNSS_PASSWORD)
        ftp.cwd('.')
        dirs = [GNSS_REMOTE_DIRECTORY, 't02', year, doy, name]
        for r_dir in dirs:
            try:
                ftp.mkd(r_dir)
            except Exception as e:
                sys.stderr.write(e.message)
            finally:
                ftp.cwd(r_dir)
        filename = os.path.basename(path_to_upload)
        file_list = ftp.nlst()
        existed_files = [item.split()[-1] for item in file_list]
        if filename in existed_files:
            if os.path.getsize(path_to_upload) <= ftp.size(filename):
                print(u"File: {0} existed!".format(filename))
            else:
                print(u"Uploading: {0}.".format(path_to_upload))
                fp = open(path_to_upload, 'rb')
                ftp.storbinary('STOR %s' % filename, fp)
                fp.close()
                print(u"{0} Uploaded.".format(path_to_upload))
        else:
            print(u"Uploading: {0}.".format(path_to_upload))
            fp = open(path_to_upload, 'rb')
            ftp.storbinary('STOR %s' % filename, fp)
            fp.close()
            print(u"Uploaded {0}.".format(path_to_upload))
    except Exception as e:
        sys.stderr.write(u"GNSS: {0} raise an exception {1} when uploading.".format(name, e))
    finally:
        try:
            ftp.quit()
        except Exception as e:
            pass
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


def server_download(address, name, year, doy, gps_save_dir, raw_save_dir):
    cp = ConfigParser()
    cp.read('settings.ini')
    FTP_TIMEOUT = cp.getint('FTP', 'FTP_TIMEOUT')
    FTP_PORT = cp.getint('FTP', 'FTP_PORT')
    FTP_DEBUG_LEVEL = cp.getint('FTP', 'FTP_DEBUG_LEVEL')
    SERVER_ROOT_DIRECTORY = cp.get('SERVER', 'SERVER_ROOT_DIRECTORY')
    ftp = FTP()
    ftp.set_debuglevel(FTP_DEBUG_LEVEL)
    try:
        ftp.connect(address, FTP_PORT, FTP_TIMEOUT)
        ftp.login()
        ftp.cwd(SERVER_ROOT_DIRECTORY + '/' + year + '/' + doy)
        files = ftp.nlst()
        for item in files:
            filename = item.split()[-1]
            remote_file_size = ftp.size(filename)
            suffix = filename.split('.')[0][-1].lower()
            if not os.path.exists(gps_save_dir):
                os.makedirs(gps_save_dir)
            if not os.path.exists(raw_save_dir):
                os.makedirs(raw_save_dir)
            if (name.upper() in filename.upper()) and (filename.split('.')[-1].upper() in ['RAW', 'T01', 'T02', 'T00']):
                save_file_name = name.lower() + doy + suffix + '.' + filename.split('.')[-1]
                if '.T0' in filename.upper():
                    save_path = os.path.join(gps_save_dir, save_file_name)
                elif ".RAW" in filename.upper():
                    save_file_name = os.path.join(raw_save_dir, save_file_name)
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
        pass
    finally:
        try:
            ftp.quit()
        except Exception as e:
            pass
        del ftp


def download_station(dt, **stn):
    ymdStr = format_date_string(dt)
    mark = stn.get('mark')
    year = str(dt.year)
    doy = day_of_year(dt.year, dt.month, dt.day)
    cp = ConfigParser()
    cp.read('settings.ini')
    BINARY_LOCAL_DIRECTORY = cp.get('GPS_BIN_DIR', 'BINARY_LOCAL_DIRECTORY')
    GNSS_DIRECTORY = cp.get('GNSS', 'GNSS_DIRECTORY')
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
                try:
                    netrs_download(address, mark, ymdStr, save_dir)
                except:
                    print traceback.format_exc()
                    try:
                        system_name = get_system_name(address)
                        suffix = section.get('suffix')
                        http_prefix = "http://" + address + "/download/" + ymdStr[:6] + "/"
                        remote_filename = system_name + ymdStr + suffix + ".T00"
                        url = http_prefix + remote_filename
                        local_file_name = mark.lower() + doy + suffix[-1] + ".T00"
                        save_path = os.path.join(save_dir, local_file_name)
                        os.system('netrs.exe ' + url + ' ' + save_path)
                    except:
                        print traceback.format_exc()

        elif receiver_type == 'NETR9':
            for section in sections:
                upload = section.get('upload')
                alias = section.get('alias')
                section_name = section.get('name')
                suffix = section.get('suffix')
                if upload:
                    enable_gnss = cp.getint('GNSS', 'ENABLE_DOWNLOAD')
                    if not enable_gnss:
                        print "{0}'s receiver: {1} was disabled in global setting file.".format(mark, receiver_type)
                        continue
                    save_dir = os.path.join(GNSS_DIRECTORY, year, doy, alias.upper())
                    if not os.path.exists(save_dir):
                        os.makedirs(save_dir)
                    gnss_download(address, alias, section_name, suffix, ymdStr, save_dir)
                else:
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
                section_name = section.get('name')
                netr9_download(address, mark, section_name, ymdStr, save_dir)

        elif receiver_type == 'SERVER':
            enable_server = cp.getint('SERVER', 'ENABLE_DOWNLOAD')
            if not enable_server:
                print "{0}'s receiver: {1} was disabled in global setting file.".format(mark, receiver_type)
                continue
            save_dir = os.path.join(BINARY_LOCAL_DIRECTORY, year, doy)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            for section in sections:
                server_download(address, mark, year, doy, save_dir, RAW_DIRECTORY)

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


