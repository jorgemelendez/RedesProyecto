
def segmentarArchivo(archivo, MSS):#MSS es el numero macimo de bytes que se quiere que tenga cada paquete
	lista = list()
	i = 0
	largo = len(archivo)
	while i < largo:
		lista.append( archivo[i:i+MSS] )
		i = i + MSS
	return lista


def archivoToString(direccion):
	archivo = open(direccion, 'rb')#Leer en binario
	contenido = archivo.read();
	archivo.close  # Cierra archivo
	return contenido
