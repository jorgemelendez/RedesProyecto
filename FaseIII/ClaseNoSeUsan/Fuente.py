import sys
import threading
import socket
import errno
import codecs
import os
import ipaddress

from socket import error as SocketError

class Fuente:
	def __init__(self,ipFuente,puertoFuente):
		self.ipFuente = ipFuente
		self.puertoFuente = puertoFuente