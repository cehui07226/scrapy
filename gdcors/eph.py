# coding:utf-8
# /usr/bin/python
import os
from ftplib import FTP
from sys import platform
from gpstime import gpsweek


class EphSite:
    def __init__(self, name, address, brdc, sp3, username='', password=''):
        self.name = name
        self.address = address
        self.brdc = brdc
        self.sp3 = sp3
        self.username = username
        self.password = password
        self.ftp = None

    def login(self):
        status = True
        try:
            self.ftp = FTP()
            self.ftp.set_debuglevel(0)
            self.ftp.connect(self.address, timeout=20)
            self.ftp.login(self.username, self.password)
            self.ftp.cwd('.')
        except:
            status = False
            self.ftp = None
        return status

    def gen_igs_name(self, year, doy):
        return 'igs' + str(gpsweek(year, doy)) + '.sp3.Z'

    def gen_igr_name(self, year, doy):
        return 'igr' + str(gpsweek(year, doy)) + '.sp3.Z'

    def gen_igu_name(self, year, doy):
        return 'igu' + str(gpsweek(year, doy)) + '_18.sp3.Z'

    def get_table(self, table_name, store_dir, name=None):
        raise NotImplementedError()

    def gen_brdc_path(self, year, doy):
        raise NotImplementedError()

    def gen_sp3_path(self, year, doy):
        return self.sp3 + str(gpsweek(year, doy))[:4] + '/'

    def get_brdc(self, year, doy, store_dir):
        if self.ftp is None:
            return False
        status = True
        auto_eph = "auto" + str(doy).rjust(3, '0') + "0." + str(year)[2:] + "n.Z"
        brdc_eph = "brdc" + str(doy).rjust(3, '0') + "0." + str(year)[2:] + "n.Z"
        eph = None
        try:
            self.ftp.cwd(self.gen_brdc_path(year, doy))
            rinex_files = self.ftp.nlst()
            if brdc_eph in rinex_files:
                eph = brdc_eph
            if auto_eph in rinex_files:
                eph = auto_eph
            if eph is not None:
                local_path = os.path.join(store_dir, eph)
                if os.path.isdir(store_dir) and (not os.path.exists(store_dir)):
                    os.makedirs(store_dir)
                fp = open(local_path, 'wb')
                cmd = 'RETR ' + eph
                self.ftp.retrbinary(cmd, fp.write)
                fp.close()
                if platform != 'win32':
                    os.system("uncompress " + local_path)
                else:
                    os.system('7z.exe e ' + local_path + ' -o' + store_dir)
                try:
                    os.remove(local_path)
                except:
                    pass
            else:
                raise IndexError("Cannot find the broadcast eph: %s." % eph)
        except:
            status = False
        return status

    def get_sp3(self, year, doy, store_dir, sp3):
        if self.ftp is None:
            return False
        status = True
        try:
            self.ftp.cwd(self.gen_sp3_path(int(year), int(doy)))
            sp3_files = self.ftp.nlst()
            if sp3 in sp3_files:
                local_path = os.path.join(store_dir, sp3)
                if os.path.isdir(store_dir) and (not os.path.exists(store_dir)):
                    os.makedirs(store_dir)
                fp = open(local_path, 'wb')
                cmd = 'RETR ' + sp3
                self.ftp.retrbinary(cmd, fp.write)
                fp.close()
                if platform != 'win32':
                    os.system("gunzip " + local_path)
                else:
                    os.system('7z.exe e ' + local_path + ' -o' + store_dir)
                try:
                    os.remove(local_path)
                except:
                    pass
            else:
                raise IndexError("Cannot find the sp3 eph: %s." % sp3)
        except Exception as e:
            print e
            status = False
        return status

    def __str__(self):
        return "%s %s" % (self.name, self.address)

    def quit(self):
        if self.ftp is not None:
            try:
                self.ftp.quit()
                self.ftp = None
            except:
                pass


class SOPAC(EphSite):
    def __init__(self):
        EphSite.__init__(self, 'SOPAC', 'garner.ucsd.edu', '/pub/rinex/', '/pub/products/', 'anonymous',
                         'cehui07226@hotmail.com')

    def get_table(self, table_name, store_dir, name=None):
        if self.ftp is None:
            return False
        status = True
        local_path = os.path.join(store_dir, table_name)
        if os.path.isdir(store_dir) and (not os.path.exists(store_dir)):
            os.makedirs(store_dir)
        if name is not None:
            local_path = os.path.join(store_dir, name)
        try:
            self.ftp.cwd('/pub/gamit/tables/')
            tables = self.ftp.nlst()
            if table_name in tables:
                fp = open(local_path, 'w')
                cmd = 'RETR ' + table_name
                self.ftp.retrlines(cmd, fp.write)
                fp.close()
            else:
                raise IndexError("Cannot find the table: %s." % table_name)
        except:
            status = False
        return status

    def gen_brdc_path(self, year, doy):
        return self.brdc + str(year) + '/' + str(doy).rjust(3, '0') + '/'


