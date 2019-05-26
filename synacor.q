/ q implementation of synacor vm

MAXINT:"j"$2 xexp 15 / 32768

Read:{ $[MAXINT>x;x;.vm.reg x - MAXINT] };
SetRegister:{ .vm.reg[x - MAXINT]:y mod MAXINT };
BitwiseOr:{  0b sv (0b vs x)|(0b vs y) };
BitwiseAnd:{ 0b sv (0b vs x)&(0b vs y) };
BitwiseNot:{ 0b sv 0b,-15#not(0b vs x) };
BitwiseXor:{ 0b sv (0b vs x)<>0b vs y };

// 0. stop execution and terminate the program
Halt:{[] .vm.run:0b; };
// 1. set register <a> to the value of <b>
Set:{ SetRegister[x;] Read y; };
// 2. push <a> onto the stack
Push:{ .vm.stk,:Read x; };
// 3. remove the top element from the stack and write it into <a>; empty stack = error
Pop:{ SetRegister[x;] last .vm.stk;.vm.stk:-1 _ .vm.stk; };
// 4. set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise
Eq:{ SetRegister[x;] Read[y] = Read z; };
// 5. set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise
Gt:{ SetRegister[x;] Read[y] > Read z; };
// 6. jump to <a>
Jmp:{ Read x };
// 7. if <a> is nonzero, jump to <b>
Jt:{ if[Read x;:Read y]; };
// 8. if <a> is zero, jump to <b>
Jf:{ if[0=Read x;:Read y]; };
// 9. assign into <a> the sum of <b> and <c> (modulo 32768)
Add:{ SetRegister[x;] Read[y] + Read z; };
// 10. store into <a> the product of <b> and <c> (modulo 32768)
Mult:{ SetRegister[x;] Read[y] * Read z; };
// 11. store into <a> the remainder of <b> divided by <c>
Mod:{ SetRegister[x;] Read[y] mod Read z; };
// 12. stores into <a> the bitwise and of <b> and <c>
And:{ SetRegister[x;] BitwiseAnd[Read y;Read z]; };
// 13. stores into <a> the bitwise or of <b> and <c>
Or:{ SetRegister[x;] BitwiseOr[Read y;Read z]; };
// 14. stores 15-bit bitwise inverse of <b> in <a>
Not:{ SetRegister[x;] BitwiseNot Read y; };
// 15. read memory at address <b> and write it to <a>
Rmem:{ SetRegister[x;] .vm.mem Read y };
// 16. write the value from <b> into memory at address <a>
Wmem:{ .vm.mem[Read x]:Read y };
// 17. write the address of the next instruction to the stack and jump to <a>
Call:{ Push[.vm.ptr+2];.vm.calls,:Read x;:Read x };
// 18. remove the top element from the stack and jump to it; empty stack = halt
Ret:{[] p:last .vm.stk;.vm.stk:-1 _ .vm.stk;:p; };
// 19. write the character represented by ascii code <a> to the terminal
Out:{ $[10=Read x;[-1"c"$.vm.stdout;.vm.stdout:()];.vm.stdout,:Read x]; };
// 20. read a character from the terminal and write its ascii code to <a>
In:{
  if[0=count .vm.stdin;
    .vm.stdin:("j"$read0 0),10; // append newline
    // custom behaviour
    if[.vm.stdin~"j"$"fix\n";
      .vm.reg[7]:1;                      // non-zero register 7
      .vm.mem[5489 5490]:2#21;           // skip billion year check
      .vm.mem[5491 5492 5493 5494]:4#21; // skip validation of return value
      -1@"teleporter fixed\nWhat do you do?";
      .vm.stdin:("j"$read0 0),10
      ];
    ];
  SetRegister[x;] first .vm.stdin;
  .vm.stdin:1_.vm.stdin;
  };
// 21. no operation
Noop:{[] };
// 22. xor a and b and store back in a
Xor:{ SetRegister[x;] BitwiseXor[Read x;Read y]; };

// setup instructions and argument counts
.vm.inst:(Halt;Set;Push;Pop;Eq;Gt;Jmp;Jt;Jf;Add;Mult;Mod;And;Or;Not;Rmem;Wmem;Call;Ret;Out;In;Noop;Xor)
.vm.argc:{ $[null first v:value[x][1];0;count v] } each .vm.inst

// each number is stored as a 16-bit little-endian pair (low byte, high byte)
.vm.mem:{256 sv reverse x} each 2 cut read1 `:challenge.bin
.vm.run:0b
.vm.stk:.vm.stdin:.vm.stdout:()
.vm.reg:8#0
.vm.ptr:0
.vm.calls:()

// hack 2125 to be pure xor
.vm.mem[2125 + til 4]:22 32768 32769 18
vm:{[]
  .vm.run:1b;
  while[.vm.run;
    .vm.ptr:$[null r:.vm.inst[i]. $[a:.vm.argc i:.vm.mem .vm.ptr;.vm.mem 1 + .vm.ptr + til a;1#`];
              1 + .vm.ptr + a;
              r
             ]
    ]
  };
/ run the virtual machine
vm[]
