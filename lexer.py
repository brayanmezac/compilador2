from typing import List, Dict, Set
from m_token import Token, TokenType, CompilerError, ErrorType
class Lexer:
    def __init__(self):
        self.keywords = {
            'if', 'else', 'while', 'for', 'int', 'float', 'string', 
            'boolean', 'print', 'input', 'return', 'void', 'class',
            'public', 'private', 'true', 'false', 'break', 'continue'
        }
        self.operators = {
            '+', '-', '*', '/', '=', '==', '<', '>', '<=', '>=', 
            '!=', '&&', '||', '!', '++', '--', '+=', '-=', '*=', '/='
        }
        self.delimiters = {'{', '}', '(', ')', ';', ',', '[', ']', '.'}
        self.boolean_literals = {'true', 'false'}
        # Lexer para [NEW]
        self.arroba = {'@'}

    def tokenize(self, code: str) -> List[Token]:
        tokens = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            position = 0
            while position < len(line):
                char = line[position]
                
                # Ignorar espacios en blanco
                if char.isspace():
                    position += 1
                    continue
                
                # Procesar booleanos
                if position + 4 <= len(line) and line[position:position+4] == 'true':
                    tokens.append(Token(TokenType.BOOLEAN, 'true', line_num, position))
                    position += 4
                    continue
                    
                if position + 5 <= len(line) and line[position:position+5] == 'false':
                    tokens.append(Token(TokenType.BOOLEAN, 'false', line_num, position))
                    position += 5
                    continue
                
                # Strings
                if char in '"\'':
                    string, new_pos = self.extract_string(line, position, char, line_num)
                    tokens.append(string)
                    position = new_pos
                    continue
                
                # Comentarios
                if char == '/' and position + 1 < len(line):
                    if line[position + 1] == '/':
                        break  # Ignorar resto de la línea
                    if line[position + 1] == '*':
                        position = self.skip_multiline_comment(lines, line_num, position)
                        continue
                
                # Operadores lógicos
                if char == '&' and position + 1 < len(line) and line[position + 1] == '&':
                    tokens.append(Token(TokenType.OPERATOR, '&&', line_num, position))
                    position += 2
                    continue
                    
                if char == '|' and position + 1 < len(line) and line[position + 1] == '|':
                    tokens.append(Token(TokenType.OPERATOR, '||', line_num, position))
                    position += 2
                    continue
                
                # Números
                if char.isdigit() or (char == '.' and position + 1 < len(line) and line[position + 1].isdigit()):
                    num, new_pos = self.extract_number(line, position, line_num)
                    tokens.append(num)
                    position = new_pos
                    continue
                
                # Identificadores y palabras clave
                if char.isalpha() or char == '_':
                    word, new_pos = self.extract_word(line, position, line_num)
                    tokens.append(word)
                    position = new_pos
                    continue
                
                # Operadores
                if char in self.operators or (char in '<>!' and position + 1 < len(line) and line[position + 1] == '='):
                    op, new_pos = self.extract_operator(line, position, line_num)
                    tokens.append(op)
                    position = new_pos
                    continue
                
                # Delimitadores
                if char in self.delimiters:
                    tokens.append(Token(TokenType.DELIMITER, char, line_num, position))
                    position += 1
                    continue
                
                # tokenizador para [NEW]
                if char in self.arroba:
                    tokens.append(Token(TokenType.ARROBA, char, line_num, position))
                    position += 1
                    continue

                # Caracteres no reconocidos
                raise CompilerError(
                    ErrorType.LEXICAL,
                    f"Carácter no reconocido: {char}",
                    line_num,
                    position,
                    "un carácter válido",
                    char
                )
        
        return tokens
    def extract_string(self, line: str, start: int, quote: str, line_num: int) -> tuple:
        position = start + 1
        string = quote
        while position < len(line):
            char = line[position]
            string += char
            position += 1
            if char == quote and line[position-2] != '\\':
                return Token(TokenType.STRING, string, line_num, start), position
        raise CompilerError(
            ErrorType.LEXICAL,
            "String no cerrado",
            line_num,
            start,
            f"cierre de string con {quote}",
            "fin de línea"
        )

    def extract_number(self, line: str, start: int, line_num: int) -> tuple:
        position = start
        num = ''
        dots = 0
        while position < len(line) and (line[position].isdigit() or line[position] == '.'):
            if line[position] == '.':
                dots += 1
                if dots > 1:
                    raise CompilerError(
                        ErrorType.LEXICAL,
                        "Número mal formado: múltiples puntos decimales",
                        line_num,
                        start,
                        "un único punto decimal",
                        f"número con {dots} puntos"
                    )
            num += line[position]
            position += 1
        return Token(TokenType.NUMBER, num, line_num, start), position

    def extract_word(self, line: str, start: int, line_num: int) -> tuple:
        position = start
        word = ''
        while position < len(line) and (line[position].isalnum() or line[position] == '_'):
            word += line[position]
            position += 1
        token_type = TokenType.KEYWORD if word in self.keywords else TokenType.IDENTIFIER
        return Token(token_type, word, line_num, start), position

    def extract_operator(self, line: str, start: int, line_num: int) -> tuple:
        position = start
        op = line[position]
        position += 1
        if position < len(line):
            possible_op = op + line[position]
            if possible_op in self.operators:
                op = possible_op
                position += 1
        return Token(TokenType.OPERATOR, op, line_num, start), position
