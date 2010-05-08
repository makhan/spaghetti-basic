"""
A module that simply bolts on simple loops
by translating them into interpretable code in Spaghetti.
"""

from tokenizer import tokenize
header="""
DIM __call_stack(1000000) AS INTEGER
DIM __loop_stack(1000000) AS INTEGER
__call_sp=0
__loop_sp=0
"""

DEBUG=False

def translate(lines):
	#output=tokenize(header)
	if DEBUG:
		for line in lines:
			print line
	output=[]
	cur_line=900000
	last_loop=[]
	loop_stack=[]
	for line in lines:
		if len(line)==0:
			continue
		if line[0]=='FOR':
			var,start,end=line[1],line[3],line[5]
			if len(line)>6:
				step=line[7]
			else:
				step=+1
			if DEBUG:
				print "found var=%s, start=%s, end=%s, step=%s"%(var,start,end,step)
			output.append([str(cur_line),'LET',var,'=',start])
			cur_line+=1
			
			#output.append(tokenize("__loop_stack(__call_sp)=%d"%cur_line)
			#output.append(tokenize("__call_sp=__call_sp+1"))
			output.append([str(cur_line), 'IF',var,'=',end,'THEN','GOTO'])
			
			loop_stack.append(step)
			loop_stack.append(var)
			loop_stack.append(cur_line)
			last_loop.append(len(output)-1)
			cur_line+=1
		elif line[0]=='NEXT':
			try:
				return_point=last_loop.pop()
			except IndexError:
				print "Unmatched NEXT"
				return []
			return_line=loop_stack.pop()
			var=loop_stack.pop()
			step=loop_stack.pop()
			output.append(['LET',var,'=',var,'+',str(step)])
			output.append(['GOTO', str(return_line)])
			#line after NEXT
			cur_line+=1
			output[return_point].append(str(cur_line))
			output.append([str(cur_line),'REM','Line after for loop'])
			cur_line+=1
		else:
			output.append(line)
	if DEBUG:
		for line in output:
			print line
	return output
