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

			#Pregunta si la mascara y el puerto que ingreso esta correcta.
			mascara1 = int(listaTuplas[1])
			puerto1 = int(listaTuplas[2])

			#El string de conexion para ensennar el mensaje.
			idConexion = listaTuplas[0], mascara1, int(listaTuplas[2])

			#El If funciona para ver si se ignora o se ingresa cada tupla.
			if mascara1 < 2 or mascara1 > 30: 
				print('Se ingoro: ' + idConexion +' .La mascara debe de estar [2,30]')
			else:		
				#Pregunta si el puerto esta entre los rangos. 
				hayKey = self.listaTuplas.get(idConexion)
				
				#Pregunta si la mascara esta entre 2-30, si se exede pone el mayor rango.
				mascara2 = int(listaTuplas[4])
				puerto2 = int(listaTuplas[5])
				distancia = int(listaTuplas[6])

				otroIpDistancia = listaTuplas[3],mascara2,puerto2, distancia

				if mascara2 < 2 or mascara2 > 30:
					print('Se ignoro agregar ' + str(otroIpDistancia) + ' a la conexion ' + str(idConexion) +' . La mascara debe estar entre [2,30]')

				elif distancia < 20 or distancia > 100:
					print ('Se ignoro agregar ' + str(otroIpDistancia) + ' a la conexion ' + str(idConexion) +' . La distancia debe estar entre [20,100]')
				else:
					if hayKey is None:
						listaDireccion = list()
						listaDireccion.append(otroIpDistancia)
						self.listaTuplas[idConexion] = listaDireccion
					else:
						listaDireccion.append(otroIpDistancia)


	def getDiccionario(self):
		return self.listaTuplas