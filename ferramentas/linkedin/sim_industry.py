"""Cena 1080x1080: IA triando ordens de manutenção (visual do vídeo do LinkedIn)."""
import math
import os
import random
import subprocess

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 1080
FPS = 30
DUR = 17.0
FADE = 0.4

BG = (18, 18, 28)
PANEL = (28, 28, 42)
PANEL_LINE = (48, 48, 66)
GREEN = (80, 220, 120)
MUTED = (160, 166, 200)
WHITE = (240, 240, 245)
PRIO = {"URGENTE": (229, 72, 77), "ALTA": (240, 150, 60), "MÉDIA": (225, 200, 80), "BAIXA": (140, 140, 160)}
TEAMS = ["MECÂNICA", "ELÉTRICA", "INSTRUMENTAÇÃO", "AUTOMAÇÃO"]

TICKETS = [
    ("Vazamento de óleo na prensa", "MECÂNICA", "ALTA"),
    ("Motor da esteira aquecendo", "ELÉTRICA", "ALTA"),
    ("Sensor de pressão sem leitura", "INSTRUMENTAÇÃO", "MÉDIA"),
    ("Válvula travada na linha de vapor", "MECÂNICA", "URGENTE"),
    ("CLP perdeu comunicação", "AUTOMAÇÃO", "URGENTE"),
    ("Ruído no rolamento do exaustor", "MECÂNICA", "MÉDIA"),
    ("Disjuntor desarmando no painel", "ELÉTRICA", "ALTA"),
    ("Calibrar balança da expedição", "INSTRUMENTAÇÃO", "BAIXA"),
    ("Tela da IHM travando", "AUTOMAÇÃO", "MÉDIA"),
    ("Trocar lâmpada do galpão", "ELÉTRICA", "BAIXA"),
    ("Correia do transportador solta", "MECÂNICA", "MÉDIA"),
    ("Termopar do forno oscilando", "INSTRUMENTAÇÃO", "ALTA"),
]

pygame.init()
pygame.display.set_mode((1, 1))


def F(size, bold=False):
    return pygame.font.Font(os.path.join(HERE, "segoeuib.ttf" if bold else "segoeui.ttf"), size)


F_TITLE, F_SUB, F_CAP = F(30, True), F(38, True), F(28)
F_CARD, F_TAG, F_HEAD, F_TEAM = F(20), F(14, True), F(18, True), F(19, True)


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, k):
    return a + (b - a) * k


def mixc(a, b, k):
    k = max(0.0, min(1.0, k))
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def text(s, txt, f, col, pos, anchor="topleft", alpha=1.0):
    img = f.render(txt, True, col)
    if alpha < 1:
        img.set_alpha(int(255 * max(0, alpha)))
    r = img.get_rect(**{anchor: pos})
    s.blit(img, r)
    return r


# ---------- layout ----------
INBOX = pygame.Rect(36, 230, 380, 640)
NET_C = (540, 550)
Q_X, Q_W = 666, 378
Q_Y0, Q_H, Q_GAP = 230, 148, 16
QUEUES = {t: pygame.Rect(Q_X, Q_Y0 + i * (Q_H + Q_GAP), Q_W, Q_H) for i, t in enumerate(TEAMS)}
CARD_W, CARD_H = 344, 74

# rede pequena no centro
LAYERS = [5, 6, 4]
NODES = []
for li, n in enumerate(LAYERS):
    x = NET_C[0] - 70 + li * 70
    NODES.append([(x, NET_C[1] - (n - 1) * 26 / 2 + i * 26) for i in range(n)])
EDGES = [(li, i, j) for li in range(2) for i in range(LAYERS[li]) for j in range(LAYERS[li + 1])]

# linha do tempo: chamados com texto, cada vez mais rápidos; depois uma enxurrada sem texto
events = []
t = 1.2
for i, tk in enumerate(TICKETS):
    events.append(dict(t=t, text=tk[0], team=tk[1], prio=tk[2], big=True))
    t += max(0.42, 1.25 - i * 0.09)
rng = random.Random(7)
while t < DUR - 2.2:
    team = rng.choice(TEAMS)
    prio = rng.choices(list(PRIO), weights=[1, 3, 4, 2])[0]
    events.append(dict(t=t, text=None, team=team, prio=prio, big=False))
    t += 0.11

T_IN, T_NET, T_OUT = 0.45, 0.35, 0.55  # entrada->IA, processamento, IA->fila


