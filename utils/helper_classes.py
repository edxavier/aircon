#!/usr/bin/python
import datetime
from email.mime.base import MIMEBase
import os
import smtplib
import mimetypes
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import Encoders
from email.utils import COMMASPACE, formatdate
from os.path import basename

__author__ = 'Eder Xavier Rojas'
# Creado  07-08-15
import subprocess
import socket, struct, sys, time

class TermColors(object):
    ENDC='\033[0m'
    BOLD='\033[01m'
    UnderLine='\033[04m'
    Strikethrough='\033[09m'
    #Foreground
    fgBlack='\033[30m'
    fgRed='\033[31m'
    fgGreen='\033[32m'
    fgOrange='\033[33m'
    fgBlue='\033[34m'
    fgPurple='\033[35m'
    fgCyan='\033[36m'
    fgLightgrey='\033[37m'
    fgDarkgrey='\033[90m'
    fgLightred='\033[91m'
    fgLightgreen='\033[92m'
    fgYellow='\033[93m'
    fgLightblue='\033[94m'
    fgPink='\033[95m'
    fgLightcyan='\033[96m'
    #background
    bgBlack='\033[40m'
    bgRed='\033[41m'
    bgGreen='\033[42m'
    bgOrange='\033[43m'
    bgBlue='\033[44m'
    bgPurple='\033[45m'
    bgCyan='\033[46m'
    bgLightgrey='\033[49m'

    INFO = fgLightcyan+BOLD+bgBlack
    WARNING = fgOrange+BOLD+bgBlack
    ERROR = fgLightred+BOLD+bgBlack


    def center(self,width=80, text="",fill="-"):
        return text.center(width,fill)

    # your code
    def print_row(self,msg, status):
        print "%-55s %-1s " % (msg, status)

    def msg(self, message="", title=""):
        line = self.center(text="",fill='-')
        title = self.center(text=title,fill=' ')
        #print(self.INFO+line+self.ENDC)
        print(self.INFO+title+self.ENDC)
        print(self.INFO+line+self.ENDC)
        print(message)

    def info(self, message=""):
        line = self.center(text="",fill='-')
        title = self.center(text="INFO",fill=' ')
        #print(self.INFO+line+self.ENDC)
        print(self.INFO+title+self.ENDC)
        print(self.INFO+line+self.ENDC)
        print(message+"\n")

    def warning(self, message):
        line = self.center(text="",fill='-')
        title = self.center(text="WARNING",fill=' ')
        #print(self.INFO+line+self.ENDC)
        print(self.WARNING+title+self.ENDC)
        print(self.WARNING+line+self.ENDC)
        print(message+"\n")

    def error(self, message):
        line = self.center(text="",fill='-')
        title = self.center(text="ERROR",fill=' ')
        #print(self.INFO+line+self.ENDC)
        print(self.ERROR+title+self.ENDC)
        print(self.ERROR+line+self.ENDC)
        print(message+"\n")



class Pyng(object):
    """Envio de mensajes icmp
        :param direccion: Especifique el IP o Hostname
    """
    def __init__(self, direccion="127.0.0.1"):
        self._direccion = direccion

    def send_pyng(self):
        """Envia un mensaje icmp
        :return: 0 Exito ; 1 Falla
        """
        ret = subprocess.call("ping -c 1 %s" % self._direccion,
                              shell=True,
                              stdout=open('/dev/null', 'w'),
                              stderr=subprocess.STDOUT)
        return ret


class Pysntp(object):

    def __init__(self, direccion="127.0.0.1"):
        self._direccion = direccion


    def get_time(self):
        TIME1970 = 2208988800L
        # Thanks to F.Lundh
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.settimeout(2)
        data = '\x1b' + 47 * '\0'
        client.sendto(data, (self._direccion, 123))
        #client.sendto(data, ('10.160.80.205', 123))

        try:
            data, address = client.recvfrom(1024)
            if data:
                t = struct.unpack('!12I', data)[10]
                t -= TIME1970
                utc_dt = datetime.datetime.utcfromtimestamp(t)
                return utc_dt
            else:
                return None
        except socket.timeout, e:
            return None            


class Pymail(object):
    def send(self,file='', dest='stecnica@eaai.com.ni'):
        sender = 'edxavier05@gmail.com'
        receivers = [dest]

        try:
            cli = smtplib.SMTP('smtp.gmail.com', 587)
            cli.ehlo()
            cli.starttls()
            cli.login("edxavier05@gmail.com", "konnichiwa")
            msg = MIMEMultipart()
            msg['From'] = "Sala Tecnica"
            msg['Subject'] = "Email Autogenerado - Mantto. Aircon"
            msg.attach(MIMEText("Se adjunta un archivo con el resultado de las comprobaciones "
                                "del Mantenimiento Mensual Aircon \n para mejor visualizacion de los datos"
                                " abrir el archivo con Excel"))

            ctype, encoding = mimetypes.guess_type(file)
            if ctype is None or encoding is not None:
                ctype = "application/octet-stream"

            maintype, subtype = ctype.split("/", 1)

            if maintype == "text":
                fp = open(file)
                # Note: we should handle calculating the charset
                attachment = MIMEText(fp.read(), _subtype=subtype)
                fp.close()
            attachment.add_header("Content-Disposition", "attachment", filename=basename(file))
            msg.attach(attachment)


            cli.sendmail(sender,receivers,msg.as_string())

        except (socket.gaierror, socket.error, socket.herror, smtplib.SMTPException), e:
            print e

print os.path.dirname(os.path.realpath(__file__))