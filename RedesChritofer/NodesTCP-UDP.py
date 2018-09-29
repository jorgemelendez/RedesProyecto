import sys
import threading
import socket
import errno
import codecs
import os
import ipaddress

from socket import error as SocketError

class Mensaje:
	def __init__(self,ip,puerto,mensaje):
		self.ip = ip
		self.puerto = puerto
		self.mensaje = mensaje

class Red:
	def __init__(self,ipFuente,puertoFuente,ipRed, mascaraRed, costo):
		self.ipFuente = ipFuente
		self.puertoFuente = puertoFuente
		self.ipRed = ipRed
		self.mascaraRed = mascaraRed 
		self.costo = costo

	def soyEsaRed(self, ipRed, mascaraRed):
		if ipRed == self.ipRed and mascaraRed == self.mascaraRed:
			return True
		return False

	def soyEsaFuente(self, ipFuente, puertoFuente):
		if ipFuente == self.ipFuente and puertoFuente == self.puertoFuente:
			return True
		return False

	def costoMenor(self, costo):
		if costo < self.costo:
			return True
		return False

	def actualizarRed(self,ipFuente,puertoFuente,ipRed, mascaraRed, costo):
		self.ipFuente = ipFuente
		self.puertoFuente = puertoFuente
		self.ipRed = ipRed
		self.mascaraRed = mascaraRed 
		self.costo = costo

class Fuente:
	def __init__(self,ipFuente,puertoFuente):
		self.ipFuente = ipFuente
		self.puertoFuente = puertoFuente

