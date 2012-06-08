#! /usr/bin/python

'''
Created on 29.09.2011

@author: schmittb

This is the main file for the daemon that takes care of executing commands on the sensor-nodes.

'''
import os, sys, wsn_controller, communications, optparse, ConfigParser, logging, socket
from logging.handlers import RotatingFileHandler
from daemon import Daemon

comm_client = None
config = None
pidfile = '/tmp/parallel-wsn-daemon.pid'
sys.logger = None
sys.log_lvl = logging.DEBUG #TODO: set to logging.WARNING for production use
        
class parallel_wsn_daemon(Daemon):    
    
    def run (self):
 
        #declare access to global config            
        global config 
        
        #startup the tcp-server and client                    
        global comm_server
        comm_server = communications.CommHandler
        
        global comm_client
        comm_client = communications.CommClient()
        
        #startup the wsn-controller
        global ctrl
        sys.logger.debug("Starting WSN_CONTROLLER Module") #@UndefinedVariable (this is to ignore the error in eclipse)
        ctrl = wsn_controller.controller()
        ctrl.start_serial(config.get("main", "sn_path"), config, comm_client)
        
        #bind server to all valid ip-addresses of this machine
        ip_addr = "0"

        #put tcp-server in own thread    
        sys.logger.debug("starting TCP-Server on ip %s port %s and putting it in own thread" %(ip_addr, int(cp.get("main", "client_port")))) #@UndefinedVariable (this is to ignore the error in eclipse)    
        ch = communications.myTCPServer((ip_addr, int(config.get("main", "daemon_port"))), comm_server, self)
        ch.allow_reuse_address = True
        sys.logger.debug("Waiting for Command-Packets from Client") #@UndefinedVariable (this is to ignore the error in eclipse)
        ch.serve_forever()

    def connection_established(self, client):
        ctrl.connection_available(client)
    
    def connection_terminated(self):
        ctrl.connection_terminated()        

    def process_comm(self, comm_data):
        global ctrl
        ctrl.execute(comm_data)
        
def ensure_dir(f):
    #d = os.path.dirname(f)
    if not os.path.exists(f):
        os.makedirs(f)


if __name__ == "__main__":
    
    #parsing if a config-file-path was passed
    optparser = optparse.OptionParser(usage="usage: %prog [-c] start|stop|restart|status")
    optparser.add_option("-c", "--configfile", dest="cf", type="string", action="store", metavar='config-file', help="specify the path to the config file (default is /etc/parallel-wsn/parallel-wsn-daemon.config)", default="/etc/parallel-wsn/parallel-wsn-daemon.config")
    optparser.add_option('-l', '--logpath', dest='logpath', type='string', action='store', help='define path to the logfile (default is $HOME/logs/)')
    optparser.add_option('-v', '--verbose', dest='verbose', action='store_true', help='turn on warning and diagnostic messages (OPTIONAL)')
      
    (options, args) = optparser.parse_args(sys.argv)

    if options.verbose:
        sys.log_lvl = logging.DEBUG
            
    #init parser to parse the config-file  
    cp = ConfigParser.RawConfigParser()
    if options.verbose:
        print ("reading configuration file from %s" %options.cf) #@UndefinedVariable (this is to ignore the error in eclipse)
    res = cp.read(options.cf)

    if len(res) == 0:
        print "Could not read config-file at %s!\n" % options.cf
        sys.exit(-1)
    else:
        config = cp
        pidfile = config.get("main", "pidfile")
            
    sys.logger = logging.getLogger('parallel-wsn-daemon')
    sys.logger.setLevel(sys.log_lvl) #@UndefinedVariable (this is to ignore the error in eclipse)
    if options.logpath:
        logfile = options.logpath.rstrip('/')+'/parallel-wsn-daemon-'+socket.gethostname()+'.log'
        ensure_dir(options.logpath)
    else:
        path = cp.get("main", "logpath")
        if path[0] == "$":
            envvar = os.getenv(path.split()[0][1:]) 
            if len(path.split()) > 1:
                path = envvar + path.split()[1]
            else:
                path = envvar
        ensure_dir(path)
        logfile = path.rstrip('/') + '/parallel-wsn-daemon-'+socket.gethostname()+'.log'
        if options.verbose:
            print "logging to: %s" %logfile
    lfh = RotatingFileHandler(logfile, mode='a', maxBytes=1000000, backupCount=5)        
    sys.logger.addHandler(lfh) #@UndefinedVariable (this is to ignore the error in eclipse)
    formatter = logging.Formatter('%(asctime)s %(message)s')
    lfh.setFormatter(formatter)
    #don't log to console
    sys.logger.propagate = False 
    
    #if starting or restarting - (re-)read the configuration and write new logfile
    if (args[1] == 'start' or args[1] == 'restart'):
        #on init start a new file if existing one is not empty
        if os.path.getsize(logfile) > 0:
            lfh.doRollover()
    
    #check the daemon commands
    if options.verbose:
        daemon = parallel_wsn_daemon(pidfile, sys.stdin, sys.stdout, sys.stderr)
    else:
        daemon = parallel_wsn_daemon(pidfile)
    if len(args) == 2:
            if 'start' == args[1]:
                sys.logger.debug("Received Signal to start the daemon") #@UndefinedVariable (this is to ignore the error in eclipse)
                daemon.start()                
            elif 'stop' == args[1]:
                sys.logger.debug("Received Signal to stop the daemon") #@UndefinedVariable (this is to ignore the error in eclipse)
                daemon.stop()
            elif 'restart' == args[1]:
                sys.logger.debug("Received Signal to restart the daemon") #@UndefinedVariable (this is to ignore the error in eclipse)
                daemon.restart()
            elif 'status' == args[1]:
                sys.logger.debug("Printing status of daemon") #@UndefinedVariable (this is to ignore the error in eclipse)
                daemon.status()
            else:
                optparser.print_usage()
                sys.exit(2)
            sys.exit(0)
    else:
            print "usage: %s [options] start|stop|restart|status" % sys.argv[0]
            sys.exit(2)

    
    
    
