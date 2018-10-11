import threading
class Bitacora:
	def __init__(self, direccionDelArchivo):
		self.archivo = open(direccionDelArchivo, "w+")
		self.lockBitacora = threading.Lock()

	def escribir(self, texto):
		self.lockBitacora.acquire()
		self.archivo.write(texto + "\n")
		self.lockBitacora.release()

	def terminar(self):
		self.lockBitacora.acquire()
		self.archivo.close()
		self.lockBitacora.release()
