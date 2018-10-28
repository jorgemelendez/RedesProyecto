import sys
import time
import socket
import threading
import datetime
import os
from random import randrange

class BanderaFin:
	def __init__(self, bandera):
		self.bandera = bandera
		self.lockBandera = threading.Lock()

	def leerBandera(self):
		self.lockBandera.acquire()
		retorno = self.bandera
		self.lockBandera.release()
		return retorno

	def modificarBandera(self,bandera):
		self.lockBandera.acquire()
		self.bandera = bandera
		self.lockBandera.release()		
