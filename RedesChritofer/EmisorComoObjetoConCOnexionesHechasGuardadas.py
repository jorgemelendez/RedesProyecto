import sys
import threading
import socket

class ConexionAbierta:

	def __init__(self,ip,puerto,socketEmisorTCP):
		self.socketEmisorTCP = socketEmisorTCP
		self.ip = ip
		self.puerto = puerto

	def enviarMensaje(self,mensaje):
		self.socketEmisorTCP.send(bytes(mensaje.encode()))

	def cerrarConexion(self):
		self.socketEmisorTCP.close()

	def soyLaConexion(self,ip,puerto):
		if self.ip == ip and self.puerto == puerto:
			return True
		
		return False

class EmisorTCP:
	def hacerConexion(self, ip,puerto):
		#se crea el socket para enviar
		socketEmisorTCP = socket.socket()
		conexion = ConexionAbierta(ip,puerto,socketEmisorTCP)
		#AQUI DEBERIAMOS PREGUNTAR SI YA EXISTE LA CONEXION, PARA USAR LA EXISTENTE
		#Se establece la conexion con el receptorTCP mediante la ip y el puerto
		socketEmisorTCP.connect((ip, puerto))
		print("Conectado al servidor")
		conexiones.append(conexion)

	#retorna el numero del indice de la conexion si lo encuentra, sino entonces retorna -1
	def buscarConexion(self, ip,puerto):
		i = 0;

		largo = len(conexiones)

		while i < largo:
			if conexiones[i].soyLaConexion(ip,puerto) :
				return i
			i = i + 1
		return -1

	def cerrarUnaConexion(self, ip,puerto):
		i = 0;
		largo = len(conexiones)
		while i < largo:
			if conexiones[i].soyLaConexion(ip,puerto) :
				conexiones[i].cerrarConexion()
				conexiones.remove(conexiones[i])
			i = i + 1

	def cerrarConexiones(self):
		i = 0;
		largo = len(conexiones)
		while i < largo:
			conexiones[i].cerrarConexion()
			conexiones.remove(conexiones[i])
			i = i + 1

	def enviarMensaje(self):
		ip = input("Digite la ip del destinatario: ")
		puerto = input("Digite el puerto del destinatario: ")

		indice = self.buscarConexion(ip,int(puerto))

		if indice == -1:
			print("Voy a crear la conexion")
			self.hacerConexion(ip,int(puerto))
			print("Nueva conexion echa")
			mensaje = input("Mensaje a enviar: ")
			conexiones[len(conexiones)-1].enviarMensaje(mensaje)
		else:
			print("Voy a usar una conexion existente")
			mensaje = input("Mensaje a enviar: ")
			conexiones[indice].enviarMensaje(mensaje)

if __name__ == '__main__':
	tcp = EmisorTCP()

	conexiones = list()

	tcp.enviarMensaje()

	tcp.enviarMensaje()

	tcp.enviarMensaje()
	tcp.enviarMensaje()
	tcp.enviarMensaje()
	tcp.enviarMensaje()

	tcp.cerrarConexiones()



	