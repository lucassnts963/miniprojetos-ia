"""Vídeo YouTube (1920x1080): "Nem tudo precisa de IA", a menor rota pelas capitais.

O código mostrado é o de ../../tutorial/rota_do_zero.py. Tudo o que aparece (rotas, tempos, as doze
rodadas do genético, as rodadas do método exato) é calculado rodando esse código; nada é desenhado à mão.

uso (venv com numpy, scipy, pygame e pygments: ferramentas/venv-video):
  python render.py                  -> out/video_silent.mp4
  python render.py --still cena t   -> out/still_<cena>_<t>.png
  python render.py --lista          -> cenas e durações
"""
import csv
import itertools
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEO = os.path.dirname(HERE)
PROJ = os.path.dirname(VIDEO)
RAIZ = os.path.dirname(PROJ)
TUT = os.path.join(PROJ, "tutorial")
for p in (os.path.join(RAIZ, "ferramentas", "youtube"), TUT, VIDEO, PROJ):
    sys.path.insert(0, p)
from tema import (BODY, CARD, CARD_2, FG, H, INK, LINE_A, LINE_ON_CARD, MUTE, RED, RED_SOFT, TINT_A, W,  # noqa: E402
                  appear, badge, barra_h, card, chip, ease, eyebrow, font, mix, rrect, text, titulo)
from video import BOTTOM, TOP, Video  # noqa: E402
import pygame  # noqa: E402
import rota_do_zero as T  # noqa: E402
from scipy.optimize import Bounds, LinearConstraint, milp  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
v = Video(HERE, fonte=os.path.join(TUT, "rota_do_zero.py"), selo="OTIMIZAÇÃO · PYTHON")
CINZA = (150, 150, 162)


def fmt(n, d=0):
    return f"{n:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ================= dados: roda o tutorial =================
NOMES, _lat, _lon = T.carregar(os.path.join(TUT, "capitais.csv"))
LAT, LON = np.degrees(_lat), np.degrees(_lon)
D = T.matriz_km(_lat, _lon)
INI = NOMES.index("Belém")
N = len(NOMES)
with open(os.path.join(PROJ, "dados", "cidades.csv"), encoding="utf-8") as f:
    _c = list(csv.DictReader(f))
BR_LAT = np.array([float(r["lat"]) for r in _c if r["ilha"] == "0"])
BR_LON = np.array([float(r["lon"]) for r in _c if r["ilha"] == "0"])

ROTA_NN = T.vizinho_mais_proximo(D, INI)


def passos_dois_opt(rota):
    """Mesmo laço do T.dois_opt, guardando cada melhoria (rota, i, j)."""
    rota, fotos = rota[:], []
    melhorou = True
    while melhorou:
        melhorou = False
        for i in range(1, len(rota) - 1):
            for j in range(i + 1, len(rota)):
                nova = rota[:i] + rota[i:j + 1][::-1] + rota[j + 1:]
                if T.comprimento(nova, D) < T.comprimento(rota, D) - 1e-9:
                    rota, melhorou = nova, True
                    fotos.append((rota[:], i, j))
    return fotos


FOTOS_2OPT = passos_dois_opt(ROTA_NN)
ROTA_2OPT = T.dois_opt(ROTA_NN, D)
assert FOTOS_2OPT[-1][0] == ROTA_2OPT


