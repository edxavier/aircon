#!/usr/bin/python
__author__ = 'Eder Xavier Rojas'
# Creado  07-08-15
import os, stat
import getpass
import argparse
import csv
import shutil
import paramiko
from os.path import expanduser
from utils.helper_classes import *
from utils.functions import *

if __name__ == "__main__":
    try:
        t = TermColors()
        clear = lambda: os.system('clear')
        parser = argparse.ArgumentParser(description=t.fgLightblue+t.bgBlack+'Utilidad para realizar el mantenimiento mensual'
                                                 ' de las posiciones de sistema aircon 2100'+t.ENDC)

        parser.add_argument('-a', '--address', action='store', help='Direccion destino',)
        parser.add_argument('-f', '--file', action='store', help='Archivo con el listado de direcciones IP, una por linea')
        args = parser.parse_args()
        hosts = []
        addr = None
        #Verificar que se ejecute como root
        if getpass.getuser() != "root":
            cmd = t.BOLD+os.path.basename(__file__)+t.ENDC
            t.info("Debes ejecutar el comando "+cmd +" como usuario root ")
            exit()

        if args.file:
            if os.path.isfile(args.file):
                try:
                    with open(args.file) as file:
                        print t.center(text=" VERIFICANDO ACCESO DE LSITADO DE HOST ")
                        time.sleep(2)
                        for line in file:
                            line = line.rstrip('\n').rstrip('\r').strip() #eliminar enter y espacios en blanco
                            if len(line) > 0 and not line.startswith('#'):
                                #verificar que este accesible
                                p = Pyng(direccion=line)
                                if p.send_pyng() == 0:
                                    hosts.append(line)
                                else:
                                   t.print_row(line,t.fgYellow+"INACCESIBLE"+t.ENDC)
                except IOError as e:
                    print "Unable to open file" #Does not exist OR no read permissions
            else:
                t.warning("El archivo "+t.BOLD+args.file+t.ENDC+" no existe")
                while not addr:
                    addr = raw_input(t.fgLightblue + t.bgBlack + "Especifique una direccion IP destino:"+t.ENDC)
                    p = Pyng(direccion=addr)
                    if addr:
                        if p.send_pyng() == 0:
                            hosts.append(addr)
                        else:
                            t.print_row(addr,t.fgYellow+"INACCESIBLE"+t.ENDC)
                            addr=None
        else:
            if args.address:
                hosts.append(args.address)
            else:
                while not addr:
                    addr = raw_input(t.fgLightblue + t.bgBlack + "Especifique una direccion IP destino:"+t.ENDC)
                    p = Pyng(direccion=addr)
                    if addr:
                        if p.send_pyng() == 0:
                            hosts.append(addr)
                        else:
                            t.print_row(addr,t.fgYellow+"INACCESIBLE"+t.ENDC)
                            addr=None
        #dclear()
        if len(hosts) > 0:
            print t.center(text=" INICIANDO MANTENIMIENTO MENSUAL AIRCON 2100 ")
            time.sleep(2)
            mylist = ['Fecha', 'ID','Posicion', 'Memoria Total','RAM Libre', 'Swap Libre','Uptime','Uso de CPU','Carga de CPU']
            mylist += ['Procesos','Uso de Disco en /','Sincronizacion','Diferencia tiempo','Ping LAN1', 'Ping LAN2']
            date = datetime.datetime.now()
            file_name = "mantto_mensual_aricon_"+date.strftime("%d%m%Y")+".csv"
            file_path = "/tmp/"+file_name


            with open(file_path, 'wb') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                wr.writerow(mylist)
                for host in hosts:
                        i = 1
                        # Try to connect to the host.
                        # Retry a few times if it fails.
                        while True:
                            #print "Intentado conexion con  %s (%i/4 intentos)" % (host, i)
                            try:
                                ssh = paramiko.SSHClient()
                                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                                ssh.connect(host)
                              #  print "Connected to %s" % host
                                id = str(host).split('.')[3]
                                now = datetime.datetime.now()
                                fecha = now.strftime("%d-%m-%y %H:%M")
                                t.msg(title="OBTENIENDO DATOS DE "+host, message="")
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

                                break
                            except paramiko.AuthenticationException:
                                print "Authentication failed when connecting to %s" % host
                                break
                            except Exception, e:
                                print "Could not SSH to %s, waiting for it to start" % host
                                print(e.message)
                                i += 1
                                time.sleep(2)

                            # If we could not connect within time limit
                            if i == 4:
                                print "Could not connect to %s. Giving up" % host
                                break
            resp1 = None
            home = expanduser("~")
            print(home)
            print(file_name)
            #cambiar permisos para q todos puedan modificarlo
            os.chmod(file_path, stat.S_IRWXO)
            while not resp1 or resp1!='y' and resp1!='n':
                resp1 =raw_input("Desea enviar copia del resultado a bincer@eaai.com.ni? [y/n]:")
                if resp1 == 'y':
                    print("Enviando...")
                    mail = Pymail()
                    file = file_path
                    mail.send(file=file, dest='bincer@eaai.com.ni')
                else:
                    break

            resp = None

            #try:
             #   os.remove(home+"/"+file_name)
            #except:
             #   pass

            while not resp or resp!='y' and resp!='n':
                resp =raw_input("Desea enviar copia del  resultado a stecnica@eaai.com.ni? [y/n]:")
            if resp == 'y':
                print("Enviando...")
                mail = Pymail()
                file = file_path
                mail.send(file=file, dest='stecnica@eaai.com.ni')
                shutil.copy(file_path,home)
                t.info("Se ha guardado una copia en "+home+'/'+file_name)
            else:
                shutil.copy(file_path,home)
                t.info("Se ha guardado una copia en "+home+'/'+file_name)

            os.remove(file_path)


        else:
            t.warning("Terminado por falta de hosts validos")
    except KeyboardInterrupt:
        print("")
        t.error("EJECUCION INTERRUNPIDA")


