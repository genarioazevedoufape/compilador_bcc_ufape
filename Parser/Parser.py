class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.loop_depth = 0  # Contador de contexto de loop
        self.scope_stack = [{}]  # Pilha de escopos (inicia com o escopo global)
        self.function_return_type = None  # Tipo de retorno da função atual
        self.procedure_params = {}  # Dicionário para mapear procedimentos e seus parâmetros
        self.function_params = {}  # Dicionário para mapear funções e seus parâmetros
        self.temp_counter = 0  # Contador para variáveis temporárias
        self.code = []  # Lista para armazenar o código de três endereços
        self.label_counter = 0  # Contador para labels
        self.used_variables = set()  # Rastreia variáveis usadas
        self.declared_variables = set()  # Rastreia variáveis declaradas
        self.uninitialized_vars = set()  # Rastreia variáveis não inicializadas

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
            self.error_sintatico(f"Caractere inválido encontrado: '{token.lexema}'")
        return None

    def error_sintatico(self, message):
        """Gera um erro de sintaxe com contexto."""
        token = self.current_token()
        context = f"Na linha {token.linha} encontrou '{token.lexema}'" if token else "no final da entrada"
        raise SyntaxError(f"[Erro Sintático] {message} {context}")

    def error_semantico(self, message):
        """Gera um erro semântico com contexto."""
        token = self.current_token()
        context = f"Na linha {token.linha} encontrou '{token.lexema}'" if token else "no final da entrada"
        raise ValueError(f"[Erro Semântico] {message} {context}")

    def enter_scope(self):
        """Entra em um novo escopo."""
        self.scope_stack.append({})

    def check_unused_variables(self):
        """Verifica se há variáveis declaradas mas não utilizadas."""
        for scope in self.scope_stack:
            for name, info in scope.items():
                if not info["used"] and not name.startswith('_'):
                    print(f"[Aviso Semântico] Variável '{name}' declarada mas não utilizada")

    def check_uninitialized_vars(self):
        """Verifica variáveis declaradas mas não inicializadas ao sair do escopo."""
        for var in self.uninitialized_vars:
            print(f"[Aviso Semântico] Variável '{var}' declarada mas nunca inicializada")

    def exit_scope(self):
        """Sai do escopo atual com verificações adicionais."""
        self.check_uninitialized_vars()
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()

    def verify_expression_types(self, left_type, right_type, operator):
        """Verifica compatibilidade de tipos em operações."""
        if operator in ["+", "-", "*", "/", "%"]:
            if left_type != "int" or right_type != "int":
                self.error_semantico(f"Operação '{operator}' requer operandos inteiros, encontrados {left_type} e {right_type}")
            return "int"
        
        elif operator in ["==", "!=", "<", "<=", ">", ">="]:
            if left_type != right_type:
                self.error_semantico(f"Operação de comparação '{operator}' requer operandos do mesmo tipo, encontrados {left_type} e {right_type}")
            return "boolean"
        
        elif operator in ["&&", "||"]:
            if left_type != "boolean" or right_type != "boolean":
                self.error_semantico(f"Operação lógica '{operator}' requer operandos booleanos, encontrados {left_type} e {right_type}")
            return "boolean"
        
        return None
    
    def check_return_paths(self, function_name, return_type):
        """Verifica se todos os caminhos da função retornam um valor."""
        if return_type != "void" and not self.scope_stack[-1].get("_has_return", False):
            self.error_semantico(f"Função '{function_name}' não retorna valor em todos os caminhos")

    def verify_function_return(self, function_name, expr_type):
        """Verifica se o tipo de retorno corresponde ao declarado."""
        expected_type = self.function_params[function_name]["return_type"]
        if expr_type != expected_type:
            self.error_semantico(f"Tipo de retorno incorreto em '{function_name}'. Esperado {expected_type}, encontrado {expr_type}")

    def verify_parameters(self, name, expected_types, actual_args, is_function=True):
        """Verifica os parâmetros de funções/procedimentos."""
        if len(expected_types) != len(actual_args):
            kind = "função" if is_function else "procedimento"
            self.error_semantico(f"Número incorreto de argumentos para {kind} '{name}'. Esperado {len(expected_types)}, encontrado {len(actual_args)}")
        
        for i, (expected, (actual_type, _)) in enumerate(zip(expected_types, actual_args)):
            if expected != actual_type:
                self.error_semantico(f"Tipo incorreto para argumento {i+1} em '{name}'. Esperado {expected}, encontrado {actual_type}")

    def add_symbol(self, name, symbol_type, initialized=False, is_param=False):
        """Adiciona um símbolo ao escopo atual com verificação de declaração duplicada."""
        if name in self.scope_stack[-1]:
            self.error_semantico(f"Identificador '{name}' já declarado no escopo atual.")
        
        self.scope_stack[-1][name] = {
            "type": symbol_type,
            "initialized": initialized or is_param,
            "used": False
        }
        self.declared_variables.add(name)
        if not initialized and not is_param:
            self.uninitialized_vars.add(name)

    def get_symbol_type(self, name):
        """Retorna o tipo de um símbolo com verificações adicionais."""
        for scope in reversed(self.scope_stack):
            if name in scope:
                scope[name]["used"] = True  # Marca como usado
                self.used_variables.add(name)
                
                if name in self.uninitialized_vars:
                    self.uninitialized_vars.remove(name)
                
                if not scope[name]["initialized"]:
                    self.error_semantico(f"Variável '{name}' usada antes de ser inicializada.")
                return scope[name]["type"]
        self.error_semantico(f"Identificador '{name}' não declarado.")
    
    def new_temp(self):
        """Gera um novo nome de variável temporária."""
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self):
        """Gera um novo label."""
        self.label_counter += 1
        return f"L{self.label_counter}"

    def emit(self, code):
        """Adiciona uma instrução ao código de três endereços."""
        self.code.append(code)
        print(code)  # Exibe no terminal   

    def parse(self):
        """Inicia o processo de parsing com verificações finais."""
        print("\n=== Código de Três Endereços ===")
        try:
            result = self.programa()
            
            # Verificações semânticas finais
            self.check_unused_variables()
            self.check_uninitialized_vars()
            
            # Verifica se o último token foi processado corretamente
            if self.current_token() and self.current_token().tipo != "FIM":
                self.error_sintatico("Fim inesperado do parsing")
                
            # Retorna o código gerado se o parsing foi bem-sucedido
            return self.code if result else None
                
        except (SyntaxError, ValueError) as e:
            print(f"\nErro encontrado: {e}")
            return None
            
        print("===============================")
        return self.code
    
    def programa(self):
        """Processa o programa principal."""
        if self.bloco():
            print("Parsing completo sem erros.")
        else:
            self.error_sintatico("Erro ao interpretar o programa.")
        return True

    def bloco(self):
        """Processa um bloco de código."""
        while self.current_token():
            token = self.current_token()
            
            # Se encontrar um } ou FIM, retorna True para indicar fim do bloco
            if token.tipo in ["RCBRACK", "FIM"]:
                return True
                
            if self.declaracao_variavel():
                continue
            elif self.comando_impressao():
                continue
            elif self.comando_condicional():
                continue
            elif self.comando_enquanto():
                continue
            elif self.declaracao_funcao():
                continue
            elif self.declaracao_procedimento():
                continue
            elif self.desvio_incondicional():
                continue
            elif self.chamada_procedimento():
                if not self.match("SEMICOLON"):
                    self.error_sintatico("Esperado ';' após a chamada do procedimento.")
                continue
            elif self.chamada_funcao():
                if not self.match("SEMICOLON"):
                    self.error_sintatico("Esperado ';' após a chamada da função.")
                continue
            else:
                if token.tipo != "RCBRACK":
                    self.error_sintatico(f"Comando inválido: {token.lexema}")
                break
        return True

    def declaracao_variavel(self):
        """Processa declaração de variável marcando como inicializada quando há atribuição."""
        tipo = self.especificador_tipo()
        if not tipo:
            token = self.current_token()
            if token and token.tipo == "ID_VAR":
                if self.peek() and self.peek().tipo == "ATTR":
                    return self.atribuicao_variavel()
                else:
                    self.error_semantico(f"Declaração de variável '{token.lexema}' na linha {token.linha} não é antecedida por um especificador de tipo.")
            return False

        if self.match("ID_VAR"):
            var_name = self.tokens[self.current - 1].lexema
            # Adiciona a variável ao escopo, marcando como inicializada se houver atribuição
            initialized = False
            
            if self.match("ATTR"):
                expr_type, expr_temp = self.expressao()
                if expr_type != tipo:
                    self.error_semantico(f"Atribuição inválida: esperado '{tipo}', encontrado '{expr_type}'.")
                self.emit(f"{var_name} = {expr_temp}")
                initialized = True
                if self.match("SEMICOLON"):
                    self.add_symbol(var_name, tipo, initialized)
                    return True
                else:
                    self.error_sintatico("Esperado ';' após a atribuição da variável.")
            elif self.match("SEMICOLON"):
                self.add_symbol(var_name, tipo, initialized)
                return True
            else:
                self.error_sintatico("Esperado ';' após o identificador da variável.")
        else:
            self.error_sintatico("Esperado identificador de variável.")
        return False

    def atribuicao_variavel(self):
        """Processa uma atribuição de variável marcando como inicializada."""
        var_name = self.tokens[self.current].lexema
        # Primeiro verifica se a variável existe
        var_type = None
        for scope in reversed(self.scope_stack):
            if var_name in scope:
                var_type = scope[var_name]["type"]
                break
        
        if var_type is None:
            self.error_semantico(f"Variável '{var_name}' não declarada.")
        
        self.match("ID_VAR")
        if self.match("ATTR"):
            expr_type, expr_temp = self.expressao()
            if expr_type != var_type:
                self.error_semantico(f"Atribuição inválida: esperado '{var_type}', encontrado '{expr_type}'.")
            
            self.emit(f"{var_name} = {expr_temp}")
            
            # Atualiza o status de inicialização no escopo mais interno onde a variável existe
            for scope in reversed(self.scope_stack):
                if var_name in scope:
                    scope[var_name]["initialized"] = True
                    break
                    
            if self.match("SEMICOLON"):
                return True
            else:
                self.error_sintatico("Esperado ';' após a atribuição da variável.")
        else:
            self.error_sintatico("Esperado '=' após o identificador da variável.")
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
                expr_type, expr_temp = self.expressao()
                if expr_type != "boolean":
                    self.error_semantico(f"Condição do 'if' deve ser do tipo 'boolean', encontrado '{expr_type}'.")
                
                false_label = self.new_label()
                end_label = self.new_label()
                
                self.emit(f"ifFalse {expr_temp} goto {false_label}")
                
                if self.match("RBRACK"):
                    if self.match("LCBRACK"):
                        self.emit(f"// Bloco do if")
                        if self.bloco():
                            self.emit(f"goto {end_label}")
                            self.emit(f"{false_label}:")
                            if self.match("RCBRACK"):
                                self.else_opcional(end_label)
                                self.emit(f"{end_label}:")
                                return True
                            else:
                                self.error_sintatico("Esperado '}' para fechar o bloco do 'if'.")
                        else:
                            self.error_sintatico("Bloco do 'if' inválido.")
                    else:
                        self.error_sintatico("Esperado '{' para iniciar o bloco do 'if'.")
                else:
                    self.error_sintatico("Esperado ')' para fechar a condição do 'if'.")
            else:
                self.error_sintatico("Esperado '(' para abrir a condição do 'if'.")
        return False

    def else_opcional(self, end_label):
        """Processa o bloco else opcional."""
        if self.match("ELSE"):
            if self.match("LCBRACK"):
                self.emit(f"// Bloco do else")
                if self.bloco():
                    if not self.match("RCBRACK"):
                        self.error_sintatico("Esperado '}' para fechar o bloco do 'else'.")
                else:
                    self.error_sintatico("Bloco do 'else' inválido.")
            else:
                self.error_sintatico("Esperado '{' para abrir o bloco do 'else'.")
        return True

    def comando_enquanto(self):
        """Processa um comando while."""
        if self.match("WHILE"):
            start_label = self.new_label()
            loop_label = self.new_label()
            end_label = self.new_label()
            
            self.emit(f"{start_label}:")
            
            if self.match("LBRACK"):
                expr_type, expr_temp = self.expressao()
                if expr_type != "boolean":
                    self.error_semantico(f"Condição do 'while' deve ser do tipo 'boolean', encontrado '{expr_type}'.")
                
                self.emit(f"ifFalse {expr_temp} goto {end_label}")
                
                if self.match("RBRACK"):
                    if self.match("LCBRACK"):
                        self.loop_depth += 1
                        self.emit(f"{loop_label}:")
                        self.emit(f"// Bloco do while")
                        
                        # Processa o bloco até encontrar RCBRACK
                        while True:
                            token = self.current_token()
                            if not token:
                                self.error_sintatico("Fechamento '}' esperado para o bloco while")
                            
                            if token.tipo == "RCBRACK":
                                self.match("RCBRACK")
                                break
                                
                            if not (self.declaracao_variavel() or 
                                    self.comando_condicional() or 
                                    self.comando_impressao() or 
                                    self.atribuicao_variavel() or 
                                    self.desvio_incondicional()):
                                self.error_sintatico(f"Comando inválido dentro do bloco while: {token.lexema}")
                        
                        self.loop_depth -= 1
                        self.emit(f"goto {start_label}")
                        self.emit(f"{end_label}:")
                        return True
                    else:
                        self.error_sintatico("Esperado '{' para iniciar o bloco do 'while'.")
                else:
                    self.error_sintatico("Esperado ')' para fechar a condição do 'while'.")
            else:
                self.error_sintatico("Esperado '(' para abrir a condição do 'while'.")
        return False

    def comando_impressao(self):
        """Processa um comando print."""
        if self.match("PRINT"):
            expr_type, expr_temp = self.expressao()
            
            if expr_type not in ["int", "boolean"]:
                self.error_semantico(f"Tipo inválido para impressão: '{expr_type}'.")
                
            self.emit(f"print {expr_temp}")
            
            # Verifica SEMICOLON apenas se o próximo token não for FIM ou RCBRACK
            next_token = self.current_token()
            if next_token and next_token.tipo not in ["FIM", "RCBRACK"]:
                if not self.match("SEMICOLON"):
                    self.error_sintatico("Esperado ';' após o comando 'print'.")
            
            return True
        return False
            
    def declaracao_funcao(self):
        """Processa a declaração de uma função."""
        if self.match("FUNC"):
            return_type = self.especificador_tipo()
            if not return_type:
                self.error_sintatico("Esperado tipo de retorno da função.")
            
            if self.match("ID_FUNC"):
                func_name = self.tokens[self.current - 1].lexema
                # Armazena o tipo de retorno no dicionário de funções
                self.function_params[func_name] = {
                    "return_type": return_type,
                    "param_types": []
                }
                self.function_return_type = return_type  # Mantém para compatibilidade
                self.enter_scope()  # Entra no escopo da função

                if self.match("LBRACK"):
                    params = self.lista_parametros()
                    self.function_params[func_name]["param_types"] = [param["type"] for param in params]
                    if self.match("RBRACK"):
                        if self.match("LCBRACK"):
                            # Verifica se o bloco tem retorno em todos os caminhos
                            self.scope_stack[-1]["_has_return"] = False
                            if self.bloco_com_retorno(return_type):
                                if not self.scope_stack[-1]["_has_return"] and return_type != "void":
                                    self.error_semantico(f"Função '{func_name}' não retorna valor em todos os caminhos.")
                                
                                if self.match("RCBRACK"):
                                    self.exit_scope()
                                    return True
                                else:
                                    self.error_sintatico("Esperado '}' para fechar o corpo da função.")
                            else:
                                self.error_sintatico("Bloco da função inválido.")
                        else:
                            self.error_sintatico("Esperado '{' para iniciar o corpo da função.")
                    else:
                        self.error_sintatico("Esperado ')' para fechar a lista de parâmetros.")
                else:
                    self.error_sintatico("Esperado '(' para iniciar a lista de parâmetros.")
            else:
                self.error_sintatico("Esperado identificador da função.")
        return False
        
    def bloco_com_retorno(self, expected_return_type):
        """Processa um bloco verificando declarações de retorno."""
        has_return = False

        while self.current_token():
            token = self.current_token()
            
            if token.tipo == "RCBRACK":
                return True
                
            if token.tipo == "FIM":
                return True  # Final do programa, não precisa de SEMICOLON

            if self.match("RETURN"):
                if expected_return_type == "void":
                    self.error_semantico("Função void não pode retornar valor.")

                expr_type, expr_temp = self.expressao()
                if expr_type != expected_return_type:
                    self.error_semantico(f"Tipo de retorno inválido: esperado '{expected_return_type}', encontrado '{expr_type}'.")

                self.emit(f"return {expr_temp}")

                # Só exige ponto e vírgula se não for o último comando do bloco
                if self.current_token() and self.current_token().tipo != "RCBRACK":
                    if not self.match("SEMICOLON"):
                        self.error_sintatico("Esperado ';' após o retorno.")

                # Marca que encontrou um retorno
                self.scope_stack[-1]["_has_return"] = True
                has_return = True
                continue

            # Processa outras declarações normalmente
            if self.declaracao_variavel():
                continue
            elif self.comando_condicional_com_retorno(expected_return_type):
                # Verifica se o comando condicional tem retorno em ambos os ramos
                if self.scope_stack[-1].get("_has_return", False):
                    has_return = True
                continue
            elif self.comando_enquanto():
                continue
            elif self.chamada_procedimento():
                continue
            elif self.chamada_funcao():
                if not self.match("SEMICOLON"):
                    self.error_sintatico("Esperado ';' após a chamada da função.")
                continue
            elif self.comando_impressao():
                continue
            elif self.desvio_incondicional():
                continue
            else:
                break

        # Verifica se o bloco tem retorno em todos os caminhos (se necessário)
        if expected_return_type != "void" and not has_return:
            self.error_semantico(f"Função não retorna valor em todos os caminhos.")

        return has_return

    def comando_condicional_com_retorno(self, expected_return_type):
        """Processa if/else verificando retorno em ambos os ramos."""
        if self.match("IF"):
            if self.match("LBRACK"):
                expr_type, expr_temp = self.expressao()
                if expr_type != "boolean":
                    self.error_semantico(f"Condição do 'if' deve ser do tipo 'boolean', encontrado '{expr_type}'.")
                
                false_label = self.new_label()
                end_label = self.new_label()
                
                self.emit(f"ifFalse {expr_temp} goto {false_label}")
                
                if self.match("RBRACK"):
                    if self.match("LCBRACK"):
                        # Processa bloco do if
                        if_has_return = self.bloco_com_retorno(expected_return_type)
                        if self.match("RCBRACK"):
                            # Processa else se existir
                            else_has_return = self.else_opcional_com_retorno(expected_return_type, end_label)
                            
                            # Se ambos os ramos têm retorno, marca como tendo retorno
                            if if_has_return and else_has_return:
                                self.scope_stack[-1]["_has_return"] = True
                            return True
                        else:
                            self.error_sintatico("Esperado '}' para fechar o bloco do 'if'.")
                    else:
                        self.error_sintatico("Esperado '{' para iniciar o bloco do 'if'.")
                else:
                    self.error_sintatico("Esperado ')' para fechar a condição do 'if'.")
            else:
                self.error_sintatico("Esperado '(' para abrir a condição do 'if'.")
        return False

    def else_opcional_com_retorno(self, expected_return_type, end_label=None):
        """Processa else verificando retorno."""
        if self.match("ELSE"):
            if self.match("LCBRACK"):
                else_has_return = self.bloco_com_retorno(expected_return_type)
                if not self.match("RCBRACK"):
                    self.error_sintatico("Esperado '}' para fechar o bloco do 'else'.")
                return else_has_return
            else:
                self.error_sintatico("Esperado '{' para abrir o bloco do 'else'.")
        return False

    def lista_parametros(self):
        """Processa a lista de parâmetros marcando-os como inicializados."""
        params = []
        if self.match("RBRACK"):  # Caso não haja parâmetros
            return params
        
        tipo = self.especificador_tipo()
        if not tipo:
            self.error_sintatico("Esperado tipo do parâmetro.")
        
        if self.match("ID_VAR"):
            param_name = self.tokens[self.current - 1].lexema
            self.add_symbol(param_name, tipo, is_param=True)  # Marca como parâmetro
            params.append({"type": tipo})
            
            while self.match("COMMA"):
                tipo = self.especificador_tipo()
                if not tipo:
                    self.error_sintatico("Esperado tipo do parâmetro.")
                
                if self.match("ID_VAR"):
                    param_name = self.tokens[self.current - 1].lexema
                    self.add_symbol(param_name, tipo, is_param=True)  # Marca como parâmetro
                    params.append({"type": tipo})
                else:
                    self.error_sintatico("Esperado identificador do parâmetro.")
        
        return params
    def declaracao_parametro(self):
        """Processa a declaração de um parâmetro."""
        tipo = self.especificador_tipo()
        if not tipo:
            self.error_sintatico("Esperado tipo do parâmetro.")
        
        if self.match("ID_VAR"):
            param_name = self.tokens[self.current - 1].lexema
            self.add_symbol(param_name, tipo)
            return True
        return False

    def expressao(self):
        """Processa uma expressão."""
        return self.expressao_logica()

    def expressao_logica(self):
        """Processa uma expressão lógica com verificação de tipos comparáveis."""
        left_type, left_temp = self.expressao_aditiva()
        token = self.current_token()
        
        if token and token.tipo in ["EQUAL", "NOTEQUAL", "LESS", "LESSEQUAL", "GREAT", "GREATEQUAL"]:
            op = token.tipo
            self.match(token.tipo)
            right_type, right_temp = self.expressao_aditiva()
            
            # Verificação explícita de tipos comparáveis
            if left_type != right_type:
                self.error_semantico(f"Tipos incompatíveis na expressão: '{left_type}' e '{right_type}'.")
            
            # Verificação de operadores específicos para tipos numéricos
            if op in ["LESS", "LESSEQUAL", "GREAT", "GREATEQUAL"]:
                if left_type != "int":
                    self.error_semantico(f"Operador '{op}' requer operandos do tipo 'int', encontrado '{left_type}'.")
            
            # Operadores de igualdade/diferença podem ser usados com booleanos ou inteiros
            elif op in ["EQUAL", "NOTEQUAL"]:
                if left_type not in ["int", "boolean"]:
                    self.error_semantico(f"Operador '{op}' requer operandos do tipo 'int' ou 'boolean', encontrado '{left_type}'.")
            
            result_temp = self.new_temp()
            op_map = {
                "EQUAL": "==",
                "NOTEQUAL": "!=",
                "LESS": "<",
                "LESSEQUAL": "<=",
                "GREAT": ">",
                "GREATEQUAL": ">="
            }
            self.emit(f"{result_temp} = {left_temp} {op_map[op]} {right_temp}")
            return "boolean", result_temp
        return left_type, left_temp

    def expressao_aditiva(self):
        """Processa uma expressão aditiva (+, -)."""
        left_type, left_temp = self.expressao_multiplicativa()
        token = self.current_token()
        while token and token.tipo in ["SUM", "SUB"]:
            op = token.tipo
            self.match(token.tipo)
            right_type, right_temp = self.expressao_multiplicativa()
            if left_type != "int" or right_type != "int":
                self.error_semantico(f"Operação aritmética requer operandos do tipo 'int', encontrado '{left_type}' e '{right_type}'.")
            
            result_temp = self.new_temp()
            op_map = {"SUM": "+", "SUB": "-"}
            self.emit(f"{result_temp} = {left_temp} {op_map[op]} {right_temp}")
            
            left_type = "int"
            left_temp = result_temp
            token = self.current_token()
        return left_type, left_temp

    def expressao_multiplicativa(self):
        """Processa uma expressão multiplicativa (*, /, %)."""
        left_type, left_temp = self.termo()
        token = self.current_token()
        while token and token.tipo in ["MUL", "DIV", "MOD"]:
            op = token.tipo
            self.match(token.tipo)
            right_type, right_temp = self.termo()
            if left_type != "int" or right_type != "int":
                self.error_semantico(f"Operação multiplicativa requer operandos do tipo 'int', encontrado '{left_type}' e '{right_type}'.")
            
            result_temp = self.new_temp()
            op_map = {"MUL": "*", "DIV": "/", "MOD": "%"}
            self.emit(f"{result_temp} = {left_temp} {op_map[op]} {right_temp}")
            
            left_type = "int"
            left_temp = result_temp
            token = self.current_token()
        return left_type, left_temp

    def termo(self):
        """Processa um termo (número, variável, chamada de função ou valor booleano)."""
        token = self.current_token()
        if token.tipo == "NUMBER":
            value = token.lexema
            self.match("NUMBER")
            temp = self.new_temp()
            self.emit(f"{temp} = {value}")
            return "int", temp
        elif token.tipo == "TRUE" or token.tipo == "FALSE":
            value = token.lexema.lower()
            self.match(token.tipo)
            temp = self.new_temp()
            self.emit(f"{temp} = {value}")
            return "boolean", temp
        elif token.tipo == "ID_VAR":
            var_name = token.lexema
            var_type = self.get_symbol_type(var_name)
            self.match("ID_VAR")
            return var_type, var_name
        elif token.tipo == "ID_FUNC":
            # Chamada de função como parte de uma expressão
            func_type, func_temp = self.chamada_funcao()
            if func_type:
                return func_type, func_temp
        self.error_sintatico(f"Esperado número, variável ou chamada de função, encontrado '{token.lexema}'.")
        
    def chamada_funcao(self):
        """Processa uma chamada de função e retorna o tipo de retorno e o temporário."""
        if self.match("ID_FUNC"):
            func_name = self.tokens[self.current - 1].lexema
            if func_name in self.function_params:
                func_info = self.function_params[func_name]
                if self.match("LBRACK"):
                    expected_params = func_info["param_types"]
                    actual_args = self.lista_argumentos()
                    
                    # Verificação semântica: número de parâmetros
                    if len(actual_args) != len(expected_params):
                        self.error_semantico(f"Número incorreto de argumentos para '{func_name}'. Esperado {len(expected_params)}, encontrado {len(actual_args)}")
                    
                    # Verificação semântica: tipos dos parâmetros
                    for i, ((arg_type, _), expected_type) in enumerate(zip(actual_args, expected_params)):
                        if arg_type != expected_type:
                            self.error_semantico(f"Tipo incorreto para argumento {i+1} em '{func_name}'. Esperado {expected_type}, encontrado {arg_type}")
                    
                    # Emitir chamada de função
                    result_temp = self.new_temp()
                    args_str = ", ".join([arg[1] for arg in actual_args])
                    self.emit(f"{result_temp} = call {func_name}, {args_str}")
                    
                    if not self.match("RBRACK"):
                        self.error_sintatico("Esperado ')' após argumentos da função")
                    
                    # Verificação semântica: resultado não utilizado
                    next_token = self.current_token()
                    if next_token and next_token.tipo != "SEMICOLON":
                        print(f"[Aviso Semântico] Resultado da função '{func_name}' não utilizado")
                    
                    return func_info["return_type"], result_temp
                else:
                    self.error_sintatico("Esperado '(' após nome da função")
            else:
                self.error_semantico(f"Função '{func_name}' não declarada")
        return None, None
    
    def lista_argumentos(self):
        """Processa a lista de argumentos de uma função e retorna uma lista de tuplas (tipo, temp)."""
        if self.match("RBRACK"):  # Caso não haja argumentos
            return []
        
        args = []
        expr_type, expr_temp = self.expressao()
        # Verifica se é uma variável declarada ou uma temporária válida
        if not (expr_temp.startswith('t') or self.get_symbol_type(expr_temp) if not expr_temp.startswith('t') else True):
            self.error_semantico(f"Argumento inválido: {expr_temp}")
        args.append((expr_type, expr_temp))
        while self.match("COMMA"):
            expr_type, expr_temp = self.expressao()
            args.append((expr_type, expr_temp))
        return args

    def declaracao_procedimento(self):
        """Processa a declaração de um procedimento."""
        if self.match("PROC"):
            if self.match("ID_PROC"):
                proc_name = self.tokens[self.current - 1].lexema
                self.enter_scope()  # Entra no escopo do procedimento

                if self.match("LBRACK"):
                    params = self.lista_parametros()
                    self.procedure_params[proc_name] = [param["type"] for param in params]
                    if self.match("RBRACK"):
                        if self.match("LCBRACK"):
                            # Processa o bloco até encontrar RCBRACK
                            while self.current_token() and self.current_token().tipo != "RCBRACK":
                                if not (self.declaracao_variavel() or 
                                        self.comando_condicional() or 
                                        self.comando_enquanto() or 
                                        self.comando_impressao() or 
                                        self.atribuicao_variavel() or 
                                        self.desvio_incondicional()):
                                    self.error_sintatico(f"Comando inválido no procedimento: {self.current_token().lexema}")
                            
                            if self.match("RCBRACK"):
                                self.exit_scope()
                                return True
                            else:
                                self.error_sintatico("Esperado '}' para fechar o corpo do procedimento.")
                        else:
                            self.error_sintatico("Esperado '{' para iniciar o corpo do procedimento.")
                    else:
                        self.error_sintatico("Esperado ')' para fechar a lista de parâmetros.")
                else:
                    self.error_sintatico("Esperado '(' para iniciar a lista de parâmetros.")
            else:
                self.error_sintatico("Esperado identificador do procedimento.")
        return False
    
    def chamada_procedimento(self):
        """Processa uma chamada de procedimento."""
        if self.match("ID_PROC"):
            proc_name = self.tokens[self.current - 1].lexema
            if self.match("LBRACK"):
                expected_params = self.get_procedure_params(proc_name)
                actual_args = self.lista_argumentos()
                if len(actual_args) != len(expected_params):
                    self.error_semantico(f"Número incorreto de argumentos para o procedimento '{proc_name}'. Esperado {len(expected_params)}, encontrado {len(actual_args)}.")
                
                # Correção: Extrai apenas o tipo (arg_type) de cada tupla em actual_args
                for i, ((arg_type, _), param_type) in enumerate(zip(actual_args, expected_params)):
                    if arg_type != param_type:
                        self.error_semantico(f"Tipo incorreto para o argumento {i + 1} no procedimento '{proc_name}'. Esperado '{param_type}', encontrado '{arg_type}'.")
                
                if self.match("RBRACK"):
                    return True
                else:
                    self.error_sintatico("Esperado ')' para fechar os argumentos do procedimento.")
            else:
                self.error_sintatico("Esperado '(' para iniciar os argumentos do procedimento.")
        return False
    
    def desvio_incondicional(self):
        """Processa comandos de desvio incondicional (break, continue)."""
        if self.match("BREAK") or self.match("CONTINUE"):
            if self.loop_depth == 0:
                self.error_sintatico("'break' e 'continue' só podem ser usados dentro de loops.")
            if self.match("SEMICOLON"):
                return True
            else:
                self.error_sintatico("Esperado ';' após 'break' ou 'continue'.")
        return False
    

    def get_procedure_params(self, proc_name):
        """Retorna uma lista com os tipos dos parâmetros do procedimento."""
        if proc_name in self.procedure_params:
            return self.procedure_params[proc_name]
        self.error_semantico(f"Procedimento '{proc_name}' não declarado.")
        return []

    def get_function_params(self, func_name):
        """Retorna uma lista com os tipos dos parâmetros da função."""
        if func_name in self.function_params:
            return self.function_params[func_name]
        self.error_semantico(f"Função '{func_name}' não declarada.")
        return []
