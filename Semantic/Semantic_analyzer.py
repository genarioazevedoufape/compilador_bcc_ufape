class SemanticAnalyzer:
    def __init__(self, tokens, symbol_table):
        self.tokens = tokens
        self.symbol_table = symbol_table
        self.current = 0
        self.loop_depth = 0
        self.function_context = None
        self.function_return_type = {}  # Mapeia funções para seus tipos de retorno
    
    def current_token(self):
        return self.tokens[self.current] if self.current < len(self.tokens) else None
    
    def next_token(self):
        self.current += 1
    
    def analyze(self):
        while self.current < len(self.tokens):
            token = self.current_token()
            if token.tipo == "TYPE_INT" or token.tipo == "TYPE_BOOLEAN":
                self.declare_variable()
            elif token.tipo == "ID_VAR":
                self.check_variable_usage()
            elif token.tipo == "FUNC":
                self.declare_function()
            elif token.tipo == "PROC":
                self.declare_procedure()
            elif token.tipo in ["BREAK", "CONTINUE"]:
                self.check_loop_control()
            elif token.tipo == "RETURN":
                self.check_return_statement()
            self.next_token()
    
    def declare_variable(self):
        var_type = self.current_token().tipo  # Armazena o tipo da variável
        self.next_token()
        if self.current_token().tipo == "ID_VAR":
            var_name = self.current_token().lexema
            if var_name in self.symbol_table:
                raise ValueError(f"Erro Semântico: Variável '{var_name}' já declarada.")
            self.symbol_table[var_name] = var_type  # Armazena o tipo da variável
        else:
            raise ValueError("Erro Semântico: Esperado identificador de variável.")
    
    def check_variable_usage(self):
        var_name = self.current_token().lexema
        if var_name not in self.symbol_table:
            raise ValueError(f"Erro Semântico: Variável '{var_name}' não declarada.")
    
    def declare_function(self):
        func_type = self.current_token().tipo  # Obtém o tipo de retorno da função
        self.next_token()
        if self.current_token().tipo == "ID_FUNC":
            func_name = self.current_token().lexema
            if func_name in self.symbol_table:
                raise ValueError(f"Erro Semântico: Função '{func_name}' já declarada.")
            self.symbol_table[func_name] = "FUNC"
            self.function_return_type[func_name] = func_type  # Armazena o tipo de retorno da função
            self.function_context = func_name
        else:
            raise ValueError("Erro Semântico: Esperado identificador de função.")
    
    def check_return_statement(self):
        if self.function_context is None:
            raise ValueError("Erro Semântico: 'return' fora de função.")
        expected_type = self.function_return_type.get(self.function_context)
        self.next_token()
        return_value = self.current_token()
        if return_value.tipo != expected_type:
            raise ValueError(f"Erro Semântico: Retorno inválido em '{self.function_context}', esperado {expected_type} mas encontrado {return_value.tipo}.")
    
    def declare_procedure(self):
        self.next_token()
        if self.current_token().tipo == "ID_PROC":
            proc_name = self.current_token().lexema
            if proc_name in self.symbol_table:
                raise ValueError(f"Erro Semântico: Procedimento '{proc_name}' já declarado.")
            self.symbol_table[proc_name] = "PROC"
        else:
            raise ValueError("Erro Semântico: Esperado identificador de procedimento.")
    
    def check_loop_control(self):
        if self.loop_depth == 0:
            raise ValueError("Erro Semântico: 'break' ou 'continue' usados fora de um loop.")
