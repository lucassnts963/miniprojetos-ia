"""Cenas 1080x1080 do mapa para o vídeo do LinkedIn do projeto 02 (tema elucas.dev).

  1. "O método": rotas pelas capitais evoluindo geração após geração (o algoritmo genético da cobrinha)
     e, por cima, a melhor rota possível, com prova (método exato).
  2. "O dado certo": Brasil inteiro, rota planejada no mapa (linha reta) x planejada pela estrada,
     as duas medidas na estrada. Sem números na tela: barras de mesma escala.

    python cenas_mapa.py                # renderiza cena_metodo.mp4 e cena_estrada.mp4
    python cenas_mapa.py --still metodo 9
"""
import os
import subprocess
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import numpy as np
import pygame

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
RAIZ = os.path.dirname(PROJ)
sys.path.insert(0, PROJ)
sys.path.insert(0, os.path.join(RAIZ, "ferramentas", "youtube"))
import genetico as G  # noqa: E402
import rota as R  # noqa: E402
from exato import resolver_exato  # noqa: E402
from tema import (BODY, CARD, FG, INK, LINE_A, LINE_ON_CARD, MUTE, RED, RED_SOFT, TINT_A, TINT_BORDER_A,  # noqa: E402
                  ease, font, mix, rrect, text)

sys.stdout.reconfigure(encoding="utf-8")
W = H = 1080
FPS = 30
FADE = 0.4
CINZA = (150, 150, 162)
CACHE = os.path.join(HERE, "cache_mapa.npz")

# ---------------- dados (o modelo decide tudo; nada roteirizado) ----------------
cap, _ = R.montar_mapa("reta", capitais=True)
ib = R.achar(cap, "Belém/PA")
Dcap = G.matriz(cap)
HIST = []
G.evoluir(Dcap, ib, geracoes=600, pop_tam=150, seed=1,
          ao_fim_da_geracao=lambda g, melhor, km_: HIST.append((list(map(int, melhor)), float(km_))))
OTIMA, KM_OTIMA, _, _ = resolver_exato(Dcap, ib)
if OTIMA[0] != ib:
    OTIMA = OTIMA[::-1]
print(f"genético: {HIST[0][1]:,.0f} -> {HIST[-1][1]:,.0f} km; ótimo comprovado {KM_OTIMA:,.0f} km")

if os.path.exists(CACHE):
    c = np.load(CACHE, allow_pickle=True)
    BR_LAT, BR_LON, PLANO_RETA, PLANO_EST, KM_RE, KM_EE = (c[k] for k in ("lat", "lon", "reta", "est", "km_re", "km_ee"))
else:
    est, _ = R.montar_mapa("estrada")
    reta = R.Mapa(est.nomes, est.lat, est.lon)
    ie = R.achar(est, "Belém/PA")
    PLANO_RETA, _, _ = R.resolver(reta, ie, verboso=False, segundos=20)
    PLANO_EST, _, _ = R.resolver(est, ie, verboso=False, segundos=20)
    KM_RE, KM_EE = est.comprimento(PLANO_RETA), est.comprimento(PLANO_EST)
    BR_LAT, BR_LON = est.lat, est.lon
    np.savez(CACHE, lat=BR_LAT, lon=BR_LON, reta=np.array(PLANO_RETA), est=np.array(PLANO_EST),
             km_re=KM_RE, km_ee=KM_EE)
KM_RE, KM_EE = float(KM_RE), float(KM_EE)
print(f"Brasil na estrada: planejada no mapa {KM_RE:,.0f} km, planejada pela estrada {KM_EE:,.0f} km "
      f"({1 - KM_EE / KM_RE:.0%} a menos)")

# ---------------- desenho ----------------
BG = pygame.Surface((W, H))


def fundo():
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W * 0.5) / (W * 0.6)) ** 2 + ((yy - H * 0.48) / (H * 0.6)) ** 2)
    g = np.clip(1 - d, 0, 1) ** 2 * 0.16
    arr = np.zeros((W, H, 3))
    for i in range(3):
        arr[:, :, i] = (INK[i] + (RED[i] - INK[i]) * g).T
    pygame.surfarray.blit_array(BG, arr.astype(np.uint8))
    dot = mix(INK, (255, 255, 255), 0.11)
    for x in range(12, W, 24):
        for y in range(12, H, 24):
            pygame.draw.circle(BG, dot, (x, y), 1)


fundo()


