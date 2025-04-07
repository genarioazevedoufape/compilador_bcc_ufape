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
    print("=========================\n\n")
  
    scanner = Scanner(codigo_exemplo)

    try:
        tokens = scanner.scan()
    except Exception as e:
        print(f"Erro ao escanear o código: {e}")
        return

    # print("=== Tokens Gerados ===")
    # for token in tokens:
    #     print(f"Tipo: {token.tipo}, Lexema: '{token.lexema}', Linha: {token.linha}")
    # print("======================")

    parser = Parser(tokens)

    try:
        parser = Parser(tokens)
        success = parser.parse()
        
        if success:
            # print("\n=== Código de Três Endereços Otimizado ===")
            formatted_code = parser.get_formatted_code()
            # print(formatted_code)
            
            # Salva em arquivo
            with open('3aderecos.txt', 'w') as f:
                f.write(formatted_code)
            
    except SyntaxError as e:
        print(f"Erro de sintaxe: {e}")
        return
    except Exception as e:
        print(f"Erro semântico: {e}")
        return

if __name__ == "__main__":
    Main()