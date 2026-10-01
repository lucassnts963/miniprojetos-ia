"""Testes do mundo simulado:  python mundo/teste_mundo.py  (a partir da raiz do repositório)."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mundo import PISTAS, Bolas, Carros, Mundo, Pista  # noqa: E402


def teste_raios():
    m = Mundo(10, 10).bordas()
    d = m.raios(np.array([[5.0, 5.0]]), np.array([[0, np.pi / 2, np.pi, np.pi / 4]]), 50)[0]
    assert np.allclose(d, [5, 5, 5, 5 * np.sqrt(2)])
    m.cone(8, 5, raio=1)
    assert np.isclose(m.raios(np.array([[5.0, 5.0]]), np.array([[0.0]]), 50)[0, 0], 2)      # para na borda do cone
    assert m.raios(np.array([[5.0, 5.0]]), np.array([[0.0]]), 1.5)[0, 0] == 1.5             # nada dentro do alcance


def teste_contato():
    m = Mundo(10, 10).bordas().caixa(5, 5, 2, 2)
    toca = m.toca(np.array([[0.5, 5.0], [2.5, 5.0], [3.5, 5.0]]), 1.0)
    assert toca.tolist() == [True, False, True]                # parede, livre, caixa
    pos, normal, bateu = m.empurrar(np.array([[0.5, 5.0]]), 1.0)
    assert bateu[0] and np.allclose(pos, [[1, 5]]) and np.allclose(normal, [[1, 0]])


def teste_bola_fica_no_mundo():
    m = Mundo(10, 10).bordas()
    b = Bolas([[5, 5], [2, 8]], [[9, 4], [-6, 7]])
    for _ in range(3000):
        b.passo(m, 0.01)
        assert (b.pos > 0).all() and (b.pos < 10).all()


def teste_carro():
    m = Mundo(200, 20).bordas()
    c = Carros(2, 10, 10, 0.0)
    for _ in range(100):                                        # 5 s acelerando em linha reta
        c.passo(m, np.zeros(2), np.array([1.0, -1.0]), 0.05)
    assert c.pos[0, 0] > 40 and np.isclose(c.pos[0, 1], 10)     # o primeiro andou reto
    assert np.allclose(c.pos[1], [10, 10])                      # o segundo só freou: não anda de ré
    for _ in range(400):
        c.passo(m, np.zeros(2), np.ones(2), 0.05)
    assert not c.vivo.any() and (c.vel == 0).all()              # bateram no fim do mundo e pararam


def teste_pistas():
    for nome in PISTAS:
        p = Pista(nome)
        m = p.montar(Mundo())
        assert not m.toca(p.centro, Carros.RAIO).any(), nome    # dá para passar pelo meio da pista inteira
        onde = np.zeros(1, int)
        for i in range(1, 2 * len(p.centro)):                   # andar pela linha do meio conta progresso
            onde = p.avancar(p.centro[[i % len(p.centro)]], onde)
        assert onde[0] == 2 * len(p.centro) - 1, nome
        assert p.avancar(p.centro[[-10]], onde)[0] == onde[0]   # voltar para trás não conta


if __name__ == "__main__":
    for nome, f in list(globals().items()):
        if nome.startswith("teste_"):
            f()
            print("ok", nome)