class TablaAlcanzabilidad:
	tabla = list()
	lockTablaAlcanzabilidad = threading.Lock()
	
	def __init__(self):
		self.tabla = list()
		self.lockTablaAlcanzabilidad = threading.Lock()

	#Llamar solo CON candado adquirido
	def existeRed(self, ipRed, mascaraRed):
		#self.lockTablaAlcanzabilidad.acquire()
		i = 0
		largo = len(self.tabla)
		while i < largo:
			if self.tabla[i].soyEsaRed(ipRed, mascaraRed) :
				#self.lockTablaAlcanzabilidad.release()
				return i
			i = i + 1
		#self.lockTablaAlcanzabilidad.release()
		return -1

	#Llamar solo SIN candado adquirido
	def imprimirTabla(self):
		self.lockTablaAlcanzabilidad.acquire()
		i = 0
		largo = len(self.tabla)
		while i < largo:
			ipFuente = self.tabla[i].ipFuente
			puertoFuente = self.tabla[i].puertoFuente
			ipA = int.from_bytes( self.tabla[i].ipRed[0:1], byteorder='big' )
			ipB = int.from_bytes( self.tabla[i].ipRed[1:2], byteorder='big' )
			ipC = int.from_bytes( self.tabla[i].ipRed[2:3], byteorder='big' )
			ipD = int.from_bytes( self.tabla[i].ipRed[3:4], byteorder='big' )

			mascaraRed = int.from_bytes( self.tabla[i].mascaraRed, byteorder='big' )
			costo = int.from_bytes( self.tabla[i].costo, byteorder='big' )
			print(str(ipFuente) + " " + str(puertoFuente) + " " + str(ipA) + "." + str(ipB) + "." + str(ipC) + "." + str(ipD) + " " + str(mascaraRed) + " " + str(costo) )

			i = i + 1

		self.lockTablaAlcanzabilidad.release()

	#NO necesita tener candado
	def validarIP(self, ip,mascara):
		ipA = int.from_bytes( ip[0:1], byteorder='big' )
		ipB = int.from_bytes( ip[1:2], byteorder='big' )
		ipC = int.from_bytes( ip[2:3], byteorder='big' )
		ipD = int.from_bytes( ip[3:4], byteorder='big' )
		mas = int.from_bytes( mascara[0:1], byteorder='big' )

		ipcompleta = str(ipA) + "." + str(ipB) + "." + str(ipC) + "." + str(ipD) + "/" + str(mas)
		try:
			n = ipaddress.ip_network(ipcompleta) 
			return True
		except ValueError as e:
			return False

	#Llamar solo SIN candado adquirido
	def borrarFuenteDesdeAfuera(self,ipFuente, puetoFuente):
		self.lockTablaAlcanzabilidad.acquire()
		#print("Entre a borrar fuente")
		i = 0
		largo = len(self.tabla)
		while i < largo:
			#print("while")
			if self.tabla[i].soyEsaFuente(ipFuente, puetoFuente) :
				self.tabla.pop(i)
				largo = largo - 1
			else:
				i = i + 1
		#print("Termine while")
		self.lockTablaAlcanzabilidad.release()

	#Llamar solo CON candado adquirido
	def borrarFuente(self,ipFuente, puetoFuente):
		#self.lockTablaAlcanzabilidad.acquire()
		#print("Entre a borrar fuente")
		i = 0
		largo = len(self.tabla)
		while i < largo:
			#print("while")
			if self.tabla[i].soyEsaFuente(ipFuente, puetoFuente) :
				self.tabla.pop(i)
				largo = largo - 1
			else:
				i = i + 1
		#print("Termine while")
		#self.lockTablaAlcanzabilidad.release()

	#Llamar solo SIN candado adquirido
	def eliminarPrimerFuente(self):
		self.lockTablaAlcanzabilidad.acquire()
		#print("Entre a eliminar primer fuente")
		i = 0
		largo = len(self.tabla)
		if largo > 0:
			ipFuente = self.tabla[i].ipFuente
			puertoFuente = self.tabla[i].puertoFuente
			#print("Mande a borrar fuente")
			self.borrarFuente(ipFuente,puertoFuente)
			#print("Volvi de borrar fuente")
			self.lockTablaAlcanzabilidad.release()
			return Fuente( ipFuente, puertoFuente )
		else:
			self.lockTablaAlcanzabilidad.release()
			return Fuente( "", 0 )

	#Llamar solo SIN candado adquirido
	def actualizarTabla(self, mensaje):
		#self.lockTablaAlcanzabilidad.acquire()

		ipFuenteNuevo = mensaje.ip
		puertoFuenteNuevo = mensaje.puerto
		bytesMensaje = mensaje.mensaje

		cantTuplas = int(codecs.encode(bytesMensaje[0:2], 'hex_codec'))
		i = 0
		while i < cantTuplas:
			ipRedNuevo = bytesMensaje[(i*8)+2:(i*8)+6]
			mascaraRedNuevo = bytesMensaje[(i*8)+6:(i*8)+7]
			costoNuevo = bytesMensaje[(i*8)+7:(i*8)+10]

			if self.validarIP(ipRedNuevo,mascaraRedNuevo):

				self.lockTablaAlcanzabilidad.acquire()
				exite = self.existeRed(ipRedNuevo, mascaraRedNuevo)
				if exite == -1 :
					#Se crea una nueva tupla
					self.tabla.append(Red(ipFuenteNuevo,puertoFuenteNuevo,ipRedNuevo, mascaraRedNuevo, costoNuevo))
				else:
					#se actualiza la tupla de ser necesario
					if self.tabla[exite].costoMenor(costoNuevo) :
						self.tabla[exite].actualizarRed(ipFuenteNuevo,puertoFuenteNuevo,ipRedNuevo, mascaraRedNuevo, costoNuevo);
					#Si el costo es mayor queda como antes
				self.lockTablaAlcanzabilidad.release()
			i = i + 1

		#self.lockTablaAlcanzabilidad.release()

class MensajesRecibidos:
	mensajesRecibidos = list()
	lockMensajesRecibidos = threading.Lock()

	def __init__(self):
		self.mensajesRecibidos = list()
		self.lockMensajesRecibidos = threading.Lock()

	#Llamar solo SIN candado adquirido
	def guardarMensaje(self,mensaje):
		self.lockMensajesRecibidos.acquire()
		self.mensajesRecibidos.append(mensaje)
		self.lockMensajesRecibidos.release()

	#NO necesita tener candado
	def imprimirMensaje(self, mensaje):
		ip = mensaje.ip
		puerto = mensaje.puerto
		bytesMensaje = mensaje.mensaje

		cantTuplas = int(codecs.encode(bytesMensaje[0:2], 'hex_codec'))
		i = 0
		#print("\n\nIPf = " + str(ip) + " Puerto = " + str(puerto) + " Envio el siguiente mensaje: ")
		print("IPf = " + str(ip) + " Puerto = " + str(puerto) + " Envio el siguiente mensaje: ")
		while i < cantTuplas:
			ipA = int.from_bytes( bytesMensaje[(i*8)+2:(i*8)+3], byteorder='big' )
			ipB = int.from_bytes( bytesMensaje[(i*8)+3:(i*8)+4], byteorder='big' )
			ipC = int.from_bytes( bytesMensaje[(i*8)+4:(i*8)+5], byteorder='big' )
			ipD = int.from_bytes( bytesMensaje[(i*8)+5:(i*8)+6], byteorder='big' )
			mascara = int.from_bytes( bytesMensaje[(i*8)+6:(i*8)+7], byteorder='big' )
			costo = int.from_bytes( bytesMensaje[(i*8)+7:(i*8)+10], byteorder='big' )
			print( str(ipA) + "." + str(ipB) + "." + str(ipC) + "." + str(ipD) + " " + str(mascara) + " " + str(costo) )
			i = i + 1
		#print("\n\n")

	#Llamar solo SIN candado adquirido
	def imprimirMensajes(self):
		self.lockMensajesRecibidos.acquire()
		i = 0
		largo = len(self.mensajesRecibidos)
		while i < largo:
			self.imprimirMensaje( self.mensajesRecibidos[i] )
			i = i + 1
		self.lockMensajesRecibidos.release()

