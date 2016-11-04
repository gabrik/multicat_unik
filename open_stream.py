import os
import socket 
import sys
from subprocess import call


def main():

	BUFFSIZE = 1024	

	port = 8001
	address = '0.0.0.0'

	iface=(address,port)	

	print 'Starring server...'

	
	sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

	sock.bind(iface)

	while True:
			
		data,addr = sock.recvfrom(BUFFSIZE)
	
		print data
	

if __name__ == '__main__':
	main()

