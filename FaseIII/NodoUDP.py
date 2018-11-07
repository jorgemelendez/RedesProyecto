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
from ReceptorUDP import *
from EmisorUDP import *

class NodoUDP:
	def iniciarNodoUDP(self, ip, puerto):
		mensajesRecibidos= MensajesRecibidos()
		tablaAlcanzabilidad = TablaAlcanzabilidad()

		receptorUDP = ReceptorUDP(mensajesRecibidos, tablaAlcanzabilidad)
		proceso_receptorUDP = threading.Thread(target=receptorUDP.procRecibeMsg, args=(ip,puerto,))
		proceso_receptorUDP.start()

		emisorUDP = EmisorUDP(mensajesRecibidos, tablaAlcanzabilidad)
		proceso_emisorUDP = threading.Thread(target=emisorUDP.despligueMenuUDP, args=())
		proceso_emisorUDP.start()

		