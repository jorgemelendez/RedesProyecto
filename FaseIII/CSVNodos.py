import csv

class CSVNodos:
	puerto =list()

	def __init__(self, nombreDeArchivo):
		self.nombreDeArchivo = nombreDeArchivo
		self.leerArchivo()

	def leerArchivo(self):
		leearchivo = open(self.nombreDeArchivo, "r")
		self.ipMia = leearchivo.readline()
		print(self.ipMia)
		self.mascara = int(leearchivo.readline())
		for line in leearchivo:
			self.puerto.append(int(line))

	def getIP(self):
		return self.ipMia

	def getMascara(self):
		return self.mascara

	def getListaPuertos(self):
		return self.puerto

if __name__ == '__main__':
	var1 = input('Direccion de Archivo')
	var2 = CSVNodos(var1)
	print(var2.getIP())
	print(var2.getMascara())
	print(var2.getListaPuertos())

		

