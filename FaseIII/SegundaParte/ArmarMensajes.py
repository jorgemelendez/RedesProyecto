import ipaddress

#Funcion que pasa un string IP a 4 bytes,
# retorna 0 bytes si la ip era invalida
#ip: ip que quiere convertir a bytes
def ipToBytes(ip):
	myip = ip.split('.')
	bytesIp = bytearray()
	ipPrueba = ip + "/32"
	try:
		n = ipaddress.ip_network(ipPrueba)
	except ValueError as e:
		print("Ip invalida")
	else:
		for x in range(0, 4):
			ipnum = int(myip[x])
			bytesIp += (ipnum).to_bytes(1, byteorder='big')
	return bytesIp

#Funcion que convierte una IP de 4 bytes a
# una ip String
#bytesIp: la ip en 4 bytes que desea convertir
def bytesToIp(bytesIp):
	ip = str(int(bytesIp[0]))
	ip += "."
	ip += str(int(bytesIp[1]))
	ip += "."
	ip += str(int(bytesIp[2]))
	ip += "."
	ip += str(int(bytesIp[3]))
	return ip

#Funcion que retorna el entero num en un vector de bytes de cantBytes bytes
#num: entero que desea convertir
#cantBytes: cantidad de bytes que se quiere que tenga el numero convertido
def intToBytes( num, cantBytes ):
	return (num).to_bytes(cantBytes, byteorder='big')

#Funcion que convierte un vector de bytes en un entero
#numbytes: bytes que quiere convertir en un numero entero
def bytesToInt(numbytes):
	return int.from_bytes(numbytes, byteorder='big')

#class ArmarMensajes:
#tipoMensaje = 01, Indica mensaje de solicitud de conexion, en los datos va el puerto receptor del que arma el mensaje(el que solicita conexion)
#tipoMensaje = 05, Indica mensaje de ACK de solicitud de conexion, en los datos va el puerto receptor del que arma el mensaje(el que solicita conexion)
#tipoMensaje = 06, Indica mensaje de ACK de llegada de ACK(finalizacion de conexion), en este caso los datos va la ip, puerto con la que me hablo usted
#tipoMensaje = 16, Indica mensaje de datos, e este caso el SEC(SN) si aplica, en los datos van los datos del mensaje
#tipoMensaje = 20, Indica mensaje de ACK de datos, en este caso si aplica el SEC(RN), en este caso los datos van vacios
#Todos los parametros deben venir en el formato respectivo, excepto los datos que deben venir en bytes
def armarPaq(miIpRec, miPuertoRec, otroIpRec, otroPuertoRec, tipoMensaje, SN, RN, datos):
	resp = bytearray()
	resp += ipToBytes(miIpRec)#4bytes
	resp += intToBytes(miPuertoRec,2)#2bytes
	resp += ipToBytes(otroIpRec)#4bytes
	resp += intToBytes(otroPuertoRec,2)#2bytes
	resp += intToBytes(tipoMensaje,1)#1bytes
	resp += intToBytes(SN,1)#1bytes #ver de tamano SN
	resp += intToBytes(RN,1)#1bytes #ver de tamano RN
	resp += datos
	return resp