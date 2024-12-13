from Lexer.Token import Token

class Scanner:
    def __init__(self, programa):
        self.tokens = []
        self.programa = programa
        self.inicio = 0
        self.atual = 0
        self.linha = 1

    def __str__(self):
        return f"Tokens: {self.tokens}, Inicio: {self.inicio}, Atual: {self.atual}, Linha: {self.linha}"

    def nextChar(self):
        self.atual += 1
        return self.programa[self.atual - 1]

    def lookAhead(self):
        if self.atual < len(self.programa):
            return self.programa[self.atual]
        return '\0'

    def scan(self):
        self.scanTokens()
        self.tokens.append(Token("FIM", '', self.linha))
        return self.tokens

    def scanTokens(self):
        keywords = {
            "if": "IF", "else": "ELSE", "while": "WHILE", "break": "BREAK",
            "continue": "CONTINUE", "print": "PRINT", "true": "TRUE",
            "false": "FALSE", "func": "FUNC", "proc": "PROC", "return": "RETURN",
            "int": "TYPE_INT", "boolean": "TYPE_BOOLEAN"
        }
        tokens_map = {
            '(': "LBRACK", ')': "RBRACK", '{': "LCBRACK", '}': "RCBRACK",
            ';': "SEMICOLON", ',': "COMMA", '+': "SUM", '-': "SUB",
            '*': "MUL", '/': "DIV"
        }

        while self.atual < len(self.programa):
            self.inicio = self.atual
            char = self.nextChar()

            if char in ' \t\r':
                pass
            elif char == '\n':
                self.linha += 1
            elif char in tokens_map:
                self.tokens.append(Token(tokens_map[char], char, self.linha))
            elif char == "=":
                self._match_double_char("=", "EQUAL", "ATTR")
            elif char == "!":
                if self.lookAhead() == "=":  # Verifica se o próximo caractere é "="
                    self.nextChar()  # Consome o "="
                    self.tokens.append(Token("NOTEQUAL", "!=" , self.linha))  # Adiciona o token NOTEQUAL
                else:
                    self.tokens.append(Token("NOT", "!" , self.linha))  # Caso contrário, é o operador NOT
            elif char == "<":
                if self.lookAhead() == "=":  # Verifica se o próximo caractere é "="
                    self.nextChar()  # Consome o "="
                    self.tokens.append(Token("LESSEQUAL", "<=" , self.linha))  # Adiciona o token LESSEQUAL
                else:
                    self.tokens.append(Token("LESS", "<" , self.linha))  # Caso contrário, é o operador LESS
            elif char == ">":
                if self.lookAhead() == "=":  # Verifica se o próximo caractere é "="
                    self.nextChar()  # Consome o "="
                    self.tokens.append(Token("GREATEQUAL", ">=" , self.linha))  # Adiciona o token GREATEQUAL
                else:
                    self.tokens.append(Token("GREAT", ">" , self.linha))  # Caso contrário, é o operador GREAT
            elif char.isdigit():
                self._scan_number()
            elif char.isalpha():
                self._scan_identifier(keywords)
            else:
                self.tokens.append(Token("INVALID", char, self.linha))
                print(f"Caractere Inválido na linha {self.linha}: {char}")

    def _match_double_char(self, expected, double_type, single_type):
        if self.lookAhead() == expected:
            self.nextChar()
            self.tokens.append(Token(double_type, f"{expected}{expected}", self.linha))
        else:
            self.tokens.append(Token(single_type, expected, self.linha))

    def _scan_number(self):
        while self.lookAhead().isdigit():
            self.nextChar()
        if self.lookAhead() == '.':
            self.nextChar()
            while self.lookAhead().isdigit():
                self.nextChar()
        self.tokens.append(Token("NUMBER", self.programa[self.inicio:self.atual], self.linha))

    def _scan_identifier(self, keywords):
        while self.lookAhead().isalnum():
            self.nextChar()
        lexeme = self.programa[self.inicio:self.atual]
        # Verifica se o lexema é uma palavra reservada
        token_type = keywords.get(lexeme, "ID")
        if lexeme.startswith("v") and token_type == "ID":
            token_type = "ID_VAR"
        elif lexeme.startswith("f") and token_type == "ID":
            token_type = "ID_FUNC"
        elif lexeme.startswith("p") and token_type == "ID":
            token_type = "ID_PROC"
        self.tokens.append(Token(token_type, lexeme, self.linha))
