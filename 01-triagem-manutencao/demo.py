"""Ações da bancada para a triagem de ordens de manutenção (ver ../bancada/README.md)."""
import csv
import json
import os
import re
import subprocess
import sys

import numpy as np

from modelo import ARQUIVO, DADOS, HERE, Triagem, carregar_dados
from rede import EQUIPES, PRIORIDADES
from vetorizador import palavras

INFO = {"nome": "Triagem de manutenção", "descricao": "Texto do chamado → equipe e prioridade"}

CORRECOES = os.path.join(DADOS, "chamados_correcoes.csv")
EXEMPLOS = [
    "o motor da bomba 2 tá cheirando queimado",
    "vazamento de óleo na prensa, pingando no chão",
    "CLP da linha 3 não comunica com a IHM",
    "painel soltando fumaça, parou tudo",
    "calibrar o transmissor de nível na parada",
    "rolamento chiando na esteira",
    "sensor de presença da iluminação do banheiro não funciona",
    "robô da paletizadora parado com alarme",
    "barulho estranho no motor do exaustor",
    "operador levou choque na bancada",
    "trocar lâmpadas do escritório por LED",
    "manômetro da caldeira com vidro trincado",
]

_estado = {"modelo": None, "versao": None, "inverso": None}


def _modelo():
    """Carrega o modelo e recarrega sozinho quando o modelo.npz muda (depois de um treino)."""
    versao = os.path.getmtime(ARQUIVO)
    if _estado["versao"] != versao:
        m = Triagem.carregar()
        _estado.update(modelo=m, versao=versao, inverso={i: t for t, i in m.tfidf.vocab.items()})
    return _estado["modelo"]


def _contar_correcoes():
    if not os.path.exists(CORRECOES):
        return 0
    with open(CORRECOES, encoding="utf-8") as f:
        return max(0, sum(1 for _ in f) - 1)


def info(_):
    m = _modelo()
    textos, ye, yp = carregar_dados()
    hist = {}
    caminho = os.path.join(HERE, "historico.json")
    if os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as f:
            hist = json.load(f)
    return dict(
        equipes=EQUIPES, prioridades=PRIORIDADES, exemplos=EXEMPLOS,
        n_exemplos=len(textos), n_correcoes=_contar_correcoes(),
        por_equipe={e: int((ye == i).sum()) for i, e in enumerate(EQUIPES)},
        por_prioridade={p: int((yp == i).sum()) for i, p in enumerate(PRIORIDADES)},
        n_termos=len(m.tfidf.vocab), n_oculta=int(m.rede.p["b1"].size), n_parametros=m.rede.n_parametros(),
        metricas=hist.get("metricas") or {})


def _logit(p):
    """Mede influência em logit: perto de 100% a probabilidade satura, o logit não (ver modelo._motivo)."""
    p = min(max(float(p), 1e-9), 1 - 1e-9)
    return np.log(p / (1 - p))


