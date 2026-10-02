"""Carrossel do LinkedIn: "Como uma LLM funciona", parte 1 — a máquina de completar texto.

Um painel contínuo (8 quadros de 1080x1350) cortado em 8 imagens. O que costura tudo é a própria frase
que a máquina escreveu, pedaço por pedaço, andando sobre a linha vermelha e atravessando as emendas.
As apostas e os textos vêm do modelo treinado (video/dados.json, feito por video/preparar.py).

    C:/dev/venv/Scripts/python.exe 06-completar-texto/carrossel/carrossel.py
    -> carrossel/01.png ... 08.png, panorama.png e carrossel.pdf
"""
import json
import math
import os

from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(AQUI)
FONTES = os.path.join(os.path.dirname(PROJ), "ferramentas", "youtube", "fonts")
with open(os.path.join(PROJ, "video", "dados.json"), encoding="utf-8") as f:
    D = json.load(f)

N, LADO, ALT, K, MARGEM = 8, 1080, 1350, 2, 84
INK, CARD, CARD_2 = (12, 12, 15), (22, 22, 26), (31, 31, 36)
RED, RED_SOFT, VERDE = (229, 72, 77), (240, 138, 141), (88, 214, 141)
FG, BODY, MUTE, LINE = (236, 236, 239), (180, 180, 188), (135, 135, 143), (64, 64, 72)

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
    linha = ""
    for palavra in t.split():
        tenta = (linha + " " + palavra).strip()
        if larg(tenta, tipo, tam) > largura and linha:
            texto(x, y, linha, tipo, tam, cor)
            y += tam * entre
            linha = palavra
        else:
            linha = tenta
    texto(x, y, linha, tipo, tam, cor)
    return y + tam * entre


def caixa(x, y, w, h, raio=18, cor=CARD, borda=LINE, esp=2):
    d.rounded_rectangle([x * K, y * K, (x + w) * K, (y + h) * K], radius=raio * K, fill=cor, outline=borda, width=esp * K)


def circulo(x, y, r, cor=None, borda=None, esp=3):
    d.ellipse([(x - r) * K, (y - r) * K, (x + r) * K, (y + r) * K], fill=cor, outline=borda, width=esp * K)


def linha(pontos, cor, esp=3):
    d.line([(px * K, py * K) for px, py in pontos], fill=cor, width=esp * K, joint="curve")


def chip(x, y, t, tam=34, maquina=False, borda=None, tipo="md"):
    """Um pedaço de texto como bloco. -> largura ocupada"""
    t = t.replace("\n", " ")
    w = larg(t, tipo, tam) + 14
    caixa(x, y, w, tam * 1.55, 9, RED + (80,) if maquina else (255, 255, 255, 22), borda or (0, 0, 0, 0), 3 if borda else 0)
    texto(x + 7, y + tam * 0.775, t, tipo, tam, FG, "lm")
    return w + 7


def chips(x, y, pedacos, largura, tam=34, n_meus=99, borda=None):
    """Vários pedaços, quebrando linha. -> (x, y) logo depois do último"""
    cx, cy = x, y
    for i, p in enumerate(pedacos):
        w = larg(p, "md", tam) + 21
        if cx + w > x + largura and cx > x:
            cx, cy = x, cy + tam * 1.9
            p = p.lstrip()
        cx += chip(cx, cy, p, tam, i >= n_meus, borda(i) if borda else None)
    return cx, cy


def barras(x, y, apostas, largura, escolhido=None, n=5, tam=28):
    maior = max(a["p"] for a in apostas[:n])
    for i, a in enumerate(apostas[:n]):
        yy = y + i * 58
        on = a["pedaco"] == escolhido
        texto(x + 210, yy + 18, a["pedaco"].strip() or "espaço", "mono", tam, FG if on else BODY, "rm")
        caixa(x + 230, yy + 5, largura - 230, 26, 13, (255, 255, 255, 18), (0, 0, 0, 0), 0)
        caixa(x + 230, yy + 5, max(26, (largura - 230) * a["p"] / maior), 26, 13, RED if on else (120, 70, 74), (0, 0, 0, 0), 0)


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
    return 1215 + 26 * math.sin(x / 520) + 12 * math.sin(x / 190 + 1.3)


pts = [(x, fio_y(x)) for x in range(150, N * LADO - 150, 6)]
linha(pts, RED + (60,), 16)
linha(pts, RED, 6)
circulo(150, fio_y(150), 16, RED)

