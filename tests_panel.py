from threading import Thread
import time
import cmd, serial, sys, threading, readline, time, ConfigParser
import wx, os, glob
from wxPython.wx import *
from test_parser import Tester
from terminal import tester

class TestsPanel(wx.Panel):
    
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        
        self.main_area = wx.BoxSizer(wx.HORIZONTAL)
    
        # self.SetBackgroundColour((255, 0, 0))
            
        self.textConsole = wx.ListCtrl(self, size=(300,-1), style=wx.LC_REPORT|wx.BORDER_SUNKEN)
        self.textConsole.InsertColumn(0, 'Result', width=100)
        self.textConsole.SetMaxSize((300, -1))
        self.textConsole.InsertColumn(1, 'Test Description', width=500)
        self.textConsole.Bind(wx.EVT_LEFT_UP, self.onListItemClicked)
        self.listindex = 0
        
        rules_area = wx.BoxSizer(wx.VERTICAL)
        
        button = wx.Button(self, label="Run All Tests", id=501)
        # button.Bind(wx.EVT_BUTTON, self.onButtonClicked)
        rules_area.Add(button, 0, wx.EXPAND)

        button = wx.Button(self, label="Run Selected Test", id=501)
        button.Bind(wx.EVT_BUTTON, self.onRunButtonClicked)
        rules_area.Add(button, 0, wx.EXPAND|wx.BOTTOM, 20)
        
        self.viewingCode = True
        
        button = wx.Button(self, label="Toggle View", id=500)
        button.Bind(wx.EVT_BUTTON, self.onToggleView)
        rules_area.Add(button, 0, wx.EXPAND|wx.BOTTOM|wx.TOP, 20)
        self.editoutput = wx.TextCtrl(self, value="", pos=(150, 60), size=(100,400), style=wx.TE_MULTILINE|wx.TE_PROCESS_TAB|wx.HSCROLL)
        self.editoutput.SetBackgroundColour((0, 0, 0))
        self.editoutput.Hide()
        
        self.lblsend = wx.StaticText(self, label="Test Script Description", pos=(20,60))
        self.editsend = wx.TextCtrl(self, value="", pos=(150, 60), size=(100,-1))
        
        self.lblbody = wx.StaticText(self, label="Test Script Code", pos=(20,60))
        self.editbody = wx.TextCtrl(self, value="", pos=(150, 60), size=(100,400), style=wx.TE_MULTILINE|wx.TE_PROCESS_TAB|wx.HSCROLL)
        rules_area.Add(self.lblsend, 0, wx.EXPAND)
        rules_area.Add(self.editsend, 0, wx.EXPAND)
        rules_area.Add(self.lblbody, 0, wx.EXPAND)
        rules_area.Add(self.editbody, 0, wx.EXPAND)
        rules_area.Add(self.editoutput, 0, wx.EXPAND)
        
        button = wx.Button(self, label="Save", id=501)
        button.Bind(wx.EVT_BUTTON, self.saveTextField)
        rules_area.Add(button, 0, wx.EXPAND)
                 
        self.main_area.Add(self.textConsole, 0, wx.EXPAND)
        self.main_area.Add(rules_area, 1, wx.EXPAND)
        
        self.SetSizerAndFit(self.main_area)
        
        self.scanDirectory()
    
    def saveTextField(self, event):
        fileName = self.editsend.GetValue()
        
        f_write = open("./tests/" + fileName, 'w')
        f_write.write(self.editbody.GetValue())
        f_write.close()
        
        self.scanDirectory()
        wx.MessageBox("Saved test script to " + fileName)
        
    def scanDirectory(self):
        self.textConsole.DeleteAllItems()
        index = 0
        for filename in glob.glob("./tests/*"):
            self.textConsole.InsertStringItem(index, "Not Started")
            self.textConsole.SetStringItem(index, 1, filename.replace("./tests/", ""))
            
            index = index + 1

    def tester_send(self, node_name, text):
        
        for terminal in self.terminals:
            if terminal.name == node_name:
                if text == "RESET":
                    terminal.connect("/dev/tty" + terminal.name)
                else:
                    print "Sending text:" + text
                    terminal.send(text.strip() + "\n")
    
    def test_failed(self, test_index):
        self.textConsole.SetItemText(test_index, "FAILED")
        self.textConsole.SetItemBackgroundColour(test_index, (200,0,0))
                
    def test_passed(self, test_index):
        self.textConsole.SetItemText(test_index, "PASSED")
        self.textConsole.SetItemBackgroundColour(test_index, (0,200,0))
        
    def onListItemClicked(self, event):
        try:
            selected = self.textConsole.GetFirstSelected()
            name = self.textConsole.GetItem(selected, 1).GetText()
            self.editsend.Clear()
            self.editsend.AppendText(name)
            
            f_read = open("./tests/" + name, 'r')
            self.editbody.Clear()
            self.editbody.AppendText(f_read.read())
            f_read.close()
        except:
            pass
        
    def onRunButtonClicked(self, event):
        selected = self.textConsole.GetFirstSelected()
        name = self.textConsole.GetItem(selected, 1).GetText()
        
        self.textConsole.SetItemBackgroundColour(selected, (200,0,0))
        
        tester.load("./tests/" + name)
        tester.run(selected, self)
    
    def refreshOutput(self):
        self.editoutput.SetValue("")
        
        new_text = ""
        for variable, val in tester.globals.iteritems():
            new_text = new_text + "\r\n>> Variable: " + variable + " - " + val
                
        self.editoutput.SetValue(new_text)
                
    def onToggleView(self, event):
        if self.viewingCode == False:
            self.lblbody.SetLabel("Code Editor")
            self.viewingCode = True
            self.editoutput.Hide()
            self.editbody.Show()
        else:
            self.lblbody.SetLabel("Output View")
            self.viewingCode = False
            self.editoutput.Show()
            self.editbody.Hide()
            self.refreshOutput()
            
        self.Layout()