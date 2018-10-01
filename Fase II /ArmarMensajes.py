class ArmarMensajes:
	#tipoMensaje = 2, Indica que es un Paquete para establecer una conexion, en los datos deben venir los datos respectivos
	#tipoMensaje = 8, Indica que es un ACK de respuesta al paquete que recibio, en este caso el numero de secuencia y reconocimiento")
	#tipoMensaje = 9, Indica que es un ACK de respuesta a fin de conexion")
	#tipoMensaje = 10, Indica que es un ACK de respuesta a inicio de conexion")
	#tipoMensaje = 0, Indica que es un NACK de respuesta al paquete recibido, en este caso el numero de secuencia y reconocimiento")
	#tipoMensaje = 16, Indica que es un paquete de datos
	def armarPaq(self, tipoMensaje,reconocimiento, datos):
		resp = bytearray()
		#resp += (puertoOrigen).to_bytes(2, byteorder='big')
		#resp += (puertoDestino).to_bytes(2, byteorder='big')
		resp += (tipoMensaje).to_bytes(1, byteorder='big')
		resp += (reconocimiento).to_bytes(4, byteorder='big')
		resp += datos
		#print (len(resp))
		return resp

	#REVISAR SI SE NECESITA RECONOCIMIENTO, EN ESTE CASO NO PORQUE ES CONEXION CRE0
	#REVISAR PARA QUE SE NECESITA EL PUERTORECEPTORACK, el otro si porque hay que mandar mi puerto receptor
	def armarPaqIniciarConexion(self,reconocimiento, puertoReceptorACKOrigen, puertoReceptorMensOrigen):
		datos = (puertoReceptorACKOrigen).to_bytes(2, byteorder='big')
		datos += (puertoReceptorMensOrigen).to_bytes(2, byteorder='big')
		
		return armarPaq(self, 2,reconocimiento, datos)

	#REVISAR SI SE NECESITA RECONOCIMIENTO, EN ESTE CASO NO PORQUE ES ACK DE CONEXION CRE0
	#REVISAR PARA QUE SE NECESITA EL PUERTORECEPTORACK, el otro si porque hay que mandar mi puerto receptor
	def armarPaqACKConexion(self,reconocimiento, puertoReceptorACKOrigen, puertoReceptorMensOrigen):
		datos = (puertoReceptorACKOrigen).to_bytes(2, byteorder='big')
		datos += (puertoReceptorMensOrigen).to_bytes(2, byteorder='big')
		
		return armarPaq(self, 10,reconocimiento, datos)

	#REVISAR PARA QUE SE NECESITA EL PUERTORECEPTORES
	def armarPaqDatos(self,reconocimiento, puertoReceptorACKOrigen, puertoReceptorMensOrigen, datosCodificados):
		datos = (puertoReceptorACKOrigen).to_bytes(2, byteorder='big')
		datos += (puertoReceptorMensOrigen).to_bytes(2, byteorder='big')

		datos += datosCodificados
		return armarPaq(self, 16,reconocimiento, datos)

	def desarmarMensaje(self, mensaje):
		if mensaje[0:2] == 2:
			print ("Paquete de iniciar conexion")
		elif mensaje[0:2] == 10:
			print ("Paquete ACK de iniciar conexion")

#Deben ser 4 porque debe ser fullduplex, entonces por cada dirreccion se debe tener para mandar mensajes, y el ack de vuelva, eso seria una y la otra agrega 2 mas.
class ConexionLogica:
	ipOtro = ""
	puertoEmisorMensOtro = 0 #2bytes 
	puertoReceptorACKOtro = 0 #2bytes 

	puertoReceptorMensOtro = 0 #2bytes 
	puertoEmisorACKOtro = 0 #2bytes #NO SE SI SE OCUPA

	def __init__(self, ipOrigen, puertoEmisorMensOrigen, puertoReceptorACKOrigen, puertoReceptorMensOrigen, puertoEmisorACKOrigen):
		self.miIp = ip
		self.miPuerto = puerto
		self.otroIp = ip
		self.otroPuerto = puerto



class Prueba:
	mensaje = Mensaje()
	
	def establecerConexion(self, ipDestino, puertoDestino):
		mysocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		mysocket.settimeout(0.5)

		mensajeConexion = mensaje.armarPaqACKConexion(5000,puertoDestino,secuencia,reconocimiento, puertoReceptorACKOrigen, puertoReceptorMensOrigen)

		while user_input:
		    mysocket.sendto(mensajeConexion, (ipDestino, puertoDestino) )     
		    acknowledged = False
		    # spam dest until they acknowledge me (sounds like my kids)
		    while not acknowledged:
		        try:
		            ACK, address = mysocket.recvfrom(1024)
		            acknowledged = True
		        except socket.timeout:
		            mysocket.sendto(user_input, dest)
		    print ACK
		    user_input = raw_input()

		mysocket.close()