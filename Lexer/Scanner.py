from Lexer.Token import Token

class Scanner:
    def __init__(self, programa):
        self.tokens = []
        self.symbol_table = {}  # Tabela de símbolos
        self.programa = programa
        self.inicio = 0
        self.atual = 0
        self.linha = 1

    def __str__(self):
        return f"Tokens: {self.tokens}, Symbol Table: {self.symbol_table}, Inicio: {self.inicio}, Atual: {self.atual}, Linha: {self.linha}"

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
                if self.lookAhead() == "=":
                    self.nextChar()
                    self.tokens.append(Token("NOTEQUAL", "!=" , self.linha))
                else:
                    self.tokens.append(Token("NOT", "!" , self.linha))
            elif char == "<":
                if self.lookAhead() == "=":
                    self.nextChar()
                    self.tokens.append(Token("LESSEQUAL", "<=" , self.linha))
                else:
                    self.tokens.append(Token("LESS", "<" , self.linha))
            elif char == ">":
                if self.lookAhead() == "=":
                    self.nextChar()
                    self.tokens.append(Token("GREATEQUAL", ">=" , self.linha))
                else:
                    self.tokens.append(Token("GREAT", ">" , self.linha))
            elif char.isdigit():
                self._scan_number()
            elif char.isalpha():
                self._scan_identifier(keywords)
            else:
                self.tokens.append(Token("INVALID", char, self.linha))

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

        lexeme = self.programa[self.inicio:self.atual]

        if self.lookAhead().isalpha():
            while self.lookAhead().isalnum():
                self.nextChar()
            lexeme = self.programa[self.inicio:self.atual]
            self.tokens.append(Token("INVALID", lexeme, self.linha))
        else:
            self.tokens.append(Token("NUMBER", lexeme, self.linha))

    def _scan_identifier(self, keywords):
        if not (self.programa[self.inicio].isalpha() or self.programa[self.inicio] == '_'):
            self.tokens.append(Token("INVALID", self.programa[self.inicio:self.atual], self.linha))
            return

        while self.lookAhead().isalnum() or self.lookAhead() == '_':
            self.nextChar()

        lexeme = self.programa[self.inicio:self.atual]
        if lexeme not in keywords:
            if lexeme.startswith("v") and lexeme[1:].isalnum(): 
                self.tokens.append(Token("ID_VAR", lexeme, self.linha))
                self.symbol_table[lexeme] = "VAR"  # Registrando na tabela de símbolos como variável
            elif lexeme.startswith("f") and lexeme[1:].isalnum(): 
                self.tokens.append(Token("ID_FUNC", lexeme, self.linha))
                self.symbol_table[lexeme] = "VAR" 
            elif lexeme.startswith("p") and lexeme[1:].isalnum(): 
                self.tokens.append(Token("ID_PROC", lexeme, self.linha))
                self.symbol_table[lexeme] = "VAR"
            else:
                self.tokens.append(Token("INVALID", lexeme, self.linha))
        else:
            token_type = keywords.get(lexeme, "ID")
            self.tokens.append(Token(token_type, lexeme, self.linha))
            self.symbol_table[lexeme] = token_type  # Registrando na tabela de símbolos como palavra-chave
