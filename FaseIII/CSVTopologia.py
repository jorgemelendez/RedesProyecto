import csv


class CSVTopologia:
	self.listaTuplas = dic()

	def __init__(self, nombrearchivo):
		self.nombrearchivo = nombrearchivo
		llenaDiccionario(self.nombrearchivo);

	def llenaDiccionario(self):
		for line in leearchivo:
			listaTupla = line.split(',')

		idConexion = listaTuplas[0], int(listaTuplas[1]), int(listaTuplas[2])
		hayKey = self.listaTuplas.get(idConexion)
		otroIpDistancia = listaTuplas[3],int(listaTuplas[4]),int(listaTuplas[5]), int(listaTuplas[6])

		if hayKey is None:
			listaDireccion = list()
			listaDireccion.append()
			self.listaTuplas[idConexion] = listaDireccion
		else
			listaDireccion.append

		if listaMensajes is None:
			listaMensajes = list()
			listaMensajes.append(otroIpDistancia)
			self.buzon[idConexion] = listaMensajes
		else:
			listaMensajes.append(otroIpDistancia)


	def getDiccionario(self):
		return listaTuplas




