"""Neuroevolução: ninguém ensina o carro a dirigir. Os que vão mais longe deixam filhos.

    simular(...)          solta a população inteira na pista e mede até onde cada carro chegou
    proxima_geracao(...)  os melhores passam direto; o resto nasce de dois pais, com pequenas mutações
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # raiz do repositório (pasta mundo/)
from mundo import Carros  # noqa: E402

import cerebro  # noqa: E402

DT = 1 / 20            # s por passo da simulação
SEM_AVANCO = 4.0       # s: carro que fica esse tempo sem avançar sai da corrida


def simular(mundo, pista, genomas, segundos=40.0, gravar=False):
    """-> (metros percorridos por carro, gravação ou None)."""
    n = len(genomas)
    carros = Carros(n, *pista.largada())
    onde = np.zeros(n, int)                 # ponto da linha do meio em que cada carro está
    parado = np.zeros(n)                    # há quanto tempo não avança
    quadros = []
    for passo in range(int(segundos / DT)):
        v = carros.vivo
        if not v.any():
            break
        leitura = np.zeros((n, len(cerebro.SENSORES)))
        leitura[v] = mundo.raios(carros.pos[v], carros.ang[v, None] + cerebro.SENSORES[None, :], cerebro.ALCANCE) / cerebro.ALCANCE
        entradas = np.column_stack([leitura, carros.vel / carros.VEL_MAX])
        oculta, saida = cerebro.decidir(genomas, entradas)
        if gravar and passo % 2 == 0:
            quadros.append((carros.pos.copy(), carros.ang.copy(), v.copy(), entradas, oculta, saida))
        carros.passo(mundo, saida[:, 0], saida[:, 1], DT)
        novo = pista.avancar(carros.pos, onde)
        parado = np.where(novo > onde, 0.0, parado + DT)
        onde = novo
        carros.vivo &= parado < SEM_AVANCO
    metros = onde * pista.passo
    if not gravar:
        return metros, None
    lider = int(metros.argmax())
    return metros, dict(
        dt=DT * 2, lider=lider,
        x=[q[0][:, 0].round(2).tolist() for q in quadros],
        y=[q[0][:, 1].round(2).tolist() for q in quadros],
        ang=[q[1].round(3).tolist() for q in quadros],
        vivo=[q[2].astype(int).tolist() for q in quadros],
        # o que o líder viu, pensou e fez em cada quadro
        entradas=[q[3][lider].round(3).tolist() for q in quadros],
        oculta=[q[4][lider].round(3).tolist() for q in quadros],
        saida=[q[5][lider].round(3).tolist() for q in quadros],
    )


def proxima_geracao(genomas, metros, rng, elite=4, taxa=0.15, forca=0.3):
    """elite: quantos passam sem mudar · taxa: chance de cada peso mudar · forca: tamanho da mudança."""
    n = len(genomas)
    ordem = np.argsort(-metros)
    nova = [genomas[i].copy() for i in ordem[:elite]]

    def torneio():
        a = rng.integers(0, n, 3)
        return genomas[a[metros[a].argmax()]]

    while len(nova) < n:
        pai, mae = torneio(), torneio()
        filho = np.where(rng.random(cerebro.TAMANHO) < 0.5, pai, mae)
        muda = rng.random(cerebro.TAMANHO) < taxa
        nova.append(filho + muda * rng.normal(0, forca, cerebro.TAMANHO))
    return np.array(nova)
