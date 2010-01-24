#! /usr/bin/python
from expression_parser import *
DEBUG=False

TYPES=['INTEGER','DOUBLE','SINGLE','BOOLEAN','STRING']

def key_word(source,key):
	(tokens,pos)=source
	if pos>=len(tokens):
		raise ParseError("Malformed statement: expected keyword %s, got %s"%(key,tokens[pos]))
	else:
		if tokens[pos]==key:
			source[-1]+=1
		else:
			raise ParseError("Malformed statement: expected keyword %s, got %s"%(key,tokens[pos])+' '.join(source[0]))


def get_identifier(source):
	(tokens,pos)=source
	if pos>=len(tokens) or not identifier(tokens[pos]):
		raise ParseError('Malformed statement: expected <identifier> got %s'%str(tokens))
	else:
		source[-1]+=1
		if expect(source,'('):
			lst=list_statement(source)
			if not expect(source,')'):
				raise ParseError('Malformed statement: expected ) got %s'%str(tokens))
			return ("IDENTIFIER",tokens[pos],lst)
		else:
			return ("IDENTIFIER",tokens[pos])

def is_let_stmt(source):
	(tokens,pos)=source
	if tokens[pos]=='LET':
		return True
	elif identifier(tokens[pos]):
		new_source=[tokens,pos]
		parsed_id=get_identifier(new_source)
		pos=new_source[-1]
		return pos<len(tokens)-1 and tokens[pos]=='='
	else:
		return False
def stmt(source):
	(tokens,pos)=source
	if pos>=len(tokens):
		raise ParseError('Not a statement: expecting statement')
	else:
		if tokens[pos]=='IF':
			return branch(source)
		elif tokens[pos]=='GOTO':
			return jump(source)
		elif is_let_stmt(source):
			return asgn(source)
		elif tokens[pos]=='INPUT':
			return inp(source)
		elif tokens[pos]=='PRINT':
			return output(source)
		elif tokens[pos]=='GOSUB':
			return sub(source)
		elif tokens[pos]=='RETURN':
			return return_(source)
		elif tokens[pos]=='DIM':
			return decl(source)
		elif tokens[pos]=='END':
			return end(source)
		elif tokens[pos]=='REM':
			return rem(source)
		else:
			return expression(source)
			
def rem(source):
	while len(source[0])>source[-1]:
		source[-1]+=1
	return ('REM',)
	
def return_(source):
	key_word(source,'RETURN')
	return ('RETURN',)

def end(source):
	key_word(source,'END')
	return ('END',)
	
def jump(source):
	(tokens,pos)=source
	key_word(source,'GOTO')
	return ('GOTO',expression(source))

def branch(source):
	(tokens,pos)=source
	key_word(source,'IF')
	condition=expression(source)
	if DEBUG:
		print "condition:",condition
	key_word(key='THEN',source=source)
	targ1=stmt(source)
	if source[-1]<len(source[0]) and source[0][source[-1]]=='ELSE':
		key_word(source,'ELSE')
		targ2=stmt(source)
		return ('IF',condition,targ1,targ2)
	else:
		return ('IF',condition,targ1)

def decl(source):
	(tokens,pos)=source
	key_word(source,"DIM")
	var=get_identifier(source)
	if source[-1]<len(source[0]) and source[0][source[-1]]=='AS':
		key_word(source,'AS')
		t=type_(source)
		return ("DIM",var,t)
	else:
		return ("DIM",var,"UNKNOWN") 	

def asgn(source):
	#print "asgn"
	(tokens,pos)=source
	if pos>=len(source):
		raise ParseError("Malformed statement: Expected LET or <identifier>")
	else:
		if tokens[pos]=='LET':
			key_word(source,'LET')
		var=get_identifier(source)
		key_word(source,'=')
		val=expression(source)
		return ('LET',var,val)

def inp(source):
	key_word(source,'INPUT')
	var=get_identifier(source)
	return ('INPUT',var)

def output(source):
	key_word(source,'PRINT')
	#var=expression(source)#get_identifier(source)
	#newline=not(source[-1]<len(source[0]) and source[0][source[-1]]==',')
	#return ('PRINT',var,newline)
	var=list_statement(source)
	return ('PRINT',var)

def sub(source):
	key_word(source,'GOSUB')
	targ=expression(source)
	return ('GOSUB',targ)

def type_(source):
	(tokens,pos)=source
	if pos>=len(tokens) or not(tokens[pos] in TYPES):
		#print tokens[pos]==TYPES[-1]
		#print not(tokens[pos] in TYPES)
		raise ParseError("Malformed Statement: Expected [%s], got %s"%(' or '.join(TYPES), 'nothing' if pos>=len(tokens) else tokens[pos]))
	else:
		source[-1]+=1
		return tokens[pos]

	
def parse(line):
	line=line.split()
	line_num=line[0]
	line=line[1:]
	source=[line,0]
	return stmt(source)

def get_line_number(source):
	(tokens,pos)=source
	import ctypes
	if pos>=len(tokens):
		raise ParseError("Expected: Line number")
	else:
		try:
			num=int(tokens[pos])
			if num>=1 and num<=0x7FFFFFFF:
				source[-1]+=1
				return (tokens[pos],)
			else:
				raise ParseError("Expected: Line number")
		except ValueError,v:	
			raise ParseException("%s is not a valid line number"%tokens[pos])

def program(source):
	(tokens,pos)=source
	if len(tokens)==0:
		return None
	elif pos>=len(tokens):
		return None
	else:
		line_num=get_line_number(source)
		parse_tree=statement(source)
		if source[-1]<len(source[0]):
			key_word(source,'\n')
		rest=program(source)
		return (line_num,parse_tree,rest) if rest else (line_num,parse_tree)

def make_source(tokens):
	return [tokens,0]
def create_parse_trees(lines):
	#each line is tokenized separately
	line_num_to_index={}
	for i,line in enumerate(lines):
		#first token is always line number
		line_num_to_index[int(line[0])]=i
	return (line_num_to_index,tuple([stmt(make_source(line[1:])) for line in lines]))
	
if __name__=='__main__':
	from sys import stdin
	while True:
		line=raw_input()
		print parse(line)

