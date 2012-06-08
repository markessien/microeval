from threading import Thread
import time
import cmd, serial, sys, threading, readline, time, ConfigParser
import wx, os, glob
from wxPython.wx import *
from test_parser import Tester
from terminal import tester
import ssh
from settings import *
import subprocess

class DeployPanel(wx.Panel):
    
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        
        self.main_area = wx.BoxSizer(wx.VERTICAL)
        
        buttons_area = wx.BoxSizer(wx.HORIZONTAL)
        
        
        self.lbluser = wx.StaticText(self, label="User:", pos=(40,60))
        self.edituser = wx.TextCtrl(self, value="", pos=(150, 60), size=(100,-1))
        buttons_area.Add(self.lbluser, 0, wx.EXPAND|wx.TOP, 5)
        buttons_area.Add(self.edituser, 0, wx.EXPAND)
        
                
        self.lblpw = wx.StaticText(self, label="Password:", pos=(40,60))
        self.editpw = wx.TextCtrl(self, value="", pos=(150, 60), size=(100,-1),style = wxTE_PASSWORD)
        buttons_area.Add(self.lblpw, 0, wx.EXPAND|wx.TOP, 5)
        buttons_area.Add(self.editpw, 0, wx.EXPAND)
        
        button = wx.Button(self, label="Test (Run ls)", id=501)
        button.Bind(wx.EVT_BUTTON, self.onButtonTest)
        buttons_area.Add(button, 0, wx.EXPAND)
        
        button = wx.Button(self, label="Flash", id=502)
        button.Bind(wx.EVT_BUTTON, self.onButtonFlashNodes)
        buttons_area.Add(button, 0, wx.EXPAND)

        button = wx.Button(self, label="Start P-WSN", id=502)
        button.Bind(wx.EVT_BUTTON, self.onButtonStartParallelWSN)
        buttons_area.Add(button, 0, wx.EXPAND)

        button = wx.Button(self, label="Set Addresses", id=502)
        button.Bind(wx.EVT_BUTTON, self.onButtonSetAddresses)
        buttons_area.Add(button, 0, wx.EXPAND)
        
        button = wx.Button(self, label="Copy Logs...", id=502)
        button.Bind(wx.EVT_BUTTON, self.onButtonCopyLogs)
        buttons_area.Add(button, 0, wx.EXPAND)
                        
        self.editoutput = wx.TextCtrl(self, value="", pos=(150, 60), size=(100,400), style=wx.TE_MULTILINE|wx.TE_PROCESS_TAB|wx.HSCROLL)
        self.editoutput.SetBackgroundColour((0, 0, 0))
        self.editoutput.SetForegroundColour((0, 180, 0))
        
        self.main_area.Add(buttons_area, 0, wx.EXPAND)
        self.main_area.Add(self.editoutput, 1, wx.EXPAND)
    
        self.SetSizerAndFit(self.main_area)
    
    def onButtonCopyLogs(self, event):
        self.editoutput.AppendText("# Connecting...\n")
        wx.Yield()
        # subprocess.call(["scp -P2222 essien@uhu.imp.fu-berlin.de:/home/essien/testbed/parallel-wsn/logs/* /home/mark/Code/2011-Essien-Mark/Src/ukleos/projects/security/microeval/logs/",""],shell=True)
        # os.system("scp -P2222 essien@uhu.imp.fu-berlin.de:/home/essien/testbed/parallel-wsn/logs/* /home/mark/Code/2011-Essien-Mark/Src/ukleos/projects/security/microeval/logs/")
        
        # return 

        s = ssh.Connection(DEPLOY_SERVER, port=DEPLOY_SERVER_PORT, username = self.edituser.GetValue(), password=self.editpw.GetValue())
        self.editoutput.AppendText("# Result=" + str(s) + "\n")
        
        wx.Yield()

        self.editoutput.AppendText("# Copying log files\n")
        
        f = open(LOCAL_ADDRESS_LIST)
        for line in f.readlines():
            wx.Yield()
            line = line.strip('\n')
            log_name = LOG_PREFIX + line + ".log"
            self.editoutput.AppendText("Copying log " + log_name + "\n");
            try:
                s.get(REMOTE_LOG_DIR + log_name,  "./logs/" + log_name)
                self.editoutput.AppendText("...copied\n")
            except:
                self.editoutput.AppendText("...not found\n")
        
        self.editoutput.AppendText("# Files copied.\n")
            
        wx.Yield()
        self.editoutput.AppendText("# Closing Connection\n\n")       
        s.close()
                

    def onButtonSetAddresses(self, event):
        self.editoutput.AppendText("# Connecting...\n")
        s = ssh.Connection(DEPLOY_SERVER, port=DEPLOY_SERVER_PORT, username = self.edituser.GetValue(), password=self.editpw.GetValue())
        self.editoutput.AppendText("# Result=" + str(s) + "\n")
        
        wx.Yield()
        
        self.editoutput.AppendText("# Setting address on nodes\n")
        
        item = 1
        f = open(LOCAL_ADDRESS_LIST)
        for line in f.readlines():
            line = line.strip('\n')
            self.editoutput.AppendText("Setting address on " + line)
            results = s.execute(PARALLEL_WSN_PATH + 'parallel_wsn.py -c ' + PARALLEL_WSN_PATH + 'parallel-wsn.config -H ' + line + ' "set addr 10.' + str(item) + '"')
            
            for result in results:
                self.editoutput.AppendText(result)
                print result
                
            self.editoutput.AppendText("# Set address of " + line + " to 10." + str(item) + "\n")
            item = item + 1
            wx.Yield()
            
        
        self.editoutput.AppendText("# Closing Connection\n\n")       
        s.close()
                  
    def onButtonStartParallelWSN(self, event):
        self.editoutput.AppendText("# Connecting...\n")
        s = ssh.Connection(DEPLOY_SERVER, port=DEPLOY_SERVER_PORT, username = self.edituser.GetValue(), password=self.editpw.GetValue())
        self.editoutput.AppendText("# Result=" + str(s) + "\n")
        
        wx.Yield()
        
        self.editoutput.AppendText("# Starting WSN-Daemon on nodes\n")
        results = s.execute("parallel-ssh -h hosts.txt -t 180 '" + PARALLEL_WSN_PATH_NODE + "parallel_wsn_daemon.py -c " + PARALLEL_WSN_PATH_NODE + "parallel-wsn-daemon.config restart'")
        for result in results:
            self.editoutput.AppendText(result)
            
        wx.Yield()
        self.editoutput.AppendText("# Closing Connection\n\n")       
        s.close()
        
    def onButtonFlashNodes(self, event):
        self.editoutput.AppendText("# Connecting...\n")
        s = ssh.Connection(DEPLOY_SERVER, port=DEPLOY_SERVER_PORT, username = self.edituser.GetValue(), password=self.editpw.GetValue())
        self.editoutput.AppendText("# Result=" + str(s) + "\n")
        
        self.editoutput.AppendText("# Copying hex file...\n")
        wx.Yield()
        
        try:
            # Obviously you should change this path. Be sure to make hex folder (within testbed)
            result = s.put(LOCAL_HEX_FILE, REMOTE_HEX_FILE)
            self.editoutput.AppendText(str(result))
        except:
            self.editoutput.AppendText("# Local file not found!!!\n")
        
        self.editoutput.AppendText("# Copy complete\n")
        self.editoutput.AppendText("# Flashing nodes now (needs about 5 minutes)\n")
        wx.Yield()

        results = s.execute("parallel-ssh -h hosts.txt -t 180 'lpc2k_pgm /dev/ttyUSB0 " + REMOTE_HEX_FILE_NODE + "'")
        for result in results:
            self.editoutput.AppendText(result)
        
        self.editoutput.AppendText("# Closing Connection\n\n")       
        s.close()
    
    def onButtonTest(self, event):
        self.editoutput.AppendText("# Connecting...\n")
        s = ssh.Connection(DEPLOY_SERVER, port=DEPLOY_SERVER_PORT, username = self.edituser.GetValue(), password=self.editpw.GetValue())
        self.editoutput.AppendText("# Result=" + str(s) + "\n")
        
        wx.Yield()
        # s.put('hello.txt')
        # s.get('goodbye.txt')
        self.editoutput.AppendText("# > ls\n")
        results = s.execute('ls')
        for result in results:
            if result:
                self.editoutput.AppendText(result)
        
        self.editoutput.AppendText("# Closing Connection\n\n")
        s.close()