"""TF-IDF em NumPy: transforma o texto do chamado em um vetor de números."""
import math
import re
import unicodedata
from collections import Counter

import numpy as np


def palavras(texto):
    """Minúsculas, sem acento, só letras e números: 'Válvula' e 'valvula' viram a mesma coisa."""
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9]+", texto)


def termos(texto):
    """Palavras, pares de palavras e pedaços de 3 a 5 letras.

    Os pedaços fazem 'vazando' e 'vazamento' compartilharem termos ('<vaz', 'vaza'),
    então o modelo entende variações que nunca viu no treino.
    """
    ps = palavras(texto)
    out = [f"w:{p}" for p in ps]
    out += [f"b:{a}_{b}" for a, b in zip(ps, ps[1:])]
    for p in ps:
        p = f"<{p}>"
        for n in (3, 4, 5):
            out += [f"c:{p[i:i + n]}" for i in range(len(p) - n + 1)]
    return out


class Tfidf:
    def __init__(self, min_df=2):
        self.min_df = min_df
        self.vocab = {}
        self.idf = None

    def fit(self, textos):
        df = Counter()
        for t in textos:
            df.update(set(termos(t)))
        mantidos = sorted(t for t, c in df.items() if c >= self.min_df)
        self.vocab = {t: i for i, t in enumerate(mantidos)}
        n = len(textos)
        # termo raro pesa mais que termo que aparece em todo chamado ("da", "do", "na")
        self.idf = np.array([math.log((1 + n) / (1 + df[t])) + 1 for t in mantidos])
        return self

    def transform(self, textos):
        X = np.zeros((len(textos), len(self.vocab)))
        for i, t in enumerate(textos):
            for termo, c in Counter(termos(t)).items():
                j = self.vocab.get(termo)
                if j is not None:
                    X[i, j] = 1 + math.log(c)
        X *= self.idf
        norma = np.linalg.norm(X, axis=1, keepdims=True)
        norma[norma == 0] = 1
        return X / norma

    def fit_transform(self, textos):
        return self.fit(textos).transform(textos)
