"""Vídeo do post da base de conhecimento viva (LLM Wiki), 1080x1080, animado.

Roteiro: documentos soltos (e-mail, anotação, ata...) -> cada um é aprovado e vira uma página ligada às
outras -> a rede cresce -> alguém pergunta no chat -> a IA percorre as páginas ligadas -> resposta com a fonte.
O conteúdo (bomba, selo mecânico) é fictício, só para a demonstração.

    ferramentas/venv-video/Scripts/python.exe posts/video_llm_wiki.py            # -> carrossel_llm_wiki/video.mp4
    ferramentas/venv-video/Scripts/python.exe posts/video_llm_wiki.py --still 30 # um quadro em PNG
"""
import math
import os
import subprocess
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
PASTA = os.path.join(AQUI, "carrossel_llm_wiki")
sys.path.insert(0, os.path.join(RAIZ, "ferramentas", "youtube"))
sys.path.insert(0, os.path.join(RAIZ, "ferramentas", "musica"))
from tema import BODY, CARD, CARD_2, FG, INK, MUTE, RED, RED_SOFT, ease, font, mix, rrect, text  # noqa: E402

W = H = 1080
FPS = 30
DUR = 47.5
VERDE = (88, 214, 141)
CINZA = (74, 74, 84)

# ---------------- tempos ----------------
T_DOCS = 3.6          # documentos soltos aparecem
T_ENTRA = 10.6        # começam a passar pela aprovação
PASSO = 1.4           # intervalo entre um documento e o seguinte
T_CRESCE = 20.4       # o resto da rede aparece
T_CHAT = 25.0
T_PERGUNTA = (25.8, 27.6)
T_BUSCA = 28.3
SALTO = 0.95
T_RESPOSTA = (33.3, 37.3)
T_FIM = 42.6          # fechamento

# ---------------- a rede ----------------
NOS = [("índice", 540, 262), ("bomba", 300, 338), ("manutenções", 480, 428), ("parada anterior", 700, 366),
       ("selo mecânico", 868, 476), ("pendências", 648, 540), ("procedimento", 168, 474), ("fornecedor", 952, 338),
       ("contrato", 790, 246), ("equipe", 322, 540), ("ata", 150, 276), ("estoque", 490, 566)]
ARESTAS = [(0, 1), (0, 3), (0, 8), (1, 2), (1, 6), (1, 10), (2, 3), (2, 5), (2, 9), (3, 4), (3, 7), (4, 5), (4, 7),
           (5, 11), (9, 11), (6, 9), (8, 7)]
CAMINHO = [0, 1, 2, 3, 4, 5]                      # por onde a IA passa para responder
PERGUNTA = "Por que a bomba parou de novo?"
RESPOSTA = ["Foi o selo mecânico. Ele já tinha falhado na", "parada anterior e a troca ficou pendente."]
FONTES = ["relatório da parada", "e-mail da manutenção"]

# documentos soltos: (tipo, x, y, ângulo, nó em que vira página)
DOCS = [("e-mail", 250, 420, -9, 2), ("anotação", 560, 360, 7, 5), ("ata", 850, 430, -6, 10),
        ("relatório", 330, 720, 8, 3), ("foto", 620, 690, -11, 4), ("planilha", 880, 740, 6, 11)]
BANDEJA = (740, 770)
FILA = (120, 800)       # onde os documentos esperam a vez, empilhados


def nasce(i):
    """Momento em que o nó i aparece na rede."""
    for k, d in enumerate(DOCS):
        if d[4] == i:
            return T_ENTRA + k * PASSO + 1.35
    resto = [n for n in range(len(NOS)) if n not in [d[4] for d in DOCS]]
    return T_CRESCE + resto.index(i) * 0.4


NASCE = [nasce(i) for i in range(len(NOS))]


