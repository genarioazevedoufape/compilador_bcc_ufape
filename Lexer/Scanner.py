from Lexer.Token import Token

class Scanner:
    def __init__(self, programa):
        self.tokens = []
        self.programa = programa
        self.inicio = 0
        self.atual = 0
        self.linha = 1

    def __str__(self):
        return "Tokens: %s\n Inicio: %s\n Atual: %s\n Linha: %s\n" % (str(self.tokens), str(self.inicio), str(self.atual), str(self.linha))

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
            "if": "IF",
            "else": "ELSE",
            "while": "WHILE",
            "break": "BREAK",
            "continue": "CONTINUE",
            "print": "PRINT",
            "true": "TRUE",
            "false": "FALSE",
            "func": "FUNC",
            "proc": "PROC",
            "return": "RETURN",
            "int": "TYPE_INT",
            "boolean": "TYPE_BOOLEAN"
        }
        while self.atual < len(self.programa):
            self.inicio = self.atual
            char = self.nextChar()
            if char in ' \t\r':
                pass
            elif char == '\n':
                self.linha += 1
            elif char in '(){};,':
                tokens_map = {
                    '(': "LBRACK",
                    ')': "RBRACK",
                    '{': "LCBRACK",
                    '}': "RCBRACK",
                    ';': "SEMICOLON",
                    ',': "COMMA"
                }
                self.tokens.append(Token(tokens_map[char], char, self.linha))
            elif char in '+-*/':
                tokens_map = {'+': "SUM", '-': "SUB", '*': "MUL", '/': "DIV"}
                self.tokens.append(Token(tokens_map[char], char, self.linha))
            elif char == '=':
                if self.lookAhead() == '=':
                    self.atual += 1
                    self.tokens.append(Token("EQUAL", "==", self.linha))
                else:
                    self.tokens.append(Token("ATTR", "=", self.linha))
            elif char == '<':
                if self.lookAhead() == '=':
                    self.atual += 1
                    self.tokens.append(Token("LESSEQUAL", "<=", self.linha))
                else:
                    self.tokens.append(Token("LESS", "<", self.linha))
            elif char == '>':
                if self.lookAhead() == '=':
                    self.atual += 1
                    self.tokens.append(Token("GREATEQUAL", ">=", self.linha))
                else:
                    self.tokens.append(Token("GREAT", ">", self.linha))
            elif char.isdigit():
                while self.lookAhead().isdigit():
                    self.nextChar()
                self.tokens.append(Token("NUMBER", self.programa[self.inicio:self.atual], self.linha))
            elif char.isalpha():
                while self.lookAhead().isalnum():
                    self.nextChar()
                lexeme = self.programa[self.inicio:self.atual]
                if lexeme in keywords:
                    self.tokens.append(Token(keywords[lexeme], lexeme, self.linha))
                elif lexeme.startswith("v"):
                    self.tokens.append(Token("ID_VAR", lexeme, self.linha))
                elif lexeme.startswith("f"):
                    self.tokens.append(Token("ID_FUNC", lexeme, self.linha))
                elif lexeme.startswith("p"):
                    self.tokens.append(Token("ID_PROC", lexeme, self.linha))
                else:
                    self.tokens.append(Token("ID", lexeme, self.linha))
            else:
                print(f'Caractere Inválido na linha {self.linha}: {char}')
                exit(2)
