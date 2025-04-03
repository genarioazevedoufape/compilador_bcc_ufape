
# Projeto de Compiladores - 2024.2  
***
## Ferramenta de Análise Léxica, Sintática e Semântica  

**Curso**: Ciência da Computação da Universidade Federal do Agreste de Pernambuco  
**Autores**: Genário Azevedo e João Victor Iane  
**Orientadora**: Prof. Dra. Maria Aparecida A. Sibaldo  

***
## Descrição do Projeto  
Este projeto é uma ferramenta completa de análise léxica, sintática e semântica desenvolvida para a disciplina de Compiladores. A ferramenta realiza:

1. Análise léxica (identificação de tokens)
2. Análise sintática (verificação da estrutura gramatical)
3. Análise semântica (verificação de tipos, escopo e outras regras contextuais)
4. Geração de código intermediário (código de três endereços)

A ferramenta processa programas escritos em uma linguagem simples desenvolvida em sala, com suporte a declarações de variáveis, estruturas condicionais, loops, funções e procedimentos.

***
## Componentes Principais  

### 1. Análise Léxica (Scanner)
- **Responsabilidade**: Converter o código fonte em tokens
- **Tokens reconhecidos**:
  - Palavras-chave: `if`, `else`, `while`, `break`, `continue`, `print`, `func`, `proc`, `return`
  - Tipos: `int`, `boolean`
  - Identificadores: 
    - `v...` para variáveis (ID_VAR)
    - `f...` para funções (ID_FUNC) 
    - `p...` para procedimentos (ID_PROC)
  - Operadores: 
    - Aritméticos: `+`, `-`, `*`, `/`, `%`
    - Relacionais: `==`, `!=`, `<`, `<=`, `>`, `>=`
    - Atribuição: `=`
  - Delimitadores: `(`, `)`, `{`, `}`, `;`, `,`

### 2. Análise Sintática (Parser)
- **Responsabilidade**: Verificar a estrutura gramatical do programa
- **Estruturas reconhecidas**:
  - Declarações de variáveis (`int x = 10;`)
  - Estruturas condicionais (`if-else`)
  - Loops (`while`)
  - Funções e procedimentos
  - Chamadas de função/procedimento
  - Expressões aritméticas e lógicas
  - Comandos `break`, `continue` e `return`

### 3. Análise Semântica
- **Responsabilidade**: Verificar as regras contextuais da linguagem
- **Verificações implementadas**:
  - **Escopo e declarações**:
    - Variáveis/funções declaradas antes do uso
    - Sem declarações duplicadas no mesmo escopo
    - Controle de escopo aninhado (global, funções, procedimentos)
  
  - **Tipos**:
    - Compatibilidade em operações aritméticas (ambos operandos devem ser `int`)
    - Compatibilidade em operações lógicas (ambos operandos devem ser `boolean`)
    - Condições de `if` e `while` devem ser `boolean`
    - Tipo de retorno de funções deve corresponder à declaração
  
  - **Atribuições**:
    - Tipo do valor atribuído deve corresponder ao tipo da variável
  
  - **Funções/procedimentos**:
    - Número e tipos de parâmetros nas chamadas
    - Funções devem retornar valor em todos os caminhos possíveis
    - Procedimentos não podem retornar valores
  
  - **Outras verificações**:
    - `break`/`continue` só podem aparecer dentro de loops
    - Detecção de variáveis não inicializadas
    - Detecção de variáveis declaradas mas não utilizadas

### 4. Geração de Código Intermediário
- **Responsabilidade**: Gerar código de três endereços otimizado
- **Características**:
  - Uso de temporários para expressões complexas
  - Labels para controle de fluxo
  - Chamadas a funções/procedimentos
  - Otimizações básicas (eliminação de código redundante)

***
## Estrutura do Projeto  

```
/Lexer
  Token.py         # Classe para representação de tokens
  Scanner.py       # Implementação do analisador léxico

/Parser
  Parser.py        # Implementação do analisador sintático/semântico
  gramatica.bnf    # Gramática formal da linguagem

Main.py            # Ponto de entrada do programa
teste.txt          # Arquivo de exemplo para análise
3aderecos.txt      # Saída com código de três endereços gerado
```

***
## Como Executar  

1. **Pré-requisitos**:
   - Python 3.x instalado

2. **Execução**:
   ```bash
   python Main.py
   ```

3. **Arquivos**:
   - Edite `teste.txt` para incluir seu código fonte
   - O resultado da análise será exibido no terminal
   - O código de três endereços gerado será salvo em `3aderecos.txt`

4. **Exemplo de Saída**:
   - Listagem de tokens identificados
   - Erros encontrados (léxicos, sintáticos ou semânticos)
   - Código de três endereços gerado (se a análise for bem-sucedida)

***
## Exemplos de Código Válido  

```c
int vA = 7;
int vB = 15;

func int fSomar(int v1, int v2) {
    return v1 + v2;
}

func boolean fEhPar(int vNumero) {
    return vNumero % 2 == 0;
}

func int fMultiplicar(int vNumero) {
    return vNumero * 2;
}

proc pContador(int vInicio, int vFim) {
    while (vInicio <= vFim) {
        print vInicio;
        vInicio = vInicio + 1;
    }
}

pContador(1, 5);
```
***
## Referências  

1. Aho, A. V. et al. Compiladores: Princípios, Técnicas e Ferramentas. 2ª edição.
2. Appel, A. W. Modern Compiler Implementation in Java. 2ª edição.
3. Material da disciplina de Compiladores - UFAPE 2024.2