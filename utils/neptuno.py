import re
from datetime import timedelta, datetime

import click

from utils.helper_classes import Pysntp


class NeptunoHelper(object):
    ENDC = '\033[0m'
    BOLD = '\033[01m'
    # Foreground
    fgGreen = '\033[32m'
    fgLightred = '\033[31m'
    fgYellow = '\033[93m'
    bgLightgrey = '\033[49m'

    OK = fgGreen + BOLD
    WARNING = fgYellow + BOLD
    ERROR = fgLightred + BOLD

    def __init__(self, host="127.0.0.1", ssh=None):
        self.host = host
        self.ssh = ssh

    def limpiar_espacios(self, text):
        return ' '.join(text.split())

    def get_memoria(self):

        # Send the command (non-blocking)
        stdin, stdout, stderr = self.ssh.exec_command("free -m")

        # Wait for the command to terminate
        values = []
        for i, line in enumerate(stdout):
            if i <= 3:
                line = line.rstrip()
                line = line.rstrip('\n').rstrip('\r').strip()
                line = self.limpiar_espacios(line)
                values.append(line)
        ram_total = str(values[1]).split()[1]
        swap = str(values[3]).split()
        free_ram_percent = (float(str(values[2]).split()[3]) / float(ram_total)) * 100
        uso_swap = (float(swap[3]) / float(swap[1])) * 100
        return ram_total, "{0:.1f}".format(free_ram_percent) + "%", "{0:.1f}".format(uso_swap) + "%"

    def get_procesos_carga_cpu(self):
        # Send the command (non-blocking)
        stdin, stdout, stderr = self.ssh.exec_command("cat /proc/loadavg")

        # Wait for the command to terminate
        values = []
        for i, line in enumerate(stdout):
            line = line.rstrip()
            line = line.rstrip('\n').rstrip('\r').strip()
            line = self.limpiar_espacios(line)
            values.append(line)
        splited = str(values[0]).split()
        return splited[2], splited[3]

    def get_uso_cpu(self):

        # Send the command (non-blocking)
        stdin, stdout, stderr = self.ssh.exec_command("vmstat")

        # Wait for the command to terminate
        values = []
        for i, line in enumerate(stdout):
            line = line.rstrip()
            line = line.rstrip('\n').rstrip('\r').strip()
            line = self.limpiar_espacios(line)
            values.append(line)

        splited = str(values[2]).split()
        usage = 100 - float(splited[len(splited) - 2])
        return "{0:.1f}".format(usage) + "%"

    def get_uso_disco(self):
        # Send the command (non-blocking)
        stdin, stdout, stderr = self.ssh.exec_command("df -h /")
        raiz = stdout.read().decode()
        raiz = re.split(' ', raiz.strip('\n').strip('\r'))[-2]

        stdin, stdout, stderr = self.ssh.exec_command("df -h /home")
        home = stdout.read().decode()
        home = re.split(' ', home.strip('\n').strip('\r'))[-2]

        stdin, stdout, stderr = self.ssh.exec_command("df -h /home/rec")
        rec = stdout.read().decode()
        rec = re.split(' ', rec.strip('\n').strip('\r'))[-2]

        stdin, stdout, stderr = self.ssh.exec_command("df -h /var")
        var = stdout.read().decode()
        var = re.split(' ', var.strip('\n').strip('\r'))[-2]

        return raiz, home, rec, var

    def get_estado_raid(self):
        stdin, stdout, stderr = self.ssh.exec_command("cat /proc/mdstat")
        md = stdout.read().decode()
        md = re.split('\n', md.strip('\n').strip('\r'))
        md0, md1, md2, md3 = '---', '---', '---', '---'
        if len(md) >=15:
            md3 = re.split(' ', md[3].strip('\r').strip())[-1]
            md2 = re.split(' ', md[6].strip('\r').strip())[-1]
            md1 = re.split(' ', md[9].strip('\r').strip())[-1]
            md0 = re.split(' ', md[12].strip('\r').strip())[-1]
            if md0 == '[UU]':
                md0 = 'OK'
            else:
                md0 = 'F'

            if md1 == '[UU]':
                md1 = 'OK'
            else:
                md1 = 'F'

            if md2 == '[UU]':
                md2 = 'OK'
            else:
                md2 = 'F'

            if md3 == '[UU]':
                md3 = 'OK'
            else:
                md3 = 'F'

        return md0, md1, md2, md3

    def get_salud_disco(self):
        stdinA, stdoutA, stderrA = self.ssh.exec_command("sudo smartctl -H /dev/hdc")
        stdinB, stdoutB, stderrB = self.ssh.exec_command("sudo smartctl -H /dev/hdd")

        outputA = stdoutA.read().decode()
        outputB = stdoutB.read().decode()

        resultadoA = re.split(':', outputA.strip('\n').strip('\r'))[-1].strip()
        resultadoB = re.split(':', outputB.strip('\n').strip('\r'))[-1].strip()

        if resultadoA == 'PASSED':
            resultadoA = self.OK + resultadoA + self.ENDC
        elif resultadoA == 'No such file or directory':
            resultadoA = self.WARNING + '---' + self.ENDC
        else:
            resultadoA = self.ERROR + resultadoA + self.ENDC

        if resultadoB == 'PASSED':
            resultadoB = self.OK + resultadoB + self.ENDC
        elif resultadoB == 'No such file or directory':
            resultadoB = self.WARNING + '---' + self.ENDC
        else:
            resultadoB = self.ERROR + '****' + self.ENDC


        # **********************************************
        stdinA, stdoutA, stderrA = self.ssh.exec_command("sudo smartctl -A /dev/hdc")
        stdinB, stdoutB, stderrB = self.ssh.exec_command("sudo smartctl -A /dev/hdd")

        outputA = stdoutA.read().decode()
        outputB = stdoutB.read().decode()

        realocations_valueA = re.split('Reallocated_Sector_Ct', outputA)[1].split('\n')[0].strip().split()[1]
        realocations_rawA = re.split('Reallocated_Sector_Ct', outputA)[1].split('\n')[0].strip().split()[-1]

        spins_valueA = re.split('Spin_Retry_Count', outputA)[1].split('\n')[0].strip().split()[1]
        seeks_valueA = re.split('Seek_Error_Rate', outputA)[1].split('\n')[0].strip().split()[1]
        reads_valueA = re.split('Raw_Read_Error_Rate', outputA)[1].split('\n')[0].strip().split()[1]

        realocations_valueB, realocations_rawB, spins_valueB, seeks_valueB, reads_valueB = '--', '--', '--', '--', '--'

        if self.host not in ['10.160.80.192']:
            realocations_valueB = re.split('Reallocated_Sector_Ct', outputB)[1].split('\n')[0].strip().split()[1]
            realocations_rawB = re.split('Reallocated_Sector_Ct', outputB)[1].split('\n')[0].strip().split()[-1]

            spins_valueB = re.split('Spin_Retry_Count', outputB)[1].split('\n')[0].strip().split()[1]
            seeks_valueB = re.split('Seek_Error_Rate', outputB)[1].split('\n')[0].strip().split()[1]
            reads_valueB = re.split('Raw_Read_Error_Rate', outputB)[1].split('\n')[0].strip().split()[1]

        return resultadoA, resultadoB, realocations_valueA, realocations_rawA, spins_valueA, seeks_valueA, reads_valueA, realocations_valueB,\
               realocations_rawB, spins_valueB, seeks_valueB, reads_valueB

    def get_uptime(self):

        # Send the command (non-blocking)
        stdin, stdout, stderr = self.ssh.exec_command("cat /proc/uptime")

        # Wait for the command to terminate
        values = []
        for i, line in enumerate(stdout):
            line = line.rstrip()
            line = line.rstrip('\n').rstrip('\r').strip()
            line = self.limpiar_espacios(line)
            values.append(line)
        uptime_seconds = float(str(values[0]).split()[0])
        uptime_string = str(timedelta(seconds=uptime_seconds))
        return uptime_string.split('.')[0]

    def get_sincronia(self):
        # Send the command (non-blocking)
        stdin, stdout, stderr = self.ssh.exec_command("date '+%Y-%m-%d %H:%M:%S %Z'")
        sntp = Pysntp(direccion="10.160.80.205")

        # Wait for the command to terminate
        values = []
        for i, line in enumerate(stdout):
            line = line.rstrip()
            line = line.rstrip('\n').rstrip('\r').strip()
            line = self.limpiar_espacios(line)
            values.append(line)
        local = datetime.strptime(values[0], '%Y-%m-%d %H:%M:%S %Z')
        sntp_time = sntp.get_time()
        if sntp_time is None:
            click.secho("Fallo verificacion de sincronia con %s" % sntp._direccion, bg='white', fg='red', bold=True,
                        reverse=True)
        sntp_time = sntp.get_time()
        if sntp_time is not None:
            dif = local - sntp_time
            sec = dif.total_seconds()
            if sec >= 5 or sec <= -5:
                return self.ERROR + str(sec) + " seg." + self.ENDC
            else:
                return self.OK + str(sec) + " seg." + self.ENDC
        else:
            return self.WARNING + "NO VERIFICADO" + self.ENDC


    def get_procesos_ininterrumpibles(self):
        stdin, stdout, stderr = self.ssh.exec_command('ps auxf | awk \'{printf"%s", $8}\' | grep D | wc -l')
        res = stdout.read().decode().strip('\ns')
        if res == '0':
            return 'OK'
        else:
            return res
