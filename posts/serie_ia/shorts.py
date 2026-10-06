"""Shorts verticais (1080x1920, Reels e YouTube Shorts) da série "IA sem mistério", um por parte, com trilha lo-fi.

Cada short é uma lista de cenas animadas: (duração, rótulo, título, legenda, função que desenha).
Os cortes em tokens e os números da parte 2 são os do cortador do projeto 06; os pesos e palpites são ilustração.

    ferramentas/venv-video/Scripts/python.exe posts/serie_ia/shorts.py 1          # -> posts/serie_ia/parte1/short.mp4
    ferramentas/venv-video/Scripts/python.exe posts/serie_ia/shorts.py todos
    ferramentas/venv-video/Scripts/python.exe posts/serie_ia/shorts.py 2 --still 21.5
"""
import math
import os
import subprocess
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(RAIZ, "ferramentas", "youtube"))
sys.path.insert(0, os.path.join(RAIZ, "ferramentas", "musica"))
from tema import BODY, CARD, CARD_2, FG, INK, MUTE, RED, RED_SOFT, ease, font, mix, rrect, text  # noqa: E402

W, H, FPS = 1080, 1920, 30
CX, M = W // 2, 80                       # centro e margem
PALCO = 700                              # onde começa a área das animações
VERDE, CINZA, VINHO, AZUL, LINHA = (88, 214, 141), (44, 44, 50), (96, 34, 38), (38, 62, 96), (70, 70, 80)

FUNDO = pygame.Surface((W, H))
FUNDO.fill(INK)
for gx in range(18, W, 36):
    for gy in range(18, H, 36):
        FUNDO.set_at((gx, gy), (34, 34, 40))


# ---------------- peças de desenho ----------------
def ap(t, ini, d=0.45):
    """0 -> 1 a partir de `ini` segundos (entrada suave)."""
    return ease((t - ini) / d)


def bloco(s, rect, cor=CARD, borda=LINHA, a=1.0, raio=22, esp=2):
    if a <= 0:
        return
    rrect(s, cor + (int(255 * a),), rect, raio)
    if borda:
        rrect(s, borda + (int(255 * a),), rect, raio, esp)


def chip(s, t, x, y, tam=48, cor=CINZA, a=1.0, mono=False, borda=None):
    """Um bloco de texto. -> largura"""
    f = font("mono-md" if mono else "sans-md", tam)
    w, h = f.size(t)[0] + 26, int(tam * 1.6)
    if a > 0:
        tmp = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(tmp, cor, (0, 0, w, h), border_radius=12)
        if borda:
            pygame.draw.rect(tmp, borda, (0, 0, w, h), 4, border_radius=12)
        tmp.blit(f.render(t, True, FG), (13, int(tam * 0.18)))
        tmp.set_alpha(int(255 * min(1, a)))
        s.blit(tmp, (x, y))
    return w


def frase(s, itens, y, tam=48, n=None, a=1.0, x=M, largura=W - 2 * M, vao=10, centro=False):
    """Blocos em sequência, quebrando linha. itens = [(texto, cor)]; n = quantos aparecem (o último surge aos poucos).
    -> lista de retângulos (x, y, w, h) de todos os blocos, inclusive os que ainda não apareceram"""
    f = font("sans-md", tam)
    linhas, atual, lw = [], [], 0
    for i, (t, _) in enumerate(itens):
        w = f.size(t)[0] + 26
        if atual and lw + w > largura:
            linhas.append((atual, lw - vao))
            atual, lw = [], 0
        atual.append((i, w))
        lw += w + vao
    linhas.append((atual, lw - vao))
    rects = [None] * len(itens)
    for li, (linha_, total) in enumerate(linhas):
        cx = x + ((largura - total) / 2 if centro else 0)
        for i, w in linha_:
            yy = y + li * tam * 2.0
            rects[i] = (cx, yy, w, int(tam * 1.6))
            k = 1.0 if n is None else max(0.0, min(1.0, n - i))
            if k > 0:
                chip(s, itens[i][0], cx, yy + (1 - ease(k)) * 16, tam, itens[i][1], a * ease(k))
            cx += w + vao
    return rects


def lacuna(s, x, y, tam, t, a=1.0, w=150):
    if a <= 0:
        return
    k = 0.55 + 0.45 * abs(math.sin(t * 3))
    rrect(s, RED + (int(255 * a * k),), (x, y, w, int(tam * 1.6)), 12, 4)
    text(s, "?", font("sans-b", tam), RED_SOFT, (x + w / 2, y + tam * 0.8), "center", a)


def barras(s, itens, y, t, a=1.0, x=M, largura=W - 2 * M, cor_on=RED, passo=92):
    """itens = [(rótulo, tamanho de 0 a 1, destacada)]. Crescem com o tempo."""
    for i, (rot, v, on) in enumerate(itens):
        k = ap(t, i * 0.18, 0.6) * a
        if k <= 0:
            continue
        yy = y + i * passo
        text(s, rot, font("sans-md", 42), FG if on else BODY, (x + 250, yy + 24), "midright", k)
        rrect(s, (255, 255, 255, int(18 * k)), (x + 280, yy, largura - 280, 48), 24)
        rrect(s, (cor_on if on else (120, 70, 74)) + (int(255 * k),), (x + 280, yy, max(48, (largura - 280) * v * ap(t, i * 0.18, 0.9)), 48), 24)


def cartoes(s, itens, y, t, a=1.0, passo=176, espera=1.0):
    """Lista de cartões que entram um a um. itens = [(título, detalhe)]"""
    for i, (cab, det) in enumerate(itens):
        k = ap(t, 0.3 + i * espera) * a
        if k <= 0:
            continue
        yy = y + i * passo + (1 - k) * 24
        bloco(s, (M, yy, W - 2 * M, 150), a=k)
        text(s, cab, font("sans-sb", 42), FG, (M + 34, yy + 48), "midleft", k)
        text(s, det, font("sans", 33), BODY, (M + 34, yy + 104), "midleft", k)


def seta(s, x, y, a=1.0, cor=RED, tam=64, baixo=True):
    text(s, "↓" if baixo else "→", font("sans-b", tam), cor, (x, y), "center", a)


def fala(s, t_, y, minha, a=1.0, w=None, apagada=False):
    f = font("sans-md", 36)
    w = w or f.size(t_)[0] + 60
    x = W - M - w if minha else M
    cor, borda = ((70, 30, 34), RED) if minha else (CARD_2, LINHA)
    if apagada:
        cor, borda = (20, 20, 24), (40, 40, 46)
    bloco(s, (x, y, w, 84), cor, borda, a, 20)
    text(s, t_, f, (90, 90, 98) if apagada else FG, (x + 30, y + 42), "midleft", a)


# ---------------- cenas comuns ----------------
def abertura(linhas, sub):
    def fn(s, t, a):
        for i, l in enumerate(linhas):
            k = ap(t, 0.2 + i * 0.25) * a
            text(s, l, font("sans-b", 104), FG, (CX, 640 + i * 124 + (1 - k) * 30), "midtop", k)
        text(s, sub, font("sans-md", 46), BODY, (CX, 660 + len(linhas) * 124 + 40), "midtop", ap(t, 1.2) * a)
    return fn


def fechamento(resumo):
    def fn(s, t, a):
        text(s, resumo, font("sans-md", 40), BODY, (CX, 700), "midtop", ap(t, 0.2) * a)
        for i, l in enumerate(("A sua imaginação", "é o limite.")):
            text(s, l, font("sans-b", 100), FG, (CX, 800 + i * 120), "midtop", ap(t, 0.6 + i * 0.2) * a)
        text(s, "@elucas.dev", font("mono", 38), MUTE, (CX, 1120), "midtop", ap(t, 1.4) * a)
    return fn


def pratica(itens):
    return lambda s, t, a: cartoes(s, itens, PALCO + 30, t, a)


# =====================================================================================
# PARTE 1 · como a IA escreve um texto
# =====================================================================================
COMECO1 = "Uma IA que escreve é".split()
RESTO1 = "uma máquina que adivinha a próxima palavra, uma de cada vez, até o texto ficar pronto.".split()
FRASE1 = [(p, CINZA) for p in COMECO1] + [(p, VINHO) for p in RESTO1]


