	def revisaMensaje(self, mensaje):
		mascaraByte = bytearray()
		ipByte = bytearray()
		ipByteComp = bytearray()

		ipA = int.from_bytes( mensaje[2:3], byteorder='big' )
		ipB = int.from_bytes( mensaje[3:4], byteorder='big' )
		ipC = int.from_bytes( mensaje[4:5], byteorder='big' )
		ipD = int.from_bytes( mensaje[5:6], byteorder='big' )
		mascara = int.from_bytes( mensaje[6:7], byteorder='big' )
		
		ipByte = mensaje[2:3] + mensaje[3:4] + mensaje[4:5] + mensaje[5:6]
		ipByteComp = ipByte

		numBytes = mascara/8
		numBits = mascara%8

		if(numBits > 0):
			numBitsAux = 1

		for a in range (0,4):
			if(numBytes != 0):
				mascaraByte += (255).to_bytes(1,byteorder = 'big')
				--numBytes
			elif(numBitsAux != 0):
				if(numBits == 1):
					mascaraByte += (128).to_bytes(1,byteorder='big')
				elif(numBits == 2):
					mascaraByte += (192).to_bytes(1,byteorder='big')
				elif(numBits == 3):
					mascaraByte += (224).to_bytes(1,byteorder='big')
				elif(numBits == 4):
					mascaraByte += (240).to_bytes(1,byteorder='big')
				elif(numBits == 5):
					mascaraByte += (248).to_bytes(1,byteorder='big')
				elif(numBits == 6):
					mascaraByte += (252).to_bytes(1,byteorder='big')
				elif(numBits == 7):
					mascaraByte += (254).to_bytes(1,byteorder='big')
			else:
				mascaraByte += (0).to_bytes(1,byteorder='big')

		ipByteComp = ipByteComp&mascaraByte

		if(ipByteComp == ipByte):
			flag = True
		else:
			flag = False
		return flag