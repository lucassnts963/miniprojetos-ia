"""Vídeo YouTube (1920x1080): rede neural do zero, camada por camada, no tema elucas.dev.

Todo o código mostrado é o de ../../tutorial/triagem_do_zero.py, com os números reais das
linhas. Os valores das visualizações são calculados aqui, rodando esse mesmo código.

uso (venv com numpy, pygame e pygments, ex.: C:/dev/snake/venv):
  python render.py                  -> out/video_silent.mp4
  python render.py --still cena t   -> out/still_<cena>_<t>.png
  python render.py --lista          -> cenas, durações e capítulos
"""
import copy
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
TUT = os.path.join(PROJ, "tutorial")
sys.path.insert(0, os.path.join(os.path.dirname(PROJ), "ferramentas", "youtube"))
sys.path.insert(0, TUT)
from tema import *  # noqa: E402,F401,F403
from tema import (BACKDROP, BODY, CARD, CARD_2, FG, FPS, H, INK, LINE_A, LINE_ON_CARD, MUTE, PRIO, RED,  # noqa: E402
                  RED_SOFT, TINT_A, W, active_hl, appear, badge, barra_h, card, chip, chrome, code_block, ease,
                  eyebrow, font, lerp, mix, rrect, text, titulo)
import pygame  # noqa: E402
import triagem_do_zero as T  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
ARQ = "triagem_do_zero.py"
SRC = open(os.path.join(TUT, ARQ), encoding="utf-8").read().split("\n")

# ---------------- roda o tutorial (mesmo passo a passo do __main__) ----------------
TEXTOS, Y_EQ, Y_PR = T.carregar(os.path.join(TUT, "chamados.csv"))
_ordem = np.random.default_rng(42).permutation(len(TEXTOS))
_corte = int(len(TEXTOS) * 0.8)
TR, TE = _ordem[:_corte], _ordem[_corte:]
TFIDF = T.Tfidf().fit([TEXTOS[i] for i in TR])
X_TR = TFIDF.transform([TEXTOS[i] for i in TR])
X_TE = TFIDF.transform([TEXTOS[i] for i in TE])
V = X_TR.shape[1]
REDE0 = T.criar_rede(V)
REDE = copy.deepcopy(REDE0)


def treinar_registrando(rede, X, ye, yp, epocas=100, lr=0.002, l2=3e-3, dropout=0.5, lote=32, seed=0):
    """Igual ao T.treinar (mesma sequência aleatória), guardando perda e acerto de teste por época."""
    rng = np.random.default_rng(seed)
    m = {k: np.zeros_like(w) for k, w in rede.items()}
    v = {k: np.zeros_like(w) for k, w in rede.items()}
    passo, hist = 0, []
    for _ in range(epocas):
        ordem = rng.permutation(len(X))
        for ini in range(0, len(X), lote):
            idx = ordem[ini:ini + lote]
            g = T.gradientes(rede, X[idx], ye[idx], yp[idx], dropout, rng)
            passo += 1
            for k in rede:
                if k.startswith("W"):
                    g[k] += l2 * rede[k]
                m[k] = 0.9 * m[k] + 0.1 * g[k]
                v[k] = 0.999 * v[k] + 0.001 * g[k] ** 2
                m_hat = m[k] / (1 - 0.9 ** passo)
                v_hat = v[k] / (1 - 0.999 ** passo)
                rede[k] -= lr * m_hat / (np.sqrt(v_hat) + 1e-8)
        _, _, pe, pp = T.forward(rede, X)
        _, _, qe, qp = T.forward(rede, X_TE)
        hist.append((T.perda(pe, pp, ye, yp), (qe.argmax(1) == Y_EQ[TE]).mean(), (qp.argmax(1) == Y_PR[TE]).mean()))
    return hist


HIST = treinar_registrando(REDE, X_TR, Y_EQ[TR], Y_PR[TR])
_, _, _pe, _pp = T.forward(REDE, X_TE)
ACC_EQ, ACC_PR = (_pe.argmax(1) == Y_EQ[TE]).mean(), (_pp.argmax(1) == Y_PR[TE]).mean()
PREV_EQ_TE = _pe.argmax(1)
N_PARAMS = sum(w.size for w in REDE.values())

HOOK_TXT = "o motor da bomba 2 tá cheirando queimado"
HOOK = T.classificar(REDE, TFIDF, HOOK_TXT)
EX = "vazamento de óleo na prensa, pingando no chão"
X_EX = TFIDF.transform([EX])
Z1_EX, H_EX, PEQ_EX, PPR_EX = T.forward(REDE, X_EX)
TERMINAL = [f"época {i + 1:3d}  perda {HIST[i][0]:.3f}" for i in range(9, 100, 10)]
TERMINAL += [f"teste  equipe {ACC_EQ:.0%}  prioridade {ACC_PR:.0%}", str(HOOK)]
print(f"tutorial: vocab {V}, params {N_PARAMS}, teste equipe {ACC_EQ:.0%} prioridade {ACC_PR:.0%}, "
      f"exemplo -> {HOOK}", flush=True)


def fmt(n):
    return f"{n:,}".replace(",", ".")


# ---------------- cenas + tempos da narração ----------------
SCENES = []
_TIMING_PATH = os.path.join(HERE, "narr", "timing.json")
TIMING = json.load(open(_TIMING_PATH, encoding="utf-8"))["scenes"] if os.path.exists(_TIMING_PATH) else {}
_CUR = {"cues": {}, "dur": 0}


def C(name, default):
    """Momento (s) em que a narração diz a frase ligada a este cue; senão o padrão."""
    return _CUR["cues"].get(name, default)


def scene(name, dur, chapter=None):
    def deco(fn):
        tm = TIMING.get(name, {})
        SCENES.append(dict(name=name, dur=tm.get("dur", dur), fn=fn, chapter=chapter, cues=tm.get("cues", {})))
        return fn
    return deco


# ---------------- peças de layout ----------------
TOP = 236
BOTTOM = 990


def L(trecho, apos=1):
    """Número (1-indexado) da primeira linha do tutorial, a partir de `apos`, que contém o trecho."""
    for i in range(apos - 1, len(SRC)):
        if trecho in SRC[i]:
            return i + 1
    raise ValueError(f"trecho não encontrado no tutorial: {trecho!r}")


def faixa(n):
    """Linhas do PASSO n (do cabeçalho até antes do próximo passo)."""
    a = L(f"PASSO {n} ·")
    try:
        b = L(f"PASSO {n + 1} ·") - 1
    except ValueError:
        b = len(SRC)
    while not SRC[b - 1].strip():
        b -= 1
    return a, b