def p1_teclado(s, t, a):
    bloco(s, (M + 40, PALCO + 40, W - 2 * M - 80, 420), a=a, raio=40)
    rrect(s, (255, 255, 255, int(16 * a)), (M + 90, PALCO + 90, W - 2 * M - 180, 120), 24)
    digitado = "Bom"[:max(0, int((t - 0.6) / 0.3))]
    text(s, digitado + ("|" if int(t * 2) % 2 == 0 else ""), font("sans-md", 60), FG, (M + 130, PALCO + 150), "midleft", a)
    x = M + 100
    for i, p in enumerate(("dia", "trabalho", "descanso")):
        k = ap(t, 2.0 + i * 0.25) * a
        on = i == 0 and t > 3.6
        w = chip(s, p, x, PALCO + 300, 46, (70, 30, 34) if on else CARD_2, k, borda=RED if on else LINHA)
        x += w + 26


def p1_palpites(s, t, a):
    itens = FRASE1[:10]
    r = frase(s, itens, PALCO, 54, a=a)
    x, y, w, _ = r[-1]
    if t < 5.2:
        lacuna(s, x + w + 12 if x + w + 170 < W - M else M, y if x + w + 170 < W - M else y + 108, 54, t, a)
    else:
        chip(s, "próxima", x + w + 12 if x + w + 250 < W - M else M, y if x + w + 250 < W - M else y + 108, 54, VINHO, ap(t, 5.2) * a)
    text(s, "OS PALPITES DELA", font("mono-md", 30), MUTE, (M, PALCO + 400), "topleft", ap(t, 1.2) * a)
    barras(s, [("próxima", 1.0, t > 4.4), ("resposta", 0.45, False), ("melhor", 0.22, False)], PALCO + 460, t - 1.4, a)


def p1_repete(s, t, a):
    n = len(COMECO1) + max(0.0, (t - 0.5) / 0.48)
    r = frase(s, FRASE1, PALCO, 56, n=n, a=a)
    i = int(n)
    if i < len(FRASE1):
        x, y, w, _ = r[i]
        lacuna(s, x, y, 56, t, a * (1 - min(1, (n - i) * 2)), w=max(110, w))


def p1_leu(s, t, a):
    for j in range(9):                                     # folhas caindo numa pilha
        k = ap(t, 0.2 + j * 0.28, 0.5)
        if k <= 0:
            continue
        x, y = M + 30 + j * 26, PALCO + 40 + j * 20 - (1 - k) * 260
        bloco(s, (x, y, 430, 260), CARD_2, LINHA, a * k, 18)
        for i, fr in enumerate((0.8, 0.6, 0.72, 0.5)):
            rrect(s, (90, 90, 100, int(255 * a * k)), (x + 30, y + 50 + i * 44, 370 * fr, 14), 7)
    k = ap(t, 3.4) * a
    seta(s, 760, PALCO + 250, k, baixo=False)
    text(s, "depois de “Bom”", font("sans-md", 40), BODY, (900, PALCO + 220), "center", k)
    text(s, "vem “dia”", font("sans-sb", 50), FG, (900, PALCO + 284), "center", k)


def p1_cuidado(s, t, a):
    for i, (txt, cor) in enumerate((("soa bem e está certo", VERDE), ("soa bem e está errado", RED))):
        k = ap(t, 0.4 + i * 1.3) * a
        bloco(s, (M, PALCO + 60 + i * 190, W - 2 * M, 150), CARD, cor, k, esp=4)
        text(s, txt, font("sans-md", 50), FG, (M + 40, PALCO + 135 + i * 190), "midleft", k)
    text(s, "para ela, os dois são só", font("mono", 34), MUTE, (CX, PALCO + 470), "midtop", ap(t, 3.2) * a)
    text(s, "“a próxima palavra”", font("mono-md", 38), RED_SOFT, (CX, PALCO + 520), "midtop", ap(t, 3.2) * a)


def p1_pratica(s, t, a):
    text(s, "PEDIDO VAGO", font("mono-md", 30), MUTE, (M, PALCO), "topleft", a)
    bloco(s, (M, PALCO + 50, W - 2 * M, 110), a=a)
    text(s, "Faça um relatório.", font("sans-md", 44), FG, (M + 34, PALCO + 105), "midleft", a)
    k = ap(t, 1.6) * a
    text(s, "COMEÇO CLARO", font("mono-md", 30), VERDE, (M, PALCO + 210), "topleft", k)
    bloco(s, (M, PALCO + 260, W - 2 * M, 440), CARD, VERDE, k, esp=4)
    for j, (rot, val) in enumerate((("quem ela deve ser", "Você é planejador de manutenção."), ("a situação", "Estas são as paradas do mês."),
                                    ("como você quer a resposta", "Resuma em tópicos."))):
        kk = ap(t, 2.2 + j * 0.9) * a
        text(s, rot, font("mono-md", 30), RED_SOFT, (M + 34, PALCO + 290 + j * 134), "topleft", kk)
        text(s, val, font("sans-md", 42), FG, (M + 34, PALCO + 332 + j * 134), "topleft", kk)


P1 = [
    (4.0, "", [], ("", ""), abertura(["Como a IA", "escreve", "um texto?"], "em menos de um minuto")),
    (6.5, "VOCÊ JÁ VIU ISSO", ["No teclado do", "seu celular"], ("Ele sugere a próxima palavra", "sem entender a conversa."), p1_teclado),
    (7.5, "A IDEIA", ["A IA adivinha a", "próxima palavra"], ("Ela olha o texto e dá palpites", "para o que vem depois."), p1_palpites),
    (9.5, "O TRUQUE", ["Escolhe uma.", "E repete."], ("Uma palavra de cada vez,", "até o texto ficar pronto."), p1_repete),
    (6.5, "DE ONDE VÊM OS PALPITES", ["Ela leu muito.", "Muito mesmo."], ("De tanto ler, aprendeu", "o que costuma vir depois do quê."), p1_leu),
    (6.5, "O CUIDADO", ["Ela não consulta", "um arquivo"], ("O texto é escrito na hora: pode sair", "errado com a mesma segurança."), p1_cuidado),
    (8.0, "NA PRÁTICA", ["O começo", "é tudo"], ("Pedido vago recebe", "a resposta mais comum."), p1_pratica),
    (4.5, "", [], ("", ""), fechamento("Quem entende como funciona, pede melhor.")),
]

# =====================================================================================
# PARTE 2 · por que a IA erra contas
# =====================================================================================
TOK_FRASE = ["a", "manutenção", "prev", "ent", "iva"]
TOK_RARA = ["al", "mo", "x", "ar", "if", "ado"]
TOK_IDS = [("a", 179), ("bomba", 2411), ("pa", 1861), ("rou", 1106), ("de", 180), ("novo", 2057)]


def separar(s, pedacos, y, t, ini, a, tam=60, grupos=None):
    """Pedaços que começam colados e se afastam: é o corte em tokens. grupos = índices que iniciam palavra nova."""
    f = font("sans-md", tam)
    k = ap(t, ini, 0.8)
    larguras = [f.size(p)[0] + 26 for p in pedacos]
    vaos = [(26 if grupos and i in grupos else 0) + 12 * k for i in range(len(pedacos))]
    total = sum(larguras) + sum(vaos[1:]) - (26 * (1 - k)) * (len(pedacos) - 1)
    x = CX - total / 2
    for i, (p, w) in enumerate(zip(pedacos, larguras)):
        if i:
            x += vaos[i] - 26 * (1 - k)
        chip(s, p, x, y, tam, mix(CINZA, VINHO if i % 2 == 0 else (60, 60, 70), k), a)
        x += w


def p2_corte(s, t, a):
    text(s, "O QUE VOCÊ ESCREVE", font("mono-md", 30), MUTE, (CX, PALCO), "midtop", a)
    text(s, "a manutenção preventiva", font("sans-md", 62), FG, (CX, PALCO + 50), "midtop", a)
    seta(s, CX, PALCO + 210, ap(t, 1.4) * a)
    text(s, "O QUE ELA RECEBE: TOKENS", font("mono-md", 30), RED_SOFT, (CX, PALCO + 290), "midtop", ap(t, 1.8) * a)
    separar(s, TOK_FRASE, PALCO + 350, t, 2.4, ap(t, 1.8) * a, grupos={1, 2})


