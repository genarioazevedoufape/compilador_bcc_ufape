class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.loop_depth = 0  # Contador de contexto de loop
        self.scope_stack = [{}]  # Pilha de escopos (inicia com o escopo global)
        self.function_return_type = None  # Tipo de retorno da função atual

    def current_token(self):
        return self.tokens[self.current] if self.current < len(self.tokens) else None

    def peek(self):
        """Retorna o próximo token sem avançar o índice."""
        if self.current + 1 < len(self.tokens):
            return self.tokens[self.current + 1]
        return None

    def match(self, expected_type):
        """Verifica se o token atual corresponde ao tipo esperado."""
        token = self.current_token()
        if token and token.tipo == expected_type:
            print(f"Matched {expected_type}: {token.lexema} na linha {token.linha}")
            self.current += 1
            return token
        elif token and token.tipo == "INVALID":
            self.error(f"Caractere inválido encontrado: '{token.lexema}'")
        return None

    def error(self, message):
        """Gera um erro de sintaxe com contexto."""
        token = self.current_token()
        context = f"Na linha {token.linha} encontrou '{token.lexema}'" if token else "no final da entrada"
        raise SyntaxError(f"{message} {context}")

    def enter_scope(self):
        """Entra em um novo escopo."""
        self.scope_stack.append({})

    def exit_scope(self):
        """Sai do escopo atual."""
        if len(self.scope_stack) > 1:  # Não remove o escopo global
            self.scope_stack.pop()

    def add_symbol(self, name, symbol_type):
        """Adiciona um símbolo ao escopo atual."""
        if name in self.scope_stack[-1]:
            self.error(f"Identificador '{name}' já declarado no escopo atual.")
        self.scope_stack[-1][name] = {"type": symbol_type}

    def get_symbol_type(self, name):
        """Retorna o tipo de um símbolo, verificando todos os escopos."""
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]["type"]
        self.error(f"Identificador '{name}' não declarado.")

    def parse(self):
        """Inicia o processo de parsing."""
        return self.programa()

    def programa(self):
        """Processa o programa principal."""
        if self.bloco():
            print("Parsing completo sem erros.")
        else:
            self.error("Erro ao interpretar o programa.")
        return True

    def bloco(self):
        """Processa um bloco de código."""
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
                if not self.match("SEMICOLON"):
                    self.error("Esperado ';' após a chamada da função.")
                continue
            elif self.comando_impressao():
                continue
            elif self.desvio_incondicional():
                continue
            else:
                break
        return True

    def declaracao_variavel(self):
        tipo = self.especificador_tipo()
        if not tipo:
            token = self.current_token()
            if token and token.tipo == "ID_VAR":
                # Se não houver especificador de tipo, verifica se é uma atribuição
                if self.peek() and self.peek().tipo == "ATTR":
                    return self.atribuicao_variavel()
                else:
                    self.error(f"Declaração de variável '{token.lexema}' na linha {token.linha} não é antecedida por um especificador de tipo.")
            return False

        if self.match("ID_VAR"):
            var_name = self.tokens[self.current - 1].lexema
            self.add_symbol(var_name, tipo)

            if self.match("ATTR"):
                expr_type = self.expressao()
                if expr_type != tipo:
                    self.error(f"Atribuição inválida: esperado '{tipo}', encontrado '{expr_type}'.")
                if self.match("SEMICOLON"):
                    return True
                else:
                    self.error("Esperado ';' após a atribuição da variável.")
            elif self.match("SEMICOLON"):
                return True
            else:
                self.error("Esperado ';' após o identificador da variável.")
        else:
            self.error("Esperado identificador de variável.")
        return False

    def atribuicao_variavel(self):
        """Processa uma atribuição de variável."""
        var_name = self.tokens[self.current].lexema
        var_type = self.get_symbol_type(var_name)
        self.match("ID_VAR")

        if self.match("ATTR"):
            expr_type = self.expressao()
            if expr_type != var_type:
                self.error(f"Atribuição inválida: esperado '{var_type}', encontrado '{expr_type}'.")
            if self.match("SEMICOLON"):
                return True
            else:
                self.error("Esperado ';' após a atribuição da variável.")
        else:
            self.error("Esperado '=' após o identificador da variável.")
        return False
    def especificador_tipo(self):
        """Processa o tipo de uma variável."""
        if self.match("TYPE_INT"):
            return "int"
        elif self.match("TYPE_BOOLEAN"):
            return "boolean"
        return None

    def comando_condicional(self):
        """Processa um comando condicional (if)."""
        if self.match("IF"):
            if self.match("LBRACK"):
                expr_type = self.expressao()
                if expr_type != "boolean":
                    self.error(f"Condição do 'if' deve ser do tipo 'boolean', encontrado '{expr_type}'.")
                if self.match("RBRACK"):
                    if self.match("LCBRACK"):
                        if self.bloco():
                            if self.match("RCBRACK"):
                                self.else_opcional()
                                return True
                            else:
                                self.error("Esperado '}' para fechar o bloco do 'if'.")
                        else:
                            self.error("Bloco do 'if' inválido.")
                    else:
                        self.error("Esperado '{' para iniciar o bloco do 'if'.")
                else:
                    self.error("Esperado ')' para fechar a condição do 'if'.")
            else:
                self.error("Esperado '(' para abrir a condição do 'if'.")
        return False

    def else_opcional(self):
        """Processa o bloco else opcional."""
        if self.match("ELSE"):
            if self.match("LCBRACK"):
                if self.bloco():
                    if not self.match("RCBRACK"):
                        self.error("Esperado '}' para fechar o bloco do 'else'.")
                else:
                    self.error("Bloco do 'else' inválido.")
            else:
                self.error("Esperado '{' para abrir o bloco do 'else'.")
        return True

    def comando_enquanto(self):
        """Processa um comando while."""
        if self.match("WHILE"):
            if self.match("LBRACK"):
                expr_type = self.expressao()
                if expr_type != "boolean":
                    self.error(f"Condição do 'while' deve ser do tipo 'boolean', encontrado '{expr_type}'.")
                if self.match("RBRACK"):
                    if self.match("LCBRACK"):
                        self.loop_depth += 1
                        if self.bloco():
                            self.loop_depth -= 1
                            if self.match("RCBRACK"):
                                return True
                            else:
                                self.error("Esperado '}' para fechar o bloco do 'while'.")
                        else:
                            self.error("Bloco do 'while' inválido.")
                    else:
                        self.error("Esperado '{' para iniciar o bloco do 'while'.")
                else:
                    self.error("Esperado ')' para fechar a condição do 'while'.")
            else:
                self.error("Esperado '(' para abrir a condição do 'while'.")
        return False

    def comando_impressao(self):
        """Processa um comando print."""
        if self.match("PRINT"):
            expr_type = self.expressao()
            if expr_type not in ["int", "boolean"]:
                self.error(f"Tipo inválido para impressão: '{expr_type}'.")
            if self.match("SEMICOLON"):
                return True
            else:
                self.error("Esperado ';' após o comando 'print'.")
        return False

    def declaracao_funcao(self):
        """Processa a declaração de uma função."""
        if self.match("FUNC"):
            return_type = self.especificador_tipo()
            if not return_type:
                self.error("Esperado tipo de retorno da função.")
            
            if self.match("ID_FUNC"):
                func_name = self.tokens[self.current - 1].lexema
                self.function_return_type = return_type
                self.enter_scope()  # Entra no escopo da função

                if self.match("LBRACK"):
                    if self.lista_parametros():
                        if self.match("RBRACK"):
                            if self.match("LCBRACK"):
                                if self.bloco():
                                    if self.match("RETURN"):
                                        expr_type = self.expressao()
                                        if expr_type != return_type:
                                            self.error(f"Tipo de retorno inválido: esperado '{return_type}', encontrado '{expr_type}'.")
                                        if self.match("SEMICOLON"):
                                            if self.match("RCBRACK"):
                                                self.exit_scope()  # Sai do escopo da função
                                                return True
                                            else:
                                                self.error("Esperado '}' para fechar o corpo da função.")
                                        else:
                                            self.error("Esperado ';' após o retorno da função.")
                                    else:
                                        self.error("Esperado 'return' no corpo da função.")
                                else:
                                    self.error("Bloco da função inválido.")
                            else:
                                self.error("Esperado '{' para iniciar o corpo da função.")
                        else:
                            self.error("Esperado ')' para fechar a lista de parâmetros.")
                    else:
                        self.error("Lista de parâmetros inválida.")
                else:
                    self.error("Esperado '(' para iniciar a lista de parâmetros.")
            else:
                self.error("Esperado identificador da função.")
        return False

    def lista_parametros(self):
        """Processa a lista de parâmetros de uma função."""
        if self.match("RBRACK"):  # Caso não haja parâmetros
            return True
        
        if self.declaracao_parametro():
            while self.match("COMMA"):
                if not self.declaracao_parametro():
                    self.error("Esperado parâmetro após ','.")
            return True
        return False

    def declaracao_parametro(self):
        """Processa a declaração de um parâmetro."""
        tipo = self.especificador_tipo()
        if not tipo:
            self.error("Esperado tipo do parâmetro.")
        
        if self.match("ID_VAR"):
            param_name = self.tokens[self.current - 1].lexema
            self.add_symbol(param_name, tipo)
            return True
        return False

    def expressao(self):
        """Processa uma expressão."""
        return self.expressao_logica()

    def expressao_logica(self):
        """Processa uma expressão lógica."""
        left_type = self.expressao_aditiva()
        token = self.current_token()
        if token and token.tipo in ["EQUAL", "NOTEQUAL", "LESS", "LESSEQUAL", "GREAT", "GREATEQUAL"]:
            self.match(token.tipo)
            right_type = self.expressao_aditiva()
            if left_type != right_type:
                self.error(f"Tipos incompatíveis na expressão: '{left_type}' e '{right_type}'.")
            return "boolean"
        return left_type

    def expressao_aditiva(self):
        """Processa uma expressão aditiva (+, -)."""
        left_type = self.expressao_multiplicativa()
        token = self.current_token()
        while token and token.tipo in ["SUM", "SUB"]:
            self.match(token.tipo)
            right_type = self.expressao_multiplicativa()
            if left_type != right_type:
                self.error(f"Tipos incompatíveis na expressão: '{left_type}' e '{right_type}'.")
            left_type = "int"  # O resultado de uma operação aditiva é sempre int
            token = self.current_token()
        return left_type

    def expressao_multiplicativa(self):
        """Processa uma expressão multiplicativa (*, /, %)."""
        left_type = self.termo()
        token = self.current_token()
        while token and token.tipo in ["MUL", "DIV", "MOD"]:
            self.match(token.tipo)
            right_type = self.termo()
            if left_type != right_type:
                self.error(f"Tipos incompatíveis na expressão: '{left_type}' e '{right_type}'.")
            left_type = "int"  # O resultado de uma operação multiplicativa é sempre int
            token = self.current_token()
        return left_type

    def termo(self):
        """Processa um termo (número, variável ou chamada de função)."""
        token = self.current_token()
        if token.tipo == "NUMBER":
            self.match("NUMBER")
            return "int"
        elif token.tipo == "TRUE" or token.tipo == "FALSE":
            self.match(token.tipo)
            return "boolean"
        elif token.tipo == "ID_VAR":
            var_name = token.lexema
            var_type = self.get_symbol_type(var_name)
            self.match("ID_VAR")
            return var_type
        elif self.chamada_funcao():
            return self.function_return_type
        else:
            self.error(f"Esperado número, variável ou chamada de função, encontrado '{token.lexema}'.")

    def chamada_funcao(self):
        """Processa uma chamada de função."""
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
        """Processa a lista de argumentos de uma função."""
        if self.match("RBRACK"):  # Caso não haja argumentos
            return True
        
        if self.expressao():
            while self.match("COMMA"):
                if not self.expressao():
                    self.error("Esperado expressão após ','.")
            return True
        return False

    def declaracao_procedimento(self):
        """Processa a declaração de um procedimento."""
        if self.match("PROC"):
            if self.match("ID_PROC"):
                proc_name = self.tokens[self.current - 1].lexema
                self.enter_scope()  # Entra no escopo do procedimento

                if self.match("LBRACK"):
                    if self.lista_parametros():
                        if self.match("RBRACK"):
                            if self.match("LCBRACK"):
                                if self.bloco():
                                    if self.match("RCBRACK"):
                                        self.exit_scope()  # Sai do escopo do procedimento
                                        return True
                                    else:
                                        self.error("Esperado '}' para fechar o corpo do procedimento.")
                                else:
                                    self.error("Bloco do procedimento inválido.")
                            else:
                                self.error("Esperado '{' para iniciar o corpo do procedimento.")
                        else:
                            self.error("Esperado ')' para fechar a lista de parâmetros.")
                    else:
                        self.error("Lista de parâmetros inválida.")
                else:
                    self.error("Esperado '(' para iniciar a lista de parâmetros.")
            else:
                self.error("Esperado identificador do procedimento.")
        return False

    def chamada_procedimento(self):
        """Processa uma chamada de procedimento."""
        if self.match("ID_PROC"):
            if self.match("LBRACK"):
                if self.lista_argumentos():
                    if self.match("RBRACK"):
                        if self.match("SEMICOLON"):
                            return True
                        else:
                            self.error("Esperado ';' após a chamada do procedimento.")
                    else:
                        self.error("Esperado ')' para fechar os argumentos do procedimento.")
                else:
                    self.error("Argumentos inválidos na chamada do procedimento.")
            else:
                self.error("Esperado '(' para iniciar os argumentos do procedimento.")
        return False

    def desvio_incondicional(self):
        """Processa comandos de desvio incondicional (break, continue)."""
        if self.match("BREAK") or self.match("CONTINUE"):
            if self.loop_depth == 0:
                self.error("'break' e 'continue' só podem ser usados dentro de loops.")
            if self.match("SEMICOLON"):
                return True
            else:
                self.error("Esperado ';' após 'break' ou 'continue'.")
        return False