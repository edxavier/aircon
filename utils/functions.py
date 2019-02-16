#!/usr/bin/python
import select
import click
import re
__author__ = 'Eder Xavier Rojas'
# Creado  07-09-15
from datetime import timedelta
import datetime
from .helper_classes import Pysntp

ENDC='\033[0m'
BOLD='\033[01m'
#Foreground
fgGreen='\033[32m'
fgLightred='\033[31m'
fgYellow='\033[93m'
bgLightgrey='\033[49m'

OK = fgGreen+BOLD
WARNING = fgYellow+BOLD
ERROR = fgLightred+BOLD

def clear_multiple_spaces(text=""):
    return ' '.join(text.split())

def get_position(host="127.0.0.1", ssh=None):

    # Send the command (non-blocking)
    stdin, stdout, stderr = ssh.exec_command("cat /root/pos")

    # Wait for the command to terminate
    values = []
    for i, line in enumerate(stdout):
        if i <= 3:
            line = line.rstrip()
            line = line.rstrip('\n').rstrip('\r').strip()
            line = clear_multiple_spaces(line)
            values.append(line)
    if len(values) > 0:
        return values[0]
    else:
        return "----"
        #print "%d: %s" % (i, line)


def get_memory(host="127.0.0.1", ssh=None):

    # Send the command (non-blocking)
    stdin, stdout, stderr = ssh.exec_command("free -m")

    # Wait for the command to terminate
    values = []
    for i, line in enumerate(stdout):
        if i <= 3:
            line = line.rstrip()
            line = line.rstrip('\n').rstrip('\r').strip()
            line = clear_multiple_spaces(line)
            values.append(line)
    ram = str(values[1]).split()
    swap = str(values[3]).split()
    free_ram_percent = (float(ram[3]) / float(ram[1])) * 100
    return ram[1], ram[3]+" ("+"{0:.2f}".format(free_ram_percent)+"%)", swap[1]+"/"+ swap[3]

        #print "%d: %s" % (i, line)

def get_uptime(host="127.0.0.1", ssh=None):

    # Send the command (non-blocking)
    stdin, stdout, stderr = ssh.exec_command("cat /proc/uptime")

    # Wait for the command to terminate
    values = []
    for i, line in enumerate(stdout):
        line = line.rstrip()
        line = line.rstrip('\n').rstrip('\r').strip()
        line = clear_multiple_spaces(line)
        values.append(line)
    uptime_seconds = float(str(values[0]).split()[0])
    uptime_string = str(timedelta(seconds = uptime_seconds))
    return uptime_string.split('.')[0]

def get_cpu_usage(host="127.0.0.1", ssh=None):

    # Send the command (non-blocking)
    stdin, stdout, stderr = ssh.exec_command("mpstat")

    # Wait for the command to terminate
    values = []
    for i, line in enumerate(stdout):
        line = line.rstrip()
        line = line.rstrip('\n').rstrip('\r').strip()
        line = clear_multiple_spaces(line)
        values.append(line)

    splited = str(values[3]).split()
    usage = 100 - float(splited[len(splited)-2])
    return "{0:.2f}".format(usage)+"%"

def get_load_avg(host="127.0.0.1", ssh=None):
    # Send the command (non-blocking)
    stdin, stdout, stderr = ssh.exec_command("cat /proc/loadavg")

    # Wait for the command to terminate
    values = []
    for i, line in enumerate(stdout):
        line = line.rstrip()
        line = line.rstrip('\n').rstrip('\r').strip()
        line = clear_multiple_spaces(line)
        values.append(line)

    splited = str(values[0]).split()
    load_avg = (float(splited[0])+float(splited[1])+float(splited[2])/3)
    procs = splited[3]
    return "{0:.2f}".format(load_avg), procs

def get_disk_usage(host="127.0.0.1", ssh=None):
    # Send the command (non-blocking)
    stdin, stdout, stderr = ssh.exec_command("df -hT /")

    # Wait for the command to terminate
    values = []
    for i, line in enumerate(stdout):
        line = line.rstrip()
        line = line.rstrip('\n').rstrip('\r').strip()
        line = clear_multiple_spaces(line)
        values.append(line)

    if len(values) > 2:
        splited = str(values[2]).split()
        percent = splited[len(splited)-2]
    else:
        splited = str(values[1]).split()
        percent = splited[len(splited)-2]
    return (percent)


