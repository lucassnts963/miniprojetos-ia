"""Vídeo YouTube (1920x1080) — Snake com neuroevolução, no tema elucas.dev.

uso:
  python render.py                 -> renderiza tudo em out/video.mp4
  python render.py --still cena t  -> salva out/still_<cena>_<t>.png (pré-visualização)
"""
import math
import os
import random
import subprocess
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import numpy as np
import pygame
from pygments.lexers import PythonLexer
from pygments.token import Token

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = "C:/dev/snake"
sys.path.insert(0, PROJ)
os.chdir(PROJ)  # genetic_ai importa config relativo
import genetic_ai as ga  # noqa: E402

os.chdir(HERE)
W, H, FPS = 1920, 1080, 30

# ---------------- tema elucas ----------------
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


def mix(a, b, k):
    k = max(0.0, min(1.0, k))
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


LINE = mix(INK, (255, 255, 255), 0.09)
LINE_ON_CARD = mix(CARD, (255, 255, 255), 0.09)

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
        _fonts[key] = pygame.font.Font(os.path.join(HERE, "fonts", files[kind] + ".ttf"), size)
    return _fonts[key]


# ---------------- helpers de desenho ----------------
def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def appear(t, start, dur=0.5):
    return ease((t - start) / dur)


def text(surf, s, f, color, pos, anchor="topleft", alpha=1.0):
    img = f.render(s, True, color)
    if alpha < 1:
        img.set_alpha(int(255 * max(0, alpha)))
    r = img.get_rect(**{anchor: pos})
    surf.blit(img, r)
    return r


def text_lines(surf, lines, f, color, pos, lh=None, anchor="topleft", alpha=1.0):
    lh = lh or int(f.get_linesize() * 1.05)
    x, y = pos
    for i, ln in enumerate(lines):
        a = anchor
        text(surf, ln, f, color, (x, y + i * lh), a, alpha)
    return y + len(lines) * lh


def rrect(surf, color, rect, radius=14, width=0):
    if len(color) == 4:
        tmp = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        pygame.draw.rect(tmp, color, (0, 0, rect[2], rect[3]), width, border_radius=radius)
        surf.blit(tmp, (rect[0], rect[1]))
    else:
        pygame.draw.rect(surf, color, rect, width, border_radius=radius)


def card(surf, rect, title=None, radius=16):
    rrect(surf, CARD, rect, radius)
    rrect(surf, LINE_A, rect, radius, 1)
    if title is not None:
        x, y, w, _ = rect
        for i, c in enumerate([(70, 70, 76)] * 3):
            pygame.draw.circle(surf, c, (x + 26 + i * 20, y + 24), 6)
        text(surf, title, font("mono", 20), MUTE, (x + 96, y + 24), "midleft")
        pygame.draw.line(surf, LINE_ON_CARD, (x, y + 48), (x + w - 1, y + 48))


def badge(surf, s, pos, size=18, anchor="topleft"):
    f = font("mono-md", size)
    tw, th = f.size(s)
    r = pygame.Rect(0, 0, tw + 28, th + 12)
    setattr(r, anchor, pos)
    rrect(surf, TINT_A, r, 8)
    rrect(surf, TINT_BORDER_A, r, 8, 1)
    text(surf, s, f, RED_SOFT, r.center, "center")
    return r


def eyebrow(surf, s, pos, alpha=1.0, anchor="topleft"):
    return text(surf, s, font("mono-md", 22), RED, pos, anchor, alpha)


# ---------------- fundo + chrome ----------------
def make_backdrop():
    bg = pygame.Surface((W, H))
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W * 0.5) / (W * 0.55)) ** 2 + ((yy - H * 0.45) / (H * 0.6)) ** 2)
    g = np.clip(1 - d, 0, 1) ** 2 * 0.18
    arr = np.zeros((W, H, 3))
    for i in range(3):
        arr[:, :, i] = (INK[i] + (RED[i] - INK[i]) * g).T
    pygame.surfarray.blit_array(bg, arr.astype(np.uint8))
    dot = mix(INK, (255, 255, 255), 0.11)
    for x in range(16, W, 32):
        for y in range(16, H, 32):
            pygame.draw.circle(bg, dot, (x, y), 1)
    return bg


BACKDROP = make_backdrop()


def chrome(surf, chapter=None):
    pygame.draw.rect(surf, RED, (64, 44, 12, 12), border_radius=3)
    text(surf, "elucas.dev", font("mono-sb", 24), FG, (88, 50), "midleft")
    badge(surf, "IA · PYTHON", (W - 64, 34), 16, "topright")
    text(surf, "@elucas.dev", font("mono", 20), MUTE, (64, H - 44), "midleft")
    if chapter:
        text(surf, chapter, font("mono", 20), MUTE, (W - 64, H - 44), "midright")


# ---------------- código com destaque ----------------
SRC_LINES = open(os.path.join(PROJ, "genetic_ai.py"), encoding="utf-8").read().split("\n")
KW = {"def", "class", "return", "if", "else", "elif", "for", "in", "while", "not", "and", "or", "import",
      "from", "as", "None", "True", "False", "lambda", "with", "try", "finally", "break", "is"}


