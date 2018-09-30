import sys
import threading
import socket
import errno
import codecs
import os
import ipaddress

from socket import error as SocketError

class Mensaje:
	def __init__(self,ip,puerto,mensaje):
		self.ip = ip
		self.puerto = puerto
		self.mensaje = mensaje