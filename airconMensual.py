#!/usr/bin/python3
import sys
import click
import getpass
import os
import traceback
from tqdm import tqdm
from time import sleep
from prettytable import PrettyTable
import paramiko

from utils.functions import get_memory, get_uptime, get_cpu_usage, get_load_avg, get_disk_usage, get_sync_verification, \
    get_ping_verification, get_disk_health
from utils.helper_classes import Ping
unaviables = []
hosts = []


def leer_archivo(source_file):
    """Simple program that greets NAME for a total of COUNT times."""
    global _file
    if not os.path.isfile(source_file):
        click.secho('Archivo invalido'.center(80, '*'), fg='red', bold=True, reverse=True)
        exit()
    else:
        _file = open(source_file)

    lines = []
    for line in _file:
        lines.append(line)
    click.secho('Verificando conectividad de hosts'.center(80, '-'), fg='blue', bold=True)
    for line in tqdm(lines, leave=True):
        line = line.rstrip('\n').rstrip('\r').strip()  # Eliminar enter y espacios en blanco
        if len(line) > 0 and not line.startswith('#'):
            # verificar que este accesible
            #sleep(0.1)
            p = Ping(direccion=line)
            if p.send_pyng() == 0:
                hosts.append(line)
            else:
                unaviables.append(line)
    click.secho('Verificion finalizada'.center(80, '-'), fg='blue', bold=True)
    sleep(1)
    if len(unaviables) > 0:
        click.secho('Se encontraron sin conexion los siguientes hosts'.center(80, '*'), fg='yellow', bold=True, reverse=True)
        t = PrettyTable(['Host', 'Estado'])
        for uh in unaviables:
            t.add_row([uh, 'Sin conexion'])
        print(t)
        if click.confirm(click.style('Deseas continuar?', fg='green', reverse=True), default=True):
            ejecutar_mantenimiento()
        else:
            click.secho('Mantenimiento cancelado '.center(80, '*'), fg='red', bold=True, reverse=True)
            exit()
    else:
        ejecutar_mantenimiento()


def ejecutar_mantenimiento():
    resultados = ['Mem Total', 'Mem free', 'Swap free', 'Uptime', '%CPU', 'Procesos']
    resultados += ['Uso /', 'sda', 'sdb', 'Sinc.', 'LAN1', 'LAN2', 'Offset', 'Carga CPU']

    click.clear()
    click.secho('INICIANDO MANTENIMIENTO MENSUAL AIRCON 2100'.center(80, '_'), fg='white', bold=True, reverse=True)
    if hosts.__len__() > 0:
        for host in hosts:
            click.secho(host.center(80, '='), fg='white', bold=True, reverse=True)
            tabla = PrettyTable(resultados)
            intentos = 0
            while True:
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    # ssh.connect(host)
                    ssh.connect(host, username="root", password="root")
                    ram, ram_free, swap = get_memory(host, ssh=ssh)
                    mylist = [ ram, ram_free, swap]
                    mylist.append(get_uptime(host=host, ssh=ssh))
                    mylist.append(get_cpu_usage(host=host, ssh=ssh))
                    lavg, procs = get_load_avg(host=host, ssh=ssh)
                    #mylist.append(lavg)
                    mylist.append(procs)
                    mylist.append(get_disk_usage(host=host, ssh=ssh))
                    discoA, discoB = get_disk_health(host=host, ssh=ssh)
                    mylist.append(discoA)
                    mylist.append(discoB)
                    offset, local, server, status = get_sync_verification(host=host, ssh=ssh)
                    mylist.append(status)
                    if1, if2 = get_ping_verification(host=host, ssh=ssh)
                    mylist.append(if1)
                    mylist.append(if2)
                    mylist.append(str(offset) + " seg")
                    mylist.append(lavg)
                    ssh.close()
                    tabla.add_row(mylist)
                    print(tabla)
                    input('Presiona ENTER para continuar')
                    break
                except paramiko.AuthenticationException:
                    click.secho("Fallo de auntenticacion con:  %s" % host, bg='red', fg='white', bold=True,
                                reverse=True)
                    break
                except:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    click.secho(" %s > %s ===> reintentando." % (host, exc_value), bg='yellow', fg='black', bold=True, reverse=False)
                    #traceback.print_exc(file=sys.stdout)
                    print('-' * 60)
                    intentos += 1
                    sleep(2)

                # If we could not connect within time limit
                if intentos == 4:
                    click.secho("No se pudo conectar a %s.!" % host, bg='white', fg='red', bold=True, reverse=False)
                    break
            click.clear()

        click.secho('MANTENIMIENTO FINALIZADO'.center(80, '_'), bg='green', fg='white', bold=True,
                    reverse=False)
        input('Presiona ENTER para continuar')
    else:
        click.secho('No hay ningun host disponible en la lista, verifica la conexion'.center(80, '_'), fg='yellow', bold=True, reverse=True)

@click.command()
@click.option('--tipo', type=click.Choice(['ope', 'sim']), default="ope",
              help="Indica el modo de ejecucion", prompt="Modo de ejecucion")
def mantenimiento(tipo):
    click.clear()
    if tipo == 'ope':
        click.echo(click.style('=> Seleccionado modo OPERACIONAL', fg='green', bold=True, reverse=True))
        leer_archivo('./operational')
    else:
        click.secho('=> Seleccionado modo SIMULACION', fg='yellow', bold=True, reverse=True)
        leer_archivo('./simulation')


if __name__ == "__main__":
    click.clear()
    # Verificar que se ejecute como root
    if getpass.getuser() != "root":
        cmd = os.path.basename(__file__)
        click.secho("Debes ejecutar el comando " + cmd + " como usuario root!", fg='red', bold=True, reverse=True)
        exit()
    click.secho('*' * 50)
    mantenimiento()
