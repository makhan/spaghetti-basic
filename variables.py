import operator

class Variable:
	def __init__(self, name, type_, value):
		self.name=name
		self.type=type_
		self.value=value
	
	def __str__(self):
		return str(value)
		
class StringType:
	def __init__(self,value):
		self.value=value
		self.__class__=StringType
	def __str__(self):
		return self.value
	
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
		
	def set_(self,coords, value):
		pos=self.__convert(coords)
		self.__array[pos]=value
		return value
		
	def get(self, coords):
		pos=self.__convert(coords)
		return self.__array[pos]

class Function:
	def __init__(self, f):
		self.__f=f
	
	def get(self, args):
		return self.__f(*args)