def tok_color(ttype, val):
    if ttype in Token.Comment:
        return MUTE
    if ttype in Token.Literal.String:
        return RED_SOFT
    if ttype in Token.Literal.Number:
        return RED_SOFT
    if ttype in Token.Keyword or val in KW:
        return RED
    if ttype in Token.Name.Function or ttype in Token.Name.Class:
        return (255, 255, 255)
    if ttype in Token.Name.Builtin:
        return RED_SOFT
    if ttype in Token.Operator or ttype in Token.Punctuation:
        return BODY
    return FG


LEX = PythonLexer()


def code_block(surf, rect, first, last, t, hl=None, title="genetic_ai.py", size=21, reveal=0.0):
    """Desenha genetic_ai.py[first..last] (1-indexado). hl = (a, b) linhas destacadas."""
    card(surf, rect, title)
    x0, y0 = rect[0] + 20, rect[1] + 66
    f = font("mono", size)
    lh = int(size * 1.5)
    lines = SRC_LINES[first - 1:last]
    base_indent = min((len(l) - len(l.lstrip()) for l in lines if l.strip()), default=0)
    surf.set_clip(pygame.Rect(rect[0], rect[1] + 50, rect[2] - 14, rect[3] - 56))
    for i, ln in enumerate(lines):
        n = first + i
        vis = appear(t, reveal + i * 0.04, 0.3) if reveal is not None else 1
        if vis <= 0:
            continue
        y = y0 + i * lh
        on = hl is None or (hl[0] <= n <= hl[1])
        if hl is not None and on:
            rrect(surf, TINT_A, (rect[0] + 8, y - 3, rect[2] - 16, lh), 6)
            pygame.draw.rect(surf, RED, (rect[0] + 8, y - 3, 3, lh))
        text(surf, f"{n:>3}", f, (70, 70, 78), (x0, y), alpha=vis)
        x = x0 + f.size("0000")[0]
        dim = 1.0 if on else 0.38
        for ttype, val in LEX.get_tokens(ln[base_indent:]):
            if val == "\n":
                continue
            col = mix(CARD, tok_color(ttype, val), dim)
            img = f.render(val, True, col)
            img.set_alpha(int(255 * vis))
            surf.blit(img, (x, y))
            x += img.get_width()
            if x > rect[0] + rect[2] - 20:
                break
    surf.set_clip(None)


def active_hl(t, marks):
    cur = None
    for ts, rng in marks:
        if t >= ts:
            cur = rng
    return cur


def side_notes(surf, t, notes, x, y, w):
    """notes: [(t_start, titulo, [linhas])] — o atual fica aceso, os anteriores apagados."""
    cur = -1
    for i, (ts, *_r) in enumerate(notes):
        if t >= ts:
            cur = i
    yy = y
    for i, (ts, title, body) in enumerate(notes):
        a = appear(t, ts, 0.45)
        if a <= 0:
            break
        act = i == cur
        off = int((1 - a) * 18)
        col_t = FG if act else MUTE
        pygame.draw.rect(surf, RED if act else LINE, (x, yy + off + 4, 4, 30 + 34 * len(body)), border_radius=2)
        text(surf, title, font("sans-sb", 30), col_t, (x + 24, yy + off), alpha=a)
        for j, b in enumerate(body):
            text(surf, b, font("sans", 24), BODY if act else mix(INK, MUTE, 0.7), (x + 24, yy + off + 44 + j * 34), alpha=a)
        yy += 70 + 34 * len(body)


# ---------------- episódio real do modelo ----------------
AGENT = ga.load_agent(os.path.join(PROJ, "best_snake.npz"))
BRAIN = AGENT.brain


def forward_all(x):
    x = np.asarray(x, dtype=float)
    a1 = np.maximum(0, x @ BRAIN.w1 + BRAIN.b1)
    a2 = np.maximum(0, a1 @ BRAIN.w2 + BRAIN.b2)
    out = a2 @ BRAIN.w3 + BRAIN.b3
    return x, a1, a2, out


def record_episode(size, seed, max_steps):
    env = ga.MiniSnake(size, random.Random(seed))
    frames = []
    while env.alive and env.steps < max_steps:
        st = env.get_state()
        x, a1, a2, out = forward_all(st)
        act = int(np.argmax(out))
        frames.append(dict(snake=list(env.snake), food=env.food, dir=env.direction, score=env.score,
                           x=x, a1=a1, a2=a2, out=out, act=act))
        env.step(act)
    frames.append(dict(snake=list(env.snake), food=env.food, dir=env.direction, score=env.score,
                       x=frames[-1]["x"], a1=frames[-1]["a1"], a2=frames[-1]["a2"], out=frames[-1]["out"],
                       act=frames[-1]["act"], dead=not env.alive))
    return frames


def pick_episode(size=20, need=700):
    best = None
    for seed in range(200):
        fr = record_episode(size, seed, need)
        sc = fr[-1]["score"]
        if len(fr) >= need and (best is None or sc > best[1]):
            best = (fr, sc, seed)
        if best and best[1] >= 38:
            break
    return best


