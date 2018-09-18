import sys
import multiprocessing
import socket
import errno
import codecs
from socket import error as SocketError

class Mensaje:
	def __init__(self,ip,puerto,mensaje):
		self.ip = ip
		self.puerto = puerto
		self.mensaje = mensaje

class ReceptorTCP:
	mensajesRecibidos = list()
	def guardarMensaje(self,mensaje):
		self.mensajesRecibidos.append(mensaje)

	def imprimirMensaje(self, mensaje):
		ip = mensaje.ip
		puerto = mensaje.puerto
		bytesMensaje = mensaje.mensaje

		cantTuplas = int(codecs.encode(bytesMensaje[0:2], 'hex_codec'))
		i = 0
		print("IPf = " + str(ip) + " Puerto = " + str(puerto) + " dice : ")
		while i < cantTuplas:
			ipA = codecs.encode(bytesMensaje[(i*8)+2:(i*8)+3], 'hex_codec')
			ipB = codecs.encode(bytesMensaje[(i*8)+3:(i*8)+4], 'hex_codec')
			ipC = codecs.encode(bytesMensaje[(i*8)+4:(i*8)+5], 'hex_codec')
			ipD = codecs.encode(bytesMensaje[(i*8)+5:(i*8)+6], 'hex_codec')
			mascara = codecs.encode(bytesMensaje[(i*8)+6:(i*8)+7], 'hex_codec')
			costo = codecs.encode(bytesMensaje[(i*8)+7:(i*8)+10], 'hex_codec')
			print( str(ipA) + "." + str(ipB) + "." + str(ipC) + "." + str(ipD) + " " + str(mascara) + " " + str(costo) )
			i = i + 1

	def imprimirMensajes(self):
		i = 0
		largo = len(self.mensajesRecibidos)
		while i < largo:
			self.imprimirMensaje( self.mensajesRecibidos[i] )
			i = i + 1

	def establecerConexion(self, conexion, addr):
		while True:
			#Recibimos el mensaje, con el metodo recv recibimos datos y como parametro 
			#la cantidad de bytes para recibir
			try:#EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE
				#aqui hay problemas porque nos se maneja la excepcion de que se pierda la conexion
				print("Esperando mensaje")
				recibido = conexion.recv(1024)
				if(recibido == b''):#Salida para cuando el otro muere antes de mandar el primer mensaje
					break
			except SocketError:
				break
			#Si el mensaje recibido es la palabra close se cierra la aplicacion
			if recibido == "close":
				break
		 
			#Si se reciben datos nos muestra la IP y el mensaje recibido
			print (str(addr[0]) + " dice: ")
			
			#print(codecs.encode(recibido[0:2], 'hex_codec'))
			#print(codecs.encode(recibido[2:3], 'hex_codec'))
			#print(codecs.encode(recibido[3:4], 'hex_codec'))
			#print(codecs.encode(recibido[4:5], 'hex_codec'))
			#print(codecs.encode(recibido[5:6], 'hex_codec'))
			#print(codecs.encode(recibido[6:7], 'hex_codec'))
			#print(codecs.encode(recibido[7:10], 'hex_codec'))

			mensaje = Mensaje(addr[0],addr[1],recibido)
			self.guardarMensaje(mensaje)
			self.imprimirMensaje(mensaje) 
			
			#Devolvemos el mensaje al cliente
			try:
				conexion.send(recibido)
			except SocketError as e:
				print(e)
				break
		conexion.close()

	def recibir(self,ip,puerto):
		#instanciamos un objeto para trabajar con el socket
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		 
		#Con el metodo bind le indicamos que puerto debe escuchar y de que servidor esperar conexiones
		#Es mejor dejarlo en blanco para recibir conexiones externas si es nuestro caso
		s.bind((ip,puerto))
		 
		#Aceptamos conexiones entrantes con el metodo listen, y ademas aplicamos como parametro
		#El numero de conexiones entrantes que vamos a aceptar
		s.listen(5)
		
		j = 0
		while j < 2:
			j = j + 1
			#Instanciamos un objeto sc (socket cliente) para recibir datos, al recibir datos este 
			#devolvera tambien un objeto que representa una tupla con los datos de conexion: IP y puerto
			conexion, addr = s.accept()
			
			thread_servidor = multiprocessing.Process(target=self.establecerConexion(conexion,addr))
			thread_servidor.start()
			print("Conexion recibida")
		 
		
		self.imprimirMensajes()
		print("Adios.!!!")
		thread_servidor.terminate()
		thread_servidor.join()
		 
		#Cerramos la instancia del socket cliente y servidor
		s.close()

if __name__ == '__main__':
	tcp = ReceptorTCP()
	tcp.recibir("25.8.85.180",5000)