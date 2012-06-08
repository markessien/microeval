import re

def comment(scanner, token):  return "COMMENT", token
def identifier(scanner, token): return "IDENT", token
def comparison(scanner, token):   return "COMPARISON", token
def operator(scanner, token):   return "OPERATOR", token
def digit(scanner, token):      return "DIGIT", token
def end_stmnt(scanner, token):  return "END_STATEMENT", token
def quoted(scanner, token):  return "QUOTE", token
def onchanged(scanner, token):  return "ONCHANGED", token
def ifblock(scanner, token):  return "IF", token
def endblock(scanner, token):  return "ENDBLOCK", token
def onsend(scanner, token):  return "EXEC", token

scanner = re.Scanner([
    (r"--(.*)", comment),
    (r"if(.*)", ifblock),
    (r"}", endblock),
    (r"exec(.*)", onsend),
    (r"onchanged(.*)", onchanged),
    (r"'[a-zA-Z_]'\w*", identifier),
    (r"[a-zA-Z_]\w*", identifier),
    (r"\=\=", comparison),
    (r"\"[^\"]+\"", quoted),
    (r"\=", operator),
    (r"[0-9]+(\.[0-9]+)?", digit),
    (r"\n", end_stmnt),
    (r"\s+", None),
    ])

""" Class that takes a test script and executes and parses it """
class Tester():
    
    # A single or group of nodes
    class Node():
        def __init__(self, node_name):
            self.sends =  [] # List of all the sends as Send() objects
            self.node_name = node_name
        
    
    def __init__(self):
        self.running = False
            
    def load(self, filename):
        self.running = False
        self.nodes = [] # All known nodes (parsed from file)
        self.globals = {} # Global variables
        self.onchanged = {}
        self.in_function_block = False
        self.cur_onchanged_variables = []
        
        f_read = open(filename, 'r')
        lines = f_read.readlines()
        for line in lines:
            self.parse_line(line)
            
        self.print_onchanged()
        print "Done parsing"
        
    def parse_line(self, linestr):
        left_token = ""
        middle_token = ""
        right_token = ""
        tokens, remainder = scanner.scan(linestr)
        for token in tokens:
            key, val = token
            # print token
            if key == "END_STATEMENT":
                left_token = ""
                middle_token = ""
                right_token = ""
            
            if key == "EXEC":
                exec_val = val[6:]
                
                exec_val = exec_val.strip()
                exec_val = exec_val.strip("'")
                
                print ">> Adding Exec: " + exec_val
                self.cur_node.sends.append(exec_val)
                
            if key == "IF":
                if self.in_function_block == True:
                    self.add_to_function_block(val)
                
            if key == "IDENT" or key == "DIGIT" or key == "QUOTE": 
                if left_token == "":
                    left_token = val
                else:
                    right_token = val
                    self.process_three_tokens(left_token, middle_token, right_token)
                    
            if key == "OPERATOR":
                middle_token = val
                
            if key == "ONCHANGED":
                self.onchanged_start(val)
            
            if key == "ENDBLOCK":
                self.in_function_block = False
    
    def add_to_function_block(self, str):
        # print ">> Adding function block" + str
        
        for variable in self.cur_onchanged_variables:
            # print ">>> OnChangedVar --" + variable.strip() + "--"
            
            str = str.replace("LINE", variable)
            
            if not variable in self.onchanged:
                self.onchanged[variable.strip()] = []
                
            self.onchanged[variable.strip()].append(str)
    
    def print_onchanged(self):
        print "\n------------------ Event Variables ----------------------"
        for variable, cmd_list in self.onchanged.iteritems():
            print "\n>> For variable: " + variable
            for item in cmd_list:
                print "------ " + item
        
    def onchanged_start(self, variable_names):
        variable_names = variable_names.replace("onchanged(", "")
        variable_names = variable_names.replace(")", "")
        variable_names = variable_names.replace("{", "")
        variable_names = variable_names.replace("}", "")
        variable_names = variable_names.replace("(", "")
        variable_names = variable_names.split(",")
        
        self.cur_onchanged_variables = []
        
        self.in_function_block = True
        for variable in variable_names:
            if variable.strip() == "LINE":
                variable = self.cur_node.node_name + ":LINE"
            self.cur_onchanged_variables.append(variable.strip())

    def trigger_onchanged(self, variable_name, variable_new_value):
        
        if self.running == False:
            return False
        
        # print "changed: " + variable_name + ", value=" + variable_new_value
        
        self.globals[variable_name] = variable_new_value
        
        # print "Onchanged Vars" + str(self.onchanged)
        if variable_name in  self.onchanged:
            cmds = self.onchanged[variable_name]
            for cmd in cmds:
                # print "Running onchanged cmd:" + cmd
                self.direct_parse_line(cmd)
        
    def direct_parse_line(self, line):
        # Does parse without regex
        line = line.strip()
        if line.lower().find("if") >= 0:
            op_items, assignments = self.split_by_ops(line)
            
            # print str(op_items)
            
            result = False
            #print "Following will be evaluated"
            for item in op_items:
                # print "Evaluated: " + item + " -- Result="
                if self.eval_comparison(item) == True:
                    # print "True"
                    result = True
                else:
                    # print "False"
                    result = False
                    break
            
            if result == True:
                # print "TRUE: " + line
                #print "The following assignment would then be done"
                # print "assignment:" + assignments
                
                if assignments.strip() == "PASS_TEST":
                    print "PASSED THE TEST"
                    self.callback.test_passed(self.test_index)
                elif assignments.strip() == "FAIL_TEST":
                    print "FAILED THE TEST"
                    self.callback.test_failed(self.test_index)    
                else:
                    expression = assignments.split("=")
                    self.do_assignment(expression[0], expression[1])

                    
            
    
    def eval_comparison(self, str):
        items = None
        if str.find("==") >= 0:
            items = str.split("==")
            left_item = items[0].strip()
            right_item = items[1].strip()
            right_item = right_item.strip("'")
            right_item = right_item.strip('"')
           # print "Left=" + left_item
            #print "Right=" + right_item
            
            
            variable_value = self.globals[left_item]
            
            #print "Var Val=" + variable_value
            if variable_value == right_item:
                return True
            else:
                return False
            
        if str.find("contains") >= 0:
            items = str.split("contains", 1)
            left_item = items[0].strip()
            right_item = items[1].strip()
            right_item = right_item.strip("'")
            right_item = right_item.strip('"')
            
            # print "Str=" + str
            # print "RightItem=" + right_item
            variable_value = self.globals[left_item]
            if variable_value.find(right_item) >= 0:
                return True
            else:
                return False   
            
            
        
    def split_by_ops(self, line):
        """ Split the line into operationss and assignments. The ops are lists
        like x == y, r == 3, and the assignments are k = 1
        """
        
        op_items = []
        cur_op = ""
        # Split by whitespace 
        items = line.split(" ")
        # print items
        
        prev_item = items[0]
        for item in items:
            item = item.strip()
            item = item.strip("'")
            item = item.strip('"')
            if item == "==":
                cur_op = prev_item + " == "
            elif item == "contains":
                cur_op = prev_item + " contains "
            elif item == "then":
                # cur_op = cur_op + item
                op_items.append(cur_op)
                cur_op = ""
            elif not item == "":
                cur_op = cur_op + " " + item
                
            prev_item = item
            
        assignments = line.split("then")[1]
        # print "ASSIGNMENT" + assignments
        # assignments = assignments.split("=")
        
        return op_items, assignments
        
        
    def process_three_tokens(self, left_token, middle_token, right_token):
        if middle_token == "=":
            self.do_assignment(left_token, right_token)
            
        if left_token == "node":
            self.create_node(right_token)
        
        # if left_token == "send":
        #    print ">> Adding send " + right_token.strip("\"")
        #    self.cur_node.sends.append(right_token.strip("\""))
            
        if left_token == "end" and right_token == "node":
            self.cur_node = None
            
    def create_node(self, node_name):
        print ">> Creating node " + node_name
        self.cur_node = Tester.Node(node_name)
        self.nodes.append(self.cur_node)
        
    def do_assignment(self, variable_name, variable_value):
        variable_name = variable_name.strip()
        variable_value = variable_value.strip()
        print ">> Assigned " + variable_name + " to be " + variable_value
        self.globals[variable_name] = variable_value
        self.trigger_onchanged(variable_name, variable_value)
        
    def run(self, test_index, callback):
        self.running = True
        self.test_index = test_index
        self.callback = callback
        
        # Execute the commands
        for node in self.nodes:
            
            for send in node.sends:
                print "Executing " + node.node_name + "> " + send
                self.callback.tester_send(node.node_name, send)
    
    