def p2_regra(s, t, a):
    text(s, "PALAVRA COMUM", font("mono-md", 30), MUTE, (CX, PALCO), "midtop", a)
    separar(s, ["empresa"], PALCO + 50, t, 0.5, a)
    text(s, "uma peça só", font("sans", 36), BODY, (CX, PALCO + 160), "midtop", ap(t, 1.0) * a)
    k = ap(t, 2.2) * a
    text(s, "PALAVRA RARA", font("mono-md", 30), RED_SOFT, (CX, PALCO + 300), "midtop", k)
    separar(s, TOK_RARA, PALCO + 350, t, 3.0, k)
    text(s, "almoxarifado: seis peças", font("sans", 36), BODY, (CX, PALCO + 460), "midtop", ap(t, 4.0) * a)


def p2_numeros(s, t, a):
    f = font("sans-md", 50)
    larguras = [max(f.size(p)[0], font("mono-md", 40).size(str(i))[0]) + 36 for p, i in TOK_IDS]
    x = CX - (sum(larguras) + 12 * (len(larguras) - 1)) / 2
    for j, ((p, i), w) in enumerate(zip(TOK_IDS, larguras)):
        bloco(s, (x, PALCO + 60, w, 96), CINZA, None, a, 14)
        text(s, p, f, FG, (x + w / 2, PALCO + 108), "center", a)
        k = ap(t, 1.2 + j * 0.45) * a
        seta(s, x + w / 2, PALCO + 220, k, tam=48)
        bloco(s, (x, PALCO + 290 + (1 - ap(t, 1.2 + j * 0.45)) * 20, w, 96), AZUL, None, k, 14)
        text(s, str(i), font("mono-md", 40), FG, (x + w / 2, PALCO + 338), "center", k)
        x += w + 12
    text(s, "é só isto que chega até ela", font("mono", 34), MUTE, (CX, PALCO + 460), "midtop", ap(t, 4.2) * a)


def p2_conta(s, t, a):
    x = 150
    for i, p in enumerate(("48", "392", "×", "7", "615", "=")):
        if p in "×=":
            text(s, p, font("sans-b", 64), MUTE, (x + 26, PALCO + 108), "center", a)
            x += 64
        else:
            x += chip(s, p, x, PALCO + 60, 60, CINZA, ap(t, 0.2 + i * 0.2) * a, mono=True) + 8
    palpites = ["368 204 …", "367 505 …", "368 950 …"]
    i = int(max(0, t - 2.0) / 1.1) % len(palpites)
    k = ap(t, 2.0) * a
    text(s, "PALPITE", font("mono-md", 30), RED_SOFT, (CX, PALCO + 250), "midtop", k)
    dx = math.sin(t * 22) * 5
    bloco(s, (CX - 250 + dx, PALCO + 300, 500, 110), CARD, RED, k, esp=4)
    text(s, palpites[i], font("mono-md", 56), FG, (CX + dx, PALCO + 355), "center", k)
    text(s, "cada vez sai um número diferente", font("sans", 36), BODY, (CX, PALCO + 450), "midtop", ap(t, 3.4) * a)


def p2_solucao(s, t, a):
    for j, (rot, val, cor, mono) in enumerate((("1 · ela escreve a conta", "48392 * 7615", LINHA, True),
                                               ("2 · o computador executa", "368505080", AZUL, True),
                                               ("3 · ela responde certo", "O resultado é 368.505.080.", VERDE, False))):
        k = ap(t, 0.4 + j * 1.6) * a
        y = PALCO + j * 220
        text(s, rot, font("mono-md", 32), RED_SOFT if j == 0 else MUTE, (M, y), "topleft", k)
        bloco(s, (M, y + 52, W - 2 * M, 116), CARD, cor, k, esp=4)
        text(s, val, font("mono-md" if mono else "sans-md", 48), FG, (M + 34, y + 110), "midleft", k)


P2 = [
    (4.0, "", [], ("", ""), abertura(["Por que a IA", "erra contas?"], "o motivo está em como ela lê")),
    (7.0, "COMO ELA LÊ", ["Ela não lê palavras.", "Lê peças."], ("O texto é picado em peças.", "Cada peça se chama token."), p2_corte),
    (7.5, "A REGRA DO CORTE", ["Tokenização"], ("O que aparece muito vira uma peça.", "O que é raro vira várias."), p2_regra),
    (7.0, "O QUE ELA ENXERGA", ["Cada token", "vira um número"], ("A IA nunca vê letras:", "só os números das peças."), p2_numeros),
    (7.5, "POR ISSO ELA TROPEÇA", ["Ela não calcula.", "Adivinha."], ("Conta grande, que ela nunca viu igual,", "vira palpite."), p2_conta),
    (8.0, "COMO RESOLVERAM", ["Execução", "de código"], ("Ela escreve a conta.", "Um computador calcula."), p2_solucao),
    (7.5, "NA PRÁTICA", ["Quando o número", "importa"], ("A ferramenta existe,", "mas nem sempre é usada."),
     pratica([("veja se ela fez a conta", "dá para ver o programa que rodou"), ("se não fez, peça", "“calcule usando código”"),
              ("confira o que for crítico", "horas, custos, estoque, totais")])),
    (4.5, "", [], ("", ""), fechamento("Ela escreve a conta. Quem calcula é o computador.")),
]

# =====================================================================================
# PARTE 3 · por que a IA esquece o que você disse
# =====================================================================================
CONVERSA = [("Use o nosso padrão de relatório.", True), ("Combinado.", False), ("Resuma a parada de ontem.", True),
            ("Aqui está o resumo.", False), ("E a de hoje?", True)]


def p3_rele(s, t, a):
    n = min(len(CONVERSA), 1 + int(max(0, t - 0.4) / 1.25))
    for i in range(n):
        txt, minha = CONVERSA[i]
        fala(s, txt, PALCO + 30 + i * 104, minha, ap(t, 0.4 + (i - 1) * 1.25 if i else 0) * a)
    pulso = (t - 0.4) % 1.25
    k = (1 - min(1, pulso / 0.7)) if t > 0.4 else 0
    rrect(s, RED + (int((90 + 165 * k) * a),), (M - 22, PALCO + 8, W - 2 * M + 44, n * 104 + 24), 26, 4)
    text(s, "ela relê tudo, do começo", font("mono-md", 34), RED_SOFT, (CX, PALCO + 600), "midtop", ap(t, 1.6) * a)


