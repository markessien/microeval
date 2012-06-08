#! /usr/bin/python

'''
Created on 08.02.2012

@author: schmittb

this is the main programm that should be used on uhu to control the sensor nodes
'''
import os, sys, threading, communications, optparse, ConfigParser, hostsParser, time, logging, socket
from logging.handlers import RotatingFileHandler

sys.logger = None
sys.log_lvl = logging.DEBUG #TODO: set to logging.WARNING for production use

class tcp_handler():
    
    def __init__(self, ind_logs, logpath, stdout, curCmd):
        self.individual_logs = ind_logs
        self.path = logpath
        self.stdout = stdout
        self.cmd = curCmd
        if ind_logs:
            sys.logger.debug("Starting SensorNode-Output Log in individual logfile mode. Writing logfiles to: %s " %self.path) #@UndefinedVariable (this is to ignore the error in eclipse)
            self.loggerdict = dict()
        else:
            sys.logger.debug("Starting SensorNode-Output Log in cumulative logfile mode. Writing logfile to: %s " %self.path) #@UndefinedVariable (this is to ignore the error in eclipse)
            #initialize the sensor node logger
            logfile = logpath.rstrip('/')+'/parallel-wsn-sensornodes.log'
            self.snlogger = logging.getLogger('sensornode')
            self.snlogger.setLevel(logging.DEBUG)
            lfh = RotatingFileHandler(logfile, mode='a', maxBytes=1000000, backupCount=5)        
            self.snlogger.addHandler(lfh) #@UndefinedVariable (this is to ignore the error in eclipse)
            formatter = logging.Formatter('%(asctime)s %(message)s')
            lfh.setFormatter(formatter)
            #don't log to console
            self.snlogger.propagate = False
            #on init start a new file if existing one is not empty
            if os.path.getsize(logfile) > 0:
                lfh.doRollover()
                
    def create_ind_logfile(self, node_name):
        #initialize this sensor node's logger
        logfile = self.path.rstrip('/')+'/parallel-wsn-'+node_name+'.log'
        snlogger = logging.getLogger(node_name)
        snlogger.setLevel(logging.DEBUG)
        lfh = RotatingFileHandler(logfile, mode='a', maxBytes=1000000, backupCount=5)        
        snlogger.addHandler(lfh) #@UndefinedVariable (this is to ignore the error in eclipse)
        formatter = logging.Formatter('%(asctime)s %(message)s')
        lfh.setFormatter(formatter)
        
        #don't log to console
        sys.logger.propagate = False
        
        #on init start a new file if existing one is not empty
        if os.path.getsize(logfile) > 0:
            lfh.doRollover()
            
        return snlogger 
    
    def process_comm(self, packet):
        if self.stdout:
            if not packet.data == ">" and not packet.data==self.cmd:
                print socket.gethostbyaddr(packet.client_address[0])[1][0]+':\t'+packet.data
        if not self.individual_logs:    #all in one logfile - add hostname for overview
            self.snlogger.debug(socket.gethostbyaddr(packet.client_address[0])[1][0]+':\t'+packet.data)
        else:                           #individual logfiles - create logger if it doesn't exist yet
            if packet.client_address[0] in self.loggerdict:    #if a logger has been created for this sensornode - just log
                self.loggerdict[packet.client_address[0]].debug(packet.data.rstrip('\n'))
            else:                                           # else create the logger and then log
                self.loggerdict[packet.client_address[0]] = self.create_ind_logfile(packet.client_address[0])
                self.loggerdict[packet.client_address[0]].debug(packet.data.rstrip('\n'))
        
            
def ensure_dir(f):
    #d = os.path.dirname(f)
    if not os.path.exists(f):
        os.makedirs(f)            

