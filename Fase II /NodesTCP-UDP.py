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
def comando(comandosolicitado):
	ip = ""
	puerto = ""
	if comandosolicitado.find("salir") == 0 :
		sys.exit()
	if comandosolicitado.find("creaNodo-") == 0 :
		if comandosolicitado.find("pseudoBGP") == 9:
			finalIp = comandosolicitado[19:].find(" ")
			finalIp = finalIp + 1 + 19
			ip =  comandosolicitado[19:finalIp]
			inicioPuerto = finalIp
			puerto = comandosolicitado[inicioPuerto:]

			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			try:
				s.bind((ip,int(puerto)))
			except:
				print ("Error, ip o puerto incorrectos")
				return -1
			else:
				s.close()
				nodoTCP = NodoTCP()
				nodoTCP.iniciarNodoTCP(ip,int(puerto))
				return 1
		else:
			if comandosolicitado.find("intAS") == 9:
				finalIp = comandosolicitado[15:].find(" ")
				finalIp = finalIp + 1 + 15
				ip =  comandosolicitado[15:finalIp]
				inicioPuerto = finalIp
				puerto = comandosolicitado[inicioPuerto:]

				s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				try:
					s.bind((ip,int(puerto)))
				except:
					print ("Error, no se puede hacer crear el nodo en esa ip con es puerto")
					return -1
				else:
					s.close()
					nodoUDP = NodoUDP()
					nodoUDP.iniciarNodoUDP(ip,int(puerto))
					#udp.despligueMenuUDP()
					return 1
			else:
				print("Parametros no valido")
				return -1
	else:
		print("Parametros no valido")
		return -1

if __name__ == '__main__':
	if len(sys.argv) == 4:
		comando(sys.argv[1] + " " + sys.argv[2] + " " + sys.argv[3])
	else: 
		print("Faltan parametros")