class UDPNode:
	mensajesRecibidos= MensajesRecibidos()
	tablaAlcanzabilidad = TablaAlcanzabilidad()

	def __init__(self):
		self.mensajesRecibidos = MensajesRecibidos()

	def recibeMensajes(self, serverSocket):
		while 1:
			message, clientAddress = serverSocket.recvfrom(2048)
			mensaje = Mensaje(clientAddress[0],clientAddress[1], message)

			cantTuplas = int(codecs.encode(message[0:2], 'hex_codec'))
			mensajeSalir = int.from_bytes( message[2:3], byteorder='big' )
			#Si el mensaje recibido es la palabra close se cierra la aplicacion
			if cantTuplas == 1 and len(message) == 3 and mensajeSalir == 0:
				print("Nodo aviso suicidio")
				self.tablaAlcanzabilidad.borrarFuenteDesdeAfuera(clientAddress[0],clientAddress[1])
			else:
				self.mensajesRecibidos.guardarMensaje(mensaje)
				self.mensajesRecibidos.imprimirMensaje(mensaje)
				self.tablaAlcanzabilidad.actualizarTabla(mensaje)

	def procRecibeMsg(self, ip, puerto):
		#self.lockMensajesRecibidos.acquire()
		serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		serverSocket.bind((ip, puerto))
		self.recibeMensajes(serverSocket)
		#self.lockMensajesRecibidos.release()

	def tuplaToBytes(self, tupla):
		tupladiv = tupla.split(' ')
		numeroip = tupladiv[0]
		myip = numeroip.split('.')
		bytesmios = bytearray()
		for x in range(0, 4):
			ipnum = int(myip[x])
			bytesmios += (ipnum).to_bytes(1, byteorder='big')
		masc = int(tupladiv[1])
		bytesmios += (masc).to_bytes(1, byteorder='big')
		costo = int(tupladiv[2])
		bytesmios += (costo).to_bytes(3, byteorder='big')
		return bytesmios

	def leerMensaje(self):
		#print('Ingrese la cantidad de tuplas que quiere enviar:')
		entradas = 0
		leerCantTuplas = True
		while leerCantTuplas:
			lectura = input( "Ingrese la cantidad de tuplas: " )
			try:
				entradas = int(lectura)
				leerCantTuplas = False
			except ValueError as e:
				print("Cantidad de tuplas invalido")
				leerCantTuplas = True
		
		vectorBytes = bytearray((entradas).to_bytes(2, byteorder='big'))
		i = 0
		
		while i < entradas:
			#print('Ingrese la tupla:')
			leer = True
			while leer:
				tupla = input("Ingrese una tupla(ip mascara puerto): ")
				tuplaDividida = tupla.split()# tupla.replace(" ", "/",1)
				if len(tuplaDividida) == 3 :
					ipPrueba = tuplaDividida[0] + "/" + tuplaDividida[1]
					try:
						n = ipaddress.ip_network(ipPrueba) 
					except ValueError as e:
						print ("Ip o mascara no valida")
						leer = True
					else:
						leer = False
						try:
							costo = int(tuplaDividida[2]) 
						except ValueError as e:
							print ("Costo no valido")
							leer = True
						else:
							if costo > 0 and costo < 65536:
								leer = False
							else:
								print ("Costo no valido")
								leer = True
				else:
					print ("Faltan valores")

			vectorBytes += self.tuplaToBytes(tupla)
			i = i + 1
			#print('\n')
		return vectorBytes

	def envioMensajeUDP(self):
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
					message = self.leerMensaje()
					clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
					clientSocket.sendto(message, (serverNameS, serverPortS))
					clientSocket.close()

	def borrarme(self):
		mensaje = bytearray((1).to_bytes(2, byteorder='big'))# cant tuplas
		mensaje += (0).to_bytes(1, byteorder='big')
		fuente = self.tablaAlcanzabilidad.eliminarPrimerFuente()
		#print("Elimine la primer fuente")
		print ("llegue aqui")
		while fuente.puertoFuente != 0:
			clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			clientSocket.sendto(mensaje, (fuente.ipFuente, fuente.puertoFuente))
			clientSocket.close()
			fuente = self.tablaAlcanzabilidad.eliminarPrimerFuente()

	def despligueMenuUDP(self):
		print('Menu principal del modulo de Red UDP: \n'
					'\t1. Enviar un mensaje. \n'
					'\t2. Ver mensajes recibidos. \n'
					'\t3. Imprimir tabla de alcanzabilidad.\n'
					'\t4. Cerrar servidor de mensajes.')
		bandera = True
		while bandera == True:
			taskUsuario = input('Que desea hacer:')
			if taskUsuario == '1':
				self.envioMensajeUDP()
			elif taskUsuario == '2':
				print("\n\n")
				print('Mensajes recibidos:')
				self.mensajesRecibidos.imprimirMensajes()
				print("\n\n")
			elif taskUsuario == '3':
				print("\n\n")
				print('Tabla de alcanzabilidad:')
				self.tablaAlcanzabilidad.imprimirTabla()
				print("\n\n")
			elif taskUsuario == '4':
				bandera = False
				self.borrarme()
				print('Salida.')
				os._exit(1)

			else:
				print('Ingrese opcion valida.')

