from enum import Enum

class TokenType(Enum):
    NUMBER = 'NUMBER'
    IDENTIFIER = 'IDENTIFIER'
    KEYWORD = 'KEYWORD'
    OPERATOR = 'OPERATOR'
    DELIMITER = 'DELIMITER'
    #Token [NEW]
    ARROBA = 'ARROBA'
    ERROR = 'ERROR'
    STRING = 'STRING'
    BOOLEAN = 'BOOLEAN'  # Nuevo tipo para booleanos

class ErrorType(Enum):
    LEXICAL = "Error Léxico"
    SYNTACTIC = "Error Sintáctico"
    SEMANTIC = "Error Semántico"

class Token:
    def __init__(self, type: TokenType, value: str, line: int, position: int):
        self.type = type
        self.value = value
        self.line = line
        self.position = position

    def __str__(self):
        return f"Token({self.type.value}, '{self.value}', línea {self.line}, pos {self.position})"

class CompilerError(Exception):
    def __init__(self, error_type: ErrorType, message: str, line: int, position: int, expected: str = None, received: str = None):
        self.error_type = error_type
        self.message = message
        self.line = line
        self.position = position
        self.expected = expected
        self.received = received

    def __str__(self):
        base_msg = f"{self.error_type.value} en línea {self.line}, posición {self.position}: {self.message}"
        if self.expected and self.received:
            base_msg += f"\nEsperaba: {self.expected}\nRecibió: {self.received}"
        return base_msg

class Variable:
    def __init__(self, name: str, type: str, initialized: bool = False, value=None):
        self.name = name
        self.type = type
        self.initialized = initialized
        self.value = value
        self.used = False