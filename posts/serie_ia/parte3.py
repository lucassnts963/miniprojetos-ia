"""Carrossel "IA sem mistério", parte 3 — por que a IA esquece o que você disse: ela só vê o que está na conversa.

    C:/dev/venv/Scripts/python.exe posts/serie_ia/parte3.py   ->  posts/serie_ia/parte3/
"""
import os

from base import (BODY, CARD, CARD_2, CINZA, FG, LADO, LINE, MARGEM, MUTE, NADA, RED, RED_SOFT, VERDE, VINHO, caixa,
                  corpo, fundo_e_fio, rotulo, salvar, texto, titulo, topo)

COMECO = "A IA não guarda nada:".split()
RESTO = "a cada resposta ela relê a conversa inteira, e o que não cabe na leitura fica de fora.".split()
fundo_e_fio([(p, CINZA) for p in COMECO] + [(p, VINHO) for p in RESTO], tam=42)


def fala(x, y, t, minha, w=560, apagada=False, h=62):
    """Uma mensagem da conversa (as suas à direita, as dela à esquerda)."""
    cor = (70, 30, 34) if minha else CARD_2
    borda = RED if minha else LINE
    if apagada:
        cor, borda = (20, 20, 24), (40, 40, 46)
    caixa(x + (912 - w if minha else 0), y, w, h, 16, cor, borda)
    texto(x + (912 - w if minha else 0) + 22, y + h / 2, t, "md", 28, (90, 90, 98) if apagada else FG, "lm")


# ---------------- 1 · capa ----------------
topo(0, "IA SEM MISTÉRIO · PARTE 3")
y = titulo(0, ["Por que a IA", "esquece o que", "você disse?"], tam=92)
y = corpo(0, y + 10, "Você combina uma regra no começo da conversa. Lá pelas tantas, ela ignora.", tam=42)
corpo(0, y + 16, "Não é descuido. É como ela funciona.", tam=42, tipo="sb", cor=FG)
rotulo(MARGEM, 1040, "arraste e leia a frase aqui embaixo  →", RED_SOFT)

# ---------------- 2 · sem memória ----------------
topo(1, "O QUE ACONTECE")
y = titulo(1, ["Ela não tem", "memória"])
y = corpo(1, y, "Entre uma resposta e outra, nada fica guardado nela. A cada mensagem sua, a IA recebe a conversa inteira de novo e relê tudo, do começo.", tam=37)
x0 = LADO + MARGEM
rotulo(x0, y + 10, "O QUE ELA RECEBE A CADA VEZ")
caixa(x0 - 16, y + 46, 944, 318, 20, NADA, RED, 3)
fala(x0, y + 62, "Use sempre o nosso padrão de relatório.", True)
fala(x0, y + 136, "Combinado.", False, 300)
fala(x0, y + 210, "Resuma a parada de ontem.", True, 440)
fala(x0, y + 284, "sua mensagem nova", True, 330)

# ---------------- 3 · a leitura tem limite ----------------
topo(2, "O LIMITE")
y = titulo(2, ["A leitura tem", "um tamanho", "máximo"])
y = corpo(2, y, "Pense numa mesa de trabalho. Cabe muito papel, mas não cabe tudo. A IA só enxerga o que está em cima da mesa naquela hora.", tam=37)
x0 = 2 * LADO + MARGEM
caixa(x0, y + 30, 912, 250, 20, CARD, RED, 3)
rotulo(x0 + 24, y + 48, "A MESA: O QUE ELA ENXERGA", RED_SOFT)
for j in range(5):
    caixa(x0 + 40 + j * 168, y + 100 + (j % 2) * 18, 150, 150, 12, CARD_2, LINE)
    for i, fr in enumerate((0.8, 0.55, 0.7)):
        caixa(x0 + 56 + j * 168, y + 124 + (j % 2) * 18 + i * 26, 118 * fr, 9, 4, (90, 90, 100), NADA, 0)

# ---------------- 4 · conversa longa ----------------
topo(3, "CONVERSA LONGA")
y = titulo(3, ["O começo", "sai da mesa"])
y = corpo(3, y, "Quando a conversa passa do limite, as partes mais antigas são resumidas ou ficam de fora. É aí que o combinado lá do início some.", tam=37)
x0 = 3 * LADO + MARGEM
fala(x0, y + 20, "Use sempre o nosso padrão de relatório.", True, apagada=True)
fala(x0, y + 94, "Combinado.", False, 300, apagada=True)
rotulo(x0, y + 172, "— ficou de fora —")
caixa(x0 - 16, y + 212, 944, 172, 20, NADA, RED, 3)
fala(x0, y + 228, "(muitas mensagens depois)", False, 420)
fala(x0, y + 302, "Resuma a parada de hoje.", True, 430)

