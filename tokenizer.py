#! /usr/bin/python
DEBUG=False

# TODO:
# Use a real lexer
# Currently this is a regex hack-job

import re
STRING=[r'\"[^\"]*\"',r"\'[^\']*\'"]
WORDS=map(lambda x:"\\b%s\\b"%x,['IF','LET','AS','THEN','ELSE','DIM','PRINT','INPUT','GOTO','GOSUB','RETURN',
		'STRING','INTEGER','DOUBLE','FLOAT','BOOLEAN','AND','OR','NOT','XOR','REM','END'])
OPERATORS=[r'\+',r'\-',r'\*',r'/',r'\%',r'>=',r'<=',r'<>','=','<','>',r'\(',r'\)',r',',]
IDENTIFIER_NUMBER=[r'\b\d*\.\d+\b',r'\b\d+\.\d*\b',r'\b\d+\b',r'\b\w+\b']
LABELS=[r'\b\w+:\b']

if DEBUG:
	print WORDS
all_tokens=[]
all_tokens.extend(STRING)
all_tokens.extend(WORDS)
all_tokens.extend(OPERATORS)
all_tokens.extend(IDENTIFIER_NUMBER)
#all_tokens.extend(LABELS)

regex=re.compile('|'.join(all_tokens))

def tokenize(line):
	if DEBUG:
		print regex.findall(line)
	return regex.findall(line)

if __name__=='__main__':
	from sys import stdin
	for line in stdin:
		normal=line.split()
		my=tokenize(line)
		print normal
		print my
