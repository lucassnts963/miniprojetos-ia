"""Coisas que se movem no mundo. Cada classe guarda um LOTE (N corpos) em arrays do NumPy.

    Carros  dirigidos por volante e acelerador (modelo de bicicleta); batem e param.
    Bolas   corpos soltos que quicam nas paredes (serve de exemplo e de teste do contato).

Para um objeto novo: guarde o estado em arrays, escreva um passo(mundo, dt) e use
mundo.raios / mundo.toca / mundo.empurrar.
"""
import numpy as np


class Carros:
    COMPRIMENTO, LARGURA = 4.2, 1.9      # m (para desenhar)
    RAIO = 1.25                          # m (círculo usado na colisão)
    ENTRE_EIXOS = 2.6                    # m
    VEL_MAX = 18.0                       # m/s (~65 km/h)
    ACELERACAO, FREIO = 8.0, 14.0        # m/s²
    ARRASTO = 0.35                       # 1/s: tira velocidade aos poucos
    ESTERCO_MAX = 0.55                   # rad (~31°) de giro das rodas da frente

    def __init__(self, n, x, y, ang):
        self.n = n
        self.pos = np.tile(np.array([x, y], float), (n, 1))
        self.ang = np.full(n, float(ang))
        self.vel = np.zeros(n)
        self.vivo = np.ones(n, bool)

    def passo(self, mundo, volante, acelerador, dt):
        """volante e acelerador em [-1, 1] (acelerador negativo freia). Quem bate, para."""
        v = self.vivo
        acel = np.where(acelerador >= 0, acelerador * self.ACELERACAO, acelerador * self.FREIO)
        self.vel = np.where(v, np.clip(self.vel + (acel - self.ARRASTO * self.vel) * dt, 0.0, self.VEL_MAX), 0.0)
        # modelo de bicicleta: quanto mais rápido e mais esterçado, mais o carro gira
        giro = self.vel / self.ENTRE_EIXOS * np.tan(np.clip(volante, -1, 1) * self.ESTERCO_MAX)
        self.ang = self.ang + np.where(v, giro * dt, 0.0)
        self.pos = self.pos + (np.stack([np.cos(self.ang), np.sin(self.ang)], 1) * (self.vel * dt)[:, None]) * v[:, None]
        bateu = v & mundo.toca(self.pos, self.RAIO)
        self.vivo = v & ~bateu
        return bateu

    def sensores(self, mundo, angulos, alcance):
        """Raios a partir do carro, em ângulos relativos à frente dele. -> (N, K) de 0 (colado) a 1 (livre)."""
        return mundo.raios(self.pos, self.ang[:, None] + np.asarray(angulos)[None, :], alcance) / alcance


class Bolas:
    """Corpos redondos soltos: andam em linha reta, perdem um pouco de energia e quicam."""

    def __init__(self, pos, vel, raio=0.8, quique=0.9, atrito=0.1):
        self.pos, self.vel = np.asarray(pos, float).copy(), np.asarray(vel, float).copy()
        self.raio, self.quique, self.atrito = raio, quique, atrito
        self.n = len(self.pos)

    def passo(self, mundo, dt):
        self.vel *= 1 - self.atrito * dt
        self.pos = self.pos + self.vel * dt
        self.pos, normal, bateu = mundo.empurrar(self.pos, self.raio)
        vn = (self.vel * normal).sum(1)                       # velocidade na direção da parede
        reflete = bateu & (vn < 0)
        self.vel = np.where(reflete[:, None], self.vel - (1 + self.quique) * vn[:, None] * normal, self.vel)
        return bateu
