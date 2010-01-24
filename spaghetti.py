#! /usr/bin/python

# Spaghetti
# A simple BASIC interpreter
#
# First released 25th January 2010
# Muntasir Azam Khan
# <muntasir.khan@gmail.org>

# Warning:
# The code has practically no comments/docstrings
# Trying to run incorect programs generates exceptions -> no helpful syntax error type messages

DEBUG=False

from sys import argv
import operator
import ctypes
import tokenizer
import syntax_parser
from variables import Variable,StringType, MultiArray, Function
import standard_library

		
OPERATORS=['+','-','*','/','%','AND','OR','NOT','XOR','=','>','<','<>','>=','<=']

NUMERIC_PRECEDENCE=[StringType,ctypes.c_bool,ctypes.c_long,ctypes.c_float, ctypes.c_double]
REQUIRED_PY_TYPE={
	ctypes.c_bool: bool,   
	ctypes.c_long: int,
	ctypes.c_float: float,
	ctypes.c_double: float,
	StringType: str
}

NUMERIC_TYPES={
	ctypes.c_bool: 'BOOLEAN',
	ctypes.c_long: 'INTEGER',
	ctypes.c_float: 'DOUBLE',
	ctypes.c_double: 'DOUBLE',
	StringType: 'STRING'
}

DATA_TYPES={
	'INTEGER':ctypes.c_long,
	'DOUBLE':ctypes.c_double,
	'SINGLE':ctypes.c_float,
	'BOOLEAN':ctypes.c_bool,
	'STRING': StringType
}

def cast(dest, var):
	return dest(var.value)

def cast_boolean(x):
	if x:
		return 1
	else:
		return 0

def cast_string(number):
	return str(number.value)

def binary_oper(x,y,return_type,op):
	if DEBUG:
		print "operation:",x,op,y
	return return_type(op(x.value,y.value))

def unary_oper(x,return_type,op):
	return return_type(op(x.value))
		
def make_func(return_type,op):
	def ret(x,y):
		return binary_oper(x,y,return_type,op)
	return ret

def make_unary_func(return_type,op):
	def ret(x):
		return unary_oper(x,y,return_type,op)
	return ret

def get_type(a,b):
	if DEBUG:
		print "type of ",a," and ",b
	at=type(a)
	bt=type(b)
	# Stupid Hack
	(at,bt) = map(lambda x: x if x in NUMERIC_TYPES else StringType, (at,bt))
	if DEBUG:
		print "types are ",at," and ",bt
	
	n=NUMERIC_PRECEDENCE
	return NUMERIC_TYPES[n[max(n.index(at),n.index(bt))]]

	
class Interpreter:
	def __init__(self,parse_trees,line_mapping):
		self.parse_trees=parse_trees
		self.line_mapping=line_mapping
		self.functions={
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
		self.variables=standard_library.stdlib
		self.stack=[]
		
	def printer(self,lst):
		if lst==None:
			return
		elif len(lst)==2:
			print self.evaluate(lst[1]).value
		else:
			print self.evaluate(lst[1]).value,
			self.printer(lst[-1])
			
	def evaluate(self,node):
		if DEBUG:
			print "Evaluating",node
		if self.cur_line>=len(self.parse_trees):
			return None
		if node[0]=='DIM':
			name=node[1][1]
			id_node=node[1]
			
			if len(node)>2:
				datatype=DATA_TYPES[node[2]]
			else:
				datatype=DATA_TYPES['INTEGER']
			
			if name in self.variables:
				raise InterpreterError("Runtime Error: %s already declared"%name)
			
			if len(id_node)==2:
				var=Variable(name,datatype,datatype(0))
			else:
				#array
				dimensions=self.evaluate(id_node[-1])
				var=MultiArray(dimensions, name, datatype,datatype(0))
			
			self.variables[name]=var
			self.cur_line+=1
		elif node[0]=='LET':
			varname=node[1][1]
			value=self.evaluate(node[2])
			if DEBUG:
				print value
			if varname not in self.variables:
				var=Variable(varname,DATA_TYPES['INTEGER'],cast(DATA_TYPES['INTEGER'],0))
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
