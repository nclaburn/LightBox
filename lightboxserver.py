#!/usr/bin/python
import serial
import time
import sys, getopt, os
import SocketServer, socket, string
from collections import deque
import threading

def usage():
    """ command line parameters """
    print 'LightBox Server'
    print 'Command line options:'
    print '-h --help show this help screen'
    print '-s --serialport= The serial port to use.  This parameter must be defined'
    print '-c --command= The command to monitor.  If this parameter is not set then LightBox will operate in "server" mode'
    print '--serverport=[%s] The port the LightBox server should listen on.  If this parameter is set "command" will be ignored'  % 3001 

def main():
    """
    The lightboxserver takes commands from the lightboxMakeClient via UDP and
    sends it to Lightbox device commands via serial (USB).
    """
    serialPort = None
    localPort = 3001
    command = ''
    serverMode = False;
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:c:p:", ["help", "serialport=", "command=", "serverport="])
    except getopt.GetoptError:
        usage()
        sys.exit( 2 )
    if len(opts) == 0:
        usage()
        sys.exit()
            
    print opts
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit()
        if o in ('-s', '--serialport'):
            serialPort = a
        if o in ('-c', '--command' ):
            command = a
        elif o in ('-p', '--serverport'):
            localPort = a
            serverMode = True

    if serialPort == None:
        print 'A serial port argument must be defined!'
        usage()
        sys.exit( 2 )
    
    lbs = LightBoxServer( serialPort, serverport = localPort, command = command )
    lbs.Start()
    try:
        time.sleep( 1 )
        print 'Press Enter to quit'
        sys.stdin.read(1)
    except ( KeyboardInterrupt, SystemExit ):
        print 'Shutting down'
    lbs.Stop()
    
class LightBoxServer( threading.Thread ):
    """Threaded server. Opens a UDP socket and listens
    on the given port. Also opens the given serial port to send
    commands to the lightbox serial device"""
    def __init__( self, serialport, serverport = 0, command = None ):
        threading.Thread.__init__( self )
        self.serialPort = serialport
        self.serverPort = serverport
        self.command = command
        self.Serial = Serial( serialport )
        self.server = None
        self.stopThread = False
        self.deque = deque()

    def Start( self ):
        """
        Start the lightbox server. Opens socket and serial device
        """
        if self.Serial.Open():
            print 'Starting Lightbox server'
            self.server = UdpServer( '0.0.0.0', self.serverPort, self.deque )
            self.stopThread = True
            self.start()
        
    def Stop( self ):
        """
        Stop the lightbox server. Closes socket and serial device
        """
        self.stopThread = False
        print 'Shutting down Lightbox server'
        if self.server != None:
            self.server.Stop()
        self.Serial.Close()
    
    def run( self ):
        """
        Run thread for the server.
        """
        if self.server:
            self.server.Start()
        
        while self.stopThread:
            if len( self.deque ) > 0:
                self.Serial.Write( self.deque.pop() )
            time.sleep( .5 )
        
class Serial( threading.Thread ):
    """
    Serial port server. Handles serial port communications.
    """
    def __init__( self, serialport ):
        threading.Thread.__init__( self )
        self.ser = None
        self.serialPort = serialport
        self.stopThread = False;
        
    def Close( self ):
        """Closes the serial port"""
        print 'Closing serial port '
        self.stopThread = True
        if self.ser != None:
            self.ser.close()

    def Open( self ):
        """Opens the serial port"""
        try:
            print 'Opening serial port'
            self.ser = serial.Serial( self.serialPort, timeout = .25 )
            #print "Waiting for lightbox init..."
            self.stopThread = False
            self.start()            
        except (KeyboardInterrupt, SystemExit):
            print 'Closing serial port..'
        except serial.SerialException, (message):
            print 'Error opening serial port:'
            print message
            return False
        return True

    def Write( self, data ):
        """
        Write given data to the serial port.
        """
        print 'Writing serial data [%s]' % data
        self.ser.write( data )
    
    def Read( self ):
        """
        Read data from serial port. Expects a newline character.
        """
        print 'Read serial data [%s]' % self.ser.readline()

    def run( self ):
        """
        Overridden thread
        """
        while self.stopThread:
            print 'Read serial data [%s]' % self.ser.readline()
        
class UdpServer( threading.Thread ):
    """
    Udp server class. This class starts a UDP server that listens
    on the given address and port. The deque will retain the incoming
    messages for use by calling code.
    """
    def __init__( self, address, port, deque):
        threading.Thread.__init__( self )
        self.address = address
        self.port = port
        self.endpoint = ( address, port )
        self.socket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.deque = deque
        self.stopThread = False
        
    def Start( self ):
        """
        Start the UDP server.
        """
        try:
            self.socket.bind( self.endpoint )
        except socket.error:
            print 'Bind failed for port %d: [%s]' % ( self.port, socket.error )
            raise SystemExit
        self.stopThread = True
        self.start()
        print 'UDP server started'
    
    def run( self ):
        """
        The overridden thread function. Listens for incoming commands
        and puts them on the output deque.
        """
        while self.stopThread:
            datagram, addr = self.socket.recvfrom( 256 )
            if datagram:
                if ( ord( datagram[ 0 ] ) > ord( 'A' ) ) and ( ord( datagram[ 0 ] ) < ord( 'z' ) ):
                    self.deque.appendleft( datagram )
                    print 'Received command from [%s]:  Command [%s]' % ( addr[ 0 ], datagram )
                else:
                    print 'Received bogus data from [%s]' % addr[ 0 ]
    def Stop( self ):
        """
        Stop the thread and close the socket
        """
        print 'UDP server stopped'
        self.stopThread = False
        self.socket.close()
        
if __name__ == '__main__':
    main()
