"""Carrossel "IA sem mistério", parte 4 — como a IA decide o que importa: a atenção.

Os pesos desenhados são ilustração do mecanismo, não medida de um modelo.

    C:/dev/venv/Scripts/python.exe posts/serie_ia/parte4.py   ->  posts/serie_ia/parte4/
"""
import math
import os

from base import (BODY, CARD, CARD_2, CINZA, FG, LADO, LINE, MARGEM, MUTE, NADA, RED, RED_SOFT, VERDE, VINHO, caixa,
                  chip, circulo, corpo, fundo_e_fio, larg, linha, rotulo, salvar, texto, titulo, topo)

COMECO = "Para escrever cada palavra,".split()
RESTO = "a IA olha tudo o que veio antes e dá mais peso ao que parece importar.".split()
fundo_e_fio([(p, CINZA) for p in COMECO] + [(p, VINHO) for p in RESTO], tam=44)


def pesos(x, y, palavras, alvo, tam=34, largura=912):
    """A frase em blocos; embaixo de cada palavra, uma barra verde com o peso que ela recebe. palavras = [(texto, peso)]"""
    cx, cy = x, y
    for t, p in palavras:
        w = larg(t, "md", tam) + 18
        if cx + w > x + largura and cx > x:
            cx, cy = x, cy + tam * 2.7
        chip(cx, cy, t, tam, VINHO if t == alvo else CINZA)
        if p > 0:
            caixa(cx, cy + tam * 1.7, w, 6 + 22 * p, 4, VERDE + (int(70 + 185 * p),), NADA, 0)
        cx += w + 8
    return cy + tam * 2.7


# ---------------- 1 · capa ----------------
topo(0, "IA SEM MISTÉRIO · PARTE 4")
y = titulo(0, ["Como a IA", "decide o que", "importa?"], tam=92)
y = corpo(0, y + 10, "Você manda um texto enorme e uma instrução. Às vezes ela segue à risca. Às vezes parece que nem leu.", tam=42)
corpo(0, y + 16, "A diferença está em como ela distribui a atenção.", tam=42, tipo="sb", cor=FG)
rotulo(MARGEM, 1040, "arraste e leia a frase aqui embaixo  →", RED_SOFT)

# ---------------- 2 · ela pesa ----------------
topo(1, "O MECANISMO · ATENÇÃO")
y = titulo(1, ["Ela dá peso", "a cada palavra"])
y = corpo(1, y, "Antes de escrever a próxima palavra, a IA olha tudo o que veio antes e decide quanto cada trecho pesa, como um holofote que ilumina mais umas palavras que outras. O nome técnico: atenção.", tam=37)
x0 = LADO + MARGEM
rotulo(x0, y + 12, "QUANTO CADA PALAVRA PESA PARA A PRÓXIMA")
yy = pesos(x0, y + 56, [("A", 0.05), ("bomba", 0.9), ("parou", 0.7), ("porque", 0.3), ("o", 0.05), ("selo", 1.0), ("estava", 0.25)], None, 38)
caixa(x0, yy, 130, 60, 9, NADA, RED, 4)
texto(x0 + 65, yy + 30, "?", "b", 40, RED_SOFT, "mm")

# ---------------- 3 · é assim que ela entende ----------------
topo(2, "POR QUE FUNCIONA")
y = titulo(2, ["É assim que ela", "liga os pontos"])
y = corpo(2, y, "Na frase abaixo, “ele” é o técnico, o selo ou a bomba? Para decidir, a IA dá mais peso às palavras que ajudam a responder.", tam=37)
x0 = 2 * LADO + MARGEM
pesos(x0, y + 30, [("O", 0), ("técnico", 0.25), ("trocou", 0.3), ("o", 0), ("selo", 1.0), ("da", 0), ("bomba", 0.3),
                  ("porque", 0.15), ("ele", 0), ("estava", 0.35), ("gasto.", 0.85)], "ele", 36)
rotulo(x0, y + 250, "barra verde: o peso de cada palavra para entender “ele”", VERDE)

# ---------------- 4 · mais texto, mais disputa ----------------
topo(3, "O LIMITE")
y = titulo(3, ["Mais texto,", "mais disputa"])
y = corpo(3, y, "O peso é dividido entre tudo o que ela está lendo. Num texto curto, a sua instrução pesa muito. Num texto enorme, ela disputa espaço com todo o resto.", tam=36)
x0 = 3 * LADO + MARGEM
for j, (rot, n) in enumerate((("TEXTO CURTO", 5), ("TEXTO LONGO", 26))):
    yy = y + 16 + j * 150
    rotulo(x0, yy, rot)
    w = (912 - (n - 1) * 6) / n
    for i in range(n):
        instr = i == (1 if j == 0 else 9)
        caixa(x0 + i * (w + 6), yy + 40, w, 70, 8, RED if instr else CARD_2, NADA, 0)
