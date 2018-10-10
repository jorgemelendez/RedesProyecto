import sys
import time
import socket
import threading

from ArmarMensajes import *
from LeerArchivo import *
from Buzon import *

class HiloConexionUDPSegura:

	def __init__(self, buzonReceptor, otraConexion, miConexion, socketConexion, lockSocket):
		self.buzonReceptor = buzonReceptor
		self.otraConexion = otraConexion
		self.miConexion = miConexion
		self.SN = 0
		self.RN = 0
		self.socketConexion = socketConexion
		self.lockSocket = lockSocket
		self.datosRecibidos = bytearray()
		self.etapaSyn = 0

		print("Cree hilo")		

		self.lockArchivos = threading.Lock()
		self.ArchivosAEnviar = list()#Archivos por enviar

		self.archivoActual = list()#Archivo actual que se esta enviando

		self.ackDatosFin = False

		self.ackHandshakeTerminado = False
		
		self.ultimoMensajeMandado = bytearray()

	def soyLaConexionHacia(self, ip, puerto):
		return self.otraConexion == (ip,puerto)

	def meterArchivoAEnviar(self, contenidoArchivo):
		segmentado = segmentarArchivo(contenidoArchivo, 5)
		self.lockArchivos.acquire()
		self.ArchivosAEnviar.append(segmentado)
		self.lockArchivos.release()


	def connect(self, ipServidor, puertoServidor):
		mensaje = armarPaq(self.miConexion[0], self.miConexion[1], self.otraConexion[0], self.otraConexion[1], 1, self.SN, self.RN, bytearray() ) #NO HAY QUE MANDAR DATOS PORQUE ES ESTABLECIENDO CONEXION
		self.lockSocket.acquire()
		self.socketConexion.sendto(mensaje, (ipServidor, puertoServidor))
		self.lockSocket.release()
		self.etapaSyn = 2
		

	#METER MENSAJE EN EL BUZON ANTES DE CREAR EL HILO
	def receptor(self):
		while True:

			
			



			recibido = self.buzonReceptor.sacarDatos(self.otraConexion)
			if recibido is None:
				time.sleep(1)#ANALIZAR LA CANTIDAD DE SEGUNDOS
			#if recibido is None:
				recibido = self.buzonReceptor.sacarDatos(self.otraConexion)
			if recibido is None:

				if self.etapaSyn == 3 and self.ackHandshakeTerminado == False:#Caso donde no llegan los primeros primeros datos y ya se envio el ack syn
					ACKConexion = armarPaq(self.miConexion[0], self.miConexion[1], self.otraConexion[0], self.otraConexion[1], 3, self.SN, self.RN, bytearray()) #NO HAY QUE MANDAR DATOS PORQUE ES ESTABLECIENDO CONEXION
					self.lockSocket.acquire()
					self.socketConexion.sendto(ACKConexion, self.otraConexion)
					self.lockSocket.release()
				if self.etapaSyn == 3 and self.ackHandshakeTerminado == True: #Caso donde no responde con paq nuevo
					ACKDatos = armarPaq(self.miConexion[0], self.miConexion[1], self.otraConexion[0], self.otraConexion[1], 10, self.SN, self.RN, self.ultimoMensajeMandado ) #VER SI TENGO DATOS PARA MANDAR
					self.lockSocket.acquire()
					self.socketConexion.sendto(ACKDatos, self.otraConexion)
					self.lockSocket.release()
				else:
					if self.etapaSyn == 2: #Caso donde no responden syn
						self.connect(self.otraConexion[0], self.otraConexion[1])
						#VER CUANTOS INTENTOS DE RENVIO DE INTENTO DE CONEXIONS
					else:
						if self.etapaSyn == 1:#Caso donde no responden respuesta a syn(no llega ack syn)
							ACKConexion = armarPaq(self.miConexion[0], self.miConexion[1], self.otraConexion[0], self.otraConexion[1], 1, self.SN, self.RN, bytearray()) #NO HAY QUE MANDAR DATOS PORQUE ES ESTABLECIENDO CONEXION
							self.lockSocket.acquire()
							self.socketConexion.sendto(ACKConexion, self.otraConexion)
							self.lockSocket.release()
				time.sleep(1)#ANALIZAR LA CANTIDAD DE SEGUNDOS
			else:
				otroIpRec = bytesToIp(recibido[0:4])
				otroPuertoRec = bytesToInt(recibido[4:6])
				miIpRec = bytesToIp(recibido[6:10])
				miPuertoRec = bytesToInt(recibido[10:12])
				tipoPaq = bytesToInt(recibido[12:13])
				SNpaq = bytesToInt(recibido[13:14])
				RNpaq = bytesToInt(recibido[14:15])
				datos = recibido[15:]



				print("Etapa: "+ str(self.etapaSyn) + " TipoPaq" + str(tipoPaq) + " RN: " + str(self.RN) + " SN: " + str(self.SN) + " RNpaq: " + str(RNpaq) + " SN: " + str(SNpaq)  )


				#Poner primero el caso de que esta sincronmizando

				if self.etapaSyn != 3:
					if self.etapaSyn == 0 and tipoPaq == 1:
						#Guardar el SNpaq y revisar cuando hay que aumentarlo
						self.RN = SNpaq + 1
						self.SN = 0
						self.connect(self.otraConexion[0], self.otraConexion[1])
						self.etapaSyn = 1
						print ("Entre en 1")
					elif self.etapaSyn == 2 and tipoPaq == 1:
						#Guardar el SNpaq y revisar cuando hay que aumentarlo
						self.RN = SNpaq + 1
						self.SN = RNpaq
						ACKConexion = armarPaq(self.miConexion[0], self.miConexion[1], self.otraConexion[0], self.otraConexion[1], 3, self.SN, self.RN, bytearray()) #NO HAY QUE MANDAR DATOS PORQUE ES ESTABLECIENDO CONEXION
						self.lockSocket.acquire()
						self.socketConexion.sendto(ACKConexion, self.otraConexion)
						self.lockSocket.release()
						self.etapaSyn = 3
						print ("Entre en 2")
						print ("Termine handshake como emisor")
						#break #QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQUUUUUUUUUUUUUUUUUUIIIIIIIIIIIIIIIIIIIITTTTTTTTTTTTTTTAAAAAAAAAAAAAAAAAAAAAARRRRRRRRRRRRRRRRRRRRR
					elif self.etapaSyn == 1 and tipoPaq == 3:
						self.etapaSyn = 3
						print ("Entre en 3")
						print("Termine handshake como receptor")
						#break #QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQUUUUUUUUUUUUUUUUUUIIIIIIIIIIIIIIIIIIIITTTTTTTTTTTTTTTAAAAAAAAAAAAAAAAAAAAAARRRRRRRRRRRRRRRRRRRRR
					else:
						print("Mensaje extranno")
						print(tipoPaq)
						print (self.etapaSyn)
				else:
					if tipoPaq == 10:
						if self.RN == SNpaq: #REVISAR SI ES DEL TIPO DE MENSAJE QUE ESTOY ESPERANDO
							self.datosRecibidos += datos
							#Enviar paquete de ack de respuesta
							self.RN = self.RN + 1

							if RNpaq > self.SN:
								self.SN = RNpaq

								if len(self.archivoActual) == 0: #paquete actual ya termino y ya lo confirmaron
									self.lockArchivos.acquire()
									if len(self.ArchivosAEnviar) != 0: # si hay mas paquetes para enviar
										
										self.archivoActual = self.ArchivosAEnviar.pop(0)
									
										self.ultimoMensajeMandado = self.archivoActual.pop(0)
									else:
										self.ultimoMensajeMandado = bytearray()
									self.lockArchivos.release()
								else:
									self.ultimoMensajeMandado = self.archivoActual.pop(0)

								ACK = armarPaq(self.miConexion[0], self.miConexion[1], self.otraConexion[0], self.otraConexion[1], 10, self.SN, self.RN, self.ultimoMensajeMandado) #VER SI TENGO DATOS PARA MANDAR
								
								self.lockSocket.acquire()
								self.socketConexion.sendto(ACK, emisor)
								self.lockSocket.release()
							#VEEEEEEEEEEEEEEEEEEEER EL ELSE PORQUE CREO QUE HAY QUE MANDAR ALGO AUNQUE SEA UN ACK



