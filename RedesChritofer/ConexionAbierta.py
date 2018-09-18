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



if __name__ == '__main__':
	ip = input("Digite la ip del destinatario: ")
	puerto = input("Digite el puerto del destinatario: ")
	#se crea el socket para enviar
	socketEmisorTCP = socket.socket()
	conexion = ConexionAbierta(ip,int(puerto),socketEmisorTCP)
	#AQUI DEBERIAMOS PREGUNTAR SI YA EXISTE LA CONEXION, PARA USAR LA EXISTENTE
	#Se establece la conexion con el receptorTCP mediante la ip y el puerto
	socketEmisorTCP.connect((ip, int(puerto)))
	print("Conectado al servidor")
	
	#SE DEBE PREGUNTAR LA CANTIDAD DE TUPLAS(N)
	#Creamos el ciclo para leer las n tuplas
	#while True:
		#pedimos y leermos la IP, la pasamos numeros para que entre en 4 byte
		#pedimos y leermos la mascara, la pasamos numeros para que entre en 1 byte
		#pedimos y leermos el costo, la pasamos numeros para que entre en 2 byte
		#en cada iteracion concatenamos los bytes y los concatenamos a las iteraciones anteriores
		
	    #Instanciamos una entrada de datos para que el cliente pueda enviar mensajes
	mensaje = input("Mensaje a enviar: ")
	 
	    #Con la instancia del objeto servidor (socketEmisorTCP) y el metodo send, enviamos el mensaje introducido
	socketEmisorTCP.send(bytes(mensaje.encode()))
	 
	    
	 
	#Imprimimos la palabra Adios para cuando se cierre la conexion
	print ("Mensaje enviado.")
	 
	#Cerramos la instancia del objeto servidor
	

	mensaje2 = input("Mensaje a enviar: ")
	conexion.enviarMensaje(mensaje2)
	if conexion.soyLaConexion(ip,int(puerto)):
		conexion.cerrarConexion()