def classificar(payload):
    texto = (payload.get("texto") or "").strip()
    if not palavras(texto):
        return {"vazio": True}
    m = _modelo()
    inv = _estado["inverso"]
    X = m.tfidf.transform([texto])
    h, pe, pp = m.rede.forward(X)
    x, h, pe, pp = X[0], h[0], pe[0], pp[0]
    e, p = int(pe.argmax()), int(pp.argmax())

    # influência de cada palavra: quanto a confiança cai quando ela sai do texto
    partes = re.split(r"(\s+)", texto)
    idx = [i for i, s in enumerate(partes) if palavras(s)]
    _, pe2, pp2 = m.rede.forward(m.tfidf.transform(["".join(partes[:i] + partes[i + 1:]) for i in idx]))
    k_de = {i: k for k, i in enumerate(idx)}
    tokens = []
    for i, s in enumerate(partes):
        if not s:
            continue
        tok = {"t": s, "eq": None, "pr": None}
        if i in k_de:
            k = k_de[i]
            tok["eq"] = round(float(_logit(pe[e]) - _logit(pe2[k, e])), 4)
            tok["pr"] = round(float(_logit(pp[p]) - _logit(pp2[k, p])), 4)
        tokens.append(tok)

    # termos que o modelo reconheceu, ordenados pelo quanto empurram as saídas escolhidas
    # (contribuição linear: x_i * w1_ij nos neurônios acesos, vezes o peso até a saída)
    ativos = np.nonzero(x)[0]
    contrib = x[ativos][:, None] * m.rede.p["w1"][ativos] * (h > 0)[None, :]
    score = contrib @ m.rede.p["we"][:, e] + contrib @ m.rede.p["wp"][:, p]
    # os pedaços de letras são somados na palavra de onde vieram: "<mot", "otor>" -> motor
    ps = list(dict.fromkeys(palavras(texto)))
    grupos = {}
    for k, i in enumerate(ativos):
        tipo, nome = inv[i][0], inv[i][2:]
        if tipo == "w":
            donos = [nome]
        elif tipo == "b":
            donos = [nome.replace("_", " ")]
        else:
            donos = [w for w in ps if nome in f"<{w}>"]
        for d in donos:
            grupos.setdefault(d, []).append(k)
    nomes = list(grupos)
    G = np.array([contrib[grupos[n]].sum(0) for n in nomes]).reshape(len(nomes), h.size)
    gscore = np.array([score[grupos[n]].sum() for n in nomes])
    gordem = [int(g) for g in np.argsort(-gscore) if gscore[g] > 0]
    smax = max(float(gscore.max(initial=0)), 1e-9)
    termos = [{"termo": nomes[g], "tipo": "par" if " " in nomes[g] else "palavra",
               "peso": round(float(gscore[g]) / smax, 3), "n": len(grupos[nomes[g]])} for g in gordem[:14]]
    desconhecidas = [w for w in ps if f"w:{w}" not in m.tfidf.vocab]

    # grafo: palavras -> oculta (contribuição x_i * w1_ij nos neurônios que acenderam) -> saídas escolhidas
    T = gordem[:8]
    c1 = G[T]
    arestas1 = [(int(a), int(b), float(c1[a, b])) for a, b in zip(*np.nonzero(c1 > 0))]
    arestas1 = sorted(arestas1, key=lambda z: -z[2])[:48]
    ce = h * m.rede.p["we"][:, e]
    cp = h * m.rede.p["wp"][:, p]
    top_e = [int(j) for j in np.argsort(-ce)[:10] if ce[j] > 0]
    top_p = [int(j) for j in np.argsort(-cp)[:10] if cp[j] > 0]
    n1 = max((z[2] for z in arestas1), default=1)
    n2 = max(float(ce.max()), float(cp.max()), 1e-9)
    hmax = float(h.max()) or 1.0

    return dict(
        equipe=EQUIPES[e], prioridade=PRIORIDADES[p],
        prob_equipe=[round(float(v), 4) for v in pe], prob_prioridade=[round(float(v), 4) for v in pp],
        tokens=tokens, termos=termos, desconhecidas=desconhecidas, n_termos_ativos=int(len(ativos)),
        grafo=dict(
            termos=[nomes[g] for g in T],
            oculta=[round(float(v) / hmax, 3) for v in h],
            a1=[[a, b, round(w / n1, 3)] for a, b, w in arestas1],
            ae=[[j, round(float(ce[j]) / n2, 3)] for j in top_e],
            ap=[[j, round(float(cp[j]) / n2, 3)] for j in top_p],
        ))


def corrigir(payload):
    """Guarda um exemplo rotulado. O arquivo entra sozinho no próximo treino (dados/chamados*.csv)."""
    texto = " ".join((payload.get("texto") or "").replace(";", ",").split())
    equipe, prioridade = payload.get("equipe"), payload.get("prioridade")
    if not palavras(texto) or equipe not in EQUIPES or prioridade not in PRIORIDADES:
        raise ValueError("texto, equipe ou prioridade inválidos")
    novo = not os.path.exists(CORRECOES)
    with open(CORRECOES, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        if novo:
            w.writerow(["texto", "equipe", "prioridade"])
        w.writerow([texto, equipe, prioridade])
    return {"n_correcoes": _contar_correcoes()}


def retreinar(_):
    """Roda o treinar.py completo (validação cruzada + modelo final) e recarrega o modelo."""
    r = subprocess.run([sys.executable, "treinar.py"], cwd=HERE, capture_output=True,
                       text=True, encoding="utf-8", timeout=900)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-2000:] or "treino falhou")
    return dict(info(None), log=r.stdout[-4000:])


ACOES = {"info": info, "classificar": classificar, "corrigir": corrigir, "retreinar": retreinar}
