import sys
import random
import subprocess

from CSVNodos import *

class CreadorNodos:

	#Metodo que se encarga de abrir las teminales de los nodos que tiene que crear
	# pathArchivo: direccion del archivo que tiene que leer
	def crearNodos(self, pathArchivo):
		lectorCSV = CSVNodos(pathArchivo)
		ip = lectorCSV.getIP()
		mascara = lectorCSV.getMascara()
		puertos = lectorCSV.getListaPuertos()
		print("Cantidad de puertos leida ",len(puertos))
		for i in puertos:
			pid = subprocess.Popen(args=["gnome-terminal", "--command=python3 NodesTCP-UDP.py creaNodo-intAS " + ip + " " + str(mascara) + " " + str(i)]).pid
			if(pid > 2):
				print(str((ip,mascara,i)) + " creado con exito")
			else:
				print("Error al crear al nodo")

#Metodo que inica el programa para crear nodos
if __name__ == '__main__':
	if len(sys.argv) == 1:
		creador = CreadorNodos()
		creador.crearNodos("/home/christofer/Escritorio/RedesProyecto/10.232.68.72")
	else: 
		print("Faltan parametros, ingrese la direccion del archivo CSV")