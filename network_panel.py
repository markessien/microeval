from threading import Thread
import time
import cmd, serial, sys, threading, readline, time, ConfigParser
import wx, os, glob
from wxPython.wx import *
from test_parser import Tester
from terminal import tester
import ssh
import scriptutil as SU
import re

class NetworkPanel(wx.Panel):
    
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        
        self.main_area = wx.BoxSizer(wx.VERTICAL)
        
        self.toolbar = wx.BoxSizer(wx.HORIZONTAL)
        self.loadComboList()
        
        # self.editsearch = wx.TextCtrl(self, value="", pos=(150, 60), size=(200,-1))
        self.comboSearch = wx.ComboBox(self, -1, "", (15, 30), wx.DefaultSize,self.comboList, wx.CB_DROPDOWN)
        self.toolbar.Add(self.comboSearch, 0, wx.EXPAND)
        
        button = wx.Button(self, label="Search and Highlight", id=502)
        button.Bind(wx.EVT_BUTTON, self.onButtonSearch)
        self.toolbar.Add(button, 0, wx.EXPAND)

        button = wx.Button(self, label="Reset", id=502)
        button.Bind(wx.EVT_BUTTON, self.onButtonClear)
        self.toolbar.Add(button, 0, wx.EXPAND)

        button = wx.Button(self, label="Toggle Search Results", id=502)
        button.Bind(wx.EVT_BUTTON, self.onButtonToggle)
        self.toolbar.Add(button, 0, wx.EXPAND)
                        
                        
        button = wx.Button(self, label="Rescan", id=503)
        button.Bind(wx.EVT_BUTTON, self.onButtonRescan)
        self.toolbar.Add(button, 0, wx.EXPAND)
        
        self.imagelist = wx.ImageList(width=32, height=32)
        self.imagelist.Add(wx.Image("images/chip.png").ConvertToBitmap())
        
        self.networkNodes = wx.ListCtrl(self, size=(300,-1), style=wx.LC_ICON|wx.BORDER_SUNKEN|wx.LC_SORT_ASCENDING)
        self.networkNodes.AssignImageList(self.imagelist, wx.IMAGE_LIST_NORMAL)
        
        self.networkNodes.InsertColumn(1, 'Test Description', width=500)
        self.networkNodes.SetBackgroundColour((128, 128, 128))
        self.listindex = 0
        
        self.editoutput = wx.TextCtrl(self, value="", pos=(150, 60), size=(100,400), style=wx.TE_MULTILINE|wx.TE_PROCESS_TAB|wx.HSCROLL)
        self.editoutput.SetBackgroundColour((0, 0, 0))
        self.editoutput.SetForegroundColour((0, 180, 0))
        self.editoutput.Hide()
        
        self.main_area.Add(self.toolbar, 0, wx.EXPAND)
        self.main_area.Add(self.networkNodes, 1, wx.EXPAND)
        self.main_area.Add(self.editoutput, 1, wx.EXPAND)
        
        self.SetSizerAndFit(self.main_area)
        
        EVT_LIST_ITEM_RIGHT_CLICK(self.networkNodes, -1, self.onListItemRightClicked )
        
        self.networkNodes.SetForegroundColour((0, 0, 0))
        
        wx.Yield()
        self.scanDirectory()
        
    def loadComboList(self):
        self.comboList = []
        
    def scanDirectory(self):
        self.networkNodes.DeleteAllItems()
        for filename in glob.glob("logs/*"):
            filename = filename.replace("logs/", "")
            filename = filename.replace("parallel-wsn-daemon-", "")
            filename = filename.replace(".log", "")
            self.networkNodes.InsertStringItem(self.listindex, filename, 0)
            self.networkNodes.SetItemData(self.listindex, ord(filename[0]) + ord(filename[1]))
            self.listindex = self.listindex + 1
            
        self.networkNodes.SortItems(self.sortColumn)

    def onButtonRescan(self, event):
        self.scanDirectory()
        
        self.main_area.Layout()
            
    def onButtonToggle(self, event):
        if self.editoutput.IsShown():
           self.editoutput.Hide()
           self.networkNodes.Show()
        else:
            self.networkNodes.Hide()
            self.editoutput.Show()
        
        self.main_area.Layout()
    
    def onButtonClear(self, event):
        print "Clearing nodes..."
        item = -1;
        while 1:
            item = self.networkNodes.GetNextItem(item, wx.LIST_NEXT_ALL)
            if ( item == -1 ):
                break;
            
            self.networkNodes.SetItemTextColour(item, (0, 0, 0))
    
    def sortColumn(self, item1, item2):
        return item1 < item2
        """
        text1 = self.networkNodes.GetItemText(item1)
        text2 = self.networkNodes.GetItemText(item2)
        
        if (ord(text1[0]) > ord(text2[0])):
            return 1
        elif (ord(text1[0]) < ord(text2[0])):
            return -1
        
        return ord(text1[1]) > ord(text2[1])
        """
    
    def searchInFiles(self, str):
        found = False
        for item in self.comboList:
            if item == str:
                found = True
        
        if found == False:
            self.comboList.insert(0, str)
            if len(self.comboList) > 7:
                self.comboList.pop()
        
        self.comboSearch.SetItems(self.comboList)
        
        result_set = {}
        for filename in glob.glob("logs/*"):
            fhandle = open(filename, 'r')
            # fcontent = fhandle.read()
            # print "Searching " + filename
            
            for line in fhandle.readlines():
                # line = line.lower()
                try:
                    # if line.find("Setting address to") >= 0:
                        
                    if line.lower().find(str.lower()) >= 0:
                        # print "Found " + line
                        result_set[filename] = line
                        found = True
                        break
                except:
                    pass # Ordinal not in range, most likely
                
            fhandle.close()
            
        return result_set    
        
    def onButtonSearch(self, event):
        #flist = SU.ffindgrep('.',
        #                     namefs=(lambda s: s.endswith('.log'),),
        #                    regexl=(self.editsearch.GetValue(), re.I))
        
        self.editoutput.SetValue("")
        
        print "--------------- Search Results -------------------"
        search = "" + self.comboSearch.GetValue()
        results = self.searchInFiles(search)
        
        # print str(flist)
        for filename, line in results.items():
            node_name = filename.replace("logs/parallel-wsn-daemon-", "")
            node_name = node_name.replace(".log", "")
            
            line.replace("             ", "")
            line.replace("             ", "")
            
            if line.find("#") >= 0:
                linearray = line.split("#")
                # linearray[2] = line.split("@")
                line = linearray[1]
            
            
            line = line.strip()
            
            if line.find("@") >= 0:
                line = line.split("@")[0]
            
            result =  "Node: " + node_name + "   >>> " + line 
            print result
            
            self.editoutput.AppendText(result+ "\n")
            
            item = self.networkNodes.FindItem(0, node_name)
            if item >= 0:
                self.networkNodes.SetItemTextColour(item, (255, 0, 0))
            
        # print str(flist)
        
    def onListItemRightClicked(self, event):
        
        menu = wxMenu()
        menu.Append( 700, "Open in terminal1" )
        menu.Append( 701, "Open in terminal2" )
        menu.Append( 702, "Open in terminal3" )
        menu.Append( 703, "Open in terminal4" )
        
        EVT_MENU( menu, 700, self.MenuSelectionCb )
        EVT_MENU( menu, 701, self.MenuSelectionCb )
        EVT_MENU( menu, 702, self.MenuSelectionCb )
        EVT_MENU( menu, 703, self.MenuSelectionCb )
        
        self.PopupMenu( menu, event.GetPoint() )
        menu.Destroy() # destroy to avoid mem leak
  
    def MenuSelectionCb( self, event ):
        selected = self.networkNodes.GetFirstSelected()
        node_name = self.networkNodes.GetItemText(selected)
        
        terminal_numer = event.GetId() - 700;
        self.callback.OpenNode(node_name, terminal_number=terminal_numer)
  