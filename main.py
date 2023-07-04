#!/usr/bin/env python3

import codecs
import time
import sys
import ast
import os
import io

ver = "dev"

operations = [
    "OP_INTPUSH",
    "OP_STRINGPUSH",
    "OP_MEMREAD",
    "OP_MEMWRITE",
    "OP_EXIT",
    "OP_SLEEP",
    "OP_PLUS",
    "OP_MINUS",
    "OP_MULT",
    "OP_DIVMOD",
    "OP_POW",
    "OP_INPUT",
    "OP_DUMP",
    "OP_STRINGIFY",
    "OP_INTIFY",
    "OP_LENGTH",
    "OP_DUPLICATE",
    "OP_OVER",
    "OP_SWAP",
    "OP_ROT",
    "OP_INCLUDE",
    "OP_DROP",
    "OP_PROC",
    "OP_EQUALS",
    "OP_NOT",
    "OP_OR",
    "OP_AND",
    "OP_BOR",
    "OP_BAND",
    "OP_RSHIFT",
    "OP_LSHIFT",
    "OP_LTOE",
    "OP_GTOE",
    "OP_LT",
    "OP_GT",
    "OP_IF",
    "OP_ELSE",
    "OP_WHILE",
    "OP_END",
]

for k, i in enumerate(operations):
    exec(f"{i} = k")  # bad decision ;(

include_paths = [os.path.abspath("inc"), os.getcwd()]

def push_int(num):
    return (OP_INTPUSH, num)

def push_str(string):
    return (OP_STRINGPUSH, string)

def memory_read():
    return (OP_MEMREAD, )

def memory_write():
    return (OP_MEMWRITE, )

def exit_():
    return (OP_EXIT, )

def sleep():
    return (OP_SLEEP, )

def plus():
    return (OP_PLUS, )

def minus():
    return (OP_MINUS, )

def mult():
    return (OP_MULT, )

def dividemod():
    return (OP_DIVMOD, )

def powerof():
    return (OP_POW, )

def input_():
    return (OP_INPUT, )

def dump():
    return (OP_DUMP, )

def stringify():
    return (OP_STRINGIFY, )

def intify():
    return (OP_INTIFY, )

def length():
    return (OP_LENGTH, )
    
def duplicate():
    return (OP_DUPLICATE, )
    
def over():
    return (OP_OVER, )

def swap():
    return (OP_SWAP, )

def rot():
    return (OP_ROT, )

def include():
    return (OP_INCLUDE, )

def drop():
    return (OP_DROP, )

def procedure(name):
    return (OP_PROC, name)

def equals():
    return (OP_EQUALS, )

def not_():
    return (OP_NOT, )

def or_():
    return (OP_OR, )

def and_():
    return (OP_AND, )

def bitwise_or():
    return (OP_BOR, )

def bitwise_and():
    return (OP_BAND, )

def bitwise_shift_right():
    return (OP_RSHIFT, )

def bitwise_shift_left():
    return (OP_LSHIFT, )

def greaterthan_or_equeal():
    return (OP_GTOE, )

def lesserthan_or_equeal():
    return (OP_LTOE, )

def greaterthan():
    return (OP_GT, )

def lesserthan():
    return (OP_LT, )

def if_start():
    return (OP_IF, )

def if_else():
    return (OP_ELSE, )

def while_start(condition):
    return (OP_WHILE, condition)

def end():
    return (OP_END, )


