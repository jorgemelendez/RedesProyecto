import time
import socket
from ArmarMensajes import *
from LeerArchivo import *

class HiloConexionUDPSegura:

	def __init__(self, buzonReceptor, otraConexion, miConexion, socketConexion, lockSocket):
		self.buzonReceptor = buzonReceptor
		self.otraConexion = otraConexion
		self.miConexion = miConexion
		self.SN = 0
		self.RN = 0
		self.socketConexion = socketConexion
		self.lockSocket = lockSocket
		self.datosRecibidos = bytearray()
		self.etapaSyn = 0

		

		self.lockArchivos = threading.Lock()
		self.paquetesEnviar = list()#Archivos por enviar

		self.paqueteActual = list()#Archivo actual que se esta enviando

		self.ackDatosFin = False

		self.ackHandshakeTerminado = False
		
		self.ultimoMensajeMandado = bytearray()

	def meterArchivoAEnviar(self, contenidoArchivo):
		segmentado = self.segmentarArchivo(contenidoArchivo, 5)
		self.lockArchivos.acquire()
		self.paquetesEnviar.append(segmentado)
		self.lockArchivos.release()


	def connect(self, ipServidor, puertoServidor):
		mensaje = armarPaq(self.miConexion[0], self.miConexion[1], self.otraConexion[0], self.otraConexion[1], 1, self.SN, self.RN, bytearray() ) #NO HAY QUE MANDAR DATOS PORQUE ES ESTABLECIENDO CONEXION
		self.lockSocket.acquire()
		self.socketConexion.sendto(mensaje, (ipServidor, puertoServidor))
		self.lockSocket.release()
		self.etapaSyn = 2
		

	#METER MENSAJE EN EL BUZON ANTES DE CREAR EL HILO
	def receptor():
		while True:

			if len(self.paqueteActual) == 0 and ackDatosFin == False: #paquete actual ya termino y ya lo confirmaron
				if len(self.paquetesEnviar) != 0: # si hay mas paquetes para enviar
					self.lockArchivos.acquire()
					self.paqueteActual = self.paquetesEnviar.pop(0)
					self.lockArchivos.release()
			



			mensaje = self.buzonReceptor.sacarDatos(self.otraConexion)
			if mensaje is None:
				time.sleep(1)#ANALIZAR LA CANTIDAD DE SEGUNDOS
			#if mensaje is None:
				mensaje = self.buzonReceptor.sacarDatos(self.otraConexion)
			if mensaje is None:

				if self.etapaSyn == 3 and self.ackHandshakeTerminado == False:#Caso donde no llegan los primeros primeros datos y ya se envio el ack syn
					ACKConexion = armarPaq(self.miConexion[0], self.miConexion[1], self.otraConexion[0], self.otraConexion[1], 3, self.SN, self.RN, bytearray()) #NO HAY QUE MANDAR DATOS PORQUE ES ESTABLECIENDO CONEXION
					self.lockSocket.acquire()
					self.socketConexion.sendto(ACKConexion, self.otraConexion)
					self.lockSocket.release()
				if self.etapaSyn == 3 and self.ackHandshakeTerminado == True: #Caso donde no responde con paq nuevo
					ACKDatos = armarPaq(self.miConexion[0], self.miConexion[1], self.otraConexion[0], self.otraConexion[1], 10, self.SN, self.RN, self.ultimoMensajeMandado ) #VER SI TENGO DATOS PARA MANDAR
					self.lockSocket.acquire()
					self.socketConexion.sendto(ACKDatos, self.otraConexion)
					self.lockSocket.release()
				else:
					if self.etapaSyn == 2: #Caso donde no responden syn
						self.connect(self, self.otraConexion[0], self.otraConexion[1])
					else:
						if self.etapaSyn == 1:#Caso donde no responden respuesta a syn(no llega ack syn)
							ACKConexion = armarPaq(self.miConexion[0], self.miConexion[1], self.otraConexion[0], self.otraConexion[1], 1, self.SN, self.RN, bytearray()) #NO HAY QUE MANDAR DATOS PORQUE ES ESTABLECIENDO CONEXION
							self.lockSocket.acquire()
							self.socketConexion.sendto(ACKConexion, self.otraConexion)
							self.lockSocket.release()
				time.sleep(1)#ANALIZAR LA CANTIDAD DE SEGUNDOS
			else:
				otroIpRec = bytesToIp(recibido[0:4])
				otroPuertoRec = bytesToInt(recibido[4:6])
				miIpRec = bytesToIp(recibido[6:10])
				miPuertoRec = bytesToInt(recibido[10:12])
				tipoPaq = bytesToInt(recibido[12:13])
				SNpaq = bytesToInt(recibido[13:14])
				RNpaq = bytesToInt(recibido[14:15])
				datos = recibido[15:]

				#Poner primero el caso de que esta sincronmizando

				if self.etapaSyn != 3:
					if self.etapaSyn == 0 and tipoPaq == 1:
						self.connect(self.otraConexion[0], self.otraConexion[1])
						self.etapaSyn = 1
					elif self.etapaSyn == 2 and tipoPaq == 1:
						ACKConexion = armarPaq(self.miConexion[0], self.miConexion[1], self.otraConexion[0], self.otraConexion[1], 3, self.SN, self.RN, self.ultimoMensajeMandado) #NO HAY QUE MANDAR DATOS PORQUE ES ESTABLECIENDO CONEXION
						self.lockSocket.acquire()
						self.socketConexion.sendto(ACKConexion, self.otraConexion)
						self.lockSocket.release()
						self.etapaSyn = 3
						break #QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQUUUUUUUUUUUUUUUUUUIIIIIIIIIIIIIIIIIIIITTTTTTTTTTTTTTTAAAAAAAAAAAAAAAAAAAAAARRRRRRRRRRRRRRRRRRRRR
					elif self.etapaSyn == 1 and tipoPaq == 3:
						self.etapaSyn = 3
						break #QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQUUUUUUUUUUUUUUUUUUIIIIIIIIIIIIIIIIIIIITTTTTTTTTTTTTTTAAAAAAAAAAAAAAAAAAAAAARRRRRRRRRRRRRRRRRRRRR
					else:
						print("Mensaje extranno")
						print(tipoPaq)
				else:
					if self.SN == self.RNpaq: #REVISAR SI ES DEL TIPO DE MENSAJE QUE ESTOY ESPERANDO
						self.datosRecibidos += datos
						#Enviar paquete de ack de respuesta
						self.RN = self.RN + 1

						#self.ultimoMensajeMandado = 
						ACK = armarPaq(miIpRec, miPuertoRec, otroIpRec, otroPuertoRec, 1, self.SN, self.RN, self.ultimoMensajeMandado) #VER SI TENGO DATOS PARA MANDAR
						
						self.lockSocket.acquire()
						self.socketConexion.sendto(ACK, emisor)
						self.lockSocket.release()



