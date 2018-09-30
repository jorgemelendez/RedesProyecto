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

def iniciarNodoUDP(self,ip,puerto):
	mensajesRecibidos= MensajesRecibidos()
	tablaAlcanzabilidad = TablaAlcanzabilidad()

	repetorUDP = ReceptorUDP(mensajesRecibidos, tablaAlcanzabilidad)
	proceso_repetorUDP = threading.Thread(target=repetorUDP.recibir, args=(ip,puerto,))
	proceso_repetorUDP.start()

	emisorUDP = EmisorUDP(mensajesRecibidos, tablaAlcanzabilidad)
	proceso_emisorUDP = threading.Thread(target=emisorUDP.menu, args=())
	proceso_emisorUDP.start()

