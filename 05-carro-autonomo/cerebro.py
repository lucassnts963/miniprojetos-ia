"""O cérebro do carro: uma rede neural pequena, guardada como uma lista de números (o genoma).

    entradas: 7 sensores de distância (0 = colado, 1 = livre) + a velocidade
    oculta:   8 neurônios (tanh)
    saídas:   volante e acelerador, de -1 a 1 (tanh)

As funções trabalham com a população inteira de uma vez: genomas tem forma (N, TAMANHO).
"""
import numpy as np

SENSORES = np.radians([-90, -50, -25, 0, 25, 50, 90])   # ângulos dos raios, em relação à frente do carro
ALCANCE = 30.0                                          # m
ENTRADAS, OCULTA, SAIDAS = len(SENSORES) + 1, 8, 2
TAMANHO = ENTRADAS * OCULTA + OCULTA + OCULTA * SAIDAS + SAIDAS


def aleatorios(n, rng):
    return rng.normal(0, 0.5, (n, TAMANHO))


def abrir(genomas):
    """Corta cada genoma nos pesos e vieses das duas camadas."""
    g, i = np.atleast_2d(genomas), 0
    partes = []
    for forma in ((ENTRADAS, OCULTA), (OCULTA,), (OCULTA, SAIDAS), (SAIDAS,)):
        k = int(np.prod(forma))
        partes.append(g[:, i:i + k].reshape(len(g), *forma))
        i += k
    return partes


def decidir(genomas, entradas):
    """entradas (N, ENTRADAS) -> oculta (N, OCULTA), saídas (N, 2): volante e acelerador."""
    w1, b1, w2, b2 = abrir(genomas)
    h = np.tanh(np.einsum("ni,nih->nh", entradas, w1) + b1)
    return h, np.tanh(np.einsum("nh,nho->no", h, w2) + b2)
