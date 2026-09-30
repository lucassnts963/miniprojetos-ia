"""Cena 1080x1080: o modelo de triagem DE VERDADE classificando chamados (LinkedIn/Stories).

Visual no tema elucas.dev (o mesmo do YouTube): fundo ink com brilho vermelho e grade de
pontos, IBM Plex Sans/Mono, marca no topo, @elucas.dev no rodapé e capítulo no canto.

Nada aqui é roteirizado: equipe, prioridade, confiança, motivo e as ativações da
camada oculta vêm do modelo treinado (../modelo.npz).

    python cena_triagem.py              # renderiza cena_triagem.mp4
    python cena_triagem.py --still 6.5  # salva um quadro em PNG para conferir
"""
import os
import random
import subprocess
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import numpy as np
import pygame

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, PROJ)
from modelo import Triagem, carregar_dados  # noqa: E402
from rede import EQUIPES  # noqa: E402
from vetorizador import palavras  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")

W = H = 1080
FPS = 30
DUR = 24.0
FADE = 0.4
FONTES = os.path.join(os.path.dirname(PROJ), "ferramentas", "youtube", "fonts")

# ---------------- tema elucas (igual ao ferramentas/youtube/render.py) ----------------
INK = (12, 12, 15)
CARD = (22, 22, 26)
RED = (229, 72, 77)
RED_SOFT = (240, 138, 141)
FG = (236, 236, 239)
BODY = (180, 180, 188)
MUTE = (135, 135, 143)
LINE_A = (255, 255, 255, 23)
TINT_A = (229, 72, 77, 31)
TINT_BORDER_A = (229, 72, 77, 77)
PRIO = {"URGENTE": (229, 72, 77), "ALTA": (240, 150, 60), "MÉDIA": (225, 200, 80), "BAIXA": (140, 140, 160)}


def mix(a, b, k):
    k = max(0.0, min(1.0, k))
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


CARD_2 = mix(CARD, (255, 255, 255), 0.04)   # card dentro de card
LINE_ON_CARD = mix(CARD, (255, 255, 255), 0.09)
NODE_OFF = mix(CARD, (255, 255, 255), 0.12)

# os três primeiros são digitados na tela; os outros entram direto, cada vez mais rápido
DIGITADOS = [
    "o motor da bomba 2 tá cheirando queimado",
    "vazamento de óleo na prensa, pingando no chão",
    "CLP da linha 3 não comunica com a IHM",
]
RAPIDOS = [
    "painel soltando fumaça, parou tudo",
    "calibrar o transmissor de nível na parada",
    "rolamento chiando na esteira",
    "tela do supervisório congelou",
    "sensor de temperatura do forno oscilando",
    "lâmpada do corredor queimada",
    "robô da paletizadora parado com alarme",
    "válvula de controle travada, reator esquentando",
    "bomba de água gelada vibrando muito",
    "manômetro da caldeira com vidro trincado",
]

pygame.init()
pygame.display.set_mode((1, 1))
_fonts = {}


def font(kind, size):
    key = (kind, size)
    if key not in _fonts:
        files = {
            "sans": "IBMPlexSans-Regular", "sans-md": "IBMPlexSans-Medium", "sans-sb": "IBMPlexSans-SemiBold",
            "sans-b": "IBMPlexSans-Bold", "mono": "IBMPlexMono-Regular", "mono-md": "IBMPlexMono-Medium",
            "mono-sb": "IBMPlexMono-SemiBold",
        }
        _fonts[key] = pygame.font.Font(os.path.join(FONTES, files[kind] + ".ttf"), size)
    return _fonts[key]


# ---------------- helpers de desenho ----------------
def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, k):
    return a + (b - a) * k


def text(s, txt, f, col, pos, anchor="topleft", alpha=1.0):
    img = f.render(txt, True, col)
    if alpha < 1:
        img.set_alpha(int(255 * max(0, alpha)))
    r = img.get_rect(**{anchor: pos})
    s.blit(img, r)
    return r


def rrect(s, color, rect, radius=14, width=0):
    if len(color) == 4:
        tmp = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        pygame.draw.rect(tmp, color, (0, 0, rect[2], rect[3]), width, border_radius=radius)
        s.blit(tmp, (rect[0], rect[1]))
    else:
        pygame.draw.rect(s, color, rect, width, border_radius=radius)


