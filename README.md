Ferramenta de Análise Léxica e Sintática

Disciplina: Compiladores  
Curso: Ciência da Computação - UFAPE  
Autores: Genário Azevedo e João Victor Iane

Descrição do Projeto
Este projeto é uma ferramenta de análise léxica e sintática desenvolvida para a disciplina de Compiladores. A ferramenta realiza a análise de programas escritos em uma linguagem simples, identificando tokens e verificando sua conformidade com as regras gramaticais especificadas.  

Componentes principais
1. Análise Léxica (Lexer):  
   - Identifica e classifica tokens como palavras reservadas, identificadores, operadores e outros símbolos presentes no programa.
   - Implementado na classe `Scanner`.
   - Utiliza a classe `Token` para representar os tokens gerados.

2. Análise Sintática (Parser):  
   - Verifica se a sequência de tokens segue as regras gramaticais definidas.
   - Implementado na classe `Parser`, que utiliza um conjunto de métodos recursivos para interpretar diferentes partes da gramática.

Funcionalidades
- Análise Léxica:
  - Gera tokens para:
    - **Palavras reservadas**: `if`, `else`, `while`, `print`, etc.
    - **Tipos de dados**: `int`, `boolean`.
    - **Identificadores**: `variáveis`, `funções`, `procedimentos`.
    - **Operadores**: `+`, `-`, `*`, `/`, `=`, `!=`, `<`, `<=`, `>`, `>=`.
    - **Delimitadores**: `(`, `)`, `{`, `}`, `;`, `,`.
  - Representação de tokens via classe `Token`.

- *Análise Sintática*:
  - Reconhece comandos como:
    - Declarações de variáveis (`int x = 10;`).
    - Condicionais (`if`, `else`).
    - Laços (`while`).
    - Declarações e chamadas de funções e procedimentos.
    - Comandos de impressão (`print`).
    - Expressões aritméticas e lógicas.

- Gramática:
  - A gramática utilizada está definida no arquivo [gramatica.bnf](./gramatica.bnf).

Estrutura do Projeto(Falta)
