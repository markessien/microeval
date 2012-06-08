#!/usr/bin/python
# -*- coding: utf-8 -*-

import cmd, serial, sys, threading, readline, time, ConfigParser
import wx, os, glob
from threading import Thread
from datetime import datetime
from pylab import *
from wxPython.wx import *
from microeval_tests import *
import numpy as num
import collections
from terminal_file import TerminalFile

matplotlib.interactive( True )
matplotlib.use( 'WXAgg' )

ID_FILE_OPEN = wxNewId()
ID_FILE_CLOSE = wxNewId()
ID_FILE_EXIT = wxNewId()
ID_HELP_ABOUT = wxNewId()
ID_VIEW_TEST = wxNewId()

   
				
class TokenProcessor:
	
	def __init__(self):
		self.current_word = ""
		self.last_word = ""
		self.current_line = ""
		self.item_bg_color = "black"
		self.item_txt_color = "green"
		self.sent_a_newline = False
		self.make_bold = False
	
	def on_new_line_started(self):
		self.sent_a_newline = False
		self.item_bg_color = "black"
		
		if not self.item_txt_color == "green": # output is green till we start logging
			self.item_txt_color = "white"
		self.current_line = ""
	
	def removeNonAscii(self, s): 
		return "".join(i for i in s if (ord(i)<=126 and ord(i)>=32))
		
	def receive_char(self, c):
		if self.sent_a_newline:
			self.on_new_line_started()
			
		if c == ' ' or c == '\n' or c == '\r':
			self.last_word = self.current_word
			self.current_word = ""
		else:
			self.current_word = self.current_word + c
		
		#if ord(c) < 128:
		self.current_line = self.current_line + self.removeNonAscii(c)
		
		if self.last_word == "->":
			self.item_txt_color = "blue"
		
		if self.last_word == "==":
			self.make_bold = True
		
		if self.last_word.find("ERROR") >= 0:
			self.item_txt_color = "red"
		
		if c == '\n':
			self.sent_a_newline = True
			self.current_line=self.removeNonAscii(self.current_line)

			return True
		else:
			return False


