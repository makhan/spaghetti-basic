#! /usr/bin/python

# Spaghetti
# A simple BASIC interpreter
#
# First released 25th January 2010
# Muntasir Azam Khan
# <muntasir.khan@gmail.org>

# Warning:
# Most of the code has practically no comments/docstrings
# Trying to run incorect programs generates exceptions -> no helpful syntax error type messages
# There is no real lexer at the moment. That part of the job is done for now using regexes.

DEBUG=False

from sys import argv
import operator
import ctypes
import tokenizer
import syntax_parser
from variables import Variable,StringType, MultiArray, Function
import standard_library

#Allowed operators		
OPERATORS=['+','-','*','/','%','AND','OR','NOT','XOR','=','>','<','<>','>=','<=']

#determines order of promotion to another type whne mixed types used in the same expression 
NUMERIC_PRECEDENCE=[StringType,ctypes.c_bool,ctypes.c_long,ctypes.c_float, ctypes.c_double]

#mapping of C/variables module types to equivalent python types
REQUIRED_PY_TYPE={
	ctypes.c_bool: bool,   
	ctypes.c_long: int,
	ctypes.c_float: float,
	ctypes.c_double: float,
	StringType: str
}

#mapping of C/variables module types to Spaghetti types
NUMERIC_TYPES={
	ctypes.c_bool: 'BOOLEAN',
	ctypes.c_long: 'INTEGER',
	ctypes.c_float: 'DOUBLE',
	ctypes.c_double: 'DOUBLE',
	StringType: 'STRING'
}

#mapping of Spaghetti types to C/variables module types
DATA_TYPES={
	'INTEGER':ctypes.c_long,
	'DOUBLE':ctypes.c_double,
	'SINGLE':ctypes.c_float,
	'BOOLEAN':ctypes.c_bool,
	'STRING': StringType
}


def cast(dest, var):
	"""Casts to a new type
	types are either C types (ctypes.*) or types defined in the variables module.
	var must have a .value attribute that is a Python type.
	"""
	return dest(var.value)

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
	at=type(a)
	bt=type(b)
	
	# Stupid Hack: x in not in NUMERIC_TYPES => x is StringType
	# This will break when additional types are added, but works for now
	(at,bt) = map(lambda x: x if x in NUMERIC_TYPES else StringType, (at,bt))
	
	if DEBUG:
		print "types are ",at," and ",bt
	
	n=NUMERIC_PRECEDENCE
	#return highest of at and bt (i.e. promoting the lower of them to that type would not lose data) 
	return NUMERIC_TYPES[n[max(n.index(at),n.index(bt))]]

	
class Interpreter:
	"""The main interpreter class.
	Takes a list of parse trees and start evaluation from the first one"""
	def __init__(self,parse_trees,line_mapping):
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
		self.variables=standard_library.stdlib # initiall it only has predefined functions 
		self.stack=[] # call stack used to store return locations for GOSUB-RETURN 
		
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
		
		if node[0]=='DIM':
			# decalaration
			name=node[1][1] # gets the name of the identifier only (e.g. in myvar and myvar(3,3), myvar is the name)
			id_node=node[1] # parse tree rooted at id_node represents an identifier 
			
			# not specifying a data type make it INTEGER by default
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
			if DEBUG:
				print value
				
			if varname not in self.variables:
				rhs_type=get_type(value,value)
				if len(node[1])==2:
					var=Variable(varname,DATA_TYPES[rhs_type],cast(DATA_TYPES[rhs_type],ctypes.c_long(0)))
				else:
					raise InterpreterError("Cannot assign to undeclared array %s: "%varname)
				self.variables[varname]=var
			else:
				var=self.variables[varname]
			
			if len(node[1])==2:
				var.value=var.type(REQUIRED_PY_TYPE[var.type](value.value))
			else:
				coords=self.evaluate(node[1][-1])
				try:
					var.set_(coords,var.type(REQUIRED_PY_TYPE[var.type](value.value)))
				except AttributeError,e:	
					raise InterpreterError("Cannot assign to %s"%varname) 
			self.cur_line+=1
		elif node[0]=='IF':
			cond=self.evaluate(node[1])
			if cond.value:
				self.evaluate(node[2])
			elif len(node)>3:
				self.evaluate(node[3])
			else:
				self.cur_line+=1
		elif node[0]=='PRINT':
			self.printer(node[1])
			self.cur_line=self.cur_line+1
		elif node[0]=='GOTO':
			target=self.evaluate(node[1])
			self.cur_line=self.line_mapping[target.value]
		elif node[0]=='GOSUB':
			target=self.evaluate(node[1])
			self.stack.append(self.cur_line+1)
			self.cur_line=self.line_mapping[target.value]
		elif node[0]=='INPUT':
			target_var=node[1][1]
			var=self.variables[target_var]
			tp=var.type
			inp=REQUIRED_PY_TYPE[tp](raw_input())
			tp=var.type
			var.value=tp(inp)
			self.cur_line+=1
		elif node[0]=='END':
			self.cur_line=len(self.parse_trees)
		elif node[0]=='RETURN':
			ret_value=self.stack.pop()
			self.cur_line=ret_value
		elif node[0]=='LITERAL':
			if node[1].startswith('"') and node[1].endswith('"'):
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
					#print "Callling %s"%var.name
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
		else:
			raise InterpreterError("Unknown parse tree node: %s"%str(node[0]))
	
	def run(self):
		self.cur_line=0
		while self.cur_line<len(self.parse_trees):
			if DEBUG:
				print "running ",self.parse_trees[self.cur_line]
			self.evaluate(self.parse_trees[self.cur_line])
	
		 
class InterpreterError:
	def __init__(self,value):
		self.value=value
	
	def __str__(self):
		return self.value
		
if __name__=='__main__':
	if len(argv)>1:
		infile=open(argv[1], 'r')
		lines=infile.readlines()
		parse_file=open(argv[1][:max(argv[1].index('.'),0)]+'_parsetree.txt','w')
		#lines=[line.split() for line in lines] # use a real tokenizer 
		lines=[tokenizer.tokenize(line) for line in lines]
		(linenum_idx,parse_tree)=syntax_parser.create_parse_trees(lines)
		parse_file.write(str(parse_tree))
		runner=Interpreter(parse_tree, linenum_idx)
		runner.run()
	else:
		print "usage: spaghetti_interpreter <file name>"
