"""Vídeo do LinkedIn (1080x1080): "De onde veio a IA que escreve?" — a máquina de completar texto.

Roteiro: o teclado do celular -> apostar no próximo pedaço (contando) -> escolher e apostar de novo ->
contagem perde o fio, a rede olha o texto inteiro -> uma LLM é isso em escala -> na prática -> fechamento.
As apostas e os textos gerados vêm do modelo treinado (video/dados.json, feito por preparar.py).

    ../ferramentas/venv-video/Scripts/python.exe video/cena_linkedin.py            # -> video/linkedin_completar.mp4
    ../ferramentas/venv-video/Scripts/python.exe video/cena_linkedin.py --still 18 # um quadro em PNG
"""
import json
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

with open(os.path.join(AQUI, "dados.json"), encoding="utf-8") as f:
    D = json.load(f)

W = H = 1080
FPS = 30
VERDE = (88, 214, 141)

# ---------------- tempos ----------------
T1, T2, T3, T4, T5, T6, DUR = 5.0, 14.5, 26.0, 36.0, 43.5, 53.0, 58.0
PASSO = 0.72                                    # segundos por pedaço gerado
N_PASSOS = min(13, len(D["passos"]))


def janela(t, ini, fim, d=0.45):
    return max(0.0, min(ease((t - ini) / d), 1 - ease((t - (fim - d)) / d)))


def chip(s, txt, pos, f, cor=FG, fundo=CARD_2, borda=(78, 78, 88), alpha=1.0, anchor="topleft", pad=(16, 9)):
    if alpha <= 0:
        return pygame.Rect(pos, (0, 0))
    w, h = f.size(txt)
    r = pygame.Rect(0, 0, w + 2 * pad[0], h + 2 * pad[1])
    setattr(r, anchor, pos)
    tmp = pygame.Surface(r.size, pygame.SRCALPHA)
    pygame.draw.rect(tmp, fundo, tmp.get_rect(), border_radius=12)
    pygame.draw.rect(tmp, borda, tmp.get_rect(), 2, border_radius=12)
    tmp.blit(f.render(txt, True, cor), pad)
    tmp.set_alpha(int(255 * alpha))
    s.blit(tmp, r)
    return r


def frase_em_pedacos(s, pedacos, x, y, largura, f, n_meus, alpha=1.0, destaque=None, entra=None):
    """Escreve os pedaços como blocos, quebrando linha. Devolve a posição logo depois do último.

    n_meus: quantos são do começo dado (cinza); os outros são da máquina (vermelho).
    destaque: índices com contorno verde (o que a máquina está olhando). entra: (índice, k) do pedaço que está surgindo.
    """
    cx, cy, alt = x, y, f.get_height() + 14
    for i, p in enumerate(pedacos):
        limpo = p.replace("\n", " ")
        w = f.size(limpo)[0]
        if cx + w > x + largura and cx > x:
            cx, cy = x, cy + alt + 10
            limpo = limpo.lstrip()
            w = f.size(limpo)[0]
        a = alpha
        if entra and entra[0] == i:
            a *= entra[1]
        elif entra and i > entra[0]:
            break
        if a > 0:
            fundo = (255, 255, 255, 20) if i < n_meus else RED + (70,)
            tmp = pygame.Surface((w + 6, alt), pygame.SRCALPHA)
            pygame.draw.rect(tmp, fundo, (0, 0, w + 4, alt), border_radius=7)
            if destaque is not None and i in destaque:
                pygame.draw.rect(tmp, VERDE, (0, 0, w + 4, alt), 3, border_radius=7)
            tmp.blit(f.render(limpo, True, FG), (2, 7))
            tmp.set_alpha(int(255 * a))
            s.blit(tmp, (cx, cy))
        cx += w + 8
    return cx, cy


def barras(s, apostas, x, y, largura, t0, t, escolhido=None, alpha=1.0, n=5):
    """Barras das apostas (sem números na tela). escolhido: pedaço que foi sorteado."""
    maior = max(a["p"] for a in apostas[:n])
    for i, a in enumerate(apostas[:n]):
        k = ease((t - t0 - i * 0.07) / 0.35) * alpha
        if k <= 0:
            continue
        yy = y + i * 62
        on = escolhido is not None and a["pedaco"] == escolhido
        nome = a["pedaco"].strip() or "espaço"
        text(s, nome, font("mono-md", 30), FG if on else BODY, (x + 250, yy + 22), "midright", k)
        rrect(s, (255, 255, 255, int(18 * k)), (x + 274, yy + 8, largura - 274, 28), 14)
        w = max(28, (largura - 274) * a["p"] / maior * k)
        rrect(s, (RED if on else (120, 70, 74)) + (int(255 * k),), (x + 274, yy + 8, w, 28), 14)