class Terminal:
	
	def __init__(self, parent_win, parent_sizer, index):
		self.ser = None
		self.parent_win = parent_win
		self.parent_sizer = parent_sizer
		self.processor = TokenProcessor()
		self.ports = []
		self.index = index
		self.tests = None
		self.last_val = 0
		self.terminal_file = TerminalFile()
	
	def __str__(self):
		return "Terminal " + str(self.index)
	
	def create_sensor_bar(self, main_area):
		sensorbar_area = wx.BoxSizer(wx.HORIZONTAL)
		main_area.Add(sensorbar_area, 0, wx.EXPAND)
		
		i = 0
		for filename in glob.glob("/dev/ttyUSB*"):
			sensor_button = wx.Button(self.parent_win, label=filename.replace("/dev/tty", ""), id=wx.ID_FILE1+i)
			sensorbar_area.Add(sensor_button, 1)
			sensor_button.Bind(wx.EVT_BUTTON, self.onConnect)
			sensorbar_area.AddSpacer((5,0))
			self.ports.append(filename)
			i = i + 1

	def create_controls(self):
		
		# This will create the terminal area for a single sensor
		main_area = wx.BoxSizer(wx.VERTICAL)
		self.create_sensor_bar(main_area)
		
		self.textConsole = wx.ListCtrl(self.parent_win, size=(-1,100), style=wx.LC_REPORT|wx.BORDER_SUNKEN)
		self.textConsole.InsertColumn(0, 'Main Thread', width=325)
		self.textConsole.InsertColumn(1, 'More Info', width=wx.LIST_AUTOSIZE)
		self.listindex = 0
		
		# Add the send bar at the bottom
		sendbar_area = wx.BoxSizer(wx.HORIZONTAL)
		lblsend = wx.StaticText(self.parent_win, label="Send:", pos=(20,60))
		self.editsend = wx.TextCtrl(self.parent_win, value="", pos=(150, 60), size=(140,-1))
		self.editsend.Bind(wx.EVT_CHAR, self.OnKeyPress)
		self.editsend.SetFocus()
		sendbar_area.Add(lblsend, 0, wx.ALIGN_CENTER_VERTICAL)
		sendbar_area.Add(self.editsend, 1)

		main_area.Add(self.textConsole, 3, wx.EXPAND)
		main_area.Add(sendbar_area, 0, wx.EXPAND)
		
		self.parent_sizer.Add(main_area, 1, wx.EXPAND)
		
		theta = num.arange( 0, 45*2*num.pi, 0.02 )
		

		
	def OnKeyPress(self, event):
		
		# self.graph_panel.
		# for profiling
		
		if event.GetKeyCode() == wx.WXK_RETURN:
			self.out(self.editsend.GetValue().strip() + "\n")
			
			if self.ser:
				self.ser.write(self.editsend.GetValue().strip() + "\n")
			self.editsend.SetValue("")
			
		event.Skip()
	
	def sendKeystrokes(self, text_to_send, to_serial):
		self.add_to_list(text_to_send + "\n")
		
		if (to_serial == True):
			if self.ser == None:
				self.tests.test_failed(self)
				self.add_to_list("No serial port")
			else:
				self.ser.write(text_to_send + "\n")
		
	def onConnect(self, event):
	
		button_id = event.GetId()
		clicked_button = self.parent_win.FindWindowById(button_id)
		self.port = self.ports[button_id - wx.ID_FILE1]
		self.terminal_file.open("log" + self.port.replace("/dev/tty", ""))
		
		try:
			self.ser = serial.Serial(port=self.port, baudrate=115200, dsrdtr=0, rtscts=0)
		except serial.serialutil.SerialException:
			self.out("Could not open serial port " + self.port + ". Device not available")
			return
		
		self.ser.setDTR(0)
		self.ser.setRTS(0)
		
		# start serial->console thread
		# self.reader = TerminalReader()
		receiver_thread = TerminalReader(self.ser, self) # threading.Thread(target=self.reader, args=(self.ser, self, ))
		receiver_thread.setDaemon(1)
		receiver_thread.start()

	def add_to_list(self, str):
		self.textConsole.InsertStringItem(self.listindex, str)
		item = self.textConsole.GetItem(self.listindex)
		
		self.textConsole.SetStringItem(self.listindex, 1, "-")
		# self.textConsole.SetItemBackgroundColour(self.listindex, self.processor.item_bg_color)
		# self.textConsole.SetItemTextColour(self.listindex, self.processor.item_txt_color)
		# self.textConsole.SetColumnWidth(0, wx.LIST_AUTOSIZE)
		self.listindex += 1
			
	def out(self, c):
			
		self.terminal_file.write(c)
			
		if self.processor.receive_char(c) == True:	
			print "Received line:" + self.processor.current_line
			
			
			self.tests.data_received(self, c, self.processor.current_line)
			
			# line = "Line %s" % self.listindex
			self.textConsole.InsertStringItem(self.listindex, self.processor.current_line)
			item = self.textConsole.GetItem(self.listindex)
			
			if self.processor.current_line.find('@') >= 0:
				more_info = self.processor.current_line.split('@', 1)[1]
				self.textConsole.SetStringItem(self.listindex, 1, more_info)
				self.textConsole.SetStringItem(self.listindex, 0, self.processor.current_line.split('@', 1)[0])
				self.textConsole.SetColumnWidth(1, wx.LIST_AUTOSIZE)
			
			if self.processor.current_line.find('# !') >= 0:
				self.textConsole.SetItemBackgroundColour(self.listindex, "blue")
			else:
				self.textConsole.SetItemBackgroundColour(self.listindex, self.processor.item_bg_color)
			self.textConsole.SetItemTextColour(self.listindex, self.processor.item_txt_color)

			
			if self.processor.make_bold == True:
				font = item.GetFont()
				font.SetWeight(wx.FONTWEIGHT_BOLD)
				item.SetFont(font)
				
			self.textConsole.EnsureVisible(self.textConsole.GetItemCount() - 1)
			self.listindex += 1
			
			# print "In out : " + self.processor.current_line[:7]
			if (not self.processor.current_line.find("//start") == -1):
				self.timing = []
				self.last_val = -1
				print "found start"
				for i in range(0, 100):
					self.timing.append(0)
				
			
			if (not (self.processor.current_line.find("//sent")) == -1):
				val = int(self.processor.current_line.split(':')[2])
				if self.last_val == -1:
					self.last_val = val
				
				"""
				time_diff = val - self.last_val
				self.last_val = val
				self.timing.append(time_diff)
				
				if len(self.timing) > 100:
					self.timing.pop(0)
				
				# for i in arange(1,200):
					# sin(x+i/10.0)
				# deque(['apple','orange','grape','banana','mango'], maxlen=5)
				
				print "timing length =" + str(len(self.timing))
				x = arange(0,100,0.1)  
				
				x1 = self.timing
				print x1
				self.line.set_ydata(x1)  # update the data
					# draw()		   self.timing			  # redraw the canvas self.timing
				self.graph_panel.figure.canvas.draw()
				"""
			
				# print self.timing
		else:
			if not self.tests == None:
				self.tests.data_received(self, c, None)
				
class TerminalReader(Thread):
   def __init__ (self, ser, callback):
	  Thread.__init__(self)
	  self.ser = ser
	  self.callback = callback
	  
   def run(self):
	 while (1):
		c = self.ser.read(1)
		wx.CallAfter(self.callback.out, c)
		   