class emisor:

	def __init__(self, miConexion, buzonReceptor, socketConexion, lockSocket, conexiones, lockConexiones):
		self.conexiones = conexiones
		self.lockConexiones = lockConexiones
		self.miConexion = miConexion
		self.buzonReceptor = buzonReceptor
		self.socketConexion = socketConexion
		self.lockSocket = lockSocket



	#Llamar solo CON candado adquirido
	def buscarConexionLogica(self, ip,puerto):#APLICA SI LAS CONEXIONES DEBEN ESTAR PARA AMBOS , creo que deben estar aunque para tener una lista de las conexiones hechas para usarlas, VER QUE DICE LA PROFE
		i = 0;
		largo = len(self.conexiones)
		while i < largo:
			if self.conexiones[i].soyLaConexionHacia(ip,puerto) :
				return i
			i = i + 1
		return -1

	def enviarArchivo(self):
		otraIp = input('Digite la ip del destinatario: ')
		ipPrueba = otraIp + "/32"
		try:
			n = ipaddress.ip_network(ipPrueba)
		except ValueError as e:
			print ("Ip no valida")
		else:
			lecturaPuerto = input('Digite el puerto del destinatario: ')
			try:
				otroPuerto = int(lecturaPuerto)
			except ValueError as e:
				print ("Puerto no valido")
			else:
				if otroPuerto < 0 or otroPuerto > 65535:
					print ("Puerto no valido")
				else:
					direccion = input('Digite la direccion del archivo: ')
					#direccion = "/home/christofer/Escritorio/RedesProyecto/ArchivoPrueba.txt" #QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQUUUUUUUUUUUUUUUUUUIIIIIIIIIIIIIIIIIIIITTTTTTTTTTTTTTTAAAAAAAAAAAAAAAAAAAAAARRRRRRRRRRRRRRRRRRRRR
					contenido = archivoToString(direccion)
					self.lockConexiones.acquire()
					indice = self.buscarConexionLogica(otraIp, otroPuerto)

					if indice == -1:
						print ("Nueva conexion")
						conexion = HiloConexionUDPSegura( self.buzonReceptor, (otraIp,otroPuerto), self.miConexion, self.socketConexion, self.lockSocket )
						conexion.connect(otraIp,otroPuerto)

						conexion.meterArchivoAEnviar(contenido)
						
						hiloNuevaConexion = threading.Thread(target=conexion.receptor, args=())
						hiloNuevaConexion.start()

						self.conexiones.append(conexion)#ANALIDAR CUANDO HAY QUE SACARLA POR SI NO SE HACE EL HANDSHAKE O TERMINA LA CONEXION O TIMEOUT EN ENVIAR DATOS
					
					else:
						print("Conexion existente")
						
						conexion.meterArchivoAEnviar(contenido)

					self.lockConexiones.release()




