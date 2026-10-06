"""Carrossel "IA sem mistério", parte 6 — por que a mesma pergunta dá respostas diferentes: o sorteio e a temperatura.

As fatias da roleta e as barras são ilustração do mecanismo.

    C:/dev/venv/Scripts/python.exe posts/serie_ia/parte6/carrossel.py   ->  as imagens saem nesta pasta
"""
import math
import os

import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # base.py fica na pasta da série
import base
from base import (BODY, CARD, CARD_2, FG, K, LADO, LINE, MARGEM, MUTE, NADA, RED, RED_SOFT, VERDE, caixa, cartoes,
                  circulo, corpo, fecho, linha, rodape, rotulo, salvar, texto, titulo, topo)

rodape("A IA não escolhe sempre", "o palpite mais forte: ela sorteia entre os mais prováveis, e por isso cada resposta sai um pouco diferente.", tam=40)


def roleta(cx, cy, r, fatias):
    """fatias = [(tamanho, cor, rótulo)]; a soma dos tamanhos é 1."""
    ang = -90.0
    for v, cor, rot in fatias:
        base.d.pieslice([(cx - r) * K, (cy - r) * K, (cx + r) * K, (cy + r) * K], ang, ang + 360 * v, fill=cor, outline=base.INK, width=3 * K)
        meio = math.radians(ang + 180 * v)
        if rot:
            texto(cx + math.cos(meio) * r * 0.6, cy + math.sin(meio) * r * 0.6, rot, "md", 26, FG, "mm")
        ang += 360 * v
    circulo(cx, cy, 16, FG)
    linha([(cx, cy), (cx + r * 0.72, cy - r * 0.5)], FG, 6)


# ---------------- 1 · capa ----------------
topo(0, "IA SEM MISTÉRIO · PARTE 6")
y = titulo(0, ["Mesma pergunta,", "respostas", "diferentes?"], tam=88)
y = corpo(0, y + 10, "Você pergunta duas vezes a mesma coisa e a IA responde de dois jeitos. Seu colega pergunta e recebe um terceiro.", tam=42)
corpo(0, y + 16, "Não é bug. É de propósito.", tam=42, tipo="sb", cor=FG)
rotulo(MARGEM, 1040, "arraste e leia a frase aqui embaixo  →", RED_SOFT)

# ---------------- 2 · ela sorteia ----------------
topo(1, "O MECANISMO")
y = titulo(1, ["Ela gira", "uma roleta"])
y = corpo(1, y, "A cada palavra, a IA tem vários palpites. Ela não pega sempre o mais forte: gira uma roleta em que o palpite mais provável ocupa a fatia maior. O nome técnico: amostragem.", tam=35)
roleta(LADO + 300, y + 190, 170, [(0.55, (150, 50, 56), "próxima"), (0.25, (110, 60, 66), "resposta"), (0.12, (80, 62, 68), "melhor"), (0.08, (60, 60, 68), "")])
texto(LADO + 520, y + 130, "fatia maior:", "sans", 30, BODY)
texto(LADO + 520, y + 172, "sai mais vezes", "sb", 34, FG)
texto(LADO + 520, y + 240, "fatia menor:", "sans", 30, BODY)
texto(LADO + 520, y + 282, "sai de vez em quando", "sb", 34, FG)

# ---------------- 3 · temperatura ----------------
topo(2, "O BOTÃO · TEMPERATURA")
y = titulo(2, ["O botão", "da ousadia"])
y = corpo(2, y, "Existe um ajuste que controla esse sorteio. Chama-se temperatura. Baixa: ela fica com os palpites mais prováveis. Alta: arrisca mais, e o texto sai mais variado.", tam=36)
x0 = 2 * LADO + MARGEM
for j, (rot, fat, leg) in enumerate((("TEMPERATURA BAIXA", [(0.9, (150, 50, 56), ""), (0.07, (110, 60, 66), ""), (0.03, (60, 60, 68), "")], "previsível"),
                                    ("TEMPERATURA ALTA", [(0.4, (150, 50, 56), ""), (0.3, (110, 60, 66), ""), (0.18, (80, 62, 68), ""), (0.12, (60, 60, 68), "")], "variado"))):
    rotulo(x0 + j * 470, y + 10, rot, MUTE if j == 0 else RED_SOFT)
    roleta(x0 + j * 470 + 130, y + 180, 120, fat)
    texto(x0 + j * 470 + 290, y + 180, leg, "sb", 32, FG, "lm")

