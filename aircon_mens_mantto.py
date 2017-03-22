#!/usr/bin/python
import os, stat
from os.path import expanduser
import click, traceback
import csv
import paramiko
import shutil
from datetime import datetime as dtime
import getpass
from tqdm import tqdm
from time import sleep
from utils.helper_classes import *
from utils.functions import *

from utils.helper_classes import Pyng, TermColors

__author__ = 'Eder Xavier Rojas'

all_colors = 'black', 'red', 'green', 'yellow', 'blue', 'magenta', \
             'cyan', 'white'
unaviables = []
hosts = []

def validate_file(ctx, param, value):
    if not os.path.isfile(value):
        value = click.prompt('Please enter a valid source file', type=click.File())
    else:
        value = open(value)
    return value


@click.command()
@click.option('--source-file', default='/home/server/operational', help="Archivo origen", prompt=True,
              callback=validate_file)
def from_file(source_file):
    """Simple program that greets NAME for a total of COUNT times."""
    lines = []
    for line in source_file:
        lines.append(line)
    click.secho('Verificando listado de hosts'.center(80, '-'), fg='blue', bold=True)
    for line in tqdm(lines, leave=True):
        line = line.rstrip('\n').rstrip('\r').strip()  # Eliminar enter y espacios en blanco
        if len(line) > 0 and not line.startswith('#'):
            # verificar que este accesible
            p = Pyng(direccion=line)
            if p.send_pyng() == 0:
                hosts.append(line)
            else:
                unaviables.append(line)
    click.clear()
    if len(unaviables) > 0:
        click.secho('Se encontraron ineccesibles los siguientes'.center(80, '*'), fg='yellow', bold=True, reverse=True)
        for uh in unaviables:
            sleep(0.4)
            print "%-55s %-1s " % (uh, click.style('INACCESIBLE',fg='yellow', bold=True))
    exec_mantto()


@click.command()
@click.option('-s', '--subnet', default='10.160.80', help="Red destino", prompt=True)
@click.option('-i', '--init', default=1, prompt=True, type=click.IntRange(1, 254))
@click.option('-l', '--last', default=26, prompt=True, type=click.IntRange(1, 254))
def use_range(subnet, init, last):
    if init > last:
        last = click.prompt('Especifique un numero en el rango de %s a 254' % str(init), type=click.IntRange(init, 254))
    click.secho('Verificando rango de hosts'.center(80, '-'), fg='blue', bold=True)
    for i in range(init, last + 1):
        # verificar que este accesible
        target = str(subnet) + '.' + str(i)
        p = Pyng(direccion=target)
        if p.send_pyng() == 0:
            hosts.append(target)
        else:
            unaviables.append(target)
            print "%-55s %-1s " % (target, click.style('INACCESIBLE', fg='yellow', bold=True))

    exec_mantto()



@click.command()
@click.option('--exec-type', type=click.Choice(['range-mode', 'file-mode']), default="file-mode",
              help="Indica el modo de ejecucion", prompt="Modo de ejecucion")
def mantto(exec_type):
    """Comando para ejecutar mantenimiento mensual del sistema Aircon 2100."""
    if (exec_type == "file-mode"):
        click.clear()
        click.echo(click.style('=> Seleccionado modo de ejecucion desde archivo', fg='magenta', bold=True, reverse=True))
        click.echo(click.style('Especifique el archivo con el listado de hosts', fg='blue', bold=True, reverse=True))
        from_file()
    else:
        click.echo(click.style('=> Seleccionado modo de ejecucion por rango', fg='magenta', bold=True, reverse=True))
        click.echo(click.style('Especifique el rango de hosts', fg='blue', bold=True, reverse=True))
        use_range()

    for color in all_colors:
        click.echo(click.style('I am colored %s and bold' % color,
                               fg=color, bold=True))
    for color in all_colors:
        click.echo(click.style('I am reverse colored %s' % color, fg=color,
                               reverse=True))


