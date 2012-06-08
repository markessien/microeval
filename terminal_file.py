""" Represents a textfile with the contents of a sensor  board """
from threading import Thread
import time

files_directory = "./logs/"

class TerminalFile():
    
    def open(self, file_path):
        self.f = open(files_directory + file_path, 'w')
        
    def read(self, file):
        pass
    
    def write(self, c):
        self.f.write(c)
        
    
def file_monitoring(i):
    while (1):
        # print "sleeping 5 sec from thread %d" % i
        time.sleep(1)
        # print "finished sleeping from thread %d" % i
    
t = Thread(target=file_monitoring, args=(0,))
t.start()