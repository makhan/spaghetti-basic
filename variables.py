import operator
from collections import deque
import ctypes

class Variable:
	def __init__(self, name, type_, value):
		self.name=name
		self.type=type_
		self.value=value
	
	def __str__(self):
		return str(self.value)
		
class StringType:
	def __init__(self,value):
		self.value=value
		self.__class__=StringType
	def __str__(self):
		return self.value
	def __len__(self):
		return len(self.__value__) 
	
class MultiArray:
	def __convert(self,coords):
		ret=0
		factor=1
		for (c,p) in zip((x.value for x in coords),self.__dimensions):
			ret+=factor*c
			factor*=p
		return ret
		
	def __init__(self, dimensions, name, type_, default_value=None):
		self.__dimensions=[x.value for x in dimensions]
		self.__array=[default_value for i in xrange(reduce(operator.mul,(x.value for x in dimensions),1))]
		self.type=type_
		self.name=name
		self.value=self.__array
		
	def set_(self,coords, value):
		pos=self.__convert(coords)
		self.__array[pos]=value
		return value

	def get(self, coords):
		pos=self.__convert(coords)
		return self.__array[pos]
	def num_dimensions(self):
		return len(self.__dimensions)
	#def __len__(self):
	#	return len(self.__array)

	#def value(self):
	#	return tuple(self.__array)
		
class Function:
	def __init__(self, f):
		self.__f=f
	
	def get(self, args):
		ret=self.__f(*args)
		if ret is None:
			return ctypes.c_long(0)
		else:
			return ret
			 
class FileHandle:
	def __init__(self,f):
		self.__f=f
		self.__tokens=deque()
		self.value=f;
		print "created FileHandle ",f
	def get_line(self):
		return self.__f.readline()
	def write(self,x):
		"Writes a single token into the file"
		try:
			to_write=x.value
		except AttributeError,e:
			raise FileIOError("Cannot write complex type")
		self.__f.write(to_write)
	def read(self):
		"Reads a single token from the file (or file buffer) and returns a StringType"
		#print "in read"
		while len(self.__tokens)==0:
			self.__tokens.extend(self.__f.readline().split())
			#print "tokens=",self.__tokens
		return StringType(self.__tokens.popleft())
	
class FileIOError:
	def __init__(self, mesg):
		self.__mesg=mesg
	def __str__(self):
		return self.__mesg