def code(s, t, first, last, marks, x=100, w=1010, min_size=19):
    """Bloco de código com destaque pelos cues.

    marks = [(t, None | (trecho_inicio, trecho_fim))]: os trechos viram números de linha, então o render
    não quebra quando o tutorial muda. A fonte encolhe até min_size; se ainda não couber em altura,
    a janela rola (suave) para mostrar o trecho destacado.
    """
    res = [(ts, None if r is None else (L(r[0], first), L(r[1], L(r[0], first)))) for ts, r in marks]
    maior = max(len(ln) for ln in SRC[first - 1:last])
    size = 21
    while size > min_size and (font("mono", size).size("0" * (maior + 4))[0] + 48 > w
                               or (last - first + 1) * int(size * 1.5) + 72 > BOTTOM - TOP):
        size -= 1
    n_vis = (BOTTOM - TOP - 72) // int(size * 1.5)
    hl = active_hl(t, res)
    a = first
    if last - first + 1 > n_vis:
        def inicio(h):
            if h is None:
                return first
            meio = (h[0] + h[1]) / 2
            return int(max(first, min(last - n_vis + 1, meio - n_vis / 2)))
        atual = [i for i, (ts, _) in enumerate(res) if t >= ts]
        k_i = atual[-1] if atual else 0
        antes = inicio(res[k_i - 1][1]) if k_i > 0 else first
        k = ease((t - res[k_i][0]) / 0.7)
        a = int(round(lerp(antes, inicio(res[k_i][1]), k)))
    code_block(s, (x, TOP, w, BOTTOM - TOP), SRC, a, min(last, a + n_vis - 1), t, hl, ARQ, size, reveal=0.1)


def painel(s, rect, titulo_txt=None, alpha=1.0):
    if alpha <= 0:
        return
    tmp = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    card(tmp, (0, 0, rect[2], rect[3]), titulo_txt)
    tmp.set_alpha(int(255 * alpha))
    s.blit(tmp, (rect[0], rect[1]))


def rotulo(s, txt, pos, alpha=1.0, anchor="topleft"):
    return text(s, txt, font("mono-md", 17), MUTE, pos, anchor, alpha)


def chips_linha(s, itens, x, y, largura, t0, t, f=None, cores=None, passo=0.04, gap=8):
    """Chips com quebra de linha; aparecem em sequência a partir de t0. Retorna o y final."""
    f = f or font("mono", 19)
    cx, cy = x, y
    alt = f.get_height() + 12
    for i, it in enumerate(itens):
        w_ = f.size(it)[0] + 24
        if cx > x and cx + w_ > x + largura:
            cx, cy = x, cy + alt + gap
        a = appear(t, t0 + i * passo, 0.3)
        if a > 0:
            fg, bg, borda = (cores or {}).get(i, (FG, CARD_2, LINE_A))
            chip(s, it, (cx, cy), f, fg, bg, borda, a)
        cx += w_ + gap
    return cy + alt


def seta(s, a, b, cor=MUTE, alpha=1.0, largura=2):
    if alpha <= 0:
        return
    c = mix(INK, cor, alpha)
    pygame.draw.line(s, c, a, b, largura)
    d = np.array(b, float) - np.array(a, float)
    d /= np.linalg.norm(d) + 1e-9
    n = np.array([-d[1], d[0]])
    p1 = np.array(b) - d * 12 + n * 6
    p2 = np.array(b) - d * 12 - n * 6
    pygame.draw.polygon(s, c, [b, tuple(p1), tuple(p2)])


