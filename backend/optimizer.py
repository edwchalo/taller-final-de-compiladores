import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import LexerError
from parser import ParserError
from semantic import SemanticError
from intermediate import Instruction, IntermediateCode, generate_source


def _is_number(value):
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def _format_number(value):
    number = float(value)
    if number.is_integer():
        return str(int(number))
    return str(number)


def _copy_instruction(instruction):
    return Instruction(
        instruction.destination,
        instruction.operator,
        instruction.arg1,
        instruction.arg2,
    )


class Optimization:
    def __init__(self, technique, before, after):
        self.technique = technique
        self.before = before
        self.after = after

    def __str__(self):
        return f"[{self.technique}] {self.before}  →  {self.after}"


class OptimizationResult:
    def __init__(self, before, after, applied):
        self.before = before
        self.after = after
        self.applied = applied

    def __str__(self):
        lines = [
            "Código antes de optimizar:",
            str(self.before),
            "",
            "Código después de optimizar:",
            str(self.after),
        ]
        if self.applied:
            lines.append("")
            lines.append("Optimizaciones aplicadas:")
            for item in self.applied:
                lines.append(f"- {item}")
        else:
            lines.append("")
            lines.append("No se aplicaron optimizaciones.")
        return "\n".join(lines)


class Optimizer:
    def optimize(self, intermediate_code):
        before = IntermediateCode(
            [_copy_instruction(item) for item in intermediate_code.instructions]
        )
        instructions = [
            _copy_instruction(item) for item in intermediate_code.instructions
        ]
        applied = []

        changed = True
        while changed:
            changed = False
            if self._simplify_algebra(instructions, applied):
                changed = True
            if self._fold_constants(instructions, applied):
                changed = True
            if self._propagate_constants(instructions, applied):
                changed = True

        self._eliminate_dead_code(instructions, applied)
        after = IntermediateCode(instructions)
        return OptimizationResult(before, after, applied)

    def _propagate_constants(self, instructions, applied):
        constants = {}
        changed = False

        for instruction in instructions:
            original = str(instruction)

            if instruction.arg1 in constants:
                instruction.arg1 = constants[instruction.arg1]
            if instruction.arg2 is not None and instruction.arg2 in constants:
                instruction.arg2 = constants[instruction.arg2]

            updated = str(instruction)
            if updated != original:
                applied.append(
                    Optimization("Propagación de constantes", original, updated)
                )
                changed = True

            if instruction.operator is None and _is_number(instruction.arg1):
                constants[instruction.destination] = instruction.arg1
            else:
                constants.pop(instruction.destination, None)

        return changed

    def _fold_constants(self, instructions, applied):
        changed = False

        for instruction in instructions:
            if instruction.operator is None:
                continue
            if not (_is_number(instruction.arg1) and _is_number(instruction.arg2)):
                continue
            if instruction.operator == "/" and float(instruction.arg2) == 0:
                continue

            original = str(instruction)
            left = float(instruction.arg1)
            right = float(instruction.arg2)
            if instruction.operator == "+":
                value = left + right
            elif instruction.operator == "-":
                value = left - right
            elif instruction.operator == "*":
                value = left * right
            else:
                value = left / right
            result = _format_number(value)
            instruction.operator = None
            instruction.arg1 = result
            instruction.arg2 = None
            applied.append(
                Optimization("Plegado de constantes", original, str(instruction))
            )
            changed = True

        return changed

    def _simplify_algebra(self, instructions, applied):
        changed = False

        for instruction in instructions:
            if instruction.operator is None:
                continue

            original = str(instruction)
            left = instruction.arg1
            right = instruction.arg2
            operator = instruction.operator
            simplified = None

            if operator == "+" and right == "0":
                simplified = left
            elif operator == "+" and left == "0":
                simplified = right
            elif operator == "-" and right == "0":
                simplified = left
            elif operator == "*" and right == "1":
                simplified = left
            elif operator == "*" and left == "1":
                simplified = right
            elif operator == "*" and (left == "0" or right == "0"):
                simplified = "0"
            elif operator == "/" and right == "1":
                simplified = left

            if simplified is None:
                continue

            instruction.operator = None
            instruction.arg1 = simplified
            instruction.arg2 = None
            applied.append(
                Optimization("Simplificación algebraica", original, str(instruction))
            )
            changed = True

        return changed

    def _eliminate_dead_code(self, instructions, applied):
        live = set()
        kept_reversed = []

        for instruction in reversed(instructions):
            destination = instruction.destination
            is_temp = destination.startswith("t") and destination[1:].isdigit()
            if is_temp and destination not in live:
                applied.append(
                    Optimization(
                        "Eliminación de código muerto",
                        str(instruction),
                        "(eliminada)",
                    )
                )
                continue

            kept_reversed.append(instruction)
            if is_temp:
                live.discard(destination)
            live.add(instruction.arg1)
            if instruction.arg2 is not None:
                live.add(instruction.arg2)

        instructions[:] = list(reversed(kept_reversed))


def optimize(intermediate_code):
    return Optimizer().optimize(intermediate_code)


def optimize_source(source):
    intermediate_code = generate_source(source)
    return optimize(intermediate_code)


if __name__ == "__main__":
    ejemplos = [
        ("Plegado de constantes", "x = 2 + 3"),
        ("Simplificación algebraica", "a = 10\nresultado = a + 0"),
        ("Simplificación algebraica", "a = 10\nresultado = a * 1"),
        (
            "Varias técnicas",
            "a = 10\nb = 5\nresultado = (2 + 3) * 1",
        ),
    ]

    for titulo, ejemplo in ejemplos:
        print("=" * 50)
        print(titulo)
        print("Código fuente:")
        print(ejemplo)
        print()
        try:
            print(optimize_source(ejemplo))
        except (LexerError, ParserError, SemanticError) as error:
            print(error)
        print()
