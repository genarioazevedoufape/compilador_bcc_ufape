class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def current_token(self):
        return self.tokens[self.current] if self.current < len(self.tokens) else None

    def match(self, expected_type):
        token = self.current_token()
        if token and token.tipo == expected_type:
            print(f"Matched {expected_type}: {token.lexema} na linha {token.linha}")  
            self.current += 1
            return token
        # else:
        #     if token:
        #         print(f"Expected {expected_type}, mas chegou {token.tipo}: {token.lexema} na linha {token.linha}")  
        #     else:
        #         print(f"Expected {expected_type}, mas chegou ao fim da entrada")
        #     return None

    def error(self, message):
        token = self.current_token()
        context = f"Na linha {token.linha} encontrou '{token.lexema}'" if token else "no final da entrada"
        print(f"Error: {message} {context}")  
        raise SyntaxError(f"{message} {context}")

    def parse(self):
        return self.programa()

    def programa(self):
        if self.bloco():
            print("Parsing completo sem erros.")
        else:
            self.error("Erro ao interpretar o programa.")
        return True

    def bloco(self):
        while self.current_token():
            
            if self.declaracao_variavel():  
                continue
            elif self.comando_condicional():  
                continue
            elif self.comando_enquanto():  
                continue
            elif self.declaracao_funcao():  
                continue
            elif self.declaracao_procedimento():  
                continue
            elif self.chamada_procedimento():  
                continue
            elif self.chamada_funcao():  
                continue
            elif self.comando_impressao():  
                continue
            else:
                break  
        return True

    def declaracao_variavel(self):
        if self.especificador_tipo(): 
            if self.match("ID_VAR"): 
                if self.match("ATTR"):  
                    if self.expressao(): 
                        if self.match("SEMICOLON"):  
                            return True
                        else:
                            self.error("Esperado ';' após a atribuição da variável.")
                    else:
                        self.error("Expressão inválida na atribuição da variável.")
                elif self.match("SEMICOLON"):
                    return True
                else:
                    self.error("Esperado ';' após o identificador da variável.")
            else:
                self.error("Esperado identificador de variável.")
        return False

    def especificador_tipo(self):
        return self.match("TYPE_INT") or self.match("TYPE_BOOLEAN")

    def comando_condicional(self):
        if self.match("IF"):
            if self.match("LBRACK"):  
                if self.expressao():  
                    if self.match("RBRACK"):  
                        if self.match("LCBRACK"): 
                            if self.bloco():  
                                if self.match("RCBRACK"):  
                                    self.else_opcional()  
                                    return True

        return False

    def else_opcional(self):
        if self.match("ELSE"):
            if self.match("LCBRACK"):  
                self.bloco()  
                if not self.match("RCBRACK"):  
                    self.error("Esperado '}' para fechar o bloco do 'else'.")
        return True  

    def else_part(self):
        if self.match("ELSE"):
            if self.match("LCBRACK"):
                if self.bloco():
                    if self.match("RCBRACK"):
                        return True
        return False  

    def comando_enquanto(self):
        if self.match("WHILE"):
            if self.match("LBRACK"):  
                if self.expressao():
                    if self.match("RBRACK"):  
                        if self.match("LCBRACK"):  
                            if self.bloco():
                                self.desvio_incondicional()
                                if self.match("RCBRACK"):  
                                    return True
        return False

    def comando_impressao(self):
        if self.match("PRINT"):
            if self.match("ID_VAR") or self.match("NUMBER") or self.match("TRUE") or self.match("FALSE"):  
                if self.match("SEMICOLON"):  
                    return True
                else:
                    self.error("Esperado ';' após o comando 'print'.")
            else:
                self.error("Esperado constante ou identificador após 'print'.")
        return False

    def constante(self):
        return self.match("NUMBER") or self.match("TRUE") or self.match("FALSE")

    def declaracao_funcao(self):
        if self.match("FUNC"):  
            if self.especificador_tipo():  
                if self.match("ID_FUNC"):  
                    if self.match("LBRACK"):  
                        if self.lista_parametros():  
                            if self.match("RBRACK"):  
                                if self.match("LCBRACK"):  
                                    if self.bloco():  
                                        if self.match("RETURN"):  
                                            if self.expressao():  
                                                if self.match("SEMICOLON"):  
                                                    if self.match("RCBRACK"):  
                                                        return True
                                        else:
                                            self.error("Esperado 'return' com uma expressão válida.")
                                else:
                                    self.error("Esperado '{' para iniciar o corpo da função.")
                        else:
                            self.error("Lista de parâmetros inválida ou ausente.")
                    else:
                        self.error("Esperado '(' para declarar os parâmetros da função.")
        return False

    def lista_parametros(self):
        if self.match("RBRACK"):  
            return True
        if self.declaracao_parametro():
            while self.match("COMMA"):
                if not self.declaracao_parametro():
                    self.error("Parâmetro esperado após ','")
            return True
        return False

    def declaracao_parametro(self):
        if self.especificador_tipo() or self.match("ID_VAR"):
            if self.match("ID_VAR"):
                return True
        return False

    def expressao(self):
        if self.match("NUMBER") or self.match("ID_VAR") or self.match("TRUE") or self.match("FALSE"):
            while self.current_token() and self.current_token().tipo in [
                "SUM", "SUB", "MUL", "DIV", 
                "EQUAL", "NOTEQUAL", "LESS", 
                "LESSEQUAL", "GREAT", "GREATEQUAL"
            ]:
                self.match(self.current_token().tipo)  
                if not (self.match("NUMBER") or self.match("ID_VAR")):
                    self.error("Esperado número ou variável após o operador")
            return True

        elif self.chamada_funcao():  
            return True
        return False

    def expressao_logica(self):
        if self.termo():
            while self.match("EQUAL") or self.match("NOTEQUAL") or \
                self.match("LESS") or self.match("LESSEQUAL") or \
                self.match("GREAT") or self.match("GREATEQUAL"):
                if not self.termo():  # Espera um termo após o operador lógico
                    self.error("Esperado termo após operador lógico.")
            return True
        return False

    def expressao_aritmetica(self):
        if self.termo():  # Primeiramente, verifica um termo
            while self.match("SUM") or self.match("SUB") or self.match("MUL") or self.match("DIV"):
                if not self.termo():
                    self.error("Termo esperado após operador na expressão aritmética")
            return True
        return False

    def termo(self):
        return self.match("ID_VAR") or self.constante()

    def chamada_funcao(self):
        if self.match("ID_FUNC"):  
            if self.match("LBRACK"):  
                if self.lista_argumentos():  
                    if self.match("RBRACK"):  
                        return True
                else:
                    self.error("Argumentos inválidos na chamada da função.")
            else:
                self.error("Esperado '(' para iniciar a chamada da função.")
        return False
    
    def lista_argumentos(self):
        if self.match("RBRACK"):  # Nenhum argumento
            return True
        if self.expressao():
            while self.match("COMMA"):
                if not self.expressao():
                    self.error("Expressão esperada após ',' nos argumentos da função.")
            return True
        return False

    def declaracao_procedimento(self):
        if self.match("PROC"):
            if self.match("ID_PROC"):
                if self.match("LBRACK"):
                    if self.lista_parametros():
                        if self.match("RBRACK"):
                            if self.match("LCBRACK"):
                                if self.bloco():
                                    if self.match("RCBRACK"):
                                        return True
        return False

    def chamada_procedimento(self):
        if self.match("ID_PROC"):
            if self.match("LBRACK"):
                self.lista_parametros()
                if self.match("RBRACK"):
                    if self.match("SEMICOLON"):
                        return True
        return False
    
    def desvio_incondicional(self):
        if self.match("BREAK") or self.match("CONTINUE"):
            if self.match("SEMICOLON"):
                return True
            else:
                self.error("Esperado ';' após 'break' ou 'continue'.")
        return True  

    def atribuicao_variavel(self):
        token = self.match("ID_VAR")
        if token:  # Identificador encontrado
            if self.match("ATTR"):  
                if self.expressao():
                    if self.match("SEMICOLON"):
                        return True
                    else:
                        self.error("Esperado ';' no final da tarefa")
        return False
