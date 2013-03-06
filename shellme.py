from commands import getoutput
from argparse import ArgumentParser
from os import system
import sys

"""Lazy mans shellcode maker.  Wraps nasm/objdump stuff.
"""

def check():
	"""i need nasm/objdump"""
	found = True
	if getoutput("which nasm") == '':
		found = False
	elif getoutput("which objdump") == '':
		found = False
	return found

def get_output(inf,arch='elf'):
	"""format into a string of bytes"""
	output = ''
	if '.nasm' in inf:
		tmp = getoutput("nasm -f %s %s"%(arch,inf))
		if 'error' in tmp:
			print '[-] Error in your asm: ', tmp
			sys.exit(1)	
		inf = inf.replace(".nasm", ".o")
	tmp = getoutput("objdump -d %s"%inf)
	
	opcodes = ''
	for line in tmp.split('\n')[7:]:
		tmp = line.split(':',1)
		if len(tmp) > 1 and len(tmp[1]) > 0: tmp = tmp[1]
		else: continue

		# split on tab to get opcodes
		tmp = ''.join(tmp).split('\t')
		if len(tmp) > 1: tmp = tmp[1].strip().replace(' ','')
		if '<' in tmp: continue
		opcodes += tmp
	return opcodes

def encode(lbyte):
	"""Take the opcode string and insert \\x's.  
	   I'll add in fancy encoding and output
	   formatting eventually.
	"""
	formatted_lbyte = ''.join(["\\x"+lbyte[idx]+lbyte[idx+1] for idx in range(0,len(lbyte)-1,2)])
	return formatted_lbyte

def format_output(dmp,width=8):
	"""Input should just be a stream of formatted hex bytes
	   i.e. \\x05\\x06\\x07...
	   Returns this truncated into columns with a width of width 
	"""
	dmp = dmp.split('\\x')[1:]
	return '\\x'+'\n\\x'.join(['\\x'.join(dmp[i:i+width]) for i in range(0,len(dmp),width)])

def compile_instruction(instruction,arch='elf'):
	"""Compile a single instruction and return opcodes"""
	with open('/tmp/tmp-me.nasm', 'w+') as f:
		f.write(instruction.decode('string-escape')+'\n')
	ops = encode(get_output('/tmp/tmp-me.nasm',arch))
	system('rm -f /tmp/tmp-me.nasm /tmp/tmp-me.o')
	return ops

def run(options):
	"""encode/dump"""
	if options.inf:
		dmp = encode(get_output(options.inf,options.arch))
	elif options.instruction:
		dmp = compile_instruction(options.instruction,options.arch)

	print '[+] Encoded:\n', format_output(dmp)
	if options.output:
		with open(options.output, 'w') as f:
			f.write(format_output(dmp))

def arguments():
	"""Handle cli"""
	parser = ArgumentParser()
	parser.add_argument('-n',help='nasm or object file',metavar='FILE',action='store',dest='inf')
	parser.add_argument('-o',help='output file',action='store',dest='output')
	parser.add_argument('-i',help='instruction',action='store',dest='instruction')
	parser.add_argument('-a',help='architecture [elf/elf64]',action='store',dest='arch',default='elf')

	if len(sys.argv) < 2:
		parser.print_help()
		sys.exit(1)

	return parser.parse_args()	

if __name__=="__main__":	
	if not check():
		print '[-] I need objdump and nasm'
		sys.exit(1)
	run(arguments())
