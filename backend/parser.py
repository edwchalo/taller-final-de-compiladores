import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import tokenize, LexerError


class ParserError(Exception):
    def __init__(self, message, line=None, column=None):
        self.phase = "sintáctico"
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.full_message())

    def full_message(self):
        if self.line is not None and self.column is not None:
            return (
                f"ERROR SINTÁCTICO: {self.message} "
                f"(línea {self.line}, posición {self.column})"
            )
        return f"ERROR SINTÁCTICO: {self.message}"


class Program:
    def __init__(self, assignments):
        self.assignments = assignments

    def __str__(self):
        if not self.assignments:
            return "(programa vacío)"
        return "\n".join(str(assignment) for assignment in self.assignments)


class Assignment:
    def __init__(self, name, expression, line, column):
        self.name = name
        self.expression = expression
        self.line = line
        self.column = column

    def __str__(self):
        return f"{self.name} = {self.expression}"


class BinaryOp:
    def __init__(self, operator, left, right, line, column):
        self.operator = operator
        self.left = left
        self.right = right
        self.line = line
        self.column = column

    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"


class Number:
    def __init__(self, value, line, column):
        self.value = value
        self.line = line
        self.column = column

    def __str__(self):
        return self.value


class Identifier:
    def __init__(self, name, line, column):
        self.name = name
        self.line = line
        self.column = column

    def __str__(self):
        return self.name


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def parse(self):
        assignments = []
        while not self._is_at_end():
            assignments.append(self._assignment())
        return Program(assignments)

    def _assignment(self):
        identifier = self._consume(
            "IDENTIFICADOR",
            "se esperaba un identificador al inicio de una asignación",
        )
        self._consume("ASIGNACION", "se esperaba '=' después del identificador")
        expression = self._expression()
        return Assignment(
            identifier.value,
            expression,
            identifier.line,
            identifier.column,
        )

    def _expression(self):
        node = self._term()
        while self._check("SUMA") or self._check("RESTA"):
            operator_token = self._advance()
            right = self._term()
            node = BinaryOp(
                operator_token.value,
                node,
                right,
                operator_token.line,
                operator_token.column,
            )
        return node

    def _term(self):
        node = self._factor()
        while self._check("MULTIPLICACION") or self._check("DIVISION"):
            operator_token = self._advance()
            right = self._factor()
            node = BinaryOp(
                operator_token.value,
                node,
                right,
                operator_token.line,
                operator_token.column,
            )
        return node

    def _factor(self):
        if self._check("NUMERO"):
            token = self._advance()
            return Number(token.value, token.line, token.column)

        if self._check("IDENTIFICADOR"):
            token = self._advance()
            return Identifier(token.value, token.line, token.column)

        if self._check("PARENTESIS_IZQ"):
            self._advance()
            expression = self._expression()
            self._consume("PARENTESIS_DER", "se esperaba ')' para cerrar el paréntesis")
            return expression

        raise ParserError(
            "se esperaba un número, un identificador o '('",
            self._error_line(),
            self._error_column(),
        )

    def _consume(self, token_type, message):
        if self._check(token_type):
            return self._advance()
        raise ParserError(message, self._error_line(), self._error_column())

    def _check(self, token_type):
        if self._is_at_end():
            return False
        return self._current().type == token_type

    def _current(self):
        return self.tokens[self.position]

    def _advance(self):
        token = self._current()
        self.position += 1
        return token

    def _is_at_end(self):
        return self.position >= len(self.tokens)

    def _error_line(self):
        if self.tokens:
            if self._is_at_end():
                return self.tokens[-1].line
            return self._current().line
        return 1

    def _error_column(self):
        if self.tokens:
            if self._is_at_end():
                last = self.tokens[-1]
                return last.column + len(str(last.value))
            return self._current().column
        return 1


def parse(tokens):
    return Parser(tokens).parse()


def parse_source(source):
    return parse(tokenize(source))


if __name__ == "__main__":
    ejemplos = [
        "x = 10\ny = 20\nresultado = x + y\ntotal = (x + y) * 2",
        "x = 10 +",
    ]

    for ejemplo in ejemplos:
        print("=" * 50)
        print("Código fuente:")
        print(ejemplo)
        print()
        try:
            arbol = parse_source(ejemplo)
            print("Análisis sintáctico: correcto")
            print("Árbol:")
            print(arbol)
        except (LexerError, ParserError) as error:
            print(error)
        print()
