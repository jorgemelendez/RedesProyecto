import csv


class CSVTopologia:

	def __init__(self, nombrearchivo):
		self.listaTuplas = dict()
		self.nombrearchivo = nombrearchivo
		self.llenaDiccionario()

	def llenaDiccionario(self):
		leearchivo = open(self.nombrearchivo,"r")
		for line in leearchivo:
			listaTuplas = line.split(',')

			idConexion = listaTuplas[0], int(listaTuplas[1]), int(listaTuplas[2])
			hayKey = self.listaTuplas.get(idConexion)
			otroIpDistancia = listaTuplas[3],int(listaTuplas[4]),int(listaTuplas[5]), int(listaTuplas[6])

			if hayKey is None:
				listaDireccion = list()
				listaDireccion.append(otroIpDistancia)
				self.listaTuplas[idConexion] = listaDireccion
			else:
				listaDireccion.append(otroIpDistancia)


	def getDiccionario(self):
		return self.listaTuplas




