"""Motor de cenas dos vídeos do YouTube (1920x1080), em cima do tema elucas.dev (tema.py).

Um vídeo é uma lista de cenas. Cada cena é uma função (superfície, t) com uma duração padrão;
quando existe narr/timing.json (gerado por ferramentas/narracao/pipeline.py), a duração e os
cues passam a seguir a fala.

    v = Video(pasta_do_video, fonte="caminho/do/tutorial.py")

    @v.cena("hook", 10.0)
    def hook(s, t): ...

    @v.cena("passo1", 20.0, "passo 1 · os dados")
    def passo1(s, t):
        titulo(s, t, "// passo 1", "Os dados")
        v.codigo(s, t, *v.faixa(1), [(0, None), (v.C("csv", 2.0), ("def carregar", "return"))])

    v.main()      # python render.py | --still cena t | --lista
"""
import json
import os
import subprocess
import sys

import pygame

from tema import BACKDROP, FPS, H, W, active_hl, chrome, code_block, ease, font, lerp

TOP, BOTTOM = 236, 990
FADE = 0.35


class Video:
    def __init__(self, pasta, fonte=None, selo="IA · PYTHON"):
        self.pasta = pasta
        self.selo = selo
        self.cenas = []
        self._cur = {"cues": {}, "dur": 0}
        caminho = os.path.join(pasta, "narr", "timing.json")
        self.timing = {}
        if os.path.exists(caminho):
            with open(caminho, encoding="utf-8") as f:
                self.timing = json.load(f)["scenes"]
        self.fonte_nome, self.src = "", []
        if fonte:
            self.fonte_nome = os.path.basename(fonte)
            with open(fonte, encoding="utf-8") as f:
                self.src = f.read().split("\n")

    # ---------- cenas e tempos ----------
    def cena(self, nome, dur, capitulo=None):
        def deco(fn):
            tm = self.timing.get(nome, {})
            self.cenas.append(dict(name=nome, dur=tm.get("dur", dur), fn=fn, chapter=capitulo, cues=tm.get("cues", {})))
            return fn
        return deco

    def C(self, nome, padrao):
        """Momento (s) em que a narração diz a frase ligada a este cue; senão o padrão."""
        return self._cur["cues"].get(nome, padrao)

    @property
    def dur(self):
        return self._cur["dur"]

    # ---------- código ----------
    def L(self, trecho, apos=1):
        """Número (1-indexado) da primeira linha da fonte, a partir de `apos`, que contém o trecho."""
        for i in range(apos - 1, len(self.src)):
            if trecho in self.src[i]:
                return i + 1
        raise ValueError(f"trecho não encontrado em {self.fonte_nome}: {trecho!r}")

    def faixa(self, n):
        """Linhas do PASSO n (do cabeçalho até antes do próximo passo)."""
        a = self.L(f"PASSO {n} ·")
        try:
            b = self.L(f"PASSO {n + 1} ·") - 1
        except ValueError:
            b = len(self.src)
        while not self.src[b - 1].strip():
            b -= 1
        return a, b

    def codigo(self, s, t, first, last, marks, x=100, w=1010, min_size=19):
        """Bloco de código com destaque pelos cues. marks = [(t, None | (trecho_inicio, trecho_fim))].

        Os trechos viram números de linha (o render não quebra quando a fonte muda). A fonte encolhe
        até min_size; se ainda não couber em altura, a janela rola até o trecho destacado.
        """
        res = [(ts, None if r is None else (self.L(r[0], first), self.L(r[1], self.L(r[0], first)))) for ts, r in marks]
        maior = max(len(ln) for ln in self.src[first - 1:last])
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
                return int(max(first, min(last - n_vis + 1, (h[0] + h[1]) / 2 - n_vis / 2)))
            atual = [i for i, (ts, _) in enumerate(res) if t >= ts]
            k_i = atual[-1] if atual else 0
            antes = inicio(res[k_i - 1][1]) if k_i > 0 else first
            a = int(round(lerp(antes, inicio(res[k_i][1]), ease((t - res[k_i][0]) / 0.7))))
        code_block(s, (x, TOP, w, BOTTOM - TOP), self.src, a, min(last, a + n_vis - 1), t, hl, self.fonte_nome, size,
                   reveal=0.1)

    # ---------- render ----------
    def compor(self, sc, t):
        frame = BACKDROP.copy()
        conteudo = pygame.Surface((W, H), pygame.SRCALPHA)
        self._cur["cues"], self._cur["dur"] = sc["cues"], sc["dur"]
        sc["fn"](conteudo, t)
        k = min(1.0, t / FADE, (sc["dur"] - t) / FADE)
        if k < 1:
            conteudo.set_alpha(int(255 * max(0, k)))
        frame.blit(conteudo, (0, 0))
        chrome(frame, sc["chapter"], self.selo)
        return frame

    def main(self):
        out_dir = os.path.join(self.pasta, "out")
        os.makedirs(out_dir, exist_ok=True)
        if "--lista" in sys.argv:
            t0 = 0.0
            for sc in self.cenas:
                m, s_ = divmod(t0, 60)
                print(f"{int(m)}:{int(s_):02d}  {sc['name']:<12} {sc['dur']:5.1f}s  {sc['chapter'] or ''}")
                t0 += sc["dur"]
            print(f"total {t0 / 60:.1f} min")
            return
        if "--still" in sys.argv:
            i = sys.argv.index("--still")
            nome, t = sys.argv[i + 1], float(sys.argv[i + 2])
            sc = next(x for x in self.cenas if x["name"] == nome)
            caminho = os.path.join(out_dir, f"still_{nome}_{t:g}.png")
            pygame.image.save(self.compor(sc, t), caminho)
            print("ok", caminho)
            return
        print(f"duração {sum(x['dur'] for x in self.cenas):.1f}s", flush=True)
        out = os.path.join(out_dir, "video_silent.mp4")
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                              "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                              "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        n = 0
        for sc in self.cenas:
            for k in range(int(round(sc["dur"] * FPS))):
                p.stdin.write(pygame.image.tobytes(self.compor(sc, k / FPS), "RGB"))
                n += 1
            print(f"  {sc['name']:<12} ok ({n} frames)", flush=True)
        p.stdin.close()
        p.wait()
        print("OK", out)
