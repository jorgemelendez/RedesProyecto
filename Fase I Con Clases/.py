import sys
import threading
import socket
import errno
import codecs
import os
import ipaddress
from socket import error as SocketError

class UDPNode:
	mensajesRecibidos= MensajesRecibidos()
	tablaAlcanzabilidad = TablaAlcanzabilidad()

	