def card_bg(s, rect, title=None, radius=16):
    """Card do tema: fundo card, borda fina e, com título, a barra de janela com três bolinhas."""
    rrect(s, CARD, rect, radius)
    rrect(s, LINE_A, rect, radius, 1)
    if title is not None:
        x, y, w, _ = rect
        for i in range(3):
            pygame.draw.circle(s, (70, 70, 76), (x + 22 + i * 16, y + 22), 5)
        text(s, title, font("mono", 17), MUTE, (x + 80, y + 22), "midleft")
        pygame.draw.line(s, LINE_ON_CARD, (x, y + 44), (x + w - 1, y + 44))


def badge(s, txt, pos, size=16, anchor="topleft"):
    f = font("mono-md", size)
    tw, th = f.size(txt)
    r = pygame.Rect(0, 0, tw + 24, th + 10)
    setattr(r, anchor, pos)
    rrect(s, TINT_A, r, 8)
    rrect(s, TINT_BORDER_A, r, 8, 1)
    text(s, txt, f, RED_SOFT, r.center, "center")
    return r


def rich(s, txt, f, x, y, largura, destaque=(), cor=FG, cor_destaque=RED_SOFT, max_linhas=2, entrelinha=24):
    """Texto quebrado em linhas, com as palavras do 'motivo' pintadas de outra cor."""
    esp = f.size(" ")[0]
    cx, linha = x, 0
    for w in txt.split():
        img_w = f.size(w)[0]
        if cx > x and cx + img_w > x + largura:
            linha += 1
            cx = x
            if linha >= max_linhas:
                return
        hl = any(p in destaque for p in palavras(w))
        s.blit(f.render(w, True, cor_destaque if hl else cor), (cx, y + linha * entrelinha))
        cx += img_w + esp


def make_backdrop():
    bg = pygame.Surface((W, H))
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W * 0.5) / (W * 0.6)) ** 2 + ((yy - H * 0.48) / (H * 0.6)) ** 2)
    g = np.clip(1 - d, 0, 1) ** 2 * 0.18
    arr = np.zeros((W, H, 3))
    for i in range(3):
        arr[:, :, i] = (INK[i] + (RED[i] - INK[i]) * g).T
    pygame.surfarray.blit_array(bg, arr.astype(np.uint8))
    dot = mix(INK, (255, 255, 255), 0.11)
    for x in range(12, W, 24):
        for y in range(12, H, 24):
            pygame.draw.circle(bg, dot, (x, y), 1)
    return bg


BACKDROP = make_backdrop()


def chrome(s):
    pygame.draw.rect(s, RED, (48, 42, 12, 12), border_radius=3)
    text(s, "elucas.dev", font("mono-sb", 22), FG, (68, 48), "midleft")
    badge(s, "INDÚSTRIA", (W - 48, 32), 15, "topright")
    text(s, "@elucas.dev", font("mono", 18), MUTE, (48, H - 40), "midleft")
    text(s, "triagem de manutenção", font("mono", 18), MUTE, (W - 48, H - 40), "midright")


# ---------------- o modelo decide tudo ----------------
modelo = Triagem.carregar()


def classificar(txt):
    r = modelo.classificar(txt)
    h, _, _ = modelo.rede.forward(modelo.tfidf.transform([txt]))
    r["oculta"] = h[0]
    return r


events = []
t = 1.0
for txt in DIGITADOS:
    # o próximo começa a ser digitado enquanto o anterior ainda está sendo decidido
    t_type = len(txt) / 30.0
    events.append(dict(t=t + t_type, t0=t, big=True, typed=True, net=1.1, **classificar(txt)))
    t = events[-1]["t"] + 0.9
t = events[-1]["t"] + 1.3
for i, txt in enumerate(RAPIDOS):
    net = max(0.3, 0.7 - i * 0.05)
    events.append(dict(t=t, t0=t - 0.2, big=True, typed=False, net=net, **classificar(txt)))
    t += max(0.45, 1.1 - i * 0.09)
