"""This module is an incomplete implementation of the VM required to solve the Synacor challenge"""

import struct # for pack, unpack
import sys    # for exit

# 15-bit addressable space
MAXINT = pow(2, 15)

# pylint: disable=too-many-instance-attributes,too-few-public-methods
class Synacor(object):
    """The Synacore Virtual Machine"""

    def _try_register(self, x):
        """returns value in register or literal"""
        return x if x < MAXINT else self.register[x - MAXINT]

    def _register(self, x, y):
        """writes value y to register x"""
        self.register[x - MAXINT] = int(y)

    def _stdout(self, x):
        """append to stdout buffer, print if newline"""
        if x == ord("\n"):
            print "".join(self.stdout)
            self.stdout = list()
        else:
            self.stdout.append(chr(x))

    def _stdin(self):
        """read into stdin buffer if empty, else pop stdin buffer"""
        def user_input():
            """read user input"""
            raw = raw_input()
            ui = raw.split(" ")
            return [raw, ui[0], ui[1:]]
        if len(self.stdin) == 0:
            raw, cmd, args = user_input()
            while cmd in self.own_instructions:
                try:
                    self.own_instructions[cmd](self, *args)
                except TypeError as e:
                    print e
                print "What do you do?"
                raw, cmd, args = user_input()
            self.stdin = [ord(x) for x in raw + "\n"]
        return self.stdin.pop(0) # pop front of queue

    def _halt(self):
        """stop execution and terminate the program"""
        self.running = False
    def _set(self, a, b):
        """set register <a> to the value of <b>"""
        self._register(a, self._try_register(b))
    def _push(self, a):
        """push <a> onto the stack"""
        self.stack.append(self._try_register(a))
    def _pop(self, a):
        """remove the top element from the stack and write it into <a>"""
        self._register(a, self.stack.pop())
    def _eq(self, a, b, c):
        """set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise"""
        self._register(a, self._try_register(b) == self._try_register(c))
    def _gt(self, a, b, c):
        """set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise"""
        self._register(a, self._try_register(b) > self._try_register(c))
    def _jmp(self, a):
        """jump to <a>"""
        return self._try_register(a)
    def _jt(self, a, b):
        """jump-true, if <a> is nonzero, jump to <b>"""
        return self._try_register(b) if self._try_register(a) != 0 else None
    def _jf(self, a, b):
        """jump-false, if <a> is zero, jump to <b>"""
        return self._try_register(b) if self._try_register(a) == 0 else None
    def _add(self, a, b, c):
        """assign into <a> the sum of <b> and <c> (modulo 32768)"""
        self._register(a, (self._try_register(b) + self._try_register(c)) % MAXINT)
    def _mult(self, a, b, c):
        """store into <a> the product of <b> and <c> (modulo 32768)"""
        self._register(a, (self._try_register(b) * self._try_register(c)) % MAXINT)
    def _mod(self, a, b, c):
        """store into <a> the remainder of <b> divided by <c>"""
        self._register(a, self._try_register(b) % self._try_register(c))
    def _and(self, a, b, c):
        """store into <a> the bitwise and of <b> and <c>"""
        self._register(a, self._try_register(b) & self._try_register(c))
    def _or(self, a, b, c):
        """store into <a> the bitwise or of <b> and <c>"""
        self._register(a, self._try_register(b) | self._try_register(c))
    def _not(self, a, b):
        """store 15-bit bitwise inverse of <b> in <a>"""
        self._register(a, 0x7fff & ~self._try_register(b))
    def _rmem(self, a, b):
        """read memory at address <b> and write it to <a>"""
        self._register(a, self.memory[self._try_register(b)])
    def _wmem(self, a, b):
        """write the value from <b> into memory at address <a>"""
        #if a == 3952:
        #    print "orb value ",self._try_register(b)
        #elif a == 3953:
        #    print "steps taken",self._try_register(b)
        self.memory[self._try_register(a)] = self._try_register(b)
    def _call(self, a):
        """write the address of the next instruction to the stack and jump to <a>"""
        self.stack.append(self.ptr + 2) # call takes 1 argument
        return self._try_register(a)
    def _ret(self):
        """remove the top element from the stack and jump to it"""
        return self.stack.pop()
    def _out(self, a):
        """push character represented by ascii code <a> to stdout buffer"""
        self._stdout(self._try_register(a))
    def _in(self, a):
        """pop character from stdin buffer and write its ascii code to <a>"""
        self._register(a, self._stdin())

    # custom functions
    def _dump(self):
        """dump out memory, registers, stack and instruction pointer to disk"""
        def dump(filename, data):
            """inner dump function"""
            with open(filename, "wb") as save:
                save.write(data)
        dump("memory.dmp",
             struct.pack("<" + "H" * len(self.memory), *self.memory))
        dump("register.dmp",
             struct.pack("<" + "H" * len(self.register), *self.register))
        dump("stack.dmp",
             struct.pack("<" + "H" * len(self.stack), *self.stack))
        dump("ptr.dmp",
             struct.pack("<" + "H", self.ptr))

    def _load(self):
        """load in memory, registers, stack and instruction pointer from disk"""
        def load(filename, unpack):
            """inner load function"""
            with open(filename, "rb") as save:
                dump = save.read()
                return list(struct.unpack(unpack, dump))
        self.memory = load("memory.dmp",
                           "<" + "H" * len(self.memory))
        self.register = load("register.dmp",
                             "<" + "H" * len(self.register))
        self.stack = load("stack.dmp",
                          "<" + "H" * len(self.stack))
        self.ptr = load("ptr.dmp",
                        "<" + "H")[0]
    def _fix_teleporter(self):
        print "'Fixing' teleporter..."
        self.register[7] = 1 # correct value TBD, wrong value => incorrect code
        self._poke(6027, 8) # change jt R0 6035 => jf R0 6035 (skip teleporter sanity)
        self._poke(5495, 7) # change jf R1 5579 to jt R1 5579 (skip valid value check)
    def _toggle_debug(self):
        print "Debug " + ("off" if self.debug else "on")
        self.debug = ~self.debug
    def _print_registers(self):
        print "Registers", self.ptr, [x for x in self.register]
    def _peek(self, address, length):
        print " ".join(str(x) for x in self.memory[int(address):int(address) + int(length)])
    def _poke(self, address, value):
        print "Poke: " + str(address) + " = " + str(value)
        self._wmem(int(address), int(value))
    def _dump_known_instructions(self):
        with open("instructions.txt", "w") as dmp:
            for _, v in sorted(self.known_instructions.iteritems()):
                dmp.write(v + "\n")

    own_instructions = dict([("dump", _dump),
                             ("load", _load),
                             ("fix", _fix_teleporter),
                             ("debug", _toggle_debug),
                             ("registers", _print_registers),
                             ("peek", _peek),
                             ("poke", _poke),
                             ("dki", _dump_known_instructions),
                             ("exit", sys.exit)])

    instructions = [[_halt, 0, "halt"], # 0
                    [_set, 2, "set"],   # 1
                    [_push, 1, "push"], # 2
                    [_pop, 1, "pop"],   # 3
                    [_eq, 3, "eq"],     # 4
                    [_gt, 3, "gt"],     # 5
                    [_jmp, 1, "jmp"],   # 6
                    [_jt, 2, "jt"],     # 7
                    [_jf, 2, "jf"],     # 8
                    [_add, 3, "add"],   # 9
                    [_mult, 3, "mult"], # 10
                    [_mod, 3, "mod"],   # 11
                    [_and, 3, "and"],   # 12
                    [_or, 3, "or"],     # 13
                    [_not, 2, "not"],   # 14
                    [_rmem, 2, "rmem"], # 15
                    [_wmem, 2, "wmem"], # 16
                    [_call, 1, "call"], # 17
                    [_ret, 0, "ret"],   # 18
                    [_out, 1, "out"],   # 19
                    [_in, 1, "in"],     # 20
                    [lambda x: None, 0, "noop"]
                   ]

    def _create_debug_string(self, instruction_name, args):
        debug_string = ""
        debug_string += str(self.ptr).ljust(6)
        debug_string += instruction_name.ljust(5)
        regs = [x if x < MAXINT else "R" + str(x-MAXINT) for x in args]
        debug_string += " ".join(str(x).ljust(6) for x in regs).ljust(20)
        debug_string += "| "
        debug_string += " ".join(str(x).ljust(6) for x in self.register)
        return debug_string

    def _dbg(self, instruction_name, args):
        """write debug info to debug log"""
        if not self.debug_file:
            self.debug_file = open("debug.log", "a")
        self.debug_file.write(self._create_debug_string(instruction_name, args) + "\n")

    def __init__(self, memory, debug=False):
        self.running = False
        # initialise memory
        self.memory = memory
        # initialise registers to zero
        self.register = 8*[0]
        # initialise empty stack
        self.stack = list()
        # initialise instruction pointer
        self.ptr = 0
        # buffers for std in and out
        self.stdout = list()
        self.stdin = list() # no need for collections.deque
        # debug settings
        self.debug_file = None
        self.debug = debug
        self.known_instructions = dict()

    def run(self):
        """Start up the Virtual Machine"""
        self.running = True

        while self.running:
            # current instruction
            instruction = self.memory[self.ptr]
            func, argcount, name = self.instructions[instruction]
            args = self.memory[self.ptr + 1:self.ptr + argcount + 1]
            if self.ptr not in self.known_instructions:
                self.known_instructions[self.ptr] = self._create_debug_string(name, args)
            if self.debug:
                self._dbg(name, args)
            res = func(self, *args)
            # if result is a location, jump to it, otherwise go to next instruction
            self.ptr = res if res else self.ptr + argcount + 1

        self._dump_known_instructions()

with open("challenge.bin", "rb") as f:
    rom = f.read()
    mem = list(struct.unpack("<" + "H" * (len(rom) / 2), rom))
    VM = Synacor(mem, debug=False)
    try:
        VM.run()
    except KeyboardInterrupt:
        print "\nCTRL+C pressed, exiting."
