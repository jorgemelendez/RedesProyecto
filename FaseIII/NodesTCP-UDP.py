import sys
import threading
import socket
import errno
import codecs
import os
import ipaddress

from socket import error as SocketError
from NodoUDP import *
from NodoTCP import *

#Metodo que procesa los parametros enviados desde la consola
#tipoNodo: tipo de nodo que desea crear, en este caso solo se puede con UDP
#ip: direccion ip que va a tener el nodo
#mascaraString: mascara del nodo como una string
#puertoString: puerto del nodo como una string
def comando(tipoNodo, ip, mascaraString, puertoString):
	if tipoNodo == "creaNodo-intAS":
		mascara = int(mascaraString)
		puerto = int(puertoString)
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		try:
			s.bind((ip,puerto))
		except:
			print ("Error, no se puede hacer crear el nodo en esa ip con es puerto")
			return -1
		else:
			s.close()
			nodoUDP = NodoUDP(ip, mascara, puerto)
			nodoUDP.iniciarNodoUDP()
			return 1
	else:
		print("Parametros no valido")
		return -1

#Metodo que intenta dar inicio a la ejecucion del nodo con los parametros dados
if __name__ == '__main__':
	if len(sys.argv) == 5:
		comando(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
	else: 
		print("Faltan o sobran parametros")