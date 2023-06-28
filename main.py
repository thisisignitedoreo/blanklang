import sys
import ast
import os

iota_counter = 0
def iota(reset=0):
    global iota_counter
    iota_counter += 1
    if reset:
        iota_counter = 0
    return iota_counter

OP_INTPUSH = iota(1)
OP_STRINGPUSH = iota()
OP_PLUS = iota()
OP_MINUS = iota()
OP_MULT = iota()
OP_DIVMOD = iota()
OP_INPUT = iota()
OP_DUMP = iota()
OP_STRINGIFY = iota()
OP_INTIFY = iota()
OP_LENGTH = iota()
OP_DUPLICATE = iota()
OP_OVER = iota()
OP_SWAP = iota()
OP_INCLUDE = iota()
OP_DROP = iota()
OP_MACRO = iota()
OP_EQUALS = iota()
OP_NOT = iota()
OP_LTOE = iota()
OP_GTOE = iota()
OP_LT = iota()
OP_GT = iota()
OP_IF = iota()
OP_ELSE = iota()
OP_WHILE = iota()
OP_END = iota()

include_paths = [os.path.abspath("inc"), os.getcwd()]

def push_int(num):
    return (OP_INTPUSH, num)

def push_str(string):
    return (OP_STRINGPUSH, string)

def plus():
    return (OP_PLUS, )

def minus():
    return (OP_MINUS, )

def mult():
    return (OP_MULT, )

def dividemod():
    return (OP_DIVMOD, )

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

def include():
    return (OP_INCLUDE, )

def drop():
    return (OP_DROP, )

def macro_start(name, macro):
    return (OP_MACRO, name, macro)

def equals():
    return (OP_EQUALS, )

def not_():
    return (OP_NOT, )

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

def while_start():
    return (OP_WHILE, )

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

def lex(file_):
    file_ = "\n".join([i.split("//")[0] for i in file_.split("\n")])
    n = 0
    buffers = []
    new_file = ""
    while n < len(file_):
        if file_[n] == '"':
            buf = '"'
            n += 1
            while file_[n] != '"':
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

    new_file = new_file.split()

    cursor = 0
    while cursor < len(new_file):
        if new_file[cursor] == '"':
            yield push_str(buffers.pop(0))
            
        elif new_file[cursor] == "+":
            yield plus()
            
        elif new_file[cursor] == "-":
            yield minus()
            
        elif new_file[cursor] == "*":
            yield mult()
            
        elif new_file[cursor] == "divmod":
            yield dividemod()
            
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
            
        elif new_file[cursor] == "include":
            yield include()
            
        elif new_file[cursor] == "drop":
            yield drop()
        
        elif new_file[cursor] == "macro":
            cursor += 1
            name = new_file[cursor]
            cursor += 1
            end_ = find_next(new_file, cursor, lambda x: x == "end")
            macro = " ".join(new_file[cursor:end_])
            yield macro_start(name, macro)
            cursor = end_

        elif new_file[cursor] == "=":
            yield equals()

        elif new_file[cursor] == "not":
            yield not_()
            
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
            yield while_start()

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

macros = {}

n = 0

debug = "--debug" in sys.argv

def crossreference_ends(program):
    stack = []

    for k, i in enumerate(program):
        if i[0] == OP_IF:
            stack.append((i[0], k))
        elif i[0] == OP_WHILE:
            stack.append((i[0], k))
        elif i[0] == OP_END:
            start = stack.pop()
            program[start[1]] = (start[0], k)

    if not len(stack) == 0:
        print("ERROR: some blocks arent closed")
        exit(1)

    return program

def interpret(program):
    global stack, n
    cursor = 0

    program = crossreference_ends(program)
    
    while cursor < len(program):
        n += 1
        if debug:
            print("[DEBUG] Step")
            print(f"[DEBUG] Step: {n}")
            print(f"[DEBUG] Stack: <{', '.join(map(repr, stack))}>")
            print(f"[DEBUG] Current: [<{'>, <'.join(map(repr, program[cursor]))}>]")
            print(f"[DEBUG] Cursor: {cursor}")
            
            
        if program[cursor][0] == OP_INTPUSH:
            if not isint(program[cursor][1]) and not program[cursor][1] in macros.keys():
                print(program[cursor])
                print(f"ERROR: no operation or macro \"{program[cursor][1]}\"")
                exit(1)
            
            if program[cursor][1] in macros.keys():
                interpret(list(lex(macros[program[cursor][1]])))
            else:
                stack.append(int(program[cursor][1]))
        
        if program[cursor][0] == OP_STRINGPUSH:
            stack.append(program[cursor][1])
        
        if program[cursor][0] == OP_PLUS:
            check_stack_length(stack, 2)
            a, b = stack.pop(), stack.pop()
            stack.append(a + b)
        
        if program[cursor][0] == OP_MINUS:
            check_stack_length(stack, 2)
            a, b = stack.pop(), stack.pop()
            stack.append(a - b)
        
        if program[cursor][0] == OP_MULT:
            check_stack_length(stack, 2)
            a, b = stack.pop(), stack.pop()
            stack.append(a * b)
        
        if program[cursor][0] == OP_DIVMOD:
            check_stack_length(stack, 2)
            a, b = stack.pop(), stack.pop()
            stack.append(b // a)
            stack.append(b % a)
        
        if program[cursor][0] == OP_INPUT:
            stack.pop(input())
        
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
        
        if program[cursor][0] == OP_INCLUDE:
            check_stack_length(stack, 1)
            a = stack.pop()
            b = find_file(include_paths, a)
            interpret(list(lex(open(b).read())))
        
        if program[cursor][0] == OP_DROP:
            check_stack_length(stack, 1)
            stack.pop()
        
        if program[cursor][0] == OP_MACRO:
            if debug:
                print(f"[DEBUG] MacroDefine: \"{program[cursor][1]}\": <{program[cursor][2]}>")
            macros[program[cursor][1]] = program[cursor][2]

        if program[cursor][0] == OP_EQUALS:
            check_stack_length(stack, 2)
            a, b = stack.pop(), stack.pop()
            stack.append(int(a == b))

        if program[cursor][0] == OP_NOT:
            check_stack_length(stack, 1)
            a = stack.pop()
            stack.append(int(not a))
        
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
            end = program[cursor][1]
            check_stack_length(stack, 1)
            while_value = stack.pop()
            while while_value:
                interpret(program[cursor + 1:end])
                check_stack_length(stack, 1)
                while_value = stack.pop()
            cursor = end
        
        cursor += 1

# 123
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ERROR: no file specified")
        exit(1)
    
    if not os.path.isfile(sys.argv[1]):
        print("ERROR: file does not exist")
        exit(1)
        
    interpret(list(lex(open(sys.argv[1]).read())))
    
