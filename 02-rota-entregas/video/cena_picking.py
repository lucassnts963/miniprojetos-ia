"""Cena 1080x1080: separação de pedidos (picking) num armazém, na ordem da lista x rota otimizada.

Mesmo pedido, mesma velocidade de caminhada, mesmo tempo parado em cada item: só muda a ordem.
A distância entre dois pontos é a caminhada real pelos corredores (busca em grade), e a ordem
otimizada é a melhor possível, com prova (o mesmo método exato do projeto 02, com volta à expedição).

    python cena_picking.py              # renderiza cena_picking.mp4
    python cena_picking.py --still 9    # um quadro em PNG para conferir
"""
import os
import random
import subprocess
import sys
from collections import deque

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import numpy as np
import pygame

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
RAIZ = os.path.dirname(PROJ)
sys.path.insert(0, PROJ)
sys.path.insert(0, os.path.join(RAIZ, "ferramentas", "youtube"))
from exato import resolver_exato  # noqa: E402
from tema import (BODY, CARD, CARD_2, FG, INK, LINE_A, LINE_ON_CARD, MUTE, RED, RED_SOFT, TINT_A,  # noqa: E402
                  TINT_BORDER_A, ease, font, mix, rrect, text)

sys.stdout.reconfigure(encoding="utf-8")
W = H = 1080
FPS = 30
DUR = 26.0
FADE = 0.4

# ---------------- o armazém (grade) ----------------
COLS, ROWS = 30, 34
RACK_COLS = [(2, 3), (6, 7), (10, 11), (14, 15), (18, 19), (22, 23), (26, 27)]  # estantes costas com costas
RACK_ROWS = [(3, 15), (19, 30)]                                                  # dois blocos, corredor no meio
EXPEDICAO = (33, 15)  # (linha, coluna) onde o separador começa e termina

livre = np.ones((ROWS, COLS), bool)
for c0, c1 in RACK_COLS:
    for r0, r1 in RACK_ROWS:
        livre[r0:r1 + 1, c0:c1 + 1] = False


def bfs(inicio):
    """Distância (em células) e caminho até cada célula andável, pelos corredores."""
    dist = np.full((ROWS, COLS), -1)
    pai = {}
    q = deque([inicio])
    dist[inicio] = 0
    while q:
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < ROWS and 0 <= cc < COLS and livre[rr, cc] and dist[rr, cc] < 0:
                dist[rr, cc] = dist[r, c] + 1
                pai[(rr, cc)] = (r, c)
                q.append((rr, cc))
    return dist, pai


def caminho(pai, inicio, fim):
    cel = [fim]
    while cel[-1] != inicio:
        cel.append(pai[cel[-1]])
    return cel[::-1]


# ---------------- o pedido ----------------
N_ITENS = 16
SEED = int(os.environ.get("PICKING_SEED", 11))  # pedido típico (entre as sementes testadas, 52 a 60% menos caminhada)
rng = random.Random(SEED)
prateleiras = [(r, c) for c0, c1 in RACK_COLS for r0, r1 in RACK_ROWS for r in range(r0, r1 + 1) for c in (c0, c1)]
itens = rng.sample(prateleiras, N_ITENS)
# onde o separador para: a célula do corredor em frente à prateleira
paradas = [(r, c - 1) if (c, c + 1) in RACK_COLS else (r, c + 1) for r, c in itens]
nos = [EXPEDICAO] + paradas
buscas = [bfs(p) for p in nos]
D = np.array([[buscas[i][0][nos[j]] for j in range(len(nos))] for i in range(len(nos))], float)

ORDEM_LISTA = [0] + list(range(1, len(nos)))            # a lista chega na ordem dos códigos dos produtos
ORDEM_OTIMA, _, _, _ = resolver_exato(D, 0, volta=True)
if ORDEM_OTIMA[0] != 0:
    ORDEM_OTIMA = ORDEM_OTIMA[::-1]


def etapas_do_calculo():
    """Ordens intermediárias do algoritmo (vizinho mais próximo, depois cada troca que melhora), para mostrar
    a rota sendo calculada na tela. Termina na ordem ótima."""
    import rota as R
    m = R.Mapa([str(i) for i in range(len(nos))], np.zeros(len(nos)), np.zeros(len(nos)), D)
    r = R.Rota(m, R.vizinho_mais_proximo(m, 0), volta=True)
    r.inicio = 0
    fotos = [list(ORDEM_LISTA), r.t.tolist()]
    olhar = np.ones(m.n, bool)
    mudou = True
    while mudou:
        mudou = False
        for c in range(m.n):
            olhar[c] = False
            if r.dois_opt(c, olhar) or r.or_opt(c, olhar):
                fotos.append(r.t.tolist())
                mudou = True
    fotos.append([int(x) for x in ORDEM_OTIMA])
    return fotos


