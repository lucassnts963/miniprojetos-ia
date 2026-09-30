"""Tema elucas.dev para os vídeos do YouTube (1920x1080, Pygame).

Extraído de render.py (vídeo da cobrinha) para ser reaproveitado pelos miniprojetos:
cores, fontes IBM Plex, cards, selos, fundo com grade de pontos, moldura e bloco de código
com destaque de sintaxe e linhas destacadas.
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import numpy as np  # noqa: E402
import pygame  # noqa: E402
from pygments.lexers import PythonLexer  # noqa: E402
from pygments.token import Token  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1920, 1080, 30

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


LINE = mix(INK, (255, 255, 255), 0.09)
LINE_ON_CARD = mix(CARD, (255, 255, 255), 0.09)
CARD_2 = mix(CARD, (255, 255, 255), 0.04)

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
        _fonts[key] = pygame.font.Font(os.path.join(AQUI, "fonts", files[kind] + ".ttf"), size)
    return _fonts[key]


# ---------------- animação ----------------
def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def appear(t, start, dur=0.5):
    return ease((t - start) / dur)


def lerp(a, b, k):
    return a + (b - a) * k


# ---------------- desenho ----------------
def text(surf, s, f, color, pos, anchor="topleft", alpha=1.0):
    img = f.render(s, True, color)
    if alpha < 1:
        img.set_alpha(int(255 * max(0, alpha)))
    r = img.get_rect(**{anchor: pos})
    surf.blit(img, r)
    return r


def rrect(surf, color, rect, radius=14, width=0):
    if len(color) == 4:
        tmp = pygame.Surface((max(1, int(rect[2])), max(1, int(rect[3]))), pygame.SRCALPHA)
        pygame.draw.rect(tmp, color, (0, 0, int(rect[2]), int(rect[3])), width, border_radius=radius)
        surf.blit(tmp, (rect[0], rect[1]))
    else:
        pygame.draw.rect(surf, color, rect, width, border_radius=radius)


def card(surf, rect, title=None, radius=16):
    rrect(surf, CARD, rect, radius)
    rrect(surf, LINE_A, rect, radius, 1)
    if title is not None:
        x, y, w, _ = rect
        for i in range(3):
            pygame.draw.circle(surf, (70, 70, 76), (x + 26 + i * 20, y + 24), 6)
        text(surf, title, font("mono", 20), MUTE, (x + 96, y + 24), "midleft")
        pygame.draw.line(surf, LINE_ON_CARD, (x, y + 48), (x + w - 1, y + 48))


def badge(surf, s, pos, size=18, anchor="topleft", alpha=1.0):
    f = font("mono-md", size)
    tw, th = f.size(s)
    r = pygame.Rect(0, 0, tw + 28, th + 12)
    setattr(r, anchor, pos)
    tmp = pygame.Surface(r.size, pygame.SRCALPHA)
    rrect(tmp, TINT_A, (0, 0, *r.size), 8)
    rrect(tmp, TINT_BORDER_A, (0, 0, *r.size), 8, 1)
    text(tmp, s, f, RED_SOFT, (r.w // 2, r.h // 2), "center")
    tmp.set_alpha(int(255 * max(0, alpha)))
    surf.blit(tmp, r)
    return r


def eyebrow(surf, s, pos, alpha=1.0, anchor="topleft"):
    return text(surf, s, font("mono-md", 22), RED, pos, anchor, alpha)


def titulo(surf, t, eyebrow_txt, titulo_txt, y=110):
    """Cabeçalho padrão de cena: '// passo N' em vermelho + título grande."""
    eyebrow(surf, eyebrow_txt, (100, y), appear(t, 0))
    text(surf, titulo_txt, font("sans-b", 50), FG, (100, y + 32), alpha=appear(t, 0.15))


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


def chrome(surf, chapter=None, selo="IA · PYTHON"):
    pygame.draw.rect(surf, RED, (64, 44, 12, 12), border_radius=3)
    text(surf, "elucas.dev", font("mono-sb", 24), FG, (88, 50), "midleft")
    if selo:
        badge(surf, selo, (W - 64, 34), 16, "topright")
    text(surf, "@elucas.dev", font("mono", 20), MUTE, (64, H - 44), "midleft")
    if chapter:
        text(surf, chapter, font("mono", 20), MUTE, (W - 64, H - 44), "midright")


# ---------------- código ----------------
KW = {"def", "class", "return", "if", "else", "elif", "for", "in", "while", "not", "and", "or", "import",
      "from", "as", "None", "True", "False", "lambda", "with", "try", "finally", "break", "is"}
LEX = PythonLexer()


def tok_color(ttype, val):
    if ttype in Token.Comment:
        return MUTE
    if ttype in Token.Literal.String or ttype in Token.Literal.Number:
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


def code_block(surf, rect, src_lines, first, last, t, hl=None, title="", size=21, reveal=0.0):
    """Desenha src_lines[first..last] (1-indexado, com os números reais do arquivo).

    hl = (a, b): linhas destacadas; as outras ficam apagadas. reveal: quando as linhas aparecem.
    """
    card(surf, rect, title)
    x0, y0 = rect[0] + 20, rect[1] + 66
    f = font("mono", size)
    lh = int(size * 1.5)
    surf.set_clip(pygame.Rect(rect[0], rect[1] + 50, rect[2] - 14, rect[3] - 56))
    for i, ln in enumerate(src_lines[first - 1:last]):
        n = first + i
        vis = appear(t, reveal + i * 0.03, 0.3) if reveal is not None else 1
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
        for ttype, val in LEX.get_tokens(ln):
            if val == "\n":
                continue
            img = f.render(val, True, mix(CARD, tok_color(ttype, val), dim))
            img.set_alpha(int(255 * vis))
            surf.blit(img, (x, y))
            x += img.get_width()
            if x > rect[0] + rect[2] - 20:
                break
    surf.set_clip(None)


def active_hl(t, marks):
    """marks = [(t, (linha_a, linha_b)), ...] -> o destaque vigente no tempo t."""
    cur = None
    for ts, rng in marks:
        if t >= ts:
            cur = rng
    return cur


def chip(surf, s, pos, f=None, fg=FG, bg=CARD_2, borda=LINE_A, alpha=1.0, anchor="topleft", pad=(12, 6)):
    f = f or font("mono", 20)
    tw, th = f.size(s)
    r = pygame.Rect(0, 0, tw + pad[0] * 2, th + pad[1] * 2)
    setattr(r, anchor, pos)
    tmp = pygame.Surface(r.size, pygame.SRCALPHA)
    rrect(tmp, (*bg, 255) if len(bg) == 3 else bg, (0, 0, *r.size), 8)
    rrect(tmp, borda if len(borda) == 4 else (*borda, 255), (0, 0, *r.size), 8, 1)
    text(tmp, s, f, fg, (r.w // 2, r.h // 2), "center")
    tmp.set_alpha(int(255 * max(0, alpha)))
    surf.blit(tmp, r)
    return r


def barra_h(surf, x, y, w, h, v, cor=RED, fundo=None, alpha=1.0):
    """Barra horizontal com valor 0..1."""
    fundo = fundo or LINE_ON_CARD
    tmp = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(tmp, (*fundo, 255), (0, 0, w, h), border_radius=h // 2)
    if v > 0:
        pygame.draw.rect(tmp, (*cor, 255), (0, 0, max(h, int(w * min(1, v))), h), border_radius=h // 2)
    tmp.set_alpha(int(255 * max(0, alpha)))
    surf.blit(tmp, (x, y))