def card(s, cx, cy, ev, scale=1.0, alpha=1.0, show_tag=False):
    w, h = int(CARD_W * scale), int(CARD_H * scale)
    r = pygame.Rect(0, 0, w, h)
    r.center = (int(cx), int(cy))
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surf, (40, 40, 58), (0, 0, w, h), border_radius=10)
    pygame.draw.rect(surf, PRIO[ev["prio"]] if show_tag else PANEL_LINE, (0, 0, w, h), 2, border_radius=10)
    pygame.draw.rect(surf, PRIO[ev["prio"]] if show_tag else MUTED, (0, 0, 6, h), border_radius=3)
    if scale > 0.6 and ev["text"]:
        text(surf, "Ordem de manutenção", F_TAG, MUTED, (18, 10))
        text(surf, ev["text"], F_CARD, WHITE, (18, 32))
        if show_tag:
            tg = F_TAG.render(ev["prio"], True, BG)
            tr = pygame.Rect(0, 0, tg.get_width() + 14, 20)
            tr.topright = (w - 10, 8)
            pygame.draw.rect(surf, PRIO[ev["prio"]], tr, border_radius=5)
            surf.blit(tg, tg.get_rect(center=tr.center))
    surf.set_alpha(int(255 * alpha))
    s.blit(surf, r)


def queue_slot(team, k):
    q = QUEUES[team]
    per_row = 16
    row, col = divmod(k, per_row)
    return q.x + 20 + col * 22 + 8, q.y + 62 + row * 22 + 8