def get_sync_verification(host="127.0.0.1", ssh=None):
        # Send the command (non-blocking)
    stdin, stdout, stderr = ssh.exec_command("date '+%Y-%m-%d %H:%M:%S %Z'")
    sntp = Pysntp(direccion="10.160.80.205")

    # Wait for the command to terminate
    values = []
    for i, line in enumerate(stdout):
        line = line.rstrip()
        line = line.rstrip('\n').rstrip('\r').strip()
        line = clear_multiple_spaces(line)
        values.append(line)
    local = datetime.datetime.strptime(values[0],'%Y-%m-%d %H:%M:%S %Z')
    sntp_time = sntp.get_time()
    if(sntp_time is None):
        click.secho("Fallo verificacion de sincronia con %s" % sntp._direccion, bg='white', fg='red', bold=True, reverse=True)
    sntp_time = sntp.get_time()
    if sntp_time is not None:
        dif = local - sntp_time
        sec = dif.total_seconds()
        if sec >= 5 or sec <= -5:
            return sec, local, sntp_time, ERROR + "NO" + ENDC
        else:
            return sec, local, sntp_time,  OK + "OK" + ENDC
    else:
        return -1, local, sntp_time, WARNING + "NO VERIFICADO" + ENDC




def get_ping_verification(host="127.0.0.1", ssh=None):
        # Send the command (non-blocking)
    stdin, stdout, stderr = ssh.exec_command("ping -c 3 10.160.80.205")

    output = stdout.read()
    list_output = re.split(',', output.decode().rstrip('\n').rstrip('\r').strip())
    recibidos = re.split(' ', list_output[1].strip())[0]

    if int(recibidos) <= 0:
        if1 = ERROR + "NO" + ENDC
    else:
        if1 = OK + "OK" + ENDC
    # LAN 2
    stdin, stdout, stderr = ssh.exec_command("ping -c 3 10.161.80.205")

    output = stdout.read()
    list_output = re.split(',', output.decode().rstrip('\n').rstrip('\r').strip())
    recibidos = re.split(' ', list_output[1].strip())[0]

    if int(recibidos) <= 0:
        if2 = ERROR + bgLightgrey + "NO" + ENDC
    else:
        if2 = OK + "OK" + ENDC

    return if1, if2

def get_disk_health(host="127.0.0.1", ssh=None):

    if host in ['fdp1', 'fdp2', 'rdp1', 'rdp2', 'rdcu1', 'rdcu2', 'dls1', 'dls2', 'drf1', 'drf2']:
        stdinA, stdoutA, stderrA = ssh.exec_command("smartctl -H  -d cciss,0 /dev/cciss/c0d0")
        stdinB, stdoutB, stderrB = ssh.exec_command("smartctl -H  -d cciss,1 /dev/cciss/c0d0")
        outputA = stdoutA.read()
        outputB = stdoutB.read()

        resultadoA = re.split(':', outputA.decode().strip('\n').strip('\r'))[-1].strip()
        resultadoB = re.split(':', outputB.decode().strip('\n').strip('\r'))[-1].strip()

        if resultadoA == 'OK':
            resultadoA = OK + resultadoA + ENDC
        elif resultadoA == 'No such file or directory':
            resultadoA = WARNING + '---' + ENDC
        else:
            resultadoA = ERROR + resultadoA + ENDC

        if resultadoB == 'OK':
            resultadoB = OK + resultadoB + ENDC
        elif resultadoB == 'No such file or directory':
            resultadoB = WARNING + '---' + ENDC
        else:
            resultadoB = ERROR + resultadoB + ENDC
    else:
        stdinA, stdoutA, stderrA = ssh.exec_command("smartctl -H /dev/sda")
        stdinB, stdoutB, stderrB = ssh.exec_command("smartctl -H /dev/sdb")
        outputA = stdoutA.read()
        outputB = stdoutB.read()

        resultadoA = re.split(':', outputA.decode().strip('\n').strip('\r'))[-1].strip()
        resultadoB = re.split(':', outputB.decode().strip('\n').strip('\r'))[-1].strip()

        if resultadoA == 'PASSED':
            resultadoA = OK + resultadoA + ENDC
        elif resultadoA == 'No such file or directory':
            resultadoA = WARNING + '---' + ENDC
        else:
            resultadoA = ERROR + resultadoA + ENDC

        if resultadoB == 'PASSED':
            resultadoB = OK + resultadoB + ENDC
        elif resultadoB == 'No such file or directory':
            resultadoB = WARNING + '---' + ENDC
        else:
            resultadoB = ERROR + resultadoB + ENDC

    return resultadoA, OK+resultadoB+ENDC,
