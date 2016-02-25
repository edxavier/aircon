#!/bin/bash

for i in $(seq 1 26)
do
	echo "10.160.80."$i
	#ssh-copy-id -i $HOME"/.ssh/id_rsa.pub" root@10.160.80.22

	#ssh "root@10.160.80."$i 'touch /root/pos; echo "POS$i" > /root/pos'

	#echo "Indique la Posicion correspondiente ";
	#ssh "root@10.160.80."$i 'read pos;echo $pos > /root/pos;'


done
