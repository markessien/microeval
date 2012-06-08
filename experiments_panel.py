from threading import Thread
import time
import cmd, serial, sys, threading, readline, time, ConfigParser
import wx, os, glob
from wxPython.wx import *
from test_parser import Tester
from terminal import tester


"""
To use the experimental tab, you need to add a line like this to the output
> EXPERIMENT(DataRate, RTT=%lu)

Run the nodes very normally, and afterwards you can analyse the log files. This
tab will help you extract the experiment values from the log files, it does not
run the actual experiment

Add your comparisons for the experiments in processExperiment

"""
class ExperimentsPanel(wx.Panel):
    
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        
        self.main_area = wx.BoxSizer(wx.VERTICAL)
        
        self.SetBackgroundColour((0, 0, 0))
        
        self.toolbar = wx.BoxSizer(wx.HORIZONTAL)
        
        sampleList = ['Data-Rate', 'Latency', 'Neighbouring', 'NeighbourCount', 'MessagesSent']
        
        # self.editsearch = wx.Tself.comboExperimentsextCtrl(self, value="", pos=(150, 60), size=(200,-1))
        self.comboExperiments = wx.ComboBox(self, -1, "Data-Rate", (15, 30), wx.DefaultSize,sampleList, wx.CB_DROPDOWN)
        
        self.toolbar.Add(self.comboExperiments, 0, wx.EXPAND)
        
        button = wx.Button(self, label="Start", id=502)
        button.Bind(wx.EVT_BUTTON, self.onButtonStart)
        self.toolbar.Add(button, 0, wx.EXPAND)

        button = wx.Button(self, label="Save Results...", id=502)
        button.Bind(wx.EVT_BUTTON, self.onButtonSave)
        self.toolbar.Add(button, 0, wx.EXPAND)
                
        self.editoutput = wx.TextCtrl(self, value="", pos=(150, 60), size=(100,400), style=wx.TE_MULTILINE|wx.TE_PROCESS_TAB|wx.HSCROLL)
        self.editoutput.SetBackgroundColour((255, 255, 255))
        self.editoutput.SetForegroundColour((0, 0, 0))
        
        self.main_area.Add(self.toolbar, 0, wx.EXPAND)
        self.main_area.Add(self.editoutput, 1, wx.EXPAND)
        
        self.SetSizerAndFit(self.main_area)
        
        
    def onButtonStart(self, event):
        
        print "Parsing Experiment"
        
        self.editoutput.SetValue("")
        self.outputtedHeader = False
        self.column1 = {}
        self.column2 = {}
        self.column3 = {}
        result_set = {}
        for filename in glob.glob("logs/*"):
            fhandle = open(filename, 'r')
            
            experiment_name = ""
            node_name = ""
            node_address = ""
            
            filename = filename.replace("logs/", "")
            filename = filename.replace("parallel-wsn-daemon-", "")
            node_name = filename.replace(".log", "")
            
            print "Reading file" + filename
            
            # self.recordOut("\nNODE Name: " + filename)
            line_number = 0
            for line in fhandle.readlines():
                try:
                    line_number = line_number + 1
                    
                    if line.find("Setting address to") >= 0:
                        node_address = line[line.find("Setting address to") + 18:line.find("    ")]
                        # self.processExperiment(node_name, node_address, "", "")
                        self.column1[node_name] = 0 # Not found
                        self.column2[node_name] = 0
                        self.column3[node_name] = 0
                
                        # self.recordOut("NODE Address: " + node_address)
                        
                    if line.find("EXPERIMENT(") >= 0:
                        params = line[line.find("EXPERIMENT(") + len("EXPERIMENT("):]
                        params.strip(")")
                        params = params.split(",")
                        experiment_name = params[0]
                        del params[0]
                        
                        vals = []
                        for item in params:
                            if item.find("@") >= 0:
                                item = item.split("@")[0]
                            item = item.strip()
                            
                            vals.append(item)
                            
                        self.processExperiment(node_name, node_address, experiment_name, vals, line_number)
                except:
                    pass # Ordinal not in range, most likely
            
            fhandle.close()
            
        if self.endExperiment() == True:
            for key, val in self.column1.iteritems():
                col2_val = ""
                col3_val = ""
                if self.column2.has_key(key):
                    col2_val = self.column2[key]
                    
                if self.column3.has_key(key):
                    col3_val = self.column3[key]
                    
                self.recordOut(str(val) + "    " + str(col2_val) + "    " + str(col3_val))
            
        return result_set    
    
    def endExperiment(self):
        selectedExperiment = self.comboExperiments.GetValue()
        
        if (selectedExperiment == "MessagesSent"):
            self.recordOut("# Number of messages sent over network lifetime = " + str(self.messageSendCount))
            return False
            
        if (selectedExperiment == "NeighbourCount"):
            self.recordOut("# Number of neighbours gained over network lifetime = " + str(self.neighbourCount))
            return False

        return True
    
    def processExperiment(self, node_name, node_address, experimentName, experimentValues, line_number):
        
        selectedExperiment = self.comboExperiments.GetValue()
        
        # Print out header part
        if self.outputtedHeader == False:

            if selectedExperiment == "NeighbourCount":
               self.outputtedHeader = True
               self.neighbourCount = 0
               self.recordOut("# This experiment counts the number of neighbours in the entire network")

            if selectedExperiment == "MessagesSent":
               self.outputtedHeader = True
               self.messageSendCount = 0
               self.recordOut("# This experiment counts the number of messages sent in the life-time of network")
                                          
            if selectedExperiment == "Neighbouring":
               self.outputtedHeader = True
               self.radioErrorCount = 0
               self.messageSendCount = 0
               self.recordOut("# This experiment measures the neighbouring behaviour")
               
            if experimentName == "RREQCoverage" and selectedExperiment == "Routing":
                self.outputtedHeader = True
                self.recordOut("# This experiment measures the range of route-requests")
                self.recordOut("# A route-request is started and an observation is made")
                self.recordOut("# how many nodes are able to receive it at least once")
                self.recordOut("# Number of nodes in the network=125")
                self.recordOut("# Each line represents a complete data record for one node.")
                self.recordOut("# The meanings of the columns are as follows:")
                self.recordOut("# column 1: Did this node receive a route request?")
                self.recordOut("# column 2: How many neighbours did it have?")
                self.recordOut("# column 3: Rejected a packet because not neighbour?")
        
            if experimentName == "DataRate" and selectedExperiment == "Data-Rate":
                self.outputtedHeader = True
                self.data_rate_iteration = 0
                self.recordOut("# This experiment measures the data-rate")
                self.recordOut("# Number of nodes in network=4")
                self.recordOut("# ")
                self.recordOut("# Each line represents a complete data record for one node.")
                self.recordOut("# The meanings of the columns are as follows:")
                self.recordOut("# Column 1: Round-trip-time (44 Payload Bytes) in hwtimer ticks")
        
    
            if experimentName == "RadioDataRate" and selectedExperiment == "Data-Rate":
                self.outputtedHeader = True
                self.data_rate_iteration = 0
                self.recordOut("# This experiment measures the unencrypted radio data-rate")
                self.recordOut("# Number of nodes in network=4")
                self.recordOut("# ")
                self.recordOut("# Each line represents a complete data record for one node.")
                self.recordOut("# The meanings of the columns are as follows:")
                self.recordOut("# Column 1: Round-trip-time (44 Payload Bytes) in hwtimer ticks")
            
        if experimentName == "SendError" and selectedExperiment == "Neighbouring":
            self.radioErrorCount += 1
            self.recordOut("# Radio Errors = " + str(self.radioErrorCount))

        if experimentName == "MessagesSent" and (selectedExperiment == "MessagesSent"):
            self.messageSendCount += 1
            return
        
        if experimentName == "NewNeighbour" and (selectedExperiment == "NeighbourCount"):
            self.neighbourCount += 1
            return
        
                        
        if experimentName == "MessageSent" and (selectedExperiment == "Neighbouring" or selectedExperiment == "MessagesCount"):
            self.messageSendCount += 1
            self.recordOut("# Messages Sent = " + str(self.messageSendCount))
                                
        for val in experimentValues:
            
            print experimentName
            print " - " + selectedExperiment
                            
            if experimentName == "RREQCoverage" and selectedExperiment == "Routing":
                if val.find("RREQS=") >= 0:        
                    self.column1[node_name] = val[len("RREQS="):]
                elif val.find("Neighbours=") >= 0:
                    self.column2[node_name] = val[len("Neighbours="):]
                elif val.find("REJECTED=1") >= 0:
                    self.column3[node_name] = 1
            
            if experimentName == "DataRate" and selectedExperiment == "Data-Rate":
                self.data_rate_iteration = self.data_rate_iteration + 1
                if val.find("RTT=") >= 0:
                    rrt_time = val[len("RTT="):]
                    rrt_time = rrt_time.strip(")")
                    self.column1[node_name + str(self.data_rate_iteration)] = rrt_time

            if experimentName == "RadioDataRate" and selectedExperiment == "Data-Rate":
                self.data_rate_iteration = self.data_rate_iteration + 1
                if val.find("RTT=") >= 0:
                    rrt_time = val[len("RTT="):]
                    rrt_time = rrt_time.strip(")")
                    self.column1[node_name + str(self.data_rate_iteration)] = rrt_time
                                        
        # self.recordOut("Experiment line: " + node_name + " " + node_address + " Name: " + experimentName + str(experimentValues))
        
    def recordOut(self, str):
        self.editoutput.AppendText(str + "\n")
        
    def onButtonSave(self, event):
        pass