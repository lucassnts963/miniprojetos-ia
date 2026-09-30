"""Junta o TF-IDF e a rede num modelo só, que salva, carrega e explica a decisão."""
import csv
import glob
import json
import os

import numpy as np

from rede import EQUIPES, PRIORIDADES, RedeTriagem
from vetorizador import Tfidf, palavras

HERE = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(HERE, "dados")
ARQUIVO = os.path.join(HERE, "modelo.npz")
# palavras que não servem como explicação ("por causa de: na, o")
VAZIAS = set("a o e as os da do das dos de na no nas nos em com sem por pra para um uma que ta esta se ao".split())


def carregar_dados(*arquivos):
    """Lê os CSVs de exemplo (por padrão, todos os lotes em dados/)."""
    arquivos = arquivos or sorted(glob.glob(os.path.join(DADOS, "chamados*.csv")))
    linhas = []
    for caminho in arquivos:
        with open(caminho, encoding="utf-8") as f:
            linhas += list(csv.DictReader(f, delimiter=";"))
    textos = [l["texto"] for l in linhas]
    ye = np.array([EQUIPES.index(l["equipe"]) for l in linhas])
    yp = np.array([PRIORIDADES.index(l["prioridade"]) for l in linhas])
    return textos, ye, yp


class Triagem:
    def __init__(self, tfidf, rede):
        self.tfidf = tfidf
        self.rede = rede

    @classmethod
    def treinar(cls, textos, ye, yp, n_oculta=32, seed=0, **kw):
        tfidf = Tfidf().fit(textos)
        rede = RedeTriagem(len(tfidf.vocab), n_oculta, seed=seed)
        rede.treinar(tfidf.transform(textos), ye, yp, seed=seed, **kw)
        return cls(tfidf, rede)

    def probabilidades(self, textos):
        return self.rede.prever(self.tfidf.transform(textos))

    def classificar(self, texto, motivos=3):
        """Equipe, prioridade, confiança e as palavras que mais pesaram na decisão."""
        pe, pp = self.probabilidades([texto])
        e, p = int(pe[0].argmax()), int(pp[0].argmax())
        return {
            "texto": texto,
            "equipe": EQUIPES[e], "conf_equipe": float(pe[0, e]),
            "prioridade": PRIORIDADES[p], "conf_prioridade": float(pp[0, p]),
            "prob_equipe": dict(zip(EQUIPES, pe[0].round(3).tolist())),
            "prob_prioridade": dict(zip(PRIORIDADES, pp[0].round(3).tolist())),
            "motivo_equipe": self._motivo(texto, 0, e, motivos),
            "motivo_prioridade": self._motivo(texto, 1, p, motivos),
        }

    def _motivo(self, texto, saida, classe, n):
        """Tira uma palavra por vez e mede quanto a confiança cai (oclusão).

        A queda é medida em logit, log(p / (1 - p)): perto de 100% de confiança, tirar uma
        palavra forte quase não muda a probabilidade (outra palavra segura), mas muda o logit.
        """
        ps = palavras(texto)
        if len(ps) < 2:
            return ps

        def logit(p):
            p = np.clip(p, 1e-9, 1 - 1e-9)
            return np.log(p / (1 - p))

        base = logit(self.probabilidades([texto])[saida][0, classe])
        sem = [" ".join(ps[:i] + ps[i + 1:]) for i in range(len(ps))]
        queda = base - logit(self.probabilidades(sem)[saida][:, classe])
        candidatas = [i for i in np.argsort(-queda) if queda[i] > 0 and ps[i] not in VAZIAS]
        # as que pesam de verdade; se nenhuma passar do corte, ao menos a mais forte
        ordem = [i for i in candidatas if queda[i] > 0.3] or candidatas[:1]
        return [ps[i] for i in ordem[:n]]

    def salvar(self, caminho=ARQUIVO):
        np.savez_compressed(
            caminho, vocab=json.dumps(self.tfidf.vocab), idf=self.tfidf.idf,
            **{k: v for k, v in self.rede.p.items()})

    @classmethod
    def carregar(cls, caminho=ARQUIVO):
        d = np.load(caminho)
        tfidf = Tfidf()
        tfidf.vocab = json.loads(str(d["vocab"]))
        tfidf.idf = d["idf"]
        rede = RedeTriagem(len(tfidf.vocab), d["b1"].size)
        rede.p = {k: d[k] for k in RedeTriagem.NOMES}
        return cls(tfidf, rede)
