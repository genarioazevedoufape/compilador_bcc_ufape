from Lexer.Scanner import Scanner
from Parser.Parser import Parser

def Main():
    # Código de exemplo que será analisado
    codigo_exemplo = """
    int v1 = 10;
    if (v1 > 5) {
        print v1;
    } else {
        print 0;
    }
    """
    print("=== Código de Exemplo ===")
    print(codigo_exemplo)
    print("=========================\n")

    # Criar uma instância do Scanner
    scanner = Scanner(codigo_exemplo)

    # Realizar a análise léxica
    try:
        tokens = scanner.scan()
    except Exception as e:
        print(f"Erro ao escanear o código: {e}")
        return

    # Exibir os tokens gerados
    print("=== Tokens Gerados ===")
    for token in tokens:
        print(token)
    print("======================")

    # Criar uma instância do Parser
    parser = Parser(tokens)

    # Realizar a análise sintática
    try:
        parser.parse()
        print("\nAnálise sintática concluída com sucesso!")
    except SyntaxError as e:
        print(f"Erro de sintaxe: {e}")

if __name__ == "__main__":
    Main()
