import sys
import threading
import socket


def receptorTCP(ip,puerto):
	#se crea el socket para recibir
	socketReceptorTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#Indicamos en que puerto debe escucha y la ip de este nodo
	socketReceptorTCP.bind((ip, int(puerto)))
	#Indicamos el numero de conexiones entrantes que vamos a aceptar
	socketReceptorTCP.listen(5)
	#Objeto para recibir datos,cuando este recibe da otro objeto con IP y puerto
	conexionEstablecida, addr = socketReceptorTCP.accept()
	print("receptorTCP funcionando correctamente") 
	#Ciclo para que se mantenga escuchando
	while True:
	    #llamado a metodo para recibimos datos y como parametrola cantidad de bytes para recibir(RRRRRRRRREVISAR SI CON ESA CANTIDAD DE PUEDE)
	    recibido = conexionEstablecida.recv(1024)#HAY QUE AGARRAR EL ERROR DE CUANDO SE DESCONECTA
	    #Si el mensaje recibido es la palabra close se cierra la aplicacion
	    if recibido == "close":#VER CUAL ES LA CONDICION PARA CERRAR LA CONEXION
	        borrar = 0
	        #AQUI VA EL CODIGO PARA CERRAR LA CONEXION
	 
	    #Si se reciben datos nos muestra la IP y el mensaje recibido, CREO QUE NO HAY QUE IMPRIMIRLO
	    print (str(addr[0]) + " dice: " +  str(recibido.decode()))
	    #AQUI SE DEBE GUARDAR EL MENSAJE EN LA TABLA DE ALCANZABILIDAD
	 	

	    #Devolvemos el mensaje al cliente
	    #conexionEstablecida.send(recibido)

	print("Adios.!!!")
	 
	#Cerramos la conexion
	conexionEstablecida.close()
	#Cerramos el socket, Creo que deberia haber un while antes del que esta que dentro 
	#tenga ese, para asi cerrar la conexion pero no el socket
	socketReceptorTCP.close()

def emisorTCP():

	ip = input("Digite la ip del destinatario: ")
	puerto = input("Digite el puerto del destinatario: ")
	#AQUI DEBERIAMOS PREGUNTAR SI YA EXISTE LA CONEXION, PARA USAR LA EXISTENTE
	#se crea el socket para enviar
	socketEmisorTCP = socket.socket()
	#AQUI DEBERIAMOS USAR LA CLASE CONEXIONABIERTA PARA GUARDAR EL SOCKET
	#AQUI DEBERIAMOS METER EL NUEVO OBJETO EN UNA LISTA PARA PODER CONSULTARLO
	#Se establece la conexion con el receptorTCP mediante la ip y el puerto
	socketEmisorTCP.connect((ip, int(puerto)))
	print("Conectado al servidor")
	
	#SE DEBE PREGUNTAR LA CANTIDAD DE TUPLAS(N)
	#Creamos el ciclo para leer las n tuplas
	#while True:
		#pedimos y leermos la IP, la pasamos numeros para que entre en 4 byte
		#pedimos y leermos la mascara, la pasamos numeros para que entre en 1 byte
		#pedimos y leermos el costo, la pasamos numeros para que entre en 2 byte
		#en cada iteracion concatenamos los bytes y los concatenamos a las iteraciones anteriores
		
	    #Instanciamos una entrada de datos para que el cliente pueda enviar mensajes
	mensaje = input("Mensaje a enviar: ")
	 
	    #Con la instancia del objeto servidor (socketEmisorTCP) y el metodo send, enviamos el mensaje introducido
	socketEmisorTCP.send(bytes(mensaje.encode()))
	 
	    
	 
	#Imprimimos la palabra Adios para cuando se cierre la conexion
	print ("Mensaje enviado.")
	 
	#Cerramos la instancia del objeto servidor
	socketEmisorTCP.close()



def nodoTCP(ip,puerto):
	thread_cliente = threading.Thread(target=emisorTCP)
	thread_cliente.start()

	thread_servidor = threading.Thread(target=receptorTCP(ip,puerto))
	thread_servidor.start()

def comando(comandosolicitado):
	if comandosolicitado.find("salir") == 0 :
		sys.exit()
	if comandosolicitado.find("creaNodo-") == 0 :
		if comandosolicitado.find("pseudoBGP") == 9:
			finalIp = comandosolicitado[19:].find(" ")
			finalIp = finalIp + 1 + 19
			ip =  comandosolicitado[19:finalIp]
			inicioPuerto = finalIp
			puerto = comandosolicitado[inicioPuerto:]
			nodoTCP(ip,int(puerto))
		else:
			if comandosolicitado.find("intAS") == 9:
				finalIp = comandosolicitado[15:].find(" ")
				finalIp = finalIp + 1 + 15
				ip =  comandosolicitado[15:finalIp]
				inicioPuerto = finalIp
				puerto = comandosolicitado[inicioPuerto:]
				#nodoUDP(ip,int(puerto))
			else:
				print("Comando no valido")

	print("La direcion ip es: " + ip)
	print("El puerto es: " + puerto)
		
def consola():
	comandoDigitado = input(">")
	comando(comandoDigitado)


if __name__ == '__main__':
	#nodo()
	consola()