from utils import inet_utils
import sys
sys.path.append('./bin/')

import socket as sck
import threading
import datetime
from bottle import *

#sudo pip3 install --install-option="--prefix=/home/gabriele/Scrivania/multicat_unik" --ignore-installed bottle



destinations=[]

@get('/destination/add/<ip>')
def add_destination(ip):
        if ip not in destinations:
            global destinations
            destinations.append(ip)
            return str('OK')
        else:
            return str('KO')

@get('/destination/del/<ip>')
def remove_destination(ip):
    if ip in destinations:
        global destinations
        destinations.remove(ip)
        return str('OK')
    else:
        return str('KO')


@get('/destinations/')
def remove_destination(ip):
    return destinations

def main():
    #if len(sys.argv)<3:
    #    print ('Usage %s interface ipaddress1,ipaddress2,...' % sys.argv[0])
    #    sys.exit(0)

    HOST = 'localhost'
    PORT = 8001


    device=sys.argv[1]

    #destinations=sys.argv[2:]

    addr = (HOST,PORT)
    sock = sck.socket(sck.AF_PACKET,sck.SOCK_RAW,sck.IPPROTO_RAW)

    iface=(device,0x0800)


    sock.bind(iface)

    print ('Listening to: %s:%s' % iface)
   

    while True:
        raw_buffer = sock.recv(65535)

        for d in destinations:
            if inet_utils.duplicate_pkt(raw_buffer,d,'FFFFFFFFFFFF',sock) == None:
                print ('data sent ' + datetime.datetime.now().time().isoformat())
            #else:
            #   print ('error')
            #sock.sendall(data.encode())




if __name__=='__main__':
    threading.Thread(target=main).start()
    run(host='0.0.0.0',port=8080,debug=True)

