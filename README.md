Aqui está a versão atualizada do seu README com a seção de **Análise Semântica** incluída:

---

# Projeto de Compiladores - 2024.2  
***
## Ferramenta de Análise Léxica, Sintática e Semântica  

**Curso**: Ciência da Computação da Universidade Federal do Agreste de Pernambuco  
**Autores**: Genário Azevedo e João Victor Iane  
***
## Descrição do Projeto  
Este projeto é uma ferramenta de análise léxica, sintática e semântica desenvolvida para a disciplina de Compiladores. A ferramenta realiza a análise de programas escritos em uma linguagem simples, identificando tokens, verificando a estrutura gramatical e garantindo a correção semântica do código. Desenvolvido conforme orientação da Prof. Dra. Maria Aparecida A. Sibaldo.  

---

## Componentes Principais  

### 1. **Análise Léxica (Lexer)**  
   - Identifica e classifica tokens como:  
     - **Palavras reservadas**: `if`, `else`, `while`, `print`, etc.  
     - **Tipos de dados**: `int`, `boolean`.  
     - **Identificadores**: `variáveis`, `funções`, `procedimentos`.  
     - **Operadores**: `+`, `-`, `*`, `/`, `=`, `!=`, `<`, `<=`, `>`, `>=`.  
     - **Delimitadores**: `(`, `)`, `{`, `}`, `;`, `,`.  
   - Implementação: Classe `Scanner` e representação de tokens via classe `Token`.  

### 2. **Análise Sintática (Parser)**  
   - Verifica se a sequência de tokens segue as regras gramaticais definidas.  
   - Reconhece estruturas como:  
     - Declarações de variáveis (`int x = 10;`).  
     - Condicionais (`if`, `else`).  
     - Laços (`while`).  
     - Declarações e chamadas de funções/procedimentos.  
     - Comandos de impressão (`print`).  
     - Expressões aritméticas e lógicas.  
   - Implementação: Classe `Parser` com métodos recursivos para interpretação da gramática.  

### 3. **Análise Semântica**  
   - Realiza verificações de contexto para garantir a validade do código:  
     - **Declaração e Escopo**:  
       - Verifica se identificadores (variáveis, funções, procedimentos) estão declarados antes do uso.  
       - Controla escopos aninhados (global, funções, procedimentos).  
       - Garante que variáveis não sejam redeclaradas no mesmo escopo.  
     - **Tipos de Dados**:  
       - Valida compatibilidade em operações aritméticas (`+`, `-`, `*`, `/`, `%`) e lógicas (`==`, `!=`, `<`, `>`, etc.).  
       - Verifica se condições em `if` e `while` são do tipo `boolean`.  
       - Garante que o tipo de retorno de funções corresponda à declaração.  
     - **Atribuições**:  
       - Valida compatibilidade entre o tipo da variável e o valor atribuído.  
     - **Funções e Procedimentos**:  
       - Verifica número e tipos dos argumentos em chamadas.  
       - Garante que funções tenham retorno em todos os caminhos possíveis.  
     - **Inicialização**:  
       - Detecta uso de variáveis não inicializadas.  
     - **Controle de Fluxo**:  
       - Valida comandos `break` e `continue` apenas dentro de loops.  

---

## Gramática  
- A gramática utilizada está definida no arquivo [gramatica.bnf](./gramatica.bnf).  

---

## Estrutura do Projeto  
```markdown
/Lexer  
  Token.py         # Classe para representar tokens  
  Scanner.py       # Implementação do analisador léxico  

/Parser  
  Parser.py        # Implementação do analisador sintático e semântico  
  gramatica.bnf    # Gramática formal da linguagem  

Main.py            # Script principal para execução da ferramenta  
```

--- 

## Como Executar  
1. Clone o repositório.  
2. Execute `Main.py` com o arquivo de código-fonte a ser analisado.  
3. A saída exibirá tokens, árvore sintática e erros (léxicos, sintáticos ou semânticos).  

