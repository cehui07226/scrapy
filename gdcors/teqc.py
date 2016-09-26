# coding:utf-8
import math
import os
import shutil
import traceback


def trimble_to_rinex(year, src_path, out_dir):
    error = None
    interval = None
    print(src_path)
    if os.path.exists(src_path):
        year = str(year)
        directory, filename = os.path.split(src_path)
        name, suffix = filename.split('.')
        dat_path = os.path.join(directory, name + '.dat')
        rinex_name = name + '.' + year[2:] + 'o'
        nav_name = name + '.' + year[2:] + 'n'
        obs_save_path = os.path.join(out_dir, rinex_name)
        nav_save_path = os.path.join(out_dir, nav_name)
        try:
            os.system('bin2rnx.exe ' + src_path + ' ' + dat_path)
            shutil.move(os.path.join(directory, rinex_name), obs_save_path)
            os.remove(dat_path)
            os.remove(nav_save_path)
            interval = get_rinex_interval(obs_save_path)
        except Exception as e:
            print traceback.format_exc()
    else:
        error = Exception(str.format('{0} not found.', src_path))
    return interval, error


def change_interval(src_path, new_interval, out_dir):
    error = None
    if os.path.exists(src_path):
        directory, filename = os.path.split(src_path)
        save_path = os.path.join(out_dir, filename)
        try:
            os.system('teqc.exe -O.dec ' + str(new_interval) + ' ' + src_path + '>' + save_path)
        except Exception as e:
            error = e
            print e
    else:
        error = Exception(str.format('{0} not found.', src_path))
    return error


def get_rinex_interval(src_path):
    interval = None
    if os.path.exists(src_path):
        try:
            with open(src_path, 'r') as fp:
                for line in fp:
                    if line.__contains__('INTERVAL'):
                        interval = int(float(line.strip().split()[0]))
                        break
                fp.close()
        except:
            print traceback.format_exc()
    return interval


def get_rinex_coordinate(src_path):
    coord = []
    if os.path.exists(src_path):
        try:
            with open(src_path, 'r') as fp:
                for line in fp:
                    if line.__contains__('APPROX POSITION XYZ'):
                        coord = [float(item) for item in line.strip().split()[:3]]
                        break
                fp.close()
        except:
            print traceback.format_exc()
    return coord


def is_coord_equal(coord1, coord2):
    result = False
    try:
        delta_x = coord1[0] - coord2[0]
        delta_y = coord1[1] - coord2[1]
        delta_z = coord1[2] - coord2[2]
        if math.sqrt(math.pow(delta_x, 2) + math.pow(delta_y, 2) + math.pow(delta_z, 2)) < 300.0:
            result = True
    except:
        print traceback.format_exc()
    return result
