import csv


class CSVTopologia:

	def __init__(self, nombrearchivo):
		self.dicNodos = dict()
		self.nombrearchivo = nombrearchivo
		self.llenaDiccionario()

	def llenaDiccionario(self):
		leearchivo = open(self.nombrearchivo,"r")
		for line in leearchivo:
			tupla = line.split(',') #Tupla es (ip1, mascara1, puerto1, ip2, mascara2, puerto2, distancia)
			#Saca los datos del nodo de salida
			ip1 = tupla[0]
			mascara1 = int(tupla[1])
			puerto1 = int(tupla[2])
			#Saca los datos del nodo vecino
			ip2 = tupla[3]
			mascara2 = int(tupla[4])
			puerto2 = int(tupla[5])
			#Saca la distancia entre los nodos
			distancia = int(tupla[6])
			#Llave para el diccionario
			nodoId = ip1, mascara1, puerto1
			#Id del vecino y distancia, este es el valor del diccionario (ip, mascara, puerto, distancia)
			vecinoIdDistancia = ip2, mascara2, puerto2, distancia
			vecinoId = ip2, mascara2, puerto2

			#Revisa que las mascaras son un valor valido
			if mascara1 < 2 or mascara1 > 30: 
				print('Se ingora ' + nodoId +' porque la mascara debe de estar en [2,30]')
			elif mascara2 < 2 or mascara2 > 30:
				print("Se ingora " + nodoId +" porque la mascara del vecino " + str(vecinoId) + " debe de estar en [2,30]")
			elif distancia < 20 or distancia > 100:
				print("Se ingora " + nodoId +" --> " + str(vecinoId) + " porque la distancia debe estar en [20,100]")
			else:
				#print("Nodo salida " + str(nodoId))
				#print("Nodo llegada " + str(vecinoIdDistancia))
				#Pide los vecinos del nodo
				listaVecinos = self.dicNodos.get(nodoId)

				if listaVecinos is None:
					#print("No tenia vecinos")
					listaVecinos = list()
					listaVecinos.append(vecinoIdDistancia)
					self.dicNodos[nodoId] = listaVecinos
				else:
					#print("Tenia vecinos")
					listaVecinos.append(vecinoIdDistancia)
				#print(listaVecinos)


	def getDiccionario(self):
		return self.dicNodos