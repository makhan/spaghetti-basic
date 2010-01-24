from variables import Variable, StringType, MultiArray,Function
import math
import ctypes
import random

DEBUG=False

def wrapper(f, return_type):
	def ret(*args):
		newargs=[x.value for x in args]
		
		if DEBUG:
			print "Called function: %s"%str(f)
			print "with arguments",newargs
		
		return return_type(f(*newargs))
	return ret

string_lib=[
	('MID', lambda s,i,j: s[i:i+j]),
	('LEFT', lambda s,i: s[:i]),
	('RIGHT', lambda s,i:s[-i:]),
	('CHR', chr),
	('STR',str) 
]

int_lib=[
	('INT', int),
	('ASC', ord),
	('ABS',abs)
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


stdlib={}
stdlib.update([(name,Function(wrapper(f,ctypes.c_long))) for (name,f) in int_lib])
stdlib.update([(name,Function(wrapper(f,StringType))) for name,f in string_lib])
stdlib.update([(name.upper(),Function(wrapper(f,ctypes.c_double))) for name,f in float_lib])