class ReceptorTCP:
	mensajesRecibidos = MensajesRecibidos()
	tablaAlcanzabilidad = TablaAlcanzabilidad()

	def __init__(self,mensajesRecibidos, tablaAlcanzabilidad):
		self.mensajesRecibidos = mensajesRecibidos
		self.tablaAlcanzabilidad = tablaAlcanzabilidad

	def establecerConexion(self, conexion, addr):
		while True:
			#Recibimos el mensaje, con el metodo recv recibimos datos y como parametro 
			#la cantidad de bytes para recibir
			try:
				recibido = conexion.recv(2048)
			except SocketError:
				print("Conexion Perdida")
				self.tablaAlcanzabilidad.borrarFuenteDesdeAfuera(addr[0],addr[1])
				break

			if(recibido == b''):#Salida para cuando el otro muere antes de mandar el primer mensaje
				print("Conexion Perdida")
				self.tablaAlcanzabilidad.borrarFuenteDesdeAfuera(addr[0],addr[1])
				break

			cantTuplas = int(codecs.encode(recibido[0:2], 'hex_codec'))
			#mensajeSalir = int.from_bytes( recibido[2:3], byteorder='big' )
			#Si el mensaje recibido es la palabra close se cierra la aplicacion
			if cantTuplas == 1 and len(recibido) == 3:
				print("Conexion Terminada")
				self.tablaAlcanzabilidad.borrarFuenteDesdeAfuera(addr[0],addr[1])
				break
			
			mensaje = Mensaje(addr[0],addr[1],recibido)
			self.mensajesRecibidos.guardarMensaje(mensaje)
			self.mensajesRecibidos.imprimirMensaje(mensaje) 
			self.tablaAlcanzabilidad.actualizarTabla(mensaje)
			
		conexion.close()

	def recibir(self,ip,puerto):
		#instanciamos un objeto para trabajar con el socket
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		 
		s.bind((ip,puerto))
		 
		s.listen(5)
		
		while True:
			conexion, addr = s.accept()
			
			thread_servidor = threading.Thread(target=self.establecerConexion, args=(conexion,addr))
			thread_servidor.start()
			print("Conexion recibida")
		
		#Cerramos la instancia del socket cliente y servidor
		s.close()

class ConexionAbierta:

	def __init__(self,ip,puerto,socketEmisorTCP):
		self.socketEmisorTCP = socketEmisorTCP
		self.ip = ip
		self.puerto = puerto

	def enviarMensaje(self,mensaje):
		try:
			sent = self.socketEmisorTCP.send(mensaje)
		except SocketError as e:
				print("ERROR AL ENVIAR EL MENSAJE, Conexion no disponible")
				return False
		else:
			if sent == 0:
				print("ERROR AL ENVIAR EL MENSAJE, Conexion no disponible")
				return False
		return True

	def cerrarConexion(self):
		self.socketEmisorTCP.close()

	def soyLaConexion(self,ip,puerto):
		if self.ip == ip and self.puerto == puerto:
			return True
		
		return False

