#Modulo basico de todas las comunicaciones de networks en Python.
#Con ella podemos crear los sockets dentro de nuestro programa.

import socket
import subprocess
import threading


class Mensaje:
    def __init__(self, mensaje=''):
        self.mensaje = mensaje

    def getMensaje(self):
        return self.mensaje

print('UDP (My ip: ' + socket.gethostbyname(socket.gethostname()) + '}:' +
      '\nEsta recibiendo mensajes en el fondo...\n')

taskUsuario = ""
serverName = input('Ingrese el nombre del servidor que quiere utilizar: ')
serverPort = input('Ingrese el numero de puerto a utilizar: ')
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#test = subprocess.Popen(["clear"])
print ('\n\n')

#Metodo que despliega Menu principal de UDP
def despligueMenuUDP():
    print('Menu principal del modulo de Red UDP: \n'
          '\t1. Enviar un mensaje. \n'
          '\t2. Ver mensajes recibidos. \n'
          '\t3. Cerrar servidor de mensajes.')

#Metodo que envia un mensaje mediante UDP al IP + socket que esocgio al inicio.
def envioMensajeUDP():
    message = input('Ingrese el mensaje que desea enviar: ')
    clientSocket.sendto(message, (serverName, serverPort))
    print('El mensaje fue enviado.\n')

#Metodo que despliega el Menu para ver los mensajes recibidos.
#def verMensajesMenu():
  # Desplegar menu donde puede ver los mensajes que ha recibido.

despligueMenuUDP()
taskUsuario = input('Que desea hacer:')

bandera = True
while bandera == True:
  if taskUsuario == '1':
    envioMensajeUDP()
    bandera = False
  elif taskUsuario == '2':
    #Llamar metodo de despligue de verMensajesMenu()
    bandera = False
  elif taskUsuario == '3':
    bandera = False
    print('Se cerrara el menu.')
    clientSocket.close()
  else:
    print('Ingrese una opcion valida.')
#Tipo UDP y envio del Mensaje:







