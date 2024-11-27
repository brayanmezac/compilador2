from typing import List, Dict, Set
from m_token import Token, TokenType, Variable, CompilerError, ErrorType
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.scope_stack = [{}]  # Cada elemento es un dict de Variable objects
        self.loop_depth = 0
        self.initialized_vars: Set[str] = set()
    
    def parse_print_statement(self):
        """Analiza una declaración print y sus argumentos"""
        self.advance()  # consume 'print'
        self.expect(TokenType.DELIMITER, '(')
        
        # Guardar el tipo retornado por la expresión
        expr_type = self.parse_expression()
        
        if expr_type is None:
            token = self.current_token()
            raise CompilerError(
                ErrorType.SEMANTIC,
                "Expresión inválida en print",
                token.line,
                token.position
            )
            
        self.expect(TokenType.DELIMITER, ')')
        self.expect(TokenType.DELIMITER, ';')
        
        return expr_type

    

    def get_variable(self, var_name: str) -> Variable:
        """Busca una variable en todos los ámbitos, desde el más interno al más externo"""
        for scope in reversed(self.scope_stack):
            if var_name in scope:
                return scope[var_name]
        return None
    
    ## VERIFICA DECLARACION DOBLE
    def declare_variable(self, name: str, type_: str, initialized: bool = False):
        if name in self.scope_stack[-1]:
            token = self.current_token()
            raise CompilerError(
                ErrorType.SEMANTIC,
                f"Variable '{name}' ya declarada en este ámbito",
                token.line,
                token.position
            )
        self.scope_stack[-1][name] = Variable(name, type_, initialized)

    ## VERIFICA INICIALIZADA LA VARIABLE
    def check_variable_initialization(self, var_name: str):
        var = self.get_variable(var_name)
        if var and not var.initialized:
            token = self.current_token()
            raise CompilerError(
                ErrorType.SEMANTIC,
                f"Variable '{var_name}' utilizada sin inicializar",
                token.line,
                token.position
            )


    def validate_types(self, left_type: str, right_type: str, operator: str):
        # Validación de tipos para operaciones booleanas
        if operator in ['&&', '||']:
            if left_type != 'boolean' or right_type != 'boolean':
                token = self.current_token()
                raise CompilerError(
                    ErrorType.SEMANTIC,
                    f"Operador '{operator}' requiere operandos booleanos",
                    token.line,
                    token.position
                )
            return 'boolean'

        # Validación de tipos para operaciones aritméticas
        if operator in ['+', '-', '*', '/']:
            if left_type == 'string' and right_type == 'string' and operator == '+':
                return 'string'
            if left_type in ['int', 'float'] and right_type in ['int', 'float']:
                return 'float' if 'float' in [left_type, right_type] else 'int'
            token = self.current_token()
            raise CompilerError(
                ErrorType.SEMANTIC,
                f"Operación '{operator}' no válida entre tipos {left_type} y {right_type}",
                token.line,
                token.position
            )

        # Validación de tipos para operaciones de comparación
        if operator in ['>', '<', '>=', '<=', '==', '!=']:
            if left_type == right_type:
                return 'boolean'
            if left_type in ['int', 'float'] and right_type in ['int', 'float']:
                return 'boolean'
            token = self.current_token()
            raise CompilerError(
                ErrorType.SEMANTIC,
                f"Comparación no válida entre tipos {left_type} y {right_type}",
                token.line,
                token.position
            )

        return None


    def parse_expression(self):
        """Analiza una expresión y retorna su tipo"""
        left_type = self.parse_term()
        
        while (self.current < len(self.tokens) and 
               self.current_token().type == TokenType.OPERATOR):
            operator = self.current_token().value
            self.advance()
            
            right_type = self.parse_term()
            
            # Validar que ambos tipos no sean None
            if left_type is None or right_type is None:
                token = self.current_token()
                raise CompilerError(
                    ErrorType.SEMANTIC,
                    f"No se puede realizar la operación '{operator}' con valores indefinidos",
                    token.line,
                    token.position
                )
            
            # Validación de operadores relacionales
            if operator in ['>', '<', '>=', '<=', '==', '!=']:
                if left_type in ['int', 'float'] and right_type in ['int', 'float']:
                    left_type = 'boolean'  # La comparación produce un boolean
                elif left_type == right_type:
                    left_type = 'boolean'
                else:
                    token = self.current_token()
                    raise CompilerError(
                        ErrorType.SEMANTIC,
                        f"Comparación no válida entre tipos {left_type} y {right_type}",
                        token.line,
                        token.position
                    )
            # Operadores aritméticos
            elif operator in ['+', '-', '*', '/']:
                if left_type in ['int', 'float'] and right_type in ['int', 'float']:
                    left_type = 'float' if 'float' in [left_type, right_type] else 'int'
                else:
                    token = self.current_token()
                    raise CompilerError(
                        ErrorType.SEMANTIC,
                        f"Operación '{operator}' no válida entre tipos {left_type} y {right_type}",
                        token.line,
                        token.position
                    )
            # Operadores lógicos
            elif operator in ['&&', '||']:
                if left_type == 'boolean' and right_type == 'boolean':
                    left_type = 'boolean'
                else:
                    token = self.current_token()
                    raise CompilerError(
                        ErrorType.SEMANTIC,
                        f"Operador '{operator}' requiere operandos booleanos",
                        token.line,
                        token.position
                    )
            
        return left_type

    def parse_term(self):
        token = self.current_token()
        
        if token.type == TokenType.IDENTIFIER:
            var = self.get_variable(token.value)
            if var is None:
                raise CompilerError(
                    ErrorType.SEMANTIC,
                    f"Variable '{token.value}' no declarada",
                    token.line,
                    token.position
                )
            self.check_variable_initialization(token.value)
            var.used = True
            self.advance()
            return var.type
            ### VERIFICA EL TIPO
        elif token.type == TokenType.NUMBER:
            self.advance()
            return 'float' if '.' in token.value else 'int'
        
        # Tipo [NEW]
        elif token.type == TokenType.ARROBA:
            self.advance()
            return 'ARROBA'
            
        elif token.type == TokenType.STRING:
            self.advance()
            return 'string'
            
        elif token.type == TokenType.BOOLEAN:
            self.advance()
            return 'boolean'
            
        elif token.value == '(':
            self.advance()
            type_ = self.parse_expression()
            self.expect(TokenType.DELIMITER, ')')
            return type_
            
        raise CompilerError(
            ErrorType.SYNTACTIC,
            "Se esperaba un término válido",
            token.line,
            token.position
        )

    def parse_variable_declaration(self):
        tipo = self.current_token().value
        self.advance()

        if self.current_token().type != TokenType.IDENTIFIER:
            raise CompilerError(
                ErrorType.SYNTACTIC,
                "Se esperaba un identificador",
                self.current_token().line,
                self.current_token().position
            )

        var_name = self.current_token().value
        self.declare_variable(var_name, tipo)
        self.advance()

        initialized = False
        if self.current_token().type == TokenType.OPERATOR and self.current_token().value == '=':
            self.advance()
            value_type = self.parse_expression()
            
            if tipo != value_type and not (tipo in ['float', 'int'] and value_type in ['float', 'int']):
                raise CompilerError(
                    ErrorType.SEMANTIC,
                    f"No se puede asignar valor de tipo {value_type} a variable de tipo {tipo}",
                    self.current_token().line,
                    self.current_token().position
                )
            initialized = True
            self.initialized_vars.add(var_name)
            self.scope_stack[-1][var_name].initialized = True

        self.expect(TokenType.DELIMITER, ';')

    def parse_assignment(self):
        var_name = self.current_token().value
        var = self.get_variable(var_name)
        if var is None:
            raise CompilerError(
                ErrorType.SEMANTIC,
                f"Variable '{var_name}' no declarada",
                self.current_token().line,
                self.current_token().position
            )

        self.advance()
        operator = self.current_token().value
        self.advance()

        if operator in ['+=', '-=', '*=', '/=']:
            self.check_variable_initialization(var_name)
            value_type = self.parse_expression()
            if var.type not in ['int', 'float'] or value_type not in ['int', 'float']:
                raise CompilerError(
                    ErrorType.SEMANTIC,
                    f"Operador {operator} solo válido para tipos numéricos",
                    self.current_token().line,
                    self.current_token().position
                )
        else:
            value_type = self.parse_expression()
            if var.type != value_type and not (var.type in ['float', 'int'] and value_type in ['float', 'int']):
                raise CompilerError(
                    ErrorType.SEMANTIC,
                    f"No se puede asignar valor de tipo {value_type} a variable de tipo {var.type}",
                    self.current_token().line,
                    self.current_token().position
                )

        var.initialized = True
        self.initialized_vars.add(var_name)
        self.expect(TokenType.DELIMITER, ';')

    def parse_if_statement(self):
        """Analiza una estructura if con validación de tipo booleano"""
        self.advance()  # consume 'if'
        self.expect(TokenType.DELIMITER, '(')
        
        condition_type = self.parse_expression()
        if condition_type != 'boolean':
            token = self.tokens[self.current - 1]  # Token anterior
            raise CompilerError(
                ErrorType.SEMANTIC,
                "La condición del if debe ser de tipo boolean",
                token.line,
                token.position
            )
            
        self.expect(TokenType.DELIMITER, ')')
        self.expect(TokenType.DELIMITER, '{')
        
        self.scope_stack.append({})
        while self.current < len(self.tokens) and self.current_token().value != '}':
            self.parse_statement()
        self.expect(TokenType.DELIMITER, '}')
        self.scope_stack.pop()

        if (self.current < len(self.tokens) and 
            self.current_token().type == TokenType.KEYWORD and 
            self.current_token().value == 'else'):
            self.advance()
            self.expect(TokenType.DELIMITER, '{')
            
            self.scope_stack.append({})
            while self.current < len(self.tokens) and self.current_token().value != '}':
                self.parse_statement()
            self.expect(TokenType.DELIMITER, '}')
            self.scope_stack.pop()

    def parse_while_statement(self):
        self.loop_depth += 1
        self.advance()  # consume 'while'
        self.expect(TokenType.DELIMITER, '(')
        
        condition_type = self.parse_expression()
        if condition_type != 'boolean':
            raise CompilerError(
                ErrorType.SEMANTIC,
                "La condición del while debe ser de tipo boolean",
                self.current_token().line,
                self.current_token().position
            )
            
        self.expect(TokenType.DELIMITER, ')')
        self.expect(TokenType.DELIMITER, '{')
        
        self.scope_stack.append({})
        while self.current < len(self.tokens) and self.current_token().value != '}':
            self.parse_statement()
        self.expect(TokenType.DELIMITER, '}')
        self.scope_stack.pop()
        self.loop_depth -= 1

    def parse_for_statement(self):
        """Analiza una estructura for con manejo mejorado de ámbitos"""
        self.loop_depth += 1
        self.advance()  # consume 'for'
        self.expect(TokenType.DELIMITER, '(')
        
        # Crear nuevo ámbito para el for
        self.scope_stack.append({})
        
        # Inicialización
        if self.current_token().type == TokenType.KEYWORD:
            self.parse_variable_declaration()
        else:
            self.parse_assignment()
            
        # Condición
        condition_type = self.parse_expression()
        if condition_type != 'boolean':
            token = self.current_token()
            raise CompilerError(
                ErrorType.SEMANTIC,
                "La condición del for debe ser de tipo boolean",
                token.line,
                token.position
            )
        self.expect(TokenType.DELIMITER, ';')
        
        # Incremento/actualización
        increment_start = self.current
        self.parse_expression()
        increment_end = self.current
        
        self.expect(TokenType.DELIMITER, ')')
        self.expect(TokenType.DELIMITER, '{')
        
        # Crear ámbito para el cuerpo del for
        self.scope_stack.append({})
        
        while self.current < len(self.tokens) and self.current_token().value != '}':
            self.parse_statement()
            
        self.expect(TokenType.DELIMITER, '}')

        # Eliminar el ámbito del cuerpo del for
        self.scope_stack.pop()
        # Eliminar el ámbito de la inicialización del for
        self.scope_stack.pop()
        
        self.loop_depth -= 1

    def parse_statement(self):
        """Analiza un statement con manejo mejorado de print y ámbitos"""
        if self.current >= len(self.tokens):
            raise CompilerError(
                ErrorType.SYNTACTIC,
                "Fin inesperado del código",
                self.tokens[-1].line,
                self.tokens[-1].position
            )

        token = self.current_token()
        
        if token.type == TokenType.KEYWORD:
            if token.value in ['int', 'float', 'string', 'boolean']:
                self.parse_variable_declaration()
            elif token.value == 'if':
                self.parse_if_statement()
            elif token.value == 'while':
                self.parse_while_statement()
            elif token.value == 'for':
                self.parse_for_statement()
            elif token.value == 'print':
                self.parse_print_statement()
            elif token.value == 'break':
                if self.loop_depth == 0:
                    raise CompilerError(
                        ErrorType.SEMANTIC,
                        "'break' fuera de un bucle",
                        token.line,
                        token.position
                    )
                self.advance()
                self.expect(TokenType.DELIMITER, ';')
            elif token.value == 'continue':
                if self.loop_depth == 0:
                    raise CompilerError(
                        ErrorType.SEMANTIC,
                        "'continue' fuera de un bucle",
                        token.line,
                        token.position
                    )
                self.advance()
                self.expect(TokenType.DELIMITER, ';')
        elif token.type == TokenType.IDENTIFIER:
            var_name = token.value
            var = self.get_variable(var_name)
            if var is None:
                raise CompilerError(
                    ErrorType.SEMANTIC,
                    f"Variable '{var_name}' no declarada",
                    token.line,
                    token.position
                )
            if self.current + 1 < len(self.tokens) and self.tokens[self.current + 1].type == TokenType.OPERATOR:
                self.parse_assignment()
            else:
                self.parse_expression()
                self.expect(TokenType.DELIMITER, ';')
        else:
            self.parse_expression()
            self.expect(TokenType.DELIMITER, ';')


    def parse(self):
        try:
            while self.current < len(self.tokens):
                self.parse_statement()
            
            # Verificar variables no utilizadas al final del análisis
            for scope in self.scope_stack:
                for var_name, var in scope.items():
                    if not var.used:
                        raise CompilerError(
                            ErrorType.SEMANTIC,
                            f"Variable '{var_name}' declarada pero nunca utilizada",
                            self.tokens[0].line,  # Usando la primera línea como referencia
                            0
                        )
        except IndexError:
            last_token = self.tokens[-1] if self.tokens else Token(TokenType.ERROR, "", 1, 0)
            raise CompilerError(
                ErrorType.SYNTACTIC,
                "Se llegó al final del código inesperadamente",
                last_token.line,
                last_token.position
            )

    def current_token(self) -> Token:
        if self.current >= len(self.tokens):
            raise CompilerError(
                ErrorType.SYNTACTIC,
                "Se llegó al final del código inesperadamente",
                self.tokens[-1].line if self.tokens else 1,
                self.tokens[-1].position if self.tokens else 0
            )
        return self.tokens[self.current]

    def advance(self):
        self.current += 1

    def expect(self, type: TokenType, value: str):
        token = self.current_token()
        if token.type != type or token.value != value:
            raise CompilerError(
                ErrorType.SYNTACTIC,
                f"Se esperaba '{value}'",
                token.line,
                token.position,
                value,
                token.value
            )
        self.advance()