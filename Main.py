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
        print(f"Tipo: {token.tipo}, Lexema: '{token.lexema}', Linha: {token.linha}")
    print("======================")

    parser = Parser(tokens)

    try:
        three_address_code = parser.parse()
        
        if three_address_code is not None:
            print("\n=== Código de Três Endereços Gerado ===")
            for instruction in three_address_code:
                print(instruction)
            print("=======================================")
            
            with open('codigo_3endercos.txt', 'w') as f:
                for instruction in three_address_code:
                    f.write(instruction + '\n')
            
    except SyntaxError as e:
        print(f"Erro de sintaxe: {e}")
        return  
    except Exception as e:
        print(f"Erro semântico: {e}")
        return  

if __name__ == "__main__":
    Main()