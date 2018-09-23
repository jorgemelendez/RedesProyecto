import ipaddress

if ipaddress.ip_address('192.167.0.1') in ipaddress.ip_network('192.168.0.0/16'):
	print("HOla")

pedir = True
while pedir:
	ipmod = input("ingrese:")
	ip = ipmod.replace(" ", "/")
	try:
		n = ipaddress.ip_network(ip) 
		pedir = False
	except ValueError as e:
		print("Direccion de red no valida")
		pedir = True


netw = n.network_address.packed
mask = n.netmask.packed
mascara = n.hostmask.packed

print(n)
print(netw)
print(mask)
print(mascara)


ipA = int.from_bytes( netw[0:1], byteorder='big' )
ipB = int.from_bytes( netw[1:2], byteorder='big' )
ipC = int.from_bytes( netw[2:3], byteorder='big' )
ipD = int.from_bytes( netw[3:4], byteorder='big' )

print( str(ipA) + "." + str(ipB) + "." + str(ipC) + "." + str(ipD) + "/" + str(mascara) )

print(ipA)
print(ipB)
print(ipC)
print(ipD)