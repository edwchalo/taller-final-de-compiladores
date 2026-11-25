import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import LexerError
from parser import BinaryOp, Identifier, Number, ParserError, parse_source
from semantic import SemanticError, analyze


class Instruction:
    def __init__(self, destination, operator, arg1, arg2=None):
        self.destination = destination
        self.operator = operator
        self.arg1 = arg1
        self.arg2 = arg2

    def __str__(self):
        if self.operator is None:
            return f"{self.destination} = {self.arg1}"
        return f"{self.destination} = {self.arg1} {self.operator} {self.arg2}"


class IntermediateCode:
    def __init__(self, instructions):
        self.instructions = instructions

    def __str__(self):
        if not self.instructions:
            return "(sin instrucciones)"
        return "\n".join(str(instruction) for instruction in self.instructions)

    def to_lines(self):
        return [str(instruction) for instruction in self.instructions]


class IntermediateGenerator:
    def __init__(self):
        self.instructions = []
        self.temp_count = 0

    def generate(self, program):
        for assignment in program.assignments:
            self._generate_assignment(assignment)
        return IntermediateCode(self.instructions)

    def _new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def _generate_assignment(self, assignment):
        value = self._generate_expression(assignment.expression)
        self.instructions.append(Instruction(assignment.name, None, value))

    def _generate_expression(self, node):
        if isinstance(node, Number):
            return node.value

        if isinstance(node, Identifier):
            return node.name

        if isinstance(node, BinaryOp):
            left = self._generate_expression(node.left)
            right = self._generate_expression(node.right)
            temp = self._new_temp()
            self.instructions.append(
                Instruction(temp, node.operator, left, right)
            )
            return temp

        raise SemanticError("nodo de expresión no reconocido para código intermedio")


def generate(program):
    return IntermediateGenerator().generate(program)


def generate_source(source):
    program = parse_source(source)
    analyze(program)
    return generate(program)


if __name__ == "__main__":
    ejemplos = [
        "a = 10\nb = 5\nresultado = (a + b) * 2",
        "resultado = a + 5",
    ]

    for ejemplo in ejemplos:
        print("=" * 50)
        print("Código fuente:")
        print(ejemplo)
        print()
        try:
            codigo = generate_source(ejemplo)
            print("Código de tres direcciones:")
            print(codigo)
        except (LexerError, ParserError, SemanticError) as error:
            print(error)
        print()
