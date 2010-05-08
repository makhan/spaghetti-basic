#! /usr/bin/python

# Spaghetti
# A simple BASIC interpreter
#
# First released 25th January 2010
# Muntasir Azam Khan
# <muntasir.khan@gmail.org>

# Warning:
# Most of the code has practically no comments/docstrings
# Trying to run incorect programs generates exceptions -> no helpful "syntax error" type messages
# There is no real lexer at the moment. That part of the job is done for now using regexes.

# Release History:
#   Version 0.1 - 24th January 2010
#   Initial Release
#
#   Version 0.2 - 4th May 2010
#   Many major bugfixes
#   Added support for 2 major features: command line arguments, INPUTLINE, and multiple variable INPUT
#
#   Version 0.2.1 - ?th May 2010
#   Some bugfixes
#   Added SORT,REVERSE, FORMAT, UCASE, LCASE functions

DEBUG=False

from sys import argv,setrecursionlimit
import operator
import ctypes
import tokenizer
import syntax_parser
from variables import Variable, StringType, MultiArray, Function, FileHandle
import standard_library
import getopt
from reader import DataSource
from translator import translate

#Allowed operators		
OPERATORS=['+','-','*','/','%','AND','OR','NOT','XOR','=','>','<','<>','>=','<=']

#determines order of promotion to another type when mixed types used in the same expression 
NUMERIC_PRECEDENCE=[StringType,ctypes.c_bool,ctypes.c_long,ctypes.c_float, ctypes.c_double]

#mapping of C/variables module types to equivalent python types
REQUIRED_PY_TYPE={
	ctypes.c_bool: bool,   
	ctypes.c_long: int,
	ctypes.c_float: float,
	ctypes.c_double: float,
	StringType: str#,
	#FileHandle: file
}

# mapping of C/variables module types to Spaghetti types
NUMERIC_TYPES={
	ctypes.c_bool: 'BOOLEAN',
	ctypes.c_long: 'INTEGER',
	ctypes.c_float: 'DOUBLE',
	ctypes.c_double: 'DOUBLE',
	StringType: 'STRING',
	FileHandle:'FILE'
}

# mapping of Spaghetti types to C/variables module types
DATA_TYPES={
	'INTEGER':ctypes.c_long,
	'DOUBLE':ctypes.c_double,
	'SINGLE':ctypes.c_float,
	'BOOLEAN':ctypes.c_bool,
	'STRING': StringType,
	'FILE': FileHandle
}


def cast(dest, var):
	"""Casts to a new type
	types are either C types (ctypes.*) or types defined in the variables module.
	var must have a .value attribute that is a Python type.
	"""
	#print "casting ", var, " to ", dest
	ret= dest(var.value)
	#print ret
	return ret
	
def cast_boolean(x):
	"""Returns 1 or 0 based on whether x is evaluated to True (according to Python's rules of truth) or not"""
	if x:
		return 1
	else:
		return 0

def cast_string(number):
	"""Casts a C type or a type from teh variables module to a Python string"""
	return str(number.value)

def binary_oper(x,y,return_type,op):
	"""Performs a binary operation on two values and casts the answer to a specified type"""
	if DEBUG:
		print "operation:",x,op,y
	return return_type(op(x.value,y.value))

def unary_oper(x,return_type,op):
	"""Performs a unary operation on a value and casts the answer to a specified type"""
	return return_type(op(x.value))
		
def make_func(return_type,op):
	"""Returns a function that takes two arguments and returns value whose type is return_type.
	Basically returns a function that wraps binary_oper function, not needing the extra arguments"""
	def ret(x,y):
		return binary_oper(x,y,return_type,op)
	return ret

def make_unary_func(return_type,op):
	"""Same as make_func, only for unary operations"""
	def ret(x):
		return unary_oper(x,return_type,op)
	return ret

def get_type(a,b):
	"""Returns the type of the answer if a binary operation is to be performed on a and b"""
	if DEBUG:
		print "type of ",a," and ",b
	at=a.__class__
	bt=b.__class__
	
	if DEBUG:
		print "vars are ",a," and ",b
		print "types are ",at," and ",bt
	
	n=NUMERIC_PRECEDENCE
	#return highest of at and bt (i.e. promoting the lower of them to that type would not lose data) 
	return NUMERIC_TYPES[n[max(n.index(at),n.index(bt))]]

	