FUNDO = pygame.Surface((W, H))
FUNDO.fill(INK)
for gx in range(18, W, 36):
    for gy in range(18, H, 36):
        FUNDO.set_at((gx, gy), (34, 34, 40))

CABECAS = [(T1, T2, "A IDEIA", "Apostar no próximo pedaço"),
           (T2, T3, "O TRUQUE", "Escolha um. Aposte de novo."),
           (T3, T4, "O SALTO", "Olhar o texto inteiro"),
           (T4, T5, "A ESCALA", "Uma LLM é isso, em tamanho gigante"),
           (T5, T6, "NA PRÁTICA", "Ela continua o que você começa")]
LEGENDAS = [(0.8, T1, "Você já usa uma versão simples disso:", "o teclado do celular."),
            (T1, T1 + 4.6, "Dado um começo, qual pedaço", "de texto vem depois?"),
            (T1 + 4.6, T2, "O primeiro jeito: ler muito texto", "e contar o que costuma vir depois."),
            (T2, T3, "A máquina escolhe um pedaço,", "cola no texto e aposta outra vez."),
            (T3, T3 + 5.0, "Só contando, ela enxerga os últimos", "pedaços e perde o fio da conversa."),
            (T3 + 5.0, T4, "A rede neural pesa o texto inteiro", "e mantém o assunto."),
            (T4, T5, "Resumir, traduzir, responder, programar:", "tudo é continuar um texto."),
            (T5, T6, "Diga o papel, o contexto e o formato.", "Começo claro, continuação certeira.")]


def leque(s, origem, n, abertura, comprimento, cor, k, semente):
    """Feixe de continuações possíveis saindo do fim do pedido."""
    for i in range(n):
        ang = (i / (n - 1) - 0.5) * abertura + math.sin(semente + i * 1.7) * abertura * 0.06
        comp = comprimento * (0.75 + 0.25 * math.sin(semente * 2 + i)) * k
        fim = (origem[0] + math.cos(ang) * comp, origem[1] + math.sin(ang) * comp)
        pygame.draw.aaline(s, cor, origem, fim)
        pygame.draw.circle(s, cor, (int(fim[0]), int(fim[1])), 5)


