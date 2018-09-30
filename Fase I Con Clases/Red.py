import sys
import threading
import socket
import errno
import codecs
import os
import ipaddress

from socket import error as SocketError

class Red:
	def __init__(self,ipFuente,puertoFuente,ipRed, mascaraRed, costo):
		self.ipFuente = ipFuente
		self.puertoFuente = puertoFuente
		self.ipRed = ipRed
		self.mascaraRed = mascaraRed 
		self.costo = costo

	def soyEsaRed(self, ipRed, mascaraRed):
		if ipRed == self.ipRed and mascaraRed == self.mascaraRed:
			return True
		return False

	def soyEsaFuente(self, ipFuente, puertoFuente):
		if ipFuente == self.ipFuente and puertoFuente == self.puertoFuente:
			return True
		return False

	def costoMenor(self, costo):
		if costo < self.costo:
			return True
		return False

	def actualizarRed(self,ipFuente,puertoFuente,ipRed, mascaraRed, costo):
		self.ipFuente = ipFuente
		self.puertoFuente = puertoFuente
		self.ipRed = ipRed
		self.mascaraRed = mascaraRed 
		self.costo = costo