# a frase que a máquina escreveu anda sobre o fio, atravessando as emendas
FRASE = D["pedacos"] + [p["pedaco"] for p in D["passos"]]
x = 250.0
i = 0
while x < N * LADO - 420:
    p = FRASE[i % len(FRASE)]
    w = larg(p.replace("\n", " "), "md", 30) + 14
    maquina = i % len(FRASE) >= len(D["pedacos"])
    chip(x, fio_y(x + w / 2) - 23, p, 30, maquina)
    x += w + (150 if (i + 1) % len(FRASE) == 0 else 34)
    i += 1
fx = N * LADO - 150
circulo(fx, fio_y(fx), 44, None, RED + (90,), 4)
circulo(fx, fio_y(fx), 20, RED)

# ---------------- 1 · capa ----------------
topo(0, "COMO FUNCIONA A IA QUE ESCREVE · PARTE 1")
y = titulo(0, ["Uma máquina", "de completar", "texto"], tam=92)
corpo(0, y + 10, "É só isso que a IA que escreve faz. Entender esse mecanismo muda o jeito de pedir.", tam=40)
cx, cy = chips(MARGEM, 850, D["pedacos"], 900, 44)
caixa(cx + 4, cy, 130, 68, 10, (0, 0, 0, 0), RED, 4)
texto(cx + 69, cy + 34, "?", "b", 44, RED_SOFT, "mm")
texto(MARGEM, 1000, "arraste  →", "mono", 24, MUTE)

# ---------------- 2 · você já usa ----------------
topo(1, "VOCÊ JÁ USA")
y = titulo(1, ["O teclado do", "seu celular"])
y = corpo(1, y, "Você digita uma palavra e ele sugere a próxima. Ele não entende a conversa: só aposta no que costuma vir depois.")
x0 = LADO + 200
caixa(x0, 760, 680, 300, 34, CARD, LINE)
caixa(x0 + 36, 796, 608, 84, 18, (255, 255, 255, 14), (0, 0, 0, 0), 0)
texto(x0 + 64, 838, "Bom |", "md", 40, FG, "lm")
for j, palavra in enumerate(("dia", "trabalho", "descanso")):
    w = larg(palavra, "md", 32) + 44
    xx = x0 + 60 + j * 205
    caixa(xx, 930, w, 64, 14, (70, 30, 34) if j == 0 else CARD_2, RED if j == 0 else LINE)
    texto(xx + w / 2, 962, palavra, "md", 32, FG, "mm")

# ---------------- 3 · a ideia ----------------
topo(2, "A IDEIA")
y = titulo(2, ["Apostar no", "próximo pedaço"])
y = corpo(2, y, "A IA que escreve faz o mesmo. Dado um começo, ela calcula a chance de cada pedaço de texto ser o próximo.")
x0 = 2 * LADO + MARGEM
cx, cy = chips(x0, y + 20, D["pedacos"], 900, 38)
caixa(cx + 4, cy, 100, 59, 10, (0, 0, 0, 0), RED, 4)
texto(x0, y + 120, "AS APOSTAS", "mono", 21, MUTE)
barras(x0, y + 160, D["passos"][0]["apostas"], 900, escolhido=D["passos"][0]["pedaco"])

# ---------------- 4 · o truque ----------------
topo(3, "O TRUQUE")
y = titulo(3, ["Escolhe um.", "Aposta de novo."])
y = corpo(3, y, "Ela cola o pedaço escolhido no texto e repete. Um pedaço de cada vez, até a resposta ficar pronta.")
x0 = 3 * LADO + MARGEM
for etapa, n in enumerate((1, 4, 9)):
    yy = y + 20 + etapa * 150
    texto(x0, yy, f"{'depois' if etapa else 'primeiro'}", "mono", 20, MUTE)
    chips(x0, yy + 34, FRASE[:len(D["pedacos"]) + n], 900, 30, len(D["pedacos"]))
texto(x0, y + 480, "em vermelho: o que a máquina escreveu", "mono", 20, RED_SOFT)

