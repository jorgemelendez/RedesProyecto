#Modulo basico de todas las comunicaciones de networks en Python.
#Con ella podemos crear los sockets dentro de nuestro programa.
import socket

"""En el nombre del servidor proporcionamos la direccion IP  del servidor o el nombre del host 'google.com
   Si utilizamos un nombre de host una busqueda de DNS se efectuara de manera automatica.'"""
serverName = '10.1.138.83'

"""Ponemos el numero del puerto en el 12000"""
serverPort = 4001


"""Crea el socket cliente, el primer parametro: 
   AD_INET --> Indica que el network que vamos a rabajar esta usando IPv4.
   socke.SOCK_DGRAM --> Indica el tipo de socket que vamos a utilizar en este caso es UDP.

   Cabe resalta que en este caso no estamos especificando el numero de puerto  del socket
   del cliente, este trabajao se lo estamos dejando al sistema opertativo."""
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

"""Permite al usuario ingresar un mensaje que va a querer ser enviado. """
message = input('Input lowercase sentence:')


""""El metodo sendto() adjunta la direccion destino (serverName, serverPort) al mensaje y 
    manda el paquete resultante al socket del proceso llamado clientSocket."""
clientSocket.sendto(message,(serverName, serverPort))

"""Cuando un paquete llega al socket del cliente los datos del paquete son puestos en una
   variable llamda modifiedMessage, la direccion fuente del paquete s pone en la variable
   serverAddress. Esta variable 'serverAddress' contiene ambos la direccion IP del servidor
   y el puerto del servidor.

   El metodo recvfrom toma un buffer de tamanno de 2048 como el input."""
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)

"""Muestra el mensaje."""
print (modifiedMessage)

"""Cierra el socket."""
clientSocket.close()

