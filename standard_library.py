from variables import Variable, StringType, MultiArray, Function, FileHandle
import math
import ctypes
import random

DEBUG=False

function_mapping={
	int:ctypes.c_long,
	float:ctypes.c_double,
	file:FileHandle,
	str:StringType
}

def wrapper(f):
	def ret(*args):
		#print args
		try:
			new_args=[x.value for x in args]
		except:
			new_args=args
		answer=f(*new_args)
		return_type=function_mapping.get(type(answer),StringType)
		return return_type(answer)
	return ret

string_lib=[
	('MID', lambda s,i,j: s[i:i+j]),
	('LEFT', lambda s,i: s[:i]),
	('RIGHT', lambda s,i:s[-i:]),
	('CHR', chr),
	('STR',str),
	('UCASE',lambda x: x.upper()),
	("LCASE",lambda x: x.lower()),
	#('LEN',len)
	('FORMAT', lambda x,y: (x%y))
]

int_lib=[
	('INT', int),
	('ASC', ord),
	('ABS',abs),
	('FIND',lambda s,t:s.find(t)),
	('LEN',len)
]

float_lib=[
	('acos',math.acos),
	('acosh',math.acosh),
	('asin',math.asin),
	('asinh',math.asinh),
	('atan',math.atan),
	('atan2',math.atan2),
	('atanh',math.atanh),
	('ceil',math.ceil),
	('cos',math.cos),
	('cosh',math.cosh),
	('exp',math.exp),
	('fabs',math.fabs),
	('floor',math.floor),
	('log',math.log),
	('pow',math.pow),
	('sin',math.sin),
	('sinh',math.sinh),
	('sqrt',math.sqrt),
	('tan',math.tan),
	('tanh',math.tanh),
	('dbl',float)
]

# Additional Functions


# Array Functions
def sort(array):
	array.sort(key=lambda x:x.value)
	return None

def reverse(array):
	array.reverse()
	return None
	
def fold(array):
	try:
		ret=sum(x.value for x in array)
	except TypeError:
		raise LibraryError("Cannot sum over non-numeric data")
	return_type=function_mapping.get(type(ret),StringType)
	return return_type(ret)

def join(delimiter, array):
	delimiter=delimiter.value
	ret=delimiter.join(str(x.value) for x in array)
	return StringType(ret)

array_lib=[
	("SORT", sort),
	("REVERSE",reverse),
	("SUM", fold),
	("JOIN",join)
]

# File I/O -  * Not implemented yet *

#def open_file(name,wr):
#	t={'READ':'r','R':'r', 'WRITE':'w','W':'w'}
#	f=open(name,t[wr])
#	return f

#def finput(name):
#	ret=name.read()
	#print "got ",ret
#	return ret
	#return StringType(name.read())
#def foutput(name,var):
	#name.value.write(var)
#	name.write(var)
	
stdlib={}
stdlib.update([(name,Function(wrapper(f))) for (name,f) in int_lib])
stdlib.update([(name,Function(wrapper(f))) for name,f in string_lib])
stdlib.update([(name.upper(),Function(wrapper(f))) for name,f in float_lib])
stdlib.update([(name,Function(f)) for name,f in array_lib])
#stdlib.update((name,Function(wrapper(f))) for name,f in (('open', open_file), ('input', finput), ('print', foutput)))

#stdlib.update([(name, Function(f)) for name,f in hacky_functions])

class LibraryError:
	def __init__(self, message="Invalid library call"):
		self.message=message
	def __str__(self):
		return self.message