# ---------------- 4 · nem no zero ----------------
topo(3, "UM DETALHE")
y = titulo(3, ["Nem no mínimo", "sai idêntico"])
y = corpo(3, y, "Dá para reduzir a variação, mas não para zerar. A própria documentação de um dos fabricantes avisa: mesmo com a temperatura no mínimo, a mesma entrada pode gerar saídas diferentes.", tam=36)
x0 = 3 * LADO + MARGEM
for j, t in enumerate(("O relatório aponta três causas.", "O relatório indica três causas.", "São três as causas apontadas.")):
    caixa(x0, y + 16 + j * 96, 912, 80, 16, CARD, LINE)
    texto(x0 + 28, y + 56 + j * 96, t, "md", 32, FG, "lm")
rotulo(x0, y + 314, "mesma pergunta, três respostas válidas")

# ---------------- 5 · é útil ----------------
topo(4, "O LADO BOM")
y = titulo(4, ["A variação", "é uma ferramenta"])
y = corpo(4, y, "Se a resposta fosse sempre a mesma, pedir de novo não adiantaria. É a variação que deixa você pedir outra versão, outro tom, outra ideia.", tam=37)
x0 = 4 * LADO + MARGEM
for j, (rot, val, cor) in enumerate((("quer ideias", "a variação ajuda", VERDE), ("quer padrão", "a variação atrapalha", RED))):
    caixa(x0 + j * 470, y + 20, 442, 150, 18, CARD, cor)
    texto(x0 + j * 470 + 28, y + 66, rot, "mono", 26, MUTE, "lm")
    texto(x0 + j * 470 + 28, y + 120, val, "sb", 34, FG, "lm")

# ---------------- 6 · como domar ----------------
topo(5, "COMO DOMAR")
y = titulo(5, ["Você controla", "pelo pedido"])
y = corpo(5, y, "Nas ferramentas de conversa, em geral esse botão não aparece para você. O que você controla é o pedido: quanto mais ele define o resultado, menos espaço sobra para o sorteio.", tam=35)
x0 = 5 * LADO + MARGEM
caixa(x0, y + 16, 912, 250, 18, CARD, VERDE)
for j, (rot, val) in enumerate((("formato fixo", "Responda numa tabela: causa, evidência, ação."), ("um exemplo", "Siga o modelo do relatório abaixo."))):
    texto(x0 + 28, y + 44 + j * 112, rot, "mono", 23, RED_SOFT)
    texto(x0 + 28, y + 76 + j * 112, val, "md", 31, FG)

# ---------------- 7 · na prática ----------------
topo(6, "NA PRÁTICA")
y = titulo(6, ["Use o sorteio", "a seu favor"])
y = corpo(6, y, "Decida antes se você quer padrão ou quer opções.", tam=37)
cartoes(6, y, [("tarefa repetitiva: trave o formato", "modelo de resposta e um exemplo pronto"),
               ("quer ideias: peça várias de uma vez", "e peça de novo, se nenhuma servir"),
               ("decisão importante: pergunte duas vezes", "se as respostas divergem, confira")])

fecho("Não é bug: é sorteio. E dá para domar.", "Você já recebeu duas respostas opostas para a mesma pergunta?",
      "Na parte 7: até quando a IA sabe das coisas.")
salvar(os.path.dirname(os.path.abspath(__file__)))
