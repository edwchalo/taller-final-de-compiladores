import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import LexerError
from parser import BinaryOp, Identifier, Number, ParserError, parse_source


class SemanticError(Exception):
    def __init__(self, message, line=None, column=None):
        self.phase = "semántico"
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.full_message())

    def full_message(self):
        if self.line is not None and self.column is not None:
            return (
                f"ERROR SEMÁNTICO: {self.message} "
                f"(línea {self.line}, posición {self.column})"
            )
        return f"ERROR SEMÁNTICO: {self.message}"


class SymbolTable:
    def __init__(self):
        self.symbols = {}

    def declare(self, name, line, column):
        if name not in self.symbols:
            self.symbols[name] = {
                "name": name,
                "line": line,
                "column": column,
            }

    def is_declared(self, name):
        return name in self.symbols

    def to_rows(self):
        return [
            {
                "name": info["name"],
                "declared_at_line": info["line"],
                "declared_at_column": info["column"],
            }
            for info in self.symbols.values()
        ]


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()

    def analyze(self, program):
        for assignment in program.assignments:
            self._analyze_assignment(assignment)
        return self.symbol_table

    def _analyze_assignment(self, assignment):
        self._analyze_expression(assignment.expression)
        self.symbol_table.declare(
            assignment.name,
            assignment.line,
            assignment.column,
        )

    def _analyze_expression(self, node):
        if isinstance(node, Number):
            return

        if isinstance(node, Identifier):
            if not self.symbol_table.is_declared(node.name):
                raise SemanticError(
                    f'variable "{node.name}" no declarada.',
                    node.line,
                    node.column,
                )
            return

        if isinstance(node, BinaryOp):
            self._analyze_expression(node.left)
            self._analyze_expression(node.right)
            return

        raise SemanticError("nodo de expresión no reconocido")


def analyze(program):
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(program)


def analyze_source(source):
    program = parse_source(source)
    return analyze(program)


if __name__ == "__main__":
    ejemplos = [
        "a = 10\nresultado = a + 5",
        "resultado = a + 5",
    ]

    for ejemplo in ejemplos:
        print("=" * 50)
        print("Código fuente:")
        print(ejemplo)
        print()
        try:
            tabla = analyze_source(ejemplo)
            print("Análisis semántico: correcto")
            print("Tabla de símbolos:")
            for fila in tabla.to_rows():
                print(
                    f"  {fila['name']} "
                    f"(declarada en línea {fila['declared_at_line']})"
                )
        except (LexerError, ParserError, SemanticError) as error:
            print(error)
        print()
