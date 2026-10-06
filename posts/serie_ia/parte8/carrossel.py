"""Carrossel "IA sem mistério", parte 8 — precisa sempre da IA mais potente? Modelos de vários tamanhos (a frota).

As barras de capacidade, velocidade e custo são ilustração da troca, sem escala.

    C:/dev/venv/Scripts/python.exe posts/serie_ia/parte8/carrossel.py   ->  as imagens saem nesta pasta
"""
import os

import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # base.py fica na pasta da série
from base import (BODY, CARD, CARD_2, FG, LADO, LINE, MARGEM, MUTE, NADA, RED, RED_SOFT, VERDE, caixa, cartoes, corpo,
                  fecho, rodape, rotulo, salvar, texto, titulo, topo)

rodape("Existem IAs de vários tamanhos:", "a maior resolve mais, mas custa mais e demora mais, e muita tarefa do dia a dia cabe na menor.", tam=40)

# ---------------- 1 · capa ----------------
topo(0, "IA SEM MISTÉRIO · PARTE 8")
y = titulo(0, ["Precisa sempre", "da IA mais", "potente?"], tam=92)
y = corpo(0, y + 10, "Ninguém manda um caminhão entregar uma carta. Com IA, muita gente faz exatamente isso, e paga por isso.", tam=42)
corpo(0, y + 16, "IA também tem tamanho.", tam=42, tipo="sb", cor=FG)
rotulo(MARGEM, 1040, "arraste e leia a frase aqui embaixo  →", RED_SOFT)

# ---------------- 2 · modelo ----------------
topo(1, "O NOME TÉCNICO")
y = titulo(1, ["Modelo"])
y = corpo(1, y, "Cada IA que escreve é um modelo. E os fabricantes não oferecem um só: oferecem uma família, do pequeno e rápido ao grande e mais capaz.", tam=37)
x0 = LADO + MARGEM
for j, (rot, lado) in enumerate((("pequeno", 110), ("médio", 170), ("grande", 240))):
    xx = x0 + 40 + j * 300
    caixa(xx, y + 290 - lado, lado, lado, 18, CARD, RED if j == 2 else LINE)
    texto(xx + lado / 2, y + 322, rot, "md", 30, FG, "ma")

# ---------------- 3 · a troca ----------------
topo(2, "A TROCA")
y = titulo(2, ["Capacidade,", "velocidade e custo"], tam=64)
y = corpo(2, y, "O modelo maior resolve tarefas mais difíceis. Em troca, responde mais devagar e custa mais a cada uso. Não existe o melhor em tudo.", tam=37)
x0 = 2 * LADO + MARGEM
for j, (rot, vals) in enumerate((("PEQUENO", (0.4, 1.0, 0.2)), ("GRANDE", (1.0, 0.45, 1.0)))):
    xx = x0 + j * 470
    rotulo(xx, y + 10, rot, MUTE if j == 0 else RED_SOFT)
    for i, (nome, v) in enumerate(zip(("capacidade", "velocidade", "custo"), vals)):
        texto(xx, y + 72 + i * 66, nome, "sans", 26, BODY, "lm")
        caixa(xx + 160, y + 58 + i * 66, 270, 28, 14, (255, 255, 255, 18), NADA, 0)
        caixa(xx + 160, y + 58 + i * 66, 270 * v, 28, 14, RED if i == 2 else VERDE, NADA, 0)

# ---------------- 4 · a frota ----------------
topo(3, "A METÁFORA")
y = titulo(3, ["Monte a frota,", "não compre", "só caminhão"], tam=64)
y = corpo(3, y, "Cada veículo para a sua carga:", tam=37)
cartoes(3, y, [("a moto: modelo pequeno", "classificar, separar, extrair um dado, resumo curto"),
               ("a van: modelo médio", "redigir, revisar, responder com contexto"),
               ("o caminhão: modelo grande", "análise longa, problema difícil, muitas etapas")])

# ---------------- 5 · a dica de quem fabrica ----------------
topo(4, "A DICA DE QUEM FABRICA")
y = titulo(4, ["Comece pelo menor.", "Suba se faltar."], tam=64)
y = corpo(4, y, "A documentação de um dos fabricantes sugere este caminho para muitas aplicações: começar com o modelo rápido e barato, testar com os seus casos e trocar por um maior só onde ele não der conta.", tam=35)
y = corpo(4, y, "Para tarefa complexa, o caminho inverso também vale: começar pelo mais capaz e depois enxugar.", tam=35, tipo="sb", cor=FG)

# ---------------- 6 · o modelo próprio ----------------
topo(5, "ALÉM DA FROTA")
y = titulo(5, ["E a bicicleta:", "a IA sob medida"], tam=64)
y = corpo(5, y, "Para uma decisão repetitiva e bem definida, dá para treinar uma IA pequena só para ela. Foi o que mostrei nos primeiros posts: uma rede minúscula triando ordens de manutenção, respondendo na hora e sem custo por uso.", tam=35)
x0 = 5 * LADO + MARGEM
caixa(x0, y + 16, 912, 96, 18, CARD, VERDE)
texto(x0 + 28, y + 64, "uma tarefa, uma IA pequena, resposta na hora", "md", 32, FG, "lm")

# ---------------- 7 · na prática ----------------
topo(6, "NA PRÁTICA")
y = titulo(6, ["Escolha pelo", "tamanho da tarefa"])
y = corpo(6, y, "Antes de escolher a ferramenta, olhe para a carga.", tam=37)
cartoes(6, y, [("muito volume, tarefa simples", "modelo pequeno: rápido e barato"),
               ("pouco volume, decisão difícil", "modelo grande: vale o custo"),
               ("na dúvida, teste com os seus casos", "dez exemplos reais dizem mais que a propaganda")])

fecho("A maior nem sempre é a melhor escolha.", "Em qual tarefa da sua empresa uma IA menor já daria conta?",
      "Fim da primeira temporada da série.")
salvar(os.path.dirname(os.path.abspath(__file__)))