def p3_mesa(s, t, a):
    bloco(s, (M, PALCO + 40, W - 2 * M, 470), CARD, RED, a, esp=4)
    text(s, "A MESA · JANELA DE CONTEXTO", font("mono-md", 30), RED_SOFT, (M + 30, PALCO + 62), "topleft", a)
    for j in range(8):
        k = ap(t, 0.5 + j * 0.45)
        if k <= 0:
            continue
        cabe = j < 6
        x = M + 50 + (j % 3) * 300 + (0 if cabe else 320)
        y = PALCO + 130 + (j // 3) * 180
        if not cabe:                                        # as que não cabem ficam do lado de fora, apagadas
            x, y = M + 50 + (j - 6) * 300, PALCO + 560
        bloco(s, (x, y - (1 - k) * 60, 250, 150), CARD_2 if cabe else (20, 20, 24), LINHA, a * k, 16)
        for i, fr in enumerate((0.8, 0.55, 0.7)):
            rrect(s, (90, 90, 100, int((255 if cabe else 90) * a * k)), (x + 26, y + 36 + i * 32 - (1 - k) * 60, 198 * fr, 12), 6)
    text(s, "não coube", font("mono", 32), MUTE, (M + 660, PALCO + 620), "midleft", ap(t, 4.2) * a)


def p3_longa(s, t, a):
    sobe = min(3, max(0.0, (t - 1.0) / 1.2)) * 104          # a conversa cresce e empurra o começo para fora
    topo_mesa = PALCO + 250
    falas = CONVERSA + [("Agora compare as duas.", True), ("Use o padrão no relatório.", True), ("Que padrão?", False)]
    for i, (txt, minha) in enumerate(falas):
        y = PALCO + 30 + i * 104 - sobe
        visivel = i < 5 + int(sobe / 104 + 0.99)
        if visivel and y > PALCO - 40:
            fala(s, txt, y, minha, a, apagada=y < topo_mesa - 30)
    rrect(s, RED + (int(255 * a),), (M - 22, topo_mesa, W - 2 * M + 44, 440), 26, 4)
    text(s, "↑ o começo ficou de fora", font("mono", 32), MUTE, (CX, topo_mesa + 462), "midtop", ap(t, 2.4) * a)


def p3_nova(s, t, a):
    for j, (rot, cheia) in enumerate((("ONTEM", True), ("HOJE", False))):
        x = M + j * 470
        text(s, rot, font("mono-md", 30), MUTE if cheia else RED_SOFT, (x, PALCO + 20), "topleft", a)
        bloco(s, (x, PALCO + 70, 440, 420), CARD, LINHA if cheia else RED, ap(t, 0.2 + j * 1.2) * a, esp=2 if cheia else 4)
        if cheia:
            for i in range(4):
                rrect(s, ((70, 30, 34) if i % 2 else CARD_2) + (int(255 * a),), (x + 30 + (i % 2) * 120, PALCO + 110 + i * 86, 260, 62), 16)
        else:
            text(s, "vazia", font("sans-md", 48), MUTE, (x + 220, PALCO + 280), "center", ap(t, 1.8) * a)


def p3_caderno(s, t, a):
    bloco(s, (M, PALCO + 20, W - 2 * M, 250), CARD, VERDE, a, esp=4)
    text(s, "CADERNO · MEMÓRIA", font("mono-md", 30), VERDE, (M + 30, PALCO + 42), "topleft", a)
    notas = ("trabalha com manutenção", "usa o padrão de relatório")
    for i, n in enumerate(notas):
        text(s, "• " + n, font("sans", 38), BODY, (M + 30, PALCO + 130 + i * 62), "midleft", ap(t, 0.4 + i * 0.5) * a)
    k = ap(t, 2.2)
    seta(s, CX, PALCO + 330, k * a)
    bloco(s, (M, PALCO + 400, W - 2 * M, 300), CARD, RED, ap(t, 1.8) * a, esp=4)
    text(s, "A MESA DE HOJE", font("mono-md", 30), RED_SOFT, (M + 30, PALCO + 422), "topleft", ap(t, 1.8) * a)
    y = PALCO + 480 - (1 - ap(t, 2.6, 0.7)) * 330
    bloco(s, (M + 30, y, W - 2 * M - 60, 80), (30, 50, 40), None, ap(t, 2.6) * a, 16)
    text(s, "anotações do caderno", font("sans-md", 36), FG, (M + 60, y + 40), "midleft", ap(t, 2.6) * a)
    bloco(s, (M + 30, PALCO + 580, W - 2 * M - 60, 80), (70, 30, 34), None, ap(t, 3.6) * a, 16)
    text(s, "sua mensagem nova", font("sans-md", 36), FG, (M + 60, PALCO + 620), "midleft", ap(t, 3.6) * a)


P3 = [
    (4.0, "", [], ("", ""), abertura(["Por que a IA", "esquece o que", "você disse?"], "não é descuido")),
    (7.5, "O QUE ACONTECE", ["Ela não tem", "memória"], ("A cada mensagem, ela recebe", "a conversa inteira de novo."), p3_rele),
    (7.0, "O LIMITE", ["Janela de", "contexto"], ("É a mesa de trabalho dela:", "só enxerga o que está em cima."), p3_mesa),
    (7.5, "CONVERSA LONGA", ["O começo", "sai da mesa"], ("Passou do limite, o combinado", "lá do início fica de fora."), p3_longa),
    (5.5, "CONVERSA NOVA", ["Outra conversa,", "mesa vazia"], ("O que você explicou ontem", "não está na mesa de hoje."), p3_nova),
    (7.5, "COMO RESOLVERAM", ["Um caderno", "de anotações"], ("O recurso de memória guarda notas", "e põe na mesa ao começar."), p3_caderno),
    (7.5, "NA PRÁTICA", ["Cuide do que", "está na mesa"], ("O que não está na conversa,", "para ela, não existe."),
     pratica([("assunto novo, conversa nova", "menos papel velho na mesa"), ("conversa longa? peça um resumo", "e recomece com ele"),
              ("entregue o documento junto", "contrato, procedimento, histórico")])),
    (4.5, "", [], ("", ""), fechamento("Ela não lembra. Ela relê o que está na mesa.")),
]

# =====================================================================================
# PARTE 4 · como a IA decide o que importa
# =====================================================================================
def com_pesos(s, itens, y, t, a, tam=50, alvo=None, ini=1.0):
    """Frase em blocos; embaixo de cada palavra, uma barra verde (o peso) que cresce. itens = [(texto, peso)]"""
    r = frase(s, [(p, VINHO if p == alvo else CINZA) for p, _ in itens], y, tam, a=a, vao=12)
    for i, ((x, yy, w, h), (_, peso)) in enumerate(zip(r, itens)):
        k = ap(t, ini + i * 0.12, 0.7)
        if peso > 0 and k > 0:
            rrect(s, VERDE + (int((70 + 185 * peso) * a),), (x, yy + h + 8, w, (6 + 26 * peso) * k), 5)
    return r


def p4_atencao(s, t, a):
    itens = [("A", 0.05), ("bomba", 0.9), ("parou", 0.7), ("porque", 0.3), ("o", 0.05), ("selo", 1.0), ("estava", 0.25)]
    r = com_pesos(s, itens, PALCO + 20, t, a, 52)
    x, y, w, _ = r[-1]
    lacuna(s, M, y + 150, 52, t, a)
    cx = M + (W - 2 * M) * (0.5 + 0.38 * math.sin(t * 1.1))   # o holofote passeando
    luz = pygame.Surface((W, 420), pygame.SRCALPHA)
    for raio, alfa in ((260, 10), (190, 14), (120, 18)):
        pygame.draw.circle(luz, (255, 240, 200, int(alfa * a)), (int(cx), 160), raio)
    s.blit(luz, (0, PALCO - 60))
    text(s, "barra verde: quanto cada palavra pesa", font("mono", 32), VERDE, (CX, PALCO + 520), "midtop", ap(t, 2.4) * a)


def p4_liga(s, t, a):
    itens = [("O", 0), ("técnico", 0.25), ("trocou", 0.3), ("o", 0), ("selo", 1.0), ("da", 0), ("bomba", 0.3), ("porque", 0.15),
             ("ele", 0), ("estava", 0.35), ("gasto.", 0.85)]
    r = com_pesos(s, itens, PALCO + 20, t, a, 50, alvo="ele", ini=1.6)
    k = ap(t, 3.6)
    if k > 0:                                               # a ligação de "ele" até "selo"
        (x1, y1, w1, h1), (x2, y2, w2, h2) = r[8], r[4]
        pygame.draw.line(s, mix(INK, VERDE, k * a), (x1 + w1 / 2, y1 - 6), (x2 + w2 / 2, y2 + h2 + 44), 5)
    text(s, "“ele” = o selo", font("sans-sb", 52), FG, (CX, PALCO + 520), "midtop", ap(t, 4.2) * a)


def p4_disputa(s, t, a):
    n = int(5 + 23 * ap(t, 1.2, 3.0))                       # o texto cresce; a instrução (vermelha) encolhe
    w = (W - 2 * M - (n - 1) * 6) / n
    for i in range(n):
        rrect(s, (RED if i == 1 else CARD_2) + (int(255 * a),), (M + i * (w + 6), PALCO + 110, w, 130), 10)
    text(s, "em vermelho: a sua instrução", font("mono", 32), RED_SOFT, (M, PALCO + 280), "topleft", a)
    text(s, "PESO DA INSTRUÇÃO", font("mono-md", 30), MUTE, (M, PALCO + 420), "topleft", a)
    rrect(s, (255, 255, 255, int(18 * a)), (M, PALCO + 470, W - 2 * M, 56), 28)
    rrect(s, RED + (int(255 * a),), (M, PALCO + 470, (W - 2 * M) * 5 / n * 0.9, 56), 28)


def p4_meio(s, t, a):
    bloco(s, (M, PALCO + 30, W - 2 * M, 460), a=a)
    n = int(101 * ap(t, 0.5, 2.2))
    pts = [(M + 60 + i * (W - 2 * M - 120) / 100, PALCO + 110 + 250 * math.sin(math.pi * i / 100) ** 0.8) for i in range(101)]
    if n > 1:
        pygame.draw.lines(s, mix(INK, RED, a), False, pts[:n], 8)
    for i in (0, 100):
        if n > i:
            pygame.draw.circle(s, mix(INK, RED, a), (int(pts[i][0]), int(pts[i][1])), 14)
    for rot, x, anc in (("começo", M + 60, "midleft"), ("meio", CX, "center"), ("fim", W - M - 60, "midright")):
        text(s, rot, font("mono", 32), MUTE, (x, PALCO + 440), anc, a)
    text(s, "quanto mais alto, mais a IA aproveita", font("mono", 32), MUTE, (CX, PALCO + 530), "midtop", ap(t, 2.6) * a)


def p4_ordem(s, t, a):
    k = ap(t, 0.3) * a
    bloco(s, (M, PALCO + 20, W - 2 * M, 300), a=k)
    text(s, "1 · O MATERIAL", font("mono-md", 30), MUTE, (M + 30, PALCO + 42), "topleft", k)
    for i, fr in enumerate((0.92, 0.8, 0.88, 0.7, 0.84)):
        rrect(s, (90, 90, 100, int(255 * k)), (M + 30, PALCO + 110 + i * 36, (W - 2 * M - 60) * fr, 14), 7)
    k = ap(t, 1.8) * a
    y = PALCO + 360 + (1 - ap(t, 1.8, 0.7)) * 60
    bloco(s, (M, y, W - 2 * M, 230), CARD, RED, k, esp=4)
    text(s, "2 · O SEU PEDIDO · O PROMPT", font("mono-md", 30), RED_SOFT, (M + 30, y + 22), "topleft", k)
    text(s, "Com base no relatório acima,", font("sans-md", 42), FG, (M + 30, y + 110), "midleft", k)
    text(s, "liste as três causas.", font("sans-md", 42), FG, (M + 30, y + 166), "midleft", k)


P4 = [
    (4.0, "", [], ("", ""), abertura(["Como a IA", "decide o que", "importa?"], "o nome disso é atenção")),
    (7.5, "O MECANISMO", ["Atenção"], ("Um holofote: ilumina mais", "umas palavras que outras."), p4_atencao),
    (7.5, "POR QUE FUNCIONA", ["É assim que ela", "liga os pontos"], ("Para entender “ele”, ela dá", "mais peso às palavras certas."), p4_liga),
    (7.5, "O LIMITE", ["Mais texto,", "mais disputa"], ("O peso é repartido entre", "tudo o que ela está lendo."), p4_disputa),
    (7.0, "O QUE A PESQUISA MOSTRA", ["O meio", "se perde"], ("Começo e fim são mais aproveitados.", "O meio passa batido."), p4_meio),
    (7.5, "A DICA DE QUEM FABRICA", ["Documento em cima.", "Pedido embaixo."], ("O pedido fica onde ela", "presta mais atenção."), p4_ordem),
    (7.5, "NA PRÁTICA", ["Ajude a IA a", "prestar atenção"], ("Organização é o que faz", "a sua instrução pesar."),
     pratica([("um pedido de cada vez", "pedidos misturados disputam atenção"), ("destaque o que não pode faltar", "títulos, listas, regra repetida no fim"),
              ("mostre um exemplo", "um modelo pronto pesa mais")])),
    (4.5, "", [], ("", ""), fechamento("Texto organizado, atenção no lugar certo.")),
]

# =====================================================================================
# PARTE 5 · por que a IA inventa
# =====================================================================================
def p5_completa(s, t, a):
    bloco(s, (M, PALCO + 40, W - 2 * M, 250), a=a)
    text(s, "A norma que trata", font("sans-md", 48), FG, (M + 40, PALCO + 110), "midleft", a)
    text(s, "disso é a", font("sans-md", 48), FG, (M + 40, PALCO + 190), "midleft", a)
    opcoes = ["NT-4471", "NR-309", "IT-0082", "NBR-7714"]                # sempre aparece alguma coisa
    i = int(max(0, t - 1.2) / 0.9) % len(opcoes)
    if t < 1.2:
        lacuna(s, M + 290, PALCO + 152, 48, t, a, w=200)
    else:
        chip(s, opcoes[i], M + 290, PALCO + 152, 48, VINHO, a, mono=True)
    text(s, "alguma palavra sempre vem depois", font("mono", 34), MUTE, (CX, PALCO + 350), "midtop", ap(t, 2.0) * a)


def p5_alucinacao(s, t, a):
    fala(s, "Qual norma trata desse ensaio?", PALCO + 20, True, a)
    resposta = ["É a norma NT-4471, revisão C,", "item 8.3, publicada pela comissão…"]
    k = ap(t, 1.0) * a
    bloco(s, (M, PALCO + 140, W - 2 * M - 120, 220), CARD_2, LINHA, k)
    n = int(max(0, t - 1.3) * 26)
    for i, l in enumerate(resposta):
        text(s, l[:max(0, n)], font("sans-md", 40), FG, (M + 34, PALCO + 200 + i * 62), "midleft", k)
        n -= len(l)
    kk = ap(t, 4.2) * a
    bloco(s, (M, PALCO + 420, W - 2 * M, 110), CARD, RED, kk, esp=4)
    text(s, "convincente. e inventada.", font("mono-md", 40), RED_SOFT, (CX, PALCO + 475), "center", kk)
    text(s, "(exemplo fictício)", font("mono", 28), MUTE, (CX, PALCO + 560), "midtop", kk)


def p5_aluno(s, t, a):
    for j, (rot, val, cor) in enumerate((("deixar em branco", "zero", LINHA), ("chutar", "às vezes acerta", VERDE))):
        k = ap(t, 0.3 + j * 1.2) * a
        bloco(s, (M, PALCO + 30 + j * 250, W - 2 * M, 210), CARD, cor, k, esp=4)
        text(s, rot, font("mono-md", 34), MUTE, (M + 40, PALCO + 90 + j * 250), "midleft", k)
        text(s, val, font("sans-sb", 60), FG, (M + 40, PALCO + 170 + j * 250), "midleft", k)
    pontos = int(max(0, t - 2.4) * 2.2)                                   # o placar de quem chuta sobe
    text(s, f"+{pontos}", font("mono-md", 64), VERDE, (W - M - 40, PALCO + 420), "midright", ap(t, 2.4) * a)
    text(s, "+0", font("mono-md", 64), MUTE, (W - M - 40, PALCO + 170), "midright", ap(t, 1.0) * a)


def p5_detalhe(s, t, a):
    itens = ["datas", "números", "nomes", "citações", "links"]
    for j, it in enumerate(itens):
        k = ap(t, 0.3 + j * 0.5) * a
        x = M + (j % 2) * 470
        y = PALCO + 40 + (j // 2) * 150
        bloco(s, (x, y, 440, 120), CARD, RED, k, esp=4)
        text(s, it, font("sans-md", 48), FG, (x + 36, y + 60), "midleft", k)


def p5_consulta(s, t, a):
    k = ap(t, 0.3) * a
    bloco(s, (M, PALCO + 20, W - 2 * M, 200), CARD_2, LINHA, k)
    text(s, "DOCUMENTO", font("mono-md", 30), MUTE, (M + 30, PALCO + 42), "topleft", k)
    for i, fr in enumerate((0.9, 0.7, 0.8)):
        rrect(s, (RED if i == 1 and t > 1.6 else (90, 90, 100)) + (int(255 * k),), (M + 30, PALCO + 100 + i * 34, (W - 2 * M - 60) * fr, 14), 7)
    seta(s, CX, PALCO + 280, ap(t, 1.6) * a)
    kk = ap(t, 2.2) * a
    bloco(s, (M, PALCO + 340, W - 2 * M, 290), CARD, VERDE, kk, esp=4)
    text(s, "A troca do selo ficou pendente", font("sans-md", 42), FG, (M + 34, PALCO + 400), "midleft", kk)
    text(s, "desde a última parada.", font("sans-md", 42), FG, (M + 34, PALCO + 456), "midleft", kk)
    k3 = ap(t, 3.4) * a
    bloco(s, (M + 34, PALCO + 520, 560, 76), (30, 50, 40), VERDE, k3, 38)
    text(s, "fonte: relatório da parada", font("mono-md", 32), VERDE, (M + 64, PALCO + 558), "midleft", k3)


P5 = [
    (4.0, "", [], ("", ""), abertura(["Por que a IA", "inventa?"], "tem explicação, e tem como reduzir")),
    (7.0, "O MECANISMO", ["Ela sempre", "completa o texto"], ("Ela adivinha a próxima palavra.", "E sempre existe uma."), p5_completa),
    (7.5, "O NOME DISSO", ["Alucinação"], ("Texto bem escrito,", "confiante e errado."), p5_alucinacao),
    (7.0, "POR QUE ACONTECE", ["O aluno que", "chuta na prova"], ("Se em branco vale zero,", "chutar compensa."), p5_aluno),
    (6.0, "ONDE MORA O PERIGO", ["No detalhe", "específico"], ("O geral ela costuma acertar.", "O risco está no detalhe raro."), p5_detalhe),
    (7.5, "COMO RESOLVERAM", ["Prova com", "consulta"], ("Ela busca nos documentos", "e mostra a fonte."), p5_consulta),
    (7.5, "NA PRÁTICA", ["Tire o chute", "da jogada"], ("Você não elimina a alucinação.", "Você reduz e confere."),
     pratica([("entregue o documento", "com consulta, ela inventa menos"), ("peça a fonte", "e abra: link inventado não abre"),
              ("“não sei” é resposta válida", "diga isso no pedido")])),
    (4.5, "", [], ("", ""), fechamento("Bem escrito não quer dizer verdadeiro.")),
]

# =====================================================================================
# PARTE 6 · mesma pergunta, respostas diferentes
# =====================================================================================
def roleta(s, cx, cy, r, fatias, ponteiro, a=1.0):
    """fatias = [(tamanho, cor, rótulo)], somando 1; ponteiro = ângulo em graus (0 = para cima, sentido horário)."""
    if a <= 0:
        return
    tmp = pygame.Surface((2 * r + 8, 2 * r + 8), pygame.SRCALPHA)
    c, ang = r + 4, -90.0
    for v, cor, rot in fatias:
        pts = [(c, c)] + [(c + r * math.cos(math.radians(ang + 360 * v * i / 40)), c + r * math.sin(math.radians(ang + 360 * v * i / 40))) for i in range(41)]
        pygame.draw.polygon(tmp, cor, pts)
        pygame.draw.polygon(tmp, INK, pts, 4)
        if rot:
            m = math.radians(ang + 180 * v)
            img = font("sans-md", 34).render(rot, True, FG)
            tmp.blit(img, img.get_rect(center=(c + math.cos(m) * r * 0.6, c + math.sin(m) * r * 0.6)))
        ang += 360 * v
    pa = math.radians(ponteiro - 90)
    pygame.draw.line(tmp, FG, (c, c), (c + math.cos(pa) * r * 0.8, c + math.sin(pa) * r * 0.8), 8)
    pygame.draw.circle(tmp, FG, (c, c), 18)
    tmp.set_alpha(int(255 * a))
    s.blit(tmp, (cx - c, cy - c))


FAT = [(0.55, (150, 50, 56), "próxima"), (0.25, (110, 60, 66), "resposta"), (0.12, (80, 62, 68), "melhor"), (0.08, (60, 60, 68), "")]


def gira(t, paradas, cada=1.8):
    """Ponteiro que gira e para: a cada `cada` segundos, descansa num dos ângulos de `paradas`."""
    i = int(t / cada)
    k = min(1.0, (t - i * cada) / (cada * 0.6))
    de = paradas[(i - 1) % len(paradas)] if i else 0
    ate = paradas[i % len(paradas)] + 720
    return de + (ate - de) * ease(k)


def p6_roleta(s, t, a):
    roleta(s, CX, PALCO + 300, 270, FAT, gira(t, [80, 250, 120, 330]), a)
    text(s, "a fatia maior sai mais vezes. não sempre.", font("mono", 34), MUTE, (CX, PALCO + 610), "midtop", ap(t, 2.0) * a)


def p6_temperatura(s, t, a):
    baixa = [(0.9, (150, 50, 56), ""), (0.07, (110, 60, 66), ""), (0.03, (60, 60, 68), "")]
    alta = [(0.4, (150, 50, 56), ""), (0.3, (110, 60, 66), ""), (0.18, (80, 62, 68), ""), (0.12, (60, 60, 68), "")]
    for j, (rot, fat, leg, par) in enumerate((("TEMPERATURA BAIXA", baixa, "previsível", [100, 200, 60]), ("TEMPERATURA ALTA", alta, "variado", [60, 200, 290, 340]))):
        k = ap(t, 0.3 + j * 1.6) * a
        cx = M + 230 + j * 470
        text(s, rot, font("mono-md", 30), MUTE if j == 0 else RED_SOFT, (cx, PALCO + 20), "midtop", k)
        roleta(s, cx, PALCO + 280, 190, fat, gira(max(0, t - 0.3 - j * 1.6), par, 1.4), k)
        text(s, leg, font("sans-sb", 46), FG, (cx, PALCO + 510), "midtop", k)


def p6_minimo(s, t, a):
    for j, txt in enumerate(("O relatório aponta três causas.", "O relatório indica três causas.", "São três as causas apontadas.")):
        k = ap(t, 0.4 + j * 1.1) * a
        bloco(s, (M, PALCO + 40 + j * 150, W - 2 * M, 120), a=k)
        text(s, txt, font("sans-md", 42), FG, (M + 34, PALCO + 100 + j * 150), "midleft", k)
    text(s, "mesma pergunta, três respostas válidas", font("mono", 34), MUTE, (CX, PALCO + 520), "midtop", ap(t, 3.6) * a)


def p6_pedido(s, t, a):
    bloco(s, (M, PALCO + 30, W - 2 * M, 480), CARD, VERDE, a, esp=4)
    for j, (rot, l1, l2) in enumerate((("formato fixo", "Responda numa tabela:", "causa, evidência, ação."), ("um exemplo", "Siga o modelo do", "relatório abaixo."))):
        k = ap(t, 0.5 + j * 1.5) * a
        text(s, rot, font("mono-md", 32), RED_SOFT, (M + 36, PALCO + 64 + j * 220), "topleft", k)
        text(s, l1, font("sans-md", 44), FG, (M + 36, PALCO + 114 + j * 220), "topleft", k)
        text(s, l2, font("sans-md", 44), FG, (M + 36, PALCO + 170 + j * 220), "topleft", k)


P6 = [
    (4.0, "", [], ("", ""), abertura(["Mesma pergunta,", "respostas", "diferentes?"], "não é bug")),
    (8.0, "O MECANISMO · AMOSTRAGEM", ["Ela gira", "uma roleta"], ("A cada palavra, ela sorteia", "entre os palpites mais prováveis."), p6_roleta),
    (8.0, "O BOTÃO", ["Temperatura"], ("É o botão da ousadia:", "baixa, previsível; alta, variado."), p6_temperatura),
    (6.5, "UM DETALHE", ["Nem no mínimo", "sai idêntico"], ("Dá para reduzir a variação,", "não para zerar."), p6_minimo),
    (7.5, "COMO DOMAR", ["Você controla", "pelo pedido"], ("Quanto mais ele define o resultado,", "menos sobra para o sorteio."), p6_pedido),
    (7.5, "NA PRÁTICA", ["Use o sorteio", "a seu favor"], ("Decida antes: você quer", "padrão ou quer opções?"),
     pratica([("quer padrão: trave o formato", "modelo de resposta e um exemplo"), ("quer ideias: peça várias", "a variação trabalha para você"),
              ("decisão importante", "pergunte duas vezes e compare")])),
    (4.5, "", [], ("", ""), fechamento("Não é bug: é sorteio. E dá para domar.")),
]

# =====================================================================================
# PARTE 7 · até quando a IA sabe das coisas
# =====================================================================================
def p7_foto(s, t, a):
    k = ap(t, 0.8, 0.5) * a
    clarao = max(0.0, 1 - abs(t - 0.7) / 0.25)                            # o flash da câmera
    if clarao > 0:
        rrect(s, (255, 255, 255, int(170 * clarao * a)), (M, PALCO, W - 2 * M, 560), 30)
    ang = -4 * ap(t, 0.8, 0.6)
    foto = pygame.Surface((640, 520), pygame.SRCALPHA)
    pygame.draw.rect(foto, (236, 236, 239), (0, 0, 640, 520), border_radius=14)
    pygame.draw.rect(foto, CARD_2, (30, 30, 580, 380))
    for i, fr in enumerate((0.8, 0.6, 0.72, 0.5, 0.66, 0.58)):
        pygame.draw.rect(foto, (90, 90, 100), (64, 70 + i * 52, 512 * fr, 16), border_radius=8)
    foto.blit(font("mono", 30).render("tudo o que ela leu", True, (60, 60, 68)), (150, 440))
    foto = pygame.transform.rotozoom(foto, ang, 1.0)
    foto.set_alpha(int(255 * k))
    s.blit(foto, foto.get_rect(center=(CX, PALCO + 300)))


def p7_corte(s, t, a):
    y = PALCO + 260
    x0, x1, xc = M, W - M, M + 560
    k = ap(t, 0.4, 1.4)
    pygame.draw.line(s, mix(INK, RED, a), (x0, y), (x0 + (xc - x0) * k, y), 12)
    text(s, "o que ela leu", font("sans-md", 44), FG, ((x0 + xc) / 2, y - 70), "center", ap(t, 0.8) * a)
    k2 = ap(t, 2.0)
    if k2 > 0:
        pygame.draw.circle(s, mix(INK, RED, a), (xc, y), int(24 * k2))
        text(s, "data de corte", font("mono-md", 36), RED_SOFT, (xc, y + 70), "center", k2 * a)
    k3 = ap(t, 3.0, 1.0)
    if k3 > 0:
        pygame.draw.line(s, mix(INK, (70, 70, 80), a), (xc, y), (xc + (x1 - xc) * k3, y), 12)
        text(s, "não viu", font("sans-md", 44), MUTE, ((xc + x1) / 2, y - 70), "center", k3 * a)
        text(s, "hoje", font("mono-md", 36), FG, (x1, y + 70), "midright", ap(t, 3.8) * a)


def p7_empresa(s, t, a):
    for j, it in enumerate(("procedimentos internos", "contratos e propostas", "histórico de equipamentos", "decisões e atas")):
        k = ap(t, 0.3 + j * 0.6) * a
        y = PALCO + 30 + j * 140
        bloco(s, (M, y, W - 2 * M, 114), a=k)
        text(s, it, font("sans-md", 44), FG, (M + 36, y + 57), "midleft", k)
        text(s, "fora da foto", font("mono", 30), RED_SOFT, (W - M - 36, y + 57), "midright", ap(t, 1.0 + j * 0.6) * a)


def p7_avisa(s, t, a):
    k = ap(t, 0.4) * a
    fala(s, "Qual é a regra em vigor?", PALCO + 30, True, k)
    kk = ap(t, 1.6) * a
    bloco(s, (M, PALCO + 160, W - 2 * M - 100, 130), CARD_2, LINHA, kk)
    text(s, "A regra em vigor é a de…", font("sans-md", 42), FG, (M + 34, PALCO + 225), "midleft", kk)
    k3 = ap(t, 3.0) * a
    bloco(s, (M, PALCO + 360, W - 2 * M, 130), CARD, RED, k3, esp=4)
    text(s, "informação velha, com cara de nova", font("sans-md", 40), FG, (CX, PALCO + 425), "center", k3)


def p7_jornal(s, t, a):
    bloco(s, (M, PALCO + 300, W - 2 * M, 380), CARD, RED, a, esp=4)
    text(s, "A MESA · JANELA DE CONTEXTO", font("mono-md", 30), RED_SOFT, (M + 30, PALCO + 322), "topleft", a)
    for j, (rot, cor) in enumerate((("busca na internet, com fontes", (30, 50, 40)), ("o seu documento", (30, 50, 40)), ("sua pergunta", (70, 30, 34)))):
        k = ap(t, 0.6 + j * 1.3, 0.7)
        if k <= 0:
            continue
        y = PALCO + 390 + j * 96 - (1 - k) * (360 + j * 96)
        bloco(s, (M + 30, y, W - 2 * M - 60, 78), cor, None, a * min(1, k * 2), 16)
        text(s, rot, font("sans-md", 38), FG, (M + 60, y + 39), "midleft", a * min(1, k * 2))
    text(s, "a informação nova entra pela conversa", font("mono", 32), MUTE, (CX, PALCO + 40), "midtop", ap(t, 0.3) * a)
    text(s, "a foto continua a mesma", font("mono", 32), MUTE, (CX, PALCO + 90), "midtop", ap(t, 0.3) * a)


P7 = [
    (4.0, "", [], ("", ""), abertura(["Até quando", "a IA sabe", "das coisas?"], "o conhecimento dela tem data")),
    (6.5, "A ORIGEM", ["O treino é uma", "fotografia"], ("Tudo o que estava escrito", "até um certo dia."), p7_foto),
    (7.0, "O NOME TÉCNICO", ["Data de corte"], ("É o dia em que a foto foi tirada.", "O que veio depois, ela não viu."), p7_corte),
    (6.5, "MAIS IMPORTANTE", ["A sua empresa", "não saiu na foto"], ("O que é interno nunca esteve", "nos textos que ela leu."), p7_empresa),
    (6.5, "O PERIGO", ["Ela nem sempre", "avisa"], ("Pode responder com", "o que tinha na foto."), p7_avisa),
    (7.5, "COMO RESOLVERAM", ["O jornal do dia", "em cima da mesa"], ("Ela busca na internet,", "e você entrega o documento."), p7_jornal),
    (7.5, "NA PRÁTICA", ["Isso estava", "na foto?"], ("Se não estava, a informação", "tem de entrar pela conversa."),
     pratica([("assunto recente: peça para buscar", "e confira as fontes"), ("assunto interno: entregue o documento", "ela não tem como saber"),
              ("regra, preço e prazo", "confirme a data da informação")])),
    (4.5, "", [], ("", ""), fechamento("O que não estava na foto, só se você mostrar.")),
]

# =====================================================================================
# PARTE 8 · precisa sempre da IA mais potente?
# =====================================================================================
def p8_modelo(s, t, a):
    base_y = PALCO + 480
    for j, (rot, lado) in enumerate((("pequeno", 150), ("médio", 240), ("grande", 340))):
        k = ap(t, 0.4 + j * 0.9, 0.6)
        if k <= 0:
            continue
        x = M + 20 + (0, 220, 530)[j]
        l = lado * k
        bloco(s, (x, base_y - l, l, l), CARD, RED if j == 2 else LINHA, a * k, esp=4 if j == 2 else 2)
        text(s, rot, font("sans-md", 40), FG, (x + lado / 2, base_y + 30), "midtop", a * k)


def p8_troca(s, t, a):
    for j, (rot, vals) in enumerate((("PEQUENO", (0.4, 1.0, 0.2)), ("GRANDE", (1.0, 0.45, 1.0)))):
        y0 = PALCO + 20 + j * 330
        k0 = ap(t, 0.3 + j * 1.8) * a
        text(s, rot, font("mono-md", 34), MUTE if j == 0 else RED_SOFT, (M, y0), "topleft", k0)
        for i, (nome, v) in enumerate(zip(("capacidade", "velocidade", "custo"), vals)):
            k = ap(t, 0.5 + j * 1.8 + i * 0.25, 0.8)
            yy = y0 + 64 + i * 80
            text(s, nome, font("sans", 36), BODY, (M, yy + 24), "midleft", k0)
            rrect(s, (255, 255, 255, int(18 * k0)), (M + 250, yy, W - 2 * M - 250, 48), 24)
            rrect(s, (RED if i == 2 else VERDE) + (int(255 * k0),), (M + 250, yy, max(48, (W - 2 * M - 250) * v * k), 48), 24)


def p8_frota(s, t, a):
    cartoes(s, [("a moto: modelo pequeno", "classificar, separar, extrair um dado"), ("a van: modelo médio", "redigir, revisar, responder"),
                ("o caminhão: modelo grande", "análise longa, problema difícil")], PALCO + 30, t, a, espera=1.3)


def p8_dica(s, t, a):
    for j, (num, txt) in enumerate((("1", "comece pelo menor"), ("2", "teste com os seus casos"), ("3", "suba só onde faltar"))):
        k = ap(t, 0.4 + j * 1.4) * a
        y = PALCO + 40 + j * 180
        pygame.draw.circle(s, mix(INK, RED, k), (M + 50, y + 60), 46)
        text(s, num, font("sans-b", 48), INK, (M + 50, y + 60), "center", k)
        text(s, txt, font("sans-md", 50), FG, (M + 130, y + 60), "midleft", k)
        if j < 2:
            pygame.draw.line(s, mix(INK, LINHA, ap(t, 1.0 + j * 1.4) * a), (M + 50, y + 112), (M + 50, y + 190), 4)


P8 = [
    (4.0, "", [], ("", ""), abertura(["Precisa sempre", "da IA mais", "potente?"], "IA também tem tamanho")),
    (6.5, "O NOME TÉCNICO", ["Modelo"], ("Cada IA é um modelo, e eles vêm", "em vários tamanhos."), p8_modelo),
    (8.0, "A TROCA", ["Capacidade,", "velocidade e custo"], ("O maior resolve mais,", "mas demora mais e custa mais."), p8_troca),
    (8.0, "A METÁFORA", ["Monte a frota"], ("Cada veículo", "para a sua carga."), p8_frota),
    (7.5, "A DICA DE QUEM FABRICA", ["Comece pelo menor.", "Suba se faltar."], ("Muita tarefa do dia a dia", "cabe no modelo pequeno."), p8_dica),
    (7.5, "NA PRÁTICA", ["Escolha pelo", "tamanho da tarefa"], ("Antes da ferramenta,", "olhe para a carga."),
     pratica([("muito volume, tarefa simples", "modelo pequeno: rápido e barato"), ("pouco volume, decisão difícil", "modelo grande: vale o custo"),
              ("na dúvida, teste", "com os seus casos reais")])),
    (4.5, "", [], ("", ""), fechamento("A maior nem sempre é a melhor escolha.")),
]

PARTES = {1: P1, 2: P2, 3: P3, 4: P4, 5: P5, 6: P6, 7: P7, 8: P8}
TROCA = 0.4                                               # segundos de transição entre cenas

# ---------------- narração ----------------
# Com parteN/narracao.mp3 + parteN/narracao.json (feito por transcrever.py), cada cena dura o tempo da fala dela.
# Âncora = as primeiras palavras de cada cena na narração (a cena 1 começa no zero).
ANCORAS = {
    1: ["voce ja viu", "faz o mesmo", "escolhe uma", "de onde", "mas cuidado", "por isso", "a sua imaginacao"],
    2: ["porque ela nao", "esse corte", "e cada token", "por isso numa", "a solucao", "na pratica", "a sua imaginacao"],
    3: ["porque ela nao", "e essa leitura", "em conversa longa", "e numa conversa", "a solucao foi", "na pratica", "a sua imaginacao"],
    4: ["com um mecanismo", "e assim que", "mas o peso", "e as pesquisas", "por isso a", "na pratica", "a sua imaginacao"],
    5: ["porque ela escreve", "o nome disso", "e como um", "o perigo mora", "a solucao e", "na pratica", "a sua imaginacao"],
    6: ["gira uma roleta", "o botao que", "e nem no", "voce controla", "na pratica", "a sua imaginacao"],
    7: ["o treino dela", "esse dia se", "e a sua empresa", "o perigo e", "a solucao", "na pratica", "a sua imaginacao"],
    8: ["e um modelo", "o maior resolve", "pense numa frota", "a dica de", "na pratica", "a sua imaginacao"],
}
RECUO = {(1, 1): 2, (6, 0): 3, (8, 0): 3}                                       # "A IA faz o mesmo": a cena começa duas palavras antes da âncora
ATRASO = 0.5                                              # a fala entra meio segundo depois do começo do vídeo
ANTES = 0.35                                              # a cena troca um pouco antes de a fala dela começar


def _limpa(w):
    import unicodedata
    w = unicodedata.normalize("NFD", w.lower())
    return "".join(c for c in w if c.isalnum())


def narracao(parte):
    """-> (caminho do mp3, duração de cada cena seguindo a fala) ou None se não houver narração."""
    base = os.path.join(AQUI, f"parte{parte}", "narracao")
    if not (os.path.exists(base + ".mp3") and os.path.exists(base + ".json")):
        return None
    import json
    with open(base + ".json", encoding="utf-8") as f:
        d = json.load(f)
    palavras = [(_limpa(w[2]), w[0]) for w in d["palavras"]]
    inicios, pos = [0.0], 0
    for k, ancora in enumerate(ANCORAS[parte]):
        alvo = ancora.split()
        achou = next((i for i in range(pos, len(palavras) - len(alvo) + 1)
                      if [w for w, _ in palavras[i:i + len(alvo)]] == alvo), None)
        if achou is None:
            raise ValueError(f"parte {parte}: não achei a âncora '{ancora}' na narração")
        i = max(0, achou - RECUO.get((parte, k), 0))
        inicios.append(palavras[i][1] + ATRASO - ANTES)
        pos = achou + len(alvo)
    fim = d["duracao"] + ATRASO + 1.8                     # respiro no fechamento
    return base + ".mp3", [b - a for a, b in zip(inicios, inicios[1:] + [fim])]


_cache = {}


def cenas_de(parte):
    """As cenas da parte, com a duração da fala quando há narração: [(duração, duração original, ...)]"""
    if parte not in _cache:
        n = narracao(parte)
        duracoes = n[1] if n else [c[0] for c in PARTES[parte]]
        _cache[parte] = [(d,) + c for d, c in zip(duracoes, PARTES[parte])]
    return _cache[parte]


def quadro(parte, t):
    cenas = cenas_de(parte)
    total = sum(c[0] for c in cenas)
    s = FUNDO.copy()
    pygame.draw.circle(s, RED, (M + 12, 230), 12)
    text(s, "elucas.dev", font("sans-sb", 38), FG, (M + 40, 230), "midleft")
    text(s, f"IA SEM MISTÉRIO · {parte}", font("mono", 30), MUTE, (W - M, 230), "midright")
    rrect(s, (255, 255, 255, 20), (M, 280, W - 2 * M, 6), 3)
    rrect(s, RED, (M, 280, (W - 2 * M) * min(1, t / total), 6), 3)
    ini = 0.0
    for dur, original, olho, tit, leg, fn in cenas:
        tl = t - ini
        if 0 <= tl < dur:
            a = min(ease(tl / TROCA), ease((dur - tl) / TROCA))
            tl *= max(1.0, original / dur)                # cena mais curta que a original: a animação acelera para caber
            text(s, olho, font("mono-md", 32), RED_SOFT, (M, 370), "topleft", a)
            for i, l in enumerate(tit):
                text(s, l, font("sans-b", 80), FG, (M, 424 + i * 92), "topleft", a)
            fn(s, tl, a)
            text(s, leg[0], font("sans-md", 46), FG, (CX, 1500), "midtop", a)
            text(s, leg[1], font("sans-md", 46), BODY, (CX, 1562), "midtop", a)
        ini += dur
    k = min(1.0, t / 0.4, (total - t) / 0.5)
    if k < 1:
        veu = pygame.Surface((W, H))
        veu.fill(INK)
        veu.set_alpha(int(255 * (1 - max(0, k))))
        s.blit(veu, (0, 0))
    return s


def renderizar(parte):
    import trilha
    total = sum(c[0] for c in cenas_de(parte))
    out = os.path.join(AQUI, f"parte{parte}", "short.mp4")
    p = subprocess.Popen([trilha.FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                          "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", out], stdin=subprocess.PIPE)
    for n in range(int(total * FPS)):
        p.stdin.write(pygame.image.tobytes(quadro(parte, n / FPS), "RGB"))
    p.stdin.close()
    p.wait()
    musica = os.path.join(trilha.AQUI, ("tranquil_mindscape.mp3", "lucid.mp3", "tokyo_sunset.mp3", "when_i_was_human.mp3")[(parte - 1) % 4] if parte > 4 else ("lucid.mp3" if parte % 2 == 0 else "tranquil_mindscape.mp3"))
    n = narracao(parte)
    if not n:
        trilha.colocar(out, musica)
        return
    # narração na frente (-16 LUFS), trilha lo-fi baixa por trás, com fade no começo e no fim
    tmp = out[:-4] + "_tmp.mp4"
    filtro = (f"[1:a]adelay={int(ATRASO * 1000)}:all=1,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[voz];"
              f"[2:a]atrim=0:{total:.3f},asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-1.5:LRA=11,volume=0.13,"
              f"afade=t=in:st=0:d=1,afade=t=out:st={total - 2.5:.3f}:d=2.5,aresample=48000[mus];"
              f"[voz][mus]amix=inputs=2:duration=longest:normalize=0,atrim=0:{total:.3f}[a]")
    subprocess.run([trilha.FFMPEG, "-v", "error", "-y", "-i", out, "-i", n[0], "-i", musica, "-filter_complex", filtro,
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}", tmp],
                   check=True)
    os.replace(tmp, out)
    print(f"OK {out}  ({total:.1f} s, com narração)")


if __name__ == "__main__":
    alvo = sys.argv[1] if len(sys.argv) > 1 else "todos"
    if "--still" in sys.argv:
        t = float(sys.argv[sys.argv.index("--still") + 1])
        pygame.image.save(quadro(int(alvo), t), os.path.join(AQUI, f"parte{alvo}", f"_quadro_{t}.png"))
    else:
        for parte in (sorted(PARTES) if alvo == "todos" else [int(x) for x in alvo.split(",")]):
            renderizar(parte)
