"""Carrossel "IA sem mistério", parte 7 — até quando a IA sabe das coisas: a data de corte (o treino é uma fotografia).

    C:/dev/venv/Scripts/python.exe posts/serie_ia/parte7/carrossel.py   ->  as imagens saem nesta pasta
"""
import os

import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # base.py fica na pasta da série
from base import (BODY, CARD, CARD_2, FG, LADO, LINE, MARGEM, MUTE, NADA, RED, RED_SOFT, VERDE, caixa, cartoes, circulo,
                  corpo, fecho, linha, rodape, rotulo, salvar, texto, titulo, topo)

rodape("O que a IA sabe", "vem do treino, e o treino parou numa data: dali em diante, só sabe o que você mostrar ou o que ela buscar.", tam=40)

# ---------------- 1 · capa ----------------
topo(0, "IA SEM MISTÉRIO · PARTE 7")
y = titulo(0, ["Até quando", "a IA sabe", "das coisas?"], tam=92)
y = corpo(0, y + 10, "Você pergunta de uma notícia da semana passada, de uma regra que mudou, do seu próprio procedimento. E ela responde como se nada tivesse acontecido.", tam=40)
corpo(0, y + 16, "O conhecimento dela tem data.", tam=42, tipo="sb", cor=FG)
rotulo(MARGEM, 1040, "arraste e leia a frase aqui embaixo  →", RED_SOFT)

# ---------------- 2 · fotografia ----------------
topo(1, "A ORIGEM")
y = titulo(1, ["O treino é uma", "fotografia"])
y = corpo(1, y, "A IA aprendeu lendo uma quantidade enorme de textos. Essa leitura aconteceu uma vez, antes de ela chegar até você. É uma foto do que estava escrito até aquele dia.", tam=36)
x0 = LADO + MARGEM
caixa(x0 + 180, y + 20, 552, 300, 14, (236, 236, 239), NADA, 0)
caixa(x0 + 204, y + 44, 504, 210, 6, CARD_2, NADA, 0)
for i, fr in enumerate((0.8, 0.6, 0.72, 0.5, 0.66)):
    caixa(x0 + 232, y + 74 + i * 32, 440 * fr, 10, 5, (90, 90, 100), NADA, 0)
texto(x0 + 456, y + 288, "tudo o que ela leu", "mono", 22, (60, 60, 68), "mm")

# ---------------- 3 · data de corte ----------------
topo(2, "O NOME TÉCNICO")
y = titulo(2, ["Data de corte"])
y = corpo(2, y, "É o dia em que a foto foi tirada. O que aconteceu depois não está no que ela aprendeu: produto lançado, lei alterada, notícia, preço.", tam=37)
x0 = 2 * LADO + MARGEM
yl = y + 130
linha([(x0, yl), (x0 + 560, yl)], RED, 8)
linha([(x0 + 560, yl), (x0 + 912, yl)], (70, 70, 80), 8)
circulo(x0 + 560, yl, 16, RED)
circulo(x0 + 900, yl, 12, FG)
texto(x0 + 280, yl - 44, "o que ela leu", "md", 30, FG, "mm")
texto(x0 + 560, yl + 50, "data de corte", "mono", 24, RED_SOFT, "mm")
texto(x0 + 736, yl - 44, "não viu", "md", 30, MUTE, "mm")
texto(x0 + 900, yl + 50, "hoje", "mono", 24, FG, "rm")

# ---------------- 4 · a sua empresa ----------------
topo(3, "MAIS IMPORTANTE")
y = titulo(3, ["A sua empresa", "não saiu na foto"])
y = corpo(3, y, "Não é só o que é recente. O que é interno também ficou de fora: ela nunca leu o seu procedimento, o seu contrato, o histórico do seu equipamento.", tam=37)
x0 = 3 * LADO + MARGEM
for j, t in enumerate(("procedimentos internos", "contratos e propostas", "histórico de equipamentos", "decisões e atas")):
    caixa(x0 + (j % 2) * 470, y + 16 + (j // 2) * 104, 442, 86, 16, CARD, LINE)
    texto(x0 + (j % 2) * 470 + 26, y + 59 + (j // 2) * 104, t, "md", 30, FG, "lm")
rotulo(x0, y + 236, "nada disso estava nos textos do treino")

# ---------------- 5 · ela não avisa ----------------
topo(4, "O PERIGO")
y = titulo(4, ["Ela nem sempre", "avisa"])
y = corpo(4, y, "Diante de algo que não está na foto, a IA pode responder com o que tinha: uma informação antiga, dita como atual. Ou completar com um chute bem escrito, como vimos na parte 5.", tam=36)
x0 = 4 * LADO + MARGEM
caixa(x0, y + 20, 912, 96, 18, CARD, RED)
texto(x0 + 28, y + 68, "informação velha, com cara de nova", "md", 34, FG, "lm")

# ---------------- 6 · como resolveram ----------------
topo(5, "COMO RESOLVERAM · BUSCA E DOCUMENTOS")
y = titulo(5, ["O jornal do dia", "em cima da mesa"])
y = corpo(5, y, "As IAs de hoje podem buscar na internet antes de responder, e você pode entregar os seus documentos. A foto continua a mesma: a informação nova entra pela conversa, na janela de contexto.", tam=35)
x0 = 5 * LADO + MARGEM
for j, (rot, val, cor) in enumerate((("O QUE É RECENTE", "busca na internet, com fontes", VERDE), ("O QUE É SEU", "documento junto com a pergunta", VERDE))):
    caixa(x0, y + 16 + j * 128, 912, 110, 18, CARD, cor)
    texto(x0 + 28, y + 48 + j * 128, rot, "mono", 23, MUTE, "lm")
    texto(x0 + 28, y + 88 + j * 128, val, "md", 33, FG, "lm")

# ---------------- 7 · na prática ----------------
topo(6, "NA PRÁTICA")
y = titulo(6, ["Pergunte-se:", "isso estava na foto?"], tam=64)
y = corpo(6, y, "Se a resposta for não, a informação tem de entrar pela conversa.", tam=37)
cartoes(6, y, [("assunto recente: peça para buscar", "e confira as fontes que ela mostrar"),
               ("assunto interno: entregue o documento", "ela não tem como saber de outro jeito"),
               ("regra, preço e prazo: confirme a data", "é onde informação velha mais custa caro")])

fecho("O que não estava na foto, ela só sabe se você mostrar.", "Qual informação desatualizada uma IA já te passou como atual?",
      "Na parte 8: precisa sempre da IA mais potente?")
salvar(os.path.dirname(os.path.abspath(__file__)))
