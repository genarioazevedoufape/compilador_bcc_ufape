from Lexer.Scanner import Scanner
from Parser.Parser import Parser
from Semantic.Semantic_analyzer import SemanticAnalyzer

def Main():
    try:
        with open('teste.txt', 'r') as file:
            codigo_exemplo = file.read()
    except FileNotFoundError:
        print("Arquivo 'teste.txt' não encontrado!")
        return

    print("=== Código de Entrada ===")
    print(codigo_exemplo)
    print("=========================")
  
    scanner = Scanner(codigo_exemplo)

    try:
        tokens = scanner.scan()
    except Exception as e:
        print(f"Erro ao escanear o código: {e}")
        return

    print("=== Tokens Gerados ===")
    for token in tokens:
        print(token)
    print("======================")

    parser = Parser(tokens)

    try:
        parser.parse()
        print("\nAnálise Sintática concluída com sucesso!")
    except SyntaxError as e:
        print(f"Erro de sintaxe: {e}")
        return 
    
    symbol_table = scanner.symbol_table  # Passando a tabela de símbolos para a análise semântica
    analyzer = SemanticAnalyzer(tokens, symbol_table)

    try:
        analyzer.analyze()
        print("\nAnálise Semântica concluída com sucesso!")
    except ValueError as e:
        print(f"Erro Semântico: {e}")
        return

if __name__ == "__main__":
    Main()
