import wx, os, glob
from wxPython.wx import *
import collections
from terminal import Terminal
from tests_panel import TestsPanel
from deploy_panel import DeployPanel
from network_panel import NetworkPanel
from experiments_panel import ExperimentsPanel

ID_FILE_OPEN = wxNewId()
ID_FILE_CLOSE = wxNewId()
ID_FILE_EXIT = wxNewId()
ID_HELP_ABOUT = wxNewId()
ID_VIEW_TEST = wxNewId()


class BitmapImage(wx.Panel):
    def __init__(self, parent, file_name_pressed, file_name_unpressed, btn_id):
        self.bmp_pressed  = wx.Image(file_name_pressed, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.bmp_unpressed  = wx.Image(file_name_unpressed, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        
        self._bmp = self.bmp_unpressed
        wx.Panel.__init__(self, parent, btn_id, size=(self._bmp.GetWidth(), self._bmp.GetHeight()))
        self.Bind(wx.EVT_PAINT, self.OnPaint)
    
    def SetPressed(self):
        self._bmp = self.bmp_pressed
        self.pressed = True
        self.Refresh()
        self.Update()
        
    def SetUnpressed(self):
        self._bmp = self.bmp_unpressed
        self.pressed = False
        self.Refresh()
        self.Update()
        
    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDC(event.GetEventObject())
        dc.DrawBitmap(self._bmp, 0, 0)

class TerminalPanel(wx.Panel):
    
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        
        main_area = wx.BoxSizer(wx.VERTICAL)
        self.terminal = None
        
        self.textConsole = wx.ListCtrl(self, size=(-1,-1), style=wx.LC_REPORT|wx.BORDER_SUNKEN)
        self.textConsole.InsertColumn(0, 'Output', width=325)
        self.textConsole.InsertColumn(1, 'Line #', width=wx.LIST_AUTOSIZE)
        self.listindex = 0
        
        # Add the send bar at the bottom
        sendbar_area = wx.BoxSizer(wx.HORIZONTAL)
        lblsend = wx.StaticText(self, label="Send:", pos=(20,60))
        self.editsend = wx.TextCtrl(self, value="", pos=(150, 60), size=(100,-1))
        self.editsend.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.editsend.SetFocus()
        sendbar_area.Add(lblsend, 0, wx.ALIGN_CENTER_VERTICAL)
        sendbar_area.Add(self.editsend, 1)

        main_area.Add(self.textConsole, 1, wx.EXPAND|wx.ALL)
        main_area.Add(sendbar_area, 0, wx.EXPAND)
    
        self.listindex = 0
        self.SetSizerAndFit(main_area)
        # .Add(main_area, 1, wx.EXPAND)
       
    def removeNonAscii(self, s): return "".join(filter(lambda x: ord(x)<128, s))
     
    def WriteLine(self, theline):
        theline = self.removeNonAscii(theline)
        
        self.textConsole.InsertStringItem(self.listindex, theline)
        
        
        item = self.textConsole.GetItem(self.listindex)
            
        if theline.find('@') >= 0:
            more_info = theline.split('@', 1)[1]
            self.textConsole.SetStringItem(self.listindex, 1, more_info)
            self.textConsole.SetStringItem(self.listindex, 0, theline.split('@', 1)[0])
            self.textConsole.SetColumnWidth(1, wx.LIST_AUTOSIZE)
            self.textConsole.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        
    
        if theline.find('!') >= 0:
            self.textConsole.SetItemBackgroundColour(self.listindex, "blue")
            self.textConsole.SetItemTextColour(self.listindex, "white")
        elif theline.find('ERROR') >= 0:
            self.textConsole.SetItemBackgroundColour(self.listindex, "red")
            self.textConsole.SetItemTextColour(self.listindex, "white")
        elif theline.find('>>>') >= 0:
            self.textConsole.SetItemBackgroundColour(self.listindex, "white")
            self.textConsole.SetItemTextColour(self.listindex, "black")           
        else:
            self.textConsole.SetItemBackgroundColour(self.listindex, "black")
            self.textConsole.SetItemTextColour(self.listindex, "white")

        self.textConsole.EnsureVisible(self.textConsole.GetItemCount() - 1)
        self.listindex += 1
    
    def OnKeyPress(self, event):
        
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.terminal.send(self.editsend.GetValue().strip() + "\n")
            self.editsend.SetValue("")
            
        event.Skip()
        
class NodeItemPanel(wx.Panel):
    def __init__(self, parent, size, index, cmd):
        wx.Panel.__init__(self, parent, cmd, size)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.index = index
        self.bmp_sensor  = wx.Image("images/sensor.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.green_dot  = wx.Image("images/green_dot.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.red_dot  = wx.Image("images/circle_red.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        
    def OnPaint(self, event):
        dc = wx.PaintDC(event.GetEventObject())
        dc.Clear()
        dc.SetPen(wx.Pen((215,215,215), 1))
        width,height = self.GetSizeTuple()
        if self.index == 0:
            dc.DrawLine(0, 0, width, 0)
        
        dc.DrawLine(0, height-1, width, height-1)
        dc.DrawLine(0, 0, 0, height)
        dc.DrawLine(width-1, 0, width-1, height)
        
        dc.DrawBitmap(self.bmp_sensor, 5, 5)
        
        # if self.index == 3:
        #    dc.DrawBitmap(self.red_dot, 25, 10)
        # else:
        dc.DrawBitmap(self.green_dot, 25, 10)
        
        rect = self.GetClientRect()
        rect.left += 42;
        rect.top += 9;
        dc.SetTextForeground((0, 0, 0))
        dc.DrawLabel("USB" + str(self.index), rect)
    
class wxMicroEvalFrame(wx.Frame):
    
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.Centre()
                                
        file_menu = wxMenu()
        file_menu.Append(ID_FILE_OPEN, 'Open File')
        file_menu.Append(ID_FILE_CLOSE, 'Close File')
        file_menu.AppendSeparator()
        file_menu.Append(ID_FILE_EXIT, 'Exit Program')
        
        view_menu = wxMenu()
        view_menu.Append(ID_VIEW_TEST, 'View Test Panel')
        
        menu_bar = wxMenuBar()    
        menu_bar.Append(file_menu, 'File')
        menu_bar.Append(view_menu, 'View')
        self.SetMenuBar(menu_bar)
        
        EVT_MENU(self, ID_FILE_EXIT, self.OnFileExit)
        

        self.main_box_size = wx.BoxSizer(wx.VERTICAL)        
        self.SetSizerAndFit(self.main_box_size)
    
    def OnFileExit(self, evt):
        dlg = wxMessageDialog(self, 'Exit Program?', 'I Need To Know!',
                              wxYES_NO | wxICON_QUESTION)
        if dlg.ShowModal() == wxID_YES:
            dlg.Destroy()
            self.Close(true)
        else:
            dlg.Destroy()
            
    def onPaintWhitePanel(self, event):
        dc = wx.PaintDC(event.GetEventObject())
        dc.Clear()
        dc.SetPen(wx.Pen((215,215,215), 1))
        width,height = self.GetSizeTuple()
        dc.DrawLine(0, 0, width, 0)
        dc.DrawLine(0, 0, 0, height)
    
    
    def onNavbarClick(self, event):
        self.btn_terminals.SetUnpressed()
        self.btn_deploy.SetUnpressed()
        self.btn_network.SetUnpressed()
        self.btn_tests.SetUnpressed()
        self.btn_experiment.SetUnpressed()
        
    
        if (event.GetId() == 300):
            self.btn_terminals.SetPressed()
            self.white_area.Show()
            self.tests_area.Hide()
            self.deploy_area.Hide()
            self.network_area.Hide()
            self.experiments_area.Hide()
            self.lower_area_sizer.Layout()

        if (event.GetId() == 301):
            self.btn_deploy.SetPressed()
            self.white_area.Hide()
            self.tests_area.Hide()
            self.deploy_area.Show()
            self.network_area.Hide()
            self.experiments_area.Hide()
            self.lower_area_sizer.Layout()
        
        if (event.GetId() == 302):
            self.btn_network.SetPressed()
            self.network_area.Show()
            self.white_area.Hide()
            self.deploy_area.Hide()
            self.tests_area.Hide()
            self.experiments_area.Hide()
            self.lower_area_sizer.Layout()
            
        if (event.GetId() == 303):
            self.btn_tests.SetPressed()
            self.white_area.Hide()
            self.deploy_area.Hide()
            self.network_area.Hide()
            self.tests_area.Show()
            self.experiments_area.Hide()
            
            self.lower_area_sizer.Layout()
            
            
        
        if (event.GetId() == 304):
            self.btn_experiment.SetPressed()
            self.experiments_area.Show()
            self.white_area.Hide()
            self.deploy_area.Hide()
            self.network_area.Hide()
            self.tests_area.Hide()
            
            self.lower_area_sizer.Layout()
    
    def onNodeBarClick(self, event):
        index = event.GetId() - 400
        terminal = self.terminals[index]
        terminal.connect("/dev/ttyUSB" + str(index))
        
    def DrawNodeBars(self):
        self.node_bars = []
        
        for i in range(0, 4):
            node_bar = NodeItemPanel(self.right_bar, size=(200,100), index=i, cmd=400+i)
            node_bar.SetMinSize((100, 35))
            node_bar.SetBackgroundColour((255, 255, 255))
            self.right_bar_sizer.Add(node_bar, 0, wx.LEFT|wx.RIGHT, 10)
            self.node_bars.append(node_bar)
            node_bar.Bind(wx.EVT_LEFT_UP, self.onNodeBarClick)
        
        button = wx.Button(self.right_bar, label=" Flash ", id=602)
        button.Bind(wx.EVT_BUTTON, self.onButtonFlash)
        # button = 
        
        self.right_bar_sizer.Add(button, 0, wx.LEFT|wx.RIGHT|wx.TOP, 10)
        self.right_bar_sizer.Layout()
        

    def onButtonFlash(self, event):
        pass
    
    def DrawTerminals(self):
        
        self.terminal_panels = []
        self.terminals = []
        for i in range(0, 4):
            terminal_panel = TerminalPanel(parent=self.white_area)
            terminal = Terminal(terminal_panel, "USB" + str(i))
            terminal_panel.terminal = terminal
            self.terminals.append(terminal)
            self.terminal_panels.append(terminal_panel)
            
            self.white_area_sizer.Add(terminal_panel, 1, wx.EXPAND)
    
    def OpenNode(self, node_name, terminal_number):
        terminal_panel = self.terminal_panels[terminal_number]
        terminal = self.terminals[terminal_number]
        
        terminal_panel.textConsole.DeleteAllItems()
        terminal.loadFromFile("parallel-wsn-daemon-" + node_name + ".log")
    
    def AddPanels(self):
        # Add bar at the top
        
        self.top_bar = wx.Panel(self, size=(-1,60))
        self.top_bar.SetBackgroundColour((241, 241, 241))
        self.top_bar.SetMaxSize((-1, 200))
        self.top_bar_sizer = wx.BoxSizer(wx.VERTICAL)      
        
        logo_bmp = BitmapImage(self.top_bar, "images/logo2.png", "images/logo2.png", -1)
        self.top_bar_sizer.Add(logo_bmp, 0, wx.EXPAND | wx.ALL, border=10)
        self.top_bar.SetSizerAndFit(self.top_bar_sizer)
        
        self.main_box_size.Add(self.top_bar, 0, wx.EXPAND)
        
        # Add navbar on left
        self.lower_area_sizer = wx.BoxSizer(wx.HORIZONTAL)   
        self.main_box_size.Add(self.lower_area_sizer, 1, wx.EXPAND)
         
        self.nav_bar = wx.Panel(self, size=(240,-1))
        self.nav_bar.SetBackgroundColour((241, 241, 241))
        self.nav_bar.SetMaxSize((100, -1))
        self.nav_bar_sizer = wx.BoxSizer(wx.VERTICAL)      
                
        self.btn_terminals = BitmapImage(self.nav_bar, "images/terminals_pressed.png", "images/terminals_unpressed.png", 300)
        self.btn_terminals.Bind(wx.EVT_LEFT_UP, self.onNavbarClick)
        self.nav_bar_sizer.Add(self.btn_terminals, 0, wx.EXPAND)
        self.btn_terminals.SetPressed()
        
        self.btn_deploy = BitmapImage(self.nav_bar, "images/deploy.png", "images/deploy_unpressed.png", 301)
        self.btn_deploy.Bind(wx.EVT_LEFT_UP, self.onNavbarClick)
        self.nav_bar_sizer.Add(self.btn_deploy, 0, wx.EXPAND)
                        
        self.btn_network = BitmapImage(self.nav_bar, "images/network_pressed.png", "images/network_unpressed.png", 302)
        self.btn_network.Bind(wx.EVT_LEFT_UP, self.onNavbarClick)
        self.nav_bar_sizer.Add(self.btn_network, 0, wx.EXPAND)

        self.btn_tests = BitmapImage(self.nav_bar, "images/tests.png", "images/tests_unpressed.png", 303) 
        self.btn_tests.Bind(wx.EVT_LEFT_UP, self.onNavbarClick)
        self.nav_bar_sizer.Add(self.btn_tests, 0, wx.EXPAND)
        
        self.btn_experiment = BitmapImage(self.nav_bar, "images/experiment.png", "images/experiment_unpressed.png", 304) 
        self.btn_experiment.Bind(wx.EVT_LEFT_UP, self.onNavbarClick)
        self.nav_bar_sizer.Add(self.btn_experiment, 0, wx.EXPAND)
        
        self.lower_area_sizer.Add(self.nav_bar, 0, wx.EXPAND)
        
        # Draw white area
    
        self.white_area = wx.Panel(self, size=(-1,-1))
        self.white_area_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.white_area.Bind(wx.EVT_PAINT, self.onPaintWhitePanel)
        self.white_area.SetBackgroundColour((255, 255, 255))
        self.white_area.SetMaxSize((-1, -1))
        self.lower_area_sizer.Add(self.white_area, 1, wx.EXPAND)
        self.DrawTerminals()
        self.white_area.SetSizerAndFit(self.white_area_sizer)  
    
        self.tests_area = TestsPanel(parent=self)
        self.tests_area_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tests_area.SetMaxSize((-1, -1))
        self.tests_area.SetMinSize((400, 400))
        self.lower_area_sizer.Add(self.tests_area, 1, wx.EXPAND)
        self.tests_area.Hide()
        self.tests_area.terminals = self.terminals
        
        self.deploy_area = DeployPanel(parent=self)
        self.deploy_area.SetMaxSize((-1, -1))
        self.deploy_area.SetMinSize((400, 400))
        self.deploy_area.Hide()
        self.lower_area_sizer.Add(self.deploy_area, 1, wx.EXPAND)
        
        self.network_area = NetworkPanel(parent=self)
        self.network_area.SetMaxSize((-1, -1))
        self.network_area.SetMinSize((400, 400))
        self.network_area.callback = self
        self.network_area.Hide()
        self.lower_area_sizer.Add(self.network_area, 1, wx.EXPAND)
        
        self.experiments_area = ExperimentsPanel(parent=self)
        self.experiments_area.SetMaxSize((-1, -1))
        self.experiments_area.SetMinSize((400, 400))
        self.experiments_area.callback = self
        self.experiments_area.Hide()
        self.lower_area_sizer.Add(self.experiments_area, 1, wx.EXPAND)
        
        self.right_bar = wx.Panel(self, size=(200,-1))
        self.right_bar.SetBackgroundColour((241, 241, 241))
        self.right_bar.SetMinSize((200, -1))
        self.lower_area_sizer.Add(self.right_bar, 0, wx.ALL)
        
        self.right_bar_sizer = wx.BoxSizer(wx.VERTICAL)
        self.DrawNodeBars()
        self.right_bar.SetSizerAndFit(self.right_bar_sizer)  
        self.right_bar.Layout()
        
        self.nav_bar.SetSizerAndFit(self.nav_bar_sizer)
        self.nav_bar.Layout()

class wxMicroEvalApp(wx.App):

    def OnInit(self):
        frame = wxMicroEvalFrame(None, title="MicroEval", size=(900, 700))
        frame.app= self;
        self.SetTopWindow(frame)
        frame.Show()
        
        frame.AddPanels()
        frame.Layout()

        return True
        
if __name__ == "__main__":
    app = wxMicroEvalApp()
    app.MainLoop()