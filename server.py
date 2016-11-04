from utils import inet_utils
import sys
import socket as sck


def main():
    if len(sys.argv)<3:
        print ('Usage %s interface ipaddress1,ipaddress2,...' % sys.argv[0])
        sys.exit(0)

    HOST = 'localhost'
    PORT = 8001


    device=sys.argv[1]

    destinations=sys.argv[2:]

    addr = (HOST,PORT)
    sock = sck.socket(sck.AF_PACKET,sck.SOCK_RAW,sck.IPPROTO_RAW)

    iface=(device,0x0800)


    sock.bind(iface)

    print ('Listening to: %s:%s' % iface)
    print (destinations)

    while True:
        raw_buffer = sock.recv(65535)

        for d in destinations:
            if inet_utils.duplicate_pkt(raw_buffer,d,'FFFFFFFFFFFF',sock) == None:
                print ('data sent')
            #else:
            #   print ('error')
            #sock.sendall(data.encode())




if __name__=='__main__':
    main()
