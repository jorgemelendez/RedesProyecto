import sys
import time
import socket
import threading
import datetime
from random import randrange

from ArmarMensajes import *
from LeerArchivo import *
from Buzon import *
from Bitacora import *

class HiloConexionUDPSegura:

	def __init__(self, buzonReceptor, otraConexion, miConexion, socketConexion, lockSocket,  bitacora):
		self.buzonReceptor = buzonReceptor
		self.otraConexion = otraConexion
		self.miConexion = miConexion
		self.SN = 0
		self.RN = 0
		self.socketConexion = socketConexion
		self.lockSocket = lockSocket
		self.datosRecibidos = bytearray()
		self.etapaSyn = 0
		self.lockArchivos = threading.Lock()
		self.termineEnviar = threading.Lock()
		self.archivoActual = list()#Archivo actual que se esta enviando
		self.ackDatosFin = False
		self.ackHandshakeTerminado = False
		self.ultimoMensajeMandado = bytearray()
		self.bitacora = bitacora
		self.primerDatoArchivo = False
		self.now = datetime.datetime.now()
		self.lockContinuarReceptor = threading.Lock()
		self.continuarReceptor = True
		self.tipo = 0
		self.FinArchivoSN = 0
		self.FinArchivoRN = 0

	def soyLaConexionHacia(self, ip, puerto):
		return self.otraConexion == (ip,puerto)

	def meterArchivoAEnviar(self, contenidoArchivo):
		self.lockArchivos.acquire()
		self.archivoActual = segmentarArchivo(contenidoArchivo, 5)
		self.lockArchivos.release()
		print("Primero")
		self.termineEnviar.acquire()
		print("Segundo")
		self.termineEnviar.acquire()
		print("Tercero")
		self.termineEnviar.release()

	def connect(self, ipServidor, puertoServidor):
		mensaje = armarPaq(self.miConexion[0], self.miConexion[1], self.otraConexion[0], self.otraConexion[1], 1, self.SN, self.RN, bytearray() ) #NO HAY QUE MANDAR DATOS PORQUE ES ESTABLECIENDO CONEXION
		self.lockSocket.acquire()
		self.socketConexion.sendto(mensaje, (ipServidor, puertoServidor))
		self.lockSocket.release()
		self.etapaSyn = 2
		self.bitacora.escribir("HiloReceptor: Envie syn a " + ipServidor + " " + str(puertoServidor) )

	def close(self):
		self.lockContinuarReceptor.acquire()
		self.continuarReceptor = False
		self.lockContinuarReceptor.release()
		self.bitacora.escribir("HiloReceptor: Me indicaron close")

	#METER MENSAJE EN EL BUZON ANTES DE CREAR EL HILO
	def receptor(self):
		while True:
			recibido = self.buzonReceptor.sacarDatos(self.otraConexion)
			if recibido is None:
				time.sleep(0.5)#ANALIZAR LA CANTIDAD DE SEGUNDOS
				recibido = self.buzonReceptor.sacarDatos(self.otraConexion)
			if recibido is None:
				if self.etapaSyn == 3 and self.ackHandshakeTerminado == False:#Caso donde no llegan los primeros primeros datos y ya se envio el ack syn
					ACKConexion = armarPaq(self.miConexion[0], self.miConexion[1], self.otraConexion[0], self.otraConexion[1], 3, self.SN, self.RN, bytearray()) #NO HAY QUE MANDAR DATOS PORQUE ES ESTABLECIENDO CONEXION
					self.lockSocket.acquire()
					self.socketConexion.sendto(ACKConexion, self.otraConexion)
					self.lockSocket.release()
					self.bitacora.escribir("HiloReceptor: Reenvie ack de handshake " +  "\n\tmiConexion = (" + self.miConexion[0] + "," + str(self.miConexion[1]) + ")\n\totraConexion = (" + self.otraConexion[0] + "," + str(self.otraConexion[1]) + ")\n\tTipoMensaje = 3 \n\tSN = " + str(self.SN) + "\n\tRN = " + str(self.RN) + "\n\tDatos = ")
				if self.etapaSyn == 3 and self.ackHandshakeTerminado == True: #Caso donde no responde con paq nuevo
					ACKDatos = armarPaq(self.miConexion[0], self.miConexion[1], self.otraConexion[0], self.otraConexion[1], self.tipo, self.SN, self.RN, self.ultimoMensajeMandado ) #VER SI TENGO DATOS PARA MANDAR
					self.lockSocket.acquire()
					self.socketConexion.sendto(ACKDatos, self.otraConexion)
					self.lockSocket.release()
					self.bitacora.escribir("HiloReceptor: Reenvie ack de datos " +  "\n\tmiConexion = (" + self.miConexion[0] + "," + str(self.miConexion[1]) + ")\n\totraConexion = (" + self.otraConexion[0] + "," + str(self.otraConexion[1]) + ")\n\tTipoMensaje = 10 \n\tSN = " + str(self.SN) + "\n\tRN = " + str(self.RN) + "\n\tDatos = " + self.ultimoMensajeMandado.decode("utf-8"))
				else:
					if self.etapaSyn == 2: #Caso donde no responden syn
						self.connect(self.otraConexion[0], self.otraConexion[1])
						print("REENVIE SYN")
						self.bitacora.escribir("HiloReceptor: Reenvie syn " +  "\n\tmiConexion = (" + self.miConexion[0] + "," + str(self.miConexion[1]) + ")\n\totraConexion = (" + self.otraConexion[0] + "," + str(self.otraConexion[1]) + ")\n\tTipoMensaje = 1 \n\tSN = " + str(self.SN) + "\n\tRN = " + str(self.RN) + "\n\tDatos = ")
					else:
						if self.etapaSyn == 1:#Caso donde no responden respuesta a syn(no llega ack syn)
							ACKConexion = armarPaq(self.miConexion[0], self.miConexion[1], self.otraConexion[0], self.otraConexion[1], 1, self.SN, self.RN, bytearray()) #NO HAY QUE MANDAR DATOS PORQUE ES ESTABLECIENDO CONEXION
							self.lockSocket.acquire()
							self.socketConexion.sendto(ACKConexion, self.otraConexion)
							self.lockSocket.release()
							self.bitacora.escribir("HiloReceptor: Reenvie respuesta de syn " +  "\n\tmiConexion = (" + self.miConexion[0] + "," + str(self.miConexion[1]) + ")\n\totraConexion = (" + self.otraConexion[0] + "," + str(self.otraConexion[1]) + ")\n\tTipoMensaje = 1 \n\tSN = " + str(self.SN) + "\n\tRN = " + str(self.RN) + "\n\tDatos = ")
				time.sleep(0.5)#ANALIZAR LA CANTIDAD DE SEGUNDOS
			else:
				otroIpRec = bytesToIp(recibido[0:4])
				otroPuertoRec = bytesToInt(recibido[4:6])
				miIpRec = bytesToIp(recibido[6:10])
				miPuertoRec = bytesToInt(recibido[10:12])
				tipoPaq = bytesToInt(recibido[12:13])
				SNpaq = bytesToInt(recibido[13:14])
				RNpaq = bytesToInt(recibido[14:15])
				datos = recibido[15:]
				self.bitacora.escribir("HiloReceptor: recibi mensaje " + "\n\tIpOtra: " + otroIpRec + "\n\tPuertoOtro: " + str(otroPuertoRec) + "\n\tIpMia: " + miIpRec + "\n\tPuertoMio: " + str(miPuertoRec) + "\n\tTipoPaquete: " + str(tipoPaq) + "\n\tSNpaq: " + str(SNpaq) + "\n\tRNpaq: " + str(RNpaq) + "\n\tDatos: " + datos.decode("utf-8") )
				if self.etapaSyn != 3:
					if self.etapaSyn == 0 and tipoPaq == 1:
						self.RN = SNpaq + 1
						self.SN = 0
						self.connect(self.otraConexion[0], self.otraConexion[1])
						self.etapaSyn = 1
						self.bitacora.escribir("HiloReceptor: envie syn (paso 2) " +  "\n\tmiConexion = (" + self.miConexion[0] + "," + str(self.miConexion[1]) + ")\n\totraConexion = (" + self.otraConexion[0] + "," + str(self.otraConexion[1]) + ")\n\tTipoMensaje = 1 \n\tSN = " + str(self.SN) + "\n\tRN = " + str(self.RN) + "\n\tDatos = " )
					elif self.etapaSyn == 2 and tipoPaq == 1:
						self.RN = SNpaq + 1
						self.SN = RNpaq
						ACKConexion = armarPaq(self.miConexion[0], self.miConexion[1], self.otraConexion[0], self.otraConexion[1], 3, self.SN, self.RN, bytearray()) #NO HAY QUE MANDAR DATOS PORQUE ES ESTABLECIENDO CONEXION
						self.lockSocket.acquire()
						self.socketConexion.sendto(ACKConexion, self.otraConexion)
						self.lockSocket.release()
						self.etapaSyn = 3
						print ("Termine handshake como emisor")
						#self.ackHandshakeTerminado = True
						self.bitacora.escribir("HiloReceptor: envie ack de syn " +  "\n\tmiConexion = (" + self.miConexion[0] + "," + str(self.miConexion[1]) + ")\n\totraConexion = (" + self.otraConexion[0] + "," + str(self.otraConexion[1]) + ")\n\tTipoMensaje = 3 \n\tSN = " + str(self.SN) + "\n\tRN = " + str(self.RN) + "\n\tDatos = ")
						self.bitacora.escribir("Termine handshake como emisor")
					elif self.etapaSyn == 1 and tipoPaq == 3:
						self.etapaSyn = 3
						print("Termine handshake como receptor")
						self.ackHandshakeTerminado = True
						self.bitacora.escribir("Termine handshake como receptor")
						self.RN = self.RN + 1
						if RNpaq > self.SN:
							self.SN = RNpaq
							self.lockArchivos.acquire()
							if len(self.archivoActual) == 0: #paquete actual ya termino y ya lo confirmaron
								self.ultimoMensajeMandado = bytearray()
							else:
								self.ultimoMensajeMandado = self.archivoActual.pop(0)
							self.lockArchivos.release()
							ACK = armarPaq(self.miConexion[0], self.miConexion[1], self.otraConexion[0], self.otraConexion[1], 10, self.SN, self.RN, self.ultimoMensajeMandado) #VER SI TENGO DATOS PARA MANDAR
							self.tipo = 10
							self.lockSocket.acquire()
							self.socketConexion.sendto(ACK, self.otraConexion)
							self.lockSocket.release()
							self.bitacora.escribir("HiloReceptor: envie ack de datos " +  "\n\tmiConexion = (" + self.miConexion[0] + "," + str(self.miConexion[1]) + ")\n\totraConexion = (" + self.otraConexion[0] + "," + str(self.otraConexion[1]) + ")\n\tTipoMensaje = 10 \n\tSN = " + str(self.SN) + "\n\tRN = " + str(self.RN) + "\n\tDatos = " + self.ultimoMensajeMandado.decode("utf-8"))
					else:
						print("Mensaje extranno")
						self.bitacora.escribir("Mensaje recibido extranno")
				else:
					if tipoPaq == 10 or tipoPaq == 26:
						if self.RN == SNpaq: #REVISAR SI ES DEL TIPO DE MENSAJE QUE ESTOY ESPERANDO
							self.datosRecibidos += datos
							self.ackHandshakeTerminado = True
							if self.primerDatoArchivo == False and len(datos) > 0:
								self.primerDatoArchivo = True
								print("ESTE ES EL PRIMER DATO DEL ARCHIVO")
								self.bitacora.escribir("COMENCE A RECIBIR ARCHIVO")
								self.archivo = open("Archivo-"+str(self.now.year) +"_"+ str(self.now.month) +"_"+ str(self.now.day) +"_"+ str(self.now.hour) +"_"+ str(self.now.minute) +"_"+ str(self.now.second) +"_"+ str(self.now.microsecond), "wb+")
							if len(datos) > 0:
								self.archivo.write(datos)
							if tipoPaq == 26:
								print("YA TERMINE DE RECIBIR ARCHIVO")
								self.primerDatoArchivo = False
								self.bitacora.escribir("TERMINE DE RECIBIR ARCHIVO")
								self.archivo.close()
							self.RN = self.RN + 1
							if self.FinArchivoSN+1 == RNpaq and self.FinArchivoRN == SNpaq:
								self.termineEnviar.release()
							else:
								self.bitacora.escribir("FinArchivoSN+1 = " + str(self.FinArchivoSN+1) + "\nRNPaq = " + str(RNpaq) + "\nFinArchivoRN= " + str(self.FinArchivoRN) + "\nSNpaq= "+ str(SNpaq))
							if RNpaq > self.SN:
								self.SN = RNpaq
								self.tipo = 10
								self.lockArchivos.acquire()
								if len(self.archivoActual) == 0: #paquete actual ya termino y ya lo confirmaron
									self.ultimoMensajeMandado = bytearray()
								else:
									self.ultimoMensajeMandado = self.archivoActual.pop(0)
									if len(self.archivoActual) == 0:
										self.bitacora.escribir("Ultimo pedazo de enviar")
										self.bitacora.escribir("FinArchivoSN = " + str(self.SN))
										self.bitacora.escribir("FinArchivoRN = " + str(self.RN))
										self.tipo = 26
										self.FinArchivoSN = self.SN
										self.FinArchivoRN = self.RN
								self.lockArchivos.release()
								self.lockContinuarReceptor.acquire()
								continuo = self.continuarReceptor
								self.lockContinuarReceptor.release()
								ultimo = self.ultimoMensajeMandado
								#print("Pregunte si era 4")
								if continuo == False:
									print("ENTRE A ENVIAR MENSAJE TIPO 4")
									self.tipo = 4
									ACK = armarPaq(self.miConexion[0], self.miConexion[1], self.otraConexion[0], self.otraConexion[1], self.tipo, self.SN, self.RN, bytearray())
									self.bitacora.escribir("HiloReceptor: envie fin de conexion " +  "\n\tmiConexion = (" + self.miConexion[0] + "," + str(self.miConexion[1]) + ")\n\totraConexion = (" + self.otraConexion[0] + "," + str(self.otraConexion[1]) + ")\n\tTipoMensaje = "+str(self.tipo)+" \n\tSN = " + str(self.SN) + "\n\tRN = " + str(self.RN) + "\n\tDatos = ")
								else:
									ACK = armarPaq(self.miConexion[0], self.miConexion[1], self.otraConexion[0], self.otraConexion[1], self.tipo, self.SN, self.RN, self.ultimoMensajeMandado) #VER SI TENGO DATOS PARA MANDAR
									self.bitacora.escribir("HiloReceptor: envie ack de datos " +  "\n\tmiConexion = (" + self.miConexion[0] + "," + str(self.miConexion[1]) + ")\n\totraConexion = (" + self.otraConexion[0] + "," + str(self.otraConexion[1]) + ")\n\tTipoMensaje = "+str(self.tipo)+" \n\tSN = " + str(self.SN) + "\n\tRN = " + str(self.RN) + "\n\tDatos = " + self.ultimoMensajeMandado.decode("utf-8"))
								self.lockSocket.acquire()
								self.socketConexion.sendto(ACK, self.otraConexion)
								self.lockSocket.release()
						else:
							self.bitacora.escribir("Mensaje recibido extranno, RN != SNpaq")
					elif tipoPaq == 4:
						self.bitacora.escribir("El mensaje recibido es de cerrar conexion")
						self.RN = self.RN + 1
						if RNpaq > self.SN:
							self.SN = RNpaq
						ACK = armarPaq(self.miConexion[0], self.miConexion[1], self.otraConexion[0], self.otraConexion[1], 6, self.SN, self.RN, bytearray()) #VER SI TENGO DATOS PARA MANDAR
						self.bitacora.escribir("HiloReceptor: envie ack para finalizar conexion " +  "\n\tmiConexion = (" + self.miConexion[0] + "," + str(self.miConexion[1]) + ")\n\totraConexion = (" + self.otraConexion[0] + "," + str(self.otraConexion[1]) + ")\n\tTipoMensaje = 6 \n\tSN = " + str(self.SN) + "\n\tRN = " + str(self.RN) + "\n\tDatos = " )
						self.bitacora.escribir("HiloReceptor: Finalice")
						self.lockSocket.acquire()
						self.socketConexion.sendto(ACK, self.otraConexion)
						self.lockSocket.release()
						print("break 1")
						if self.termineEnviar.locked():
							self.termineEnviar.release()
						break
					elif tipoPaq == 6:
						self.bitacora.escribir("HiloReceptor: Finalice")
						print("break 2")
						if self.termineEnviar.locked():
							self.termineEnviar.release()
						break
		print("Salir de while")


