"""Carrossel "IA sem mistério", parte 5 — por que a IA inventa: a alucinação (o aluno que chuta na prova).

O exemplo da resposta inventada é fictício, escrito para ilustrar.

    C:/dev/venv/Scripts/python.exe posts/serie_ia/parte5/carrossel.py   ->  as imagens saem nesta pasta
"""
import os

import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # base.py fica na pasta da série
from base import (BODY, CARD, CARD_2, FG, LADO, LINE, MARGEM, MUTE, NADA, RED, RED_SOFT, VERDE, caixa, cartoes, corpo,
                  fecho, rodape, rotulo, salvar, texto, titulo, topo)

rodape("Quando não sabe,", "a IA não deixa em branco: ela escreve a resposta mais provável, como um aluno que chuta na prova.")

# ---------------- 1 · capa ----------------
topo(0, "IA SEM MISTÉRIO · PARTE 5")
y = titulo(0, ["Por que a IA", "inventa?"], tam=96)
y = corpo(0, y + 10, "Ela cita uma norma que não existe, um número que ninguém mediu, um link que não abre. E faz isso com toda a segurança.", tam=42)
corpo(0, y + 16, "Tem explicação. E tem como reduzir.", tam=42, tipo="sb", cor=FG)
rotulo(MARGEM, 1040, "arraste e leia a frase aqui embaixo  →", RED_SOFT)

# ---------------- 2 · ela sempre completa ----------------
topo(1, "O MECANISMO")
y = titulo(1, ["Ela sempre", "completa o texto"])
y = corpo(1, y, "A IA escreve adivinhando a próxima palavra. Esse mecanismo não tem a opção “não sei”: sempre existe uma palavra mais provável, e ela segue escrevendo.", tam=37)
x0 = LADO + MARGEM
caixa(x0, y + 20, 912, 96, 18, CARD, LINE)
texto(x0 + 28, y + 68, "A norma interna que trata disso é a", "md", 34, FG, "lm")
caixa(x0 + 640, y + 38, 130, 60, 10, NADA, RED, 4)
texto(x0 + 705, y + 68, "?", "b", 38, RED_SOFT, "mm")
rotulo(x0, y + 150, "ALGUMA PALAVRA SEMPRE VEM DEPOIS")

# ---------------- 3 · alucinação ----------------
topo(2, "O NOME DISSO")
y = titulo(2, ["Alucinação"])
y = corpo(2, y, "É quando a IA escreve, com segurança, algo que não é verdade. O texto sai bem escrito, no formato certo, e errado.", tam=37)
x0 = 2 * LADO + MARGEM
rotulo(x0, y + 10, "EXEMPLO (FICTÍCIO)")
caixa(x0 + 252, y + 50, 660, 76, 18, (70, 30, 34), RED)
texto(x0 + 276, y + 88, "Qual norma trata desse ensaio?", "md", 30, FG, "lm")
caixa(x0, y + 146, 760, 150, 18, CARD_2, LINE)
texto(x0 + 24, y + 186, "É a norma NT-4471, revisão C,", "md", 30, FG, "lm")
texto(x0 + 24, y + 228, "item 8.3, publicada pela comissão…", "md", 30, FG, "lm")
texto(x0 + 24, y + 268, "convincente. e inventada.", "mono", 24, RED_SOFT, "lm")

# ---------------- 4 · o aluno que chuta ----------------
topo(3, "POR QUE ACONTECE")
y = titulo(3, ["O aluno que", "chuta na prova"])
y = corpo(3, y, "Numa prova em que resposta em branco vale zero, chutar compensa. Pesquisadores de um dos fabricantes mostraram que as IAs são treinadas e avaliadas assim: quem arrisca pontua mais do que quem admite que não sabe.", tam=34)
x0 = 3 * LADO + MARGEM
for j, (rot, val, cor) in enumerate((("em branco", "zero", LINE), ("chute", "às vezes acerta", VERDE))):
    caixa(x0 + j * 470, y + 16, 442, 150, 18, CARD, cor)
    texto(x0 + j * 470 + 28, y + 62, rot, "mono", 26, MUTE, "lm")
    texto(x0 + j * 470 + 28, y + 116, val, "sb", 38, FG, "lm")

# ---------------- 5 · onde ela mais inventa ----------------
topo(4, "ONDE MORA O PERIGO")
y = titulo(4, ["No detalhe", "específico"])
y = corpo(4, y, "O geral ela viu muitas vezes e costuma acertar. O risco cresce no detalhe raro, que apareceu pouco ou nunca nos textos que ela leu:", tam=36)
x0 = 4 * LADO + MARGEM
for j, t in enumerate(("datas e números", "nomes e normas", "citações e referências", "links")):
    caixa(x0 + (j % 2) * 470, y + 16 + (j // 2) * 104, 442, 86, 16, CARD, RED)
    texto(x0 + (j % 2) * 470 + 26, y + 59 + (j // 2) * 104, t, "md", 31, FG, "lm")

# ---------------- 6 · como resolveram ----------------
topo(5, "COMO RESOLVERAM · BUSCA COM FONTES")
y = titulo(5, ["Prova com", "consulta"])
y = corpo(5, y, "As IAs de hoje podem consultar antes de responder: buscam na internet ou nos seus documentos e mostram de onde tiraram cada informação.", tam=35)
y = corpo(5, y, "Ainda assim ela escreve palavra por palavra. A consulta reduz o chute, não acaba com ele.", tam=35, tipo="sb", cor=FG)
x0 = 5 * LADO + MARGEM
caixa(x0, y + 16, 912, 170, 18, CARD, VERDE)
texto(x0 + 28, y + 62, "A troca do selo ficou pendente desde a última parada.", "md", 30, FG, "lm")
caixa(x0 + 28, y + 106, 400, 54, 27, (30, 50, 40), VERDE)
texto(x0 + 52, y + 133, "fonte: relatório da parada", "mono", 24, VERDE, "lm")

# ---------------- 7 · na prática ----------------
topo(6, "NA PRÁTICA")
y = titulo(6, ["Tire o chute", "da jogada"])
y = corpo(6, y, "Você não elimina a alucinação. Você reduz e confere.", tam=37)
cartoes(6, y, [("entregue o documento", "resposta com consulta inventa menos"),
               ("peça a fonte de cada afirmação", "e abra a fonte: link inventado não abre"),
               ("diga que “não sei” é resposta válida", "tire o prêmio do chute")])

fecho("Bem escrito não quer dizer verdadeiro.", "Qual foi a invenção mais convincente que uma IA já te entregou?",
      "Na parte 6: por que a mesma pergunta dá respostas diferentes.")
salvar(os.path.dirname(os.path.abspath(__file__)))
