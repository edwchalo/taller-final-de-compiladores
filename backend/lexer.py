class LexerError(Exception):
    def __init__(self, message, line, column):
        self.phase = "léxico"
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.full_message())

    def full_message(self):
        return (
            f"ERROR LÉXICO: {self.message} "
            f"(línea {self.line}, posición {self.column})"
        )


class Token:
    def __init__(self, type_, value, line, column):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def to_dict(self):
        return {
            "type": self.type,
            "value": self.value,
            "line": self.line,
            "column": self.column,
        }

    def __repr__(self):
        return f"{self.type} → {self.value}"


SINGLE_CHAR_TOKENS = {
    "=": "ASIGNACION",
    "+": "SUMA",
    "-": "RESTA",
    "*": "MULTIPLICACION",
    "/": "DIVISION",
    "(": "PARENTESIS_IZQ",
    ")": "PARENTESIS_DER",
}


class Lexer:
    def __init__(self, source):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1

    def tokenize(self):
        tokens = []

        while not self._is_at_end():
            self._skip_whitespace()
            if self._is_at_end():
                break

            char = self._current()
            start_line = self.line
            start_column = self.column

            if char.isalpha() or char == "_":
                tokens.append(self._read_identifier(start_line, start_column))
            elif char.isdigit():
                tokens.append(self._read_number(start_line, start_column))
            elif char in SINGLE_CHAR_TOKENS:
                self._advance()
                tokens.append(
                    Token(SINGLE_CHAR_TOKENS[char], char, start_line, start_column)
                )
            else:
                raise LexerError(
                    f"carácter no permitido '{char}'",
                    start_line,
                    start_column,
                )

        return tokens

    def _read_identifier(self, line, column):
        start = self.position
        while not self._is_at_end() and (self._current().isalnum() or self._current() == "_"):
            self._advance()
        value = self.source[start:self.position]
        return Token("IDENTIFICADOR", value, line, column)

    def _read_number(self, line, column):
        start = self.position

        while not self._is_at_end() and self._current().isdigit():
            self._advance()

        if not self._is_at_end() and self._current() == ".":
            self._advance()
            if self._is_at_end() or not self._current().isdigit():
                raise LexerError(
                    "número decimal incompleto: se esperaba un dígito después del punto",
                    line,
                    column,
                )
            while not self._is_at_end() and self._current().isdigit():
                self._advance()

        value = self.source[start:self.position]
        return Token("NUMERO", value, line, column)

    def _skip_whitespace(self):
        while not self._is_at_end() and self._current() in " \t\r\n":
            self._advance()

    def _current(self):
        return self.source[self.position]

    def _advance(self):
        char = self.source[self.position]
        self.position += 1
        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def _is_at_end(self):
        return self.position >= len(self.source)


def tokenize(source):
    return Lexer(source).tokenize()


if __name__ == "__main__":
    ejemplo = "resultado = (a + b) * 2"
    print("Código fuente:")
    print(ejemplo)
    print()
    print("Tokens:")
    for token in tokenize(ejemplo):
        print(token)