EP, EP_SCORE, EP_SEED = pick_episode()
A1_MAX = max(1e-6, max(f["a1"].max() for f in EP))
A2_MAX = max(1e-6, max(f["a2"].max() for f in EP))


def draw_board(surf, rect, fr, show_sensors=True, cell=None):
    size = 20
    x0, y0, w, h = rect
    c = cell or w // size
    rrect(surf, (16, 16, 20), (x0 - 10, y0 - 10, c * size + 20, c * size + 20), 12)
    rrect(surf, LINE_A, (x0 - 10, y0 - 10, c * size + 20, c * size + 20), 12, 1)
    for i in range(size + 1):
        pygame.draw.line(surf, (24, 24, 29), (x0 + i * c, y0), (x0 + i * c, y0 + size * c))
        pygame.draw.line(surf, (24, 24, 29), (x0, y0 + i * c), (x0 + size * c, y0 + i * c))
    fx, fy = fr["food"]
    pygame.draw.rect(surf, RED, (x0 + fx * c + 3, y0 + fy * c + 3, c - 6, c - 6), border_radius=4)
    n = len(fr["snake"])
    for j, (sx, sy) in enumerate(reversed(fr["snake"])):
        k = j / max(1, n - 1)
        col = mix((90, 90, 98), FG, k)
        pygame.draw.rect(surf, col, (x0 + sx * c + 2, y0 + sy * c + 2, c - 4, c - 4), border_radius=5)
    hx, hy = fr["snake"][0]
    pygame.draw.rect(surf, RED_SOFT, (x0 + hx * c + 2, y0 + hy * c + 2, c - 4, c - 4), border_radius=5)
    if show_sensors and not fr.get("dead"):
        d = fr["dir"]
        for k, dd in enumerate([d, ga.TURN_RIGHT[d], ga.TURN_LEFT[d]]):
            dx, dy = ga.DIRS[dd]
            cx, cy = hx + dx, hy + dy
            blocked = fr["x"][k] > 0.5
            r = pygame.Rect(x0 + cx * c + 1, y0 + cy * c + 1, c - 2, c - 2)
            if blocked:
                rrect(surf, (229, 72, 77, 90), r, 5)
            pygame.draw.rect(surf, RED if blocked else (80, 80, 90), r, 2, border_radius=5)
    return c


# ---------------- rede neural ----------------
IN_LABELS = ["perigo reto", "perigo direita", "perigo esquerda", "indo p/ cima", "indo p/ baixo",
             "indo p/ esquerda", "indo p/ direita", "comida à esquerda", "comida à direita", "comida acima",
             "comida abaixo"]
OUT_LABELS = ["SEGUIR RETO", "VIRAR À DIREITA", "VIRAR À ESQUERDA"]


def net_layout(rect):
    x0, y0, w, h = rect
    a, b = x0 + 230, x0 + w - 290
    cols = [a, a + (b - a) / 3, a + 2 * (b - a) / 3, b]
    sizes = [11, 16, 12, 3]
    pos = []
    for ci, n in enumerate(sizes):
        span = h - 40 if ci else h - 40
        gap = min(span / max(1, n - 1), 64 if ci == 3 else 60)
        top = y0 + h / 2 - gap * (n - 1) / 2
        pos.append([(cols[ci], top + i * gap) for i in range(n)])
    return pos


def draw_net(surf, rect, fr, live=True, alpha=1.0, highlight_layer=None):
    pos = net_layout(rect)
    layers = [fr["x"], fr["a1"] / A1_MAX, fr["a2"] / A2_MAX, None]
    out = fr["out"]
    ws = [BRAIN.w1, BRAIN.w2, BRAIN.w3]
    acts = [fr["x"], fr["a1"], fr["a2"]]
    lines = []
    for li in range(3):
        contrib = acts[li][:, None] * ws[li] if live else np.abs(ws[li]) * 0.3
        m = max(1e-6, np.abs(contrib).max())
        for i in range(ws[li].shape[0]):
            for j in range(ws[li].shape[1]):
                v = contrib[i, j] / m
                lines.append((abs(v), v, pos[li][i], pos[li + 1][j]))
    lines.sort(key=lambda z: z[0])
    for mag, v, p1, p2 in lines:
        if live:
            k = min(1.0, mag * 1.1) * alpha
            col = mix(INK, RED if v > 0 else (120, 120, 132), 0.08 + 0.85 * k)
            wdt = 1 if mag < 0.45 else 2
        else:
            col = mix(INK, (90, 90, 100), (0.15 + mag) * alpha)
            wdt = 1
        pygame.draw.aaline(surf, col, p1, p2) if wdt == 1 else pygame.draw.line(surf, col, p1, p2, wdt)
    # nós
    for li, layer in enumerate(pos):
        for i, (x, y) in enumerate(layer):
            if li < 3:
                a = float(layers[li][i]) if live else 0.0
                r = 13 if li == 0 else 11
            else:
                a = 1.0 if (live and i == fr["act"]) else 0.0
                r = 20
            fill = mix(CARD, RED, a)
            pygame.draw.circle(surf, fill, (int(x), int(y)), r)
            pygame.draw.circle(surf, RED if a > 0.5 else (70, 70, 80), (int(x), int(y)), r, 2)
    # rótulos
    fl = font("mono", 19)
    for i, (x, y) in enumerate(pos[0]):
        on = live and fr["x"][i] > 0.5
        text(surf, IN_LABELS[i], fl, FG if on else MUTE, (x - 26, y), "midright")
    fo = font("sans-sb", 24)
    omax = max(1e-6, np.abs(out).max())
    for i, (x, y) in enumerate(pos[3]):
        chosen = live and i == fr["act"]
        text(surf, OUT_LABELS[i], fo, RED if chosen else MUTE, (x + 36, y - 12), "midleft")
        bw = int(150 * max(0, out[i]) / omax) if live else 0
        pygame.draw.rect(surf, (40, 40, 46), (x + 36, y + 10, 150, 6), border_radius=3)
        if bw:
            pygame.draw.rect(surf, RED if chosen else MUTE, (x + 36, y + 10, bw, 6), border_radius=3)
        if live:
            text(surf, f"{out[i]:+.1f}", font("mono", 18), RED if chosen else MUTE, (x + 196, y + 13), "midleft")
    cap = font("mono", 18)
    names = [("entrada", "11"), ("oculta", "16 · ReLU"), ("oculta", "12 · ReLU"), ("saída", "3 · argmax")]
    for li, layer in enumerate(pos):
        x = layer[0][0]
        col = RED if highlight_layer == li else MUTE
        text(surf, names[li][0], cap, col, (x, rect[1] + rect[3] + 14), "center")
        text(surf, names[li][1], font("mono", 16), col, (x, rect[1] + rect[3] + 38), "center")


