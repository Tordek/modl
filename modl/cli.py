import sys
import codecs
import traceback

from .parser import Parser
from .scanner import Scanner
from . import interpreter


def main(args):
    if len(args) > 2:
        print("Usage: {} [script]".format(sys.args[0]), file=sys.stderr)
        exit(-1)
    elif len(args) == 2:
        exit(run_file(args[1]))
    else:
        run_prompt()


def run_file(path):
    with codecs.open(path, encoding="utf8") as script:
        env = interpreter.get_default_env()
        scanner = Scanner(command)
        parser = Parser(scanner.scan_tokens())

        for statement in parser.program():
            (result, env) = interpreter.interpret(statement, env)

        return result


def run_prompt():
    env = interpreter.get_default_env()
    while True:
        try:
            command = input("> ")
            scanner = Scanner(command)
            parser = Parser(scanner.scan_tokens())
            (result, env) = interpreter.interpret(parser.statement(), env)
            print(result)
            hadError = False
        except Exception as e:
            print(traceback.format_exc())


def error(line, message):
    report(line, "", message)


def report(line, where, message):
    global hadError
    print("[line {}] Error{}: {}".format(line, where, message), file=sys.stderr)
    hadError = True


if __name__ == "__main__":
    main(sys.argv)
