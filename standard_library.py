from variables import Variable, StringType, MultiArray,Function
import math
import ctypes
import random

DEBUG=True

function_mapping={
	int:ctypes.c_long,
	float:ctypes.c_double,
	#str:StringType
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
	#('LEN',len)
]

int_lib=[
	('INT', int),
	('ASC', ord),
	('ABS',abs),
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

#hacky_functions=[
#	('LEN',len)
#]

stdlib={}
stdlib.update([(name,Function(wrapper(f))) for (name,f) in int_lib])
stdlib.update([(name,Function(wrapper(f))) for name,f in string_lib])
stdlib.update([(name.upper(),Function(wrapper(f))) for name,f in float_lib])
#stdlib.update([(name, Function(f)) for name,f in hacky_functions])