ETAPAS = etapas_do_calculo()


def percurso(ordem):
    """Células visitadas (volta à expedição) e em que ponto do percurso cada item é coletado."""
    cel, marcos = [nos[ordem[0]]], []
    seq = list(ordem) + [ordem[0]]
    for a, b in zip(seq, seq[1:]):
        trecho = caminho(buscas[a][1], nos[a], nos[b])
        cel += trecho[1:]
        if b != 0:
            marcos.append((len(cel) - 1, b))
    return cel, marcos


CEL_A, MARCOS_A = percurso(ORDEM_LISTA)
CEL_B, MARCOS_B = percurso(ORDEM_OTIMA)
LEN_A, LEN_B = len(CEL_A) - 1, len(CEL_B) - 1
print(f"caminhada na ordem da lista: {LEN_A} células; otimizada: {LEN_B} ({1 - LEN_B / LEN_A:.0%} a menos)")

# ---------------- tempo ----------------
T_CALC = (2.6, 4.6)     # o algoritmo calcula a ordem (painel otimizado)
T_INICIO = 5.0          # os dois saem juntos
PARADA = 0.35           # segundos parado em cada item (igual para os dois)
T_FIM_A = 20.0          # quando o da lista termina: define a velocidade (a mesma para os dois)
VEL = LEN_A / (T_FIM_A - T_INICIO - PARADA * N_ITENS)  # células por segundo


def linha_do_tempo(cel, marcos):
    """Tempo em que o separador chega em cada célula do percurso (com as paradas nos itens)."""
    tempos = np.zeros(len(cel))
    parada_em = {k for k, _ in marcos}
    t = T_INICIO
    for k in range(1, len(cel)):
        t += 1 / VEL
        tempos[k] = t
        if k in parada_em:
            t += PARADA
    return tempos


TEMPOS_A = linha_do_tempo(CEL_A, MARCOS_A)
TEMPOS_B = linha_do_tempo(CEL_B, MARCOS_B)
T_FIM_B = TEMPOS_B[-1]

# ---------------- desenho ----------------
CELULA = 15
PAINEIS = [pygame.Rect(66, 252, COLS * CELULA, ROWS * CELULA), pygame.Rect(564, 252, COLS * CELULA, ROWS * CELULA)]
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


def badge(s, txt, pos, anchor="topright"):
    f = font("mono-md", 15)
    tw, th = f.size(txt)
    r = pygame.Rect(0, 0, tw + 24, th + 10)
    setattr(r, anchor, pos)
    rrect(s, TINT_A, r, 8)
    rrect(s, TINT_BORDER_A, r, 8, 1)
    text(s, txt, f, RED_SOFT, r.center, "center")


def xy(painel, cel):
    r, c = cel
    return painel.x + c * CELULA + CELULA / 2, painel.y + r * CELULA + CELULA / 2


def posicao(cel, tempos, t):
    """Posição (linha, coluna) interpolada no tempo t."""
    if t <= tempos[0]:
        return cel[0], 0
    if t >= tempos[-1]:
        return cel[-1], len(cel) - 1
    k = int(np.searchsorted(tempos, t) - 1)
    k = max(0, min(k, len(cel) - 2))
    dt = tempos[k + 1] - tempos[k]
    f = min(1.0, (t - tempos[k]) * VEL) if dt > 0 else 1.0
    (r0, c0), (r1, c1) = cel[k], cel[k + 1]
    return (r0 + (r1 - r0) * f, c0 + (c1 - c0) * f), k + f