T_FLOOD = t
_textos, _, _ = carregar_dados()
rng = random.Random(7)
rng.shuffle(_textos)
pe, pp = modelo.probabilidades(_textos)
k = 0
while t < DUR - 2.4:
    events.append(dict(t=t, t0=t, big=False, typed=False, net=0.2,
                       equipe=EQUIPES[pe[k].argmax()], prioridade=list(PRIO)[pp[k].argmax()]))
    k += 1
    t += 0.1

for ev in events:
    if ev["big"]:
        print(f"{ev['t']:5.1f}s  {ev['equipe']:<15} {ev['prioridade']:<8} {ev['texto']}  <- {ev['motivo_equipe']}")

# unidades da camada oculta que mais mudam entre os chamados mostrados (para o desenho da rede)
_hs = np.array([ev["oculta"] for ev in events if ev["big"]])
UNIDADES = np.argsort(-_hs.std(0))[:8]
H_MAX = _hs[:, UNIDADES].max(0) + 1e-9

T_IN, T_OUT = 0.45, 0.6
_r = random.Random(3)
rng_y = {id(ev): _r.uniform(-40, 260) for ev in events if not ev["big"]}

# ---------------- layout ----------------
TOP, BOTTOM = 232, 836
INBOX = pygame.Rect(48, TOP, 364, BOTTOM - TOP)
INPUT = pygame.Rect(64, TOP + 60, 332, 104)
NET_C = (540, 540)
Q_X, Q_W = 668, 364
Q_GAP = 14
Q_H = (BOTTOM - TOP - 3 * Q_GAP) // 4
QUEUES = {t: pygame.Rect(Q_X, TOP + i * (Q_H + Q_GAP), Q_W, Q_H) for i, t in enumerate(EQUIPES)}
CARD_W, CARD_H = 330, 84
LOG_Y = INPUT.bottom + 26

LAYERS = [5, 8, 4]
NODES = []
for li, n in enumerate(LAYERS):
    x = NET_C[0] - 72 + li * 72
    NODES.append([(x, NET_C[1] - (n - 1) * 24 / 2 + i * 24) for i in range(n)])


def card(s, cx, cy, ev, scale=1.0, alpha=1.0, decidido=False):
    """Desenha em tamanho cheio e reduz, para o texto continuar visível enquanto o card encolhe."""
    w, h = CARD_W, CARD_H
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cor = PRIO[ev["prioridade"]] if decidido else MUTE
    pygame.draw.rect(surf, CARD_2, (0, 0, w, h), border_radius=12)
    rrect(surf, (*cor, 200) if decidido else LINE_A, (0, 0, w, h), 12, 1 if not decidido else 2)
    pygame.draw.rect(surf, cor, (0, 10, 4, h - 20), border_radius=2)
    text(surf, "ORDEM DE MANUTENÇÃO", font("mono-md", 12), MUTE, (18, 10))
    rich(surf, ev["texto"], font("sans", 19), 18, 30, w - 30, ev["motivo_equipe"] if decidido else ())
    if decidido:
        tg = font("mono-sb", 12).render(ev["prioridade"], True, INK)
        tr = pygame.Rect(0, 0, tg.get_width() + 14, 20)
        tr.topright = (w - 10, 7)
        pygame.draw.rect(surf, cor, tr, border_radius=5)
        surf.blit(tg, tg.get_rect(center=tr.center))
    sw, sh = max(1, int(w * scale)), max(1, int(h * scale))
    if (sw, sh) != (w, h):
        surf = pygame.transform.smoothscale(surf, (sw, sh))
    surf.set_alpha(int(255 * alpha))
    s.blit(surf, surf.get_rect(center=(int(cx), int(cy))))


def queue_slot(team, k):
    q = QUEUES[team]
    row, col = divmod(k, 14)
    return q.x + 30 + col * 22, q.y + 62 + row * 22


