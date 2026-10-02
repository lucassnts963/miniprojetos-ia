"""Carrossel "IA sem mistério", parte 2 — por que a IA erra contas: ela não lê palavras, lê pedaços.

Os cortes das palavras são reais: vêm do cortador de texto do projeto 06 (06-completar-texto/modelo/pedacos.json).
Cada IA tem o seu jeito de cortar; os cortes de uma IA comercial são outros, mas a ideia é a mesma.
A frase do rodapé também aparece cortada em pedaços, atravessando os 8 quadros.

    C:/dev/venv/Scripts/python.exe posts/serie_ia/parte2.py   ->  posts/serie_ia/parte2/
"""
import os
import sys

from base import (BODY, CARD, CINZA, FG, LADO, LINE, MARGEM, MUTE, NADA, RAIZ, RED, RED_SOFT, VERDE, VINHO, caixa, chip,
                  chips, corpo, fundo_e_fio, larg, rotulo, salvar, texto, titulo, topo)

sys.path.insert(0, os.path.join(RAIZ, "06-completar-texto"))
from pedacos import Pedacos  # noqa: E402

PED = Pedacos.abrir(os.path.join(RAIZ, "06-completar-texto", "modelo", "pedacos.json"))
AZUL = (38, 62, 96)


def cortar(t):
    """-> [(pedaço sem o espaço da frente, número do pedaço, começa palavra nova?)]"""
    ids = PED.codificar(t)
    return [(PED.vocab[i].strip(), i, PED.vocab[i].startswith(" ") or n == 0) for n, i in enumerate(ids)]


def blocos(t, tam, x, y, largura=912):
    """A frase cortada: pedaços da mesma palavra ficam colados e alternam de cor. -> y logo abaixo"""
    cx, cy, cor = x, y, CINZA
    for p, _, nova in cortar(t):
        w = larg(p, "md", tam) + 18
        if nova and cx > x:
            cx += 14
        if cx + w > x + largura and cx > x:
            cx, cy = x, cy + tam * 1.9
        cor = VINHO if cor == CINZA else CINZA
        cx += chip(cx, cy, p, tam, cor) + 3
    return cy + tam * 1.9


# ---------------- o rodapé: a explicação, cortada em pedaços ----------------
RODAPE = "A IA não lê palavras: ela corta o texto em pedaços, troca cada pedaço por um número e adivinha o próximo."
itens, cor = [], CINZA
for p, _, nova in cortar(" " + RODAPE)[0:]:
    cor = VINHO if cor == CINZA else CINZA
    itens.append((p, cor))
fundo_e_fio(itens, tam=38)

# ---------------- 1 · capa ----------------
topo(0, "IA SEM MISTÉRIO · PARTE 2")
y = titulo(0, ["Por que a IA", "erra contas?"], tam=96)
y = corpo(0, y + 10, "Ela escreve um relatório inteiro em segundos e tropeça numa multiplicação grande.", tam=42)
corpo(0, y + 16, "O motivo está no jeito como ela lê.", tam=42, tipo="sb", cor=FG)
rotulo(MARGEM, 1040, "arraste: a frase aqui embaixo já está cortada  →", RED_SOFT)

# ---------------- 2 · ela lê pedaços ----------------
topo(1, "COMO ELA LÊ")
y = titulo(1, ["Ela não lê", "palavras.", "Lê pedaços."])
y = corpo(1, y, "Antes de chegar à IA, todo texto é cortado em pedaços menores. Assim:", tam=38)
x0 = LADO + MARGEM
rotulo(x0, y + 14, "O QUE VOCÊ ESCREVE")
texto(x0, y + 54, "a manutenção preventiva", "md", 46, FG)
rotulo(x0, y + 150, "O QUE ELA RECEBE", RED_SOFT)
blocos(" a manutenção preventiva", 46, x0, y + 190)

# ---------------- 3 · comum x rara ----------------
topo(2, "A REGRA DO CORTE")
y = titulo(2, ["Palavra comum:", "um pedaço.", "Palavra rara: vários."], tam=62)
y = corpo(2, y, "O que aparece muito nos textos vira um pedaço só. O que aparece pouco é montado com pedaços menores.", tam=36)
x0 = 2 * LADO + MARGEM
rotulo(x0, y + 8, "COMUNS")
yy = y + 48
cx = x0
for w in (" empresa", " produção", " trabalho"):
    yb = blocos(w, 36, cx, yy, 400)
    cx += sum(larg(p, "md", 36) + 21 for p, _, _ in cortar(w)) + 40
rotulo(x0, y + 130, "RARAS", RED_SOFT)
yy = y + 170
for w in (" almoxarifado", " empilhadeira", " paquímetro"):
    yy = blocos(w, 36, x0, yy) - 8

