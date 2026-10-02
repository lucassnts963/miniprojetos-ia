"""Testes rápidos das três peças, num texto de brinquedo:  python teste.py"""
import numpy as np

from contagem import Contagem
from pedacos import Pedacos
from rede import Rede

TEXTO = "a bomba parou de novo. a bomba parou ontem. o motor parou de novo. " * 30


def teste_pedacos():
    p = Pedacos.treinar(TEXTO, 60, min_letra=1)
    frase = "a bomba parou de novo. o motor parou ontem."
    ids = p.codificar(frase)
    assert p.decodificar(ids) == frase                       # ida e volta sem perder nada
    assert len(ids) < len(frase)                             # juntou letras em pedaços maiores
    assert p.vocab[p.codificar("x")[0]] == "\ufffd"          # letra nunca vista vira "desconhecido"


def teste_contagem():
    p = Pedacos.treinar(TEXTO, 60, min_letra=1)
    c = Contagem.treinar(p.codificar(TEXTO), len(p.vocab))
    prob, usados = c.proximo(p.codificar("a bomba"), 3)
    assert usados == min(3, len(p.codificar("a bomba"))) and np.isclose(prob.sum(), 1)
    assert p.vocab[prob.argmax()] == " parou"                # depois de "a bomba" sempre vem " parou"
    prob, usados = c.proximo(p.codificar(". a bomba parou"), 3)
    assert 0.3 < prob.max() < 0.7                            # depois vem " de" ou " ontem": divide a aposta


def teste_rede():
    r = Rede(60, 16, 32, 2, 2)
    prob, olhar = r.proximo(list(range(10)), com_atencao=True)
    assert prob.shape == (60,) and np.isclose(prob.sum(), 1, atol=1e-4)
    assert olhar.shape == (10,) and np.isclose(olhar.sum(), 1, atol=1e-4)
    assert r.proximo(list(range(40))).shape == (60,)         # texto maior que a janela: usa só o final


if __name__ == "__main__":
    for nome, f in list(globals().items()):
        if nome.startswith("teste_"):
            f()
            print("ok", nome)
