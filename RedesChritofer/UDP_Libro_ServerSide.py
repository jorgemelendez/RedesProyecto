#Modulo basico de todas las comunicaciones de networks en Python.
#Con ella podemos crear los sockets dentro de nuestro programa.
import socket


"""En el nombre del servidor proporcionamos la direccion IP  del servidor o el nombre del host 'google.com
   Si utilizamos un nombre de host una busqueda de DNS se efectuara de manera automatica.'"""
serverPort = 12000



"""Crea el socket cliente, el primer parametro: 
   AD_INET --> Indica que el network que vamos a trabajar esta usando IPv4.
   socke.SOCK_DGRAM --> Indica el tipo de socket que vamos a utilizar en este caso es UDP.

   Cabe resalta que en este caso no estamos especificando el numero de puerto  del socket
   del cliente, este trabajao se lo estamos dejando al sistema opertativo."""
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

"""Asigna el numero de puerto 12000 al socket del servidor. Cuando alguien mande un paquete
   al puerto 12000 al IP del servidor, el paquete se va a direccionar a este socket."""
serverSocket.bind(('10.1.138.18', serverPort))


print ("The server is ready to recieve")

"""Entre en while loop  """
while 1:
	message, clientAddress= serverSocket.recvfrom(2048)
	#clientAddress = serverSocket.recvfrom(2048)
	modifiedMessage = message.upper()
	serverSocket.sendto(modifiedMessage, clientAddress)