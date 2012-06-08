#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 20.09.2011

@author: schmittb

Takes care of the connection to the sensor node, 
sending commands and reading/logging/sending the output.
'''

import sys, serial, threading

logger = None
inbound_connection = False
client_address = None
serial_port_timeout= 0.5

class controller():
        
    def start_serial(self, sn_path, config, comm_client):
        sys.logger.debug("Starting Connection to the Sensor Node at %s" %sn_path) #@UndefinedVariable (this is to ignore the error in eclipse)
        #open serial-connection to the sensor-node
        self.ser = serial.Serial(sn_path, baudrate=115200, dsrdtr=0, rtscts=0, timeout=serial_port_timeout)
        
	sys.logger.debug("Resetting the Sensor Node") #@UndefinedVariable (this is to ignore the error in eclipse)
	self.ser.setDTR(1)
	self.ser.setRTS(1)
	self.ser.setDTR(0)
        self.ser.setRTS(0)
        
        # start serial->console & tcp-send thread
        console_thread = threading.Thread(target=reader, args=(self.ser, config, comm_client,))
        console_thread.setDaemon(1)
        console_thread.start()
    
    def execute(self, command):
        print("executing command: "+command)
        sys.logger.debug("Executing command %s now" %command) #@UndefinedVariable (this is to ignore the error in eclipse)
        self.ser.write(command.strip() + "\n")
     
    def reset(self):
        sys.logger.debug("Resetting the Sensor Node") #@UndefinedVariable (this is to ignore the error in eclipse)
        self.ser.setDTR(1)
        self.ser.setRTS(1)
        self.ser.setDTR(0)
        self.ser.setRTS(0)
        
    def connection_available(self, client):
        global inbound_connection
        inbound_connection = True
        global client_address
        client_address = client
        
    def connection_terminated(self):
        global inbound_connection
        inbound_connection = False
        
        
# serial-to-console thread
def reader(ser, config, comm_client):
    global inbound_connection
    stdout = config.get("main", "stdout") == "yes"
    port = config.get("main", "client_port")
    line=""
    
    sys.logger.debug("New Code: Essien")
    
    try:
        while (1):
            c = ser.read(1)
            timeup = c==""
            if timeup:              # timeout progged - no character was read
                if line=="":        # if line is empty we don't need to do anything. 
                    ser.setTimeout(None)   # no timeout needed since line is empty
                    continue
                else:               # line contains at least one character - send it
                    sys.logger.debug("sensornode:\t\t"+line.rstrip('\n')) #@UndefinedVariable (this is to ignore the error in eclipse)
                    if inbound_connection:
                        host = client_address[0]
                        print "sending %s to %s port %s" % (line, host, port)
                        comm_client.send(line, host, port)
                        print "sent something back to client at %s:%s" %(host, port)
                    line=""
            else:                   # there was a character read from serial
                if line=="":
                    ser.setTimeout(serial_port_timeout)     #reset timeout to normal 
                line+=c
                if stdout:
                    sys.stdout.write(c)
                    sys.stdout.flush()        
                if (c=='\n' or c=='\r\n'):
                    sys.logger.debug("sensornode:\t\t"+line.rstrip('\n')) #@UndefinedVariable (this is to ignore the error in eclipse)
                    if inbound_connection:
                        host = client_address[0]
                        print "sending %s to %s port %s" % (line, host, port)
                        comm_client.send(line, host, port)
                        print "sent something back to client at %s:%s" %(host, port)
                    line=""
    except:
        sys.logger.debug("Read loop CRASHED!")
    
    sys.logger.debug("Ended Read Loop")

        
            
