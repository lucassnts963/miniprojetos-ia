"""Carrossel do LinkedIn para o post da base de conhecimento viva (LLM Wiki).

Desenha UM painel contínuo (8 quadros de 1080x1350 lado a lado) e corta em 8 imagens: a linha
vermelha e as ilustrações atravessam as emendas, então cada imagem continua a anterior.

    C:/dev/venv/Scripts/python.exe posts/carrossel_llm_wiki.py
    -> posts/carrossel_llm_wiki/01.png ... 08.png, panorama.png e carrossel.pdf
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTES = os.path.join(os.path.dirname(AQUI), "ferramentas", "youtube", "fonts")
SAIDA = os.path.join(AQUI, "carrossel_llm_wiki")

N, LADO, ALT = 8, 1080, 1350
K = 2                                   # desenha no dobro e reduz (bordas lisas)
MARGEM = 84

INK, CARD, CARD_2 = (12, 12, 15), (22, 22, 26), (31, 31, 36)
RED, RED_SOFT = (229, 72, 77), (240, 138, 141)
FG, BODY, MUTE, LINE = (236, 236, 239), (180, 180, 188), (135, 135, 143), (44, 44, 50)
VERDE = (88, 214, 141)

img = Image.new("RGB", (N * LADO * K, ALT * K), INK)
d = ImageDraw.Draw(img, "RGBA")
_f = {}


def fonte(tipo, tam):
    nomes = {"sans": "IBMPlexSans-Regular", "md": "IBMPlexSans-Medium", "sb": "IBMPlexSans-SemiBold",
             "b": "IBMPlexSans-Bold", "mono": "IBMPlexMono-Medium"}
    if (tipo, tam) not in _f:
        _f[(tipo, tam)] = ImageFont.truetype(os.path.join(FONTES, nomes[tipo] + ".ttf"), tam * K)
    return _f[(tipo, tam)]


def s(*v):
    return [x * K for x in v] if len(v) > 1 else v[0] * K


def texto(x, y, t, tipo="sans", tam=36, cor=BODY, ancora="la", espaco=0):
    f = fonte(tipo, tam)
    if espaco:                                           # letras espaçadas (rótulos em caixa alta)
        for ch in t:
            d.text((x * K, y * K), ch, font=f, fill=cor, anchor=ancora)
            x += f.getlength(ch) / K + espaco
        return
    d.text((x * K, y * K), t, font=f, fill=cor, anchor=ancora)


def paragrafo(x, y, t, largura, tipo="sans", tam=36, cor=BODY, entre=1.36):
    """Quebra o texto na largura e devolve o y logo abaixo."""
    f = fonte(tipo, tam)
    linha = ""
    for palavra in t.split():
        tenta = (linha + " " + palavra).strip()
        if f.getlength(tenta) / K > largura and linha:
            texto(x, y, linha, tipo, tam, cor)
            y += tam * entre
            linha = palavra
        else:
            linha = tenta
    texto(x, y, linha, tipo, tam, cor)
    return y + tam * entre


def caixa(x, y, w, h, raio=18, cor=CARD, borda=LINE, esp=2):
    d.rounded_rectangle(s(x, y, x + w, y + h), radius=raio * K, fill=cor, outline=borda, width=esp * K)


def circulo(x, y, r, cor=None, borda=None, esp=3):
    d.ellipse(s(x - r, y - r, x + r, y + r), fill=cor, outline=borda, width=esp * K)


def linha(pontos, cor, esp=3):
    d.line([(px * K, py * K) for px, py in pontos], fill=cor, width=esp * K, joint="curve")


# ---------------- a linha que costura tudo ----------------
PONTOS_FIO = [(150, 1120), (700, 1170), (1250, 1090), (1900, 1180), (2500, 1120), (3240, 1170), (3900, 1110),
              (4320, 1160), (4900, 1215), (5400, 1170), (5950, 1225), (6480, 1200), (7100, 1262), (7560, 1235),
              (8100, 1120)]


def fio_y(x):
    """Altura do fio em x (interpolação suave entre os pontos)."""
    p = PONTOS_FIO
    if x <= p[0][0]:
        return p[0][1]
    for (x0, y0), (x1, y1) in zip(p, p[1:]):
        if x <= x1:
            k = (x - x0) / (x1 - x0)
            k = (1 - math.cos(k * math.pi)) / 2
            return y0 + (y1 - y0) * k
    return p[-1][1]


def fio():
    pts = [(x, fio_y(x)) for x in range(PONTOS_FIO[0][0], PONTOS_FIO[-1][0] + 1, 6)]
    linha(pts, RED + (60,), 16)
    linha(pts, RED, 6)


# ---------------- peças ----------------
def documento(cx, cy, ang, rotulo, w=190, h=236):
    """Folha inclinada com um rótulo e linhas de texto."""
    folha = Image.new("RGBA", (w * K, h * K), (0, 0, 0, 0))
    g = ImageDraw.Draw(folha)
    g.rounded_rectangle([0, 0, w * K - 1, h * K - 1], radius=14 * K, fill=CARD_2, outline=(70, 70, 78), width=2 * K)
    g.text((20 * K, 20 * K), rotulo, font=fonte("mono", 19), fill=RED_SOFT)
    for i, frac in enumerate((0.8, 0.62, 0.74, 0.5, 0.68)):
        yy = (70 + i * 30) * K
        g.rounded_rectangle([20 * K, yy, int(20 * K + (w - 40) * K * frac), yy + 9 * K], radius=4 * K, fill=(74, 74, 84))
    folha = folha.rotate(ang, resample=Image.BICUBIC, expand=True)
    img.paste(folha, (int(cx * K - folha.width / 2), int(cy * K - folha.height / 2)), folha)


def pagina(cx, cy, w=120, h=88, viva=False):
    caixa(cx - w / 2, cy - h / 2, w, h, 12, CARD_2, RED if viva else (70, 70, 78))
    for i, frac in enumerate((0.7, 0.5, 0.62)):
        yy = cy - h / 2 + 20 + i * 20
        d.rounded_rectangle(s(cx - w / 2 + 16, yy, cx - w / 2 + 16 + (w - 32) * frac, yy + 7), radius=3 * K,
                            fill=RED_SOFT if viva and i == 0 else (74, 74, 84))


def ligacao(a, b, cor=(90, 90, 100), esp=3):
    linha([a, b], cor, esp)


def visto(cx, cy, r):
    circulo(cx, cy, r, CARD, VERDE, 5)
    linha([(cx - r * 0.42, cy + r * 0.02), (cx - r * 0.1, cy + r * 0.34), (cx + r * 0.46, cy - r * 0.32)], VERDE, 9)


def topo(k, capitulo):
    x = k * LADO
    circulo(x + MARGEM + 9, 96, 9, RED)
    texto(x + MARGEM + 30, 96, "elucas.dev", "sb", 26, FG, "lm")
    texto(x + LADO - MARGEM, 96, f"{k + 1:02d} / {N:02d}", "mono", 22, MUTE, "rm")
    if capitulo:
        texto(x + MARGEM, 214, capitulo, "mono", 23, RED_SOFT, espaco=3)


def titulo(k, linhas, y=262, tam=74):
    for i, t in enumerate(linhas):
        texto(k * LADO + MARGEM, y + i * tam * 1.14, t, "b", tam, FG)
    return y + len(linhas) * tam * 1.14


def item(k, y, cabeca, corpo, tam=37, largura=LADO - 2 * MARGEM - 46):
    x = k * LADO + MARGEM
    circulo(x + 10, y + 25, 8, RED)
    texto(x + 46, y, cabeca, "sb", tam + 3, FG)
    return paragrafo(x + 46, y + (tam + 3) * 1.4, corpo, largura, "sans", tam, BODY) + 30


# ---------------- fundo ----------------
for gx in range(0, N * LADO, 36):
    for gy in range(18, ALT, 36):
        d.ellipse(s(gx + 17, gy - 1, gx + 19, gy + 1), fill=(255, 255, 255, 16))
for cx, cy, r in ((1080, 1010, 430), (3240, 1180, 380), (5400, 1330, 330), (7560, 1300, 420)):   # anéis nas emendas
    d.ellipse(s(cx - r, cy - r, cx + r, cy + r), outline=(255, 255, 255, 13), width=3 * K)
    d.ellipse(s(cx - r * 0.62, cy - r * 0.62, cx + r * 0.62, cy + r * 0.62), outline=RED + (30,), width=3 * K)
fio()

# ---------------- 1 · capa ----------------
topo(0, "BASE DE CONHECIMENTO VIVA")
y = titulo(0, ["Onde está o", "conhecimento", "da sua empresa?"], tam=88)
paragrafo(MARGEM, y + 30, "Num lugar que todos consultam, ou na cabeça de quem está há mais tempo na casa?",
          LADO - 2 * MARGEM, tam=39)
circulo(150, 1120, 20, RED)
circulo(150, 1120, 36, None, RED + (90,), 4)
texto(210, 1010, "arraste", "mono", 24, MUTE, espaco=3)
linha([(360, 1026), (440, 1026)], MUTE, 3)
linha([(424, 1012), (440, 1026), (424, 1040)], MUTE, 3)

# ---------------- 2 · o problema ----------------
topo(1, "O PROBLEMA")
y = titulo(1, ["O conhecimento", "está espalhado"])
y = paragrafo(LADO + MARGEM, y + 30, "Procedimento numa pasta, histórico em e-mail, decisão em ata que ninguém relê.",
              LADO - 2 * MARGEM, tam=37)
paragrafo(LADO + MARGEM, y + 14, "Quando alguém sai, parte da resposta vai junto.", LADO - 2 * MARGEM, "sb", 37, FG)
for cx, cy, ang, rot in ((960, 960, 14, "e-mail"), (1150, 1160, -11, "ata"), (1420, 930, 8, "relatório"),
                         (1640, 1140, -16, "planilha"), (1880, 950, 12, "foto"), (2110, 1060, -7, "contrato")):
    documento(cx, cy, ang, rot)

# ---------------- 3 · a ideia ----------------
topo(2, "A IDEIA")
y = titulo(2, ["A IA mantém", "uma wiki"])
y = paragrafo(2 * LADO + MARGEM, y + 30, "Em vez de reler todos os documentos a cada pergunta, a IA lê cada documento "
              "novo, resume e liga ao que já existia.", LADO - 2 * MARGEM, tam=37)
y = paragrafo(2 * LADO + MARGEM, y + 14, "O conhecimento se acumula.", LADO - 2 * MARGEM, "sb", 37, FG)
texto(2 * LADO + MARGEM, y + 26, "Ideia do pesquisador Andrej Karpathy", "mono", 22, MUTE)
# as folhas viram páginas ligadas (a rede atravessa a emenda 3|4)
REDE = [(2560, 1010), (2760, 1150), (2900, 960), (3070, 1100), (3240, 1000), (3400, 1190), (3570, 1075)]
for a, b in ((0, 1), (0, 2), (1, 3), (2, 3), (2, 4), (3, 4), (3, 5), (4, 6), (5, 6), (4, 5)):
    ligacao(REDE[a], REDE[b])
for i, (cx, cy) in enumerate(REDE):
    pagina(cx, cy, viva=i in (3, 4))

# ---------------- 4 · como funciona ----------------
topo(3, "COMO FUNCIONA")
y = titulo(3, ["Entrar, perguntar,", "auditar"]) + 26
y = item(3, y, "Entrar", "O documento novo é lido, resumido e ligado às páginas que já existem.")
y = item(3, y, "Perguntar", "A resposta vem das páginas e aponta a fonte.")
y = item(3, y, "Auditar", "De tempos em tempos, a IA procura contradições e informação vencida.")

# ---------------- 5 · adaptações: gente aprova ----------------
topo(4, "MINHAS ADAPTAÇÕES")
y = titulo(4, ["Gente aprova,", "IA mantém"]) + 26
y = item(4, y, "Nada entra sem aprovação", "O material novo espera a revisão de uma pessoa.")
y = item(4, y, "Tudo aponta para a fonte", "Se não está no documento, a IA não escreve.")
y = item(4, y, "O original não muda", "A fonte fica guardada como chegou.")
visto(4320, fio_y(4320), 78)                                             # o "aprovado" fica na emenda 4|5
# citação: páginas apontando para a fonte (atravessa a emenda 5|6)
documento(5290, 1085, -6, "fonte", 150, 186)
for cx in (5480, 5620):
    pagina(cx, 1060 if cx == 5480 else 1105, 110, 80, viva=cx == 5480)
ligacao((5365, 1085), (5425, 1065), RED_SOFT, 3)
ligacao((5535, 1068), (5565, 1095), RED_SOFT, 3)

# ---------------- 6 · adaptações: acompanha o trabalho ----------------
topo(5, "MINHAS ADAPTAÇÕES")
y = titulo(5, ["Uma base que", "acompanha o trabalho"], tam=68) + 26
y = item(5, y, "O que está vivo", "Um espaço para o foco do momento e as pendências.")
y = item(5, y, "O que se repete vira regra", "E a regra passa a valer sempre.")
y = item(5, y, "Uma base por projeto", "O que serve para todos sobe para a base central.")
# bases de projeto ligadas à central (atravessa a emenda 6|7)
HUB = (6480, 1168)
for i, ang in enumerate((150, 195, 240, 60, -12, 25)):
    px, py = HUB[0] + 205 * math.cos(math.radians(ang)), HUB[1] + 118 * math.sin(math.radians(ang))
    ligacao(HUB, (px, py), (100, 100, 110), 3)
    circulo(px, py, 24, CARD_2, (110, 110, 120), 3)
circulo(*HUB, 52, CARD, RED, 5)
circulo(*HUB, 18, RED)

# ---------------- 7 · onde se aplica ----------------
topo(6, "ONDE SE APLICA")
y = titulo(6, ["Do chão de fábrica", "ao escritório"], tam=68) + 18
for cab, corpo in (("Indústria e PCM", "histórico de cada equipamento e lições de cada parada"),
                   ("Planejamento", "premissas, restrições e o porquê de cada mudança"),
                   ("Construção e projetos", "do diário de obra ao contrato"),
                   ("Comercial", "clientes, propostas e o que fechou negócio"),
                   ("Administrativo", "políticas, processos e dúvidas que voltam sempre"),
                   ("Direito", "contratos, cláusulas, prazos e o histórico de cada caso"),
                   ("Saúde", "protocolos e estudo com a fonte à mão")):
    x = 6 * LADO + MARGEM
    circulo(x + 10, y + 19, 7, RED)
    texto(x + 40, y, cab, "sb", 31, FG)
    texto(x + 40, y + 42, corpo, "sans", 27, BODY)
    y += 96

# ---------------- 8 · fechamento ----------------
topo(7, "E NA SUA EMPRESA?")
y = titulo(7, ["A sua imaginação", "é o limite."], tam=84)
y = paragrafo(7 * LADO + MARGEM, y + 30, "Qual conhecimento da sua empresa hoje depende de uma única pessoa?",
              LADO - 2 * MARGEM, tam=40)
paragrafo(7 * LADO + MARGEM, y + 18, "Me conta nos comentários.", LADO - 2 * MARGEM, "sb", 40, FG)
fx, fy = PONTOS_FIO[-1]
circulo(fx, fy, 150, None, RED + (40,), 4)
circulo(fx, fy, 96, None, RED + (90,), 4)
circulo(fx, fy, 50, RED)
texto(7 * LADO + MARGEM, 1284, "@elucas.dev", "mono", 26, MUTE)

# ---------------- saída ----------------
os.makedirs(SAIDA, exist_ok=True)
final = img.resize((N * LADO, ALT), Image.LANCZOS)
final.save(os.path.join(SAIDA, "panorama.png"))
quadros = [final.crop((k * LADO, 0, (k + 1) * LADO, ALT)) for k in range(N)]
for k, q in enumerate(quadros):
    q.save(os.path.join(SAIDA, f"{k + 1:02d}.png"))
quadros[0].save(os.path.join(SAIDA, "carrossel.pdf"), save_all=True, append_images=quadros[1:], resolution=144)
print("ok:", SAIDA)