rotulo(x0, y + 320, "em vermelho: a sua instrução", RED_SOFT)

# ---------------- 5 · o meio se perde ----------------
topo(4, "O QUE A PESQUISA MOSTRA")
y = titulo(4, ["O meio", "se perde"])
y = corpo(4, y, "Estudos com textos longos mostram um padrão: a IA aproveita melhor o que está no começo e no fim. O que fica no meio é mais fácil de passar batido.", tam=36)
x0 = 4 * LADO + MARGEM
caixa(x0, y + 20, 912, 250, 18, CARD, LINE)
pts = [(x0 + 50 + i * 8.12, y + 80 + 130 * math.sin(math.pi * i / 100) ** 0.8) for i in range(101)]
linha(pts, RED, 6)
for (px, py) in (pts[0], pts[-1]):
    circulo(px, py, 10, RED)
texto(x0 + 50, y + 240, "começo", "mono", 22, MUTE, "lm")
texto(x0 + 456, y + 240, "meio", "mono", 22, MUTE, "mm")
texto(x0 + 862, y + 240, "fim", "mono", 22, MUTE, "rm")
rotulo(x0, y + 290, "quanto mais alto, mais a IA aproveita a informação")

# ---------------- 6 · a dica dos fabricantes ----------------
topo(5, "A DICA DE QUEM FABRICA")
y = titulo(5, ["Documento em cima.", "Pedido embaixo."], tam=62)
y = corpo(5, y, "Os próprios fabricantes recomendam: com textos longos, coloque o material primeiro e o seu pedido, o prompt, por último. Ele fica onde a IA presta mais atenção.", tam=35)
x0 = 5 * LADO + MARGEM
caixa(x0, y + 16, 912, 150, 18, CARD, LINE)
rotulo(x0 + 24, y + 32, "1 · O MATERIAL")
for i, fr in enumerate((0.92, 0.8, 0.88)):
    caixa(x0 + 24, y + 78 + i * 24, 864 * fr, 10, 5, (90, 90, 100), NADA, 0)
caixa(x0, y + 182, 912, 110, 18, CARD, RED, 3)
rotulo(x0 + 24, y + 198, "2 · O SEU PEDIDO (O PROMPT)", RED_SOFT)
texto(x0 + 24, y + 256, "Com base no relatório acima, liste as três causas.", "md", 30, FG, "lm")

# ---------------- 7 · na prática ----------------
topo(6, "NA PRÁTICA")
y = titulo(6, ["Ajude a IA a", "prestar atenção"])
y = corpo(6, y, "Organização não é capricho. É o que faz a sua instrução pesar.", tam=37)
x0 = 6 * LADO + MARGEM
for j, (cab, det) in enumerate((("um pedido de cada vez", "pedidos misturados disputam a atenção entre si"),
                                ("destaque o que não pode faltar", "títulos, listas e a regra principal repetida no fim"),
                                ("mostre um exemplo do resultado", "um modelo pronto pesa mais que uma explicação longa"))):
    caixa(x0, y + 14 + j * 124, 912, 108, 16, CARD, LINE)
    texto(x0 + 28, y + 46 + j * 124, cab, "sb", 34, FG, "lm")
    texto(x0 + 28, y + 90 + j * 124, det, "sans", 28, BODY, "lm")

# ---------------- 8 · fechamento ----------------
topo(7, "E VOCÊ?")
y = titulo(7, ["A sua imaginação", "é o limite."], tam=84)
y = corpo(7, y, "Texto organizado, atenção no lugar certo.", tam=42, tipo="sb", cor=FG)
y = corpo(7, y + 10, "Qual instrução a IA vive ignorando nos seus pedidos?", tam=42)
y = corpo(7, y + 10, "Me conta nos comentários.", tam=42, tipo="sb", cor=FG)
rotulo(7 * LADO + MARGEM, y + 50, "Na próxima semana: por que ela inventa.", RED_SOFT)
texto(7 * LADO + MARGEM, 1050, "@elucas.dev", "mono", 26, MUTE)

salvar(os.path.join(os.path.dirname(os.path.abspath(__file__)), "parte4"))
