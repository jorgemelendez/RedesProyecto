import sys
import random
import subprocess

from CSVNodos import *

class CreadorNodos:

	#IP mandado como una string
	#Lista de numeros de puertos
	def crearNodos(self, pathArchivo):
		lectorCSV = CSVNodos(pathArchivo)
		ip = lectorCSV.getIP()
		puertos = lectorCSV.getListaPuertos()

		cantidad = len(puertos)
		for i in range(cantidad):
			pid = subprocess.Popen(args=["gnome-terminal", "--command=python3 NodesTCP-UDP.py creaNodo-intAS " + ip + " " + str(puertos[i])]).pid
			if(pid > 2):
				print("Creado con exito")
			else:
				print("Error al crear al nodo")


if __name__ == '__main__':
	if len(sys.argv) == 1:
		creador = CreadorNodos()
		creador.crearNodos("/home/christofer/Escritorio/RedesProyecto/10.232.68.72")
	else: 
		print("Faltan parametros, ingrese la direccion del archivo CSV")