def isint(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

def find_next(stack, cursor, func):
    for k, i in enumerate(stack[cursor:]):
        if func(i):
            return k + cursor
    return -1

def encode_block_bytecode(block, bytesio):
    for i in block:
        bytesio.write(b"\xFD")
        for j in i:
            if isinstance(j, int):
                bytesio.write(b"\x00")
                bytesio.write(j.to_bytes(4, "little", signed=False))
            elif isinstance(j, str):
                bytesio.write(b"\x01")
                bytesio.write(len(j.encode()).to_bytes(4, "little", signed=False))
                bytesio.write(j.encode())
            elif isinstance(j, list):
                bytesio.write(b"\x02")
                encode_block_bytecode(j, bytesio)
                bytesio.write(b"\x03")
            else:
                print(f"ERROR: bytecode-encoding failure: cant encode type {type(j)}")
                print(f"ERROR: {j}")
        bytesio.write(b"\xFE")

def encode_bytecode(lexed, bytesio):
    bytesio.write(b"BLBC")
    encode_block_bytecode(lexed, bytesio)
    bytesio.write(b"\xFF")
    bytesio.close()

def decode_bytecode(bytesio):
    magic = bytesio.read(4)
    if magic != b"BLBC":
        print(f"ERROR: magic does not match - file may be corrupt or not bl bytecode")
        exit(1)

    lexed = []

    operation = bytesio.read(1)
    while operation != b"\xFF":
        if operation == b"\xFD":
            block = []
        elif operation == b"\xFE":
            lexed.append(block)
        elif operation == b"\x00":
            int_bytes = bytesio.read(4)
            block.append(int.from_bytes(int_bytes, "little", signed=False))
        elif operation == b"\x01":
            str_length = bytesio.read(4)
            str_length = int.from_bytes(str_length, "little", signed=False)
            string = bytesio.read(str_length).decode()
            block.append(string)
        elif operation == b"\x02":
            suboperation = bytesio.read(1)
            sublexed = []
            while suboperation != "\x03":
                if suboperation == b"\xFD":
                    subblock = []
                elif suboperation == b"\xFE":
                    sublexed.append(subblock)
                elif suboperation == b"\x00":
                    int_bytes = bytesio.read(4)
                    subblock.append(int.from_bytes(int_bytes, "little", signed=False))
                elif suboperation == b"\x01":
                    str_length = bytesio.read(4)
                    str_length = int.from_bytes(str_length, "little", signed=False)
                    string = bytesio.read(str_length).decode()
                    subblock.append(string)
                elif suboperation == b"\x03":
                    break
                elif suboperation == b"\x02":
                    print(f"ERROR: bytecode-decoding failure: code element in code element is unsupported")
                    exit(1)
                else:
                    print(f"ERROR: bytecode-decoding failure: invalid subtoken {suboperation}")

                suboperation = bytesio.read(1)
            block.append(sublexed)
        else:
            print(f"ERROR: bytecode-decoding failure: invalid token {operation}")

        operation = bytesio.read(1)

    return lexed

def delex(lexed):
    code = ""
    assert len(operations) == 39, "some ops unimplemented (delex)"
    for i in lexed:
        if i[0] == OP_INTPUSH:
            code += i[1]
        elif i[0] == OP_STRINGPUSH:
            code += '"' + codecs.escape_encode(i[1].encode())[0].decode() + '"'
        elif i[0] == OP_MEMWRITE:
            code += "write"
        elif i[0] == OP_MEMREAD:
            code += "read"
        elif i[0] == OP_EXIT:
            code += "exit"
        elif i[0] == OP_SLEEP:
            code += "sleep"
        elif i[0] == OP_PLUS:
            code += "+"
        elif i[0] == OP_MINUS:
            code += "-"
        elif i[0] == OP_MULT:
            code += "*"
        elif i[0] == OP_DIVMOD:
            code += "divmod"
        elif i[0] == OP_POW:
            code += "pow"
        elif i[0] == OP_INPUT:
            code += ","
        elif i[0] == OP_DUMP:
            code += "."
        elif i[0] == OP_INTIFY:
            code += "int"
        elif i[0] == OP_STRINGIFY:
            code += "str"
        elif i[0] == OP_LENGTH:
            code += "len"
        elif i[0] == OP_DUPLICATE:
            code += "dup"
        elif i[0] == OP_OVER:
            code += "over"
        elif i[0] == OP_SWAP:
            code += "swap"
        elif i[0] == OP_ROT:
            code += "rot"
        elif i[0] == OP_INCLUDE:
            code += "include"
        elif i[0] == OP_DROP:
            code += "drop"
        elif i[0] == OP_PROC:
            code += f"proc {i[1]}"
        elif i[0] == OP_EQUALS:
            code += "="
        elif i[0] == OP_NOT:
            code += "not"
        elif i[0] == OP_OR:
            code += "or"
        elif i[0] == OP_AND:
            code += "and"
        elif i[0] == OP_BOR:
            code += "|"
        elif i[0] == OP_BAND:
            code += "&"
        elif i[0] == OP_RSHIFT:
            code += ">>"
        elif i[0] == OP_LSHIFT:
            code += "<<"
        elif i[0] == OP_LTOE:
            code += "<="
        elif i[0] == OP_GTOE:
            code += ">="
        elif i[0] == OP_LT:
            code += "<"
        elif i[0] == OP_GT:
            code += ">"
        elif i[0] == OP_IF:
            code += "if"
        elif i[0] == OP_ELSE:
            code += "else"
        elif i[0] == OP_WHILE:
            code += f"while {delex(i[1])} do"
        elif i[0] == OP_END:
            code += "end"
        else:
            print(f"ERROR: delexing: unimplemented operation: <{operations[i[0]]}> (id: {i[0]})")
            exit()

        code += " "

    return code

def lex(file_):
    n = 0
    buffers = []
    new_file = ""

    while n < len(file_):
        if file_[n] == '"':
            buf = '"'
            n += 1
            while True:
                if n > 0:
                    if file_[n] == '"' and file_[n - 1] != "\\":
                        break
                else:
                    if file_[n] == '"':
                        break
                buf += file_[n]
                n += 1
            buf += '"'
            if "\n" in buf:
                print("ERROR: unexpected newline in string")
                exit()
            buf = ast.literal_eval(buf)
            buffers.append(buf)
        new_file += file_[n]
        n += 1

    new_file = "\n".join([i.split("//")[0] for i in new_file.split("\n")])
    new_file = new_file.split()

    assert len(operations) == 39, "some ops unimplemented (lex)"
    cursor = 0
    while cursor < len(new_file):
        if new_file[cursor] == '"':
            yield push_str(buffers.pop(0))
            
        elif new_file[cursor] == 'read':
            yield memory_read()

        elif new_file[cursor] == 'write':
            yield memory_write()

        elif new_file[cursor] == 'exit':
            yield exit_()

        elif new_file[cursor] == 'sleep':
            yield sleep()
            
        elif new_file[cursor] == "+":
            yield plus()
            
        elif new_file[cursor] == "-":
            yield minus()
            
        elif new_file[cursor] == "*":
            yield mult()
            
        elif new_file[cursor] == "divmod":
            yield dividemod()
            
        elif new_file[cursor] == "^":
            yield powerof()
            
        elif new_file[cursor] == ",":
            yield input_()
            
        elif new_file[cursor] == ".":
            yield dump()
            
        elif new_file[cursor] == "str":
            yield stringify()

        elif new_file[cursor] == "int":
            yield intify()

        elif new_file[cursor] == "len":
            yield length()
            
        elif new_file[cursor] == "dup":
            yield duplicate()
            
        elif new_file[cursor] == "over":
            yield over()

        elif new_file[cursor] == "swap":
            yield swap()

        elif new_file[cursor] == "rot":
            yield rot()

        elif new_file[cursor] == "include":
            yield include()
            
        elif new_file[cursor] == "drop":
            yield drop()
        
        elif new_file[cursor] == "proc":
            cursor += 1
            yield procedure(new_file[cursor])

        elif new_file[cursor] == "=":
            yield equals()

        elif new_file[cursor] == "not":
            yield not_()

        elif new_file[cursor] == "or":
            yield or_()

        elif new_file[cursor] == "and":
            yield and_()

        elif new_file[cursor] == "|":
            yield bitwise_or()

        elif new_file[cursor] == "&":
            yield bitwise_and()

        elif new_file[cursor] == ">>":
            yield bitwise_shift_right()

        elif new_file[cursor] == "<<":
            yield bitwise_shift_left()
            
        elif new_file[cursor] == ">":
            yield greaterthan()
            
        elif new_file[cursor] == "<":
            yield lesserthan()
            
        elif new_file[cursor] == ">=":
            yield greaterthan_or_equeal()
            
        elif new_file[cursor] == "<=":
            yield lesserthan_or_equeal()
            
        elif new_file[cursor] == "if":
            yield if_start()
            
        elif new_file[cursor] == "else":
            yield if_else()
            
        elif new_file[cursor] == "while":
            do = find_next(new_file, cursor, lambda x: x == "do")
            if do == -1:
                print("ERROR: do expected, but not found")
                exit(1)
            cursor += 1
            condition = lex(" ".join(new_file[cursor:do]))
            yield while_start(list(condition))
            cursor = do

        elif new_file[cursor] == "end":
            yield end()
            
        else:
            yield push_int(new_file[cursor])
            
        cursor += 1

def find_file(folders, file_name):
    for i in folders:
        if file_name in os.listdir(i):
            return os.path.abspath(i) + "/" + file_name
    print(f"ERROR: can't find \"{file_name}\" in include paths. add them by \"-I path\" argument")

def check_stack_length(stack, length):
    if len(stack) < length:
        print(f"ERROR: expected {length} element(s) on the stack, but got {len(stack)}")
        exit(1)

stack = []  # THE stack. LEGEND VARIABLE!

memory = bytearray(64 * 1024) # 64 kb of memory

procedures = {}

n = 0

debug = "--debug" in sys.argv

def crossreference_ends(program):
    stack = []

    for k, i in enumerate(program):
        if i[0] == OP_IF:
            stack.append((i[0], k))
        elif i[0] == OP_WHILE or i[0] == OP_PROC:
            stack.append((i[0], i[1], k))
        elif i[0] == OP_END:
            start = stack.pop()
            if len(start) == 3:  # procedure || while
                program[start[2]] = (start[0], start[1], k)
            else:
                program[start[1]] = (start[0], k)

    if not len(stack) == 0:
        print("ERROR: some blocks arent closed")
        exit(1)

    return program

def interpret(program):
    global stack, n
    cursor = 0

    program = crossreference_ends(program)

    if debug:
        print(f"[DEBUG] Program: {program}")
    
    while cursor < len(program):
        n += 1
        if debug:
            print("[DEBUG] Step")
            print(f"[DEBUG] Step: {n}")
            print(f"[DEBUG] Stack: <{', '.join(map(repr, stack))}>")
            print(f"[DEBUG] Current: [<{'>, <'.join([operations[i] if k == 0 else repr(i) for k, i in enumerate(program[cursor])])}>]")
            print(f"[DEBUG] Cursor: {cursor}")
            
            
        if program[cursor][0] == OP_INTPUSH:
            if not isint(program[cursor][1]) and not program[cursor][1] in procedures.keys():
                print(f"ERROR: no operation or procedure \"{program[cursor][1]}\"")
                exit(1)
            
            if program[cursor][1] in procedures.keys():
                interpret(procedures[program[cursor][1]])
            else:
                base = 10
                if program[cursor][1].startswith("0b"): base = 2
                if program[cursor][1].startswith("0x"): base = 16
                stack.append(int(program[cursor][1], base=base))
        
        if program[cursor][0] == OP_STRINGPUSH:
            stack.append(program[cursor][1])
        
        if program[cursor][0] == OP_MEMREAD:
            check_stack_length(stack, 1)
            addr = stack.pop()
            if not isinstance(addr, int):
                print("ERROR: memory address should be int")
                exit(1)
            if not 0 <= addr < 65536:
                print("ERROR: memory address is not beetween zero and 65535")
                exit(1)
            
            stack.append(memory[addr])
        
        if program[cursor][0] == OP_MEMWRITE:
            check_stack_length(stack, 2)
            addr = stack.pop()
            data = stack.pop()
            if not isinstance(addr, int):
                print("ERROR: memory address should be int")
                exit(1)
            if not isinstance(data, int):
                print("ERROR: data to write to memory should be int")
                exit(1)
            if not 0 <= addr < 65536:
                print("ERROR: memory address is not beetween zero and 65535")
                exit(1)
            if not 0 <= data < 256:
                print("ERROR: data is not beetween zero and 255")
                exit(1)
            
            memory[addr] = data

        if program[cursor][0] == OP_EXIT:
            check_stack_length(stack, 1)
            a = stack.pop()
            if not isinstance(a, int):
                print("ERROR: exit code should be integer")
                exit(1)

            exit(a)

        if program[cursor][0] == OP_SLEEP:
            check_stack_length(stack, 1)
            a = stack.pop()
            if not isinstance(a, int):
                print("ERROR: sleep amount should be integer")
                exit(1)

            time.sleep(a)

        if program[cursor][0] == OP_PLUS:
            check_stack_length(stack, 2)
            a, b = stack.pop(), stack.pop()
            if type(a) != type(b):
                print("ERROR: type of a does not match type of b")
                exit(1)
            stack.append(a + b)
        
        if program[cursor][0] == OP_MINUS:
            check_stack_length(stack, 2)
            a, b = stack.pop(), stack.pop()
            if not (isinstance(a, int) and isinstance(b, int)):
                print("ERROR: can not substract non-integer values")
                exit(1)
            stack.append(a - b)
        
        if program[cursor][0] == OP_MULT:
            check_stack_length(stack, 2)
            a, b = stack.pop(), stack.pop()
            if not (isinstance(a, int) and isinstance(b, int)):
                print("ERROR: can not multiply non-integer values")
                exit(1)
            stack.append(a * b)
        
        if program[cursor][0] == OP_DIVMOD:
            check_stack_length(stack, 2)
            a, b = stack.pop(), stack.pop()
            if not (isinstance(a, int) and isinstance(b, int)):
                print("ERROR: can not divmod non-integer values")
                exit(1)
            stack.append(a // b)
            stack.append(a % b)
        
        if program[cursor][0] == OP_POW:
            check_stack_length(stack, 2)
            a, b = stack.pop(), stack.pop()
            if not (isinstance(a, int) and isinstance(b, int)):
                print("ERROR: can not pow non-integer values")
                exit(1)
            stack.append(a ** b)
        
        if program[cursor][0] == OP_INPUT:
            stack.append(input())
        
        if program[cursor][0] == OP_DUMP:
            check_stack_length(stack, 1)
            a = stack.pop()
            if isinstance(a, str):
                print(a, end="")
            if isinstance(a, int):
                print(a)
        
        if program[cursor][0] == OP_STRINGIFY:
            check_stack_length(stack, 1)
            stack.append(str(stack.pop()))

        if program[cursor][0] == OP_INTIFY:
            check_stack_length(stack, 1)
            stack.append(int(stack.pop()))

        if program[cursor][0] == OP_LENGTH:
            check_stack_length(stack, 1)
            a = stack.pop()
            if not isinstance(a, str):
                print("ERROR: can not use len on non-str object")
                exit(1)
            stack.append(len(1))
        
        if program[cursor][0] == OP_DUPLICATE:
            check_stack_length(stack, 1)
            a = stack[-1]
            stack.append(a)
        
        if program[cursor][0] == OP_OVER:
            check_stack_length(stack, 2)
            a = stack[-2]
            stack.append(a)

        if program[cursor][0] == OP_SWAP:
            check_stack_length(stack, 2)
            a, b = stack.pop(), stack.pop()
            stack.append(a)
            stack.append(b)

        if program[cursor][0] == OP_ROT:
            check_stack_length(stack, 2)
            a, b, c = stack.pop(), stack.pop(), stack.pop()
            stack.append(a)
            stack.append(c)
            stack.append(b)
        
        if program[cursor][0] == OP_INCLUDE:
            check_stack_length(stack, 1)
            a = stack.pop()
            b = find_file(include_paths, a)
            interpret(list(lex(open(b).read())))
        
        if program[cursor][0] == OP_DROP:
            check_stack_length(stack, 1)
            stack.pop()
        
        if program[cursor][0] == OP_PROC:
            proc_body = program[cursor + 1:program[cursor][2]]
            if debug:
                print(f"[DEBUG] ProcedureDefine: \"{program[cursor][1]}\": <{proc_body}>")
            if program[cursor][1] in procedures.keys():
                print(f"ERROR: procedure {program[cursor][1]} already exists")
                exit(1)
            procedures[program[cursor][1]] = proc_body
            cursor = program[cursor][2]

        if program[cursor][0] == OP_EQUALS:
            check_stack_length(stack, 2)
            a, b = stack.pop(), stack.pop()
            stack.append(int(a == b))

        if program[cursor][0] == OP_NOT:
            check_stack_length(stack, 1)
            a = stack.pop()
            stack.append(int(not a))

        if program[cursor][0] == OP_OR:
            check_stack_length(stack, 2)
            a, b = stack.pop(), stack.pop()
            stack.append(a or b)

        if program[cursor][0] == OP_AND:
            check_stack_length(stack, 2)
            a, b = stack.pop(), stack.pop()
            stack.append(a and b)

        if program[cursor][0] == OP_BOR:
            check_stack_length(stack, 2)
            a, b = stack.pop(), stack.pop()
            stack.append(a | b)

        if program[cursor][0] == OP_BAND:
            check_stack_length(stack, 2)
            a, b = stack.pop(), stack.pop()
            stack.append(a & b)

        if program[cursor][0] == OP_RSHIFT:
            check_stack_length(stack, 2)
            a, b = stack.pop(), stack.pop()
            stack.append(a >> b)

        if program[cursor][0] == OP_LSHIFT:
            check_stack_length(stack, 2)
            a, b = stack.pop(), stack.pop()
            stack.append(a << b)
        
        if program[cursor][0] == OP_GTOE:
            check_stack_length(stack, 2)
            a, b = stack.pop(), stack.pop()
            stack.append(int(a >= b))
        
        if program[cursor][0] == OP_LTOE:
            check_stack_length(stack, 2)
            a, b = stack.pop(), stack.pop()
            stack.append(int(a <= b))
        
        if program[cursor][0] == OP_GT:
            check_stack_length(stack, 2)
            a, b = stack.pop(), stack.pop()
            stack.append(int(a > b))
        
        if program[cursor][0] == OP_LT:
            check_stack_length(stack, 2)
            a, b = stack.pop(), stack.pop()
            stack.append(int(a < b))
        
        if program[cursor][0] == OP_IF:
            check_stack_length(stack, 1)
            end = program[cursor][1]
            if_value = stack.pop()
            elseif = find_next(program, cursor, lambda x: x[0] == OP_ELSE)
            if elseif == -1 or elseif > end:
                if not if_value:
                    cursor = end
            else:
                if if_value:
                    interpret(program[cursor + 1:elseif])
                    cursor = end
                else:
                    cursor = elseif
        
        if program[cursor][0] == OP_WHILE:
            end = program[cursor][2]
            condition = program[cursor][1]
            check_stack_length(stack, 1)
            interpret(condition)
            while stack.pop():
                interpret(program[cursor + 1:end])
                check_stack_length(stack, 1)
                interpret(condition)
            cursor = end
        
        cursor += 1

def repl():
    print(f"BlankLang, version {ver}")
    print(f"REPL mode. type \".exit\" or ctrl-c to exit")
    try:
        while True:
            expr = input(">>> ")
            if expr == ".exit": exit(0)
            interpret(list(lex(expr)))
    except KeyboardInterrupt:
        exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        repl()
        exit(0)
    
    if not os.path.isfile(sys.argv[1]):
        print("ERROR: file does not exist")
        exit(1)

    if "--encode" in sys.argv:
        encode_bytecode(list(lex(open(sys.argv[1]).read())), open(f"{os.getcwd()}/{sys.argv[1].split('/')[-1].split('.')[0]}.bc", "wb"))
    elif "--decode" in sys.argv:
        interpret(decode_bytecode(open(sys.argv[1], "rb")))
    elif "--decompile" in sys.argv:
        print(delex(decode_bytecode(open(sys.argv[1], "rb"))))
        open(sys.argv[1].split(".")[0] + ".bl", "w").write(delex(decode_bytecode(open(sys.argv[1], "rb"))))
    else:
        interpret(list(lex(open(sys.argv[1]).read())))
    