class Server:	
	def __init__(self, miConexion, buzonReceptor, socketConexion, lockSocket, conexiones, lockConexiones):
		self.conexiones = conexiones
		self.lockConexiones = lockConexiones
		self.miConexion = miConexion
		self.buzonReceptor = buzonReceptor
		self.socketConexion = socketConexion
		self.lockSocket = lockSocket

	#Llamar solo CON candado adquirido
	def buscarConexionLogica(self, ip,puerto):#APLICA SI LAS CONEXIONES DEBEN ESTAR PARA AMBOS , creo que deben estar aunque para tener una lista de las conexiones hechas para usarlas, VER QUE DICE LA PROFE
		i = 0;
		largo = len(self.conexiones)
		while i < largo:
			if self.conexiones[i].soyLaConexionHacia(ip,puerto) :
				return i
			i = i + 1
		return -1

	def cicloServer(self):
		while True:
			recibido, clientAddress = self.socketConexion.recvfrom(2048)
			
			self.lockConexiones.acquire()

			existeConexion = self.buscarConexionLogica( clientAddress[0], clientAddress[1])
			print("EXISTE CONEXION")
			print(existeConexion)

			if existeConexion != -1 :
				self.buzonReceptor.meterDatos(clientAddress, recibido)
			else:
				tipoPaq = bytesToInt(recibido[12:13])
				print("Tipo paquete")
				print(tipoPaq)
				if tipoPaq == 1:
					self.buzonReceptor.meterDatos(clientAddress, recibido)
					
					conexion = HiloConexionUDPSegura( self.buzonReceptor, clientAddress, self.miConexion, self.socketConexion, self.lockSocket )
						
					self.conexiones.append(conexion)#ANALIDAR CUANDO HAY QUE SACARLA POR SI NO SE HACE EL HANDSHAKE O TERMINA LA CONEXION O TIMEOUT EN ENVIAR DATOS
					hiloNuevaConexion = threading.Thread(target=conexion.receptor, args=())
					hiloNuevaConexion.start()
				else:
					print(clientAddress)
					print("ESTA CONEXION NO EXITE Y LLEGO UN MENSAJE DISTINTO A SYN")
			
			self.lockConexiones.release()



if __name__ == '__main__':

	socketConexion = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	socketConexion.bind((sys.argv[1],int(sys.argv[2])))

	lockSocket = threading.Lock()

	#time.sleep(10)

	buzonReceptor = Buzon()

	conexiones = list()

	lockConexiones = threading.Lock()

	emisor = emisor( (sys.argv[1],int(sys.argv[2])), buzonReceptor, socketConexion, lockSocket, conexiones, lockConexiones)

	server = Server( (sys.argv[1],int(sys.argv[2])), buzonReceptor, socketConexion, lockSocket, conexiones, lockConexiones)

	threadEmisor = threading.Thread(target=server.cicloServer, args=())
	threadEmisor.start()

	emisor.enviarArchivo()