#!/usr/bin/python

import time
import sys, getopt, os
from socket import *

host = '127.0.0.1'
port = 3001
def usage():
    """ command line parameters """
    print 'LightBox Client'
    print 'Basic usage: lightboxMakeClient.py -m TARGET'
    print 'Command line options:'
    print '-h --help show this help screen'
    print '-m --maketarget= The make target to execute.  This parameter is required'
    print '-a --address=[%s] The IP address of the sever.  Default is %s' % host
    print '-p --port=[%s] The port the LightBox server is listening on. default is %s' % port
    
def main( host = host, port = port):
    """
    This client watches gnu make stdout for the "error" or "warning" keywords
    and transmit the appropriate lightbox command to the server.
    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:m:a:p:", ["help", "maketarget=", "address=", "port="])
    except getopt.GetoptError:
        usage()
        sys.exit( 2 )
    if len(opts) == 0:
        usage()
        sys.exit()
            
    makeTarget = None
    print opts
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit()
        elif o in ('-m', '--maketarget'):
            makeTarget = a
        elif o in ('-a', '--address' ):
            host = a
        elif o in ('-p', '--port'):
            port = a
        else:
            print 'Unknown parameter [%s]' % o
            usage()
            sys.exit()
            
    if makeTarget == None:
        print 'No make target defined'
	makeTarget = ''


    leds = {0:'R', 1:'G', 2:'Y'}
    buf = 125
    addr = ( host, port )
    udpSocket = socket( AF_INET, SOCK_DGRAM )

    print 'Sending command to LightBox server %s:%d' % addr
    udpSocket.sendto( 'C', addr )

    pop = os.popen4( 'make ' + makeTarget )

    try:
        errorFlag  = False
        errorWrote      = False
        warningWrote    = False
        warningFlag     = False
        lastWarning     = 0
        greenWrote      = False

        warningCounter  = 0
        resetCounter    = 0
        readline  = pop[1].readline()
        while len( readline ) > 0:
            print readline,
            if ( 'error' in readline ) or ( 'Error' in readline ):
                errorFlag = True
            elif ( 'warning' in readline ) or ( 'Warning' in readline ):
                warningCounter += 1
                warningFlag = True
            else:
                resetCounter += 1

            if ( resetCounter > 15 ) and not greenWrote:
                errorFlag = False
                errorWrote = False
                warningCounter = 0
                warningWrote = False 
                warningFlag = False
                resetCounter = 0
                udpSocket.sendto( leds[ 1 ] + str( 3 ), addr )
                greenWrote = True
                print '******************* GREEN ******************************'

            if warningFlag and not warningWrote:
                #warningLevel = ( warningCounter / 10 ) / 3
                
                #if warningLevel !=  lastWarning:
                #    lastWarning = warningLevel
                    udpSocket.sendto( leds[ 2 ] + str( 3 ), addr )
                    warningWrote = True
                    errorWrote = False
                    greenWrote = False
                    resetCounter = 0
                    warningCounter += 1
                    print '******************* YELLOW ******************************'
                #else:
                #    warningWrote = False

            if errorFlag and not errorWrote:
                udpSocket.sendto( leds[ 0 ] + str( 3 ), addr )
                errorWrote = True;
                warningWrote = False
                warningFlag = False
                greenWrote = False
                errorFlag = False
                resetCounter = 0
                print '******************* RED ******************************'
            readline  = pop[1].readline()
    #        time.sleep(1)
        print "*************************** Build Complete *****************************"
        print "Press Enter to quit"
        udpSocket.sendto( 'F', addr ) # flash the light
        sys.stdin.read(1)
        udpSocket.sendto( 'Z', addr ) # change back to random 

    except (KeyboardInterrupt, SystemExit):
        udpSocket.sendto( 'Z', addr ) # change back to random 
        print "Shutting down"
    
if __name__ == '__main__':
    main()
