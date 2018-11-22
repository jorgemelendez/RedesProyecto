from CSVTopologia import *
from ArmarMensajes import *
import threading
import threading
import socket
import os
import sys

#Clase de Nodo que funciona para distribuir los vencinos de nodos
class ServerVecinos:

	#Contructor que lee el archivo CSV de vecinos completo
	# y lo guarda en un diccionario
	#ip, ip que va a tener el servidor
	#puerto: puerto que va a tener el servidor
	#archivo: archivo csv desde donde se van a leer los vecinos
	def __init__(self, ip, puerto, archivo):
		lectorTopologia = CSVTopologia(archivo)
		self.lockDicVecinos = threading.Lock()
		self.dicVecinos = lectorTopologia.getDiccionario()
		self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		try:
			self.serverSocket.bind((ip, puerto))
		except:
			print ("Error, no se puede crear el Servidor de Vecinos en esa ip con ese puerto")
			self.serverSocket.close()
			os._exit(1)

	#Funcion para obtener el mensaje que hay que enviar a un nodo
	# que solicito sus vecinos
	#llave: tupla que indica cual nodo es el que esta solicitando
	# tupla es (ip, mascara,puerto)
	def obtenerMensajeDeVecinos(self, llave):
		self.lockDicVecinos.acquire()
		vecinos = self.dicVecinos.get(llave)
		mensajeVecinos = bytearray()
		if vecinos is not None:
			mensajeVecinos = self.construirMensaje(vecinos)
		else:
			print("No tiene vecinos ", llave)
		self.lockDicVecinos.release()
		return mensajeVecinos

	#Funcion que construye el mensaje de bytes dado una lista de vecinos
	#listaDeVecinos: lista de los vecinos que tiene el nodo
	# cada elemento de la lista es una tupla (ip, mascara, puerto, distancia)
	def construirMensaje(self, listaDeVecinos):
		mensaje = bytearray()
		for x in listaDeVecinos:
			mensaje += ipToBytes(x[0])#mete la ip como 4 bytes
			mensaje += intToBytes(x[1],1)#mete la mascara como 1 byte
			mensaje += intToBytes(x[2],2)#mete la puerto como 2 bytes
			mensaje += intToBytes(x[3],3)#mete la distancia como 3 bytes
		return mensaje

	#Ciclo del servidor para recibir mensajes y responder a los nodos 
	# que soliciten mensajes
	def recibeMensajes(self):
		while 1:
			message, clientAddress = self.serverSocket.recvfrom(2048)
			#En el mensaje debe de venir la mascara, esto para hacer la busqueda
			#La IP y el Puerto se toman de clientAddress
			if len(message) == 1:
				mascara = bytesToInt( message[0:1] )
				if mascara > 1 and mascara < 31 :
					respuesta = self.obtenerMensajeDeVecinos( (clientAddress[0], mascara, clientAddress[1]) )
					self.serverSocket.sendto(respuesta, clientAddress)
				else:
					print("Llego solicitud de vencinos con una mascara invalida")

	#Menu del Servidor de vecinos
	def iniciar(self):
		#Crea hilo para escuchar mensajes y responder a ellos
		hiloServidor = threading.Thread(target=self.recibeMensajes, args=())
		hiloServidor.start()
		#Menu del servidor de vecinos
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

#Metodo de inicio del programa para el Server de vecinos
#Hay que poner la direccion del archivo CSV como parametro y aumentar la condicion del if y enviar el parametro
if __name__ == '__main__':
	if len(sys.argv) == 4:#3:
		servidor = ServerVecinos(sys.argv[1], int(sys.argv[2]), sys.argv[3])#"/home/christofer/Escritorio/RedesProyecto/CSVServidor")
		servidor.iniciar()
	else: 
		print("Faltan parametros")