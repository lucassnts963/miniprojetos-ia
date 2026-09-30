"""Testes da busca local: ganho de cada movimento confere com o comprimento real,
a rota continua válida e, em instâncias pequenas, chega perto da ótima (força bruta).

    python teste_rota.py
"""
import itertools
import sys

import numpy as np

import rota as R


def mapa_aleatorio(n, seed):
    rng = np.random.default_rng(seed)
    lat = rng.uniform(-25, -5, n)
    lon = rng.uniform(-55, -35, n)
    return R.Mapa([f"c{i}" for i in range(n)], lat, lon)


def otimo(m, volta):
    """Força bruta: todas as ordens começando na cidade 0."""
    melhor = np.inf
    for perm in itertools.permutations(range(1, m.n)):
        melhor = min(melhor, m.comprimento([0, *perm], volta))
    return melhor


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    # 1. cada movimento: ganho previsto == ganho real, rota válida, início fixo
    for volta in (False, True):
        for seed in range(20):
            m = mapa_aleatorio(60, seed)
            r = R.Rota(m, R.vizinho_mais_proximo(m, 0), volta, conferir=True)
            r.otimizar()
            assert r.t[0] == 0 and sorted(r.t.tolist()) == list(range(m.n))
    print("ok: 40 instâncias de 60 cidades, todos os movimentos conferidos")

    # 2. perto da ótima em instâncias pequenas
    gaps = []
    for volta in (False, True):
        for seed in range(30):
            m = mapa_aleatorio(9, 100 + seed)
            r = R.Rota(m, R.vizinho_mais_proximo(m, 0), volta, conferir=True)
            r.otimizar()
            gaps.append(m.comprimento(r.t, volta) / otimo(m, volta) - 1)
    gaps = np.array(gaps)
    print(f"ok: 60 instâncias de 9 cidades: ótima em {np.mean(gaps < 1e-9):.0%}, "
          f"desvio médio {gaps.mean():.2%}, pior {gaps.max():.2%}")

    # 3. limite inferior nunca passa da rota
    for seed in range(10):
        m = mapa_aleatorio(200, 500 + seed)
        r = R.Rota(m, R.vizinho_mais_proximo(m, 0), False)
        r.otimizar()
        assert R.mst_km(m) <= m.comprimento(r.t) + 1e-6
    print("ok: limite inferior (MST) sempre abaixo da rota")


if __name__ == "__main__":
    main()