def barras_prob(s, x, y, nomes, probs, alpha=1.0, cores=None, larg=300, altura=14, gap=34, f=None):
    f = f or font("sans", 22)
    top = int(np.argmax(probs))
    for i, (n, p) in enumerate(zip(nomes, probs)):
        yy = y + i * gap
        cor = (cores or {}).get(n, RED if i == top else (70, 70, 78))
        text(s, n, f, FG if i == top else MUTE, (x, yy + altura // 2), "midleft", alpha)
        barra_h(s, x + 200, yy, larg, altura, p, cor, alpha=alpha)
        text(s, f"{p:.0%}", font("mono", 18), FG if i == top else MUTE, (x + 215 + larg, yy + altura // 2),
             "midleft", alpha)


def barras_verticais(s, rect, vals, alpha=1.0, escala=None, cor_pos=RED, cor_neg=(95, 95, 105), cortes=()):
    """Barras verticais em torno de uma linha de zero (ativações de uma camada)."""
    x, y, w, h = rect
    n = len(vals)
    escala = escala or (np.abs(vals).max() + 1e-9)
    meio = y + h // 2
    pygame.draw.line(s, mix(INK, MUTE, 0.5 * alpha), (x, meio), (x + w, meio), 1)
    bw = w / n
    for i, v in enumerate(vals):
        alt = int((h / 2 - 4) * min(1, abs(v) / escala))
        cor = cor_pos if v > 0 else cor_neg
        bx = int(x + i * bw + 2)
        r = (bx, meio - alt, max(2, int(bw - 4)), alt) if v > 0 else (bx, meio, max(2, int(bw - 4)), alt)
        if alt > 0:
            pygame.draw.rect(s, mix(INK, cor, alpha), r, border_radius=2)
        if i in cortes:
            pygame.draw.line(s, mix(INK, MUTE, alpha), (bx, meio + 8), (bx + int(bw - 4), meio + 8), 2)


# ================= CENAS =================
@scene("hook", 11.0)
def s_hook(s, t):
    box = pygame.Rect(360, 230, 1200, 118)
    card(s, box)
    n = int(len(HOOK_TXT) * min(1, max(0, (t - 0.6) / 2.0)))
    cursor = "|" if (t < 2.6 or int(t * 2.5) % 2 == 0) else ""
    rotulo(s, "NOVO CHAMADO", (box.x + 32, box.y + 22))
    text(s, HOOK_TXT[:n] + cursor, font("sans", 40), FG, (box.x + 32, box.y + 50))
    a = appear(t, 3.0)
    if a > 0:
        _, _, pe, pp = T.forward(REDE, TFIDF.transform([HOOK_TXT]))
        for i, (nome, nomes, probs, cores) in enumerate([
                ("EQUIPE", T.EQUIPES, pe[0], None),
                ("PRIORIDADE", T.PRIORIDADES, pp[0], PRIO)]):
            r = pygame.Rect(360 + i * 612, 380 + int((1 - a) * 16), 588, 290)
            painel(s, r, alpha=a)
            rotulo(s, nome, (r.x + 32, r.y + 26), a)
            top = nomes[int(np.argmax(probs))]
            text(s, top, font("sans-b", 40), FG, (r.x + 32, r.y + 52), alpha=a)
            barras_prob(s, r.x + 32, r.y + 128, nomes, probs, a, larg=230,
                        cores={k: v for k, v in (cores or {}).items()} if cores else None)
    text(s, "sem API  ·  sem PyTorch  ·  só NumPy", font("mono-md", 30), RED_SOFT, (W // 2, 740), "midtop",
         appear(t, C("sem", 5.2)))
    text(s, "e você vai escrever cada linha", font("sans-b", 54), FG, (W // 2, 810), "midtop",
         appear(t, C("cada", 7.2)))


@scene("titulo", 4.5)
def s_titulo(s, t):
    eyebrow(s, "// do zero, em python", (W // 2, 330), appear(t, 0), "midtop")
    text(s, "Rede neural que lê chamados", font("sans-b", 84), FG, (W // 2, 380), "midtop", appear(t, 0.15))
    text(s, "camada por camada  ·  só NumPy", font("sans", 38), BODY, (W // 2, 510), "midtop", appear(t, 0.5))
    badge(s, "TRIAGEM DE MANUTENÇÃO", (W // 2, 620), 20, "midtop", appear(t, 0.8))


@scene("mapa", 18.0, "o caminho")
def s_mapa(s, t):
    titulo(s, t, "// o caminho", "Do texto à decisão")
    caixas = [("texto", "chamado", 0.3), ("palavras", "passo 2", C("palavras", 1.5)),
              ("termos", "passo 3", C("palavras", 1.5) + 0.8), ("TF-IDF", "passo 4", C("tfidf", 3.5)),
              ("oculta", "32 neurônios", C("oculta", 6.0))]
    x0, y0, bw, bh, gap = 110, 360, 250, 110, 48
    for i, (nome, sub, ts) in enumerate(caixas):
        a = appear(t, ts)
        r = pygame.Rect(x0 + i * (bw + gap), y0, bw, bh)
        if a <= 0:
            continue
        painel(s, r, alpha=a)
        text(s, nome, font("sans-sb", 34), FG, (r.centerx, r.y + 30), "midtop", a)
        text(s, sub, font("mono", 18), MUTE, (r.centerx, r.bottom + 14), "midtop", a)
        if i:
            seta(s, (r.x - gap + 6, r.centery), (r.x - 6, r.centery), MUTE, a)
    a = appear(t, C("saidas", 8.0))
    xo = x0 + 5 * (bw + gap)
    for j, (nome, sub) in enumerate([("equipe", "4 classes"), ("prioridade", "4 classes")]):
        r = pygame.Rect(xo, y0 - 70 + j * 140, 260, 100)
        if a > 0:
            rrect(s, TINT_A, r, 16)
            rrect(s, (229, 72, 77, 110), r, 16, 1)
            text(s, nome, font("sans-sb", 32), FG, (r.centerx, r.y + 18), "midtop", a)
            text(s, sub, font("mono", 18), RED_SOFT, (r.centerx, r.y + 62), "midtop", a)
            seta(s, (xo - gap + 6, y0 + bh // 2), (r.x - 6, r.centery), RED, a)
    a = appear(t, C("treino", 11.0))
    if a > 0:
        yb = 720
        itens = [("perda", "passo 7"), ("backprop", "passo 8"), ("Adam", "passo 9")]
        for i, (nome, sub) in enumerate(itens):
            r = pygame.Rect(560 + i * 300, yb, 250, 96)
            painel(s, r, alpha=a)
            text(s, nome, font("sans-sb", 30), FG, (r.centerx, r.y + 18), "midtop", a)
            text(s, sub, font("mono", 18), MUTE, (r.centerx, r.y + 60), "midtop", a)
            if i:
                seta(s, (r.x - 44, r.centery), (r.x - 6, r.centery), MUTE, a)
        text(s, "treino: mede o erro, manda de volta, ajusta os pesos", font("sans", 26), BODY, (560, 850),
             alpha=a)
        pygame.draw.lines(s, mix(INK, RED, 0.8 * a), False,
                          [(1410, yb + 48), (1480, yb + 48), (1480, y0 + bh + 60), (1340, y0 + bh + 60)], 2)
        seta(s, (1340, y0 + bh + 60), (1340, y0 + bh + 8), RED, a)


@scene("setup", 17.0, "preparando")
def s_setup(s, t):
    titulo(s, t, "// preparando", "Um arquivo, uma dependência")
    code(s, t, L("import csv"), L("PRIORIDADES = ["),
         [(0, None), (C("numpy", 1.5), ("import numpy", "import numpy")),
          (C("imports", 5.0), ("import csv", "from collections")),
          (C("classes", 10.0), ("EQUIPES = [", "PRIORIDADES = ["))])
    r = pygame.Rect(1160, TOP, 660, 150)
    painel(s, r, "terminal", appear(t, C("numpy", 1.5)))
    a = appear(t, C("numpy", 1.5) + 0.3)
    text(s, "$", font("mono-sb", 28), RED, (r.x + 30, r.y + 86), "midleft", a)
    text(s, "pip install numpy", font("mono", 28), FG, (r.x + 62, r.y + 86), "midleft", a)
    notas = [("csv", "lê o arquivo de exemplos"), ("math", "log do TF-IDF"), ("re", "separa as palavras"),
             ("unicodedata", "tira os acentos"), ("Counter", "conta os termos"), ("numpy", "a rede inteira")]
    for i, (k, d) in enumerate(notas):
        a = appear(t, C("imports", 5.0) + i * 0.35)
        y = 430 + i * 62
        chip(s, k, (1160, y), font("mono-md", 20), RED_SOFT, CARD_2, (229, 72, 77, 77), a)
        text(s, d, font("sans", 24), BODY, (1380, y + 20), "midleft", a)
    a = appear(t, C("classes", 10.0))
    text(s, "a posição na lista vira o número da classe", font("sans", 24), BODY, (1160, 820), alpha=a)
    for i, e in enumerate(T.EQUIPES):
        chip(s, f"{e} → {i}", (1160 + (i % 2) * 330, 868 + (i // 2) * 56), font("mono", 19), FG, CARD_2, LINE_A, a)


# linhas espalhadas pelo arquivo (as primeiras são todas iguais: mecânica urgente)
AMOSTRA = [3, 95, 170, 240, 330, 400, 470, 540]


@scene("dados", 24.0, "passo 1 · os dados")
def s_dados(s, t):
    titulo(s, t, "// passo 1", "Os dados")
    code(s, t, *faixa(1), [(0, None), (C("csv", 1.5), ("def carregar", "linhas = list")),
                           (C("carregar", 9.0), ("textos = [l", "return textos")),
                           (C("y", 14.0), ("y_eq = np.array", "y_pr = np.array"))])
    r = pygame.Rect(1160, TOP, 660, 400)
    a = appear(t, C("csv", 1.5))
    painel(s, r, "chamados.csv  (amostra)", a)
    f = font("mono", 17)
    todas = open(os.path.join(TUT, "chamados.csv"), encoding="utf-8").read().split("\n")
    linhas = [todas[0]] + [todas[i + 1] for i in AMOSTRA]
    for i, ln in enumerate(linhas):
        aa = appear(t, C("csv", 1.5) + 0.2 + i * 0.12)
        partes = ln.split(";")
        cor = RED_SOFT if i == 0 else FG
        txt = partes[0] if len(partes[0]) <= 34 else partes[0][:33] + "…"
        y = r.y + 66 + i * 36
        text(s, txt, f, cor, (r.x + 24, y), alpha=aa)
        if len(partes) == 3:
            text(s, partes[1][:5], f, cor if i == 0 else BODY, (r.x + 430, y), alpha=aa)
            text(s, partes[2][:5], f, cor if i == 0 else MUTE, (r.x + 540, y), alpha=aa)
    text(s, f"{len(TEXTOS)} chamados", font("sans-sb", 30), FG, (1160, 670), alpha=appear(t, C("csv", 1.5) + 1.5))
    text(s, "gerados uma vez com uma LLM · link na descrição", font("sans", 22), MUTE, (1160, 712),
         alpha=appear(t, C("csv", 1.5) + 2.0))
    a = appear(t, C("y", 14.0))
    if a > 0:
        rotulo(s, "GABARITO DESSAS LINHAS", (1160, 780), a)
        ye = ", ".join(str(Y_EQ[i]) for i in AMOSTRA)
        yp = ", ".join(str(Y_PR[i]) for i in AMOSTRA)
        text(s, f"y_eq → [{ye}]", font("mono", 22), FG, (1160, 812), alpha=a)
        text(s, f"y_pr → [{yp}]", font("mono", 22), FG, (1160, 852), alpha=a)
        text(s, "0 = MECÂNICA · 1 = ELÉTRICA · 2 = INSTRUMENTAÇÃO · 3 = AUTOMAÇÃO", font("mono", 15), MUTE,
             (1160, 900), alpha=a)


@scene("palavras", 20.0, "passo 2 · limpar o texto")
def s_palavras(s, t):
    titulo(s, t, "// passo 2", "Texto → palavras")
    code(s, t, *faixa(2), [(0, None), (C("lower", 1.5), ("normalize(", "normalize(")),
                           (C("acento", 4.0), ("normalize(", '"".join')),
                           (C("regex", 10.0), ("re.findall", "re.findall"))])
    bruto = "Vazamento de ÓLEO na prensa, pingando!"
    etapas = [("entrada", bruto, 0.3), (".lower()", bruto.lower(), C("lower", 1.5)),
              ("NFKD + sem acento", "vazamento de oleo na prensa, pingando!", C("acento", 4.0))]
    for i, (rot, txt, ts) in enumerate(etapas):
        a = appear(t, ts)
        y = TOP + i * 150
        painel(s, (1160, y, 660, 124), alpha=a)
        rotulo(s, rot.upper(), (1188, y + 22), a)
        text(s, txt, font("mono", 25), FG, (1188, y + 60), alpha=a)
    a = appear(t, C("regex", 10.0))
    y = TOP + 3 * 150
    painel(s, (1160, y, 660, 200), alpha=a)
    rotulo(s, "RE.FINDALL  [a-z0-9]+", (1188, y + 22), a)
    chips_linha(s, T.palavras(bruto), 1188, y + 62, 610, C("regex", 10.0) + 0.3, t, font("mono", 24),
                cores={i: (FG, CARD_2, (229, 72, 77, 90)) for i in range(10)})


def _pedacos(p):
    return [x[2:] for x in T.termos(p) if x.startswith("c:")]


@scene("termos", 27.0, "passo 3 · termos")
def s_termos(s, t):
    titulo(s, t, "// passo 3", "Palavras → termos")
    code(s, t, *faixa(3), [(0, None), (C("w", 3.0), ("# palavras", 'out = [f"w:')),
                           (C("b", 5.0), ("# pares", 'f"b:')), (C("c", 9.0), ("# pedaços", 'f"c:')),
                           (C("comp", 12.0), ("# pedaços", 'f"c:'))])
    ex = "óleo pingando"
    ts = T.termos(ex)
    grupos = [("PALAVRAS", [x[2:] for x in ts if x[0] == "w"], C("w", 3.0)),
              ("PARES", [x[2:].replace("_", " ") for x in ts if x[0] == "b"], C("b", 5.0)),
              ("PEDAÇOS DE 3 A 5 LETRAS", [x[2:] for x in ts if x[0] == "c"], C("c", 9.0))]
    comp = appear(t, C("comp", 12.0))
    y = TOP
    rotulo(s, f'EXEMPLO: "{ex}"', (1160, y), 1 - comp)
    y += 40
    for rot, itens, t0 in grupos:
        a = appear(t, t0) * (1 - comp)
        if a <= 0:
            y += 80
            continue
        rotulo(s, rot, (1160, y), a)
        y = chips_linha(s, itens, 1160, y + 30, 660, t0, t, font("mono", 19), passo=0.03) + 22
    if comp > 0:
        a1, a2 = _pedacos("vazando"), _pedacos("vazamento")
        comum = set(a1) & set(a2)
        y = TOP + 40
        for pal, ps in (("vazando", a1), ("vazamento", a2)):
            text(s, pal, font("sans-sb", 32), FG, (1160, y), alpha=comp)
            cores = {i: (FG, (80, 30, 34), (229, 72, 77, 200)) for i, p in enumerate(ps) if p in comum}
            y = chips_linha(s, ps, 1160, y + 48, 660, C("comp", 12.0) + 0.3, t, font("mono", 19), cores,
                            passo=0.03) + 36
        text(s, f"{len(comum)} pedaços em comum", font("sans-b", 34), RED_SOFT, (1160, y + 10),
             alpha=appear(t, C("comp", 12.0) + 1.5))
        text(s, "palavra nova, pedaços conhecidos", font("sans", 26), BODY, (1160, y + 58),
             alpha=appear(t, C("comp", 12.0) + 2.0))


@scene("tfidf", 45.0, "passo 4 · TF-IDF")
def s_tfidf(s, t):
    titulo(s, t, "// passo 4", "TF-IDF: termos → números")
    code(s, t, *faixa(4), [(0, None), (C("df", 3.0), ("def fit", "df.update")),
                           (C("mindf", 8.0), ("vocab = sorted", "self.vocab =")),
                           (C("idf", 11.0), ("n = len(textos)", "self.idf =")),
                           (C("transform", 20.0), ("def transform", "for termo, c")),
                           (C("tf", 28.0), ("j = self.vocab.get", "X[i, j] =")),
                           (C("norma", 34.0), ("X *= self.idf", "return X /"))])
    idf = lambda k: TFIDF.idf[TFIDF.vocab[k]]  # noqa: E731
    linhas = [
        (C("df", 3.0), "df(t)", "em quantos chamados t aparece"),
        (C("mindf", 8.0), "min_df = 2", f"vocabulário: {fmt(V)} termos"),
        (C("idf", 11.0), "idf = ln((1+n)/(1+df)) + 1", f'"de" {idf("w:de"):.2f}  ·  "prensa" {idf("w:prensa"):.2f}'),
        (C("tf", 28.0), "tf = 1 + ln(contagem)", "o termo repetido pesa mais, mas pouco"),
        (C("norma", 34.0), "x = tf·idf / norma(tf·idf)", "curto ou longo, mesma escala"),
    ]
    for i, (ts, form, nota) in enumerate(linhas):
        a = appear(t, ts)
        y = TOP + i * 74
        on = i == max(j for j, (tj, *_r) in enumerate(linhas) if t >= tj) if t >= linhas[0][0] else False
        pygame.draw.rect(s, mix(INK, RED if on else LINE_ON_CARD, a), (1160, y + 4, 4, 58), border_radius=2)
        text(s, form, font("mono-md", 23), FG if on else BODY, (1180, y), alpha=a)
        text(s, nota, font("sans", 21), BODY if on else MUTE, (1180, y + 32), alpha=a)
    a = appear(t, C("transform", 20.0))
    if a > 0:
        y0 = TOP + 5 * 74 + 16
        painel(s, (1160, y0, 660, BOTTOM - y0), alpha=a)
        rotulo(s, "VETOR DO CHAMADO", (1188, y0 + 22), a)
        text(s, f'"{EX}"', font("sans", 19), BODY, (1188, y0 + 48), alpha=a)
        x = X_EX[0]
        idx = np.argsort(-x)[:8]
        inv = {i: k for k, i in TFIDF.vocab.items()}
        for j, i in enumerate(idx):
            aa = appear(t, C("transform", 20.0) + 0.3 + j * 0.12)
            y = y0 + 90 + j * 26
            text(s, inv[i][2:].replace("_", " "), font("mono", 17), FG, (1188, y), alpha=aa)
            barra_h(s, 1360, y + 5, 330, 10, x[i] / x[idx[0]], RED, alpha=aa)
            text(s, f"{x[i]:.2f}", font("mono", 16), MUTE, (1706, y), alpha=aa)
        text(s, f"{int((x > 0).sum())} de {fmt(V)} posições ≠ 0", font("sans-sb", 24), RED_SOFT,
             (1188, BOTTOM - 44), alpha=appear(t, C("transform", 20.0) + 2.0))


@scene("pesos", 30.0, "passo 5 · os pesos")
def s_pesos(s, t):
    titulo(s, t, "// passo 5", "A rede: os pesos")
    code(s, t, *faixa(5), [(0, None), (C("w1", 2.5), ('"W1": pesos', '"W1": pesos')),
                           (C("saidas", 7.0), ('"We": pesos', '"Wp": pesos')),
                           (C("he", 13.0), ("def pesos", "return rng.standard")),
                           (C("total", 22.0), ("return {", "    }"))])
    f = font("mono-md", 20)
    a1 = appear(t, C("w1", 2.5))
    # entrada -> W1 -> oculta
    if a1 > 0:
        rrect(s, (*RED, int(60 * a1)), (1170, 290, 26, 420), 6)
        text(s, "x", f, FG, (1183, 262), "midbottom", a1)
        text(s, f"1×{fmt(V)}", font("mono", 16), MUTE, (1183, 724), "midtop", a1)
        rrect(s, (*RED, int(110 * a1)), (1240, 290, 120, 420), 8)
        text(s, "W1", font("mono-sb", 26), FG, (1300, 500), "center", a1)
        text(s, f"{fmt(V)}×32", font("mono", 16), MUTE, (1300, 724), "midtop", a1)
        rrect(s, (*FG, int(40 * a1)), (1404, 420, 26, 160), 6)
        text(s, "h", f, FG, (1417, 412), "midbottom", a1)
        text(s, "32", font("mono", 16), MUTE, (1417, 590), "midtop", a1)
        seta(s, (1362, 500), (1398, 500), MUTE, a1)
    a2 = appear(t, C("saidas", 7.0))
    if a2 > 0:
        for j, (nome, k) in enumerate([("We", "equipe"), ("Wp", "prioridade")]):
            y = 380 + j * 160
            seta(s, (1434, 500), (1480, y + 40), MUTE, a2)
            rrect(s, (*RED, int(110 * a2)), (1486, y, 110, 80), 8)
            text(s, nome, font("mono-sb", 24), FG, (1541, y + 40), "center", a2)
            text(s, "32×4", font("mono", 16), MUTE, (1541, y + 92), "midtop", a2)
            seta(s, (1600, y + 40), (1640, y + 40), MUTE, a2)
            text(s, k, font("sans-sb", 24), FG, (1650, y + 40), "midleft", a2)
    a = appear(t, C("he", 13.0))
    text(s, "inicialização de He", font("sans-sb", 28), FG, (1160, 790), alpha=a)
    text(s, f"desvio = √(2 / entrada)  →  W1: √(2/{fmt(V)}) ≈ {np.sqrt(2 / V):.3f}", font("mono", 19), BODY,
         (1160, 830), alpha=a)
    a = appear(t, C("total", 22.0))
    text(s, f"{fmt(N_PARAMS)} parâmetros", font("sans-b", 40), RED_SOFT, (1160, 880), alpha=a)
    text(s, "quase todos em W1: um peso por termo, por neurônio", font("sans", 21), MUTE, (1160, 934), alpha=a)


@scene("forward", 38.0, "passo 6 · forward")
def s_forward(s, t):
    titulo(s, t, "// passo 6", "Forward: camada por camada")
    code(s, t, *faixa(6), [(0, None), (C("z1", 2.0), ("z1 = X @", "z1 = X @")),
                           (C("relu", 9.0), ("h = np.maximum", "h = np.maximum")),
                           (C("saidas", 17.0), ("p_eq = softmax", "p_pr = softmax")),
                           (C("saidas", 17.0) + 4.0, ("def softmax", "return e /")),
                           (C("compart", 27.0), ("z1 = X @", "return z1"))])
    rotulo(s, f'CHAMADO: "{EX}"  (rede já treinada)', (1160, TOP), appear(t, 0.3))
    z = Z1_EX[0]
    esc = np.abs(z).max()
    a = appear(t, C("z1", 2.0))
    if a > 0:
        text(s, "z1 = X @ W1 + b1", font("mono-md", 22), FG, (1160, TOP + 36), alpha=a)
        barras_verticais(s, (1160, TOP + 66, 660, 120), z, a, esc)
    k = ease((t - C("relu", 9.0) - 0.4) / 1.2)
    a = appear(t, C("relu", 9.0))
    if a > 0:
        text(s, "h = ReLU(z1)   negativo vira zero", font("mono-md", 22), FG, (1160, TOP + 200), alpha=a)
        hz = np.where(z > 0, z, z * (1 - k))
        barras_verticais(s, (1160, TOP + 230, 660, 120), hz, a, esc,
                         cortes=[i for i in range(len(z)) if z[i] <= 0 and k > 0.9])
    a = appear(t, C("saidas", 17.0))
    if a > 0:
        text(s, "p_eq = softmax(h @ We + be)", font("mono-md", 20), FG, (1160, TOP + 372), alpha=a)
        barras_prob(s, 1160, TOP + 408, T.EQUIPES, PEQ_EX[0], a, larg=270, altura=12, gap=28, f=font("sans", 20))
        text(s, "p_pr = softmax(h @ Wp + bp)", font("mono-md", 20), FG, (1160, TOP + 530), alpha=a)
        barras_prob(s, 1160, TOP + 566, T.PRIORIDADES, PPR_EX[0], a, cores=PRIO, larg=270, altura=12, gap=28,
                    f=font("sans", 20))
    a = appear(t, C("compart", 27.0))
    if a > 0:
        pygame.draw.lines(s, mix(INK, RED, a), False, [(1826, TOP + 372), (1846, TOP + 372), (1846, TOP + 676),
                                                       (1826, TOP + 676)], 2)
        text(s, "as duas saídas leem o mesmo h", font("sans-sb", 24), RED_SOFT, (1160, TOP + 704), alpha=a)


@scene("perda", 20.0, "passo 7 · a perda")
def s_perda(s, t):
    titulo(s, t, "// passo 7", "A perda: entropia cruzada")
    code(s, t, *faixa(7), [(0, None), (C("log", 1.5), ("def perda", "perda_pr =")),
                           (C("soma", 15.0), ("return perda_eq", "return perda_eq"))])
    r = pygame.Rect(1160, TOP, 660, 520)
    a = appear(t, C("log", 1.5))
    painel(s, r, "perda = −ln(p da resposta certa)", a)
    gx, gy, gw, gh = r.x + 70, r.y + 80, r.w - 110, r.h - 150

    def pt(p, v):
        return (gx + p * gw, gy + gh - min(v, 4.6) / 4.6 * gh)

    if a > 0:
        pygame.draw.line(s, mix(INK, MUTE, a), (gx, gy + gh), (gx + gw, gy + gh), 1)
        pygame.draw.line(s, mix(INK, MUTE, a), (gx, gy), (gx, gy + gh), 1)
        ps = np.linspace(0.01, 1, 120)
        k = ease((t - C("log", 1.5) - 0.3) / 1.5)
        pts = [pt(p, -np.log(p)) for p in ps[:max(2, int(len(ps) * k))]]
        pygame.draw.lines(s, mix(INK, RED, a), False, pts, 3)
        text(s, "p", font("mono", 18), MUTE, (gx + gw, gy + gh + 12), "midtop", a)
        text(s, "0", font("mono", 16), MUTE, (gx, gy + gh + 12), "midtop", a)
        text(s, "1", font("mono", 16), MUTE, (gx + gw, gy + gh + 30), "midtop", a)
    for j, (ts, p, txt) in enumerate(((C("p90", 6.0), 0.9, "certo e confiante"),
                                      (C("p10", 9.5), 0.1, "errado e confiante"))):
        aa = appear(t, ts)
        if aa > 0:
            x, y = pt(p, -np.log(p))
            pygame.draw.circle(s, mix(INK, FG if j == 0 else RED_SOFT, aa), (int(x), int(y)), 9)
            yy = gy + 10 + j * 70
            pygame.draw.circle(s, mix(INK, FG if j == 0 else RED_SOFT, aa), (gx + gw - 330, yy + 14), 7)
            text(s, f"p = {p:.1f}  →  perda {-np.log(p):.2f}", font("mono-md", 21), FG, (gx + gw - 312, yy), alpha=aa)
            text(s, txt, font("sans", 19), MUTE, (gx + gw - 312, yy + 30), alpha=aa)
    a = appear(t, C("soma", 15.0))
    text(s, "perda total =", font("sans-sb", 26), FG, (1160, 800), alpha=a)
    text(s, "−ln p(equipe certa) − ln p(prioridade certa)", font("mono", 22), RED_SOFT, (1160, 844), alpha=a)
    text(s, "média no lote", font("sans", 21), MUTE, (1160, 884), alpha=a)


# backprop: um exemplo passando pela rede ainda sem treino
_rng_bp = np.random.default_rng(3)
_mask = (_rng_bp.random((1, 32)) > 0.5) / 0.5
BP_Z1, BP_H, BP_PE, BP_PP = T.forward(REDE0, X_EX, _mask)
_y_ex = TEXTOS.index(EX) if EX in TEXTOS else None
BP_YE = int(Y_EQ[_y_ex]) if _y_ex is not None else 0
BP_YP = int(Y_PR[_y_ex]) if _y_ex is not None else 1
BP_D = BP_PE[0].copy()
BP_D[BP_YE] -= 1
_dpr = BP_PP[0].copy()
_dpr[BP_YP] -= 1
BP_DH = (BP_D @ REDE0["We"].T + _dpr @ REDE0["Wp"].T) * _mask[0] * (BP_Z1[0] > 0)


@scene("backprop", 45.0, "passo 8 · backprop")
def s_backprop(s, t):
    titulo(s, t, "// passo 8", "Backprop: de trás para frente")
    code(s, t, *faixa(8), [(0, None), (C("dsaida", 3.0), ("# saídas:", "d_eq, d_pr = d_eq / n")),
                           (C("gsaida", 9.0), ('g = {"We"', '"Wp": h.T')), (C("dh", 13.0), ("# oculta:", "d_h = ")),
                           (C("mascara", 20.0), ("mascara = (rng", "z1, h, p_eq")),
                           (C("gw1", 27.0), ('g["W1"]', 'g["W1"]')), (C("esparso", 31.0), ('g["W1"]', 'g["W1"]'))])
    rotulo(s, "UM CHAMADO NA REDE AINDA SEM TREINO", (1160, TOP), appear(t, 0.3))
    a = appear(t, C("dsaida", 3.0))
    if a > 0:
        text(s, "d = p − y", font("mono-md", 24), FG, (1160, TOP + 34), alpha=a)
        for i, e in enumerate(T.EQUIPES):
            y = TOP + 78 + i * 34
            text(s, e[:5], font("mono", 17), FG if i == BP_YE else MUTE, (1160, y))
            text(s, f"p {BP_PE[0, i]:.2f}", font("mono", 17), BODY, (1250, y), alpha=a)
            text(s, f"y {1 if i == BP_YE else 0}", font("mono", 17), RED_SOFT if i == BP_YE else MUTE, (1350, y), alpha=a)
            d = BP_D[i]
            meio = 1600
            wbar = int(abs(d) * 200)
            cor = RED if d < 0 else (110, 110, 120)
            pygame.draw.rect(s, mix(INK, cor, a), (meio - wbar if d < 0 else meio, y + 3, wbar, 14), border_radius=3)
            text(s, f"{d:+.2f}", font("mono", 17), FG, (1820, y), "topright", a)
        pygame.draw.line(s, mix(INK, MUTE, a), (1600, TOP + 72), (1600, TOP + 212), 1)
    a = appear(t, C("gsaida", 9.0))
    text(s, 'g["We"] = h.T @ d_eq     g["be"] = d_eq.sum(0)', font("mono", 21), FG, (1160, TOP + 238), alpha=a)
    a = appear(t, C("dh", 13.0))
    if a > 0:
        text(s, "d_h = (d_eq @ We.T + d_pr @ Wp.T) * ReLU' * máscara", font("mono", 19), FG, (1160, TOP + 296), alpha=a)
        off = [i for i in range(32) if BP_Z1[0, i] <= 0 or _mask[0, i] == 0]
        barras_verticais(s, (1160, TOP + 330, 660, 130), BP_DH, a, cortes=off if t > C("mascara", 20.0) else ())
        am = appear(t, C("mascara", 20.0))
        text(s, f"{len(off)} de 32 neurônios zerados (ReLU desligada ou dropout)", font("sans", 19), MUTE,
             (1160, TOP + 468), alpha=am)
    a = appear(t, C("gw1", 27.0))
    if a > 0:
        text(s, 'g["W1"] = X.T @ d_h', font("mono-md", 24), FG, (1160, TOP + 530), alpha=a)
        ae = appear(t, C("esparso", 31.0))
        tira = pygame.Rect(1160, TOP + 580, 660, 44)
        rrect(s, CARD_2, tira, 6)
        ativos = np.nonzero(X_EX[0])[0]
        for i in ativos:
            xx = tira.x + int(i / V * tira.w)
            pygame.draw.line(s, mix(CARD_2, RED, ae), (xx, tira.y + 4), (xx, tira.bottom - 4), 2)
        rotulo(s, f"as {fmt(V)} linhas de W1", (1160, tira.bottom + 10), a)
        text(s, f"só {len(ativos)} recebem gradiente: os termos do chamado", font("sans-sb", 24), RED_SOFT,
             (1160, tira.bottom + 44), alpha=ae)


@scene("adam", 36.0, "passo 9 · treino com Adam")
def s_adam(s, t):
    titulo(s, t, "// passo 9", "Treino com Adam")
    code(s, t, *faixa(9), [(0, None), (C("lote", 1.5), ("for epoca", "g = gradientes")),
                           (C("l2", 7.0), ("if k.startswith", "g[k] += l2")),
                           (C("mv", 12.0), ("# Adam:", "v[k] = 0.999")),
                           (C("hat", 20.0), ("m_hat =", "rede[k] -=")),
                           (C("curva", 26.0), ("if (epoca + 1)", 'print(f"época'))], w=1080)
    xr = 1220
    notas = [(C("lote", 1.5), "lotes de 32", "embaralha a cada época"),
             (C("l2", 7.0), "L2", "segura os pesos perto de zero"),
             (C("mv", 12.0), "m e v", "direção e tamanho do passo"),
             (C("hat", 20.0), "correção", "compensa o começo zerado")]
    k_curva = appear(t, C("curva", 26.0))
    for i, (ts, tt, dd) in enumerate(notas):
        a = appear(t, ts) * (1 - 0.65 * k_curva)
        y = TOP + i * 70
        text(s, tt, font("sans-sb", 26), FG, (xr, y), alpha=a)
        text(s, dd, font("sans", 20), MUTE, (xr, y + 34), alpha=a)
    if k_curva > 0:
        r = pygame.Rect(xr, TOP + 300, 600, 440)
        painel(s, r, "perda por época", k_curva)
        gx, gy, gw, gh = r.x + 50, r.y + 70, r.w - 80, r.h - 120
        perdas = np.array([h[0] for h in HIST])
        n = max(2, int(len(perdas) * min(1, (t - C("curva", 26.0)) / 5.0)))
        pmax = perdas.max()
        pts = [(gx + i / (len(perdas) - 1) * gw, gy + gh - perdas[i] / pmax * gh) for i in range(n)]
        pygame.draw.line(s, mix(INK, MUTE, k_curva), (gx, gy + gh), (gx + gw, gy + gh), 1)
        pygame.draw.lines(s, RED, False, pts, 3)
        text(s, f"{perdas[n - 1]:.3f}", font("mono-md", 22), FG, (pts[-1][0], pts[-1][1] - 14), "midbottom")
        text(s, f"época {n}", font("mono", 18), MUTE, (gx + gw, gy + gh + 14), "topright", k_curva)


@scene("teste", 26.0, "passo 10 · testar")
def s_teste(s, t):
    titulo(s, t, "// passo 10", "Testar de verdade")
    code(s, t, *faixa(10), [(0, None), (C("split", 1.5), ("ordem = np.random", "tr, te =")),
                            (C("fit", 5.0), ("tfidf = Tfidf().fit", "X_te =")),
                            (C("acc", 11.0), ("rede = criar_rede", 'f"  prioridade')),
                            (C("exemplo", 19.0), ("def classificar", "return EQUIPES")),
                            (C("exemplo", 19.0) + 1.5, ('exemplo = "o motor', "print(classificar"))])
    r = pygame.Rect(1160, TOP, 660, 520)
    a = appear(t, C("acc", 11.0))
    painel(s, r, "terminal", a)
    if a > 0:
        text(s, "$ python triagem_do_zero.py", font("mono", 19), RED_SOFT, (r.x + 24, r.y + 66), alpha=a)
        for i, ln in enumerate(TERMINAL):
            aa = appear(t, C("acc", 11.0) + 0.3 + i * 0.25, 0.2)
            destaque = i >= len(TERMINAL) - 2
            text(s, ln, font("mono-md" if destaque else "mono", 19), FG if destaque else BODY,
                 (r.x + 24, r.y + 104 + i * 32), alpha=aa)
    a = appear(t, C("split", 1.5)) * (1 - a)
    if a > 0:
        rotulo(s, "SEPARAÇÃO", (1160, TOP), a)
        wtr = int(620 * len(TR) / len(TEXTOS))
        rrect(s, RED, (1160, TOP + 40, wtr, 56), 8)
        rrect(s, (95, 95, 105), (1160 + wtr + 8, TOP + 40, 620 - wtr - 8, 56), 8)
        text(s, f"treino · {len(TR)}", font("mono-md", 20), (255, 255, 255), (1180, TOP + 68), "midleft", a)
        text(s, f"teste · {len(TE)}", font("mono-md", 18), FG, (1160 + wtr + 20, TOP + 68), "midleft", a)
        af = appear(t, C("fit", 5.0))
        text(s, "o TF-IDF aprende o vocabulário só no treino", font("sans-sb", 26), FG, (1160, TOP + 140), alpha=af)
        text(s, "olhar o teste antes = cola", font("sans", 22), RED_SOFT, (1160, TOP + 180), alpha=af)
    a = appear(t, C("exemplo", 19.0))
    if a > 0:
        rotulo(s, "O CHAMADO DO COMEÇO", (1160, 790), a)
        text(s, HOOK_TXT, font("sans", 24), BODY, (1160, 822), alpha=a)
        text(s, f"→ {HOOK[0]}", font("sans-b", 34), FG, (1160, 862), alpha=a)


@scene("honesto", 17.0, "resultado honesto")
def s_honesto(s, t):
    titulo(s, t, "// sendo honesto", "O que esse número quer dizer")
    itens = [
        (0.4, "ESTE CORTE", f"equipe {ACC_EQ:.0%}  ·  prioridade {ACC_PR:.0%}", f"{len(TE)} chamados de teste: teve sorte"),
        (C("cv", 4.0), "VALIDAÇÃO CRUZADA", "equipe ≈ 92%  ·  prioridade ≈ 68%", "5 partes, todos os chamados avaliados"),
        (C("prio", 7.0), "PRIORIDADE", "o ponto fraco", "alta ou média? até pessoas discordam"),
        (C("mais", 11.0), "O QUE MAIS AJUDOU", "mais exemplos", "316 → 561 chamados: equipe de 84% para 92%"),
    ]
    for i, (ts, b, tt, dd) in enumerate(itens):
        a = appear(t, ts)
        y = 270 + i * 170
        if a <= 0:
            continue
        r = (100, y + int((1 - a) * 14), 1720, 146)
        rrect(s, CARD, r, 14)
        rrect(s, LINE_A, r, 14, 1)
        badge(s, b, (140, r[1] + 73), 20, "midleft", a)
        text(s, tt, font("sans-sb", 38), FG, (640, r[1] + 30), alpha=a)
        text(s, dd, font("sans", 25), MUTE, (640, r[1] + 84), alpha=a)


@scene("rodar", 9.0, "como rodar")
def s_rodar(s, t):
    titulo(s, t, "// sua vez", "Como rodar")
    cmds = [("$ ", "pip install numpy", ""),
            ("$ ", "python triagem_do_zero.py", "# com o chamados.csv na mesma pasta")]
    for i, (p, c, cm) in enumerate(cmds):
        a = appear(t, 0.4 + i * 0.8)
        y = 330 + i * 96
        text(s, p, font("mono-sb", 36), RED, (140, y), alpha=a)
        wd = text(s, c, font("mono", 36), FG, (190, y), alpha=a).right
        if cm:
            text(s, cm, font("mono", 26), MUTE, (wd + 40, y + 8), alpha=a)
    text(s, "código completo e o CSV com os exemplos: link na descrição", font("sans", 30), BODY, (140, 620),
         alpha=appear(t, 2.2))


@scene("outro", 8.0)
def s_outro(s, t):
    a = appear(t, 0.1, 0.6)
    text(s, "a sua imaginação é o limite.", font("sans", 36), BODY, (W // 2, 360), "center", a)
    r = pygame.Rect(0, 0, 560, 120)
    r.center = (W // 2, 520)
    b = appear(t, 0.8, 0.5)
    rrect(s, RED, r.inflate(int(-40 * (1 - b)), int(-20 * (1 - b))), 18)
    text(s, "INSCREVA-SE", font("sans-b", 54), (255, 255, 255), r.center, "center", b)
    text(s, "toda semana, tech direto ao ponto", font("mono", 26), MUTE, (W // 2, 640), "center", appear(t, 1.3))
    text(s, "@elucas.dev", font("mono-sb", 40), FG, (W // 2, 740), "center", appear(t, 1.8))


# ---------------- render ----------------
FADE = 0.35


def compose(sc, t):
    frame = BACKDROP.copy()
    content = pygame.Surface((W, H), pygame.SRCALPHA)
    _CUR["cues"] = sc["cues"]
    _CUR["dur"] = sc["dur"]
    sc["fn"](content, t)
    k = min(1.0, t / FADE, (sc["dur"] - t) / FADE)
    if k < 1:
        content.set_alpha(int(255 * max(0, k)))
    frame.blit(content, (0, 0))
    chrome(frame, sc["chapter"])
    return frame


def main():
    out_dir = os.path.join(HERE, "out")
    os.makedirs(out_dir, exist_ok=True)
    if "--lista" in sys.argv:
        t0 = 0.0
        for sc in SCENES:
            m, s_ = divmod(t0, 60)
            print(f"{int(m)}:{int(s_):02d}  {sc['name']:<10} {sc['dur']:5.1f}s  {sc['chapter'] or ''}")
            t0 += sc["dur"]
        print(f"total {t0 / 60:.1f} min")
        return
    if "--still" in sys.argv:
        i = sys.argv.index("--still")
        name, t = sys.argv[i + 1], float(sys.argv[i + 2])
        sc = next(x for x in SCENES if x["name"] == name)
        path = os.path.join(out_dir, f"still_{name}_{t:g}.png")
        pygame.image.save(compose(sc, t), path)
        print("ok", path)
        return
    total = sum(x["dur"] for x in SCENES)
    print(f"duração {total:.1f}s", flush=True)
    out = os.path.join(out_dir, "video_silent.mp4")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                          "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    n = 0
    for sc in SCENES:
        for k in range(int(round(sc["dur"] * FPS))):
            p.stdin.write(pygame.image.tobytes(compose(sc, k / FPS), "RGB"))
            n += 1
        print(f"  {sc['name']:<10} ok ({n} frames)", flush=True)
    p.stdin.close()
    p.wait()
    print("OK", out)


if __name__ == "__main__":
    main()
