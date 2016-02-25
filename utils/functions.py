#!/usr/bin/python
import select

__author__ = 'Eder Xavier Rojas'
# Creado  07-09-15
from datetime import timedelta
import datetime
from helper_classes import Pysntp

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

    splited = str(values[2]).split()
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
    dif = local - sntp_time
    sec = dif.total_seconds()
    if sec >=30 or sec <=-30:
        return sec, local, sntp_time, "NO"
    else:
        return sec, local, sntp_time, "OK"

def get_ping_verification(host="127.0.0.1", ssh=None):
        # Send the command (non-blocking)
    stdin, stdout, stderr = ssh.exec_command("ping -c 3 10.160.80.205")

    # Wait for the command to terminate
    values = []
    while not stdout.channel.exit_status_ready():
    # Only print data if there is data to read in the channel
        if stdout.channel.recv_ready():
            rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
            if len(rl) > 0:
                # Print data from stdout
                line = stdout.channel.recv(1024)
                line = line.rstrip()
                line = line.rstrip('\n').rstrip('\r').strip()
                line = clear_multiple_spaces(line)
                values.append(line)
    vals = str(values[len(values)-1]).split(',')
    vals = clear_multiple_spaces(vals[1]).split()
    if int(vals[0]) <= 0:
        if1 = "NO"
    else:
        if1 = "OK"

    stdin, stdout, stderr = ssh.exec_command("ping -c 3 10.161.80.205")

    # Wait for the command to terminate
    values = []
    while not stdout.channel.exit_status_ready():
    # Only print data if there is data to read in the channel
        if stdout.channel.recv_ready():
            rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
            if len(rl) > 0:
                # Print data from stdout
                line = stdout.channel.recv(1024)
                line = line.rstrip()
                line = line.rstrip('\n').rstrip('\r').strip()
                line = clear_multiple_spaces(line)
                values.append(line)
    vals = str(values[len(values)-1]).split(',')
    vals = clear_multiple_spaces(vals[1]).split()
    if int(vals[0]) <= 0:
        if2 = "NO"
    else:
        if2 = "OK"

    return if1, if2