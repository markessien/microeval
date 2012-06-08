
from threading import Thread
import time
import cmd, serial, sys, threading, readline, time, ConfigParser
import wx, os, glob
from wxPython.wx import *
from test_parser import Tester

files_directory = "./logs/"
tester = Tester()

class Terminal():
    
    def __init__(self, display, name):
        self.display = display
        self.name = name
    
    def loadFromFile(self, filename):
        self.file_name = filename
        self.f = open(files_directory + self.file_name, 'r')
        
        for line in self.f.readlines():
            self.process_line(line)
        
    def connect(self, port):
        
        self.file_name = port.replace("/dev/tty", "")
        self.port= port
        
        
        self.open_file()
        
        try:
            self.ser = serial.Serial(port=self.port, baudrate=115200, dsrdtr=0, rtscts=0)
        except serial.serialutil.SerialException:
            self.out("Could not open serial port " + self.port + ". Device not available")
            return
        
        self.ser.setDTR(0)
        self.ser.setRTS(0)
        
        receiver_thread = TerminalReader(self.ser, self) # threading.Thread(target=self.reader, args=(self.ser, self, ))
        receiver_thread.setDaemon(1)
        receiver_thread.start()
        
    def open_file(self):
        
        try:
            self.f.close()
        except:
            pass
            
        self.f = open(files_directory + self.file_name, 'w')
        self.f_read = open(files_directory + self.file_name, 'r')
    
    def send(self, text):
        # self.out(">>> " + text + "\n")
        # tester.trigger_onchanged(self.port + ":LINE", text)
        # try:
        # self.f.flush()
        self.newline_received(text)
        self.ser.write(text)
        # except:
        #    print "Exception"
        
    def read(self, file):
        pass
    
    def out(self, c):
        try:
            if self.f:        
                self.f.write(c)
                self.f.flush()
        except:
            print "No file handle"

    def newline_received(self, theline):
        # theline = self.f_read.readline()
        self.process_line(theline)
    
    def process_line(self, theline):
        theline = theline.strip("\n")
        theline = theline.strip("\r")
        
        console_line = theline
        if (console_line.find('@') >= 0):
            console_line = console_line[0:console_line.find('@')]
        
        console_line = console_line.strip()
        print self.name + ": " + console_line
        self.display.WriteLine(theline)
        tester.trigger_onchanged(self.name + ":LINE", theline)
        
class TerminalReader(Thread):
   def __init__ (self, ser, callback):
      Thread.__init__(self)
      self.ser = ser
      self.callback = callback
      self.cur_line = ""
      
   def run(self):
     while (1):
        c = self.ser.read(1)
        if not c == '\0':
            # self.callback.out(c)
            self.cur_line = self.cur_line + c
            # print c
            
        if c == '\n':
            # Write to file
            self.callback.out(self.cur_line)
            # self.cur_line = ""
            # os.fsync(self.callback.f.fileno())
            wx.CallAfter(self.callback.newline_received, self.cur_line)
            self.cur_line = ""