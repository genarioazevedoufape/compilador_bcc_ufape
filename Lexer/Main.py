from Scanner import Scanner
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python Main.py <arquivo_fonte>")
        sys.exit(1)

    path = sys.argv[1]

    try:
        with open(path, 'r') as fonte:
            programa = fonte.read()
    except FileNotFoundError:
        print("Erro: Código Fonte não encontrado")
        sys.exit(1)

    lexer = Scanner(programa)
    tabTokens = lexer.scan()

    for token in tabTokens:
        print(token)