def draw_net(s, t):
    """Rede no centro. Durante o processamento, a camada oculta acende com as ativações reais."""
    ativo, brilho = None, 0.0
    for ev in events:
        dt = t - ev["t"]
        if ev["big"] and 0 <= dt < T_IN + ev["net"] + 0.2:
            ativo = ev
            brilho = min(1.0, dt / T_IN, (T_IN + ev["net"] + 0.2 - dt) / 0.2)
        elif not ev["big"] and 0 <= dt < T_IN + 0.2:
            brilho = max(brilho, 0.5)
    halo = pygame.Surface((240, 240), pygame.SRCALPHA)
    pygame.draw.circle(halo, (*RED, int(14 + 34 * brilho)), (120, 120), 106)
    pygame.draw.circle(halo, (*RED, int(30 + 60 * brilho)), (120, 120), 106, 1)
    s.blit(halo, (NET_C[0] - 120, NET_C[1] - 120))
    val = [np.full(LAYERS[0], brilho), np.zeros(LAYERS[1]), np.zeros(LAYERS[2])]
    if ativo is not None:
        dt = t - ativo["t"]
        k_h = smooth((dt - T_IN * 0.5) / 0.35)
        k_o = smooth((dt - T_IN * 0.5 - 0.3) / 0.35)
        val[1] = ativo["oculta"][UNIDADES] / H_MAX * k_h * brilho
        val[2] = np.array([ativo["prob_equipe"][e] for e in EQUIPES]) * k_o * brilho
    for li in range(2):
        for i, a in enumerate(NODES[li]):
            for j, b in enumerate(NODES[li + 1]):
                k = min(val[li][i], val[li + 1][j])
                pygame.draw.line(s, mix(LINE_ON_CARD, RED, 0.1 + k * 0.9), a, b, 2 if k > 0.4 else 1)
    for li, layer in enumerate(NODES):
        for i, p in enumerate(layer):
            v = val[li][i]
            pygame.draw.circle(s, mix(NODE_OFF, RED, v), p, 8)
            if v > 0.6:
                pygame.draw.circle(s, RED_SOFT, p, 8, 2)
    return ativo