def badge(s, txt, pos, anchor="topright", size=15, alpha=1.0):
    f = font("mono-md", size)
    tw, th = f.size(txt)
    r = pygame.Rect(0, 0, tw + 24, th + 10)
    setattr(r, anchor, pos)
    tmp = pygame.Surface(r.size, pygame.SRCALPHA)
    rrect(tmp, TINT_A, (0, 0, *r.size), 8)
    rrect(tmp, TINT_BORDER_A, (0, 0, *r.size), 8, 1)
    text(tmp, txt, f, RED_SOFT, (r.w // 2, r.h // 2), "center")
    tmp.set_alpha(int(255 * alpha))
    s.blit(tmp, r)


def moldura(s, eyebrow, titulo, capitulo):
    pygame.draw.rect(s, RED, (48, 42, 12, 12), border_radius=3)
    text(s, "elucas.dev", font("mono-sb", 22), FG, (68, 48), "midleft")
    badge(s, "LOGÍSTICA", (W - 48, 32))
    text(s, "@elucas.dev", font("mono", 18), MUTE, (48, H - 40), "midleft")
    text(s, capitulo, font("mono", 18), MUTE, (W - 48, H - 40), "midright")
    text(s, eyebrow, font("mono-md", 20), RED, (W // 2, 100), "midtop")
    text(s, titulo, font("sans-b", 42), FG, (W // 2, 130), "midtop")


def legendas(s, t, fases, dur):
    f = font("sans-md", 27)
    for i, (ini, l1, l2) in enumerate(fases):
        fim = fases[i + 1][0] if i + 1 < len(fases) else dur + 1
        if ini <= t < fim:
            a = min(ease((t - ini) / 0.5) if ini else 1.0, 1 - ease((t - (fim - 0.4)) / 0.4))
            text(s, l1, f, FG, (W // 2, 924), "midtop", a)
            text(s, l2, f, BODY, (W // 2, 962), "midtop", a)


def projecao(lat, lon, rect, pad=20):
    k = np.cos(np.radians(-15))
    lo0, lo1, la0, la1 = -74.5, -34.5, -34.0, 5.5
    esc = min((rect.w - 2 * pad) / ((lo1 - lo0) * k), (rect.h - 2 * pad) / (la1 - la0))
    ox = rect.x + (rect.w - (lo1 - lo0) * k * esc) / 2
    oy = rect.y + (rect.h - (la1 - la0) * esc) / 2
    return np.column_stack([ox + (lon - lo0) * k * esc, oy + (la1 - lat) * esc])


def base_mapa(rect, pontos, cor_ponto, tam=1):
    """Superfície com o card e os pontos das cidades (desenhada uma vez)."""
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    rrect(surf, CARD, rect, 16)
    rrect(surf, LINE_A, rect, 16, 1)
    for x, y in pontos:
        if tam <= 1:
            surf.set_at((int(x), int(y)), cor_ponto)
        else:
            pygame.draw.circle(surf, cor_ponto, (int(x), int(y)), tam)
    return surf


def linha_rota(s, pts, ordem, cor, largura=2, frac=1.0, alpha=255):
    n = max(2, int(len(ordem) * frac))
    tmp = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.lines(tmp, (*cor, alpha), False, [tuple(pts[c]) for c in ordem[:n]], largura)
    s.blit(tmp, (0, 0))


def saida(s, t, dur):
    k = min(1.0, t / FADE, (dur - t) / FADE)
    if k < 1:
        veu = pygame.Surface((W, H))
        veu.fill(INK)
        veu.set_alpha(int(255 * (1 - max(0, k))))
        s.blit(veu, (0, 0))


# ---------------- cena 1: o método ----------------
DUR_METODO = 15.0
MAPA1 = pygame.Rect(110, 232, 860, 664)
P1 = projecao(cap.lat, cap.lon, MAPA1, pad=48)
BR_TODOS = projecao(BR_LAT, BR_LON, MAPA1, pad=48)
BASE1 = base_mapa(MAPA1, BR_TODOS, (*mix(CARD, FG, 0.18), 255))
T_EVOLUI = (1.0, 8.2)
T_OTIMO = 8.8


def cena_metodo(t):
    s = BG.copy()
    moldura(s, "O MÉTODO", "Menor rota pelas capitais", "menor rota")
    s.blit(BASE1, (0, 0))
    for i, (x, y) in enumerate(P1):
        pygame.draw.circle(s, FG, (int(x), int(y)), 4)
    x0, y0 = P1[ib]
    pygame.draw.circle(s, RED_SOFT, (int(x0), int(y0)), 11, 3)
    text(s, "Belém", font("sans-sb", 18), FG, (x0 + 16, y0 - 22))
    # evolução: a melhor rota de cada geração, acelerando
    k = ease((t - T_EVOLUI[0]) / (T_EVOLUI[1] - T_EVOLUI[0]))
    g = int(min(len(HIST) - 1, (k ** 1.6) * (len(HIST) - 1)))
    ordem, km_ = HIST[g]
    a_ga = 1.0 if t < T_OTIMO else max(0.25, 1 - (t - T_OTIMO) / 0.6)
    linha_rota(s, P1, ordem, CINZA, 2, alpha=int(255 * a_ga))
    # barra "comprimento da rota" (sem números): encolhe conforme evolui
    bx, by, bw = MAPA1.x + 30, MAPA1.bottom - 34, 260
    text(s, "comprimento da rota", font("mono", 14), MUTE, (bx, by - 22))
    pygame.draw.rect(s, LINE_ON_CARD, (bx, by, bw, 8), border_radius=4)
    pygame.draw.rect(s, CINZA, (bx, by, int(bw * km_ / HIST[0][1]), 8), border_radius=4)
    if t >= T_OTIMO:
        a = ease((t - T_OTIMO) / 0.8)
        linha_rota(s, P1, OTIMA, RED, 4, frac=a)
        pygame.draw.rect(s, RED, (bx, by + 14, int(bw * KM_OTIMA / HIST[0][1]), 8), border_radius=4)
        badge(s, "MELHOR ROTA POSSÍVEL · COM PROVA", (MAPA1.centerx, MAPA1.y + 22), "midtop", 16,
              ease((t - T_OTIMO - 0.6) / 0.4))
    else:
        text(s, "gerações", font("mono", 14), MUTE, (MAPA1.right - 30, by - 22), "topright")
        pygame.draw.rect(s, LINE_ON_CARD, (MAPA1.right - 230, by, 200, 8), border_radius=4)
        pygame.draw.rect(s, RED_SOFT, (MAPA1.right - 230, by, int(200 * g / (len(HIST) - 1)) + 1, 8), border_radius=4)
    legendas(s, t, [(0, "O mesmo método que ensinou a cobrinha:", "rotas que evoluem, geração após geração."),
                    (T_OTIMO - 0.2, "Funcionou. Mas um método clássico", "achou a melhor rota possível, com prova.")],
             DUR_METODO)
    saida(s, t, DUR_METODO)
    return s


# ---------------- cena 2: o dado certo ----------------
DUR_ESTRADA = 14.0
MAPA_A = pygame.Rect(48, 250, 480, 540)
MAPA_B = pygame.Rect(552, 250, 480, 540)
PA = projecao(BR_LAT, BR_LON, MAPA_A, pad=24)
PB = projecao(BR_LAT, BR_LON, MAPA_B, pad=24)
BASE_A = base_mapa(MAPA_A, PA, (*mix(CARD, FG, 0.22), 255))
BASE_B = base_mapa(MAPA_B, PB, (*mix(CARD, FG, 0.22), 255))
T_DESENHO = (1.0, 6.0)
T_BARRAS = 6.6


def cena_estrada(t):
    s = BG.copy()
    moldura(s, "O DADO CERTO", "Linha reta ou estrada?", "menor rota")
    s.blit(BASE_A, (0, 0))
    s.blit(BASE_B, (0, 0))
    text(s, "PLANEJADA NO MAPA", font("mono-md", 16), MUTE, (MAPA_A.x, MAPA_A.y - 30))
    text(s, "PLANEJADA PELA ESTRADA", font("mono-md", 16), RED_SOFT, (MAPA_B.x, MAPA_B.y - 30))
    frac = ease((t - T_DESENHO[0]) / (T_DESENHO[1] - T_DESENHO[0]))
    if frac > 0:
        linha_rota(s, PA, list(PLANO_RETA), (205, 205, 215), 1, frac, 245)
        linha_rota(s, PB, list(PLANO_EST), RED, 1, frac, 235)
    # quilômetros rodados NA ESTRADA pelas duas rotas, mesma escala, sem números
    a = ease((t - T_BARRAS) / 0.5)
    if a > 0:
        k = ease((t - T_BARRAS) / 2.0)
        for rect, km_, cor in ((MAPA_A, KM_RE, (205, 205, 215)), (MAPA_B, KM_EE, RED)):
            y = rect.bottom + 34
            text(s, "rodando na estrada", font("mono", 14), MUTE, (rect.x, y - 22), alpha=a)
            pygame.draw.rect(s, LINE_ON_CARD, (rect.x, y, rect.w, 10), border_radius=5)
            pygame.draw.rect(s, cor, (rect.x, y, max(10, int(rect.w * km_ / KM_RE * k)), 10), border_radius=5)
    legendas(s, t, [(0, "Só que a distância no mapa", "não é a distância na estrada."),
                    (T_BARRAS + 0.4, "Planejar com o dado certo economiza", "mais que qualquer ajuste de algoritmo.")],
             DUR_ESTRADA)
    saida(s, t, DUR_ESTRADA)
    return s


CENAS = {"metodo": (cena_metodo, DUR_METODO, "cena_metodo.mp4"), "estrada": (cena_estrada, DUR_ESTRADA, "cena_estrada.mp4")}


def main():
    if len(sys.argv) > 3 and sys.argv[1] == "--still":
        fn = CENAS[sys.argv[2]][0]
        out = os.path.join(HERE, f"quadro_{sys.argv[2]}_{sys.argv[3]}.png")
        pygame.image.save(fn(float(sys.argv[3])), out)
        print("OK", out)
        return
    for nome, (fn, dur, arq) in CENAS.items():
        out = os.path.join(HERE, arq)
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                              "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "14",
                              "-pix_fmt", "yuv420p", "-r", str(FPS), "-an", out], stdin=subprocess.PIPE)
        for n in range(int(dur * FPS)):
            p.stdin.write(pygame.image.tobytes(fn(n / FPS), "RGB"))
        p.stdin.close()
        p.wait()
        print("OK", out)


if __name__ == "__main__":
    main()
