import re
import subprocess
import traceback


def net_check(ip):
    status = False
    try:
        p = subprocess.Popen("ping.exe -l 1 -w 1 " + ip, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        out = p.stdout.read()
        regex = re.compile('TTL')
        if len(regex.findall(out)) != 0:
            status = True
    except:
        print traceback.format_exc()
    return status