class Interpreter:
	"""The main interpreter class.
	Takes a list of parse trees and start evaluation from the first one"""
	def __init__(self,parse_trees,line_mapping, predefinded_values=dict()):
		self.parse_trees=parse_trees
		self.line_mapping=line_mapping
		self.functions={ # operators
			# format: 
			# (operator,return type): make_func(...)
			# (operator,return type,'UNARY'): make_unary_func(...)
			
			('+','INTEGER'):make_func(ctypes.c_long,operator.add),
			('+','STRING'):make_func(StringType,operator.concat),
			('-','INTEGER'):make_func(ctypes.c_long,operator.sub),
			('/','INTEGER'):make_func(ctypes.c_long,operator.div),
			('%','INTEGER'):make_func(ctypes.c_long,operator.mod),
			('*','INTEGER'):make_func(ctypes.c_long,operator.mul),
			('-','INTEGER','UNARY'):make_unary_func(ctypes.c_long,operator.neg),
			
			('+','DOUBLE'):make_func(ctypes.c_double,operator.add),
			('-','DOUBLE'):make_func(ctypes.c_double,operator.sub),
			('/','DOUBLE'):make_func(ctypes.c_double,operator.div),
			('%','DOUBLE'):make_func(ctypes.c_double,operator.mod),
			('*','DOUBLE'):make_func(ctypes.c_double,operator.mul),
			('-','DOUBLE','UNARY'):make_unary_func(ctypes.c_double,operator.neg),
				
			('AND','BOOLEAN'):make_func(ctypes.c_bool,operator.and_),
			('OR','BOOLEAN'):make_func(ctypes.c_bool,operator.or_),
			('XOR','BOOLEAN'):make_func(ctypes.c_bool,operator.xor),
			('NOT','BOOLEAN'):make_unary_func(ctypes.c_bool,operator.not_),
			
			('>','BOOLEAN'):make_func(ctypes.c_bool,operator.gt),
			('<','BOOLEAN'):make_func(ctypes.c_bool,operator.lt),
			('=','BOOLEAN'):make_func(ctypes.c_bool,operator.eq),
			('>=','BOOLEAN'):make_func(ctypes.c_bool,operator.ge),
			('<=','BOOLEAN'):make_func(ctypes.c_bool,operator.le),
			('<>','BOOLEAN'):make_func(ctypes.c_bool,operator.ne),
			
		}
			
		
		self.cur_line=0
		# self.variables stores all variables created in a Spaghetti program as well as
		# a small set of predefined functions. Since function calls look the same as 
		# accessing an array element, the interpreter also does not make any distinction,
		# and predefined function objects have a .get method just like the MultiArray class. 
		self.variables=standard_library.stdlib # initially it only has predefined functions 
		self.variables.update(predefinded_values) # take in any predefined values (usually only COMMAND)
		
		self.stack=[] # call stack used to store return locations for GOSUB-RETURN 
		self.input_source=DataSource() # wraps sys.stdin - specify optional param to read from somewhere else  
		
	def printer(self,lst):
		"""helper method that prints a list of items.
		lst is not a Python list, but rather a parse tree node
		representing a list
		"""
		if lst==None:
			return # empty list, return without printing a newline
		elif len(lst)==2:
			# non-empty list but with no next element
			# print this element including a newline and return
			print self.evaluate(lst[1]).value
		else:
			# current node has successors,
			# print current value and move on to the next node 
			print self.evaluate(lst[1]).value,
			self.printer(lst[-1])
	
	def read(self, lst, reader_function):
		"""
		Helper method that recursively reads values into a list of variables.
		The reader_function is a function that is called to read the value.
		Whether a single token or a whole line or anything else and from which source
		(e.g. stdin, file, device etc.) is determined by that.
		"""
		node=lst[1]
		target_var=node[1]
		if target_var not in self.variables:
			raise InterpreterError("variable %s not defined"%target_var)
			
		var=self.variables[target_var]
		tp=var.type
		if len(node)==2:
			# scalar
			try:
				inp=REQUIRED_PY_TYPE[tp](reader_function())
			except EOFError:
				raise InterpreterError("Can't read input, EOF found")
			tp=var.type
			var.value=tp(inp)
		else:
			# array
			indices=self.evaluate(node[2])
			try:
				inp=REQUIRED_PY_TYPE[tp](reader_function())
			except EOFError:
				raise InterpreterError("Can't read input, EOF found")
			
			try:
				var.set_(indices,tp(inp))
			except AttributeError:
				raise InterpreterError("Can't read into array %s. Make Sure it is an array and not a function."%target_var)
		if len(lst)>2:
			self.read(lst[-1], reader_function)
		
	
	def evaluate(self,node):
		"""Evaluator function
		Evaluates the parse tree rooted at the current node
		Basically a giant if construct that decides what to do
		based on the type of node (as found by the string at node[0])
		"""
		if DEBUG:
			print "Evaluating",node
		
		if self.cur_line>=len(self.parse_trees):
			#reached end of the list of parse trees
			return None
		
		if node[0]=='STMT':
			# statement
			line=self.cur_line
			self.evaluate(node[1])
			if self.cur_line==line:
				self.evaluate(node[-1])
		
		elif node[0]=='DIM':
			# declaration
			name=node[1][1] # gets the name of the identifier only (e.g. in myvar and myvar(3,3), myvar is the name)
			id_node=node[1] # parse tree rooted at id_node represents an identifier 
			
			# not specifying a data type makes it INTEGER by default
			if len(node)>2:
				datatype=DATA_TYPES[node[2]]
			else:
				datatype=DATA_TYPES['INTEGER']
			
			# declaring two variables with the same name (or the name of a predefined function) is not allowed
			if name in self.variables:
				raise InterpreterError("Runtime Error: %s already declared"%name)
			
			if len(id_node)==2:
				# scalar: simply create a new Variable
				var=Variable(name,datatype,datatype(0))
				#print "creating scalar %s"%name,var.__class__
			else:
				# array: get dimensions by evaluating the list following the name and create a MultiArray
				dimensions=self.evaluate(id_node[-1])
				var=MultiArray(dimensions, name, datatype,datatype(0))
			
			self.variables[name]=var
			self.cur_line+=1
		
		elif node[0]=='LET':
			# assignment
			varname=node[1][1] # left hand side
			value=self.evaluate(node[2]) # right hand side
			#print "got value ",value
			#if DEBUG:
			#	print value
				
			if varname not in self.variables:
				rhs_type=get_type(value,value)
				#print ">>>>>>",rhs_type
				if len(node[1])==2:
					# not an array: automatic declaration
					##print "+++++",DATA_TYPES[rhs_type]
					var=Variable(varname,DATA_TYPES[rhs_type],cast(DATA_TYPES[rhs_type],ctypes.c_long(0)))
					#print "value: ",var.value
				else:
					# array
					raise InterpreterError("Cannot assign to undeclared array %s: "%varname)
				self.variables[varname]=var
				#print "just assigned ",varname," to ", var.value.__class__
			else:
				var=self.variables[varname]
			
			if len(node[1])==2:
				# not an array: simple assignment
				#print "type: ", var.type
				#print "value: ", value
				if var.type!=value.__class__:
					#print "here"
					var.value=var.type(REQUIRED_PY_TYPE[var.type](value.value))
				else:
					var.value=value
			else:
				# array: figure out indices first and then try to assign
				coords=self.evaluate(node[1][-1])
				try:
					var.set_(coords,var.type(REQUIRED_PY_TYPE[var.type](value.value)))
				except AttributeError,e:	
					raise InterpreterError("Cannot assign to %s"%varname) 
			
			#print "checking: ",self.variables[varname].value
			self.cur_line+=1
		
		elif node[0]=='IF':
			# conditional
			cond=self.evaluate(node[1])
			if cond.value:
				self.evaluate(node[2])
			elif len(node)>3:
				# has an ELSE clause
				self.evaluate(node[3])
			else:
				self.cur_line+=1
		
		elif node[0]=='PRINT':
			# output
			self.printer(node[1])
			self.cur_line=self.cur_line+1
		
		elif node[0]=='GOTO':
			# GOTO: figure out the target and move there
			target=self.evaluate(node[1])
			self.cur_line=self.line_mapping[target.value]
		
		elif node[0]=='GOSUB':
			# GOSUB: same as GOTO, but keep return address in the stack
			target=self.evaluate(node[1])
			self.stack.append(self.cur_line+1)
			self.cur_line=self.line_mapping[target.value]
		
		elif node[0]=='INPUT':
			# read a list of tokens and save them in the supplied list of variables
			self.read(node[1], self.input_source.read_token)
			self.cur_line+=1
		elif node[0]=='INPUTLINE':
			# same as INPUT, but reads lines instead of tokens
			self.readline(node[1], self.input_source.read_line)
			self.cur_line+=1
		
		elif node[0]=='END':
			# terminates program
			self.cur_line=len(self.parse_trees)
		
		elif node[0]=='RETURN':
			# go back to the line after the last call to GOSUB
			ret_value=self.stack.pop()
			self.cur_line=ret_value
		
		elif node[0]=='LITERAL':
			if (node[1].startswith('"') and node[1].endswith('"')) or (node[1].startswith("'") and node[1].endswith("'")):
				return StringType(node[1][1:-1])
			elif '.' in node[1]:
				return ctypes.c_double(float(node[1]))
			else:
				return ctypes.c_long(int(node[1]))
		
		elif node[0]=='IDENTIFIER':
			varname=node[1]
			if varname not in self.variables:
				raise InterpreterError("variable %s not defined"%varname)
			
			if DEBUG:
				print "variable/array/function: ",varname
			var=self.variables[varname]
			if len(node)==2:
				return var.value
			else:
				indices=self.evaluate(node[2])
				if DEBUG:
					print "args=",indices
				return var.get(indices)
				 
		elif node[0] in OPERATORS[5:]:
			return self.functions[(node[0],"BOOLEAN")](*(map(self.evaluate,node[1:])))
		
		elif node[0] in OPERATORS[:5]:
			args=node[1:]
			args=map(self.evaluate,args)
			if len(args)==2:
				tp=get_type(*args)
			else:
				tp=NUMERIC_TYPES[type(args[0])]
			if (node[0]=='-' or node[0]=='NOT') and len(node)==2:
				ret=self.functions[(node[0],tp,'UNARY')](*args)
			else:
				ret=self.functions[(node[0],tp)](*args)
			return ret
		
		elif node[0]=='REM':
			self.cur_line+=1
		
		elif node[0]=='LIST':
			ret=[self.evaluate(node[1])]
			if len(node)>2:
				ret.extend(self.evaluate(node[2]))
			if DEBUG:
				print "returning ",ret
			return ret
			
		#elif node[0]=='FOR':
			# Not implemented at the parser level
			# Assumes node structure of ('FOR',identifier,start_value,end_value,step,node_inside_loop,next_node)
		#	(discard,identifier,start_value,end_value,step,node_inside_loop,next_node)=node
		#	del discard
			
		#	assignment=('LET',identifier,start_value)
			
		#	while self.evaluate(identifier).value!=self.evaluate(end_value).value:
		#		self.evaluate(node_inside_loop)
		#	self.evaluate(next_node)
		else:
			raise InterpreterError("Unknown parse tree node: %s"%str(node[0]))
	
	def run(self):
		self.cur_line=0
		while self.cur_line<len(self.parse_trees):
			if DEBUG:
				print "running ",self.parse_trees[self.cur_line]
			
			# hack: added last line to current line check to enable expressions to act like statements
			last_line=self.cur_line
			
			self.evaluate(self.parse_trees[self.cur_line])
			
			if self.cur_line==last_line:
				self.cur_line+=1
	
		 
