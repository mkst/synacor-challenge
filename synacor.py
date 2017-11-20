import struct # for unpack
import sys    # for exit

# 15-bit addressable space
MAXINT = 32768

# returns value in register or literal
def _tryregister(x):
  return x if x < MAXINT else register[x - MAXINT]
# writes value y to register x
def _register(x,y):
  register[x - MAXINT] = y
#print to screen if _debug is enabled
def _dbg(x):
  if _debug:
    print ptr,"\t"," ".join(x)

def _stackerr():
  print "Error: Empty stack, halting"
  return _halt()

def _stdout(x):
  global stdout_buf
  if x == 10:
    print "".join(stdout_buf)
    stdout_buf = []
  else:
    stdout_buf.append(chr(x))

def _stdin():
  global stdin_buf
  if len(stdin_buf) == 0:
    ui = raw_input()
    # custom debug commands
    while ui in ["dump","debug", "registers", "exit"]:
      if ui == "dump":
        with open ("memory.dmp","wb") as s:
          s.write(struct.pack("<" + "H" * len(memory), *memory))
          print "Memory dumped."
      elif ui == "debug":
        global _debug
        print "Debug: " + ("off" if _debug else "on")
        _debug = ~_debug
      elif ui == "registers":
        print "Registers",[x for x in register]
      elif ui == "exit":
        sys.exit()
      print "What do you do?"
      ui = raw_input()

    stdin_buf = [ord(x) for x in ui] + [10]
  return stdin_buf.pop(0) # pop front of queue

# stop execution and terminate the program
def _halt():
  global running
  running = False
# set register <a> to the value of <b>
def _set(a, b):
  _dbg(["_set",str(a),str(b)])
  _register(a,_tryregister(b))
# push <a> onto the stack
def _push(a):
  _dbg(["_push",str(a)])
  stack.append(_tryregister(a))
# remove the top element from the stack and write it into <a>; empty stack = error
def _pop(a):
  _dbg(["_pop",str(a)])
  if len(stack) == 0:
    return _stackerr()
  _register(a,stack.pop())
# set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise
def _eq(a,b,c):
  _dbg(["_eq",str(a),str(b),str(c)])
  value = 1 if _tryregister(b) == _tryregister(c) else 0
  _register(a,value)
# set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise
def _gt(a,b,c):
  _dbg(["_gt",str(a),str(b),str(c)])
  value = 1 if _tryregister(b) > _tryregister(c) else 0
  _register(a,value)
# jump to <a>
def _jmp(a):
  _dbg(["_jmp",str(a)])
  return _tryregister(a)
# jump-true, if <a> is nonzero, jump to <b>
def _jt(a,b):
  _dbg(["_jt",str(a),str(b)])
  return _tryregister(b) if _tryregister(a) != 0 else None
# jump-false, if <a> is zero, jump to <b>
def _jf(a,b):
  _dbg(["_jf",str(a),str(b)])
  return _tryregister(b) if _tryregister(a) == 0 else None
# assign into <a> the sum of <b> and <c> (modulo 32768)
def _add(a,b,c):
  _dbg(["_add",str(a),str(b),str(c)])
  _register(a, (_tryregister(b) + _tryregister(c)) % MAXINT)
# store into <a> the product of <b> and <c> (modulo 32768)
def _mult(a,b,c):
  _dbg(["_mult",str(a),str(b),str(c)])
  _register(a, (_tryregister(b) * _tryregister(c)) % MAXINT)
# store into <a> the remainder of <b> divided by <c>
def _mod(a,b,c):
  _dbg(["_mod",str(a),str(b),str(c)])
  _register(a,_tryregister(b) % _tryregister(c))
# stores into <a> the bitwise and of <b> and <c>
def _and(a,b,c):
  _dbg(["_and",str(a),str(b),str(c)])
  _register(a,_tryregister(b) & _tryregister(c))
# stores into <a> the bitwise or of <b> and <c>
def _or(a,b,c):
  _dbg(["_or",str(a),str(b),str(c)])
  _register(a,_tryregister(b) | _tryregister(c))
# stores 15-bit bitwise inverse of <b> in <a>
def _not(a,b):
  _dbg(["_not",str(a),str(b)])
  _register(a,0x7fff & ~_tryregister(b))
# read memory at address <b> and write it to <a>
def _rmem(a,b):
  _dbg(["_rmem",str(a),str(b)])
  _register(a,memory[_tryregister(b)])
# write the value from <b> into memory at address <a>
def _wmem(a,b):
  _dbg(["_wmem",str(a),str(b)])
  memory[_tryregister(a)] = _tryregister(b)
# write the address of the next instruction to the stack and jump to <a>
def _call(a):
  _dbg(["_call",str(a)])
  stack.append(ptr + 1)
  return _tryregister(a)
# remove the top element from the stack and jump to it; empty stack = halt
def _ret():
  _dbg(["_ret"])
  if(len(stack)==0):
    return _stackerr()
  return stack.pop()
# write the character represented by ascii code <a> to the terminal
def _out(a):
  _stdout(_tryregister(a))
# read a character from the terminal and write its ascii code to <a>
def _in(a):
  _register(a,_stdin())
# no operation
def _noop():
  #print ptr,"\t_noop"
  return

instructionset = [_halt, _set, _push, _pop, _eq, _gt, _jmp, _jt, _jf, _add, _mult, _mod, _and, _or, _not, _rmem, _wmem, _call, _ret, _out, _in, _noop]
argcounts =      [0,     2,    1,     1,    3,   3,   1,    2,   2,   3,    3,     3,    3,    3,   2,    2,     2,     1,     0,    1,    1,   0]

# eight registers
register = [0] * 8
# an unbounded stack which holds individual 16-bit values
stack = []
# array to buffer stdout
stdout_buf = []
# array to buffer input
stdin_buf = []
# instruction pointer
ptr = 0
# debug to screen?
_debug = False

with open ("challenge.bin", "rb") as datafile:
  # read contents of binary file
  data = datafile.read()
  # memory with 15-bit address space storing 16-bit values
  # each number is stored as a 16-bit little-endian pair (low byte, high byte)
  # programs are loaded into memory starting at address 0
  memory = [x for x in struct.unpack("<" + "H" * int(0.5 * len(data)), data)]
  # initialise variables
  running = True
  # run virtual machine
  while(running):
    # fetch current instruction
    i = memory[ptr]
    # pull argcount
    argcount = argcounts[i]
    # increment pointer to args
    ptr += 1
    # extract arguments
    args = [x for x in memory[ptr:ptr+argcount]]
    # execute instruction
    res = instructionset[i](*args)
    # check return value
    if res == None:        # no jump, implicit return of None
      ptr += argcount
    else:                  # jump
      ptr = res