def exec_mantto():
    t = TermColors()
    if len(hosts) < 1:
        print t.bgLightgrey + t.bgRed + "Ningun host accesible para el mantenimiento...".center(80, '*') + t.ENDC
        exit()
    click.secho('Verificion finalizada'.center(80, '-'), fg='blue', bold=True)
    raw_input(t.fgLightcyan + t.bgBlack + "Presione cualquier tecla para continuar..." + t.ENDC)
    click.clear()
    click.secho('INICIANDO MANTENIMIENTO MENSUAL AIRCON 2100'.center(80, ' '), fg='cyan', bold=True)

    mylist = ['Fecha', 'ID','Posicion', 'Memoria Total','RAM Libre', 'Swap Libre','Uptime','Uso de CPU','Carga de CPU']
    mylist += ['Procesos','Uso de Disco en /','Sincronizacion','Diferencia tiempo','Ping LAN1', 'Ping LAN2']
    date = dtime.now()
    if click.confirm(click.style('Mantenimiento SIMULACION?',bg='black', fg='green', reverse=True)):
        sector = "_SIM_"
    else:
        click.echo(click.style('Proceder como Mantenimiento OPERACIONAL',bg='black', fg='green', reverse=True))
        sector = "_OPE_"        
    file_name = "mantto_mensual_aricon"+ sector + date.strftime("%d%m%Y") + ".csv"
    temp_file_path = "/tmp/" + file_name
    succes_rate = 0
    with open(temp_file_path, 'wb') as result_file:
        wr = csv.writer(result_file, quoting=csv.QUOTE_ALL)
        wr.writerow(mylist)
        for host in hosts:
            it = 0
            while True:
                #print "Intentado conexion con  %s (%i/4 intentos)" % (host, i)
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    #ssh.connect(host)
                    ssh.connect(host, username="root", password="root")
                    #  print "Connected to %s" % host
                    id = str(host).split('.')[3]
                    now = dtime.now()
                    fecha = now.strftime("%d-%m-%y %H:%M")
                    t.msg(title="OBTENIENDO DATOS DE "+ host, message="")
                    ram, ram_free, swap = get_memory(host, ssh=ssh)
                    pos = get_position(host=host,ssh=ssh)
                    mylist = [fecha,id,pos,ram,ram_free, swap]
                    mylist.append(get_uptime(host=host,ssh=ssh))
                    mylist.append(get_cpu_usage(host=host,ssh=ssh))
                    lavg, procs = get_load_avg(host=host,ssh=ssh)
                    mylist.append(lavg)
                    mylist.append(procs)
                    mylist.append(get_disk_usage(host=host,ssh=ssh))
                    offset, local, server, status = get_sync_verification(host=host,ssh=ssh)
                    mylist.append(status)
                    mylist.append(str(offset)+" seg")
                    if1, if2 = get_ping_verification(host=host,ssh=ssh)
                    mylist.append(if1)
                    mylist.append(if2)
                    wr.writerow(mylist)
                    ssh.close()
                    succes_rate += 1
                    break
                except paramiko.AuthenticationException:
                    click.secho("Authentication failed when connecting to %s" % host, bg='white', fg='red', bold=True, reverse=True)
                    print ""
                    break
                except Exception, e:
                    click.secho("Could not SSH to %s, waiting for it to start" % host, bg='yellow', fg='black', bold=True, reverse=True)
                    #traceback.print_exc(file=sys.stdout)
                    print '-'*60   
                    print ""
                    it += 1
                    time.sleep(2)

                # If we could not connect within time limit
                if it == 4:
                    click.secho("Could not connect to %s. Giving up!" % host, bg='white', fg='red', bold=True, reverse=True)
                    break
    #if succes_rate > 0:
    home = expanduser("~")
    #cambiar permisos para q todos puedan modificarlo
    os.chmod(temp_file_path, stat.S_IRWXO)

    if click.confirm(click.style('Desea enviar copia del resultado a bincer@eaai.com.ni?', fg='green', reverse=True)):
        click.echo(click.style('=> Enviando...', fg='blue', bold=True, reverse=True))
        mail = Pymail()
        file = temp_file_path
        mail.send(file=file, dest='bincer@eaai.com.ni')


    if click.confirm(click.style('Desea enviar copia del resultado a stecnica@eaai.com.ni?', fg='green', reverse=True)):
        mail = Pymail()
        click.echo(click.style('=> Enviando...', fg='blue', bold=True, reverse=True))
        file = temp_file_path
        mail.send(file=file, dest='stecnica@eaai.com.ni')

    if click.confirm(click.style('Desea guardar una copia local?', fg='green', reverse=True)):
        click.echo(click.style('=> Copia guardada en %s ' % home, fg='blue', bold=True, reverse=True))
        shutil.copy(temp_file_path, home)

    os.remove(temp_file_path)
    click.clear()
    click.echo(click.style('MANTENIMIENTO FINALIZADO'.center(80, '*'), fg='green', bold=True, reverse=True))
    click.echo(click.style('las pruebas de ping se realizan con 10.161.80.205 (Servidor NTP)'.center(80, '*'), fg='green', bold=True, reverse=True))
    raw_input(t.fgLightcyan + t.bgBlack + "Presione cualquier tecla para continuar..." + t.ENDC)
    click.clear()


if __name__ == "__main__":
    click.clear()
#Verificar que se ejecute como root
    if getpass.getuser() != "root":
        cmd = os.path.basename(__file__)
        click.secho("Debes ejecutar el comando " + cmd + " como usuario root!", fg='red', bold=True, reverse=True)
        exit()
    #print "%-55s %-1s " % ("ddddddeeeee", click.style('WARNING',fg='yellow', bold=True))
    mantto()
