#!/usr/bin/python

import time
import sys, getopt, os
from socket import *

host = '127.0.0.1'
port = 3001
def usage():
    """ command line parameters """
    print ('LightBox Client')
    print ('Basic usage: lightboxMakeClient.py -m TARGET')
    print ('Command line options:')
    print ('-h --help show this help screen')
    print ('-a --address=[%s] The IP address of the sever.  Default is %s' % host)
    print ('-p --port=[%s] The port the LightBox server is listening on. default is %s' % port)
    
def main( host = host, port = port):
    """
    This client watches gnu make stdout for the "error" or "warning" keywords
    and transmit the appropriate lightbox command to the server.
    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:a:p:", ["help", "address=", "port="])
    except getopt.GetoptError:
        usage()
        sys.exit( 2 )
    if len(opts) == 0:
        usage()
        sys.exit()
            
    print (opts)
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit()
        elif o in ('-a', '--address' ):
            host = a
        elif o in ('-p', '--port'):
            port = int(a)
        else:
            print ('Unknown parameter [%s]' % o)
            usage()
            sys.exit()
   
    leds = {0:'R', 1:'G', 2:'Y'}
    buf = 125
    addr = ( host, port )
    udpSocket = socket( AF_INET, SOCK_DGRAM )
    command = 'C'

    print ('Sending command to LightBox server %s:%s' % (host, port))
    udpSocket.sendto( command.encode(), addr )

    print ("Press 'Q' to quit")
    try:
        while command != 'Q':
            command = input('command> ')
            udpSocket.sendto( command.encode(), addr )
            print("Sent %s" % command)
    except (KeyboardInterrupt, SystemExit):
        udpSocket.sendto( 'Z'.encode(), addr ) # change back to random 
        print ("Shutting down")
    udpSocket.sendto( 'F'.encode(), addr ) # flash the light
    udpSocket.sendto( 'Z'.encode(), addr ) # change back to random 


if __name__ == '__main__':
    main()