class emisor:

	def __init__(self, miConexion, buzonReceptor, socketConexion, lockSocket):
		self.conexiones = list()
		self.lockConexiones = threading.Lock()
		self.miConexion = miConexion
		self.buzonReceptor = buzonReceptor
		self.socketConexion = socketConexion
		self.lockSocket = lockSocket



	#Llamar solo CON candado adquirido
	def buscarConexionLogica(self, ip,puerto):#APLICA SI LAS CONEXIONES DEBEN ESTAR PARA AMBOS , creo que deben estar aunque para tener una lista de las conexiones hechas para usarlas, VER QUE DICE LA PROFE
		i = 0;
		largo = len(self.conexiones)
		while i < largo:
			if self.conexiones[i].soyLaConexionHacia(ip,puerto) :
				return i
			i = i + 1
		return -1

	def enviarArchivo(self):
		otraIp = input('Digite la ip del destinatario: ')
		ipPrueba = otraIp + "/32"
		try:
			n = ipaddress.ip_network(ipPrueba)
		except ValueError as e:
			print ("Ip no valida")
		else:
			lecturaPuerto = input('Digite el puerto del destinatario: ')
			try:
				otroPuerto = int(lecturaPuerto)
			except ValueError as e:
				print ("Puerto no valido")
			else:
				if otroPuerto < 0 or otroPuerto > 65535:
					print ("Puerto no valido")
				else:
					direccion = input('Digite la direccion del archivo: ')
					direccion = "/home/christofer/Escritorio/RedesProyecto/ArchivoPrueba.txt" #QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQUUUUUUUUUUUUUUUUUUIIIIIIIIIIIIIIIIIIIITTTTTTTTTTTTTTTAAAAAAAAAAAAAAAAAAAAAARRRRRRRRRRRRRRRRRRRRR
					contenido = archivoToString(direccion)
					self.lockConexiones.acquire()
					indice = self.buscarConexionLogica(otraIp, otroPuerto)

					if indice == -1:
						print ("Nueva conexion")
						conexion = HiloConexionUDPSegura( self.buzonReceptor, (otraIp,otroPuerto), self.miConexion, self.socketConexion, self.lockSocket )
						conexion.connect(otraIp,otroPuerto)
						hiloNuevaConexion = threading.Thread(target=conexion.receptor, args=())
						hiloNuevaConexion.start()

						self.conexiones.append(conexion)
					
					else:
						print("Conexion existente")
						

						if respEnvio == False:
							self.cerrarUnaConexion(ip,int(puerto))
						
					self.lockConexiones.release()







if __name__ == '__main__':

	socketNuevo = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	socketNuevo.bind(("192.168.0.15",int(sys.argv[1])))

	time.sleep(10)

	buzonReceptor = Buzon()

	Hilo = HiloConexionUDPSegura(buzonReceptor, otraConexion, miConexion, socketConexion, lockSocket)

	if len(sys.argv) == 3:#Inidica que si vienen 2 parametros es el que se va a conectar al otro
		Hilo.connect("192.168.0.15", int(sys.argv[2]) )

	Hilo.receptor()


	proceso_repetorTcp = threading.Thread(target=repetorTcp.recibir, args=(ip,puerto,))
	proceso_repetorTcp.start()




	buzon = Buzon()
	buzon.meterDatos(("192.168.0.15", 5000), "Primer dato")
	buzon.meterDatos(("192.168.0.15", 5000), "Segundo dato")
	buzon.meterDatos(("192.168.0.15", 5000), "Tercer dato")

	print(buzon.sacarDatos(("192.168.0.15", 5000)))
	time.sleep(0.5)

	print(buzon.sacarDatos(("192.168.0.15", 5000)))
	time.sleep(0.5)

	print(buzon.sacarDatos(("192.168.0.15", 5000)))
	time.sleep(0.5)

	print(buzon.sacarDatos(("192.168.0.15", 5000)))
	time.sleep(0.5)
