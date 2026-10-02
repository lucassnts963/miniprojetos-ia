"""Peças comuns dos carrosséis da série "IA sem mistério" (painel contínuo de 8 quadros de 1080x1350).

Cada parte importa este módulo, desenha os quadros e chama salvar(pasta). A frase do rodapé (fio) atravessa
os 8 quadros. A parte 1 foi feita antes deste módulo e fica em 06-completar-texto/carrossel/.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONTES = os.path.join(RAIZ, "ferramentas", "youtube", "fonts")

N, LADO, ALT, K, MARGEM = 8, 1080, 1350, 2, 84
INK, CARD, CARD_2 = (12, 12, 15), (22, 22, 26), (31, 31, 36)
RED, RED_SOFT, VERDE = (229, 72, 77), (240, 138, 141), (88, 214, 141)
FG, BODY, MUTE, LINE = (236, 236, 239), (180, 180, 188), (135, 135, 143), (64, 64, 72)
NADA = (0, 0, 0, 0)
CINZA, VINHO = (44, 44, 50), (96, 34, 38)

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


def chip(x, y, t, tam=34, cor=CINZA, tipo="md", folga=9):
    """Um bloco de texto. -> largura do bloco"""
    w = larg(t, tipo, tam) + 2 * folga
    caixa(x, y, w, tam * 1.55, 9, cor, NADA, 0)
    texto(x + folga, y + tam * 0.775, t, tipo, tam, FG, "lm")
    return w


def chips(x, y, itens, tam=34, largura=912, vao=8, tipo="md"):
    """Vários blocos em linha, quebrando quando não cabe. itens = [(texto, cor)]. -> (x, y) depois do último"""
    cx, cy = x, y
    for t, cor in itens:
        w = larg(t, tipo, tam) + 18
        if cx + w > x + largura and cx > x:
            cx, cy = x, cy + tam * 1.9
        cx += chip(cx, cy, t, tam, cor, tipo) + vao
    return cx, cy


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


def fio_y(x):
    return 1200 + 26 * math.sin(x / 520) + 12 * math.sin(x / 190 + 1.3)


def fundo_e_fio(itens, tam=44):
    """Grade de pontos, a linha vermelha e a frase do rodapé espalhada pelos 8 quadros. itens = [(texto, cor)]"""
    for gx in range(0, N * LADO, 36):
        for gy in range(18, ALT, 36):
            d.ellipse([(gx + 17) * K, (gy - 1) * K, (gx + 19) * K, (gy + 1) * K], fill=(255, 255, 255, 16))
    pts = [(x, fio_y(x)) for x in range(150, N * LADO - 150, 6)]
    linha(pts, RED + (60,), 16)
    linha(pts, RED, 6)
    circulo(150, fio_y(150), 16, RED)
    larguras = [larg(t, "md", tam) + 18 for t, _ in itens]
    ini, fim = 240, N * LADO - 250
    vao = (fim - ini - sum(larguras)) / (len(itens) - 1)
    x = ini
    for (t, cor), w in zip(itens, larguras):
        chip(x, fio_y(x + w / 2) - tam * 0.775, t, tam, cor)
        x += w + vao
    fx = N * LADO - 150
    circulo(fx, fio_y(fx), 44, None, RED + (90,), 4)
    circulo(fx, fio_y(fx), 20, RED)


def salvar(pasta):
    os.makedirs(pasta, exist_ok=True)
    final = img.resize((N * LADO, ALT), Image.LANCZOS)
    final.save(os.path.join(pasta, "panorama.png"))
    quadros = [final.crop((k * LADO, 0, (k + 1) * LADO, ALT)) for k in range(N)]
    for k, q in enumerate(quadros):
        q.save(os.path.join(pasta, f"{k + 1:02d}.png"))
    quadros[0].save(os.path.join(pasta, "carrossel.pdf"), save_all=True, append_images=quadros[1:], resolution=144)
    print("ok:", pasta)
