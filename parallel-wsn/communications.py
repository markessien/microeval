#!/usr/bin/python

'''
Created on 21.09.2011

@author: schmittb
'''

import SocketServer, socket, sys, fcntl, struct

creator=None

class myTCPServer(SocketServer.TCPServer):
    
    #takes care of the "address already in use" problem -> TCP's TIME_WAIT state
    allow_reuse_address = True
    
    def __init__(self, server_address, RequestHandlerClass, caller):
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)
        print "started tcp_server on %s port %s" %(server_address[0], server_address[1])
        sys.logger.debug("started tcp_server on ip %s port %s" %(server_address[0], server_address[1])) #@UndefinedVariable (this is to ignore the error in eclipse)
        global creator
        creator = caller

class CommHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        sys.logger.debug("%s: Received packet from %s with content %s" %(__name__, self.client_address[0], self.data)) #@UndefinedVariable (this is to ignore the error in eclipse)
        #print "%s wrote: %s" %(self.client_address[0], self.data)
        creator.connection_established(self.client_address)
        
        #process the received command 
        creator.process_comm(self.data)
        
        # just send back the same data, but upper-cased
        #self.request.send(res) #self.data.upper()

class ClientCommHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for the server on the client (uhu).

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        sys.logger.debug("%s: Received packet from %s with content %s" %(__name__, self.client_address[0], self.data)) #@UndefinedVariable (this is to ignore the error in eclipse)
        creator.process_comm(self)
        
        
class CommClient():
    
    def send(self, data, host, port):
            
        # Create a socket (SOCK_STREAM means a TCP socket)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        #allow socket to be used even if TCP is still in TIME_WAIT state
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        
        # Connect to server and send data
        try: 
            sock.connect((str(host), int(port)))
            count = sock.send(str(data)+ '\n')
            if(count < len(str(data))):
                print ("send error!")
                return -1
        finally:
            sock.close()
        
        # Receive data from the server and shut down
#        received = sock.recv(55000)
#        sock.close()
#        
#        # output data for debugging purposes
#        #print "Sent:     %s" % data
#        print "Execution returned:\n%s" % received  


class ip_address():

    def get_ip_address(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15]))[20:24])