def draw_frame(t):
    s = pygame.Surface((W, H))
    s.fill(BG)
    # cabeçalho
    text(s, "3 · NA INDÚSTRIA", F_TITLE, GREEN, (W // 2, 70), "midtop")
    text(s, "triagem de ordens de manutenção", F_SUB, WHITE, (W // 2, 128), "midtop")
    # caixa de entrada
    pygame.draw.rect(s, PANEL, INBOX, border_radius=16)
    pygame.draw.rect(s, PANEL_LINE, INBOX, 1, border_radius=16)
    text(s, "CHAMADOS CHEGANDO", F_HEAD, MUTED, (INBOX.x + 20, INBOX.y + 16))
    # filas
    for team, q in QUEUES.items():
        pygame.draw.rect(s, PANEL, q, border_radius=14)
        pygame.draw.rect(s, PANEL_LINE, q, 1, border_radius=14)
        text(s, team, F_TEAM, WHITE, (q.x + 20, q.y + 16))
    # IA
    active = 0.0
    for ev in events:
        k = (t - (ev["t"] + T_IN - 0.15)) / (T_NET + 0.3)
        if 0 <= k <= 1:
            active = max(active, math.sin(k * math.pi))
    pulse_phase = t * 6
    for li, i, j in EDGES:
        a, b = NODES[li][i], NODES[li + 1][j]
        w = 0.25 + 0.75 * active * (0.5 + 0.5 * math.sin(pulse_phase + i * 1.7 + j * 2.3 + li))
        pygame.draw.aaline(s, mixc(BG, GREEN, w * 0.9), a, b)
    for li, layer in enumerate(NODES):
        for i, (x, y) in enumerate(layer):
            w = active * (0.5 + 0.5 * math.sin(pulse_phase + i * 2.1 + li * 1.3))
            pygame.draw.circle(s, mixc(PANEL, GREEN, w), (int(x), int(y)), 9)
            pygame.draw.circle(s, mixc(PANEL_LINE, GREEN, active), (int(x), int(y)), 9, 2)
    text(s, "IA TREINADA", F_HEAD, mixc(MUTED, GREEN, active), (NET_C[0], NET_C[1] + 100), "midtop")
    text(s, "lê · classifica · direciona", F(16), MUTED, (NET_C[0], NET_C[1] + 126), "midtop")

    # fila de espera na caixa de entrada (próximos chamados com texto)
    waiting = [ev for ev in events if ev["big"] and ev["t"] > t][:6]
    for k, ev in enumerate(waiting):
        y = INBOX.y + 90 + k * (CARD_H + 16)
        a = ease((t - (ev["t"] - 3.5)) / 0.4) if ev["t"] - t < 3.5 else (1.0 if k < 6 else 0)
        card(s, INBOX.centerx, y + CARD_H / 2, ev, 1.0, max(0.25, min(1, a)) if k else 1.0)

    if not waiting:
        off = (t * 260) % (CARD_H + 16)
        for k in range(-1, 7):
            y = INBOX.y + 90 + k * (CARD_H + 16) - off
            if y < INBOX.y + 50 or y + CARD_H > INBOX.bottom - 10:
                continue
            r = pygame.Rect(INBOX.x + 18, y, CARD_W, CARD_H)
            pygame.draw.rect(s, (40, 40, 58), r, border_radius=10)
            pygame.draw.rect(s, PANEL_LINE, r, 2, border_radius=10)
            pygame.draw.rect(s, (70, 70, 90), (r.x + 18, r.y + 16, 120, 8), border_radius=4)
            pygame.draw.rect(s, (90, 90, 112), (r.x + 18, r.y + 40, 230, 12), border_radius=6)
        text(s, "volume alto, sem fila", F(18, True), GREEN, (INBOX.centerx, INBOX.bottom - 36), "center")

    # chamados em trânsito e já roteados
    counts = {tm: 0 for tm in TEAMS}
    for ev in events:
        dt = t - ev["t"]
        if dt < 0:
            continue
        slot = counts[ev["team"]]
        counts[ev["team"]] += 1
        qx, qy = queue_slot(ev["team"], slot)
        start = (INBOX.centerx, INBOX.y + 90 + CARD_H / 2)
        if dt < T_IN:  # indo para a IA
            k = smooth(dt / T_IN)
            x, y = lerp(start[0], NET_C[0], k), lerp(start[1], NET_C[1], k)
            if ev["big"]:
                card(s, x, y, ev, lerp(1.0, 0.62, k), 1.0 - 0.5 * max(0, k - 0.6) / 0.4)
            else:
                pygame.draw.rect(s, mixc(PANEL, MUTED, 0.7), (x - 7, y - 7, 14, 14), border_radius=4)
        elif dt < T_IN + T_NET:  # dentro da IA
            pass
        elif dt < T_IN + T_NET + T_OUT:  # indo para a fila
            k = smooth((dt - T_IN - T_NET) / T_OUT)
            q = QUEUES[ev["team"]]
            mid = (q.centerx, q.centery)
            if ev["big"]:
                x, y = lerp(NET_C[0], mid[0], k), lerp(NET_C[1], mid[1], k)
                sc = lerp(0.5, 0.95, min(1, k * 1.6)) if k < 0.7 else lerp(0.95, 0.1, (k - 0.7) / 0.3)
                if k >= 0.7:
                    x, y = lerp(mid[0], qx, (k - 0.7) / 0.3), lerp(mid[1], qy, (k - 0.7) / 0.3)
                card(s, x, y, ev, sc, 1.0, show_tag=True)
            else:
                x, y = lerp(NET_C[0], qx, k), lerp(NET_C[1], qy, k)
                pygame.draw.rect(s, PRIO[ev["prio"]], (x - 8, y - 8, 16, 16), border_radius=4)
        else:  # na fila
            pygame.draw.rect(s, PRIO[ev["prio"]], (qx - 8, qy - 8, 16, 16), border_radius=4)
        # resultado da classificação acima da IA
        if ev["big"] and T_IN + 0.1 <= dt < T_IN + T_NET + T_OUT + 0.4:
            ka = min(1, (dt - T_IN - 0.1) / 0.15, (T_IN + T_NET + T_OUT + 0.4 - dt) / 0.2)
            col = PRIO[ev["prio"]]
            r1 = text(s, ev["team"], F(22, True), WHITE, (NET_C[0], NET_C[1] - 150), "midtop", ka)
            tg = F_TAG.render(ev["prio"], True, BG)
            tr = pygame.Rect(0, 0, tg.get_width() + 16, 22)
            tr.midtop = (NET_C[0], r1.bottom + 6)
            chip = pygame.Surface(tr.size, pygame.SRCALPHA)
            pygame.draw.rect(chip, col, (0, 0, *tr.size), border_radius=6)
            chip.blit(tg, tg.get_rect(center=(tr.w // 2, tr.h // 2)))
            chip.set_alpha(int(255 * ka))
            s.blit(chip, tr)

    # legenda de prioridade
    lx = 36
    for name, col in PRIO.items():
        pygame.draw.rect(s, col, (lx, 896, 16, 16), border_radius=4)
        lx += 24 + text(s, name, F(17), MUTED, (lx + 24, 904), "midleft").width + 22
    # legenda inferior
    k = ease((t - 9.5) / 0.6)
    cap1 = "Cada chamado é lido, classificado e enviado"
    cap2 = "para a equipe certa, na hora."
    if t > 9.5:
        cap1, cap2 = "Em larga escala, sem pagar uma LLM", "a cada decisão."
    a = 1.0 if t < 9.0 else (1 - ease((t - 9.0) / 0.4) if t < 9.5 else k)
    text(s, cap1, F_CAP, MUTED, (W // 2, 950), "midtop", a)
    text(s, cap2, F_CAP, MUTED, (W // 2, 986), "midtop", a)
    # fade
    f = min(1.0, t / FADE, (DUR - t) / FADE)
    if f < 1:
        veil = pygame.Surface((W, H))
        veil.fill(BG)
        veil.set_alpha(int(255 * (1 - max(0, f))))
        s.blit(veil, (0, 0))
    return s


def main():
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "--still":
        pygame.image.save(draw_frame(float(sys.argv[2])), os.path.join(HERE, f"ind_{sys.argv[2]}.png"))
        return
    out = os.path.join(HERE, "linkedin_industry.mp4")
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
