import sys
import threading
import socket
import errno
import codecs
import os
import ipaddress

from socket import error as SocketError
from MensajesRecibidos import *
from TablaAlcanzabilidad import *
from LeerArchivo import *


#contenido  = archivoToString("/home/christofer/Escritorio/RedesProyecto/ArchivoPrueba.txt")
#segmentado = segmentarArchivo(contenido, 3)

"""i = 0
largo = len(segmentado)
while i < largo:
	print(segmentado[i])
	print (len(segmentado[i]))
	i = i + 1"""

def enviarArchivo():
	direccion = input('Digite la direccion del archivo: ')
	contenido = archivoToString(direccion)
	segmentado = segmentarArchivo(contenido, 3)#ESTE 3 ES EL NUMERO DE BYTES DE DATOS

	serverNameS = input('Digite la ip del destinatario: ')
	ipPrueba = serverNameS + "/32"
	try:
		n = ipaddress.ip_network(ipPrueba)
	except ValueError as e:
		print ("Ip no valida")
	else:
		lecturaPuerto = input('Digite el puerto del destinatario: ')
		try:
			serverPortS = int(lecturaPuerto)
		except ValueError as e:
			print ("Puerto no valido")
		else:
			if serverPortS < 0 or serverPortS > 65535:
				print ("Puerto no valido")
			else:
				i = 0
				largo = len(segmentado)
				while i < largo:
					message = segmentado[i]
					clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
					clientSocket.settimeout(0.5)##AAAAAAAAAVERIGUAR CUANTO DEBERIA DE SER
					llegoACK = False
					while llegoACK == False:
						clientSocket.sendto(message, (serverNameS, serverPortS))
						try:
							ACK, address = clientSocket.recvfrom(1024)
							llegoACK = True
							print(ACK)
							#rREVISAR SI ES UN ACK
						except socket.timeout:
							print("No llego ACK")
		
					if ACK == (1).to_bytes(1, byteorder='big'):
						i = i + 1
					clientSocket.close()




if __name__ == '__main__':
	enviarArchivo()