class InterpreterError:
	def __init__(self,value):
		self.value=value
	
	def __str__(self):
		return self.value
		
if __name__=='__main__':
	setrecursionlimit(10000)
	options,arguments=getopt.getopt(argv[1:],"p")
	if len(arguments)>=1:
		try:
			infile=open(arguments[0], 'r')
			lines=infile.readlines()
			lines=translate([tokenizer.tokenize(line) for line in lines])
			(linenum_idx,parse_tree)=syntax_parser.create_parse_trees(lines)
			if ('-p','') in options:
				# print parse tree in a separate text file
				parse_file=open(arguments[0][:max(arguments[0].index('.'),0)]+'_parsetree.txt','w')
				parse_file.write(str(parse_tree))
			cmd_line=Variable('COMMAND',StringType,StringType(' '.join(arguments)))
			#cmd=MultiArray([len(arguments)],'COMMAND',StringType,)
			#cmd_line=Variable('COMMAND',MultiArray,MultiArray())
			runner=Interpreter(parse_tree, linenum_idx, {'COMMAND$':cmd_line, 'COMMAND':cmd_line})
			runner.run()
		except IOError,ioe:
			print "Error in reading/writing file:\n",str(ioe)
			
	else:
		print "usage: ./spaghetti.py <file name> or python spaghetti.py <file_name>"
