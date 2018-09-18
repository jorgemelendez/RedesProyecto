import sys
import threading
import socket

class ConexionAbierta:

	def __init__(self,ip,puerto,socketEmisorTCP):
		self.socketEmisorTCP = socketEmisorTCP
		self.ip = ip
		self.puerto = puerto

	def enviarMensaje(self,mensaje):
		self.socketEmisorTCP.send(mensaje)

	def cerrarConexion(self):
		self.socketEmisorTCP.close()

	def soyLaConexion(self,ip,puerto):
		if self.ip == ip and self.puerto == puerto:
			return True
		
		return False

class EmisorTCP:
	#Objeto para guardar conexiones
	conexiones = list()

	def hacerConexion(self, ip,puerto):
		#se crea el socket para enviar
		socketEmisorTCP = socket.socket()
		conexion = ConexionAbierta(ip,puerto,socketEmisorTCP)
		#Se establece la conexion con el receptorTCP mediante la ip y el puerto
		socketEmisorTCP.connect((ip, puerto))
		print("Conectado al servidor")
		self.conexiones.append(conexion)

	#retorna el numero del indice de la conexion si lo encuentra, sino entonces retorna -1
	def buscarConexion(self, ip,puerto):
		i = 0;
		largo = len(self.conexiones)
		while i < largo:
			if self.conexiones[i].soyLaConexion(ip,puerto) :
				return i
			i = i + 1
		return -1

	def cerrarUnaConexion(self, ip,puerto):
		i = 0;
		largo = len(self.conexiones)
		while i < largo:
			if self.conexiones[i].soyLaConexion(ip,puerto) :
				self.conexiones[i].cerrarConexion()
				self.conexiones.remove(self.conexiones[i])
				break
			i = i + 1

	def cerrarConexiones(self):
		while len(self.conexiones) != 0:
			self.conexiones[0].cerrarConexion()
			self.conexiones.remove(self.conexiones[0])

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
	    print(bytesmios)
	    return bytesmios

	def leerMensaje(self):
		entradas = input()
		vectorBytes = bytearray((int(entradas)).to_bytes(2, byteorder='big'))
		i = 0
		while i < int(entradas):
			tupla = input()
			vectorBytes += self.tuplaToBytes(tupla)
			i = i + 1
		return vectorBytes

	def enviarMensaje(self):
		ip = input("Digite la ip del destinatario: ")
		puerto = input("Digite el puerto del destinatario: ")

		indice = self.buscarConexion(ip,int(puerto))

		if indice == -1:
			print("Voy a crear la conexion")
			self.hacerConexion(ip,int(puerto))
			print("Nueva conexion echa")
			mensaje = self.leerMensaje()
			#mensaje = input("Mensaje a enviar: ")
			self.conexiones[len(self.conexiones)-1].enviarMensaje(mensaje)
		else:
			print("Voy a usar una conexion existente")
			mensaje = self.leerMensaje()
			#mensaje = input("Mensaje a enviar: ")
			self.conexiones[indice].enviarMensaje(mensaje)




if __name__ == '__main__':
	tcp = EmisorTCP()

	#Este objeto lo tiene emisor

	tcp.enviarMensaje()

	tcp.enviarMensaje()

	tcp.cerrarConexiones()



	