class Emisor:

	def __init__(self, miConexion, buzonReceptor, socketConexion, lockSocket, conexiones, lockConexiones, bitacora):
		self.conexiones = conexiones
		self.lockConexiones = lockConexiones
		self.miConexion = miConexion
		self.buzonReceptor = buzonReceptor
		self.socketConexion = socketConexion
		self.lockSocket = lockSocket
		self.bitacora = bitacora

	#Llamar solo CON candado adquirido
	def buscarConexionLogica(self, ip,puerto):#APLICA SI LAS CONEXIONES DEBEN ESTAR PARA AMBOS , creo que deben estar aunque para tener una lista de las conexiones hechas para usarlas, VER QUE DICE LA PROFE
		i = 0;
		largo = len(self.conexiones)
		while i < largo:
			if self.conexiones[i].soyLaConexionHacia(ip,puerto) :
				return i
			i = i + 1
		return -1

	def crearHilo(self, conexion):
		conexion.receptor()
		print("Antes del terminar")
		self.lockConexiones.acquire()
		print("Despues del lock")
		self.conexiones.remove(conexion)
		self.lockConexiones.release()
		print("Libere el lock 1")

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
					contenido = archivoToString(direccion)
					self.lockConexiones.acquire()
					indice = self.buscarConexionLogica(otraIp, otroPuerto)
					if indice == -1:
						print ("Nueva conexion")
						conexion = HiloConexionUDPSegura( self.buzonReceptor, (otraIp,otroPuerto), self.miConexion, self.socketConexion, self.lockSocket, self.bitacora )
						conexion.connect(otraIp,otroPuerto)
						hiloNuevaConexion = threading.Thread(target=self.crearHilo, args=(conexion,))
						hiloNuevaConexion.start()
						self.conexiones.append(conexion)#ANALIDAR CUANDO HAY QUE SACARLA POR SI NO SE HACE EL HANDSHAKE O TERMINA LA CONEXION O TIMEOUT EN ENVIAR DATOS
						self.bitacora.escribir("Emisor: cree la conexion" + otraIp + " " + str(otroPuerto) )
						self.lockConexiones.release()
						conexion.meterArchivoAEnviar(contenido)
						print("Sali de enviar archivo 1")
					else:
						print("Conexion existente")
						self.lockConexiones.release()
						self.conexiones[indice].meterArchivoAEnviar(contenido)
						print("Sali de enviar archivo 2")
					self.bitacora.escribir("Emisor: envie un archivo a " + otraIp + " " + str(otroPuerto) )

