"""Completar texto só contando: o que costuma vir depois destes últimos pedaços?

É a origem da ideia (Claude Shannon fez isso à mão em 1948). Sem rede neural: uma tabela de contagens.
Olha os últimos `ordem` pedaços; se nunca viu essa sequência, olha um pedaço a menos, e assim por diante.
"""
import numpy as np


class Contagem:
    def __init__(self, vocab, tabelas):
        self.vocab, self.tabelas = vocab, tabelas     # tabelas[k] = (chaves, próximos, contagens), contexto de k pedaços

    def _chave(self, ctx):
        ch = np.zeros(ctx.shape[0], np.int64)
        for j in range(ctx.shape[1]):
            ch = ch * self.vocab + ctx[:, j]
        return ch

    @classmethod
    def treinar(cls, ids, vocab, ordem_max=3):
        ids = np.asarray(ids, np.int64)
        eu = cls(vocab, {})
        for k in range(ordem_max + 1):
            n = len(ids) - k
            ctx = np.stack([ids[j:j + n] for j in range(k)], 1) if k else np.zeros((n, 0), np.int64)
            unicos, cont = np.unique(eu._chave(ctx) * vocab + ids[k:], return_counts=True)
            eu.tabelas[k] = (unicos // vocab, (unicos % vocab).astype(np.int32), cont.astype(np.int32))
        return eu

    def proximo(self, contexto, ordem=3):
        """-> (chance de cada pedaço ser o próximo, quantos pedaços do contexto foram de fato usados)."""
        contexto = np.asarray(contexto, np.int64)
        for k in range(min(ordem, len(contexto), max(self.tabelas)), -1, -1):
            chaves, prox, cont = self.tabelas[k]
            ch = self._chave(contexto[len(contexto) - k:][None, :])[0]
            a, b = np.searchsorted(chaves, ch), np.searchsorted(chaves, ch, side="right")
            if b > a:
                p = np.zeros(self.vocab)
                p[prox[a:b]] = cont[a:b]
                return p / p.sum(), k
        return np.full(self.vocab, 1 / self.vocab), 0

    def salvar(self, caminho):
        np.savez_compressed(caminho, vocab=self.vocab,
                            **{f"{n}{k}": v for k, t in self.tabelas.items() for n, v in zip("cpn", t)})

    @classmethod
    def abrir(cls, caminho):
        d = np.load(caminho)
        ks = sorted(int(n[1:]) for n in d.files if n[0] == "c")
        return cls(int(d["vocab"]), {k: (d[f"c{k}"], d[f"p{k}"], d[f"n{k}"]) for k in ks})
