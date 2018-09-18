#Modulo basico de todas las comunicaciones de networks en Python.
#Con ella podemos crear los sockets dentro de nuestro programa.
import socket
import subprocess
import threading
import multiprocessing


class Mensaje:
		def __init__(self, mensaje=''):
				self.mensaje = mensaje

		def getMensaje(self):
				return self.mensaje

print('UDP (My ip: '+ socket.gethostbyname("www.goole.com") + '):' + '\nEsta recibiendo mensajes en el fondo...\n')

def recibeMensajes():
	serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	serverSocket.bind(('10.1.137.57', 5008))
	while 1:
		message, clientAddress = serverSocket.recvfrom(2048)
		print("Mensaje: " + message)

#serverName = raw_input('Ingrese mi IP: ')
#serverPort = raw_input('Ingrese mi puerto: ')
#thrdRecibeMensaje = threading.Thread(target = recibeMensajes, args = (serverName, serverPort))
#thrdRecibeMensaje.start()
thrdRecibeMensaje = multiprocessing.Process(target = recibeMensajes)
thrdRecibeMensaje.start()
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#test = subprocess.Popen(["clear"])
print ('\n\n')

#Metodo que constantemente esta recibiendo mensajes,

#Metodo que despliega Menu principal de UDP
def despligueMenuUDP():
		print('Menu principal del modulo de Red UDP: \n'
					'\t1. Enviar un mensaje. \n'
					'\t2. Ver mensajes recibidos. \n'
					'\t3. Cerrar servidor de mensajes.')

#Metodo que envia un mensaje mediante UDP al IP + socket que esocgio al inicio.
def envioMensajeUDP():
		message = raw_input('Ingrese el mensaje al que desea enviar: ')
		serverNameS = raw_input('Ingrese el IP del servidor al que quiere enviar el mensaje: ')
		serverPortS = raw_input('Ingrese el puerto al que desea enviar: ')
		message.encode('utf-8')
		clientSocket.sendto(message, (serverNameS, int(serverPortS)))
		print('El mensaje fue enviado.\n')

#Metodo que despliega el Menu para ver los mensajes recibidos.
#def verMensajesMenu():
	# Desplegar menu donde puede ver los mensajes que ha recibido.

despligueMenuUDP()
#thrdRecibeMensaje.join()
bandera = True
while bandera == True:
	taskUsuario = raw_input('Que desea hacer:')
	if taskUsuario == '1':
		envioMensajeUDP()
	elif taskUsuario == '2':
		#Llamar metodo de despligue de verMensajesMenu()
		print('hola')
	elif taskUsuario == '3':
		bandera = False
		print('Se cerrara el menu.')
		clientSocket.close()
		#Falta matar thread que recibe mensajes.
		#thrdRecibeMensaje.join()
		thrdRecibeMensaje.terminate()
		thrdRecibeMensaje.join()
	else:
		print('Ingrese una opcion valida.')
#thrdRecibeMensaje.join()
#Tipo UDP y envio del Mensaje:
