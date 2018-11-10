from CSVTopologia import *
from ArmarMensajes import *
import threading
import threading
import socket
import os

#Clase de Nodo que funciona para distribuir los vencinos de nodos
class ServerVecinos:

	#Contructor que leer el archivo CSV de vecinos completo
	# y lo guarda en un diccionario
	def __init__(self, ip, puerto, archivo):
		lectorTopologia = CSVTopologia(archivo)
		self.lockDicVecinos = threading.Lock()
		self.dicVecinos = lectorTopologia.getDiccionario()
		#Socket
		self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.serverSocket.bind((ip, puerto))

	#Funcion para obtener el mensaje que hay que enviar a un nodo
	# que solicito sus vecinos
	def obtenerMensajeDeVecinos(self, llave):
		self.lockDicVecinos.acquire()
		vecinos = self.dicVecinos.get(llave)
		mensajeVecinos = self.construirMensaje(vecinos)
		self.lockDicVecinos.release()
		return mensajeVecinos

	#Funcion que construye el mensaje de bytes
	# dado una lista de vecinos
	def construirMensaje(self, listaDeVecinos):
		mensaje = bytearray()
		for x in listaDeVecinos:
			mensaje += ipToBytes(x[0])#mete la ip como 4 bytes
			mensaje += intToBytes(x[1],1)#mete la mascara como 1 byte
			mensaje += intToBytes(x[2],2)#mete la puerto como 2 bytes
			mensaje += intToBytes(x[3],1)#mete la distancia como 1 bytes
		return mensaje

	#Ciclo del servidos para recibir mensajes y responder a los nodos 
	# que soliciten mensajes
	def recibeMensajes(self):
		while 1:
			message, clientAddress = self.serverSocket.recvfrom(2048)
			
			if len(message) == 1:
				mascara = intToBytes( message, 1 )
				if mascara > 1 and mascara < 31 :
					respuesta = self.obtenerMensajeDeVecinos( (clientAddress[0], mascara, clientAddress[1]) )
					self.serverSocket.sendto(respuesta, clientAddress)
				else:
					print("Llego solicitud de vencinos con una mascara invalida")

	def iniciar(self):
		hiloServidor = threading.Thread(target=self.recibeMensajes, args=())
		hiloServidor.start()

		bandera = True
		while bandera == True:
			print('Menu principal del modulo de Red UDP: \n'
					'\t1. Salir. \n')
			taskUsuario = input('Que desea hacer:')
			if taskUsuario == '1':
				bandera = False
				os._exit(1)
			else:
				print('Ingrese opcion valida.')


if __name__ == '__main__':
	servidor = ServerVecinos("10.1.137.114", 5000, "/home/christofer/Escritorio/RedesProyecto/CSVServidor")
	servidor.iniciar()