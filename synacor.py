import struct # for pack, unpack
import sys    # for exit

class vm:
    # define memory
    memory = None
    # initialise registers to zero
    register = 8*[0]
    # initialise empty stack
    stack = []
    # initialise instruction pointer
    ptr = 0
    # buffers for std in and out
    stdout = []
    stdin = []
    #
    debuglog = None
    debug = False
    # 15-bit addressable space
    MAXINT = pow(2, 15)

    # returns value in register or literal
    def _tryregister(self, x):
        return x if x < self.MAXINT else self.register[x - self.MAXINT]

    # writes value y to register x
    def _register(self, x,y):
        self.register[x - self.MAXINT] = int(y)

    #print to screen if _debug is enabled
    def _dbg(self, x):
        if self.debuglog is None:
            self.debuglog = open("debug.log","a")
        self.debuglog.write(str(self.ptr) + "\t"  + " ".join(x) + "\n")

    def _stdout(self, x):
        if x == ord("\n"):
            print "".join(self.stdout)
            self.stdout = []
        else:
            self.stdout.append(chr(x))

    def _stdin(self):
        if len(self.stdin) == 0:
            ui = raw_input()
            # custom debug commands
            while ui.split(" ")[0] in ["dump", "load", "debug", "registers", "exit", "fix", "peek", "poke"]:
                args = ui.split(" ")
                cmd = args[0]
                if cmd == "dump":
                    with open ("memory.dmp","wb") as s:
                        s.write(struct.pack("<" + "H" * len(self.memory), *self.memory))
                        print "Memory dumped."
                    with open ("registers.dmp","wb") as s:
                        s.write(struct.pack("<" + "H" * 8, *self.register))
                        print "Registers dumped."
                    with open ("stack.dmp","wb") as s:
                        s.write(struct.pack("<" + "H" * len(self.stack), *self.stack))
                        print "Stack dumped."
                    with open ("ptr.dmp","wb") as s:
                        s.write(struct.pack("<" + "H", self.ptr))
                        print "Ptr dumped."
                elif cmd == "load":
                    with open ("memory.dmp","rb") as s:
                        d = s.read()
                        self.memory = [x for x in struct.unpack("<" + "H" * int(0.5*len(d)), d)]
                    with open ("registers.dmp","rb") as s:
                        d = s.read()
                        self.register = [x for x in struct.unpack("<" + "H" * 8, d)]
                    with open ("stack.dmp","rb") as s:
                        d = s.read()
                        self.stack = [x for x in struct.unpack("<" + "H" * int(0.5*len(d)),d)]
                    with open ("ptr.dmp","rb") as s:
                        self.ptr = struct.unpack("<H", s.read())[0]
                elif cmd == "fix":
                    print "'Fixing' teleporter"
                    self._fixteleporter()
                elif cmd == "debug":
                    print "Debug: " + ("off" if self.debug else "on")
                    self.debug = ~self.debug
                elif cmd == "registers":
                    print "Registers",[x for x in self.register]
                elif cmd == "peek":
                    if len(args) == 3:
                        self._peek(*[int(x) for x in args[1:]])
                    else:
                        print "peek requires address and length"
                elif cmd == "poke":
                    if len(args) == 3:
                        self._poke(*[int(x) for x in args[1:]])
                    else:
                        print "poke requires address and value"
                elif cmd == "exit":
                    sys.exit()
                print "What do you do?"
                ui = raw_input()
            self.stdin = [ord(x) for x in ui + "\n"]
        return self.stdin.pop(0) # pop front of queue

    # stop execution and terminate the program
    def _halt(self):
      self.running = False
    # set register <a> to the value of <b>
    def _set(self, a, b):
      self._register(a,self._tryregister(b))
    # push <a> onto the stack
    def _push(self, a):
      self.stack.append(self._tryregister(a))
    # remove the top element from the stack and write it into <a>; empty stack = error
    def _pop(self, a):
      self._register(a,self.stack.pop())
    # set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise
    def _eq(self, a, b, c):
      self._register(a, self._tryregister(b) == self._tryregister(c))
    # set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise
    def _gt(self, a, b, c):
      self._register(a, self._tryregister(b) > self._tryregister(c))
    # jump to <a>
    def _jmp(self, a):
      return self._tryregister(a)
    # jump-true, if <a> is nonzero, jump to <b>
    def _jt(self, a, b):
      return self._tryregister(b) if self._tryregister(a) != 0 else None
    # jump-false, if <a> is zero, jump to <b>
    def _jf(self, a, b):
      return self._tryregister(b) if self._tryregister(a) == 0 else None
    # assign into <a> the sum of <b> and <c> (modulo 32768)
    def _add(self, a, b, c):
      self._register(a, (self._tryregister(b) + self._tryregister(c)) % self.MAXINT)
    # store into <a> the product of <b> and <c> (modulo 32768)
    def _mult(self, a, b, c):
      self._register(a, (self._tryregister(b) * self._tryregister(c)) % self.MAXINT)
    # store into <a> the remainder of <b> divided by <c>
    def _mod(self, a, b, c):
      self._register(a,self._tryregister(b) % self._tryregister(c))
    # stores into <a> the bitwise and of <b> and <c>
    def _and(self, a, b, c):
      self._register(a,self._tryregister(b) & self._tryregister(c))
    # stores into <a> the bitwise or of <b> and <c>
    def _or(self, a, b, c):
      self._register(a,self._tryregister(b) | self._tryregister(c))
    # stores 15-bit bitwise inverse of <b> in <a>
    def _not(self, a, b):
      self._register(a,0x7fff & ~self._tryregister(b))
    # read memory at address <b> and write it to <a>
    def _rmem(self, a, b):
      self._register(a,self.memory[self._tryregister(b)])
    # write the value from <b> into memory at address <a>
    def _wmem(self, a, b):
      self.memory[self._tryregister(a)] = self._tryregister(b)
    # write the address of the next instruction to the stack and jump to <a>
    def _call(self, a):
      self.stack.append(self.ptr + 1)
      return self._tryregister(a)
    # remove the top element from the stack and jump to it; empty stack = halt
    def _ret(self):
      return self.stack.pop()
    # write the character represented by ascii code <a> to the terminal
    def _out(self, a):
      self._stdout(self._tryregister(a))
    # read a character from the terminal and write its ascii code to <a>
    def _in(self, a):
      self._register(a,self._stdin())
    # no operation
    def _noop(self):
      return

    def _fixteleporter(self):
      self.register[7] = 1 # correct value TBD
      #self.memory[6027] = 8 # change jt 32768 6035 => jf 32768 6035 (skip teleporter sanity)
    def _peek(self, address, length):
      print " ".join([str(x) for x in self.memory[address:address+length]])
    def _poke(self, address, value):
      print "Poke: " + str(address) + " = " + str(value)
      self.memory[address] = value

    instructionset = [_halt, _set, _push, _pop, _eq, _gt, _jmp, _jt, _jf, _add, _mult, _mod, _and, _or, _not, _rmem, _wmem, _call, _ret, _out, _in, _noop]
    arguments =      [0,     2,    1,     1,    3,   3,   1,    2,   2,   3,    3,     3,    3,    3,   2,    2,     2,     1,     0,    1,    1,   0]
    names =          ["halt","set","push","pop","eq","gt","jmp","jt","jf","add","mult","mod","and","or","not","rmem","wmem","call","ret","out","in","noop"]

    # public methods
    def loadmemory(self,memory):
        self.memory = memory

    def run(self):
        self.running = True
        while (self.running):
            i = self.memory[self.ptr]
            argcount = self.arguments[i]
            self.ptr += 1
            args = [x for x in self.memory[self.ptr:self.ptr+argcount]]
            if self.debug:
                self._dbg([self.names[i]] + [str(x) for x in args])
                #self._dbg([str(x) for x in self.register])
            res = self.instructionset[i](self, *args)
            if res:                 # jump
                self.ptr = res
            else:                   # no jump, implicit return of None
                self.ptr += argcount

with open ("challenge.bin", "rb") as datafile:
    VM = vm()
    data = datafile.read()
    memory = [x for x in struct.unpack("<" + "H" * int(0.5 * len(data)), data)]
    VM.loadmemory(memory)
    try:
        VM.run()
    except KeyboardInterrupt:
        print "\nCTRL+C pressed, exiting."