def quadro(t):
    s = FUNDO.copy()
    pygame.draw.circle(s, RED, (66, 62), 8)
    text(s, "elucas.dev", font("sans-sb", 24), FG, (86, 62), "midleft")
    text(s, "COMO UMA LLM FUNCIONA · PARTE 1", font("mono", 19), MUTE, (W - 60, 62), "midright")

    for ini, fim, olho, tit in CABECAS:
        a = janela(t, ini, fim)
        if a > 0:
            text(s, olho, font("mono-md", 21), RED_SOFT, (W // 2, 118), "midtop", a)
            text(s, tit, font("sans-b", 46), FG, (W // 2, 148), "midtop", a)
    for ini, fim, l1, l2 in LEGENDAS:
        a = janela(t, ini, fim, 0.4)
        if a > 0:
            text(s, l1, font("sans-md", 31), FG, (W // 2, 930), "midtop", a)
            text(s, l2, font("sans-md", 31), BODY, (W // 2, 974), "midtop", a)

    # ----- 0 · abertura: o teclado do celular -----
    a = janela(t, 0.2, T1, 0.5)
    if a > 0:
        text(s, "De onde veio", font("sans-b", 70), FG, (W // 2, 190), "midtop", a)
        text(s, "a IA que escreve?", font("sans-b", 70), FG, (W // 2, 272), "midtop", a)
        k = ease((t - 1.3) / 0.6) * a
        rrect(s, CARD + (int(255 * k),), (240, 470, 600, 330), 34)
        rrect(s, (70, 70, 80, int(255 * k)), (240, 470, 600, 330), 34, 2)
        digitado = "Bom"[:max(0, int((t - 1.9) / 0.22))]
        rrect(s, (255, 255, 255, int(16 * k)), (276, 506, 528, 78), 18)
        text(s, digitado + ("|" if int(t * 2) % 2 == 0 else ""), font("sans-md", 38), FG, (300, 545), "midleft", k)
        for i, palavra in enumerate(("dia", "trabalho", "descanso")):
            kk = ease((t - 2.8 - i * 0.2) / 0.4) * a
            chip(s, palavra, (340 + i * 200, 650), font("sans-md", 30), alpha=kk, anchor="center",
                 fundo=(70, 30, 34) if i == 0 else CARD_2, borda=RED if i == 0 else (78, 78, 88))
        text(s, "sugestões do teclado", font("mono", 19), MUTE, (W // 2, 740), "midtop", ease((t - 3.2) / 0.4) * a)

    # ----- 1 · a ideia: apostar no próximo pedaço, contando -----
    a = janela(t, T1, T2)
    if a > 0:
        f = font("sans-md", 44)
        cx, cy = frase_em_pedacos(s, D["pedacos"], 110, 300, 860, f, len(D["pedacos"]), a)
        if int(t * 2) % 2 == 0:                                        # o espaço a preencher
            rrect(s, RED + (int(200 * a),), (cx + 4, cy + 8, 120, f.get_height() - 2), 8, 3)
        text(s, "?", font("sans-b", 40), RED_SOFT, (cx + 64, cy + 34), "center", a)
        k = janela(t, T1 + 4.6, T2 + 1) * a
        if k > 0:
            text(s, "O QUE VEIO DEPOIS, NOS TEXTOS LIDOS", font("mono-md", 19), MUTE, (130, 490), "topleft", k)
            barras(s, D["contagem"], 130, 530, 820, T1 + 4.9, t, alpha=k)

    # ----- 2 · escolher e apostar de novo -----
    a = janela(t, T2, T3)
    if a > 0:
        passo = (t - T2 - 0.9) / PASSO
        j = max(0, min(N_PASSOS - 1, int(passo)))
        dentro = passo - int(passo) if 0 <= passo < N_PASSOS else (0 if passo < 0 else 1)
        feitos = max(0, min(N_PASSOS, int(passo) + (1 if dentro > 0.55 else 0)))
        pedacos = D["pedacos"] + [p["pedaco"] for p in D["passos"][:feitos]]
        entra = (len(pedacos) - 1, ease((dentro - 0.55) / 0.25)) if feitos and passo < N_PASSOS and dentro > 0.55 else None
        frase_em_pedacos(s, pedacos, 110, 250, 860, font("sans-md", 38), len(D["pedacos"]), a, entra=entra)
        text(s, "AS APOSTAS DA REDE PARA O PRÓXIMO PEDAÇO", font("mono-md", 19), MUTE, (130, 540), "topleft", a)
        atual = D["passos"][j]
        barras(s, atual["apostas"], 130, 580, 820, T2 + 0.9 + j * PASSO - 0.2, t,
               escolhido=atual["pedaco"] if dentro > 0.4 or passo >= N_PASSOS else None, alpha=a)

    # ----- 3 · contagem x rede -----
    a = janela(t, T3, T4)
    if a > 0:
        f = font("sans-md", 27)
        base = D["compara_pedacos"]
        for i, (nome, chave, y0, ini) in enumerate((("SÓ CONTAGEM", "compara_contagem", 240, T3 + 0.6),
                                                    ("REDE NEURAL", "compara_rede", 580, T3 + 5.2))):
            k = ease((t - ini + 0.4) / 0.5) * a
            if k <= 0:
                continue
            rrect(s, CARD + (int(255 * k),), (70, y0, 940, 310), 22)
            rrect(s, ((78, 78, 88) if i == 0 else RED) + (int(255 * k),), (70, y0, 940, 310), 22, 2)
            text(s, nome, font("mono-md", 20), MUTE if i == 0 else RED_SOFT, (100, y0 + 22), "topleft", k)
            n = max(0, min(len(D[chave]), int((t - ini) / 0.13)))
            pedacos = base + D[chave][:n]
            vistos = set(range(len(pedacos) - 3, len(pedacos))) if i == 0 else set(range(len(pedacos)))
            text(s, "enxerga só os últimos pedaços" if i == 0 else "enxerga tudo o que já foi escrito",
                 font("mono", 18), VERDE, (980, y0 + 24), "topright", k)
            frase_em_pedacos(s, pedacos, 100, y0 + 64, 880, f, len(base), k, destaque=vistos)

    # ----- 4 · a escala -----
    a = janela(t, T4, T5)
    if a > 0:
        k = ease((t - T4 - 0.5) / 0.6) * a
        rrect(s, CARD + (int(255 * k),), (90, 350, 300, 300), 22)
        for i in range(36):                                            # a rede do vídeo: pequena
            pygame.draw.circle(s, mix(INK, RED_SOFT, k), (150 + (i % 6) * 36, 410 + (i // 6) * 36), 7)
        text(s, "a deste vídeo", font("sans-sb", 28), FG, (240, 730), "midtop", k)
        text(s, "treinada num computador comum", font("sans", 22), BODY, (240, 770), "midtop", k)
        cresce = ease((t - T4 - 2.0) / 2.4) * a
        if cresce > 0:
            lado = 300 + 130 * cresce
            x0, y0 = 760 - lado / 2, 500 - lado / 2
            rrect(s, CARD + (int(255 * a),), (x0, y0, lado, lado), 22)
            passo_ = 15
            for gx in range(int(x0 + 14), int(x0 + lado - 8), passo_):
                for gy in range(int(y0 + 14), int(y0 + lado - 8), passo_):
                    pygame.draw.circle(s, mix(INK, RED, 0.35 + 0.65 * abs(math.sin(gx * 0.31 + gy * 0.17 + t * 1.5))), (gx, gy), 3)
            text(s, "as grandes", font("sans-sb", 28), FG, (760, 730), "midtop", cresce)
            text(s, "leram uma parte enorme da internet", font("sans", 22), BODY, (760, 770), "midtop", cresce)
        text(s, "a mesma tarefa", font("mono-md", 20), MUTE, (W // 2, 850), "midtop", ease((t - T4 - 3.4) / 0.5) * a)

    # ----- 5 · na prática -----
    a = janela(t, T5, T6)
    if a > 0:
        for i, (pedido, rot, y0, ini, abertura, cor) in enumerate((
                ("Faça um relatório.", "PEDIDO VAGO: QUALQUER CONTINUAÇÃO SERVE", 250, T5 + 0.5, 1.1, (150, 150, 162)),
                ("", "COMEÇO CLARO: POUCAS CONTINUAÇÕES POSSÍVEIS", 570, T5 + 4.2, 0.22, VERDE))):
            k = ease((t - ini) / 0.5) * a
            if k <= 0:
                continue
            text(s, rot, font("mono-md", 19), MUTE if i == 0 else VERDE, (80, y0), "topleft", k)
            rrect(s, CARD + (int(255 * k),), (80, y0 + 34, 560, 250 if i else 100), 20)
            rrect(s, (78, 78, 88, int(255 * k)), (80, y0 + 34, 560, 250 if i else 100), 20, 2)
            if i == 0:
                text(s, pedido, font("sans-md", 32), FG, (108, y0 + 84), "midleft", k)
                origem = (650, y0 + 84)
            else:
                for n_, (rotulo, valor) in enumerate((("papel", "Você é planejador de manutenção."),
                                                      ("contexto", "Estas são as paradas do mês."),
                                                      ("formato", "Resuma em tópicos, para a diretoria."))):
                    kk = ease((t - ini - 0.4 - n_ * 0.6) / 0.4) * a
                    text(s, rotulo, font("mono-md", 18), RED_SOFT, (108, y0 + 56 + n_ * 74), "topleft", kk)
                    text(s, valor, font("sans-md", 27), FG, (108, y0 + 80 + n_ * 74), "topleft", kk)
                origem = (650, y0 + 159)
            kl = ease((t - ini - (0.6 if i == 0 else 2.3)) / 0.8)
            if kl > 0:
                leque(s, origem, 13 if i == 0 else 5, abertura, 250, mix(INK, cor, a), kl, i * 3.1)

    # ----- 6 · fechamento -----
    a = ease((t - T6 - 0.3) / 0.6)
    if a > 0:
        text(s, "Quem entende como funciona, pede melhor.", font("sans-md", 34), BODY, (W // 2, 390), "midtop", a)
        for i, l in enumerate(("A sua imaginação", "é o limite.")):
            text(s, l, font("sans-b", 76), FG, (W // 2, 456 + i * 88), "midtop", a)
        text(s, "@elucas.dev", font("mono", 24), MUTE, (W // 2, 690), "midtop", a)

    k = min(1.0, t / 0.4, (DUR - t) / 0.5)
    if k < 1:
        veu = pygame.Surface((W, H))
        veu.fill(INK)
        veu.set_alpha(int(255 * (1 - max(0, k))))
        s.blit(veu, (0, 0))
    return s


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--still":
        out = os.path.join(AQUI, f"quadro_{sys.argv[2]}.png")
        pygame.image.save(quadro(float(sys.argv[2])), out)
        print("OK", out)
        return
    import trilha
    out = os.path.join(AQUI, "linkedin_completar.mp4")
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