# ---------------- desenho dos documentos ----------------
def base_doc(tipo):
    w, h = 210, 262
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    if tipo == "anotação":                         # papel amarelo
        pygame.draw.rect(s, (236, 205, 104), (0, 0, w, h), border_radius=8)
        pygame.draw.polygon(s, (205, 172, 78), [(w - 38, h), (w, h - 38), (w, h)])
        text(s, tipo, font("mono-md", 20), (92, 72, 20), (20, 18))
        for i, fr in enumerate((0.82, 0.6, 0.74, 0.46)):
            pygame.draw.line(s, (120, 96, 34), (20, 76 + i * 38), (20 + (w - 40) * fr, 76 + i * 38 + (i % 2) * 3), 4)
        return s
    pygame.draw.rect(s, CARD_2, (0, 0, w, h), border_radius=14)
    pygame.draw.rect(s, (78, 78, 88), (0, 0, w, h), 2, border_radius=14)
    text(s, tipo, font("mono-md", 20), RED_SOFT, (20, 18))
    linhas = lambda y0, fracs: [pygame.draw.rect(s, CINZA, (20, y0 + i * 28, (w - 40) * f, 9), border_radius=4)  # noqa: E731
                                for i, f in enumerate(fracs)]
    if tipo == "e-mail":
        pygame.draw.rect(s, (60, 60, 70), (20, 58, 54, 38), border_radius=6)
        pygame.draw.lines(s, FG, False, [(22, 61), (47, 80), (72, 61)], 3)
        pygame.draw.rect(s, CINZA, (86, 64, 96, 9), border_radius=4)
        pygame.draw.rect(s, CINZA, (86, 82, 64, 9), border_radius=4)
        linhas(122, (0.9, 0.7, 0.8, 0.5))
    elif tipo == "ata":
        linhas(62, (0.85, 0.65, 0.78, 0.55))
        pygame.draw.lines(s, RED_SOFT, False, [(24, 222), (48, 204), (66, 224), (88, 206), (120, 220)], 3)
    elif tipo == "relatório":
        linhas(62, (0.8, 0.6))
        for i, v in enumerate((46, 78, 58, 96)):
            pygame.draw.rect(s, RED if i == 3 else CINZA, (28 + i * 42, 228 - v, 28, v), border_radius=4)
    elif tipo == "foto":
        pygame.draw.rect(s, (48, 52, 62), (20, 60, w - 40, 138), border_radius=8)
        pygame.draw.polygon(s, (96, 104, 122), [(34, 190), (86, 112), (128, 190)])
        pygame.draw.polygon(s, (120, 128, 148), [(96, 190), (146, 132), (186, 190)])
        pygame.draw.circle(s, (236, 205, 104), (158, 92), 14)
        linhas(214, (0.6,))
    elif tipo == "planilha":
        for i in range(6):
            pygame.draw.line(s, CINZA, (20, 64 + i * 34), (w - 20, 64 + i * 34), 2)
        for i in range(4):
            x = 20 + i * (w - 40) / 3
            pygame.draw.line(s, CINZA, (x, 64), (x, 234), 2)
        pygame.draw.rect(s, RED + (90,), (20 + (w - 40) / 3 + 2, 132 + 2, (w - 40) / 3 - 3, 31))
    return s


BASES = {d[0]: base_doc(d[0]) for d in DOCS}


def carimbar(s, pos, r, k):
    """Visto verde de aprovado (k de 0 a 1)."""
    if k <= 0:
        return
    rr = int(r * (1.5 - 0.5 * ease(k)))
    halo = pygame.Surface((rr * 2 + 8, rr * 2 + 8), pygame.SRCALPHA)
    pygame.draw.circle(halo, INK + (int(215 * min(1, k * 2)),), (rr + 4, rr + 4), rr)
    pygame.draw.circle(halo, VERDE + (int(255 * min(1, k * 2)),), (rr + 4, rr + 4), rr, 5)
    c = rr + 4
    pygame.draw.lines(halo, VERDE + (int(255 * min(1, k * 2)),), False,
                      [(c - rr * 0.42, c + 2), (c - rr * 0.1, c + rr * 0.34), (c + rr * 0.46, c - rr * 0.32)], 8)
    s.blit(halo, (pos[0] - c, pos[1] - c))


