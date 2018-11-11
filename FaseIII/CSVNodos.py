import csv

class CSVNodos:

	#Constructor
	#nombreDeArchivo: direccion del archivo CSV a leer
	def __init__(self, nombreDeArchivo):
		self.puerto =list()
		self.nombreDeArchivo = nombreDeArchivo
		self.leerArchivo()

	#Metodo que le encarga de leer el archivo de los nodos que hay que arrancar
	def leerArchivo(self):
		leearchivo = open(self.nombreDeArchivo, "r")
		self.ipMia = leearchivo.readline()
		print(self.ipMia)
		self.mascara = int(leearchivo.readline())
		for line in leearchivo:
			self.puerto.append(int(line))

	#Funcion que retorna la ip que van a tener estos nodos a arrancar
	def getIP(self):
		return self.ipMia

	#Funcion que retorna la mascara de los nodos a arrancar
	def getMascara(self):
		return self.mascara

	#Funcion que retorna una lista de los puertos que van a tener los nodos a arrancar
	def getListaPuertos(self):
		return self.puerto