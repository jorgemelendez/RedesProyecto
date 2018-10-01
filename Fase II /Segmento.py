class Segmento:

	def __init__(self,puertoOrigen,puertoDestino,secuencia,reconocimiento,indicadores, datos):
		self.puertoOrigen = puertoOrigen #2 bytes
		self.puertoDestino = puertoDestino #2 bytes
		#self.secuencia = secuencia #4 bytes
		self.reconocimiento = reconocimiento #4 bytes
		self.indicadores = indicadores #1 bytes
		self.datos = datos

	def tipoSegmento(self):
		if indicadores == 8: #1000
			print("Indica que es un ACK de respuesta al paquete que recibio, en este caso el numero de secuencia y reconocimiento")
		elif indicadores == 9:#1001
			print("Indica que es un ACK de respuesta a fin de conexion")
		elif indicadores == 10:#1010
			print("Indica que es un ACK de respuesta a inicio de conexion")
		elif indicadores == 0: #0000
			print("Indica que es un NACK de respuesta al paquete recibido, en este caso el numero de secuencia y reconocimiento")

def segmentarArchivo(archivo, MSS):#MSS es el numero macimo de bytes que se quiere que tenga cada paquete
	lista = list()
	i = 0
	largo = len(archivo)
	while i < largo:
		temp = ""
		while i < largo: #Podria hacerse con [#:#] PERO NO SE QUE PASA EN EL CASO DE QUE LA ULTIMO SEPARACION SEA MENOR CANTIDAD A LO QUE ESPERABA
			temp += str.encode(archivo[i])
			i = i + 1
		lista.append( temp )
		i = i + 1
	return lista

#tipoMensaje = 8, Indica que es un ACK de respuesta al paquete que recibio, en este caso el numero de secuencia y reconocimiento")
#tipoMensaje = 9,Indica que es un ACK de respuesta a fin de conexion")
#tipoMensaje = 10,Indica que es un ACK de respuesta a inicio de conexion")
#tipoMensaje = 0,Indica que es un NACK de respuesta al paquete recibido, en este caso el numero de secuencia y reconocimiento")
def armarPaq(puertoOrigen,puertoDestino,secuencia,reconocimiento, tipoMensaje, datos):
	resp = bytearray()
	resp += (puertoOrigen).to_bytes(2, byteorder='big')
	resp += (puertoDestino).to_bytes(2, byteorder='big')
	resp += (reconocimiento).to_bytes(4, byteorder='big')
	resp += (tipoMensaje).to_bytes(1, byteorder='big')
	resp += str.encode(datos)
	#print (len(resp))


if __name__ == '__main__':
	resp = segmentarArchivo("hola como esta todos, yo estoy bien aburrido con esta mierda de materia de U", 8)
	i = 0
	largo = len(resp)
	while i < largo:
		print(resp[i])
		i = i + 1

	#armarPaq(128, 128, 10, 10, 8, "Hola como estan")