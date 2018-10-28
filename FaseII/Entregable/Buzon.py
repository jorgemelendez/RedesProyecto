import threading
import time

class Buzon:

	def __init__(self):
		self.buzon = dict()
		self.lockBuzon = threading.Lock()

	def meterDatos(self, idConexion, mensaje):
		self.lockBuzon.acquire()
		
		listaMensajes = self.buzon.get(idConexion)
		if listaMensajes is None:
			listaMensajes = list()
			listaMensajes.append(mensaje)
			self.buzon[idConexion] = listaMensajes
		else:
			listaMensajes.append(mensaje)
		
		self.lockBuzon.release()

	#Da el id de la conexion, y le retorna el mensaje recibido para esa conezxion
	def sacarDatos(self, idConexion):
		self.lockBuzon.acquire()

		listaMensajes = self.buzon.get(idConexion)
		if listaMensajes is None:
			mensaje = None
		else:
			if len(listaMensajes) > 0:
				mensaje = listaMensajes.pop(0)
			else:
				mensaje = None

		self.lockBuzon.release()
		return mensaje