def reason(fr):
    x, act, d = fr["x"], fr["act"], fr["dir"]
    hx, hy = fr["snake"][0]
    fx, fy = fr["food"]

    def toward(dd):
        dx, dy = ga.DIRS[dd]
        return (fx - hx) * dx + (fy - hy) * dy > 0

    if act == 0:
        if x[0] < 0.5 and toward(d):
            return "comida à frente e caminho livre → segue reto"
        return "caminho livre à frente → segue reto"
    side = ga.TURN_RIGHT[d] if act == 1 else ga.TURN_LEFT[d]
    nome = "direita" if act == 1 else "esquerda"
    if x[0] > 0.5:
        return f"obstáculo à frente → desvia para a {nome}"
    if toward(side):
        return f"comida à {nome} → vira para a {nome}"
    return f"evita encurralar → vira para a {nome}"


# ---------------- cenas ----------------
SCENES = []
import json as _json
_TIMING_PATH = os.path.join(HERE, "..", "narr", "timing.json")
TIMING = _json.load(open(_TIMING_PATH, encoding="utf-8"))["scenes"] if os.path.exists(_TIMING_PATH) else {}
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


@scene("hook", 8.0)
def s_hook(s, t):
    eyebrow(s, "// neuroevolução na prática", (140, 300), appear(t, 0.1))
    a = appear(t, 0.3, 0.6)
    y = text_lines(s, ["Uma rede neural de", "435 números aprendeu", "a jogar Snake."], font("sans-b", 76), FG,
                   (140, 350 + int((1 - a) * 24)), lh=92, alpha=a)
    b = appear(t, 1.4)
    text(s, "sem dataset · sem backprop · sem PyTorch", font("mono", 28), BODY, (140, y + 30), alpha=b)
    text(s, "só NumPy e seleção natural.", font("mono", 28), RED_SOFT, (140, y + 74), alpha=appear(t, 2.2))
    fi = min(len(EP) - 1, int(t * 12) + 200)
    c = appear(t, 0.6, 0.8)
    if c > 0:
        board = pygame.Surface((600, 600), pygame.SRCALPHA)
        draw_board(board, (10, 10, 580, 580), EP[fi], show_sensors=False)
        board.set_alpha(int(255 * c))
        s.blit(board, (1180, 240))
        text(s, f"score {EP[fi]['score']}", font("mono-md", 24), MUTE, (1470, 870), "center", alpha=c)


