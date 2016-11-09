import struct
import array
import binascii
import socket

def internet_checksum(pkt):
    if struct.pack("H",1) == "\x00\x01": # big endian
        return checksum_big_endian(pkt)
    else:
        return checksum_little_endian(pkt)

def checksum_big_endian(pkt):
    if len(pkt) % 2 == 1:
        pkt += "\0"
    s = sum(array.array("H", pkt))
    s = (s >> 16) + (s & 0xffff)
    s += s >> 16
    s = ~s
    return s & 0xffff

def checksum_little_endian(pkt):
    if len(pkt) % 2 == 1:
        pkt += "\0"
    s = sum(array.array("H", pkt))
    s = (s >> 16) + (s & 0xffff)
    s += s >> 16
    s = ~s
    return (((s>>8)&0xff)|s<<8) & 0xffff


def ip_checksum(ip_header, size):
    
    cksum = 0
    pointer = 0
    
    #The main loop adds up each set of 2 bytes. They are first converted to strings and then concatenated
    #together, converted to integers, and then added to the sum.
    while size > 1:
        cksum += int((str("%02x" % (ip_header[pointer],)) + 
                      str("%02x" % (ip_header[pointer+1],))), 16)
        size -= 2
        pointer += 2
    if size: #This accounts for a situation where the header is odd
        cksum += ip_header[pointer]
        
    cksum = (cksum >> 16) + (cksum & 0xffff)
    cksum += (cksum >>16)
    
    return (~cksum) & 0xFFFF


def duplicate_pkt(in_pkt,ip_dst,mac_dst,conn):
    eth_header = in_pkt[0:14]
    ip_header = in_pkt[14:34]
    udp_header = in_pkt[34:42]

    ethh=struct.unpack('!6s6s2s',eth_header)
    iph=struct.unpack('!1s1s1H1H2s1B1B2s4s4s' , ip_header)
    udph=struct.unpack('!HHHH',udp_header)

    dstPort=udph[1]
    protocol = str(iph[6])

    if protocol=='17' and dstPort==8001: 
        #14:58:d0:cb:58:34
        dst_dup_mac=bytes([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])#binascii.unhexlify(mac_dst)

        eth_header_duplicate=struct.pack('!6s6s2s',dst_dup_mac,ethh[1],ethh[2])

        new_ip_destination=socket.inet_aton(ip_dst)
        #new_ip_destination=struct.unpack("!L", new_ip_destination)[0]

        packedIP = socket.inet_aton(socket.inet_ntoa(iph[8]))
        src_long=struct.unpack("!L", packedIP)[0]
        packedIP = socket.inet_aton(ip_dst)
        dst_long=struct.unpack("!L", packedIP)[0]

        #CALCULATE IP checksum 

        ip_chksum_pkt=struct.pack('!1s1s1H1H2s1B1BH4s4s' , iph[0],iph[1],iph[2],iph[3],iph[4],iph[5],iph[6],0,iph[8],new_ip_destination)

        ip_chksum = checksum_little_endian(ip_chksum_pkt)

        ip_header_duplicate = ip_duplicate=struct.pack('!1s1s1H1H2s1B1BH4s4s' , iph[0],iph[1],iph[2],iph[3],iph[4],iph[5],iph[6],ip_chksum,iph[8],new_ip_destination)
        #CALCULATE UDP checksum with pseudo packet

        dataLenght=udph[2]
        data=in_pkt[42:42+dataLenght]

        pseudo_udp=[0] * 4 #initialize size
        pseudo_udp[0] = src_long
        pseudo_udp[1] = dst_long
        pseudo_udp[2] = 17
        pseudo_udp[3] = dataLenght

        #print (type(pseudo_udp[0]))
        #print (type(pseudo_udp[1]))
        #print (type(pseudo_udp[2]))
        #print (type(pseudo_udp[3]))

        pseudo_udp_pkt=struct.pack('!LLxBH',pseudo_udp[0],pseudo_udp[1],pseudo_udp[2],pseudo_udp[3])
        udp_pkt_no_chk=struct.pack('!HHHH', udph[0],udph[1],udph[2],0)
        chksum_pkt = pseudo_udp_pkt+udp_pkt_no_chk+data
    
        udp_chksum=checksum_little_endian(chksum_pkt)

        udp_header_duplicate=struct.pack('!HHHH', udph[0],udph[1],udph[2],udp_chksum)


        ### creating frame
        eth_trailer=in_pkt[42+dataLenght:]

        raw_duplication=[]
        raw_duplication[0:14]=eth_header_duplicate
        raw_duplication[14:34]=ip_header_duplicate
        raw_duplication[34:42]=udp_header_duplicate
        raw_duplication[42:42+dataLenght]=data
        raw_duplication[42+dataLenght:]=eth_trailer


        return conn.sendall(bytearray(raw_duplication))
    else:
        return 'false'
    