# ---------------- 4 · vira número ----------------
topo(3, "O QUE ELA ENXERGA")
y = titulo(3, ["Cada pedaço", "vira um número"])
y = corpo(3, y, "A IA nunca vê letras. Cada pedaço é trocado pelo número dele numa lista, e ela trabalha só com esses números.", tam=37)
x0 = 3 * LADO + MARGEM
cx = x0
for p, i, _ in cortar(" a bomba parou de novo"):
    w = max(larg(p, "md", 38), larg(str(i), "mono", 30)) + 30
    caixa(cx, y + 30, w, 64, 10, CINZA, NADA, 0)
    texto(cx + w / 2, y + 62, p, "md", 38, FG, "mm")
    texto(cx + w / 2, y + 126, "↓", "b", 34, RED, "mm")
    caixa(cx, y + 158, w, 64, 10, AZUL, NADA, 0)
    texto(cx + w / 2, y + 190, str(i), "mono", 30, FG, "mm")
    cx += w + 10
rotulo(x0, y + 250, "é isto que chega até ela")

# ---------------- 5 · por isso ela tropeça ----------------
topo(4, "POR ISSO ELA TROPEÇA")
y = titulo(4, ["Ela não calcula.", "Adivinha."])
y = corpo(4, y, "Um número grande também é cortado em pedaços. A IA não faz a conta: ela adivinha os pedaços do resultado, como adivinha palavras.", tam=36)
x0 = 4 * LADO + MARGEM
cx = x0
for p in ("48", "392", " × ", "7", "615", " = "):
    if p.strip() in ("×", "="):
        texto(cx + 8, y + 60, p.strip(), "b", 44, MUTE, "lm")
        cx += 56
    else:
        cx += chip(cx, y + 24, p, 44, CINZA, "mono") + 4
caixa(cx + 6, y + 24, 130, 68, 9, NADA, RED, 4)
texto(cx + 71, y + 58, "?", "b", 44, RED_SOFT, "mm")
y = corpo(4, y + 124, "Conta pequena ela viu muitas vezes e acerta. Conta grande, ela nunca viu igual.", tam=36, tipo="sb", cor=FG)
corpo(4, y, "Contar letras de uma palavra dá o mesmo problema: ela vê pedaços, não letras.", tam=36)

# ---------------- 6 · o que ela faz bem ----------------
topo(5, "O OUTRO LADO")
y = titulo(5, ["Com texto,", "ela é ótima"])
y = corpo(5, y, "O mesmo mecanismo que atrapalha na conta é o que a faz tão boa com linguagem.", tam=38)
x0 = 5 * LADO + MARGEM
for j, t in enumerate(("resumir um documento longo", "reescrever num tom melhor", "explicar um assunto difícil",
                       "organizar anotações soltas")):
    caixa(x0, y + 20 + j * 92, 912, 76, 16, CARD, VERDE)
    texto(x0 + 28, y + 58 + j * 92, t, "md", 34, FG, "lm")

# ---------------- 7 · na prática ----------------
topo(6, "NA PRÁTICA")
y = titulo(6, ["Número exato?", "Peça a conta,", "não o resultado."], tam=64)
y = corpo(6, y, "Para tudo o que precisa bater:", tam=37)
x0 = 6 * LADO + MARGEM
for j, (cab, det) in enumerate((("peça a fórmula ou a planilha", "ela monta a conta; a planilha calcula"),
                                ("peça para usar a calculadora", "muitas IAs têm uma, e avisam quando usam"),
                                ("confira o que for crítico", "horas, custos, estoque, totais de pedido"))):
    caixa(x0, y + 14 + j * 124, 912, 108, 16, CARD, LINE)
    texto(x0 + 28, y + 46 + j * 124, cab, "sb", 34, FG, "lm")
    texto(x0 + 28, y + 90 + j * 124, det, "sans", 28, BODY, "lm")

# ---------------- 8 · fechamento ----------------
topo(7, "E VOCÊ?")
y = titulo(7, ["A sua imaginação", "é o limite."], tam=84)
y = corpo(7, y, "Texto é com ela. Número exato é com a calculadora.", tam=42, tipo="sb", cor=FG)
y = corpo(7, y + 10, "Já pegou uma IA errando uma conta ou um total?", tam=42)
y = corpo(7, y + 10, "Me conta nos comentários.", tam=42, tipo="sb", cor=FG)
rotulo(7 * LADO + MARGEM, y + 50, "Na parte 3: por que ela esquece o que você disse.", RED_SOFT)
texto(7 * LADO + MARGEM, 1050, "@elucas.dev", "mono", 26, MUTE)

salvar(os.path.join(os.path.dirname(os.path.abspath(__file__)), "parte2"))