def draw_result(s, t):
    """Decisão acima da rede e o 'porquê' abaixo, só do chamado mais recente."""
    atual = None
    for ev in events:
        dt = t - ev["t"]
        fim = T_IN + ev["net"] + T_OUT + (0.5 if ev["typed"] else 0.2)
        if ev["big"] and T_IN + 0.15 <= dt < fim:
            atual, ka = ev, min(1, (dt - T_IN - 0.15) / 0.15, (fim - dt) / 0.2)
    if atual is None:
        return
    ev = atual
    col = PRIO[ev["prioridade"]]
    text(s, "EQUIPE", font("mono-md", 12), MUTE, (NET_C[0], 290), "midtop", ka)
    r1 = text(s, ev["equipe"], font("sans-b", 24), FG, (NET_C[0], 306), "midtop", ka)
    tg = font("mono-sb", 13).render(ev["prioridade"], True, INK)
    tr = pygame.Rect(0, 0, tg.get_width() + 16, 22)
    tr.midtop = (NET_C[0], r1.bottom + 6)
    chip = pygame.Surface(tr.size, pygame.SRCALPHA)
    pygame.draw.rect(chip, col, (0, 0, *tr.size), border_radius=6)
    chip.blit(tg, tg.get_rect(center=(tr.w // 2, tr.h // 2)))
    chip.set_alpha(int(255 * ka))
    s.blit(chip, tr)
    # confiança como barra (sem número, regra dos vídeos)
    bar = pygame.Surface((150, 6), pygame.SRCALPHA)
    pygame.draw.rect(bar, (*LINE_ON_CARD, 255), (0, 0, 150, 6), border_radius=3)
    pygame.draw.rect(bar, (*RED, 255), (0, 0, int(150 * ev["conf_equipe"]), 6), border_radius=3)
    bar.set_alpha(int(255 * ka))
    s.blit(bar, (NET_C[0] - 75, tr.bottom + 10))
    # motivo
    y = 670
    text(s, "POR CAUSA DE", font("mono-md", 12), MUTE, (NET_C[0], y), "midtop", ka)
    motivo = ev["motivo_equipe"] + [p for p in ev["motivo_prioridade"] if p not in ev["motivo_equipe"]]
    originais = {palavras(w)[0]: w.strip(",.") for w in ev["texto"].split() if palavras(w)}
    for i, p in enumerate(motivo[:3]):
        text(s, originais.get(p, p), font("sans-sb", 20), RED_SOFT, (NET_C[0], y + 20 + i * 28), "midtop", ka)


def draw_input(s, t):
    foco = False
    rrect(s, INK, INPUT, 12)
    for ev in events:
        if ev["big"] and ev["t0"] <= t < ev["t"] + 0.12:
            foco = True
            if ev["typed"]:
                n = int(len(ev["texto"]) * min(1, (t - ev["t0"]) / (ev["t"] - ev["t0"])))
                shown = ev["texto"][:n] + ("|" if int(t * 3) % 2 == 0 or n < len(ev["texto"]) else "")
            else:
                shown = ev["texto"]
            rich(s, shown, font("sans", 21), INPUT.x + 16, INPUT.y + 14, INPUT.w - 32, max_linhas=3, entrelinha=28)
    if foco:
        glow = pygame.Surface((INPUT.w + 12, INPUT.h + 12), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*RED, 46), (0, 0, INPUT.w + 12, INPUT.h + 12), 6, border_radius=16)
        s.blit(glow, (INPUT.x - 6, INPUT.y - 6))
        rrect(s, (*RED, 170), INPUT, 12, 1)
    else:
        rrect(s, LINE_A, INPUT, 12, 1)
        text(s, "descreva o problema...", font("sans", 21), mix(INK, MUTE, 0.7), (INPUT.x + 16, INPUT.y + 14))


def draw_log(s, t):
    """Últimos chamados já triados, na caixa de entrada."""
    text(s, "JÁ TRIADOS", font("mono-md", 13), MUTE, (INBOX.x + 16, LOG_Y))
    feitos = [ev for ev in events if ev["big"] and t - ev["t"] >= T_IN + ev["net"] + T_OUT]
    f_t, f_e = font("sans", 15), font("mono-md", 12)
    for i, ev in enumerate(reversed(feitos[-7:])):
        y = LOG_Y + 26 + i * 50
        a = 1.0 - i * 0.1
        dt = t - ev["t"] - (T_IN + ev["net"] + T_OUT)
        a *= ease(dt / 0.3) if i == 0 else 1
        col = PRIO[ev["prioridade"]]
        row = pygame.Surface((INBOX.w - 32, 42), pygame.SRCALPHA)
        pygame.draw.rect(row, (*CARD_2, 255), (0, 0, row.get_width(), 42), border_radius=8)
        pygame.draw.rect(row, (*col, 255), (0, 8, 3, 26), border_radius=2)
        txt = ev["texto"]
        while f_t.size(txt)[0] > row.get_width() - 26 and len(txt) > 4:
            txt = txt[:-2]
        if txt != ev["texto"]:
            txt = txt.rstrip(" ,") + "…"
        row.blit(f_t.render(txt, True, FG), (14, 2))
        row.blit(f_e.render(ev["equipe"], True, RED_SOFT), (14, 23))
        row.set_alpha(int(255 * max(0, a)))
        s.blit(row, (INBOX.x + 16, y))


def draw_frame(t):
    s = BACKDROP.copy()
    chrome(s)
    text(s, "IA NA PRÁTICA", font("mono-md", 20), RED, (W // 2, 100), "midtop")
    text(s, "Triagem de ordens de manutenção", font("sans-b", 42), FG, (W // 2, 130), "midtop")

    card_bg(s, INBOX, "novo chamado")
    draw_input(s, t)
    draw_log(s, t)

    # fila acende quando um chamado grande acabou de chegar nela
    chegou = {tm: 0.0 for tm in EQUIPES}
    for ev in events:
        if ev["big"]:
            dt = t - ev["t"] - (T_IN + ev["net"] + T_OUT * 0.85)
            if 0 <= dt < 0.6:
                chegou[ev["equipe"]] = max(chegou[ev["equipe"]], 1 - dt / 0.6)
    for team, q in QUEUES.items():
        card_bg(s, q)
        if chegou[team] > 0:
            rrect(s, (*RED, int(150 * chegou[team])), q, 16, 2)
        pygame.draw.rect(s, RED, (q.x + 18, q.y + 24, 4, 16), border_radius=2)
        text(s, team, font("sans-sb", 20), FG, (q.x + 30, q.y + 32), "midleft")

    draw_net(s, t)
    draw_result(s, t)

    counts = {tm: 0 for tm in EQUIPES}
    for ev in events:
        dt = t - ev["t"]
        if dt < 0:
            continue
        # os chamados da enxurrada saem da borda da caixa de entrada, não de dentro do campo de texto
        start = (INPUT.centerx, INPUT.centery) if ev["big"] else (INBOX.right, INPUT.centery + rng_y[id(ev)])
        slot = counts[ev["equipe"]]
        counts[ev["equipe"]] += 1
        qx, qy = queue_slot(ev["equipe"], slot)
        net = ev["net"]
        if dt < T_IN:
            k = smooth(dt / T_IN)
            x, y = lerp(start[0], NET_C[0], k), lerp(start[1], NET_C[1], k)
            if ev["big"]:
                card(s, x, y, ev, lerp(1.0, 0.55, k), 1.0 - 0.8 * max(0, k - 0.6) / 0.4)
            else:
                pygame.draw.rect(s, mix(CARD, MUTE, 0.7), (x - 7, y - 7, 14, 14), border_radius=4)
        elif dt < T_IN + net:
            pass
        elif dt < T_IN + net + T_OUT:
            k = smooth((dt - T_IN - net) / T_OUT)
            q = QUEUES[ev["equipe"]]
            if ev["big"]:
                mid = (q.centerx, q.centery)
                x, y = lerp(NET_C[0], mid[0], k), lerp(NET_C[1], mid[1], k)
                sc = lerp(0.5, 0.95, min(1, k * 1.6)) if k < 0.7 else lerp(0.95, 0.1, (k - 0.7) / 0.3)
                if k >= 0.7:
                    x, y = lerp(mid[0], qx, (k - 0.7) / 0.3), lerp(mid[1], qy, (k - 0.7) / 0.3)
                card(s, x, y, ev, sc, 1.0, decidido=True)
            else:
                x, y = lerp(NET_C[0], qx, k), lerp(NET_C[1], qy, k)
                pygame.draw.rect(s, PRIO[ev["prioridade"]], (x - 8, y - 8, 16, 16), border_radius=4)
        else:
            pygame.draw.rect(s, PRIO[ev["prioridade"]], (qx - 8, qy - 8, 16, 16), border_radius=4)

    # legenda de prioridade, centralizada
    f_leg = font("mono", 15)
    larg = sum(22 + f_leg.size(n)[0] + 26 for n in PRIO) - 26
    lx = W // 2 - larg // 2
    for name, col in PRIO.items():
        pygame.draw.rect(s, col, (lx, 862, 14, 14), border_radius=4)
        lx += 22 + text(s, name, f_leg, MUTE, (lx + 22, 869), "midleft").width + 26

    # legendas: três momentos, com troca suave
    t1, t2 = events[len(DIGITADOS)]["t"] - 0.4, T_FLOOD
    fases = [(0, ("Você escreve o chamado do seu jeito.", "A IA diz a equipe, a prioridade e o porquê.")),
             (t1, ("Cada chamado cai na fila certa,", "na hora.")),
             (t2, ("Em larga escala, sem pagar uma LLM", "a cada chamado."))]
    f_cap = font("sans-md", 27)
    for i, (ini, (c1, c2)) in enumerate(fases):
        fim = fases[i + 1][0] if i + 1 < len(fases) else DUR + 1
        if ini <= t < fim:
            a = min(ease((t - ini) / 0.5) if ini else 1.0, 1 - ease((t - (fim - 0.4)) / 0.4))
            text(s, c1, f_cap, FG, (W // 2, 910), "midtop", a)
            text(s, c2, f_cap, BODY, (W // 2, 948), "midtop", a)

    f = min(1.0, t / FADE, (DUR - t) / FADE)
    if f < 1:
        veil = pygame.Surface((W, H))
        veil.fill(INK)
        veil.set_alpha(int(255 * (1 - max(0, f))))
        s.blit(veil, (0, 0))
    return s


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--still":
        out = os.path.join(HERE, f"quadro_{sys.argv[2]}.png")
        pygame.image.save(draw_frame(float(sys.argv[2])), out)
        print("OK", out)
        return
    out = os.path.join(HERE, "cena_triagem.mp4")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "14",
                          "-pix_fmt", "yuv420p", "-r", str(FPS), "-an", out], stdin=subprocess.PIPE)
    for n in range(int(DUR * FPS)):
        p.stdin.write(pygame.image.tobytes(draw_frame(n / FPS), "RGB"))
    p.stdin.close()
    p.wait()
    print("OK", out)


if __name__ == "__main__":
    main()
