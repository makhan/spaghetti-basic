from sys import stdin,stderr
from cStringIO import StringIO

class DataSource:
	def __init__(self, source=stdin):
		self.source=source
		
	def read_token(self):
		ret=StringIO()
		while True:
			c=self.source.read(1)
			if not c.isspace():
				break
			
		while not c.isspace():
			ret.write(c)
			c=self.source.read(1)
		ret.seek(0)
		return ret.read()
	
	def read_line(self):
		return self.source.readline()