class CDDIS(EphSite):
    def __init__(self):
        EphSite.__init__(self, 'CDDIS', 'cddis.gsfc.nasa.gov', '/pub/gps/data/daily/', '/gps/products/')

    def gen_brdc_path(self, year, doy):
        return self.brdc + str(year) + '/' + str(doy).rjust(3, '0') + '/' + str(year)[2:] + 'n/'


class NFS(EphSite):
    def __init__(self):
        EphSite.__init__(self, 'NFS', 'nfs.kasi.re.kr', '/gps/data/daily/', '/gps/products/')

    def gen_brdc_path(self, year, doy):
        return self.brdc + str(year) + '/' + str(doy).rjust(3, '0') + '/' + str(year)[2:] + 'n/'


class IGS(EphSite):
    def __init__(self):
        EphSite.__init__(self, 'IGS', 'igs.ensg.ign.fr', '/pub/igs/data/', '/pub/igs/products/')

    def gen_brdc_path(self, year, doy):
        return self.brdc + str(year) + '/' + str(doy).rjust(3, '0') + '/'


class WUHN(EphSite):
    def __init__(self):
        EphSite.__init__(self, 'WUHN', 'ics.gnsslab.cn', '/pub/gps/data/daily/', '/pub/gps/products/')

    def gen_brdc_path(self, year, doy):
        return self.brdc + str(year) + '/' + str(doy).rjust(3, '0') + '/'


def get_eph(year, doy, save_dir):
    brdc_status = False
    sp3_status = False
    local_eph_path = os.path.join(save_dir, 'eph')
    try:
        if not os.path.exists(local_eph_path):
            os.makedirs(local_eph_path)
    except Exception as e:
        print e
    try:
        sopac = SOPAC()
        sopac.login()
        auto_eph = os.path.join(local_eph_path, "auto" + str(doy).rjust(3, '0') + "0." + str(year)[2:] + "n")
        brdc_eph = os.path.join(local_eph_path, "brdc" + str(doy).rjust(3, '0') + "0." + str(year)[2:] + "n")
        if os.path.exists(auto_eph) or os.path.exists(brdc_eph):
            brdc_status = None
        else:
            brdc_status = sopac.get_brdc(year, doy, local_eph_path)
        igs_name = 'igs' + str(gpsweek(year, doy)) + '.sp3'
        igr_name = 'igr' + str(gpsweek(year, doy)) + '.sp3'
        igu_name = 'igu' + str(gpsweek(year, doy)) + '_18.sp3'
        igs_ephs = os.listdir(local_eph_path)
        if igs_name in igs_ephs:
            sp3_status = None
        elif igr_name in igs_ephs:
            sp3_status = sopac.get_sp3(year, doy, local_eph_path,
                                       igs_name + '.Z')  # if igr existed try download igs_eph
            if not sp3_status:
                sp3_status = None
        elif igu_name in igs_ephs:
            sp3_status = sopac.get_sp3(year, doy, local_eph_path, igs_name + '.Z')
            if not sp3_status:
                sp3_status = sopac.get_sp3(year, doy, local_eph_path, igr_name + '.Z')
                if not sp3_status:
                    sp3_status = None
        else:
            sp3_status = sopac.get_sp3(year, doy, local_eph_path, igs_name + '.Z')
            if not sp3_status:
                sp3_status = sopac.get_sp3(year, doy, local_eph_path, igr_name + '.Z')
                if not sp3_status:
                    sp3_status = sopac.get_sp3(year, doy, local_eph_path, igu_name + '.Z')
        sopac.ftp.quit()
    except Exception as e:
        print e
    return brdc_status, sp3_status


def choose_igs_eph(year, doy, save_dir):
    igs_name = 'igs' + str(gpsweek(year, doy)) + '.sp3'
    igr_name = 'igr' + str(gpsweek(year, doy)) + '.sp3'
    igu_name = 'igu' + str(gpsweek(year, doy)) + '_18.sp3'
    igs_root_path = os.path.join(save_dir, 'eph')
    igs_ephs = os.listdir(igs_root_path)
    if igs_name in igs_ephs:
        return igs_name
    elif igr_name in igs_ephs:
        return igr_name
    elif igu_name in igs_ephs:
        return igu_name
    else:
        return None
