import sys


if __name__ == '__main__':
	print ("Número de parámetros: ", len(sys.argv) )
	print ("Lista de argumentos: ", sys.argv )
	if len(sys.argv) == 4:
		print (sys.argv[1] + " " + sys.argv[2] + " " + sys.argv[3])