class Server:
	def __init__(self, miConexion, buzonReceptor, socketConexion, lockSocket, conexiones, lockConexiones, bitacora, lockFin, fin):
		self.conexiones = conexiones
		self.lockConexiones = lockConexiones
		self.miConexion = miConexion
		self.buzonReceptor = buzonReceptor
		self.socketConexion = socketConexion
		self.lockSocket = lockSocket
		self.bitacora = bitacora
		self.lockFin = lockFin
		self.fin = fin

	#Llamar solo CON candado adquirido
	def buscarConexionLogica(self, ip,puerto):#APLICA SI LAS CONEXIONES DEBEN ESTAR PARA AMBOS , creo que deben estar aunque para tener una lista de las conexiones hechas para usarlas, VER QUE DICE LA PROFE
		i = 0;
		largo = len(self.conexiones)
		while i < largo:
			if self.conexiones[i].soyLaConexionHacia(ip,puerto) :
				return i
			i = i + 1
		return -1

	def crearHilo(self, conexion):
		conexion.receptor()
		print("Antes del terminar")
		self.lockConexiones.acquire()
		print("Despues del lock")
		self.conexiones.remove(conexion)
		self.lockConexiones.release()
		print("Libere el lock 1")

	def cicloServer(self):
		self.bitacora.escribir("Servidor: Inicie")
		while True:
			self.lockSocket.acquire()
			recibido, clientAddress = self.socketConexion.recvfrom(2048)
			self.lockSocket.release()
			self.lockConexiones.acquire()
			existeConexion = self.buscarConexionLogica( clientAddress[0], clientAddress[1])
			if existeConexion != -1 :
				tipoPaq = bytesToInt(recibido[12:13])
				random = randrange(10)
				if random>1 or tipoPaq == 6:
					self.buzonReceptor.meterDatos(clientAddress, recibido)
				else:
					self.bitacora.escribir("Server: se elimino un paquete que recibi")
			else:
				tipoPaq = bytesToInt(recibido[12:13])
				if tipoPaq == 1:
					self.buzonReceptor.meterDatos(clientAddress, recibido)
					self.bitacora.escribir("Servidor: cree la conexion " + clientAddress[0] + " " + str(clientAddress[1]) )
					conexion = HiloConexionUDPSegura( self.buzonReceptor, clientAddress, self.miConexion, self.socketConexion, self.lockSocket, self.bitacora)
					self.conexiones.append(conexion)#ANALIDAR CUANDO HAY QUE SACARLA POR SI NO SE HACE EL HANDSHAKE O TERMINA LA CONEXION O TIMEOUT EN ENVIAR DATOS
					hiloNuevaConexion = threading.Thread(target=self.crearHilo, args=(conexion,))
					hiloNuevaConexion.start()
				else:
					print(clientAddress)
					print("ESTA CONEXION NO EXITE Y LLEGO UN MENSAJE DISTINTO A SYN")
			self.lockConexiones.release()
			self.lockFin.acquire()
			termino = self.fin
			self.lockFin.release()
			if termino == True:
				break
			print("Pase")

