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

	def leerMensaje(self):
		lectura = list()
		entradas = input()
		lectura.append(entradas)
		i = 0
		while i < entradas
			tupla = input()
			lectura.append(tupla)
			i = i + 1
		return lectura

	def enviarMensaje(self):
		ip = input("Digite la ip del destinatario: ")
		puerto = input("Digite el puerto del destinatario: ")

		indice = self.buscarConexion(ip,int(puerto))

		if indice == -1:
			print("Voy a crear la conexion")
			self.hacerConexion(ip,int(puerto))
			print("Nueva conexion echa")
			mensaje = leerMensaje()
			#mensaje = input("Mensaje a enviar: ")
			self.conexiones[len(self.conexiones)-1].enviarMensaje(mensaje)
		else:
			print("Voy a usar una conexion existente")
			mensaje = leerMensaje()
			#mensaje = input("Mensaje a enviar: ")
			self.conexiones[indice].enviarMensaje(mensaje)


class receptorTCP:
	
	def recibir():
		#se crea el socket para recibir
		socketReceptorTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#Indicamos en que puerto debe escucha y la ip de este nodo
		socketReceptorTCP.bind((ip, int(puerto)))
		#Indicamos el numero de conexiones entrantes que vamos a aceptar
		socketReceptorTCP.listen(5)

		while True:
			#Objeto para recibir datos,cuando este recibe da otro objeto con IP y puerto
			conexionEstablecida, addr = socketReceptorTCP.accept()
			print("Conexion establecida") 
			#Ciclo para que se mantenga escuchando
			continuarConexion = True
			while continuarConexion:
			    #llamado a metodo para recibimos datos y como parametrola cantidad de bytes para recibir(RRRRRRRRREVISAR SI CON ESA CANTIDAD DE PUEDE)
			    try:
				    recibido = conexionEstablecida.recv(1024)#HAY QUE AGARRAR EL ERROR DE CUANDO SE DESCONECTA
			    except SocketError as e:
			        if e.errno != errno.ECONNRESET:
			            print("Conexion perdida")
			            break
			    #Si el mensaje recibido es la palabra close se cierra la aplicacion
			    if recibido == "close":#VER CUAL ES LA CONDICION PARA CERRAR LA CONEXION
			        continuarConexion = False
			        #AQUI VA EL CODIGO PARA CERRAR LA CONEXION
			 
			    #Si se reciben datos nos muestra la IP y el mensaje recibido, CREO QUE NO HAY QUE IMPRIMIRLO
			    print (str(addr[0]) + " dice: " +  str(recibido.decode()))
			    #AQUI SE DEBE GUARDAR EL MENSAJE EN LA TABLA DE ALCANZABILIDAD
			 	

			    #Devolvemos el mensaje al cliente
			    #conexionEstablecida.send(recibido)

			print("Adios.!!!")
			 
			#Cerramos la conexion
			conexionEstablecida.close()
		#Cerramos el socket, Creo que deberia haber un while antes del que esta que dentro 
		#tenga ese, para asi cerrar la conexion pero no el socket
		socketReceptorTCP.close()

if __name__ == '__main__':
	tcp = EmisorTCP()

	#Este objeto lo tiene emisor

	tcp.enviarMensaje()

	tcp.enviarMensaje()

	tcp.cerrarConexiones()



	