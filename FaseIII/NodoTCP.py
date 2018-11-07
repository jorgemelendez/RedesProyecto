import sys
import threading
import socket
import errno
import codecs
import os
import ipaddress

from socket import error as SocketError
from MensajesRecibidos import *
from TablaAlcanzabilidad import *
from ReceptorTCP import *
from EmisorTCP import *

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