class pwsn_client():
    
    def run(self):     
        
        optparser = optparse.OptionParser(usage="usage: %prog [-chHl] start|stop|restart|status", conflict_handler='resolve')
        optparser.add_option('-c', '--configfile', dest='cf', type='string', action='store', metavar='config-file', help='specify the path to the config file (default is ./parallel-wsn.config)', default=(str(os.getcwd())+'/parallel-wsn.config'))
        optparser.add_option('-l', '--logpath', dest='logpath', type='string', action='store', help='define the path for the logfiles (default is ./ (CWD))') 
        optparser.add_option('-h', '--hosts', dest='host_files', action='append', metavar='HOST_FILE', help='hosts file (each line "[user@]host[:port]")')
        optparser.add_option('-H', '--host', dest='host_strings', action='append',metavar='HOST_STRING', help='additional host entries ("[user@]host[:port]")')
        optparser.add_option('-u', '--user', dest='user', help='username (OPTIONAL)')
        optparser.add_option('-t', '--waiting-time', dest='waiting_time', help='define the time in seconds for parallel-wsn to wait for answers from the sensor nodes (OPTIONAL)')
        optparser.add_option('-v', '--verbose', dest='verbose', action='store_true', help='turn on warning and diagnostic messages (OPTIONAL)')        
        
        (options, args) = optparser.parse_args(sys.argv)
        print options
        print args
        
        #check if verbose option was set
        if options.verbose:
            sys.log_lvl = logging.DEBUG
            
        #init parser to parse the config-file  
        cp = ConfigParser.RawConfigParser()
        print ("reading configuration file from %s" %options.cf) #@UndefinedVariable (this is to ignore the error in eclipse) #TODO: if verbose...
        res = cp.read(options.cf)    
        if len(res) == 0:
            print "Could not read config-file at %s!\n" % options.cf        
            sys.exit(-1)
            
        #initialize the logger
        if options.logpath:
            path = options.logpath.rstrip('/')
            ensure_dir(path)
        else:
            path = cp.get("main", "logpath")
            if path[0] == "$":
                envvar = os.getenv(path.split()[0][1:]) 
                if len(path.split()) > 1:
                    path = envvar + path.split()[1]
                else:
                    path = envvar
        print path
        ensure_dir(path)
        logfile = path.rstrip('/') + '/parallel-wsn-'+socket.gethostname()+'.log'
        if options.verbose:
            print "logging to: %s" %logfile
            
        sys.logger = logging.getLogger('parallel-wsn')
        sys.logger.setLevel(sys.log_lvl) #@UndefinedVariable (this is to ignore the error in eclipse)
        lfh = RotatingFileHandler(logfile, mode='a', maxBytes=1000000, backupCount=5)        
        sys.logger.addHandler(lfh) #@UndefinedVariable (this is to ignore the error in eclipse)
        formatter = logging.Formatter('%(asctime)s %(message)s')
        lfh.setFormatter(formatter)
        #don't log to console
        sys.logger.propagate = False
        #on init start a new file if existing one is not empty
        if os.path.getsize(logfile) > 0:
            lfh.doRollover()
                       
        global comm_server
        comm_server = communications.ClientCommHandler
        
        global comm_client
        comm_client = communications.CommClient()
        
        if not args[1]:
            print "No command specified!"
            sys.logger.error("No command specified") #@UndefinedVariable (this is to ignore the error in eclipse)
            sys.exit(-1)
        
        if cp.get("main", "individual_logfiles") == "yes":
            handler = tcp_handler(True, path.rstrip('/'), cp.get("main", "stdout"), args[1])
        else:
            handler = tcp_handler(False, path.rstrip('/'), cp.get("main", "stdout"), args[1])
        
        if os.uname()[1] == "uhu":
            #bind server only to the VLAN ip-address so that nobody outside can access the server
            ip_addr = communications.ip_address().get_ip_address("br-meshnet")
        else:
            #not running on huhu - bind server to all valid ip-addresses of this machine
            ip_addr = "0"
        
        #server in own thread
        sys.logger.debug("starting TCP-Server on ip %s port %s and putting it in own thread" %(ip_addr, int(cp.get("main", "client_port")))) #@UndefinedVariable (this is to ignore the error in eclipse)    
        ch = communications.myTCPServer((ip_addr, int(cp.get("main", "client_port"))), comm_server, handler)
        ch.allow_reuse_address = True
        ch_thread = threading.Thread(target=ch.serve_forever)
        ch_thread.setDaemon(1)
        ch_thread.start()
        
        #parse the passed hosts
        sys.logger.debug("parsing the hosts_file at %s" %options.host_files) #@UndefinedVariable (this is to ignore the error in eclipse)
        hosts = hostsParser.read_host_files(options.host_files)
         
        #if additional host_strings were defined add them too
        if options.host_strings:
            sys.logger.debug("parsing the additional hosts string %s" %options.host_strings) #@UndefinedVariable (this is to ignore the error in eclipse)
            for host_string in options.host_strings:
                res = hostsParser.parse_host_string(host_string)
                if res:
                    hosts.extend(res)
        
        if not hosts:
            print "No Hosts specified!"
            sys.logger.error("No hosts were specified in either a file or the string (-h or -H option)") #@UndefinedVariable (this is to ignore the error in eclipse)
            sys.exit(-1)
        
        if options.verbose:            
            print hosts
        
        daemon_port = cp.get("main", "daemon_port")
        sys.logger.debug("sending command to the host(s) now") #@UndefinedVariable (this is to ignore the error in eclipse)
        for host in hosts:
            if options.verbose:
                print "sending %s, %s, %s" %(args[1], str(host[0]), (host[1] if host[1] else daemon_port))
            sys.logger.debug("sending %s, %s, %s" %(args[1], str(host[0]), (host[1] if host[1] else daemon_port))) #@UndefinedVariable (this is to ignore the error in eclipse)
            try:
                comm_client.send(args[1], str(host[0]), (host[1] if host[1] else daemon_port))
            except:
                sys.logger.error("Couldn't send %s to %s" %(args[1], str(host[0]))) #@UndefinedVariable (this is to ignore the error in eclipse)
                print ("Couldn't send %s to %s" %(args[1], str(host[0])))
        
        if options.verbose:
            print "waiting for answers"
        if options.waiting_time:
            sys.logger.debug("waiting %s seconds for answers" %options.waiting_time) #@UndefinedVariable (this is to ignore the error in eclipse)
            time.sleep(float(options.waiting_time))
        else:
            sys.logger.debug("waiting %s seconds for answers" %cp.get("main", "waiting_time")) #@UndefinedVariable (this is to ignore the error in eclipse)
            time.sleep(float(cp.get("main", "waiting_time")))
        
        sys.logger.debug("shutting down TCP-Server and exiting system now") #@UndefinedVariable (this is to ignore the error in eclipse)
        ch.server_close()
        ch.shutdown()
    

if __name__ == '__main__':

    client = pwsn_client()
    client.run()
    