# ---------------- 5 · conversa nova ----------------
topo(4, "CONVERSA NOVA")
y = titulo(4, ["Outra conversa,", "mesa vazia"])
y = corpo(4, y, "O que você explicou ontem, em outra conversa, não está na mesa de hoje. Para ela, é como se nunca tivesse acontecido.", tam=37)
x0 = 4 * LADO + MARGEM
for j, (rot, cheia) in enumerate((("ONTEM", True), ("HOJE", False))):
    xx = x0 + j * 470
    rotulo(xx, y + 20, rot, MUTE if cheia else RED_SOFT)
    caixa(xx, y + 58, 440, 270, 20, CARD, LINE if cheia else RED, 2 if cheia else 3)
    if cheia:
        for i in range(4):
            caixa(xx + 24 + (i % 2) * 150, y + 82 + i * 58, 240, 44, 12, (70, 30, 34) if i % 2 else CARD_2, NADA, 0)
    else:
        texto(xx + 220, y + 193, "vazia", "md", 34, MUTE, "mm")

# ---------------- 6 · como resolveram ----------------
topo(5, "COMO RESOLVERAM")
y = titulo(5, ["Um caderno", "de anotações"])
y = corpo(5, y, "As IAs de hoje ganharam um caderno: guardam anotações sobre você e o seu trabalho e colocam essas anotações na mesa quando a conversa começa.", tam=35)
y = corpo(5, y, "Não é lembrança. É texto, relido como todo o resto. E você pode ver e apagar o que está anotado.", tam=35, tipo="sb", cor=FG)
x0 = 5 * LADO + MARGEM
caixa(x0, y + 16, 400, 200, 18, CARD, VERDE)
rotulo(x0 + 22, y + 32, "CADERNO", VERDE)
for i, t in enumerate(("trabalha com manutenção", "prefere respostas curtas", "usa o padrão de relatório")):
    texto(x0 + 22, y + 86 + i * 42, "• " + t, "sans", 25, BODY, "lm")
texto(x0 + 456, y + 116, "→", "b", 56, RED, "mm")
caixa(x0 + 512, y + 16, 400, 200, 18, CARD, RED, 3)
rotulo(x0 + 534, y + 32, "A MESA DE HOJE", RED_SOFT)
caixa(x0 + 534, y + 76, 356, 50, 12, (30, 50, 40), NADA, 0)
texto(x0 + 550, y + 101, "anotações do caderno", "md", 24, FG, "lm")
caixa(x0 + 534, y + 140, 356, 50, 12, (70, 30, 34), NADA, 0)
texto(x0 + 550, y + 165, "sua mensagem nova", "md", 24, FG, "lm")

# ---------------- 7 · na prática ----------------
topo(6, "NA PRÁTICA")
y = titulo(6, ["Cuide do que", "está na mesa"])
y = corpo(6, y, "Ela trabalha com o que enxerga. O resto, para ela, não existe.", tam=37)
x0 = 6 * LADO + MARGEM
for j, (cab, det) in enumerate((("assunto novo, conversa nova", "menos papel velho disputando espaço"),
                                ("conversa longa? peça um resumo e recomece", "leve o resumo e as regras para a conversa nova"),
                                ("entregue o documento junto com a pergunta", "contrato, procedimento, histórico do equipamento"))):
    caixa(x0, y + 14 + j * 124, 912, 108, 16, CARD, LINE)
    texto(x0 + 28, y + 46 + j * 124, cab, "sb", 33, FG, "lm")
    texto(x0 + 28, y + 90 + j * 124, det, "sans", 28, BODY, "lm")

# ---------------- 8 · fechamento ----------------
topo(7, "E VOCÊ?")
y = titulo(7, ["A sua imaginação", "é o limite."], tam=84)
y = corpo(7, y, "Ela não lembra. Ela relê o que está na mesa.", tam=42, tipo="sb", cor=FG)
y = corpo(7, y + 10, "Qual informação você vive repetindo para a IA?", tam=42)
y = corpo(7, y + 10, "Me conta nos comentários.", tam=42, tipo="sb", cor=FG)
rotulo(7 * LADO + MARGEM, y + 50, "Na parte 4: como ela decide o que importa.", RED_SOFT)
texto(7 * LADO + MARGEM, 1050, "@elucas.dev", "mono", 26, MUTE)

salvar(os.path.join(os.path.dirname(os.path.abspath(__file__)), "parte3"))
