import ipaddress

#Si lo que retorna tiene len() = 0, entonces no era una ip
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

def bytesToIp(bytesIp):
	ip = str(int(bytesIp[0]))
	ip += "."
	ip += str(int(bytesIp[1]))
	ip += "."
	ip += str(int(bytesIp[2]))
	ip += "."
	ip += str(int(bytesIp[3]))
	
	return ip

def intToBytes( num, cantBytes ):
	return (num).to_bytes(cantBytes, byteorder='big')

def bytesToInt(numbytes):
	return int.from_bytes(numbytes, byteorder='big')

#class ArmarMensajes:
#tipoMensaje = 01, Indica mensaje de solicitud de conexion, en los datos va el puerto receptor del que arma el mensaje(el que solicita conexion)
#tipoMensaje = 05, Indica mensaje de ACK de solicitud de conexion, en los datos va el puerto receptor del que arma el mensaje(el que solicita conexion)
#tipoMensaje = 06, Indica mensaje de ACK de llegada de ACK(finalizacion de conexion), en este caso los datos va la ip, puerto con la que me hablo usted
#tipoMensaje = 16, Indica mensaje de datos, e este caso el SEC(SN) si aplica, en los datos van los datos del mensaje
#tipoMensaje = 20, Indica mensaje de ACK de datos, en este caso si aplica el SEC(RN), en este caso los datos van vacios
#Todos los parametros deben venir en el formato respectivo, excepto los datos que deben venir en bytes
def armarPaq(miIpRec,miPuertoRec,otroIpRec,otroPuertoRec,tipoMensaje,SNoRN, datos):
	resp = bytearray()
	resp += ipToBytes(miIpRec)#4bytes
	resp += intToBytes(miPuertoRec,2)#2bytes
	resp += ipToBytes(otroIpRec)#4bytes
	resp += intToBytes(otroPuertoRec,2)#2bytes
	resp += intToBytes(tipoMensaje,1)#1bytes
	resp += intToBytes(SNoRN,1)#1bytes #ver de tamano SNoRN
	resp += datos
	#print (len(resp))
	return resp
"""
def armarPaqIniciarConexion(miPuertoReceptor):
	#datos = (puertoReceptorACKOrigen).to_bytes(2, byteorder='big')
	datos = (miPuertoReceptor).to_bytes(2, byteorder='big')
	
	return armarPaq(2,0, datos)

#REVISAR SI SE NECESITA RECONOCIMIENTO, EN ESTE CASO NO PORQUE ES ACK DE CONEXION CRE0
#REVISAR PARA QUE SE NECESITA EL PUERTORECEPTORACK, el otro si porque hay que mandar mi puerto receptor
def armarPaqACKConexion():
	#datos = (puertoReceptorACKOrigen).to_bytes(2, byteorder='big')
	datos = bytearray()#(miPuertoReceptor).to_bytes(2, byteorder='big')
	
	return armarPaq(10,0, datos)

#REVISAR PARA QUE SE NECESITA EL PUERTORECEPTORES
def armarPaqDatos(SN, datosCodificados):
	#datos = (puertoReceptorACKOrigen).to_bytes(2, byteorder='big')
	#datos += (puertoReceptorMensOrigen).to_bytes(2, byteorder='big')

	datos = datosCodificados
	return armarPaq(16,SN, datos)

#REVISAR PARA QUE SE NECESITA EL PUERTORECEPTORACK, el otro si porque hay que mandar mi puerto receptor
def armarPaqACKDatos(RN):
	#datos = (puertoReceptorACKOrigen).to_bytes(2, byteorder='big')
	datos = bytearray()
	
	return armarPaq(24,RN, datos)
"""








def desarmarMensaje(mensaje):
	if mensaje[0:1] == 2:
		print ("Paquete de iniciar conexion")
	elif mensaje[0:1] == 10:
		print ("Paquete ACK de iniciar conexion")

#Deben ser 4 porque debe ser fullduplex, entonces por cada dirreccion se debe tener para mandar mensajes, y el ack de vuelva, eso seria una y la otra agrega 2 mas.



"""
class Prueba:
	mensaje = Mensaje()
	
	def establecerConexion(self, otroIpRec, otroPuertoRec):
		mysocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		mysocket.settimeout(0.5)

		mensajeConexion = mensaje.armarPaqACKConexion(5000,otroPuertoRec,secuencia,reconocimiento, puertoReceptorACKOrigen, puertoReceptorMensOrigen)

		while user_input:
		    mysocket.sendto(mensajeConexion, (otroIpRec, otroPuertoRec) )     
		    acknowledged = False
		    # spam dest until they acknowledge me (sounds like my kids)
		    while not acknowledged:
		        try:
		            ACK, address = mysocket.recvfrom(1024)
		            acknowledged = True
		        except socket.timeout:
		            mysocket.sendto(user_input, dest)
		    print (ACK)
		    user_input = raw_input()

		mysocket.close()"""