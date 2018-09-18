def tuplaToBytes(tupla):
    tupladiv = tupla.split(' ')
    tuplabytes = []
    tuplaip = []
    tuplamascara = []
    tuplacosto = []
    print(tuplacosto)
    numeroip = tupladiv[0]
    myip = numeroip.split('.')
    for x in range(0, 4):
        ipnum = int(myip[x])
        tuplaip.append(bytes([ipnum]))
    masc = int(tupladiv[1])
    tuplamascara.append(bytes([masc]))
    costo = int(tupladiv[2])
    print('Costo:', costo)
    tuplacosto.append((costo).to_bytes(3, byteorder='big'))
    tuplabytes += tuplaip
    tuplabytes += tuplamascara
    tuplabytes += tuplacosto
    print(tuplabytes)

tuplaToBytes("192.168.0.15 12 12")