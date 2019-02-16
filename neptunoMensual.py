#!/usr/bin/python
import getpass
import os
import sys
import traceback
from time import sleep

import click
import paramiko
from prettytable import PrettyTable

from utils.neptuno import NeptunoHelper

if __name__ == "__main__":
    click.clear()
    # Verificar que se ejecute como root
    if getpass.getuser() != "root":
        cmd = os.path.basename(__file__)
        click.secho("Debes ejecutar el comando [ " + cmd + " ] como usuario root!", fg='red', bold=True, bg='white')
        exit()
    click.secho('*' * 50)
    resultados = ['Mem Total', 'Mem disp', 'Uso Swap', 'Procesos', 'Procs. Intmpbls.', 'Carga cpu',
                  'Uso cpu', '/', '/home', '/home/rec', '/var', 'md0', 'md1', 'md2', 'md3']

    resultados2 = ['Disco', 'SelfTest', 'ReallocateValue', 'ReallocateRaw', 'SpinRetryValue', 'SeekErrorVal',
                   'ReadErroVal', 'NTP', 'Uptime']

    click.clear()
    click.secho('INICIANDO MANTENIMIENTO MENSUAL NEPTUNO'.center(80, '-'), fg='white', bold=True, reverse=True)
    for host in ['10.160.80.190', '10.160.80.191', '10.160.80.192']:
        click.secho(host.center(80, '='), fg='white', bold=True, reverse=True)
        tabla = PrettyTable(resultados)
        tabla2 = PrettyTable(resultados2)

        intentos = 0
        while True:
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                # ssh.connect(host)
                ssh.connect(host, username="dmr", password="dmr")
                neptuno = NeptunoHelper(host, ssh)
                ram, ram_disponible, uso_swap = neptuno.get_memoria()
                carga, procesos = neptuno.get_procesos_carga_cpu()
                raiz, home, rec, var = neptuno.get_uso_disco()
                md0, md1, md2, md3 = neptuno.get_estado_raid()
                uptime = neptuno.get_uptime()
                sinc = neptuno.get_sincronia()
                procIninterrumpibles = neptuno.get_procesos_ininterrumpibles()

                hdc, hdd, realocations_valueA, realocations_rawA, spins_valueA, seeks_valueA, reads_valueA, realocations_valueB, \
                realocations_rawB, spins_valueB, seeks_valueB, reads_valueB = neptuno.get_salud_disco()

                fila = [ram, ram_disponible, uso_swap, procesos, procIninterrumpibles, carga, neptuno.get_uso_cpu(),
                        raiz, home, rec, var, md0, md1, md2, md3]
                fila2 = ['hdc', hdc, realocations_valueA, realocations_rawA, spins_valueA, seeks_valueA,
                         reads_valueA, sinc, uptime]
                fila3 = ['hdd', hdd, realocations_valueB, realocations_rawB, spins_valueB, seeks_valueB, reads_valueB,
                         '---', '---']
                tabla.add_row(fila)
                tabla2.add_row(fila2)
                tabla2.add_row(fila3)
                print(tabla)
                print(tabla2)

                input('Presiona ENTER para continuar')
                break
            except paramiko.AuthenticationException:
                click.secho("Fallo de auntenticacion con:  %s" % host, bg='red', fg='white', bold=True,
                            reverse=True)
                break
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                click.secho(" %s > %s ===> reintentando." % (host, exc_value), bg='yellow', fg='black', bold=True,
                            reverse=False)
                traceback.print_exc(file=sys.stdout)
                print('-' * 60)
                intentos += 1
                sleep(2)

            # If we could not connect within time limit
            if intentos == 4:
                click.secho("No se pudo conectar a %s.!" % host, bg='white', fg='red', bold=True, reverse=False)
                break