class nodo:

	def __init__(self, miConexion):
		self.miConexion = miConexion
		self.bitacora = Bitacora("Bitacora.txt")
		self.socketConexion = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socketConexion.bind(self.miConexion)
		self.lockSocket = threading.Lock()
		self.buzonReceptor = Buzon()
		self.conexiones = list()
		self.lockConexiones = threading.Lock()
		self.emisor = Emisor( self.miConexion, self.buzonReceptor, self.socketConexion, self.lockSocket, self.conexiones, self.lockConexiones, self.bitacora)
		self.lockFin = threading.Lock()
		self.fin = False
		self.server = Server( self.miConexion, self.buzonReceptor, self.socketConexion, self.lockSocket, self.conexiones, self.lockConexiones, self.bitacora, self.lockFin, self.fin)

	def cerrarTodo(self):
		self.lockConexiones.acquire()
		i = 0;
		largo = len(self.conexiones)
		while i < largo:
			self.conexiones[i].close()
			i = i + 1
		self.lockConexiones.release()

	def menu(self):
		bandera = True
		while bandera == True:
			print('Menu principal del modulo de Red TCP: \n'
					'\t1. Enviar un archivo. \n'
					'\t2. CerrarConexion. \n'
					'\t3. Salir. \n')
			taskUsuario = input('Que desea hacer:')
			if taskUsuario == '1':
				self.emisor.enviarArchivo()
			elif taskUsuario == '2':
				self.cerrarTodo()
			elif taskUsuario == '3':
				self.lockFin.acquire()
				self.fin = True
				self.lockFin.release()
				break
			else:
				print('Ingrese una opcion valida.')

	def nodo(self):
		threadEmisor = threading.Thread(target=self.server.cicloServer, args=())
		threadEmisor.start()
		#emisor.enviarArchivo()
		self.menu()
		#time.sleep(10)
		self.bitacora.terminar()
		print("Emisor termine")

if __name__ == '__main__':
	prueba = nodo((sys.argv[1],int(sys.argv[2])))
	prueba.nodo()