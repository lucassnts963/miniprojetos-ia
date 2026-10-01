"""Ações da bancada para o carro autônomo: uma população de redes neurais aprende a dirigir no mundo simulado."""
import os

import numpy as np

import cerebro
from evolucao import proxima_geracao, simular
from mundo import PISTAS, Carros, Mundo, Pista

INFO = {"nome": "Carro autônomo", "descricao": "Mundo simulado → uma rede neural aprende a dirigir sozinha"}

AQUI = os.path.dirname(os.path.abspath(__file__))
SALVO = os.path.join(AQUI, "cerebro.npz")

# a população mora na memória do worker: some se o código mudar ou a bancada reiniciar
E = dict(pista=None, genomas=None, geracao=0, historico=[], rng=None, campeao=None, recorde=0.0)


def _montar(nome, objetos):
    pista = Pista(nome)
    mundo = pista.montar(Mundo())
    for o in objetos or []:
        mundo.adicionar(o)
    return mundo, pista


def _estado():
    return dict(pista=E["pista"], geracao=E["geracao"], historico=E["historico"],
                carros=0 if E["genomas"] is None else len(E["genomas"]),
                tem_campeao=E["campeao"] is not None or os.path.exists(SALVO))


def info(_):
    pistas = {}
    for nome in PISTAS:
        mundo, pista = _montar(nome, [])
        pistas[nome] = dict(mundo=mundo.descrever(), **pista.descrever())
    return dict(pistas=pistas, estado=_estado(),
                carro=dict(comprimento=Carros.COMPRIMENTO, largura=Carros.LARGURA, vel_max=Carros.VEL_MAX),
                sensores=cerebro.SENSORES.tolist(), alcance=cerebro.ALCANCE,
                rede=[cerebro.ENTRADAS, cerebro.OCULTA, cerebro.SAIDAS])


def reiniciar(p):
    """População nova, com cérebros sorteados."""
    seed = p.get("seed")
    E.update(pista=p.get("pista", "circuito"), geracao=0, historico=[], campeao=None, recorde=0.0,
             rng=np.random.default_rng(seed))
    E["genomas"] = cerebro.aleatorios(int(np.clip(p.get("carros", 40), 6, 100)), E["rng"])
    return _estado()


def geracao(p):
    """Solta a população atual na pista, grava a corrida e cria a geração seguinte."""
    if E["genomas"] is None or p.get("pista", E["pista"]) != E["pista"]:
        reiniciar(p)
    mundo, pista = _montar(E["pista"], p.get("objetos"))
    metros, gravacao = simular(mundo, pista, E["genomas"], float(np.clip(p.get("segundos", 30), 5, 90)),
                               gravar=p.get("gravar", True))
    E["geracao"] += 1
    melhor = float(metros.max())
    if melhor >= E["recorde"] or E["campeao"] is None:
        E["recorde"], E["campeao"] = melhor, E["genomas"][metros.argmax()].copy()
    E["historico"].append(dict(melhor=round(melhor / pista.comprimento, 3),
                               media=round(float(metros.mean()) / pista.comprimento, 3)))
    E["genomas"] = proxima_geracao(E["genomas"], metros, E["rng"], taxa=float(p.get("taxa", 0.15)),
                                   forca=float(p.get("forca", 0.3)))
    return dict(estado=_estado(), gravacao=gravacao, melhor_m=round(melhor, 1),
                voltas=round(melhor / pista.comprimento, 2), bateram=int((metros < metros.max()).sum()))


def testar(p):
    """O campeão sozinho, numa pista (e com objetos) que pode ser diferente da do treino."""
    genoma = E["campeao"]
    origem = E["pista"]
    if genoma is None:
        if not os.path.exists(SALVO):
            raise ValueError("ainda não há campeão: evolua algumas gerações ou rode treinar.py")
        arq = np.load(SALVO)
        genoma, origem = arq["genoma"], str(arq["pista"])
    mundo, pista = _montar(p.get("pista", origem), p.get("objetos"))
    metros, gravacao = simular(mundo, pista, genoma[None, :], float(np.clip(p.get("segundos", 40), 5, 90)), gravar=True)
    fim = len(gravacao["x"]) * gravacao["dt"]
    return dict(gravacao=gravacao, voltas=round(float(metros[0] / pista.comprimento), 2), treinado_em=origem,
                bateu=bool(fim < float(p.get("segundos", 40)) - 1))


def salvar(_):
    if E["campeao"] is None:
        raise ValueError("ainda não há campeão para salvar")
    np.savez(SALVO, genoma=E["campeao"], pista=E["pista"])
    return dict(arquivo="05-carro-autonomo/cerebro.npz")


ACOES = {"info": info, "reiniciar": reiniciar, "geracao": geracao, "testar": testar, "salvar": salvar}
