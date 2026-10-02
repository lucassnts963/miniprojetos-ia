"""Ações da bancada para a máquina de completar texto: as apostas para o próximo pedaço, a continuação e o minichat."""
import json
import os

import numpy as np

from conversas import formato

INFO = {"nome": "Máquina de completar texto", "descricao": "Começo de frase → apostas para o próximo pedaço, continuação e minichat"}

AQUI = os.path.dirname(os.path.abspath(__file__))
MODELO = os.path.join(AQUI, "modelo")
EXEMPLOS = ["A manutenção preventiva é", "O Brasil é um país", "A bomba hidráulica", "Para reduzir o custo de produção,",
            "A inteligência artificial"]
PERGUNTAS = ["O que é uma bomba hidráulica?", "O que é um trocador de calor?", "Fale sobre energia solar.",
             "O que é logística?", "Explique soldagem."]
_m = {}


def _modelos():
    """Carrega pedaços, contagem e rede na primeira chamada (a rede vai para a placa de vídeo, se houver)."""
    if not _m:
        if not os.path.exists(os.path.join(MODELO, "rede.pt")):
            raise FileNotFoundError("modelo ainda não treinado: rode baixar_textos.py e depois treinar.py")
        import torch

        from contagem import Contagem
        from pedacos import Pedacos
        from rede import Rede
        salvo = torch.load(os.path.join(MODELO, "rede.pt"), map_location="cpu")
        rede = Rede(**salvo["cfg"])
        rede.load_state_dict(salvo["pesos"])
        _m.update(ped=Pedacos.abrir(os.path.join(MODELO, "pedacos.json")),
                  cont=Contagem.abrir(os.path.join(MODELO, "contagem.npz")),
                  rede=rede.to("cuda" if torch.cuda.is_available() else "cpu").eval())
    return _m["ped"], _m["cont"], _m["rede"]


def _apostas(ids, modelo, ordem):
    """-> (chance de cada pedaço, quantos pedaços do começo foram usados, para onde a rede olhou ou None)."""
    ped, cont, rede = _modelos()
    if not ids:
        ids = ped.codificar("\n")
    if modelo == "contagem":
        p, usados = cont.proximo(ids, ordem)
        olhar = None
    else:
        p, olhar = rede.proximo(ids, com_atencao=True)
        usados = min(len(ids), rede.cfg["janela"])
    p = p.copy()
    p[0] = 0                                             # nunca aposta no pedaço "desconhecido"
    return p / p.sum(), usados, olhar


def _lista(p, n):
    ped = _m["ped"]
    return [dict(id=int(i), pedaco=ped.vocab[i], p=round(float(p[i]), 4)) for i in np.argsort(-p)[:n]]


def _continuar(ids, p, quantos, parar_em=None):
    """Acrescenta pedaços a `ids`, sorteando entre as apostas (temperatura 0 = sempre a maior). -> passos"""
    ped = _m["ped"]
    modelo, ordem = p.get("modelo", "rede"), int(p.get("ordem", 3))
    temp = float(p.get("temperatura", 0.7))
    rng = np.random.default_rng(p.get("semente"))
    passos = []
    for _ in range(quantos):
        prob, usados, _ = _apostas(ids, modelo, ordem)
        if temp <= 0.01:
            escolhido = int(prob.argmax())
        else:
            q = np.zeros_like(prob)
            melhores = np.argsort(-prob)[:40]            # sorteia só entre as 40 maiores apostas
            q[melhores] = prob[melhores] ** (1 / temp)
            escolhido = int(rng.choice(len(q), p=q / q.sum()))
        if parar_em is not None and ped.vocab[escolhido] == parar_em:
            break
        passos.append(dict(pedaco=ped.vocab[escolhido], p=round(float(prob[escolhido]), 4), usados=int(usados),
                           apostas=_lista(prob, 6)))
        ids.append(escolhido)
    return passos


def info(_):
    pronto = os.path.exists(os.path.join(MODELO, "rede.pt"))
    resultado = None
    if pronto:
        with open(os.path.join(MODELO, "resultado.json"), encoding="utf-8") as f:
            resultado = json.load(f)
    return dict(pronto=pronto, resultado=resultado, exemplos=EXEMPLOS, perguntas=PERGUNTAS)


def proximo(p):
    """As apostas para o próximo pedaço, dado o texto até aqui, e o caminho por dentro da rede."""
    ped, _, rede = _modelos()
    ids = ped.codificar(p.get("texto", ""))
    modelo = p.get("modelo", "rede")
    prob, usados, olhar = _apostas(ids, modelo, int(p.get("ordem", 3)))
    janela = ids[-rede.cfg["janela"]:]
    r = dict(pedacos=[ped.vocab[i] for i in ids], apostas=_lista(prob, int(p.get("n", 8))), usados=int(usados),
             olhar=None if olhar is None or not ids else [round(float(v), 4) for v in olhar[-len(janela):]], rede=None)
    if modelo == "rede" and ids:
        n = min(len(janela), int(p.get("colunas", 12)))                # só os últimos pedaços cabem no desenho
        olhares, palpites = rede.por_dentro(ids)
        camadas = []
        for o, q in zip(olhares, palpites):
            q = q.copy()
            q[0] = 0
            i = int(q.argmax())
            camadas.append(dict(olhar=[round(float(v), 4) for v in o[-n:]], fora=round(float(o[:-n].sum()), 4),
                                palpite=ped.vocab[i], p=round(float(q[i] / q.sum()), 4)))
        r["rede"] = dict(pedacos=[ped.vocab[i] for i in janela[-n:]], camadas=camadas, cfg=rede.cfg,
                         parametros=sum(x.numel() for x in rede.parameters()))
    return r


def gerar(p):
    """Continua o texto pedaço por pedaço."""
    ped, _, _ = _modelos()
    ids = ped.codificar(p.get("texto", ""))
    passos = _continuar(ids, p, int(np.clip(p.get("quantos", 40), 1, 200)))
    return dict(passos=passos, texto=ped.decodificar(ids))


def chat(p):
    """Minichat: a conversa vira um texto só ("Pergunta: ... Resposta:") e a rede completa a resposta.

    historico: [[pergunta, resposta], ...] das trocas anteriores. A resposta termina na quebra de linha.
    """
    ped, _, _ = _modelos()
    texto = "".join(formato(a, b) for a, b in p.get("historico", [])[-3:]) + formato(p.get("pergunta", "").strip())
    ids = ped.codificar(texto)
    p = dict(p, temperatura=p.get("temperatura", 0.4))
    passos = _continuar(ids, p, int(np.clip(p.get("quantos", 70), 5, 120)), parar_em="\n")
    return dict(passos=passos, contexto=texto, resposta="".join(x["pedaco"] for x in passos).strip())


ACOES = {"info": info, "proximo": proximo, "gerar": gerar, "chat": chat}
