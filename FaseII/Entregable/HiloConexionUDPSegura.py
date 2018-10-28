import sys
import time
import socket
import threading
import datetime
import os
from random import randrange

from ArmarMensajes import *
from LeerArchivo import *
from Buzon import *
from Bitacora import *
from Emisor import *
from Servidor import *
from BanderaFin import *

class HiloConexionUDPSegura:

	def __init__(self, buzonReceptor, otraConexion, miConexion, socketConexion, lockSocket,  bitacora):
		self.buzonReceptor = buzonReceptor #Buzon donde leen los mensajes que reciben
		self.otraConexion = otraConexion #(ip,puerto) del socket que estan conectados
		self.miConexion = miConexion #(ip,puerto) del socket
		self.SN = 0
		self.RN = 0
		self.socketConexion = socketConexion
		self.lockSocket = lockSocket
		self.etapaSyn = 0 #Etapa donde esta la conexion, 0 iniciando, 1 recibo que se quieren conectar conmigo, 2 envie connect y estoy esperando respuesta, 3 terminado.
		self.lockArchivos = threading.Lock()
		self.termineEnviar = threading.Lock() #para bloquear el envio de un archivo.
		self.archivoActual = list()
		self.ackDatosFin = False #indica que ya recibi ack del ultimo paquete del archivo.
		self.ackHandshakeTerminado = False #indica que ya se termino el handshake, osea que ya se comenzo a enviar archivos
		self.ultimoMensajeMandado = bytearray()
		self.bitacora = bitacora
		self.primerDatoArchivo = False #indica que se esta enviando el primer dato del archivo
		self.now = datetime.datetime.now()
		self.lockContinuarReceptor = threading.Lock()
		self.continuarReceptor = True #Indica si el hilo continua
		self.tipo = 0 #tipo de paquete que se va a enviar
		self.FinArchivoSN = -1 #para controlar que ya se recibio ack del ultimo paquete del archivo y poder salir del envio
		self.FinArchivoRN = -1 #para controlar que ya se recibio ack del ultimo paquete del archivo y poder salir del envio

	def soyLaConexionHacia(self, ip, puerto):
		return self.otraConexion == (ip,puerto)

	def meterArchivoAEnviar(self, contenidoArchivo):
		self.lockArchivos.acquire()
		self.archivoActual = segmentarArchivo(contenidoArchivo, 5)
		self.lockArchivos.release()
		self.termineEnviar.acquire()
		self.termineEnviar.acquire()
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
		contador = 0
		while True:
			recibido = self.buzonReceptor.sacarDatos(self.otraConexion)
			if recibido is None:
				time.sleep(0.5)
				recibido = self.buzonReceptor.sacarDatos(self.otraConexion)
			if recibido is None:
				contador = contador + 1
				if contador == 10:
					if self.etapaSyn == 3 and self.ackHandshakeTerminado == False:
						print("No se pudo establecer la conexion")
						self.bitacora.escribir("No se pudo establecer la conexion")
					else:
						print("Conexion perdida")
						self.bitacora.escribir("Conexion perdida")
					if self.termineEnviar.locked():
						self.termineEnviar.release()
					break
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
						#print("REENVIE SYN")
						self.bitacora.escribir("HiloReceptor: Reenvie syn " +  "\n\tmiConexion = (" + self.miConexion[0] + "," + str(self.miConexion[1]) + ")\n\totraConexion = (" + self.otraConexion[0] + "," + str(self.otraConexion[1]) + ")\n\tTipoMensaje = 1 \n\tSN = " + str(self.SN) + "\n\tRN = " + str(self.RN) + "\n\tDatos = ")
					else:
						if self.etapaSyn == 1:#Caso donde no responden respuesta a syn(no llega ack syn)
							ACKConexion = armarPaq(self.miConexion[0], self.miConexion[1], self.otraConexion[0], self.otraConexion[1], 1, self.SN, self.RN, bytearray()) #NO HAY QUE MANDAR DATOS PORQUE ES ESTABLECIENDO CONEXION
							self.lockSocket.acquire()
							self.socketConexion.sendto(ACKConexion, self.otraConexion)
							self.lockSocket.release()
							self.bitacora.escribir("HiloReceptor: Reenvie respuesta de syn " +  "\n\tmiConexion = (" + self.miConexion[0] + "," + str(self.miConexion[1]) + ")\n\totraConexion = (" + self.otraConexion[0] + "," + str(self.otraConexion[1]) + ")\n\tTipoMensaje = 1 \n\tSN = " + str(self.SN) + "\n\tRN = " + str(self.RN) + "\n\tDatos = ")
				time.sleep(0.5)
			else:
				contador = 0
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
						self.RN = SNpaq
						self.RN = (self.RN + 1) % 8
						self.SN = 0
						self.connect(self.otraConexion[0], self.otraConexion[1])
						self.etapaSyn = 1
						self.bitacora.escribir("HiloReceptor: envie syn (paso 2) " +  "\n\tmiConexion = (" + self.miConexion[0] + "," + str(self.miConexion[1]) + ")\n\totraConexion = (" + self.otraConexion[0] + "," + str(self.otraConexion[1]) + ")\n\tTipoMensaje = 1 \n\tSN = " + str(self.SN) + "\n\tRN = " + str(self.RN) + "\n\tDatos = " )
					elif self.etapaSyn == 2 and tipoPaq == 1:
						if self.SN < RNpaq:
							self.RN = SNpaq
							self.RN = (self.RN + 1) % 8
							self.SN = RNpaq
							ACKConexion = armarPaq(self.miConexion[0], self.miConexion[1], self.otraConexion[0], self.otraConexion[1], 3, self.SN, self.RN, bytearray()) #NO HAY QUE MANDAR DATOS PORQUE ES ESTABLECIENDO CONEXION
							self.lockSocket.acquire()
							self.socketConexion.sendto(ACKConexion, self.otraConexion)
							self.lockSocket.release()
							self.etapaSyn = 3
							#print ("Termine handshake como emisor")
							#self.ackHandshakeTerminado = True
							self.bitacora.escribir("HiloReceptor: envie ack de syn " +  "\n\tmiConexion = (" + self.miConexion[0] + "," + str(self.miConexion[1]) + ")\n\totraConexion = (" + self.otraConexion[0] + "," + str(self.otraConexion[1]) + ")\n\tTipoMensaje = 3 \n\tSN = " + str(self.SN) + "\n\tRN = " + str(self.RN) + "\n\tDatos = ")
							self.bitacora.escribir("Termine handshake como emisor")
					elif self.etapaSyn == 1 and tipoPaq == 3:
						if (RNpaq > self.SN or (RNpaq==0 and self.SN==7)) and self.RN == SNpaq:
							self.etapaSyn = 3
							##print("Termine handshake como receptor")
							self.ackHandshakeTerminado = True
							self.bitacora.escribir("Termine handshake como receptor")
							self.RN = (self.RN + 1) % 8
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
						#print("Mensaje extranno")
						self.bitacora.escribir("Mensaje recibido no conincide en ningun caso")
				else:
					if tipoPaq == 10 or tipoPaq == 26:
						if self.RN == SNpaq:
							self.ackHandshakeTerminado = True
							if self.primerDatoArchivo == False and len(datos) > 0:
								self.primerDatoArchivo = True
								#print("ESTE ES EL PRIMER DATO DEL ARCHIVO")
								self.bitacora.escribir("COMENCE A RECIBIR ARCHIVO")
								self.archivo = open("Archivo-"+str(self.now.year) +"_"+ str(self.now.month) +"_"+ str(self.now.day) +"_"+ str(self.now.hour) +"_"+ str(self.now.minute) +"_"+ str(self.now.second) +"_"+ str(self.now.microsecond), "wb+")
							if len(datos) > 0:
								self.archivo.write(datos)
								print(".")
							if tipoPaq == 26:
								print("YA TERMINE DE RECIBIR ARCHIVO")
								self.primerDatoArchivo = False
								self.bitacora.escribir("TERMINE DE RECIBIR ARCHIVO")
								self.archivo.close()
							self.RN = (self.RN + 1) % 8
							#print("FinArchivoSN + 1 = " + str((self.FinArchivoSN+1)%8) + " RNpaq = " + str(RNpaq) + " FinArchivoRN = " + str(self.FinArchivoRN) + " SNPaq = " + str(SNpaq) )
							if (self.FinArchivoSN > 0  and self.FinArchivoSN+1)%8 == RNpaq and self.FinArchivoRN == SNpaq:
								self.termineEnviar.release()
								self.FinArchivoSN = -1
								self.FinArchivoRN = -1
							else:
								self.bitacora.escribir("FinArchivoSN+1 = " + str(self.FinArchivoSN+1) + "\nRNPaq = " + str(RNpaq) + "\nFinArchivoRN= " + str(self.FinArchivoRN) + "\nSNpaq= "+ str(SNpaq))
							if (RNpaq > self.SN or (RNpaq==0 and self.SN==7)):
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
									#print("ENTRE A ENVIAR MENSAJE TIPO 4")
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
						self.RN = (self.RN + 1) % 8
						if (RNpaq > self.SN or (RNpaq==0 and self.SN==7)):
							self.SN = RNpaq
						ACK = armarPaq(self.miConexion[0], self.miConexion[1], self.otraConexion[0], self.otraConexion[1], 6, self.SN, self.RN, bytearray()) #VER SI TENGO DATOS PARA MANDAR
						self.bitacora.escribir("HiloReceptor: envie ack para finalizar conexion " +  "\n\tmiConexion = (" + self.miConexion[0] + "," + str(self.miConexion[1]) + ")\n\totraConexion = (" + self.otraConexion[0] + "," + str(self.otraConexion[1]) + ")\n\tTipoMensaje = 6 \n\tSN = " + str(self.SN) + "\n\tRN = " + str(self.RN) + "\n\tDatos = " )
						self.bitacora.escribir("HiloReceptor: Finalice")
						self.lockSocket.acquire()
						self.socketConexion.sendto(ACK, self.otraConexion)
						self.lockSocket.release()
						#print("break 1")
						if self.termineEnviar.locked():
							self.termineEnviar.release()
						print("El otro nodo cerro la conexion")
						break
					elif tipoPaq == 6:
						self.bitacora.escribir("HiloReceptor: Finalice")
						#print("break 2")
						if self.termineEnviar.locked():
							self.termineEnviar.release()
						print("Cerre la conexion")
						break
		#print("Salir de while")
