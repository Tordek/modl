import sys
import codecs
import traceback

import modl_parser
import modl_scanner
import modl_interpreter

# WHY GLOBALS?!
hadError = False

def main(args):
    if len(args) > 2:
        print("Usage: {} [script]".format(sys.args[0]), file=sys.stderr)
        exit(-1)
    elif len(args) == 2:
        run_file(args[1])
        if hadError:
            exit(65)
    else:
        run_prompt()
        

def run_file(path):
    with codecs.open(path, encoding="utf8") as script:
        run(script.read())
        hadError = False
        

def run_prompt():
    env = modl_interpreter.Environment()
    while True:
        try:
            env = run(input("> "), env)
        except Exception as e:
            print(traceback.format_exc())
            

def run(command, env):
    scanner = modl_scanner.Scanner(command)
    parser = modl_parser.Parser(scanner.scan_tokens())
    interpreter = modl_interpreter.Interpreter()
    result, env = interpreter.interpret(parser.statement(), env)
    print(result)
    return env
    

def error(line, message):
    report(line, "", message)


def report(line, where, message):
    global hadError
    print("[line {}] Error{}: {}".format(line, where, message), file=sys.stderr)
    hadError = True

    
if __name__ == "__main__":
    main(sys.argv)
