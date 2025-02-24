from Lexer.Scanner import Scanner
from Parser.Parser import Parser

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


if __name__ == "__main__":
    Main()