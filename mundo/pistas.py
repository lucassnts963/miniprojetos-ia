"""Pistas fechadas: de alguns pontos de controle para as duas bordas e a linha do meio.

    p = Pista("circuito")
    p.montar(mundo)              # coloca as bordas no mundo
    p.largada()                  # (x, y, ângulo)
    p.avancar(pos, onde)         # progresso de cada carro ao longo da pista
"""
import numpy as np

# pontos de controle de cada pista, num mundo de 100 x 60 m (sentido anti-horário)
PISTAS = {
    "oval": [(22, 14), (50, 10), (78, 14), (88, 30), (78, 46), (50, 50), (22, 46), (12, 30)],
    "circuito": [(14, 16), (34, 9), (52, 16), (70, 9), (88, 18), (86, 34), (70, 40), (64, 52), (44, 50),
                 (38, 36), (24, 40), (12, 32)],
    "serpente": [(12, 12), (30, 9), (40, 22), (52, 9), (64, 22), (76, 9), (90, 14), (90, 34), (80, 50), (66, 38),
                 (54, 50), (42, 38), (30, 50), (14, 46), (10, 28)],
}


def _igualar(p, n):
    """n pontos igualmente espaçados ao longo de uma linha fechada."""
    fechado = np.vstack([p, p[:1]])
    comp = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(fechado, axis=0), axis=1))])
    alvo = np.linspace(0, comp[-1], n, endpoint=False)
    return np.column_stack([np.interp(alvo, comp, fechado[:, k]) for k in (0, 1)]), comp[-1]


def _suavizar(pontos, n, raio=6.0):
    """Arredonda os cantos do polígono: média móvel (gaussiana, `raio` em metros) ao longo da linha fechada."""
    fino, comp = _igualar(np.asarray(pontos, float), 1024)
    freq = np.fft.fftfreq(1024, d=comp / 1024)
    filtro = np.exp(-2 * (np.pi * freq * raio) ** 2)
    suave = np.column_stack([np.fft.ifft(np.fft.fft(fino[:, k]) * filtro).real for k in (0, 1)])
    return _igualar(suave, n)


class Pista:
    def __init__(self, nome="circuito", largura=8.0, n=120):
        self.nome, self.largura = nome, largura
        self.centro, self.comprimento = _suavizar(PISTAS[nome], n)
        tang = np.roll(self.centro, -1, axis=0) - np.roll(self.centro, 1, axis=0)
        tang /= np.linalg.norm(tang, axis=1)[:, None]
        normal = np.column_stack([-tang[:, 1], tang[:, 0]])
        self.tangente = tang
        self.esquerda = self.centro + normal * largura / 2
        self.direita = self.centro - normal * largura / 2
        self.passo = self.comprimento / n          # metros entre dois pontos da linha do meio

    def montar(self, mundo):
        mundo.linha(self.esquerda, fechada=True, tipo="pista")
        mundo.linha(self.direita, fechada=True, tipo="pista")
        return mundo

    def largada(self):
        (x, y), (tx, ty) = self.centro[0], self.tangente[0]
        return float(x), float(y), float(np.arctan2(ty, tx))

    def avancar(self, pos, onde, janela=10):
        """Novo índice de cada carro na linha do meio: o ponto mais perto entre os próximos `janela`.

        Só olha para a frente, então andar de ré ou cortar caminho não conta como progresso.
        `onde` é um contador que não volta a zero: voltas completas = onde // n.
        """
        n = len(self.centro)
        cand = (onde[:, None] + np.arange(janela + 1)[None, :])              # (N, J)
        d = np.linalg.norm(self.centro[cand % n] - pos[:, None, :], axis=-1)
        return cand[np.arange(len(pos)), d.argmin(axis=1)]

    def descrever(self):
        return dict(nome=self.nome, largura=self.largura, comprimento=round(self.comprimento, 1),
                    centro=self.centro.round(2).tolist(), largada=[round(v, 3) for v in self.largada()])