# ---------------- 5 · contar x rede ----------------
topo(4, "O SALTO")
y = titulo(4, ["Olhar o texto", "inteiro"])
y = corpo(4, y, "Só contando o que vem depois das últimas palavras, a máquina perde o assunto. A rede neural pesa tudo o que já foi escrito.", tam=34)
x0 = 4 * LADO + MARGEM
base = D["compara_pedacos"]
for j, (nome, chave, cor) in enumerate((("SÓ CONTANDO", "compara_contagem", LINE), ("REDE NEURAL", "compara_rede", RED))):
    yy = y + 6 + j * 226
    caixa(x0 - 20, yy, 952, 210, 20, CARD, cor)
    texto(x0, yy + 16, nome, "mono", 20, MUTE if j == 0 else RED_SOFT)
    ped = base + D[chave][:17 if j == 0 else 19]
    vistos = range(len(ped) - 3, len(ped)) if j == 0 else range(len(ped))
    chips(x0, yy + 50, ped, 900, 25, len(base), borda=lambda i, v=vistos: VERDE if i in v else None)
texto(x0, y + 470, "contorno verde: o que ela enxerga ao decidir", "mono", 20, VERDE)

# ---------------- 6 · a escala ----------------
topo(5, "A ESCALA")
y = titulo(5, ["A mesma tarefa,", "em tamanho gigante"], tam=64)
y = corpo(5, y, "A minha, treinada do zero num notebook, erra bastante. As grandes leram uma parte enorme do que a humanidade escreveu. Resumir, traduzir, responder, programar: tudo é continuar um texto.", tam=34)
x0 = 5 * LADO
caixa(x0 + 110, y + 90, 230, 230, 20, CARD, LINE)
for j in range(25):
    circulo(x0 + 157 + (j % 5) * 34, y + 137 + (j // 5) * 34, 7, RED_SOFT)
texto(x0 + 225, y + 340, "a minha", "sb", 28, FG, "ma")
caixa(x0 + 480, y + 10, 420, 310, 20, CARD, RED)
for gx in range(22):
    for gy in range(16):
        circulo(x0 + 500 + gx * 18, y + 30 + gy * 18, 3, tuple(int(INK[c] + (RED[c] - INK[c]) * (0.4 + 0.6 * abs(math.sin(gx * 0.7 + gy * 1.3)))) for c in range(3)))
texto(x0 + 690, y + 340, "as grandes", "sb", 28, FG, "ma")

# ---------------- 7 · na prática ----------------
topo(6, "NA PRÁTICA")
y = titulo(6, ["O começo", "é tudo"])
y = corpo(6, y, "Ela continua o que você começa. Pedido vago aceita qualquer continuação, e você recebe a mais comum.", tam=35)
x0 = 6 * LADO + MARGEM
texto(x0, y + 4, "PEDIDO VAGO", "mono", 20, MUTE)
caixa(x0, y + 36, 912, 78, 18, CARD, LINE)
texto(x0 + 28, y + 75, "Faça um relatório.", "md", 32, FG, "lm")
texto(x0, y + 146, "COMEÇO CLARO", "mono", 20, VERDE)
caixa(x0, y + 178, 912, 292, 18, CARD, VERDE)
for j, (rot, val) in enumerate((("papel", "Você é planejador de manutenção."), ("contexto", "Estas são as paradas do mês."),
                                ("formato", "Resuma em tópicos, para a diretoria."))):
    texto(x0 + 28, y + 200 + j * 88, rot, "mono", 20, RED_SOFT)
    texto(x0 + 28, y + 228 + j * 88, val, "md", 32, FG)

# ---------------- 8 · fechamento ----------------
topo(7, "E VOCÊ?")
y = titulo(7, ["A sua imaginação", "é o limite."], tam=84)
y = corpo(7, y, "Quem entende como funciona, pede melhor.", tam=40, tipo="sb", cor=FG)
y = corpo(7, y + 10, "Qual pedido você fez a uma IA e a resposta voltou mais longe do que esperava?", tam=40)
texto(7 * LADO + MARGEM, y + 40, "Próxima parte: ela não lê palavras, lê pedaços.", "mono", 24, RED_SOFT)
texto(7 * LADO + MARGEM, 1070, "@elucas.dev", "mono", 26, MUTE)

# ---------------- saída ----------------
final = img.resize((N * LADO, ALT), Image.LANCZOS)
final.save(os.path.join(AQUI, "panorama.png"))
quadros = [final.crop((k * LADO, 0, (k + 1) * LADO, ALT)) for k in range(N)]
for k, q in enumerate(quadros):
    q.save(os.path.join(AQUI, f"{k + 1:02d}.png"))
quadros[0].save(os.path.join(AQUI, "carrossel.pdf"), save_all=True, append_images=quadros[1:], resolution=144)
print("ok:", AQUI)
