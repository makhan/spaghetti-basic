#! /usr/bin/python

LOGICAL=["AND","OR","XOR"]
RELATIONAL=["<",">","=",'<=','>=','<>']
ADD_SUB=['+','-']
MULT=['*','/','%']

def list_statement(source):
	(tokens,pos)=source
	if pos>=len(tokens) or tokens[pos]=='\n':
		return None
	else:
		ret=expression(source)
		if len(source[0])>source[-1] and expect(source,','):
			return ('LIST',ret,list_statement(source))
		else:
			return ('LIST',ret) 	

def terminal_operator(source,op):
	(tokens,pos)=source
	if pos>=len(tokens) or tokens[pos] not in op:
		raise ParseError("Expected: %s"%(" or ".join(["'%s'"%x for x in op])))
	else:
		source[-1]+=1
		return tokens[pos]
		
def expect(source,token):
	(tokens,pos)=source
	if pos<len(tokens) and tokens[pos]==token:
		source[-1]+=1
		return True
	else:
		return False
		
def identifier(token):
	ret=len(token)>0 and ( (token[0]>='A' and token[0]<='Z') or (token[0]>='a' and token[0]<='z') or token[0]=='_') 
	for c in token:
		ret= ret and ( (c>='A' and c<='Z') or (c>='a' and c<='z') or c=='_' or (c>='0' and c<='9') )
	return ret

def literal(token):
	try:
		x=float(token)
		ret=True
	except ValueError:
		ret=False
	finally: 
		return ret or (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'"))

def not_(source):
	(tokens,pos)=source
	if pos>=len(tokens):
		raise ParseError("Expected: Identifier or Literal")
	else:
		expect(source,'NOT')
		return ('NOT', factor(source))

def unary_minus(source):
	(tokens,pos)=source
	if pos>=len(tokens):
		raise ParseError("Expected: Identifier or Literal")
	else:
		expect(source,'-')
		return ('-', factor(source))
			
def identifier_or_literal(source):
	(tokens,pos)=source
	if pos>=len(tokens):
		raise ParseError("Expected: Identifier or Literal")
	else:
		if tokens[pos]=='NOT':
			return not_(source)
		elif tokens[pos]=='-':
			return unary_minus(source)
		#ret=identifier(tokens[pos]) or literal(tokens[pos])
		#if ret:
		#	source[-1]+=1
		#	return (tokens[pos],)
		if identifier(tokens[pos]):
			source[-1]+=1
			if expect(token='(',source=source):
				lst=list_statement(source)
				if not expect(token=')',source=source):
					raise ParseError('Error in line: '+' '.join(tokens)+'\nExpected ")"')
				return ('IDENTIFIER',tokens[pos],lst)
			else:
				return ('IDENTIFIER',tokens[pos])
		elif literal(tokens[pos]):
			source[-1]+=1
			return ('LITERAL',tokens[pos])
		else:
			raise ParseError("Expected: Identifier or Literal:"+' '.join(source[0])+" got %s"%tokens[pos])
			
def factor(source):
	(tokens,pos)=source
	if pos>=len(tokens):
		raise ParseException("malformed expression")
	elif expect(source,'('):
		ret=expression(source)
		if not expect(source,')'):
			raise ParseException("malformed expression")
		return ret
	else:
		return identifier_or_literal(source)
		
def term(source):
	(tokens,pos)=source
	if pos<len(tokens):
		left=factor(source)
		#print source
		if source[-1]<len(source[0]) and source[0][source[-1]] in MULT:
			mid=terminal_operator(source,MULT)
			right=term(source)
			return (mid,left,right)
		else:
			return left
	else:
		raise ParseException("malformed expression")
	
def value(source):
	(tokens,pos)=source
	if pos<len(tokens):
		left=term(source)
		if source[-1]<len(source[0]) and source[0][source[-1]] in ADD_SUB:
			mid=terminal_operator(source,ADD_SUB)
			right=value(source)
			return (mid,left,right)
		else:
			return left
	else:
		raise ParseException("malformed expression")
	
def boolean(source):
	(tokens,pos)=source
	if pos<len(tokens):
		left=value(source)
		if source[-1]<len(source[0]) and source[0][source[-1]] in RELATIONAL:
			mid=terminal_operator(source,RELATIONAL)
			right=boolean(source)
			return (mid,left,right)
		else:
			return left
	else:
		raise ParseException("malformed expression")
	
def expression(source):
	[tokens,pos]=source
	if pos<len(tokens):
		left=boolean(source)
		#print left
		if source[-1]<len(source[0]) and source[0][source[-1]] in LOGICAL:
			#print "more to come"
			mid=terminal_operator(source,LOGICAL)
			right=expression(source)
			return (mid,left,right)
		else:
			return left
		
	else:
		raise ParseError("malformed expression"+' '.join(source[0]))
	


def make_parse_tree(expr=[]):
	source=[expr,0]
	try:
		return expression(source)
	except ParseError,p:
		print p
	
	
class ParseError(StandardError):
	def __init__(self, value="Parsing Error"):
		self.value=value
	
	def __str__(self):
		return self.value

if __name__=='__main__':
	from sys import stdin
	for line in stdin:
		tokens=line.split()
		print make_parse_tree(tokens)