class wxMicroEvalFrame(wx.Frame):
	
	def __init__(self, *args, **kwargs):
		wx.Frame.__init__(self, *args, **kwargs)
		self.Centre()
								
		self.playImage  = wx.Image("play.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		self.failImage  = wx.Image("failed.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		self.passImage  = wx.Image("passed.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		self.alertImage  = wx.Image("alert.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()


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
		
		EVT_MENU(self, ID_VIEW_TEST, self.OnViewTestPanel)
		EVT_MENU(self, ID_FILE_EXIT, self.OnFileExit)
		
		self.terminals = []
		self.terminal_splitter = wx.BoxSizer(wx.HORIZONTAL)		
		self.SetSizerAndFit(self.terminal_splitter)
	
	def OnFileExit(self, evt):
		dlg = wxMessageDialog(self, 'Exit Program?', 'I Need To Know!',
							  wxYES_NO | wxICON_QUESTION)
		if dlg.ShowModal() == wxID_YES:
			dlg.Destroy()
			self.Close(true)
		else:
			dlg.Destroy()
			
	def OnViewTestPanel(self, evt):
		# dlg = wxMessageDialog(self, 'Test View', 'I Need To Know!',
		#					  wxYES_NO | wxICON_QUESTION)
		# dlg.ShowModal()
		self.AddTestsPanel()
    
	def AddTestsPanel(self):
		self.tests = MicroEvalTests(self)
		self.tests.add_tests()
		self.tests.app = self.app;
		
		self.test_holder = wx.BoxSizer(wx.VERTICAL)	
		self.tests_panel = wx.Panel(self, size=(240,-1))
		self.terminal_splitter.Add(self.tests_panel, 0, wx.EXPAND)
		# lbltitle = wx.StaticText(self.tests_panel, label="Sensor Board Tests", pos=(5,5))
		## self.test_holder.Add(lbltitle)
		## self.test_holder.AddSpacer((5,20))
		
		# no size given, so the text determines the needed label size	   
		combo_label = wx.StaticText(self.tests_panel, -1, "Sensor Board Tests. Sender:", (10, 10))
		# create a combo box to select units of measurement to convert from
		self.combo_terminals = wx.ComboBox(self.tests_panel, -1, value="No terminals", pos=wx.Point(10, 30),
			size=wx.Size(150, 26), choices=self.terminals)
		
		self.test_holder.Add(combo_label)
		self.test_holder.Add(self.combo_terminals)
		self.test_holder.AddSpacer((5,20))
		for test in self.tests.tests:
			lblsend = wx.StaticText(self.tests_panel, label=test.test_name, pos=(10,60))
			button = wx.Button(self.tests_panel, label="Test", id=test.test_id)
			button.Bind(wx.EVT_BUTTON, self.OnTestButtonClicked)
			
			self.test_holder.Add(lblsend)
			
			btn_row = wx.BoxSizer(wx.HORIZONTAL)
			btn_row.AddSpacer((5,0))
			btn_row.Add(button)	
			
			img = wx.StaticBitmap(self.tests_panel, test.test_id+20, self.playImage, (10 + self.playImage.GetWidth(), 5), (self.playImage.GetWidth(), self.playImage.GetHeight()))
			btn_row.Add(img, 0, wx.ALIGN_CENTER_VERTICAL)	
			
			self.test_holder.Add(btn_row)
			
			self.test_holder.AddSpacer((5,10))
			
		self.tests_panel.SetSizerAndFit(self.test_holder)
		
	""" When a test button is clicked, react """
	def OnTestButtonClicked(self, event):
		btn = self.tests_panel.FindWindowById(event.GetId())
		btn.SetLabel("Testing...")
		
		img = self.tests_panel.FindWindowById(event.GetId()+20)
		img.SetBitmap(self.alertImage)
		
		for test in self.tests.tests:
			if (test.test_id == event.GetId()):
				if not test.start_func == None:
					test.start_func(test, self.selected_terminal(), self.terminals)
				else:
					self.test_failed(test.test_id)

	def selected_terminal(self):
		# Return the terminal selected in test combo
		val = self.combo_terminals.GetSelection()
		if val == wx.NOT_FOUND:
			return None
		else:
			return self.terminals[val]
		
	def test_failed(self, test_id):
		btn = self.tests_panel.FindWindowById(test_id)
		btn.SetLabel("Failed!")
		
		img = self.tests_panel.FindWindowById(test_id+20)
		img.SetBitmap(self.failImage)
		
	def test_succeeded(self, test_id):
		btn = self.tests_panel.FindWindowById(test_id)
		btn.SetLabel("Test")
		
		img = self.tests_panel.FindWindowById(test_id+20)
		img.SetBitmap(self.passImage)

	def addTerminal(self):
		t = Terminal(self, self.terminal_splitter, len(self.terminals))
		self.combo_terminals.Append(str(t))
		t.tests = self.tests;
		self.terminals.append(t)
		t.create_controls()
		
		# self.SetSizer(self.terminal_splitter)
		# self.SetMinSize(self.GetSize())
		
class wxMicroEvalApp(wx.App):

	def OnInit(self):
		frame = wxMicroEvalFrame(None, title="MicroEval", size=(800, 600))
		frame.app= self;
		self.SetTopWindow(frame)
		frame.Show()
		frame.AddTestsPanel()
		frame.addTerminal()
		frame.addTerminal()
		frame.addTerminal()
		frame.addTerminal()
		return True
		
if __name__ == "__main__":
	app = wxMicroEvalApp()
	app.MainLoop()