def genetico_com_historico(seed=0, geracoes=600, populacao=150):
    """Mesmo laço do T.genetico (mesma sequência aleatória), guardando a melhor rota de cada geração."""
    rng = np.random.default_rng(seed)
    outras = [c for c in range(N) if c != INI]
    pop = [[INI] + [int(c) for c in rng.permutation(outras)] for _ in range(populacao)]
    hist = []
    for _ in range(geracoes):
        pop.sort(key=lambda r: T.comprimento(r, D))
        hist.append((pop[0][:], float(T.comprimento(pop[0], D))))
        nova = pop[:populacao // 10]
        while len(nova) < populacao:
            pai = pop[min(rng.integers(0, populacao, 4))]
            mae = pop[min(rng.integers(0, populacao, 4))]
            nova.append(T.mutar(T.crossover_ox(pai, mae, rng), rng))
        pop = nova
    return min(pop, key=lambda r: T.comprimento(r, D)), hist


def rodadas_do_exato():
    """Mesmo laço do T.exato, guardando as ligações e os circuitos de cada rodada."""
    n = N + 1
    F = np.zeros((n, n))
    F[:-1, :-1] = D
    arestas = list(itertools.combinations(range(n), 2))
    custo = [F[i, j] for i, j in arestas]
    grau = np.zeros((n, len(arestas)))
    for k, (i, j) in enumerate(arestas):
        grau[i, k] = grau[j, k] = 1
    regras = [LinearConstraint(grau, 2, 2)]
    minimo = np.zeros(len(arestas))
    minimo[arestas.index((INI, n - 1))] = 1
    rodadas = []
    while True:
        r = milp(custo, constraints=regras, bounds=Bounds(minimo, 1), integrality=np.ones(len(arestas)))
        usadas = [arestas[k] for k in np.flatnonzero(r.x > 0.5)]
        grupos, _ = T.circuitos(usadas, n)
        rodadas.append(dict(usadas=[(i, j) for i, j in usadas if n - 1 not in (i, j)], km=float(r.fun),
                            grupos=[sorted(g - {n - 1}) for g in grupos]))
        if len(grupos) == 1:
            return rodadas
        for g in grupos:
            regras.append(LinearConstraint([float(i in g and j in g) for i, j in arestas], -np.inf, len(g) - 1))


def cronometrar(fn, repeticoes=1):
    t0 = time.perf_counter()
    for _ in range(repeticoes):
        r = fn()
    return r, (time.perf_counter() - t0) / repeticoes


CACHE = os.path.join(HERE, "cache_render.json")
if os.path.exists(CACHE):
    with open(CACHE, encoding="utf-8") as f:
        K = json.load(f)
else:
    print("medindo (uma vez, fica em cache_render.json)...", flush=True)
    K = {}
    _, K["t_nn"] = cronometrar(lambda: T.vizinho_mais_proximo(D, INI), 50)
    _, K["t_2opt"] = cronometrar(lambda: T.dois_opt(ROTA_NN, D), 5)
    _, K["t_ga"] = cronometrar(lambda: T.genetico(D, INI))
    otima, K["t_exato"] = cronometrar(lambda: T.exato(D, INI), 5)
    K["otima"] = [int(c) for c in otima]
    K["doze"] = [float(T.comprimento(T.genetico(D, INI, seed=s), D)) for s in range(12)]
    perto = [int(c) for c in np.argsort(D[INI])[:9]]
    sub = D[np.ix_(perto, perto)]
    melhor9, dt = cronometrar(lambda: T.forca_bruta(sub, 0, range(1, 9)))
    K["bruta_por_s"] = math.factorial(8) / dt
    K["perto9"] = perto
    K["melhor9"] = [perto[c] for c in melhor9]
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(K, f)

ROTA_GA, HIST_GA = genetico_com_historico()
RODADAS = rodadas_do_exato()
OTIMA = K["otima"]
KM_NN, KM_2OPT, KM_GA, KM_OTIMA = (float(T.comprimento(r, D)) for r in (ROTA_NN, ROTA_2OPT, ROTA_GA, OTIMA))
assert abs(KM_GA - K["doze"][0]) < 1e-6, "o genético reproduzido aqui tem que bater com o do tutorial"
DOZE = np.array(K["doze"])
N_OTIMO = int((DOZE < KM_OTIMA + 1).sum())
POR_S = 200_000  # ordens por segundo na força bruta (medido: ~200 mil nesta máquina)

# Brasil inteiro: rota em linha reta (rota.py) e comparação com a estrada (cenas_mapa.py)
with open(os.path.join(PROJ, "rota_belem.csv"), encoding="utf-8") as f:
    _r = list(csv.DictReader(f))
BRASIL_LAT = np.array([float(x["lat"]) for x in _r])
BRASIL_LON = np.array([float(x["lon"]) for x in _r])
KM_BRASIL = float(_r[-1]["km_acumulado"])
_m = np.load(os.path.join(VIDEO, "cache_mapa.npz"))
E_LAT, E_LON, PLANO_RETA, PLANO_EST = _m["lat"], _m["lon"], _m["reta"], _m["est"]
KM_RE, KM_EE = float(_m["km_re"]), float(_m["km_ee"])
_la, _lo = np.radians(E_LAT[PLANO_RETA]), np.radians(E_LON[PLANO_RETA])
_a = np.sin(np.diff(_la) / 2) ** 2 + np.cos(_la[:-1]) * np.cos(_la[1:]) * np.sin(np.diff(_lo) / 2) ** 2
KM_MAPA = float((2 * 6371 * np.arcsin(np.sqrt(_a))).sum())

print(f"NN {KM_NN:,.0f} · 2-opt {KM_2OPT:,.0f} · GA {KM_GA:,.0f} · ótimo {KM_OTIMA:,.0f} km | "
      f"tempos {K['t_nn']:.4f} {K['t_2opt']:.3f} {K['t_ga']:.2f} {K['t_exato']:.3f} s | "
      f"genético: ótimo em {N_OTIMO}/12, pior +{DOZE.max() / KM_OTIMA - 1:.1%} | "
      f"exato: {[len(r['grupos']) for r in RODADAS]} circuitos, {[round(r['km']) for r in RODADAS]} km | "
      f"estrada: mapa {KM_MAPA:,.0f}, reta na estrada {KM_RE:,.0f}, pela estrada {KM_EE:,.0f} "
      f"(+{KM_EE / KM_MAPA - 1:.0%}, economia {1 - KM_EE / KM_RE:.0%})", flush=True)


# ================= mapa =================
def projetar(lat, lon, rect, pad=30):
    k = math.cos(math.radians(-15))
    lo0, lo1, la0, la1 = -74.5, -34.5, -34.0, 5.5
    esc = min((rect.w - 2 * pad) / ((lo1 - lo0) * k), (rect.h - 2 * pad) / (la1 - la0))
    ox = rect.x + (rect.w - (lo1 - lo0) * k * esc) / 2
    oy = rect.y + (rect.h - (la1 - la0) * esc) / 2
    return np.column_stack([ox + (np.asarray(lon) - lo0) * k * esc, oy + (la1 - np.asarray(lat)) * esc])


_bases = {}


def mapa(s, rect, capitais=True, alpha=1.0, com_card=True):
    """Card com a silhueta do Brasil (todos os municípios) e, por cima, as capitais. Devolve os pontos."""
    chave = (tuple(rect), com_card)
    if chave not in _bases:
        surf = pygame.Surface((W, H), pygame.SRCALPHA)
        if com_card:
            rrect(surf, CARD, rect, 16)
            rrect(surf, LINE_A, rect, 16, 1)
        cor = (*mix(CARD, FG, 0.16), 255)
        for x, y in projetar(BR_LAT, BR_LON, rect):
            surf.set_at((int(x), int(y)), cor)
        _bases[chave] = (surf, projetar(LAT, LON, rect))
    surf, P = _bases[chave]
    if alpha < 1:
        surf = surf.copy()
        surf.set_alpha(int(255 * alpha))
    s.blit(surf, (0, 0))
    if capitais:
        for x, y in P:
            pygame.draw.circle(s, mix(INK, FG, alpha), (int(x), int(y)), 4)
        x0, y0 = P[INI]
        pygame.draw.circle(s, mix(INK, RED_SOFT, alpha), (int(x0), int(y0)), 11, 3)
    return P


def rota(s, P, ordem, cor, larg=3, frac=1.0, alpha=255):
    n = int(len(ordem) * frac)
    if n < 2:
        return
    tmp = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.lines(tmp, (*cor, alpha), False, [tuple(P[c]) for c in ordem[:n]], larg)
    s.blit(tmp, (0, 0))


def numero(s, txt, sub, pos, alpha=1.0, cor=FG, tam=44):
    r = text(s, txt, font("mono-sb", tam), cor, pos, alpha=alpha)
    text(s, sub, font("sans", 22), MUTE, (pos[0], r.bottom + 4), alpha=alpha)


DIR = pygame.Rect(1160, TOP, 660, BOTTOM - TOP)   # painel da direita, ao lado do código


# ================= CENAS =================
@v.cena("hook", 14.0)
def s_hook(s, t):
    r = pygame.Rect(100, 170, 980, 820)
    P = mapa(s, r)
    rng = np.random.default_rng(int(t * 3))
    if t < v.C("ia", 6.0):
        emb = [INI] + [int(c) for c in rng.permutation([c for c in range(N) if c != INI])]
        rota(s, P, emb, CINZA, 2, alpha=150)
    else:
        rota(s, P, ROTA_GA, CINZA, 3, alpha=int(255 * (1 if t < v.C("perdeu", 10.0) else 0.35)))
    a = appear(t, v.C("perdeu", 10.0), 0.9)
    if a > 0:
        rota(s, P, OTIMA, RED, 5, frac=a)
    text(s, "Belém", font("sans-sb", 22), FG, (P[INI][0] + 18, P[INI][1] - 26))
    x = 1150
    eyebrow(s, "// 27 capitais, saindo de Belém", (x, 300), appear(t, 0.3))
    text(s, "Qual é a menor rota?", font("sans-b", 62), FG, (x, 340), alpha=appear(t, 0.5))
    a = appear(t, v.C("ia", 6.0))
    chip(s, "IA · algoritmo genético", (x, 470), font("mono-md", 24), FG, CARD_2, LINE_A, a)
    text(s, f"{fmt(KM_GA)} km", font("mono-sb", 40), CINZA, (x, 530), alpha=a)
    a = appear(t, v.C("perdeu", 10.0) + 0.6)
    chip(s, "método de 1954", (x, 640), font("mono-md", 24), RED_SOFT, (60, 24, 28), (229, 72, 77, 160), a)
    text(s, f"{fmt(KM_OTIMA)} km", font("mono-sb", 40), RED_SOFT, (x, 700), alpha=a)
    text(s, "a menor possível, com prova", font("sans", 28), BODY, (x, 760), alpha=a)


@v.cena("titulo", 4.0)
def s_titulo(s, t):
    eyebrow(s, "// caixeiro-viajante em python", (W // 2, 330), appear(t, 0), "midtop")
    text(s, "Nem tudo precisa de IA", font("sans-b", 92), FG, (W // 2, 380), "midtop", appear(t, 0.15))
    text(s, "cinco jeitos de achar a menor rota, e o que cada um garante", font("sans", 36), BODY, (W // 2, 520),
         "midtop", appear(t, 0.5))


LINHAS_EXPLOSAO = [(9, "40.320", "0,2 s"), (12, "39,9 milhões", "3 minutos"), (15, "87 bilhões", "5 dias"),
                   (20, "1,2 × 10¹⁷", "19 mil anos"), (27, "4 × 10²⁶", "64 trilhões de anos")]


@v.cena("problema", 19.0, "o problema")
def s_problema(s, t):
    titulo(s, t, "// o problema", "Testar todas as ordens?")
    r = pygame.Rect(100, TOP, 800, BOTTOM - TOP)
    P = mapa(s, r)
    rng = np.random.default_rng(int(t * 7))
    emb = [INI] + [int(c) for c in rng.permutation([c for c in range(N) if c != INI])]
    rota(s, P, emb, CINZA, 2, alpha=170)
    x, y0 = 980, TOP + 10
    a = appear(t, v.C("explode", 6.0))
    for j, (cab, xx) in enumerate((("cidades", x), ("ordens possíveis", x + 170), ("tempo testando todas", x + 500))):
        text(s, cab.upper(), font("mono-md", 17), MUTE, (xx, y0), alpha=a)
    for i, (n, ordens, tempo) in enumerate(LINHAS_EXPLOSAO):
        aa = appear(t, v.C("explode", 6.0) + 0.3 + i * 0.7)
        y = y0 + 50 + i * 86
        ult = i == len(LINHAS_EXPLOSAO) - 1
        if ult and aa > 0:
            rrect(s, TINT_A, (x - 20, y - 12, 860, 74), 12)
        text(s, str(n), font("mono-sb", 40), RED_SOFT if ult else FG, (x, y), alpha=aa)
        text(s, ordens, font("mono", 34), FG, (x + 170, y + 4), alpha=aa)
        text(s, tempo, font("sans-sb", 32), RED_SOFT if ult else BODY, (x + 500, y + 6), alpha=aa)
    text(s, "a 200 mil ordens por segundo (medido)", font("sans", 22), MUTE, (x, y0 + 500), alpha=a)
    a = appear(t, v.C("universo", 13.0))
    text(s, "idade do universo: 14 bilhões de anos", font("sans-sb", 30), FG, (x, y0 + 560), alpha=a)
    text(s, "testar tudo levaria milhares de universos", font("sans", 26), BODY, (x, y0 + 604), alpha=a)


@v.cena("dados", 20.0, "passo 1 · os dados")
def s_dados(s, t):
    titulo(s, t, "// passo 1", "Os dados e a distância")
    v.codigo(s, t, *v.faixa(1), [(0, None), (v.C("csv", 1.5), ("def carregar", "return nomes")),
                                 (v.C("matriz", 6.0), ("def matriz_km", "return 2 * 6371")),
                                 (v.C("comp", 15.0), ("def comprimento", "return D[rota"))])
    a = appear(t, v.C("csv", 1.5))
    r = pygame.Rect(DIR.x, TOP, DIR.w, 270)
    if a > 0:
        tmp = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        card(tmp, (0, 0, r.w, r.h), "capitais.csv")
        tmp.set_alpha(int(255 * a))
        s.blit(tmp, r)
        linhas = open(os.path.join(TUT, "capitais.csv"), encoding="utf-8").read().split("\n")[:6]
        for i, ln in enumerate(linhas):
            text(s, ln, font("mono", 19), RED_SOFT if i == 0 else FG, (r.x + 24, r.y + 66 + i * 32),
                 alpha=appear(t, v.C("csv", 1.5) + 0.2 + i * 0.1))
    a = appear(t, v.C("matriz", 6.0))
    if a > 0:
        text(s, "D: distância entre todos os pares (km)", font("mono-md", 19), MUTE, (DIR.x, TOP + 296), alpha=a)
        cel = 13
        x0, y0 = DIR.x, TOP + 330
        dmax = D.max()
        k = ease((t - v.C("matriz", 6.0)) / 2.0)
        for i in range(int(N * k)):
            for j in range(N):
                pygame.draw.rect(s, mix(CARD, RED, D[i, j] / dmax), (x0 + j * cel, y0 + i * cel, cel - 1, cel - 1))
        text(s, "27 × 27", font("mono", 18), MUTE, (x0 + N * cel + 20, y0 + 6), alpha=a)
        text(s, "escuro = perto", font("sans", 20), MUTE, (x0 + N * cel + 20, y0 + 40), alpha=a)
        text(s, "vermelho = longe", font("sans", 20), RED_SOFT, (x0 + N * cel + 20, y0 + 70), alpha=a)
    a = appear(t, v.C("comp", 15.0))
    text(s, "comprimento = soma dos trechos da rota", font("sans-sb", 26), FG, (DIR.x, BOTTOM - 44), alpha=a)


@v.cena("bruta", 18.0, "passo 2 · força bruta")
def s_bruta(s, t):
    titulo(s, t, "// passo 2", "Força bruta")
    v.codigo(s, t, *v.faixa(2), [(0, None), (v.C("perm", 2.0), ("for ordem in", "melhor, melhor_km = rota")),
                                 (v.C("nove", 6.0), ("def forca_bruta", "return melhor"))])
    P = mapa(s, DIR)
    perto = K["perto9"]
    for c in perto:
        pygame.draw.circle(s, RED_SOFT, (int(P[c][0]), int(P[c][1])), 6)
    k = ease((t - v.C("nove", 6.0)) / 3.0)
    if t < v.C("nove", 6.0) + 3.0:
        rng = np.random.default_rng(int(t * 12))
        emb = [perto[0]] + [perto[int(i)] for i in rng.permutation(range(1, 9))]
        rota(s, P, emb, CINZA, 2, alpha=200)
    else:
        rota(s, P, K["melhor9"], RED, 4)
    a = appear(t, v.C("nove", 6.0))
    text(s, f"{fmt(int(40320 * k))} ordens testadas", font("mono-md", 24), FG, (DIR.x + 24, DIR.y + 22), alpha=a)
    text(s, "9 cidades: sai na hora", font("sans", 22), MUTE, (DIR.x + 24, DIR.y + 58), alpha=a)
    a = appear(t, v.C("cresce", 11.5))
    for i, (n, tempo) in enumerate(((15, "5 dias"), (20, "19 mil anos"), (27, "64 trilhões de anos"))):
        aa = appear(t, v.C("cresce", 11.5) + i * 0.5)
        text(s, f"{n} cidades", font("mono-md", 24), FG, (DIR.x + 24, DIR.bottom - 150 + i * 44), alpha=aa)
        text(s, tempo, font("sans-sb", 24), RED_SOFT, (DIR.x + 230, DIR.bottom - 150 + i * 44), alpha=aa)


@v.cena("vizinho", 22.0, "passo 3 · vizinho mais próximo")
def s_vizinho(s, t):
    titulo(s, t, "// passo 3", "Vizinho mais próximo")
    v.codigo(s, t, *v.faixa(3), [(0, None), (v.C("anda", 3.0), ("while livres", "livres.remove"))])
    P = mapa(s, DIR)
    k = ease((t - v.C("anda", 3.0)) / 6.0)
    n = max(1, int(1 + (N - 1) * k))
    rota(s, P, ROTA_NN[:n], CINZA, 3)
    a = appear(t, v.C("saltos", 11.0))
    if a > 0:
        # os três trechos mais longos da rota: ficaram para o final
        trechos = sorted(range(N - 1), key=lambda i: -D[ROTA_NN[i], ROTA_NN[i + 1]])[:3]
        tmp = pygame.Surface((W, H), pygame.SRCALPHA)
        for i in trechos:
            pygame.draw.line(tmp, (*RED, int(255 * a)), tuple(P[ROTA_NN[i]]), tuple(P[ROTA_NN[i + 1]]), 6)
        s.blit(tmp, (0, 0))
        text(s, "saltos longos no final", font("sans-sb", 24), RED_SOFT, (DIR.x + 24, DIR.bottom - 100), alpha=a)
    a = appear(t, v.C("km", 17.0))
    numero(s, f"{fmt(KM_NN)} km", "instantâneo, mas longe do melhor", (DIR.x + 24, DIR.y + 22), a, tam=40)


@v.cena("doisopt", 21.0, "passo 4 · 2-opt")
def s_doisopt(s, t):
    titulo(s, t, "// passo 4", "2-opt: descruzar a rota")
    v.codigo(s, t, *v.faixa(4), [(0, None), (v.C("cruza", 2.5), ("# inverte o trecho", "nova = rota[:i]")),
                                 (v.C("testa", 9.0), ("for i in range", "rota, melhorou = nova, True"))])
    P = mapa(s, DIR)
    t0 = v.C("testa", 9.0)
    k = ease((t - t0) / 5.0)
    idx = int(k * len(FOTOS_2OPT))
    if idx == 0:
        atual = ROTA_NN
        prox, i, j = FOTOS_2OPT[0]
        rota(s, P, atual, CINZA, 3)
        a = appear(t, v.C("cruza", 2.5))
        if a > 0:  # o primeiro trecho que vai ser invertido
            rota(s, P, atual[i - 1:j + 2], RED, 5, alpha=int(255 * a))
            text(s, "inverter este trecho encurta a rota", font("sans-sb", 24), RED_SOFT, (DIR.x + 24, DIR.bottom - 60),
                 alpha=a)
    else:
        atual, i, j = FOTOS_2OPT[idx - 1]
        rota(s, P, atual, CINZA, 3)
        rota(s, P, atual[i - 1:j + 2], RED, 5)
    km_ = T.comprimento(atual, D)
    numero(s, f"{fmt(km_)} km", f"{idx} de {len(FOTOS_2OPT)} inversões que melhoram", (DIR.x + 24, DIR.y + 22),
           appear(t, 1.0), tam=40)
    a = appear(t, v.C("km", 16.0))
    text(s, f"{K['t_2opt']:.2f} s".replace(".", ","), font("mono-sb", 30), RED_SOFT, (DIR.right - 24, DIR.y + 28),
         "topright", a)


OX_PAI = list("ABCDEFGHI")
OX_MAE = list("AEHCIBGDF")
OX_A, OX_B = 3, 5


@v.cena("genetico", 34.0, "passo 5 · algoritmo genético")
def s_genetico(s, t):
    titulo(s, t, "// passo 5", "Algoritmo genético: a IA da cobrinha")
    v.codigo(s, t, *v.faixa(5), [(0, None), (v.C("pop", 4.0), ("def genetico", "for _ in range(populacao)]")),
                                 (v.C("ox", 12.0), ("def crossover_ox", "return [pai[0]]")),
                                 (v.C("roda", 25.0), ("for _ in range(geracoes)", "pop = nova"))])
    t_ox, t_roda = v.C("ox", 12.0), v.C("roda", 25.0)
    k_roda = appear(t, t_roda)
    # cruzamento OX
    a = appear(t, t_ox) * (1 - k_roda)
    if a > 0:
        meio = OX_PAI[OX_A:OX_B + 1]
        resto = [c for c in OX_MAE[1:] if c not in meio]
        filho = [OX_PAI[0]] + resto[:OX_A - 1] + meio + resto[OX_A - 1:]
        kf = ease((t - v.C("filho", 17.0)) / 2.5)
        for li, (rot, seq) in enumerate((("pai", OX_PAI), ("mãe", OX_MAE), ("filho", filho))):
            y = DIR.y + 90 + li * 110
            text(s, rot, font("mono-md", 22), MUTE, (DIR.x, y + 14), alpha=a)
            for c, letra in enumerate(seq):
                x = DIR.x + 90 + c * 62
                do_pai = OX_A <= c <= OX_B
                if li == 0:
                    cor = RED if do_pai else CARD_2
                elif li == 1:
                    cor = CARD_2 if letra in meio else (70, 70, 80)
                else:
                    ordem_ap = [OX_A, OX_A + 1, OX_B] + [i for i in range(9) if not OX_A <= i <= OX_B]
                    if ordem_ap.index(c) / 9 > kf:
                        continue
                    cor = RED if do_pai else (70, 70, 80)
                rrect(s, (*cor, int(255 * a)), (x, y, 54, 54), 8)
                text(s, letra, font("mono-sb", 24), FG, (x + 27, y + 27), "center", a)
        text(s, "o filho copia um trecho do pai e completa na ordem da mãe", font("sans", 23), BODY,
             (DIR.x, DIR.y + 440), alpha=a)
        text(s, "nunca repete nem esquece cidade", font("sans-sb", 23), RED_SOFT, (DIR.x, DIR.y + 476), alpha=a)
    # evolução
    if k_roda > 0:
        P = mapa(s, DIR, alpha=k_roda)
        k = ease((t - t_roda) / 6.0)
        g = int(min(len(HIST_GA) - 1, (k ** 1.6) * (len(HIST_GA) - 1)))
        ordem, km_ = HIST_GA[g]
        rota(s, P, ordem, CINZA, 3, alpha=int(255 * k_roda))
        numero(s, f"{fmt(km_)} km", f"geração {g + 1} de {len(HIST_GA)}", (DIR.x + 24, DIR.y + 22), k_roda, tam=40)
        if k >= 1:
            text(s, f"{K['t_ga']:.1f} s".replace(".", ","), font("mono-sb", 30), CINZA, (DIR.right - 24, DIR.y + 28),
                 "topright", appear(t, t_roda + 6.0))


LIMITES = [("l1", "Não sabe quando chegou", "achou a melhor rota em {n} de 12 rodadas"),
           ("l2", "Cada rodada, uma resposta", "é aleatório: muda a semente, muda o resultado"),
           ("l3", "É lento, e piora com mais cidades", "segundos aqui; inviável para milhares"),
           ("l4", "Muitos botões para ajustar", "população, mutação, gerações, torneio…")]


@v.cena("limites", 34.0, "as limitações da IA aqui")
def s_limites(s, t):
    titulo(s, t, "// por que não IA", "As limitações do genético")
    # 12 rodadas: um ponto por rodada, na escala de km
    r = pygame.Rect(100, TOP, 800, 470)
    a = appear(t, v.C("doze", 4.0))
    card(s, r, "12 rodadas, só a semente muda")
    x0, x1 = r.x + 60, r.right - 60
    lo, hi = KM_OTIMA - 100, DOZE.max() + 100
    px = lambda km_: x0 + (km_ - lo) / (hi - lo) * (x1 - x0)  # noqa: E731
    ybase = r.y + 330
    pygame.draw.line(s, LINE_ON_CARD, (x0, ybase), (x1, ybase), 2)
    xo = px(KM_OTIMA)
    pygame.draw.line(s, RED, (xo, r.y + 90), (xo, ybase + 14), 2)
    text(s, "ótimo", font("mono-md", 18), RED_SOFT, (xo, r.y + 66), "midtop")
    text(s, f"{fmt(KM_OTIMA)} km", font("mono", 18), RED_SOFT, (xo, ybase + 22), "midtop")
    text(s, f"{fmt(DOZE.max())} km", font("mono", 18), MUTE, (px(DOZE.max()), ybase + 22), "midtop", a)
    pilha = {}
    for i, km_ in enumerate(sorted(DOZE)):
        aa = appear(t, v.C("doze", 4.0) + 0.3 + i * 0.25)
        if aa <= 0:
            continue
        chave = round(km_)
        pilha[chave] = pilha.get(chave, 0) + 1
        no_otimo = km_ < KM_OTIMA + 1
        pygame.draw.circle(s, mix(CARD, RED if no_otimo else CINZA, aa), (int(px(km_)), ybase - 24 - (pilha[chave] - 1) * 34), 13)
    text(s, f"ótimo em {N_OTIMO} de 12 · pior: {fmt((DOZE.max() / KM_OTIMA - 1) * 100, 1)}% acima", font("sans-sb", 26),
         FG, (r.x + 30, r.bottom - 60), alpha=appear(t, v.C("doze", 4.0) + 3.5))
    a = appear(t, v.C("prova", 28.0))
    text(s, "e nenhuma rodada prova que a rota é a menor", font("sans-b", 34), RED_SOFT, (100, r.bottom + 50), alpha=a)
    for i, (cue, tt, dd) in enumerate(LIMITES):
        aa = appear(t, v.C(cue, 2.0 + i * 6.0))
        if aa <= 0:
            continue
        y = TOP + i * 150 + int((1 - aa) * 14)
        rr = (960, y, 860, 128)
        rrect(s, CARD, rr, 14)
        rrect(s, LINE_A, rr, 14, 1)
        text(s, str(i + 1), font("mono-sb", 44), RED, (990, y + 34), alpha=aa)
        text(s, tt, font("sans-sb", 32), FG, (1060, y + 24), alpha=aa)
        text(s, dd.format(n=N_OTIMO), font("sans", 23), MUTE, (1060, y + 72), alpha=aa)


CORES_CIRCUITO = [(229, 72, 77), (240, 150, 60), (225, 200, 80), (120, 190, 140), (110, 160, 230), (190, 130, 220),
                  (236, 236, 239)]


@v.cena("exato", 46.0, "passo 6 · o ótimo, com prova")
def s_exato(s, t):
    titulo(s, t, "// passo 6", "A matemática: o ótimo, com prova")
    a_, b_ = v.L("def exato"), v.L("return rota", v.L("def exato"))
    v.codigo(s, t, a_, b_, [(0, None), (v.C("var", 2.5), ("arestas = list", "custo = [F[i, j]")),
                            (v.C("grau", 8.0), ("grau = np.zeros", "regras = [LinearConstraint")),
                            (v.C("r1", 13.0), ("r = milp(custo", "grupos, viz = circuitos")),
                            (v.C("proibe", 18.0), ("for g in grupos", "regras.append")),
                            (v.C("prova", 32.0), ("if len(grupos) == 1", "break"))])
    P = mapa(s, DIR)
    t1, t2 = v.C("r1", 13.0), v.C("r2", 22.0)
    tempos = [t1, t2, t2 + 1.3, t2 + 2.6]
    k_r = max([i for i, ti in enumerate(tempos) if t >= ti], default=-1)
    if k_r >= 0:
        rod = RODADAS[min(k_r, len(RODADAS) - 1)]
        a = appear(t, tempos[k_r], 0.4)
        grupo_de = {c: gi for gi, g in enumerate(rod["grupos"]) for c in g}
        um_so = len(rod["grupos"]) == 1
        tmp = pygame.Surface((W, H), pygame.SRCALPHA)
        for i, j in rod["usadas"]:
            cor = RED if um_so else CORES_CIRCUITO[grupo_de[i] % len(CORES_CIRCUITO)]
            pygame.draw.line(tmp, (*cor, int(255 * a)), tuple(P[i]), tuple(P[j]), 5 if um_so else 4)
        s.blit(tmp, (0, 0))
        n_c = len(rod["grupos"])
        text(s, f"rodada {k_r + 1}: {n_c} circuito{'s' if n_c > 1 else ''}", font("mono-md", 24),
             RED_SOFT if um_so else FG, (DIR.x + 24, DIR.y + 22))
    # o piso subindo
    a = appear(t, v.C("piso", 27.0))
    if a > 0:
        for i, rod in enumerate(RODADAS):
            if i > k_r:
                break
            y = DIR.bottom - 150 + i * 32
            larg = int(300 * (rod["km"] - 11500) / (KM_OTIMA - 11500))
            pygame.draw.rect(s, mix(CARD, RED if i == len(RODADAS) - 1 else CINZA, a), (DIR.x + 24, y, larg, 16),
                             border_radius=5)
            text(s, f"{fmt(rod['km'])} km", font("mono", 18), FG, (DIR.x + 24 + larg + 12, y - 3), alpha=a)
        text(s, "o custo só sobe: é um piso", font("sans", 22), MUTE, (DIR.x + 24, DIR.bottom - 186), alpha=a)
    a = appear(t, v.C("prova", 32.0))
    badge(s, "MENOR ROTA POSSÍVEL · COM PROVA", (DIR.x + 24, DIR.y + 62), 18, "topleft", a)
    a = appear(t, v.C("dfj", 38.0))
    text(s, "Dantzig, Fulkerson", font("sans-sb", 22), FG, (DIR.right - 24, DIR.bottom - 96), "topright", a)
    text(s, "e Johnson · 1954", font("sans-sb", 22), FG, (DIR.right - 24, DIR.bottom - 66), "topright", a)


def _tempo(seg):
    return f"{seg:.2f} s".replace(".", ",") if seg >= 0.01 else "< 0,01 s"


@v.cena("placar", 17.0, "o placar")
def s_placar(s, t):
    titulo(s, t, "// passo 7", "O placar")
    linhas = [("nn", "vizinho mais próximo", KM_NN, K["t_nn"], "nenhuma"),
              ("opt", "+ 2-opt", KM_2OPT, K["t_2opt"], "nenhuma"),
              ("ga", "algoritmo genético", KM_GA, K["t_ga"], "nenhuma"),
              ("ex", "exato", KM_OTIMA, K["t_exato"], "ótimo, com prova")]
    xs = (140, 760, 1120, 1420)
    for cab, x in zip(("método", "distância", "tempo", "garantia"), xs):
        text(s, cab.upper(), font("mono-md", 20), MUTE, (x, TOP + 6), alpha=appear(t, 0.4))
    for i, (cue, nome, km_, seg, gar) in enumerate(linhas):
        a = appear(t, v.C(cue, 2.0 + i * 3.5))
        if a <= 0:
            continue
        y = TOP + 60 + i * 150 + int((1 - a) * 14)
        melhor = cue == "ex"
        rr = (100, y, 1720, 124)
        rrect(s, CARD, rr, 14)
        rrect(s, (229, 72, 77, 150) if melhor else LINE_A, rr, 14, 2 if melhor else 1)
        cor = RED_SOFT if melhor else FG
        text(s, nome, font("sans-sb", 36), cor, (xs[0], y + 38), alpha=a)
        text(s, f"{fmt(km_)} km", font("mono-sb", 36), cor, (xs[1], y + 38), alpha=a)
        text(s, _tempo(seg), font("mono", 34), cor, (xs[2], y + 40), alpha=a)
        text(s, gar, font("sans", 30), cor if melhor else MUTE, (xs[3], y + 42), alpha=a)
        barra_h(s, xs[1], y + 92, 300, 8, (km_ - 12000) / (KM_NN - 12000), RED if melhor else CINZA, alpha=a)


@v.cena("escala", 35.0, "e com milhares de cidades?")
def s_escala(s, t):
    titulo(s, t, "// os limites do exato", "E com milhares de cidades?")
    r = pygame.Rect(100, TOP, 860, BOTTOM - TOP)
    rrect(s, CARD, r, 16)
    rrect(s, LINE_A, r, 16, 1)
    Pb = projetar(BRASIL_LAT, BRASIL_LON, r)
    k = ease((t - v.C("heur", 20.0)) / 6.0)
    if k > 0:
        n = max(2, int(len(Pb) * k))
        pygame.draw.lines(s, RED, False, [tuple(p) for p in Pb[:n]], 1)
    else:
        cor = (*mix(CARD, FG, 0.3), 255)
        for x, y in Pb:
            s.set_at((int(x), int(y)), cor)
    itens = [("pb", "Paraíba · 223 cidades", "ótimo provado em 15 s", FG),
             ("pr", "Paraná · 399 cidades", "ótimo provado em 7 min", FG),
             ("br", f"Brasil · {fmt(len(Pb))} municípios", "sem prova: grande demais para o exato", RED_SOFT),
             ("heur", "heurística: 2-opt entre vizinhos + refino", f"{fmt(KM_BRASIL)} km em 1 minuto", FG),
             ("cal", "onde havia prova", "a heurística ficou a 0,4% – 1,4% do ótimo", FG)]
    for i, (cue, tt, dd, cor) in enumerate(itens):
        a = appear(t, v.C(cue, 2.0 + i * 6.0))
        y = TOP + 10 + i * 148
        pygame.draw.rect(s, mix(INK, RED, a), (1020, y + 6, 4, 92), border_radius=2)
        text(s, tt, font("sans-sb", 32), cor, (1046, y), alpha=a)
        text(s, dd, font("sans", 26), BODY, (1046, y + 48), alpha=a)


@v.cena("estrada", 26.0, "o dado certo: linha reta x estrada")
def s_estrada(s, t):
    titulo(s, t, "// o dado certo", "Linha reta ou estrada?")
    ra, rb = pygame.Rect(100, TOP + 34, 620, 560), pygame.Rect(740, TOP + 34, 620, 560)
    for r, rot, cor in ((ra, "PLANEJADA NO MAPA (LINHA RETA)", MUTE), (rb, "PLANEJADA PELA ESTRADA", RED_SOFT)):
        rrect(s, CARD, r, 16)
        rrect(s, LINE_A, r, 16, 1)
        text(s, rot, font("mono-md", 18), cor, (r.x, r.y - 30))
    k = ease((t - 1.0) / 5.0)
    for r, plano, cor in ((ra, PLANO_RETA, (205, 205, 215)), (rb, PLANO_EST, RED)):
        Pe = projetar(E_LAT, E_LON, r)
        n = max(2, int(len(plano) * k))
        pygame.draw.lines(s, cor, False, [tuple(Pe[c]) for c in plano[:n]], 1)
    x = 1420
    a = appear(t, v.C("reta", 3.0))
    numero(s, f"{fmt(KM_MAPA)} km", "o que o mapa dizia (linha reta)", (x, TOP + 20), a, MUTE, 38)
    a = appear(t, v.C("troca", 8.0))
    numero(s, f"{fmt(KM_EE)} km", f"a viagem real pela estrada: +{fmt((KM_EE / KM_MAPA - 1) * 100)}%", (x, TOP + 150), a,
           RED_SOFT, 38)
    a = appear(t, v.C("plano", 15.0))
    if a > 0:
        yb = ra.bottom + 40
        for r, km_, cor in ((ra, KM_RE, (205, 205, 215)), (rb, KM_EE, RED)):
            text(s, f"rodando na estrada: {fmt(km_)} km", font("mono", 19), MUTE, (r.x, yb - 26), alpha=a)
            barra_h(s, r.x, yb, r.w, 12, km_ / KM_RE * ease((t - v.C("plano", 15.0)) / 1.5), cor, alpha=a)
        numero(s, f"−{fmt((1 - KM_EE / KM_RE) * 100)}%", "planejando direto pela estrada", (x, TOP + 300), a, FG, 56)
    a = appear(t, v.C("dado", 21.0))
    text(s, "o dado certo valeu mais", font("sans-b", 32), FG, (x, TOP + 470), alpha=a)
    text(s, "que qualquer algoritmo", font("sans-b", 32), RED_SOFT, (x, TOP + 512), alpha=a)


@v.cena("quando_ia", 21.0, "quando usar IA?")
def s_quando(s, t):
    titulo(s, t, "// então", "Quando usar IA?")
    cols = [("aqui", 100, "TEM FÓRMULA", "otimização", MUTE,
             ["menor rota, escala, corte de material", "objetivo é uma conta exata", "regras claras: dá para provar"]),
            ("sem", 990, "NÃO TEM FÓRMULA", "aprendizado (IA)", RED_SOFT,
             ["ler um chamado de manutenção", "reconhecer um capacete numa imagem", "o padrão está nos dados"])]
    for cue, x, rot, tt, cor, itens in cols:
        a = appear(t, v.C(cue, 3.0 if cue == "sem" else 12.0))
        if a <= 0:
            continue
        r = (x, TOP + 10 + int((1 - a) * 14), 830, 560)
        rrect(s, CARD, r, 16)
        rrect(s, (229, 72, 77, 130) if cue == "sem" else LINE_A, r, 16, 2 if cue == "sem" else 1)
        text(s, rot, font("mono-md", 22), cor, (x + 40, r[1] + 40), alpha=a)
        text(s, tt, font("sans-b", 54), FG, (x + 40, r[1] + 84), alpha=a)
        for i, it in enumerate(itens):
            pygame.draw.circle(s, mix(CARD, cor, a), (x + 52, r[1] + 220 + i * 86), 7)
            text(s, it, font("sans", 32), BODY, (x + 80, r[1] + 198 + i * 86), alpha=a)
    text(s, "problema com conta exata pede otimização, não aprendizado", font("sans-sb", 34), FG, (W // 2, 880),
         "midtop", appear(t, v.C("pede", 17.0)))


_picking = {}


@v.cena("armazem", 12.0, "na prática: separação no armazém")
def s_armazem(s, t):
    titulo(s, t, "// fora do mapa", "A mesma conta, num armazém")
    if "mod" not in _picking:
        import cena_picking
        _picking["mod"] = cena_picking
    cp = _picking["mod"]
    tt = min(cp.DUR - 4.5, 1.5 + t * (cp.T_FIM_A - 0.5) / max(1.0, v.dur - 1.0))
    quadro = pygame.transform.smoothscale(cp.quadro(tt).subsurface((40, 205, 1000, 650)), (1080, 702))
    rrect(s, CARD, (96, TOP + 16, 1088, 710), 16)
    s.blit(quadro, (100, TOP + 20))
    x = 1240
    text(s, "ordem de separação", font("sans-sb", 34), FG, (x, TOP + 60), alpha=appear(t, 0.5))
    text(s, "de um pedido", font("sans-sb", 34), FG, (x, TOP + 102), alpha=appear(t, 0.5))
    for i, (a_, b_) in enumerate((("mesmo separador", MUTE), ("mesma velocidade", MUTE), ("metade da caminhada", RED_SOFT))):
        text(s, a_, font("sans", 30), b_, (x, TOP + 210 + i * 56), alpha=appear(t, 2.0 + i * 1.2))
    text(s, "distância medida pelos corredores,", font("sans", 22), MUTE, (x, TOP + 430), alpha=appear(t, 5.0))
    text(s, "não em linha reta", font("sans", 22), MUTE, (x, TOP + 460), alpha=appear(t, 5.0))


@v.cena("rodar", 9.0, "como rodar")
def s_rodar(s, t):
    titulo(s, t, "// sua vez", "Como rodar")
    for i, (c, cm) in enumerate((("pip install numpy scipy", ""), ("python rota_do_zero.py", "# com o capitais.csv na mesma pasta"))):
        a = appear(t, 0.4 + i * 0.8)
        y = 330 + i * 96
        text(s, "$ ", font("mono-sb", 36), RED, (140, y), alpha=a)
        wd = text(s, c, font("mono", 36), FG, (190, y), alpha=a).right
        if cm:
            text(s, cm, font("mono", 26), MUTE, (wd + 40, y + 8), alpha=a)
    text(s, "código completo, os dados e o projeto inteiro: link na descrição", font("sans", 30), BODY, (140, 620),
         alpha=appear(t, 2.2))


@v.cena("outro", 13.0)
def s_outro(s, t):
    eyebrow(s, "// no próximo vídeo", (W // 2, 240), appear(t, 0.2), "midtop")
    text(s, "Aí sim, um problema que precisa de IA", font("sans-b", 54), FG, (W // 2, 286), "midtop", appear(t, 0.4))
    text(s, "visão computacional no armazém", font("sans", 36), RED_SOFT, (W // 2, 366), "midtop", appear(t, 1.0))
    t0 = max(4.0, v.dur - 7.5)
    text(s, "a sua imaginação é o limite.", font("sans", 36), BODY, (W // 2, 500), "center", appear(t, t0, 0.6))
    r = pygame.Rect(0, 0, 560, 120)
    r.center = (W // 2, 640)
    b = appear(t, t0 + 0.7, 0.5)
    rrect(s, RED, r.inflate(int(-40 * (1 - b)), int(-20 * (1 - b))), 18)
    text(s, "INSCREVA-SE", font("sans-b", 54), (255, 255, 255), r.center, "center", b)
    text(s, "@elucas.dev", font("mono-sb", 40), FG, (W // 2, 780), "center", appear(t, t0 + 1.4))


if __name__ == "__main__":
    v.main()
