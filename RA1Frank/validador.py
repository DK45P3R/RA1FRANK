import sys
import re

# ========================
# Função para ler o arquivo
# ========================
def ler_arquivo(caminho):
    with open(caminho, 'r', encoding='utf-8') as f:
        linhas = f.read().splitlines()

    if not linhas:
        raise ValueError("O arquivo está vazio.")

    try:
        n = int(linhas[0])
    except ValueError:
        raise ValueError("A primeira linha do arquivo deve conter um número inteiro.")

    expressoes = linhas[1:]
    if len(expressoes) != n:
        raise ValueError(f"Número de expressões ({len(expressoes)}) não corresponde ao indicado ({n}).")

    return expressoes

# ========================
# Analisador Léxico
# ========================
TOKENS = {
    '\\neg': 'NOT',
    '\\wedge': 'AND',
    '\\vee': 'OR',
    '\\rightarrow': 'IMPLIES',
    '\\leftrightarrow': 'IFF',
    '(': 'LPAREN',
    ')': 'RPAREN',
    'true': 'TRUE',
    'false': 'FALSE'
}

def eh_proposicao(token):
    return re.fullmatch(r'[0-9][0-9a-z]*', token) is not None

def analisador_lexico(expr):
    tokens = []
    i = 0
    while i < len(expr):
        if expr[i].isspace():
            i += 1
            continue

        # Checar operadores e constantes
        for k in sorted(TOKENS, key=lambda x: -len(x)):
            if expr.startswith(k, i):
                tokens.append((TOKENS[k], k))
                i += len(k)
                break
        else:
            # Se não for operador, pode ser proposição
            match = re.match(r'[0-9][0-9a-z]*', expr[i:])
            if match:
                prop = match.group(0)
                tokens.append(('ID', prop))
                i += len(prop)
            else:
                return None  # erro léxico
    return tokens

# ========================
# Parser LL(1)
# ========================
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def consumir(self, tipo):
        if self.pos < len(self.tokens) and self.tokens[self.pos][0] == tipo:
            self.pos += 1
            return True
        return False

    def FORMULA(self):
        if self.pos >= len(self.tokens):
            return False

        tipo, _ = self.tokens[self.pos]

        if tipo in ['TRUE', 'FALSE']:
            return self.consumir(tipo)
        elif tipo == 'ID':
            return self.consumir('ID')
        elif tipo == 'LPAREN':
            self.consumir('LPAREN')
            if self.OPERADORUNARIO():
                if self.FORMULA():
                    return self.consumir('RPAREN')
            elif self.OPERADORBINARIO():
                if self.FORMULA() and self.FORMULA():
                    return self.consumir('RPAREN')
        return False

    def OPERADORUNARIO(self):
        return self.consumir('NOT')

    def OPERADORBINARIO(self):
        return self.consumir('AND') or self.consumir('OR') or \
               self.consumir('IMPLIES') or self.consumir('IFF')

    def parse(self):
        return self.FORMULA() and self.pos == len(self.tokens)

# ========================
# Função principal
# ========================
def main():
    if len(sys.argv) != 2:
        print("Uso: python validador.py <arquivo.txt>")
        return

    try:
        expressoes = ler_arquivo(sys.argv[1])
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return

    for expr in expressoes:
        tokens = analisador_lexico(expr)
        if tokens is None:
            print("inválida")
            continue
        parser = Parser(tokens)
        print("valida" if parser.parse() else "inválida")

# ========================
# Executar
# ========================
if __name__ == "__main__":
    main()