def armazem(s, painel, titulo, cel, tempos, marcos, cor, t, destaque):
    card_r = painel.inflate(24, 24)
    rrect(s, CARD, card_r, 16)
    rrect(s, (*RED, 110) if destaque else LINE_A, card_r, 16, 2 if destaque else 1)
    text(s, titulo, font("mono-md", 16), RED_SOFT if destaque else MUTE, (painel.x, painel.y - 42))
    # estantes
    for c0, c1 in RACK_COLS:
        for r0, r1 in RACK_ROWS:
            rr = pygame.Rect(painel.x + c0 * CELULA + 1, painel.y + r0 * CELULA + 1, 2 * CELULA - 2, (r1 - r0 + 1) * CELULA - 2)
            rrect(s, CARD_2, rr, 3)
            rrect(s, LINE_A, rr, 3, 1)
            for r in range(r0 + 1, r1 + 1):
                y = painel.y + r * CELULA
                pygame.draw.line(s, LINE_ON_CARD, (rr.x + 2, y), (rr.right - 3, y), 1)
    # expedição
    ex = pygame.Rect(painel.x + 12 * CELULA, painel.y + (ROWS - 1) * CELULA, 6 * CELULA, CELULA)
    rrect(s, (*FG, 30), ex, 4)
    text(s, "EXPEDIÇÃO", font("mono-md", 11), MUTE, (ex.centerx, ex.y - 2), "midbottom")
    # itens do pedido: acendem no começo, apagam quando coletados
    _, prog = posicao(cel, tempos, t)
    coletado = {b for k, b in marcos if prog >= k}
    for i, (r, c) in enumerate(itens):
        a = ease((t - 0.8 - i * 0.12) / 0.3)
        if a <= 0:
            continue
        x, y = painel.x + c * CELULA + 2, painel.y + r * CELULA + 2
        feito = (i + 1) in coletado
        cor_item = mix(CARD_2, (95, 95, 105), a) if feito else mix(CARD_2, RED, a)
        pygame.draw.rect(s, cor_item, (x, y, CELULA - 4, CELULA - 4), border_radius=3)
        if feito:
            pygame.draw.lines(s, FG, False, [(x + 3, y + 7), (x + 6, y + 10), (x + 11, y + 3)], 2)
    # rota planejada: no painel otimizado, primeiro o algoritmo calculando (trechos se descruzando)
    plano = cel
    if destaque and t < T_INICIO:
        if t < T_CALC[0]:
            plano = None
        else:
            k_etapa = min(len(ETAPAS) - 1, int((t - T_CALC[0]) / (T_CALC[1] - T_CALC[0]) * len(ETAPAS)))
            plano, _ = percurso(ETAPAS[k_etapa])
            if T_CALC[0] <= t < T_CALC[1]:
                text(s, "calculando a melhor ordem...", font("mono-md", 15), RED_SOFT,
                     (painel.centerx, painel.y + 17 * CELULA + CELULA // 2), "center")
    if plano is not None and t > 1.6:
        a_plano = ease((t - 1.6) / 0.5) * (0.55 if t < T_INICIO else 0.3)
        tmp = pygame.Surface((W, H), pygame.SRCALPHA)
        pts = [xy(painel, c_) for c_ in plano]
        for k in range(0, len(pts) - 1, 2):  # tracejado
            pygame.draw.line(tmp, (*cor, int(255 * a_plano)), pts[k], pts[k + 1], 2)
        s.blit(tmp, (0, 0))
    # rastro e separador
    k_fim = int(prog)
    if k_fim >= 1:
        pts = [xy(painel, c_) for c_ in cel[:k_fim + 1]]
        (pr, pc), _ = posicao(cel, tempos, t)
        pts.append((painel.x + pc * CELULA + CELULA / 2, painel.y + pr * CELULA + CELULA / 2))
        pygame.draw.lines(s, mix(CARD, cor, 0.8), False, pts, 3)
    (pr, pc), _ = posicao(cel, tempos, t)
    px, py = painel.x + pc * CELULA + CELULA / 2, painel.y + pr * CELULA + CELULA / 2
    halo = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(halo, (*cor, 60), (20, 20), 18)
    s.blit(halo, (px - 20, py - 20))
    pygame.draw.circle(s, cor, (int(px), int(py)), 8)
    pygame.draw.circle(s, INK, (int(px), int(py)), 3)
    # pronto
    if t >= tempos[-1]:
        a = ease((t - tempos[-1]) / 0.4)
        f = font("sans-b", 22)
        tw = f.size("PEDIDO SEPARADO")[0]
        r = pygame.Rect(0, 0, tw + 36, 48)
        r.center = (painel.centerx, painel.y + 17 * CELULA + CELULA // 2)
        tmp = pygame.Surface(r.size, pygame.SRCALPHA)
        rrect(tmp, (*(RED if destaque else (95, 95, 105)), 235), (0, 0, *r.size), 10)
        text(tmp, "PEDIDO SEPARADO", f, (255, 255, 255), (r.w // 2, r.h // 2), "center")
        tmp.set_alpha(int(255 * a))
        s.blit(tmp, r)
    return prog, len(coletado)


def rodape_painel(s, painel, prog, n_col, cor, t):
    """Itens coletados (pontos) e caminhada (barra, na mesma escala para os dois). Sem números."""
    y = painel.bottom + 26
    for i in range(N_ITENS):
        cx = painel.x + 8 + i * 22
        if i < n_col:
            pygame.draw.circle(s, cor, (cx, y), 6)
        else:
            pygame.draw.circle(s, LINE_ON_CARD, (cx, y), 6, 2)
    text(s, "itens", font("mono", 13), MUTE, (painel.right, y), "midright")
    yb = y + 22
    larg = painel.w - 70
    pygame.draw.rect(s, LINE_ON_CARD, (painel.x, yb, larg, 8), border_radius=4)
    w_ = int(larg * min(1.0, prog / LEN_A))
    if w_ > 0:
        pygame.draw.rect(s, cor, (painel.x, yb, max(8, w_), 8), border_radius=4)
    text(s, "caminhada", font("mono", 13), MUTE, (painel.right, yb + 4), "midright")


LEGENDAS = [
    (0.0, "Um pedido, vários itens espalhados", "pelas prateleiras."),
    (T_CALC[0] - 0.2, "O algoritmo calcula a melhor ordem", "antes de o separador sair."),
    (T_INICIO + 0.6, "Mesmo pedido, mesma velocidade.", "Só muda a ordem."),
    (T_FIM_B + 0.3, "Menos caminhada,", "pedido pronto antes."),
    (T_FIM_A + 1.6, "Nem tudo precisa de IA.", "A sua imaginação é o limite."),
]


def quadro(t):
    s = BG.copy()
    pygame.draw.rect(s, RED, (48, 42, 12, 12), border_radius=3)
    text(s, "elucas.dev", font("mono-sb", 22), FG, (68, 48), "midleft")
    badge(s, "LOGÍSTICA", (W - 48, 32))
    text(s, "@elucas.dev", font("mono", 18), MUTE, (48, H - 40), "midleft")
    text(s, "rota de separação", font("mono", 18), MUTE, (W - 48, H - 40), "midright")
    text(s, "NA PRÁTICA", font("mono-md", 20), RED, (W // 2, 100), "midtop")
    text(s, "Separação de pedidos no armazém", font("sans-b", 42), FG, (W // 2, 130), "midtop")

    pa, na = armazem(s, PAINEIS[0], "NA ORDEM DA LISTA", CEL_A, TEMPOS_A, MARCOS_A, (150, 150, 162), t, False)
    pb, nb = armazem(s, PAINEIS[1], "ROTA OTIMIZADA", CEL_B, TEMPOS_B, MARCOS_B, RED, t, True)
    rodape_painel(s, PAINEIS[0], pa, na, (150, 150, 162), t)
    rodape_painel(s, PAINEIS[1], pb, nb, RED, t)

    f1, f2 = font("sans-md", 27), font("sans-md", 27)
    for i, (ini, l1, l2) in enumerate(LEGENDAS):
        fim = LEGENDAS[i + 1][0] if i + 1 < len(LEGENDAS) else DUR + 1
        if ini <= t < fim:
            a = min(ease((t - ini) / 0.5) if ini else 1.0, 1 - ease((t - (fim - 0.4)) / 0.4))
            text(s, l1, f1, FG, (W // 2, 924), "midtop", a)
            text(s, l2, f2, BODY, (W // 2, 962), "midtop", a)

    k = min(1.0, t / FADE, (DUR - t) / FADE)
    if k < 1:
        veu = pygame.Surface((W, H))
        veu.fill(INK)
        veu.set_alpha(int(255 * (1 - max(0, k))))
        s.blit(veu, (0, 0))
    return s


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--still":
        out = os.path.join(HERE, f"quadro_{sys.argv[2]}.png")
        pygame.image.save(quadro(float(sys.argv[2])), out)
        print("OK", out)
        return
    out = os.path.join(HERE, "cena_picking.mp4")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "14",
                          "-pix_fmt", "yuv420p", "-r", str(FPS), "-an", out], stdin=subprocess.PIPE)
    for n in range(int(DUR * FPS)):
        p.stdin.write(pygame.image.tobytes(quadro(n / FPS), "RGB"))
    p.stdin.close()
    p.wait()
    print("OK", out)


if __name__ == "__main__":
    main()
