import csv


class CSVTopologia:
	self.listaTuplas = dic()

	def __init__(self, nombrearchivo):
		self.nombrearchivo = nombrearchivo
		llenaDiccionario(self.nombrearchivo);

	def llenaDiccionario(self):
		for line in leearchivo:
			listaTupla = line.split(',')

		idConexion = listaTuplas[0], listaTuplas[1], listaTuplas[2]
		hayKey = self.listaTuplas.get(idConexion)
		otroIpDistancia = listaTuplas[3],listaTuplas[4],listaTuplas[5], listaTuplas[6]

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




