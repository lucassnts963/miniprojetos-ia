"""Carrossel do LinkedIn: "IA sem mistério", parte 1 — como a IA escreve um texto.

Um painel contínuo (8 quadros de 1080x1350) cortado em 8 imagens, para quem nunca ouviu falar do assunto.
O que costura tudo é uma frase só, no rodapé, que atravessa os 8 quadros: a própria explicação
("Uma IA que escreve é uma máquina que adivinha a próxima palavra, ..."), escrita palavra por palavra.
É didático: a frase e os palpites são ilustração, não saída do modelo do projeto.

    C:/dev/venv/Scripts/python.exe posts/serie_ia/parte1.py   ->  posts/serie_ia/parte1/

Feito antes do base.py das outras partes, por isso traz as próprias funções de desenho.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONTES = os.path.join(RAIZ, "ferramentas", "youtube", "fonts")
AQUI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parte1")      # pasta de saída

N, LADO, ALT, K, MARGEM = 8, 1080, 1350, 2, 84
INK, CARD, CARD_2 = (12, 12, 15), (22, 22, 26), (31, 31, 36)
RED, RED_SOFT, VERDE = (229, 72, 77), (240, 138, 141), (88, 214, 141)
FG, BODY, MUTE, LINE = (236, 236, 239), (180, 180, 188), (135, 135, 143), (64, 64, 72)
NADA = (0, 0, 0, 0)

img = Image.new("RGB", (N * LADO * K, ALT * K), INK)
d = ImageDraw.Draw(img, "RGBA")
_f = {}


def fonte(tipo, tam):
    nomes = {"sans": "IBMPlexSans-Regular", "md": "IBMPlexSans-Medium", "sb": "IBMPlexSans-SemiBold",
             "b": "IBMPlexSans-Bold", "mono": "IBMPlexMono-Medium"}
    if (tipo, tam) not in _f:
        _f[(tipo, tam)] = ImageFont.truetype(os.path.join(FONTES, nomes[tipo] + ".ttf"), tam * K)
    return _f[(tipo, tam)]


def larg(t, tipo, tam):
    return fonte(tipo, tam).getlength(t) / K


def texto(x, y, t, tipo="sans", tam=36, cor=BODY, ancora="la"):
    d.text((x * K, y * K), t, font=fonte(tipo, tam), fill=cor, anchor=ancora)


def paragrafo(x, y, t, largura, tipo="sans", tam=36, cor=BODY, entre=1.36):
    linha_ = ""
    for palavra in t.split():
        tenta = (linha_ + " " + palavra).strip()
        if larg(tenta, tipo, tam) > largura and linha_:
            texto(x, y, linha_, tipo, tam, cor)
            y += tam * entre
            linha_ = palavra
        else:
            linha_ = tenta
    texto(x, y, linha_, tipo, tam, cor)
    return y + tam * entre


def caixa(x, y, w, h, raio=18, cor=CARD, borda=LINE, esp=2):
    d.rounded_rectangle([x * K, y * K, (x + w) * K, (y + h) * K], radius=raio * K, fill=cor, outline=borda, width=esp * K)


def circulo(x, y, r, cor=None, borda=None, esp=3):
    d.ellipse([(x - r) * K, (y - r) * K, (x + r) * K, (y + r) * K], fill=cor, outline=borda, width=esp * K)


def linha(pontos, cor, esp=3):
    d.line([(px * K, py * K) for px, py in pontos], fill=cor, width=esp * K, joint="curve")


def chip(x, y, t, tam=34, maquina=False):
    """Uma palavra como bloco (vermelho = escrita pela IA). -> largura ocupada"""
    w = larg(t, "md", tam) + 18
    caixa(x, y, w, tam * 1.55, 9, (96, 34, 38) if maquina else (44, 44, 50), NADA, 0)
    texto(x + 9, y + tam * 0.775, t, "md", tam, FG, "lm")
    return w + 8


def frase(x, y, palavras, n_meus, tam=36, largura=912, lacuna=True):
    """A frase em blocos, quebrando linha, com a lacuna da próxima palavra. -> y logo abaixo"""
    cx, cy = x, y
    for i, p in enumerate(palavras):
        w = larg(p, "md", tam) + 26
        if cx + w > x + largura and cx > x:
            cx, cy = x, cy + tam * 1.9
        cx += chip(cx, cy, p, tam, i >= n_meus)
    if lacuna:
        if cx + 130 > x + largura:
            cx, cy = x, cy + tam * 1.9
        caixa(cx, cy, 120, tam * 1.55, 9, NADA, RED, 4)
        texto(cx + 60, cy + tam * 0.78, "?", "b", tam, RED_SOFT, "mm")
    return cy + tam * 1.9


def palpites(x, y, itens, largura=912):
    """Palpites com barras ilustrativas (sem números): itens = [(palavra, tamanho de 0 a 1, escolhida)]."""
    for i, (p, v, on) in enumerate(itens):
        yy = y + i * 70
        texto(x + 200, yy + 22, p, "md", 34, FG if on else BODY, "rm")
        caixa(x + 224, yy + 6, largura - 224, 32, 16, (255, 255, 255, 18), NADA, 0)
        caixa(x + 224, yy + 6, (largura - 224) * v, 32, 16, RED if on else (120, 70, 74), NADA, 0)


def rotulo(x, y, t, cor=MUTE):
    texto(x, y, t, "mono", 25, cor)


def topo(k, capitulo):
    x = k * LADO
    circulo(x + MARGEM + 9, 96, 9, RED)
    texto(x + MARGEM + 30, 96, "elucas.dev", "sb", 26, FG, "lm")
    texto(x + LADO - MARGEM, 96, f"{k + 1:02d} / {N:02d}", "mono", 22, MUTE, "rm")
    texto(x + MARGEM, 214, capitulo, "mono", 23, RED_SOFT)


def titulo(k, linhas, tam=70, y=262):
    for i, t in enumerate(linhas):
        texto(k * LADO + MARGEM, y + i * tam * 1.14, t, "b", tam, FG)
    return y + len(linhas) * tam * 1.14 + 26


def corpo(k, y, t, tam=37, tipo="sans", cor=BODY):
    return paragrafo(k * LADO + MARGEM, y, t, LADO - 2 * MARGEM, tipo, tam, cor) + 12


# ---------------- fundo e o fio ----------------
for gx in range(0, N * LADO, 36):
    for gy in range(18, ALT, 36):
        d.ellipse([(gx + 17) * K, (gy - 1) * K, (gx + 19) * K, (gy + 1) * K], fill=(255, 255, 255, 16))


def fio_y(x):
    return 1200 + 26 * math.sin(x / 520) + 12 * math.sin(x / 190 + 1.3)


pts = [(x, fio_y(x)) for x in range(150, N * LADO - 150, 6)]
linha(pts, RED + (60,), 16)
linha(pts, RED, 6)
circulo(150, fio_y(150), 16, RED)

# uma frase só atravessa os 8 quadros: a própria explicação, escrita palavra por palavra
COMECO = "Uma IA que escreve é".split()
RESTO = "uma máquina que adivinha a próxima palavra, uma de cada vez, até o texto ficar pronto.".split()
FRASE = COMECO + RESTO
TAM_FIO = 44
larguras = [larg(p, "md", TAM_FIO) + 18 for p in FRASE]
ini, fim = 240, N * LADO - 250
vao = (fim - ini - sum(larguras)) / (len(FRASE) - 1)
x = ini
for i, (p, w) in enumerate(zip(FRASE, larguras)):
    chip(x, fio_y(x + w / 2) - 34, p, TAM_FIO, i >= len(COMECO))
    x += w + vao
fx = N * LADO - 150
circulo(fx, fio_y(fx), 44, None, RED + (90,), 4)
circulo(fx, fio_y(fx), 20, RED)

# ---------------- 1 · capa ----------------
topo(0, "IA SEM MISTÉRIO · PARTE 1")
y = titulo(0, ["Como a IA", "escreve", "um texto?"], tam=96)
y = corpo(0, y + 10, "Não é mágica, e ela não pensa como a gente. É um mecanismo simples, que cabe em 8 imagens.", tam=42)
corpo(0, y + 16, "Sem termo técnico.", tam=42, tipo="sb", cor=FG)
rotulo(MARGEM, 1040, "arraste e leia a frase aqui embaixo  →", RED_SOFT)

# ---------------- 2 · você já viu ----------------
topo(1, "VOCÊ JÁ VIU ISSO")
y = titulo(1, ["No teclado do", "seu celular"])
y = corpo(1, y, "Você digita “Bom” e ele sugere “dia”. O teclado não entende a conversa. Ele só sabe que, depois de “Bom”, quase sempre vem “dia”.", tam=38)
x0 = LADO + 200
caixa(x0, y + 30, 680, 290, 34, CARD, LINE)
caixa(x0 + 36, y + 66, 608, 84, 18, (255, 255, 255, 14), NADA, 0)
texto(x0 + 64, y + 108, "Bom |", "md", 40, FG, "lm")
for j, palavra in enumerate(("dia", "trabalho", "descanso")):
    w = larg(palavra, "md", 32) + 44
    xx = x0 + 60 + j * 205
    caixa(xx, y + 196, w, 64, 14, (70, 30, 34) if j == 0 else CARD_2, RED if j == 0 else LINE)
    texto(xx + w / 2, y + 228, palavra, "md", 32, FG, "mm")

# ---------------- 3 · a ideia ----------------
topo(2, "A IDEIA")
y = titulo(2, ["A IA faz o mesmo:", "adivinha a", "próxima palavra"], tam=64)
y = corpo(2, y, "Ela olha o texto que já existe e dá um palpite para a palavra seguinte.", tam=38)
x0 = 2 * LADO + MARGEM
y = frase(x0, y + 16, COMECO + RESTO[:5], len(COMECO), 36)
rotulo(x0, y + 4, "OS PALPITES DELA")
palpites(x0, y + 46, [("próxima", 1.0, True), ("resposta", 0.45, False), ("melhor", 0.22, False)])

# ---------------- 4 · o truque ----------------
topo(3, "O TRUQUE")
y = titulo(3, ["Escolhe uma.", "E repete."])
y = corpo(3, y, "Ela cola a palavra escolhida no texto e adivinha a seguinte. Uma de cada vez, até o texto ficar pronto.", tam=38)
x0 = 3 * LADO + MARGEM
for etapa, n in enumerate((6, 9, 17)):
    y = frase(x0, y + 22, FRASE[:len(COMECO) + n], len(COMECO), 30, lacuna=etapa < 2) + 6
rotulo(x0, y + 8, "em vermelho: o que ela escreveu", RED_SOFT)

# ---------------- 5 · de onde vêm os palpites ----------------
topo(4, "DE ONDE VÊM OS PALPITES")
y = titulo(4, ["Ela leu muito.", "Muito mesmo."])
y = corpo(4, y, "Antes de conversar com você, a IA leu uma quantidade enorme de textos: livros, sites, artigos.", tam=38)
y = corpo(4, y, "De tanto ler, aprendeu o que costuma vir depois do quê.", tam=38, tipo="sb", cor=FG)
x0 = 4 * LADO + MARGEM
for j in range(7):                                             # pilha de textos lidos
    caixa(x0 + 10 + j * 30, y + 36 + j * 15, 340, 190, 14, CARD_2, LINE)
for j, fr in enumerate((0.8, 0.6, 0.72, 0.5)):
    caixa(x0 + 216, y + 160 + j * 30, 280 * fr, 10, 5, (90, 90, 100), NADA, 0)
texto(x0 + 610, y + 180, "→", "b", 60, RED, "mm")
texto(x0 + 790, y + 156, "depois de “Bom”,", "md", 30, BODY, "mm")
texto(x0 + 790, y + 202, "vem “dia”", "sb", 36, FG, "mm")

# ---------------- 6 · o cuidado ----------------
topo(5, "O CUIDADO")
y = titulo(5, ["Ela não consulta", "um arquivo de", "respostas"], tam=64)
y = corpo(5, y, "O texto é escrito na hora, palavra por palavra. Por isso sai tão natural.", tam=38)
y = corpo(5, y, "E por isso ela pode escrever algo errado com a mesma segurança de quando acerta.", tam=38, tipo="sb", cor=FG)
x0 = 5 * LADO + MARGEM
caixa(x0, y + 26, 912, 90, 18, CARD, VERDE)
texto(x0 + 28, y + 71, "soa bem e está certo", "md", 34, FG, "lm")
caixa(x0, y + 134, 912, 90, 18, CARD, RED)
texto(x0 + 28, y + 179, "soa bem e está errado", "md", 34, FG, "lm")
rotulo(x0, y + 246, "para ela, os dois são só “a próxima palavra”")

# ---------------- 7 · na prática ----------------
topo(6, "NA PRÁTICA")
y = titulo(6, ["O começo", "é tudo"])
y = corpo(6, y, "Ela continua o que você começa. Pedido vago recebe a resposta mais comum, que serve para qualquer um.", tam=36)
x0 = 6 * LADO + MARGEM
rotulo(x0, y + 6, "PEDIDO VAGO")
caixa(x0, y + 44, 912, 80, 18, CARD, LINE)
texto(x0 + 28, y + 84, "Faça um relatório.", "md", 34, FG, "lm")
rotulo(x0, y + 150, "COMEÇO CLARO", VERDE)
caixa(x0, y + 188, 912, 300, 18, CARD, VERDE)
for j, (rot, val) in enumerate((("quem ela deve ser", "Você é planejador de manutenção."),
                                ("a situação", "Estas são as paradas do mês."),
                                ("como você quer a resposta", "Resuma em tópicos, para a diretoria."))):
    texto(x0 + 28, y + 208 + j * 92, rot, "mono", 23, RED_SOFT)
    texto(x0 + 28, y + 240 + j * 92, val, "md", 33, FG)

# ---------------- 8 · fechamento ----------------
topo(7, "E VOCÊ?")
y = titulo(7, ["A sua imaginação", "é o limite."], tam=84)
y = corpo(7, y, "Quem entende como funciona, pede melhor.", tam=42, tipo="sb", cor=FG)
y = corpo(7, y + 10, "Qual pedido você fez a uma IA e a resposta veio genérica demais?", tam=42)
y = corpo(7, y + 10, "Me conta nos comentários.", tam=42, tipo="sb", cor=FG)
rotulo(7 * LADO + MARGEM, y + 50, "Na parte 2: por que ela erra contas simples.", RED_SOFT)
texto(7 * LADO + MARGEM, 1050, "@elucas.dev", "mono", 26, MUTE)

# ---------------- saída ----------------
final = img.resize((N * LADO, ALT), Image.LANCZOS)
final.save(os.path.join(AQUI, "panorama.png"))
quadros = [final.crop((k * LADO, 0, (k + 1) * LADO, ALT)) for k in range(N)]
for k, q in enumerate(quadros):
    q.save(os.path.join(AQUI, f"{k + 1:02d}.png"))
quadros[0].save(os.path.join(AQUI, "carrossel.pdf"), save_all=True, append_images=quadros[1:], resolution=144)
print("ok:", AQUI)