@scene("titulo", 4.5)
def s_title(s, t):
    a = appear(t, 0.1, 0.6)
    eyebrow(s, "// tutorial", (W // 2, 380), a, "center")
    text(s, "Neuroevolução do zero", font("sans-b", 92), FG, (W // 2, 470 + int((1 - a) * 20)), "center", a)
    text(s, "em Python", font("sans-b", 92), RED, (W // 2, 575 + int((1 - a) * 20)), "center", a)
    b = appear(t, 0.9)
    text(s, "rede neural + algoritmo genético jogando Snake", font("sans", 32), BODY, (W // 2, 680), "center", b)


CHAPTERS = ["Estrutura do projeto", "O que a cobra enxerga", "O cérebro", "Como ela aprende",
            "A função de fitness", "O treino", "Dentro da cabeça da IA", "No jogo de verdade"]


@scene("roteiro", 7.0)
def s_roadmap(s, t):
    eyebrow(s, "// o que você vai ver", (160, 180), appear(t, 0))
    for i, ch in enumerate(CHAPTERS):
        a = appear(t, 0.3 + i * 0.25)
        col, row = i // 4, i % 4
        x, y = 160 + col * 820, 280 + row * 150
        rrect(s, CARD, (x, y + int((1 - a) * 16), 760, 118), 14) if a > 0 else None
        if a > 0:
            rrect(s, LINE_A, (x, y + int((1 - a) * 16), 760, 118), 14, 1)
            text(s, f"{i + 1:02d}", font("mono-sb", 44), RED, (x + 36, y + 59 + int((1 - a) * 16)), "midleft", a)
            text(s, ch, font("sans-sb", 38), FG, (x + 130, y + 59 + int((1 - a) * 16)), "midleft", a)


TREE = [
    ("snake/", "", 0),
    ("├─ main.py", "ponto de entrada → Game().main()", 1),
    ("├─ game.py", "loop do Pygame; a cada frame pergunta a direção à IA", 1),
    ("├─ snake.py  food.py  config.py", "o jogo em si — tabuleiro 50×50", 1),
    ("├─ genetic_ai.py", "rede neural + algoritmo genético + ambiente de treino", 2),
    ("├─ train.py", "CLI de treino (retoma de onde parou)", 2),
    ("├─ best_snake.npz", "pesos do campeão — 435 números", 3),
    ("└─ best_snake_state.pkl", "a população inteira, para continuar o treino", 3),
]


@scene("estrutura", 15.0, "01 · Estrutura do projeto")
def s_tree(s, t):
    eyebrow(s, "// 01 · estrutura do projeto", (120, 130), appear(t, 0))
    card(s, (120, 190, 1680, 520), "~/dev/snake")
    for i, (name, desc, grp) in enumerate(TREE):
        a = appear(t, 0.4 + i * 0.35)
        y = 270 + i * 54
        hl = grp == 2 and t > C("hl", 5.5)
        text(s, name, font("mono-md", 28), RED_SOFT if hl else FG, (160, y), alpha=a)
        text(s, desc, font("sans", 26), BODY if not hl else FG, (780, y + 2), alpha=a)
    # fluxo
    fl = C("flow", 7.5)
    b = appear(t, fl)
    if b > 0:
        chips = ["train.py", "genetic_ai.py  ·  treina num 20×20", "best_snake.npz", "game.py  ·  joga no 50×50"]
        x = 120
        y = 790
        for i, c in enumerate(chips):
            ca = appear(t, fl + i * 0.5)
            if ca <= 0:
                break
            f = font("mono-md", 24)
            wdt = f.size(c)[0] + 44
            r = pygame.Rect(x, y, wdt, 64)
            rrect(s, TINT_A if i in (0, 3) else CARD, r, 12)
            rrect(s, TINT_BORDER_A if i in (0, 3) else LINE_A, r, 12, 1)
            text(s, c, f, FG, r.center, "center", ca)
            x += wdt
            if i < len(chips) - 1:
                text(s, "→", font("sans-b", 34), RED, (x + 28, y + 32), "center", ca)
                x += 56
        text(s, "treino e jogo são separados: o jogo só carrega os pesos salvos.", font("sans", 26), MUTE,
             (120, 890), alpha=appear(t, fl + 2.5))


@scene("sensores", 24.0, "02 · O que a cobra enxerga")
def s_state(s, t):
    eyebrow(s, "// 02 · o que a cobra enxerga", (100, 110), appear(t, 0))
    cp, cd, cc, cr = C("perigo", 4.0), C("direcao", 10.0), C("comida", 15.0), C("relativo", 20.0)
    marks = [(0, None), (cp, (41, 49)), (cd, (51, 51)), (cc, (52, 52))]
    code_block(s, (100, 160, 1030, 800), 33, 53, t, active_hl(t, marks), reveal=0.2, size=19)
    notes = [
        (C("n1", 1.5), "11 entradas, todas 0 ou 1", ["nada de pixels: só o que importa", "para decidir o próximo passo"]),
        (cp, "3 × perigo", ["tem parede ou corpo à frente,", "à direita, à esquerda?"]),
        (cd, "4 × direção atual", ["one-hot: cima, baixo,", "esquerda, direita"]),
        (cc, "4 × onde está a comida", ["esquerda/direita, acima/abaixo", "da cabeça"]),
        (cr, "relativo = portável", ["não depende do tamanho do tabuleiro"]),
    ]
    side_notes(s, t, notes, 1170, 170, 650)
    # vetor
    fr = EP[40]
    a = appear(t, 2.0)
    x = 1170
    groups = [(0, 3), (3, 7), (7, 11)]
    hl = active_hl(t, [(0, None), (cp, 0), (cd, 1), (cc, 2), (cr, None)])
    for gi, (g0, g1) in enumerate(groups):
        for k in range(g0, g1):
            on = fr["x"][k] > 0.5
            r = pygame.Rect(x, 880, 50, 56)
            lit = hl is None or hl == gi
            rrect(s, (mix(CARD, RED, 0.9) if on else CARD) if lit else mix(INK, CARD, 0.6), r, 8)
            rrect(s, LINE_A, r, 8, 1)
            text(s, "1" if on else "0", font("mono-sb", 26), (FG if on else MUTE) if lit else (60, 60, 66),
                 r.center, "center", a)
            x += 56
        x += 16
    text(s, "estado de exemplo", font("mono", 18), MUTE, (1170, 950), alpha=a)


@scene("cerebro", 22.0, "03 · O cérebro")
def s_brain(s, t):
    eyebrow(s, "// 03 · o cérebro", (100, 110), appear(t, 0))
    ci, cf, cpar, cm = C("init", 2.0), C("forward", 8.0), C("params", 16.0), C("mut", 14.0)
    marks = [(0, None), (ci, (58, 64)), (cf, (66, 70)), (cm, (78, 81))]
    code_block(s, (100, 160, 900, 530), 57, 70, t, active_hl(t, marks), reveal=0.2, size=20)
    code_block(s, (100, 710, 900, 250), 78, 81, t, active_hl(t, marks), reveal=0.8, size=20)
    hl_layer = active_hl(t, [(0, None), (ci, 1), (cf, 3), (cpar, None)])
    draw_net(s, (1000, 190, 880, 560), EP[40], live=False, alpha=appear(t, 0.8, 1.0), highlight_layer=hl_layer)
    a = appear(t, cpar)
    text(s, "11×16 + 16  +  16×12 + 12  +  12×3 + 3  =  435 parâmetros", font("mono-md", 24), FG,
         (1450, 880), "center", a)
    text(s, "sem gradiente: quem ajusta esses números é a evolução", font("sans", 26), RED_SOFT,
         (1450, 930), "center", appear(t, max(cm, cpar + 2.5)))
    notes_small = {ci: "3 camadas densas, init de He", cf: "forward = 2× ReLU + logits; argmax decide"}
    cur = None
    for k, v in notes_small.items():
        if t >= k:
            cur = v
    if cur and t < cpar:
        text(s, cur, font("sans-md", 28), FG, (1450, 900), "center")


LOOP = ["avaliar", "ranquear", "elitismo", "torneio", "crossover", "mutação"]
LOOP_SUB = ["todas jogam as mesmas partidas", "ordena pela fitness", "os 10% melhores passam intactos",
            "sorteia 4, fica o melhor", "cada peso vem de um dos pais", "ruído em 10% dos pesos"]


@scene("evolucao", 14.0, "04 · Como ela aprende")
def s_loop(s, t):
    eyebrow(s, "// 04 · como ela aprende", (100, 110), appear(t, 0))
    text(s, "Uma geração, em 6 passos", font("sans-b", 54), FG, (100, 150), alpha=appear(t, 0.2))
    text(s, "150 indivíduos por geração · repete até a cobra parar de morrer", font("sans", 28), BODY, (100, 225),
         alpha=appear(t, 0.5))
    cx, cy, R = 1340, 610, 300
    step = int(max(0, t - 1.0) / 1.6) % 6 if t > 1.0 else -1
    pygame.draw.circle(s, LINE, (cx, cy), R, 2)
    for i, name in enumerate(LOOP):
        ang = -math.pi / 2 + i * 2 * math.pi / 6
        x, y = cx + R * math.cos(ang), cy + R * math.sin(ang)
        a = appear(t, 0.5 + i * 0.15)
        on = i == step
        r = pygame.Rect(0, 0, 230, 70)
        r.center = (x, y)
        rrect(s, TINT_A if on else CARD, r, 14)
        rrect(s, RED if on else LINE_A, r, 14, 2 if on else 1)
        text(s, name, font("sans-sb", 30), FG if on else BODY, r.center, "center", a)
    if step >= 0:
        ang = -math.pi / 2 + (step + ease(((t - 1.0) % 1.6) / 1.6)) * 2 * math.pi / 6
        pygame.draw.circle(s, RED, (int(cx + R * math.cos(ang - 0.5)), int(cy + R * math.sin(ang - 0.5))), 8)
        text(s, f"{step + 1:02d}", font("mono-sb", 90), RED, (cx, cy - 40), "center")
        text(s, LOOP_SUB[step], font("sans", 28), FG, (cx, cy + 40), "center")
    lines = ["Não existe \"resposta certa\" para", "ensinar. Existe só uma nota:", "quem joga melhor, se reproduz."]
    text_lines(s, lines, font("sans-md", 36), FG, (100, 420), lh=52, alpha=appear(t, 1.5))
    text(s, "é seleção natural aplicada a pesos de rede neural.", font("sans", 28), RED_SOFT, (100, 600),
         alpha=appear(t, 3))


@scene("evolucao_codigo", 17.0, "04 · Como ela aprende")
def s_evolve_code(s, t):
    eyebrow(s, "// 04 · evolve()", (100, 110), appear(t, 0))
    ca_, ce, cfi, ccr = C("aval", 1.5), C("elite", 5.5), C("filhos", 9.5), C("cross", 13.0)
    marks = [(0, None), (ca_, (229, 233)), (ce, (242, 244)), (cfi, (246, 249))]
    code_block(s, (100, 160, 1060, 800), 227, 253, t, active_hl(t, marks), reveal=0.1, size=17)
    marks2 = [(0, None), (ccr, (280, 289))]
    code_block(s, (1200, 700, 640, 270), 280, 288, t, active_hl(t, marks2), reveal=0.5, size=15)
    notes = [
        (ca_, "avaliação justa", ["mesmas sementes para todos:", "ninguém ganha por sorte do mapa"]),
        (ce, "elitismo", ["os melhores são copiados sem mudança"]),
        (cfi, "filhos", ["torneio escolhe os pais,", "crossover mistura, mutação varia"]),
        (ccr, "crossover uniforme", ["np.where + máscara aleatória:", "50% de cada pai, peso a peso"]),
    ]
    side_notes(s, t, notes, 1200, 170, 620)


@scene("fitness", 15.0, "05 · A função de fitness")
def s_fitness(s, t):
    eyebrow(s, "// 05 · a nota de cada cobra", (100, 110), appear(t, 0))
    cco, csh, cfo, cpr = C("comer", 1.5), C("shaping", 6.0), C("fome", 10.5), C("prof", 12.5)
    marks = [(0, None), (cco, (172, 173)), (csh, (163, 166)), (cfo, (168, 170))]
    code_block(s, (100, 160, 1060, 560), 159, 173, t, active_hl(t, marks), reveal=0.1, size=19)
    notes = [
        (cco, "comer é o que mais vale", ["100 por comida + bônus quadrático:", "cobra grande vale muito mais"]),
        (csh, "reward shaping", ["+1 ao se aproximar da comida,", "−1,5 ao se afastar"]),
        (cfo, "morte por fome", ["sem comer por muito tempo = fim;", "mata as cobras que só dão voltas"]),
    ]
    side_notes(s, t, notes, 1200, 170, 620)
    text(s, "a fitness é o \"professor\": tudo o que a IA aprende vem dessa função.", font("sans-md", 30), FG,
         (100, 800), alpha=appear(t, cpr))


class VideoFeed:
    def __init__(self, start, dur, speed, crop, height):
        self.w = None
        vf = f"crop={crop},setpts=(PTS-STARTPTS)/{speed},fps={FPS},scale=-2:{height}:flags=lanczos"
        cw, ch = [int(v) for v in crop.split(":")[:2]]
        self.w = int(round(cw * height / ch / 2) * 2)
        self.h = height
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(start), "-t", str(dur), "-i",
                                   f"{PROJ}/demo/snake.mp4", "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                  stdout=subprocess.PIPE)
        self.last = None

    def frame(self):
        buf = self.p.stdout.read(self.w * self.h * 3)
        if len(buf) == self.w * self.h * 3:
            self.last = pygame.image.frombuffer(buf, (self.w, self.h), "RGB").copy()
        return self.last


_feed = {}


@scene("treino", 25.0, "06 · O treino")
def s_train(s, t):
    if "train" not in _feed:
        _feed["train"] = VideoFeed(11, 1404, 1404 / _CUR["dur"], "968:692:476:254", 700)
    img = _feed["train"].frame()
    eyebrow(s, f"// 06 · o treino — 100 gerações em {_CUR['dur']:.0f} s", (100, 110), appear(t, 0))
    x = 100
    card(s, (x, 160, img.get_width() + 40 if img else 1020, 800), "python train.py --generations 100")
    if img:
        s.blit(img, (x + 20, 230))
    notes = [
        (C("n1", 1.0), "o painel mostra as 15 melhores", ["de cada geração, das 150 que jogaram"]),
        (C("caos", 6.0), "começo: caos", ["batem na parede em poucos passos"]),
        (C("estrategia", 12.0), "meio: estratégia emergente", ["contornar as bordas surge sozinho"]),
        (C("fim", 18.0), "fim: recorde de 58 comidas", ["checkpoint a cada 10 gerações"]),
    ]
    side_notes(s, t, notes, 1170 + 20, 170, 640)


@scene("mente", 72.0, "07 · Dentro da cabeça da IA")
def s_mind(s, t):
    slow_until, slow_rate, fast_rate = C("fast", 16.0), 2.2, 11.0
    if t < slow_until:
        fi = int(t * slow_rate)
    else:
        fi = int(slow_until * slow_rate + (t - slow_until) * fast_rate)
    fi = min(fi, len(EP) - 1)
    fr = EP[fi]
    eyebrow(s, "// 07 · dentro da cabeça da IA — ao vivo", (100, 110), appear(t, 0))
    draw_board(s, (110, 200, 640, 640), fr)
    text(s, f"score {fr['score']}", font("mono-md", 26), FG, (110, 875), "topleft")
    text(s, f"passo {fi}", font("mono", 22), MUTE, (750, 878), "topright")
    draw_net(s, (820, 200, 1030, 620), fr)
    # decisão
    r = pygame.Rect(820, 880, 1030, 90)
    rrect(s, TINT_A, r, 14)
    rrect(s, TINT_BORDER_A, r, 14, 1)
    text(s, "DECISÃO", font("mono-md", 20), RED, (r.x + 28, r.y + 26), "midleft")
    text(s, OUT_LABELS[fr["act"]].lower(), font("sans-b", 34), FG, (r.x + 28, r.y + 60), "midleft")
    text(s, reason(fr), font("sans", 26), BODY, (r.right - 28, r.centery), "midright")
    if t < slow_until:
        text(s, "câmera lenta: ~2 decisões por segundo", font("mono", 20), RED_SOFT, (110, 930),
             alpha=appear(t, 0.5))
    else:
        text(s, "velocidade normal", font("mono", 20), MUTE, (110, 930))


@scene("jogo_real", 16.0, "08 · No jogo de verdade")
def s_real(s, t):
    eyebrow(s, "// 08 · plugando no jogo", (100, 110), appear(t, 0))
    cv, cmm, cg = C("conv", 1.5), C("mesmo", 7.0), C("game", 11.5)
    marks = [(0, None), (cv, (464, 471)), (cmm, (473, 474))]
    code_block(s, (100, 160, 1080, 620), 460, 474, t, active_hl(t, marks), reveal=0.1, size=22)
    notes = [
        (cv, "converte pixels em grade", ["o jogo real anda de 10 em 10 px;", "a IA pensa em células"]),
        (cmm, "mesmo build_state do treino", ["treinou em 20×20, joga em 50×50", "sem retreinar nada"]),
        (cg, "o game.py só chama decide()", ["troque a IA sem mexer no jogo"]),
    ]
    side_notes(s, t, notes, 1240, 170, 600)


@scene("rodar", 11.0, "08 · No jogo de verdade")
def s_run(s, t):
    eyebrow(s, "// como rodar", (100, 110), appear(t, 0))
    card(s, (100, 170, 1720, 560), "terminal")
    cmds = [
        ("$ ", "pip install numpy pygame", ""),
        ("$ ", "python train.py --generations 100", "# painel visual"),
        ("$ ", "python train.py --headless", "# bem mais rápido, usa todos os núcleos"),
        ("$ ", "python train.py --fresh", "# recomeça do zero"),
        ("$ ", "python main.py", "# assiste a IA jogando"),
    ]
    for i, (p, c, cm) in enumerate(cmds):
        a = appear(t, 0.4 + i * 0.7)
        y = 260 + i * 86
        text(s, p, font("mono-sb", 32), RED, (140, y), alpha=a)
        wd = text(s, c, font("mono", 32), FG, (186, y), alpha=a).right
        if cm:
            text(s, cm, font("mono", 26), MUTE, (max(wd + 40, 1020), y + 4), alpha=a)
    text(s, "multiprocessing.Pool avalia a população em paralelo; o estado salvo permite retomar.",
         font("sans", 28), BODY, (100, 790), alpha=appear(t, 4.5))


@scene("aplicacoes", 12.0)
def s_apps(s, t):
    eyebrow(s, "// e fora do jogo?", (100, 150), appear(t, 0))
    text(s, "O mesmo padrão resolve problemas reais", font("sans-b", 58), FG, (100, 200), alpha=appear(t, 0.2))
    items = [
        ("triagem", "classificar chamados e ordens de manutenção"),
        ("roteamento", "modelo pequeno antes da LLM: só o difícil vai pra API"),
        ("otimização", "algoritmo genético em escalas, rotas e sequenciamento"),
        ("decisão", "qualquer escolha repetitiva com padrão e uma nota clara"),
    ]
    for i, (b, d) in enumerate(items):
        a = appear(t, 1.0 + i * 0.6)
        y = 360 + i * 130
        if a <= 0:
            continue
        rrect(s, CARD, (100, y + int((1 - a) * 14), 1720, 104), 14)
        rrect(s, LINE_A, (100, y + int((1 - a) * 14), 1720, 104), 14, 1)
        badge(s, b.upper(), (140, y + 52 + int((1 - a) * 14)), 20, "midleft")
        text(s, d, font("sans-md", 34), FG, (440, y + 52 + int((1 - a) * 14)), "midleft", a)


@scene("outro", 7.0)
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
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    if "--still" in sys.argv:
        i = sys.argv.index("--still")
        name, t = sys.argv[i + 1], float(sys.argv[i + 2])
        sc = next(x for x in SCENES if x["name"] == name)
        if name == "treino":
            _feed["train"] = VideoFeed(11 + t * 1404 / 25, 60, 1404 / 25.0, "968:692:476:254", 700)
        pygame.image.save(compose(sc, t), os.path.join(HERE, "out", f"still_{name}_{t:g}.png"))
        print("ok")
        return
    total = sum(x["dur"] for x in SCENES)
    print(f"episódio seed={EP_SEED} score={EP_SCORE} passos={len(EP)} · duração {total:.1f}s", flush=True)
    out = os.path.join(HERE, "out", "video_silent.mp4")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                          "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    n = 0
    for sc in SCENES:
        frames = int(round(sc["dur"] * FPS))
        for k in range(frames):
            p.stdin.write(pygame.image.tobytes(compose(sc, k / FPS), "RGB"))
            n += 1
        print(f"  {sc['name']:<16} ok ({n} frames)", flush=True)
    p.stdin.close()
    p.wait()
    print("OK", out)


if __name__ == "__main__":
    main()
