#!/usr/bin/env python
 
#importamos el modulo socket
import socket
import errno
from socket import error as SocketError
 
#instanciamos un objeto para trabajar con el socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
#Con el metodo bind le indicamos que puerto debe escuchar y de que servidor esperar conexiones
#Es mejor dejarlo en blanco para recibir conexiones externas si es nuestro caso
s.bind(("192.168.0.15", 5010))
 
#Aceptamos conexiones entrantes con el metodo listen, y ademas aplicamos como parametro
#El numero de conexiones entrantes que vamos a aceptar
s.listen(5)
 
#Instanciamos un objeto sc (socket cliente) para recibir datos, al recibir datos este 
#devolvera tambien un objeto que representa una tupla con los datos de conexion: IP y puerto
sc, addr = s.accept()
 
print("Servidor funcionando correctamente")
 
while True:
 
    #Recibimos el mensaje, con el metodo recv recibimos datos y como parametro 
    #la cantidad de bytes para recibir
    try:
        recibido = sc.recv(1024)
    except SocketError as e:
        if e.errno != errno.ECONNRESET:
            print("Conexion perdida")
            break
    #Si el mensaje recibido es la palabra close se cierra la aplicacion
    if recibido == "close":
        break
 
    #Si se reciben datos nos muestra la IP y el mensaje recibido
    print (str(addr[0]) + " dice: " +  int(recibido[0:10]))

    #Devolvemos el mensaje al cliente
    try:
        sc.send(recibido)
    except SocketError as e:
        if e.errno != errno.ECONNRESET:
            print("Conexion perdida")
            break
print("Adios.!!!")
 
#Cerramos la instancia del socket cliente y servidor
sc.close()
s.close()