def no(s, i, t, quente):
    """Uma página da wiki. quente (0 a 1): quanto a IA já passou por ela."""
    nome, x, y = NOS[i]
    k = ease((t - NASCE[i]) / 0.45)
    if k <= 0:
        return
    w, h = int(74 * (0.6 + 0.4 * k)), int(54 * (0.6 + 0.4 * k))
    if quente > 0:
        g = pygame.Surface((180, 180), pygame.SRCALPHA)
        for r, a in ((84, 18), (62, 30), (46, 44)):
            pygame.draw.circle(g, RED + (int(a * quente),), (90, 90), r)
        s.blit(g, (x - 90, y - 90))
    quadro = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(quadro, CARD_2, (0, 0, w, h), border_radius=10)
    pygame.draw.rect(quadro, mix((92, 92, 104), RED, quente), (0, 0, w, h), 3 if quente else 2, border_radius=10)
    for j, fr in enumerate((0.7, 0.5, 0.62)):
        pygame.draw.rect(quadro, mix(CINZA, RED_SOFT, quente if j == 0 else 0), (11, 12 + j * 13, (w - 22) * fr, 6),
                         border_radius=3)
    quadro.set_alpha(int(255 * k))
    s.blit(quadro, (x - w // 2, y - h // 2))
    f = font("mono", 17)
    lw = f.size(nome)[0]
    rrect(s, INK + (int(215 * k),), (x - lw // 2 - 6, y + 32, lw + 12, 24), 6)      # o nome não briga com as linhas
    text(s, nome, f, mix(MUTE, FG, quente), (x, y + 34), "midtop", k)


def linha_alpha(s, a, b, cor, larg, alpha=1.0):
    if alpha <= 0:
        return
    x0, y0, x1, y1 = min(a[0], b[0]) - 8, min(a[1], b[1]) - 8, max(a[0], b[0]) + 8, max(a[1], b[1]) + 8
    tmp = pygame.Surface((int(x1 - x0), int(y1 - y0)), pygame.SRCALPHA)
    pygame.draw.line(tmp, cor + (int(255 * alpha),), (a[0] - x0, a[1] - y0), (b[0] - x0, b[1] - y0), larg)
    s.blit(tmp, (x0, y0))


def bolha(s, rect, cor, borda, alpha):
    if alpha <= 0:
        return
    tmp = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    pygame.draw.rect(tmp, cor, (0, 0, rect[2], rect[3]), border_radius=20)
    pygame.draw.rect(tmp, borda, (0, 0, rect[2], rect[3]), 2, border_radius=20)
    tmp.set_alpha(int(255 * alpha))
    s.blit(tmp, rect[:2])


def digitar(texto_, t, ini, fim):
    return texto_[:int(len(texto_) * max(0.0, min(1.0, (t - ini) / (fim - ini))))]


def janela(t, ini, fim, d=0.45):
    """1 entre ini e fim, com entrada e saída suaves."""
    return max(0.0, min(ease((t - ini) / d), 1 - ease((t - (fim - d)) / d)))


FUNDO = pygame.Surface((W, H))
FUNDO.fill(INK)
for gx in range(18, W, 36):
    for gy in range(18, H, 36):
        FUNDO.set_at((gx, gy), (34, 34, 40))

CABECAS = [(T_DOCS, T_ENTRA, "O PROBLEMA", "O conhecimento está espalhado"),
           (T_ENTRA, T_CHAT, "O MÉTODO", "A IA organiza. Você aprova."),
           (T_CHAT, T_FIM, "NA PRÁTICA", "Pergunte como a um colega")]
LEGENDAS = [(T_DOCS + 0.6, T_ENTRA, "E-mails, anotações, atas, relatórios, fotos.", "Cada um num canto."),
            (T_ENTRA, T_CRESCE, "Cada documento novo passa por você,", "e a IA resume e liga ao que já existia."),
            (T_CRESCE, T_CHAT, "O conhecimento se acumula.", "Nada se perde quando alguém sai."),
            (T_CHAT, T_RESPOSTA[0], "A pergunta é feita em linguagem comum.", "A IA percorre as páginas ligadas."),
            (T_RESPOSTA[0], T_FIM, "A resposta vem com a fonte.", "Dá para conferir de onde saiu.")]


def quadro(t):
    s = FUNDO.copy()
    pygame.draw.circle(s, RED, (66, 62), 8)
    text(s, "elucas.dev", font("sans-sb", 24), FG, (86, 62), "midleft")

    # ----- abertura -----
    a = janela(t, 0.2, T_DOCS, 0.5)
    if a > 0:
        text(s, "BASE DE CONHECIMENTO VIVA", font("mono-md", 22), RED_SOFT, (W // 2, 400), "midtop", a)
        for i, l in enumerate(("Onde está o conhecimento", "da sua empresa?")):
            text(s, l, font("sans-b", 68), FG, (W // 2, 446 + i * 80), "midtop", a)

    # ----- cabeçalho e legenda de cada parte -----
    for ini, fim, olho, tit in CABECAS:
        a = janela(t, ini, fim)
        if a > 0:
            text(s, olho, font("mono-md", 21), RED_SOFT, (W // 2, 112), "midtop", a)
            text(s, tit, font("sans-b", 46), FG, (W // 2, 142), "midtop", a)
    for ini, fim, l1, l2 in LEGENDAS:
        a = janela(t, ini, fim, 0.4)
        if a > 0:
            text(s, l1, font("sans-md", 30), FG, (W // 2, 944), "midtop", a)
            text(s, l2, font("sans-md", 30), BODY, (W // 2, 986), "midtop", a)

    meio = janela(t, T_DOCS, T_FIM, 0.5)                      # tudo o que fica entre a abertura e o fechamento
    if meio > 0:
        camada = pygame.Surface((W, H), pygame.SRCALPHA)

        # ----- a rede -----
        if t > T_ENTRA:
            passo_busca = (t - T_BUSCA) / SALTO                # em que salto a IA está
            for a_, b_ in ARESTAS:
                k = ease((t - max(NASCE[a_], NASCE[b_]) - 0.25) / 0.5)
                if k <= 0:
                    continue
                pa, pb = NOS[a_][1:], NOS[b_][1:]
                fim_l = (pa[0] + (pb[0] - pa[0]) * k, pa[1] + (pb[1] - pa[1]) * k)
                no_caminho = any({a_, b_} == {CAMINHO[j], CAMINHO[j + 1]} and passo_busca >= j + 1
                                 for j in range(len(CAMINHO) - 1))
                linha_alpha(camada, pa, fim_l, RED if no_caminho else (84, 84, 96), 4 if no_caminho else 2)
            for i in range(len(NOS)):
                quente = 0.0
                if i in CAMINHO and t > T_BUSCA:
                    quente = ease((passo_busca - CAMINHO.index(i)) / 0.35 + 0.2)
                no(camada, i, t, quente)
            j = int(passo_busca) if passo_busca >= 0 else -1    # o pulso que anda pelas ligações
            if 0 <= j < len(CAMINHO) - 1:
                k = ease(passo_busca - j)
                pa, pb = NOS[CAMINHO[j]][1:], NOS[CAMINHO[j + 1]][1:]
                px, py = pa[0] + (pb[0] - pa[0]) * k, pa[1] + (pb[1] - pa[1]) * k
                g = pygame.Surface((80, 80), pygame.SRCALPHA)
                pygame.draw.circle(g, RED + (70,), (40, 40), 26)
                pygame.draw.circle(g, (255, 220, 220), (40, 40), 9)
                camada.blit(g, (px - 40, py - 40))

        # ----- documentos soltos e a aprovação -----
        bandeja = janela(t, T_ENTRA - 0.3, T_ENTRA + len(DOCS) * PASSO + 0.4)
        if bandeja > 0:
            rrect(camada, CARD + (int(255 * bandeja),), (BANDEJA[0] - 190, BANDEJA[1] - 160, 380, 320), 22)
            rrect(camada, (78, 78, 88, int(255 * bandeja)), (BANDEJA[0] - 190, BANDEJA[1] - 160, 380, 320), 22, 2)
            text(camada, "ENTRADA · AGUARDA APROVAÇÃO", font("mono-md", 17), MUTE, (BANDEJA[0], BANDEJA[1] - 142),
                 "midtop", bandeja)
        for k, (tipo, x, y, ang, alvo) in enumerate(DOCS):
            surge = ease((t - (T_DOCS + 0.3 + k * 0.5)) / 0.5)
            if surge <= 0:
                continue
            ini = T_ENTRA + k * PASSO
            vai = ease((t - ini) / 0.5)                         # do canto para a bandeja
            sobe = ease((t - ini - 0.95) / 0.45)                # da bandeja para a rede
            if sobe >= 1:
                continue
            fila = ease((t - (T_ENTRA - 0.7)) / 0.6)            # antes da vez, espera numa pilha à esquerda
            flutua = math.sin(t * 1.3 + k * 1.7) * 7 * (1 - fila)
            x, y = x + (FILA[0] + k * 62 - x) * fila, y + flutua + (FILA[1] - y) * fila
            cx = x + (BANDEJA[0] - x) * vai
            cy = y + (BANDEJA[1] + 6 - y) * vai
            escala = (0.55 + 0.45 * surge) * (1 - 0.5 * fila) * (1 + 0.64 * vai)
            if sobe > 0:
                cx += (NOS[alvo][1] - cx) * sobe
                cy += (NOS[alvo][2] - cy) * sobe
                escala *= 1 - 0.72 * sobe
            # os que ainda esperam ficam apagados enquanto outro está na bandeja
            folha = pygame.transform.rotozoom(BASES[tipo], ang * (1 - vai), escala)
            folha.set_alpha(int(255 * surge * (1 - 0.5 * sobe)))
            camada.blit(folha, folha.get_rect(center=(cx, cy)))
            if vai >= 1:
                carimbar(camada, (cx + 62 * (1 - sobe), cy + 70 * (1 - sobe)), 40 * (1 - 0.6 * sobe),
                         (t - ini - 0.5) / 0.3)

        # ----- o chat -----
        chat = ease((t - T_CHAT) / 0.6)
        if chat > 0:
            y0 = 640 + (1 - chat) * 40
            rrect(camada, CARD + (int(255 * chat),), (70, y0, 940, 276), 24)
            rrect(camada, (64, 64, 74, int(255 * chat)), (70, y0, 940, 276), 24, 2)
            perg = digitar(PERGUNTA, t, *T_PERGUNTA)
            if perg:
                f = font("sans-md", 28)
                larg = f.size(PERGUNTA)[0] + 48
                bolha(camada, (1010 - 26 - larg, y0 + 22, larg, 58), (70, 30, 34), (150, 56, 60), 1)
                text(camada, perg, f, FG, (1010 - 26 - larg + 24, y0 + 51), "midleft")
            if t > T_PERGUNTA[1] + 0.3:
                pygame.draw.circle(camada, RED, (116, y0 + 126), 18)
                text(camada, "IA", font("sans-b", 17), INK, (116, y0 + 126), "center")
                if t < T_RESPOSTA[0]:                           # percorrendo a wiki
                    j = max(0, min(len(CAMINHO) - 1, int((t - T_BUSCA) / SALTO + 0.5)))
                    onde = NOS[CAMINHO[j]][0] if t >= T_BUSCA else "…"
                    pontos = "." * (1 + int(t * 3) % 3)
                    text(camada, f"consultando a base{pontos}", font("sans", 27), BODY, (150, y0 + 112), "midleft")
                    text(camada, f"página: {onde}", font("mono", 20), RED_SOFT, (150, y0 + 146), "midleft")
                else:
                    resto = sum(len(l) for l in RESPOSTA)
                    n = int(resto * min(1.0, (t - T_RESPOSTA[0]) / (T_RESPOSTA[1] - T_RESPOSTA[0])))
                    for i, l in enumerate(RESPOSTA):
                        text(camada, l[:max(0, n)], font("sans-md", 28), FG, (150, y0 + 112 + i * 40), "midleft")
                        n -= len(l)
                    x = 150
                    for i, fonte_ in enumerate(FONTES):
                        a = ease((t - T_RESPOSTA[1] - 0.2 - i * 0.35) / 0.4)
                        rot = "fonte: " + fonte_
                        larg = font("mono", 19).size(rot)[0] + 28
                        if a > 0:
                            bolha(camada, (x, y0 + 204, larg, 40), (34, 44, 38), (60, 130, 90), a)
                            text(camada, rot, font("mono", 19), VERDE, (x + 14, y0 + 224), "midleft", a)
                        x += larg + 14
        camada.set_alpha(int(255 * meio))
        s.blit(camada, (0, 0))

    # ----- fechamento -----
    a = ease((t - T_FIM - 0.3) / 0.6)
    if a > 0:
        text(s, "As aplicações são inúmeras.", font("sans-md", 34), BODY, (W // 2, 400), "midtop", a)
        for i, l in enumerate(("A sua imaginação", "é o limite.")):
            text(s, l, font("sans-b", 76), FG, (W // 2, 462 + i * 88), "midtop", a)
        text(s, "@elucas.dev", font("mono", 24), MUTE, (W // 2, 690), "midtop", a)

    k = min(1.0, t / 0.4, (DUR - t) / 0.5)
    if k < 1:
        veu = pygame.Surface((W, H))
        veu.fill(INK)
        veu.set_alpha(int(255 * (1 - max(0, k))))
        s.blit(veu, (0, 0))
    return s


def main():
    os.makedirs(PASTA, exist_ok=True)
    if len(sys.argv) > 2 and sys.argv[1] == "--still":
        out = os.path.join(PASTA, f"_quadro_{sys.argv[2]}.png")
        pygame.image.save(quadro(float(sys.argv[2])), out)
        print("OK", out)
        return
    import trilha
    out = os.path.join(PASTA, "video.mp4")
    p = subprocess.Popen([trilha.FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
                          "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", out], stdin=subprocess.PIPE)
    for n in range(int(DUR * FPS)):
        p.stdin.write(pygame.image.tobytes(quadro(n / FPS), "RGB"))
    p.stdin.close()
    p.wait()
    trilha.colocar(out)


if __name__ == "__main__":
    main()
