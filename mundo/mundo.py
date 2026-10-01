"""Mundo 2D visto de cima, com física simples, em NumPy. Unidades: metros e segundos.

O mundo guarda o que é fixo (paredes e obstáculos redondos) e responde três perguntas, sempre para
vários corpos de uma vez (lotes), que é o que deixa a simulação rápida:

    mundo.raios(origens, angulos, alcance)   -> até onde cada raio enxerga (sensores)
    mundo.toca(posicoes, raio)               -> quem encostou em alguma coisa
    mundo.empurrar(posicoes, raio)           -> tira o corpo de dentro da parede e diz para que lado

Quem se move (carros, bolas, o que vier) fica em objetos.py e usa essas três funções.
"""
import numpy as np


class Mundo:
    def __init__(self, largura=100.0, altura=60.0):
        self.largura, self.altura = float(largura), float(altura)
        self.seg = np.zeros((0, 4))    # paredes: x1, y1, x2, y2
        self.circ = np.zeros((0, 3))   # obstáculos redondos: x, y, raio
        self.objetos = []              # descrição de cada objeto, para desenhar e salvar

    # ---------- montar o mundo ----------
    def parede(self, x1, y1, x2, y2, tipo="parede", **extra):
        self.seg = np.vstack([self.seg, [x1, y1, x2, y2]])
        self.objetos.append(dict(tipo=tipo, pontos=[[x1, y1], [x2, y2]], **extra))
        return self

    def linha(self, pontos, fechada=False, tipo="parede", **extra):
        """Vários segmentos ligados (borda de pista, muro). fechada=True liga o último ponto ao primeiro."""
        p = np.asarray(pontos, float)
        q = np.roll(p, -1, axis=0) if fechada else p[1:]
        p = p if fechada else p[:-1]
        self.seg = np.vstack([self.seg, np.hstack([p, q])])
        self.objetos.append(dict(tipo=tipo, pontos=np.asarray(pontos, float).round(2).tolist(), fechada=fechada, **extra))
        return self

    def caixa(self, x, y, largura=2.0, altura=2.0, ang=0.0, tipo="caixa"):
        c, s = np.cos(ang), np.sin(ang)
        cantos = [(x + dx * c - dy * s, y + dx * s + dy * c)
                  for dx, dy in ((-largura / 2, -altura / 2), (largura / 2, -altura / 2),
                                 (largura / 2, altura / 2), (-largura / 2, altura / 2))]
        return self.linha(cantos, fechada=True, tipo=tipo)

    def cone(self, x, y, raio=0.6, tipo="cone"):
        self.circ = np.vstack([self.circ, [x, y, raio]])
        self.objetos.append(dict(tipo=tipo, x=float(x), y=float(y), raio=float(raio)))
        return self

    def bordas(self):
        """Fecha o mundo com quatro paredes."""
        w, h = self.largura, self.altura
        return self.linha([(0, 0), (w, 0), (w, h), (0, h)], fechada=True, tipo="borda")

    def adicionar(self, obj):
        """Objeto vindo de fora (do painel, de um arquivo): {'tipo': 'cone'|'caixa'|'parede', ...}."""
        t = obj["tipo"]
        if t == "cone":
            return self.cone(obj["x"], obj["y"], obj.get("raio", 0.6))
        if t == "caixa":
            return self.caixa(obj["x"], obj["y"], obj.get("largura", 2.0), obj.get("altura", 2.0), obj.get("ang", 0.0))
        if t == "parede":
            (x1, y1), (x2, y2) = obj["pontos"]
            return self.parede(x1, y1, x2, y2)
        raise ValueError(f"tipo de objeto desconhecido: {t}")

    def descrever(self):
        return dict(largura=self.largura, altura=self.altura, objetos=self.objetos)

    # ---------- sensores ----------
    def raios(self, origens, angulos, alcance):
        """Distância até o primeiro obstáculo em cada raio. origens (N, 2), angulos (N, K) -> (N, K) em metros."""
        o = np.asarray(origens, float)[:, None, :]                       # (N, 1, 2)
        d = np.stack([np.cos(angulos), np.sin(angulos)], axis=-1)        # (N, K, 2)
        dist = np.full(d.shape[:2], float(alcance))
        if len(self.seg):
            a, b = self.seg[:, :2], self.seg[:, 2:]
            e = b - a                                                    # (S, 2)
            ao = a[None, None, :, :] - o[:, :, None, :]                  # (N, 1, S, 2)
            den = d[..., None, 0] * e[:, 1] - d[..., None, 1] * e[:, 0]  # (N, K, S)
            with np.errstate(divide="ignore", invalid="ignore"):
                t = (ao[..., 0] * e[:, 1] - ao[..., 1] * e[:, 0]) / den
                u = (ao[..., 0] * d[..., None, 1] - ao[..., 1] * d[..., None, 0]) / den
            t = np.where((np.abs(den) > 1e-12) & (t >= 0) & (u >= 0) & (u <= 1), t, np.inf)
            dist = np.minimum(dist, t.min(axis=2))
        if len(self.circ):
            oc = o[:, :, None, :] - self.circ[None, None, :, :2]          # (N, 1, M, 2)
            bq = (oc * d[:, :, None, :]).sum(-1)                         # (N, K, M)
            cq = (oc ** 2).sum(-1) - self.circ[:, 2] ** 2
            disc = bq ** 2 - cq
            t = -bq - np.sqrt(np.maximum(disc, 0))
            t = np.where((disc >= 0) & (t >= 0), t, np.inf)
            dist = np.minimum(dist, t.min(axis=2))
        return dist

    # ---------- contato ----------
    def _mais_perto(self, pos):
        """Para cada posição: distância até o obstáculo mais próximo e o ponto dele mais perto."""
        p = np.asarray(pos, float)
        melhor = np.full(len(p), np.inf)
        ponto = p.copy()
        if len(self.seg):
            a, b = self.seg[:, :2], self.seg[:, 2:]
            e = b - a
            t = ((p[:, None, :] - a) * e).sum(-1) / np.maximum((e ** 2).sum(-1), 1e-12)
            q = a + np.clip(t, 0, 1)[..., None] * e                      # (N, S, 2)
            dq = np.linalg.norm(p[:, None, :] - q, axis=-1)
            i = dq.argmin(axis=1)
            melhor, ponto = dq[np.arange(len(p)), i], q[np.arange(len(p)), i]
        if len(self.circ):
            v = p[:, None, :] - self.circ[None, :, :2]
            dc = np.linalg.norm(v, axis=-1)
            folga = dc - self.circ[:, 2]
            i = folga.argmin(axis=1)
            idx = np.arange(len(p))
            mais = folga[idx, i] < melhor
            borda = self.circ[i, :2] + v[idx, i] / np.maximum(dc[idx, i], 1e-12)[:, None] * self.circ[i, 2:3]
            melhor = np.where(mais, folga[idx, i], melhor)
            ponto = np.where(mais[:, None], borda, ponto)
        return melhor, ponto

    def toca(self, pos, raio):
        """Quais círculos de raio `raio` nessas posições encostam em parede ou obstáculo. -> (N,) bool"""
        if not len(self.seg) and not len(self.circ):
            return np.zeros(len(pos), bool)
        return self._mais_perto(pos)[0] < raio

    def empurrar(self, pos, raio):
        """Tira o corpo de dentro do obstáculo. -> (posição corrigida, normal do contato, quem encostou)"""
        p = np.asarray(pos, float)
        if not len(self.seg) and not len(self.circ):
            return p, np.zeros_like(p), np.zeros(len(p), bool)
        d, q = self._mais_perto(p)
        bateu = d < raio
        n = (p - q) / np.maximum(np.linalg.norm(p - q, axis=1), 1e-9)[:, None]
        return np.where(bateu[:, None], q + n * raio, p), n, bateu
