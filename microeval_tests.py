from wxPython.wx import *
import wx

class MicroEvalTests():
    
    class TestData():
        def __init__(self):
            self.test_id = 0
            self.test_name = ""
            self.start_func = None
            self.results_func = None
            self.fail_func = None
            self.terminal_results = {} # stores result for each terminal
            self.running = False;
        
    def __init__(self, callback):
        self.tests = []
        self.callback = callback # used for indicating test succeeded
        
    def get_tests(self):
        return self.tests
    
    def data_received(self, terminal, c, line):
        for test in self.tests:
            if not test.results_func == None:
                test.results_func(test, terminal, c, line)
    
    def test_failed(self, terminal):
        for test in self.tests:
            if not test.fail_func == None:
                test.fail_func(test, terminal)
    
    def test_notify_succeeded(self, test):
        self.callback.test_succeeded(test.test_id)

    def test_notify_failed(self, test):
        self.callback.test_failed(test.test_id)
    
    def test_started(self, test, selected_terminal, terminals):
        test.running = True
        for terminal in terminals: test.terminal_results[terminal] = False
        
        if selected_terminal == None:
            self.test_results_failed(test, None)
            return False
        
        return True
        
    def add_test(self, test_name, start_func=None, results_func=None, fail_func=None):
        t = MicroEvalTests.TestData()
        t.test_name = test_name
        t.test_id = wxNewId()
        t.start_func = start_func
        t.results_func = results_func
        t.fail_func = fail_func;
        self.tests.append(t)
        
    """ Add your tests here"""
    def add_tests(self):
        self.add_test("Latency & Data-Rate (long-running)", self.test_start_latencytest, self.test_results_latencytest)
        self.add_test("Data Transfer", self.test_start_datatransfer, self.test_results_datatransfer, self.test_results_failed)
        self.add_test("Manual Pairwise Key-Refresh", self.test_start_keyrefresh, self.test_results_keyrefresh)
        self.add_test("Global Key-Refresh", self.test_start_global_keyrefresh, self.test_results_global_keyrefresh)
        self.add_test("Timed Key-Refresh (long-running)", self.test_start_timed_keyrefresh, self.test_results_timed_keyrefresh)
        self.add_test("Local Keep-Alive", self.test_start_local_keepalive, self.test_results_local_keepalive)
        self.add_test("Global Keep-Alive (long-running)", self.test_start_global_keepalive, self.test_results_global_keepalive)
        # self.add_test("Sensor added to network", self.test_start_sensor_added, self.test_results_sensor_added)
        self.add_test("Exclusion list", self.test_start_xlist)
        self.add_test("Replay Protection", self.test_start_replay, self.test_results_replay)
        self.add_test("Isolation detection", self.test_start_isolation)
        self.add_test("Attack detection", self.test_start_attack)
        self.add_test("Dynamic Security")
                
    """ Add the functions for your tests here """
    
    def test_start_latencytest(self, test, selected_terminal, terminals):
        if self.test_started(test, selected_terminal, terminals) == False: return
        
        selected_terminal.sendKeystrokes("Starting Latency Test", False)
        selected_terminal.sendKeystrokes("test_latency", True)
    
    def test_results_latencytest(self, test, terminal, character, line):
        if test.running == False:
            return
        
        if not line == None:
            if line.find('LATENCYTEST:WAYPOINT:') > -1:
                print line
                print "It took " + line.split(':')[3] + "ms per packet on average to transfer 25 packets of 49 bytes"
                time_required_in_secs = float(line.split(':')[3]) / 1000000.0
                print "One packet of 49bytes took " + str(time_required_in_secs) + "s"
                byte_speed =  time_required_in_secs / 49.0
                print "The time required for one byte to be sent was " + str(byte_speed) + "s"
                if byte_speed == 0:
                    bytes_in_a_second = 0
                else:
                    bytes_in_a_second = 1.0 / byte_speed
                print "The bytes-per-second on average was " + str(bytes_in_a_second)
                
                self.app.Yield()
                wx.SafeYield(self.callback, True)
            
            if line.find('LATENCYTEST:DONE') > -1:
                self.test_notify_succeeded(test)
            
    """ Tests for data transfer """
    def test_start_datatransfer(self, test, selected_terminal, terminals):
         # This will send some data from one terminal to the other
        if self.test_started(test, selected_terminal, terminals) == False: return
            
        test.terminal_results[selected_terminal] = True
        selected_terminal.sendKeystrokes("Starting Transfer Test", False)
        selected_terminal.sendKeystrokes("ping MICROEVAL_TEST 1 2 3", True)
            
    def test_results_datatransfer(self, test, terminal, character, line):
        if test.running == False:
            return
        
        if not line == None:
            if line.find('PONG:') > -1:
                test.terminal_results[terminal] = True
        
        for t, res in test.terminal_results.items():
            if res == False:
                return # a terminal did not receive results yet
            
        self.test_notify_succeeded(test)
    
    def test_results_failed(self, test, terminal):
        if test.running == False:
            return
        
        self.test_notify_failed(test)
        test.running = False
    
    """ Tests for key refresh """
    def test_start_keyrefresh(self, test, selected_terminal, terminals):
        if self.test_started(test, selected_terminal, terminals) == False: return
        
        test.terminal_results[selected_terminal] = True
        selected_terminal.sendKeystrokes("Starting Key Refresh Test", False)
        selected_terminal.sendKeystrokes("keyrefresh", True)
        
    def test_results_keyrefresh(self, test, terminal, character, line):
        if test.running == False: return
        
        if not line == None:
            # print "Received line: " + line
            
            if line.find("Successfully handled KeyRefresh-Packet") > -1:
                test.terminal_results[terminal] = True
        
        for t, res in test.terminal_results.items():
            if res == False:
                return # a terminal did not receive results yet
            
        self.test_notify_succeeded(test)
        
    """ Test for global key exchange """
    def test_start_global_keyrefresh(self, test, selected_terminal, terminals):
        if self.test_started(test, selected_terminal, terminals) == False: return
        
        test.terminal_results[selected_terminal] = True
        selected_terminal.sendKeystrokes("Starting Global Key Refresh Test", False)
        selected_terminal.sendKeystrokes("keyrefreshgk", True)
   
    def test_results_global_keyrefresh(self, test, terminal, character, line):
        if test.running == False: return
        
        if not line == None:
            print "Received line: " + line
            
            if line.find("received new Global-Key") > -1:
                test.terminal_results[terminal] = True
        
        for t, res in test.terminal_results.items():
            if res == False:
                return # a terminal did not receive results yet
            
        self.test_notify_succeeded(test)
        
    """ Test for timed key exchange """
    def test_start_timed_keyrefresh(self, test, selected_terminal, terminals):
        
        if self.test_started(test, selected_terminal, terminals) == False: return
        
        # After this test is started, it just sits and waits for the appropriate
        # Messages to arrive
        
    def test_results_timed_keyrefresh(self, test, terminal, character, line):
        if test.running == False: return
        
        if not line == None:
            print "Received line: " + line
            
            if line.find("Successfully handled KeyRefresh-Packet") > -1:
                test.terminal_results[terminal] = True
        
        for t, res in test.terminal_results.items():
            if res == False:
                return # a terminal did not receive results yet
            
        self.test_notify_succeeded(test)
        
    """ Local Keep-Alive """
    def test_start_local_keepalive(self, test, selected_terminal, terminals):
        if self.test_started(test, selected_terminal, terminals) == False: return
        
        test.terminal_results[selected_terminal] = True
        selected_terminal.sendKeystrokes("Starting Local Keep-Alive test", False)
        selected_terminal.sendKeystrokes("keepalive", True)
   
    def test_results_local_keepalive(self, test, terminal, character, line):
        if test.running == False: return
        
        if not line == None:
            print "Received line: " + line
            
            if line.find("Received local-keep-alive message") > -1:
                test.terminal_results[terminal] = True
        
        for t, res in test.terminal_results.items():
            if res == False:
                return # a terminal did not receive results yet
            
        self.test_notify_succeeded(test)
        
        
    """ Global Keep-Alive """
    def test_start_global_keepalive(self, test, selected_terminal, terminals):
        if self.test_started(test, selected_terminal, terminals) == False: return
        
        test.terminal_results[selected_terminal] = True
        selected_terminal.sendKeystrokes("Starting Global Keep-Alive test", False)
        selected_terminal.sendKeystrokes("keepaliveg", True)
   
    def test_results_global_keepalive(self, test, terminal, character, line):
        if test.running == False: return
        
        if not line == None:
            print "Received line: " + line
            
            if line.find("Successfully received keep-alive packet") > -1:
                test.terminal_results[terminal] = True
        
        for t, res in test.terminal_results.items():
            if res == False:
                return # a terminal did not receive results yet
            
        self.test_notify_succeeded(test)
        
    def test_start_sensor_added(self, test, selected_terminal, terminals):
        if self.test_started(test, selected_terminal, terminals) == False: return
        
        wx.MessageBox('Unplug a sensor board, then press OK, then plug it back', 'Info', 
                      wx.OK | wx.ICON_INFORMATION)

    
    def test_results_sensor_added(self, test, terminal, character, line):
        if test.running == False: return
        
    def test_start_xlist(self, test, selected_terminal, terminals):
        if self.test_started(test, selected_terminal, terminals) == False: return
        
        test.terminal_results[selected_terminal] = True
        selected_terminal.sendKeystrokes("Starting Exclusion List test", False)
        selected_terminal.sendKeystrokes("xlist 65530", True)
        
        wx.MessageBox('Sender excluded. Pls test transfer functions individually.', 'Info', 
                      wx.OK | wx.ICON_INFORMATION)

        self.test_notify_succeeded(test)
        
    
    def test_start_replay(self, test, selected_terminal, terminals):
        if self.test_started(test, selected_terminal, terminals) == False: return
        
        test.terminal_results[selected_terminal] = True
        selected_terminal.sendKeystrokes("Starting Replay Protection test", False)
        selected_terminal.sendKeystrokes("updatecounter 10", True)
        
        # wx.MessageBox('Sender excluded. Pls test transfer functions individually.', 'Info', 
        #               wx.OK | wx.ICON_INFORMATION)

        # self.test_notify_succeeded(test)
        
    def test_results_replay(self, test, terminal, character, line):
        if test.running == False: return
        
        if not line == None:
            print "Received line: " + line
            
            if line.find("[SEC-ERROR-AE]") > -1:
                test.terminal_results[terminal] = True
        
        for t, res in test.terminal_results.items():
            if res == False:
                return # a terminal did not receive results yet
            
        self.test_notify_succeeded(test)
        
    def test_start_isolation(self, test, selected_terminal, terminals):
        if self.test_started(test, selected_terminal, terminals) == False: return
        
        wx.MessageBox('Unplug one device', 'Info', 
                      wx.OK | wx.ICON_INFORMATION)
    
    def test_start_attack(self, test, selected_terminal, terminals):
        if self.test_started(test, selected_terminal, terminals) == False: return
        
        test.terminal_results[selected_terminal] = True
        selected_terminal.sendKeystrokes("Starting Attack test", False)
        selected_terminal.sendKeystrokes("wrongmacs 100", True)
    