import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import LexerError
from parser import ParserError
from semantic import SemanticError
from intermediate import generate_source
from optimizer import optimize


ARCHITECTURE_NOTE = (
    "Arquitectura educativa MiniCPU (ficticia). "
    "No es ensamblador real de x86 ni de ARM. "
    "Registros: R0, R1, R2. "
    "R0 = operando izquierdo y resultado; "
    "R1 = operando derecho; "
    "R2 = auxiliar."
)

OPERATORS = {
    "+": "ADD",
    "-": "SUB",
    "*": "MUL",
    "/": "DIV",
}


class AssemblyProgram:
    def __init__(self, lines):
        self.lines = lines
        self.architecture = ARCHITECTURE_NOTE

    def __str__(self):
        header = [f"; {ARCHITECTURE_NOTE}", ""]
        if not self.lines:
            return "\n".join(header + ["(sin instrucciones)"])
        return "\n".join(header + self.lines)

    def to_lines(self):
        return list(self.lines)


class CodeGenerator:
    def generate(self, intermediate_code):
        lines = []
        for instruction in intermediate_code.instructions:
            lines.append(f"; {instruction}")
            if instruction.operator is None:
                lines.extend(self._move(instruction.destination, instruction.arg1))
            else:
                lines.extend(self._binary(instruction))
            lines.append("")
        if lines and lines[-1] == "":
            lines.pop()
        return AssemblyProgram(lines)

    def _move(self, destination, source):
        return [
            f"MOV R0, {source}",
            f"MOV {destination}, R0",
        ]

    def _binary(self, instruction):
        asm_op = OPERATORS[instruction.operator]
        return [
            f"MOV R0, {instruction.arg1}",
            f"MOV R1, {instruction.arg2}",
            f"{asm_op} R0, R1",
            f"MOV {instruction.destination}, R0",
        ]


def generate(intermediate_code):
    return CodeGenerator().generate(intermediate_code)


def generate_assembly_from_source(source):
    intermediate_code = generate_source(source)
    optimized = optimize(intermediate_code)
    return generate(optimized.after), optimized


if __name__ == "__main__":
    ejemplo = "a = 10\nb = 5\nresultado = (a + b) * 2"
    print("Código fuente:")
    print(ejemplo)
    print()
    try:
        intermedio = generate_source(ejemplo)
        print("Ensamblador desde código intermedio (sin optimizar):")
        print()
        print(generate(intermedio))
        print()
        print("-" * 50)
        print()
        ensamblador, _optimizado = generate_assembly_from_source(ejemplo)
        print("Ensamblador desde código ya optimizado:")
        print()
        print(ensamblador)
    except (LexerError, ParserError, SemanticError) as error:
        print(error)