class EmisorTCP:
	#Objeto para guardar conexiones
	conexiones = list()

	lockConexiones = threading.Lock()

	mensajesRecibidos = MensajesRecibidos()

	tablaAlcanzabilidad = TablaAlcanzabilidad()

	def __init__(self,mensajesRecibidos, tablaAlcanzabilidad):
		self.mensajesRecibidos = mensajesRecibidos
		self.tablaAlcanzabilidad = tablaAlcanzabilidad
		self.conexiones = list()
		self.lockConexiones = threading.Lock()

	#Llamar solo CON candado adquirido
	def imprimirConexionesExistentes(self):
		self.lockConexiones.acquire()
		i = 0;
		largo = len(self.conexiones)
		while i < largo:
			print(self.conexiones[i].ip + " " + str(self.conexiones[i].puerto) )
			i = i + 1
		self.lockConexiones.release()

	#Llamar solo CON candado adquirido
	def hacerConexion(self, ip,puerto):
		#se crea el socket para enviar
		socketEmisorTCP = socket.socket()
		conexion = ConexionAbierta(ip,puerto,socketEmisorTCP)
		#Se establece la conexion con el receptorTCP mediante la ip y el puerto
		try:
			socketEmisorTCP.connect((ip, puerto))
		except SocketError:
			print("Fallo de conexion")
			return False
		else:
			print("Conexion establecida")
			self.conexiones.append(conexion)
			return True

	#Llamar solo CON candado adquirido
	def buscarConexion(self, ip,puerto):
		i = 0;
		largo = len(self.conexiones)
		while i < largo:
			if self.conexiones[i].soyLaConexion(ip,puerto) :
				return i
			i = i + 1
		return -1

	#Llamar solo CON candado adquirido
	def cerrarUnaConexion(self, ip,puerto):
		i = 0;
		largo = len(self.conexiones)
		while i < largo:
			if self.conexiones[i].soyLaConexion(ip,puerto) :
				self.conexiones[i].cerrarConexion()
				self.conexiones.remove(self.conexiones[i])
				break
			i = i + 1

	#Llamar solo CON candado adquirido
	def cerrarConexiones(self):
		while len(self.conexiones) != 0:
			self.conexiones[0].cerrarConexion()
			self.conexiones.remove(self.conexiones[0])

	#NO necesita tener candado
	def tuplaToBytes(self,tupla):
		tupladiv = tupla.split(' ')
		numeroip = tupladiv[0]
		myip = numeroip.split('.')
		bytesmios = bytearray()
		for x in range(0, 4):
			ipnum = int(myip[x])
			bytesmios += (ipnum).to_bytes(1, byteorder='big')
		masc = int(tupladiv[1])
		bytesmios += (masc).to_bytes(1, byteorder='big')
		costo = int(tupladiv[2])
		bytesmios += (costo).to_bytes(3, byteorder='big')
		return bytesmios

	#NO necesita tener candado
	def leerMensaje(self):
		#print('Ingrese la cantidad de tuplas que quiere enviar:')
		entradas = 0
		leerCantTuplas = True
		while leerCantTuplas:
			lectura = input( "Ingrese la cantidad de tuplas: " )
			try:
				entradas = int(lectura)
				leerCantTuplas = False
			except ValueError as e:
				print("Cantidad de tuplas invalido")
				leerCantTuplas = True
		
		vectorBytes = bytearray((entradas).to_bytes(2, byteorder='big'))
		i = 0
		
		while i < entradas:
			#print('Ingrese la tupla:')
			leer = True
			while leer:
				tupla = input("Ingrese una tupla(ip mascara puerto): ")
				tuplaDividida = tupla.split()# tupla.replace(" ", "/",1)
				if len(tuplaDividida) == 3 :
					ipPrueba = tuplaDividida[0] + "/" + tuplaDividida[1]
					try:
						n = ipaddress.ip_network(ipPrueba) 
					except ValueError as e:
						print ("Ip o mascara no valida")
						leer = True
					else:
						leer = False
						try:
							costo = int(tuplaDividida[2]) 
						except ValueError as e:
							print ("Costo no valido")
							leer = True
						else:
							if costo > 0 and costo < 65536:
								leer = False
							else:
								print ("Costo no valido")
								leer = True
				else:
					print ("Faltan valores")

			vectorBytes += self.tuplaToBytes(tupla)
			i = i + 1
			#print('\n')
		return vectorBytes

	#Llamar solo SIN candado adquirido
	def enviarMensaje(self):
		#self.lockConexiones.acquire()
		ip = input("Digite la ip del destinatario: ")
		ipPrueba = ip + "/32"
		try:
			n = ipaddress.ip_network(ipPrueba)
		except ValueError as e:
			print ("Ip no valida")
		else:
			puerto = input("Digite el puerto del destinatario: ")
			try:
				n = int(puerto)
			except ValueError as e:
				print ("Puerto no valido")
			else:
				if n < 0 or n > 65535:
					print ("Puerto no valido")
				else:
					self.lockConexiones.acquire()
					indice = self.buscarConexion(ip,int(puerto))

					if indice == -1:
						exito = self.hacerConexion(ip,int(puerto))
						if exito:
							print("Nueva conexion")
							mensaje = self.leerMensaje()
							respEnvio = self.conexiones[len(self.conexiones)-1].enviarMensaje(mensaje)
							if respEnvio == False:
								self.cerrarUnaConexion(ip,int(puerto))
							if len(mensaje) == 3:
								self.conexiones.pop(len(self.conexiones)-1)
					else:
						print("Conexion existente")
						mensaje = self.leerMensaje()
						respEnvio = self.conexiones[indice].enviarMensaje(mensaje)
						if respEnvio == False:
							self.cerrarUnaConexion(ip,int(puerto))
						if len(mensaje) == 3:
							self.conexiones.pop(indice)
					self.lockConexiones.release()

	#Llamar solo SIN candado adquirido
	def borrarme(self):
		#self.lockConexiones.acquire()
		mensaje = bytearray((1).to_bytes(2, byteorder='big'))# cant tuplas
		mensaje += (0).to_bytes(1, byteorder='big')

		i = 0
		self.lockConexiones.acquire()
		cant = len(self.conexiones)
		while i < cant:
			self.conexiones[i].enviarMensaje(mensaje)
			i = i + 1
		self.cerrarConexiones()
		self.lockConexiones.release()
		return

	#NO necesita tener candado
	def menu(self):#HACER UN WHILE CON UN MENU 
		print('Menu principal del modulo de Red TCP: \n'
					'\t1. Enviar un mensaje. \n'
					'\t2. Ver mensajes recibidos. \n'
					'\t3. Imprimir tabla de alcanzabilidad. \n'
					'\t4. Conexiones existentes. \n'
					'\t5. Cerrar nodo.')
		bandera = True
		while bandera == True:
			taskUsuario = input('Que desea hacer:')
			if taskUsuario == '1':
				self.enviarMensaje()
			elif taskUsuario == '2':
				print("\n\n")
				print('Mensajes recibidos:')
				self.mensajesRecibidos.imprimirMensajes()
				print("\n\n")
			elif taskUsuario == '3':
				print("\n\n")
				print('Tabla de alcanzabilidad:')
				self.tablaAlcanzabilidad.imprimirTabla()
				print("\n\n")
			elif taskUsuario == '5':
				bandera = False
				self.borrarme()
				print('Salida.')
				os._exit(1)
				#proceso_repetorTcp.exit()
			elif taskUsuario == '4':
				print("Conexiones existentes:")
				self.imprimirConexionesExistentes()
			else:
				print('Ingrese una opcion valida.')

class NodoTCP:

	def iniciarNodoTCP(self,ip,puerto):
		
		mensajesRecibidos = MensajesRecibidos()
		tablaAlcanzabilidad = TablaAlcanzabilidad()

		repetorTcp = ReceptorTCP(mensajesRecibidos, tablaAlcanzabilidad)
		proceso_repetorTcp = threading.Thread(target=repetorTcp.recibir, args=(ip,puerto,))
		proceso_repetorTcp.start()

		emisorTcp = EmisorTCP(mensajesRecibidos, tablaAlcanzabilidad)
		proceso_emisorTcp = threading.Thread(target=emisorTcp.menu, args=())
		proceso_emisorTcp.start()


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
					nodoUDP = UDPNode()
					thrdRecibeMensaje = threading.Thread(target = nodoUDP.procRecibeMsg, args = (ip, int(puerto),))
					thrdRecibeMensaje.start()
					thrdRecibeMensaje = threading.Thread(target = nodoUDP.despligueMenuUDP, args = ())
					thrdRecibeMensaje.start()
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