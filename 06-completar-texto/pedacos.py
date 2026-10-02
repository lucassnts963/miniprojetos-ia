"""Pedaços de texto (tokens): o modelo não lê letras nem palavras, lê pedaços.

Começa com cada letra como um pedaço e vai juntando o par que mais aparece lado a lado, até chegar ao
tamanho de vocabulário pedido (o método BPE). Palavra comum vira um pedaço só; palavra rara fica em vários.

    p = Pedacos.treinar(texto, 3000);  ids = p.codificar("A bomba parou");  p.decodificar(ids)
"""
import json
import re
from collections import Counter, defaultdict

PALAVRA = re.compile(r" ?[^\W\d_]+| ?\d| ?[^\w\s]|\s")   # o espaço vai grudado na palavra que vem depois
DESCONHECIDO = "�"


def _juntar(s, par):
    j, t = 0, []
    while j < len(s):
        if j + 1 < len(s) and s[j] == par[0] and s[j + 1] == par[1]:
            t.append(par[0] + par[1])
            j += 2
        else:
            t.append(s[j])
            j += 1
    return t


class Pedacos:
    def __init__(self, vocab, juncoes):
        self.vocab = vocab                                   # id -> pedaço
        self.id = {p: i for i, p in enumerate(vocab)}
        self.ordem = {tuple(j): i for i, j in enumerate(juncoes)}   # par -> quando foi juntado (menor = antes)
        self.juncoes = juncoes
        self._cache = {}

    @classmethod
    def treinar(cls, texto, tamanho=3000, min_letra=20):
        palavras = Counter(PALAVRA.findall(texto))
        letras = Counter()
        for w, n in palavras.items():
            for ch in w:
                letras[ch] += n
        base = sorted(ch for ch, n in letras.items() if n >= min_letra)
        ok = set(base)
        seqs = [[ch if ch in ok else DESCONHECIDO for ch in w] for w in palavras]
        freq = list(palavras.values())
        pares, onde = Counter(), defaultdict(set)            # contagem de cada par e em que palavras ele aparece
        for i, s in enumerate(seqs):
            for par in zip(s, s[1:]):
                pares[par] += freq[i]
                onde[par].add(i)
        vocab, juncoes = [DESCONHECIDO] + base, []
        while len(vocab) < tamanho and pares:
            par, n = max(pares.items(), key=lambda kv: (kv[1], kv[0]))
            if n < 2:
                break
            juncoes.append(list(par))
            vocab.append(par[0] + par[1])
            for i in list(onde[par]):                        # só mexe nas palavras que têm esse par
                s, f = seqs[i], freq[i]
                for q in zip(s, s[1:]):
                    pares[q] -= f
                    onde[q].discard(i)
                seqs[i] = t = _juntar(s, par)
                for q in zip(t, t[1:]):
                    pares[q] += f
                    onde[q].add(i)
            pares.pop(par, None)
        return cls(vocab, juncoes)

    def _palavra(self, w):
        if w not in self._cache:
            s = [ch if ch in self.id else DESCONHECIDO for ch in w]
            while len(s) > 1:
                par = min(zip(s, s[1:]), key=lambda q: self.ordem.get(q, 1e9))   # a junção aprendida primeiro
                if par not in self.ordem:
                    break
                s = _juntar(s, par)
            self._cache[w] = [self.id[p] for p in s]
        return self._cache[w]

    def codificar(self, texto):
        ids = []
        for w in PALAVRA.findall(texto):
            ids += self._palavra(w)
        return ids

    def decodificar(self, ids):
        return "".join(self.vocab[i] for i in ids)

    def salvar(self, caminho):
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dict(vocab=self.vocab, juncoes=self.juncoes), f, ensure_ascii=False)

    @classmethod
    def abrir(cls, caminho):
        with open(caminho, encoding="utf-8") as f:
            d = json.load(f)
        return cls(d["vocab"], d["juncoes"])
