"""Triagem de ordens de manutenção do zero.

Lê o texto do chamado e decide a equipe e a prioridade. Só NumPy.
Acompanha o vídeo do elucas.dev, passo a passo, camada por camada.
    pip install numpy
    python triagem_do_zero.py
"""
import csv
import math
import re
import unicodedata
from collections import Counter

import numpy as np

EQUIPES = ["MECÂNICA", "ELÉTRICA", "INSTRUMENTAÇÃO", "AUTOMAÇÃO"]
PRIORIDADES = ["URGENTE", "ALTA", "MÉDIA", "BAIXA"]


# ===== PASSO 1 · Os dados =====
def carregar(caminho):
    with open(caminho, encoding="utf-8") as f:
        linhas = list(csv.DictReader(f, delimiter=";"))
    textos = [l["texto"] for l in linhas]
    y_eq = np.array([EQUIPES.index(l["equipe"]) for l in linhas])
    y_pr = np.array([PRIORIDADES.index(l["prioridade"]) for l in linhas])
    return textos, y_eq, y_pr


# ===== PASSO 2 · Texto -> palavras =====
def palavras(texto):
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9]+", texto)


# ===== PASSO 3 · Palavras -> termos =====
def termos(texto):
    ps = palavras(texto)
    # palavras
    out = [f"w:{p}" for p in ps]
    # pares de palavras vizinhas
    out += [f"b:{a}_{b}" for a, b in zip(ps, ps[1:])]
    # pedaços de 3 a 5 letras
    for p in ps:
        p = f"<{p}>"
        for n in (3, 4, 5):
            out += [f"c:{p[i:i + n]}" for i in range(len(p) - n + 1)]
    return out


# ===== PASSO 4 · TF-IDF: termos -> vetor de números =====
class Tfidf:
    def fit(self, textos, min_df=2):
        df = Counter()
        for t in textos:
            df.update(set(termos(t)))
        vocab = sorted(t for t, c in df.items() if c >= min_df)
        self.vocab = {t: i for i, t in enumerate(vocab)}
        n = len(textos)
        idf = [math.log((1 + n) / (1 + df[t])) + 1 for t in vocab]
        self.idf = np.array(idf)
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
        return X / np.maximum(norma, 1e-12)


# ===== PASSO 5 · A rede: os pesos =====
def criar_rede(n_entrada, n_oculta=32, seed=0):
    rng = np.random.default_rng(seed)

    def pesos(n_in, n_out):  # inicialização de He
        return rng.standard_normal((n_in, n_out)) * np.sqrt(2 / n_in)

    return {
        "W1": pesos(n_entrada, n_oculta), "b1": np.zeros(n_oculta),
        "We": pesos(n_oculta, 4), "be": np.zeros(4),  # saída: equipe
        "Wp": pesos(n_oculta, 4), "bp": np.zeros(4),  # saída: prioridade
    }


# ===== PASSO 6 · Forward: camada por camada =====
def softmax(z):
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def forward(rede, X, mascara=1.0):
    z1 = X @ rede["W1"] + rede["b1"]             # camada oculta
    h = np.maximum(0, z1) * mascara              # ReLU (+ dropout)
    p_eq = softmax(h @ rede["We"] + rede["be"])  # saída 1: equipe
    p_pr = softmax(h @ rede["Wp"] + rede["bp"])  # saída 2: prioridade
    return z1, h, p_eq, p_pr


# ===== PASSO 7 · A perda: entropia cruzada =====
def perda(p_eq, p_pr, y_eq, y_pr):
    i = np.arange(len(y_eq))
    perda_eq = -np.log(p_eq[i, y_eq] + 1e-12).mean()
    perda_pr = -np.log(p_pr[i, y_pr] + 1e-12).mean()
    return perda_eq + perda_pr


# ===== PASSO 8 · Backprop: de trás para frente =====
def gradientes(rede, X, y_eq, y_pr, dropout, rng):
    n = len(X)
    mascara = (rng.random((n, rede["b1"].size)) > dropout) / (1 - dropout)
    z1, h, p_eq, p_pr = forward(rede, X, mascara)
    # saídas: probabilidade - gabarito
    d_eq = p_eq.copy()
    d_eq[np.arange(n), y_eq] -= 1
    d_pr = p_pr.copy()
    d_pr[np.arange(n), y_pr] -= 1
    d_eq, d_pr = d_eq / n, d_pr / n
    g = {"We": h.T @ d_eq, "be": d_eq.sum(0),
         "Wp": h.T @ d_pr, "bp": d_pr.sum(0)}
    # oculta: soma o erro das duas saídas, passa pela ReLU e pelo dropout
    d_h = (d_eq @ rede["We"].T + d_pr @ rede["Wp"].T) * mascara * (z1 > 0)
    g["W1"], g["b1"] = X.T @ d_h, d_h.sum(0)
    return g


# ===== PASSO 9 · Treino com Adam =====
def treinar(rede, X, y_eq, y_pr, epocas=100, lr=0.002, l2=3e-3,
            dropout=0.5, lote=32, seed=0):
    rng = np.random.default_rng(seed)
    m = {k: np.zeros_like(w) for k, w in rede.items()}
    v = {k: np.zeros_like(w) for k, w in rede.items()}
    passo = 0
    for epoca in range(epocas):
        ordem = rng.permutation(len(X))
        for ini in range(0, len(X), lote):
            idx = ordem[ini:ini + lote]
            g = gradientes(rede, X[idx], y_eq[idx], y_pr[idx], dropout, rng)
            passo += 1
            for k in rede:
                if k.startswith("W"):
                    # L2: segura os pesos perto de zero
                    g[k] += l2 * rede[k]
                # Adam: média do gradiente (m) e do gradiente ao quadrado (v)
                m[k] = 0.9 * m[k] + 0.1 * g[k]
                v[k] = 0.999 * v[k] + 0.001 * g[k] ** 2
                m_hat = m[k] / (1 - 0.9 ** passo)
                v_hat = v[k] / (1 - 0.999 ** passo)
                rede[k] -= lr * m_hat / (np.sqrt(v_hat) + 1e-8)
        if (epoca + 1) % 10 == 0:
            _, _, p_eq, p_pr = forward(rede, X)
            erro = perda(p_eq, p_pr, y_eq, y_pr)
            print(f"época {epoca + 1:3d}  perda {erro:.3f}")
    return rede


# ===== PASSO 10 · Testar e usar =====
def classificar(rede, tfidf, texto):
    _, _, p_eq, p_pr = forward(rede, tfidf.transform([texto]))
    return EQUIPES[p_eq[0].argmax()], PRIORIDADES[p_pr[0].argmax()]


if __name__ == "__main__":
    textos, y_eq, y_pr = carregar("chamados.csv")
    ordem = np.random.default_rng(42).permutation(len(textos))
    corte = int(len(textos) * 0.8)  # 80% treino, 20% teste
    tr, te = ordem[:corte], ordem[corte:]

    tfidf = Tfidf().fit([textos[i] for i in tr])
    X_tr = tfidf.transform([textos[i] for i in tr])
    X_te = tfidf.transform([textos[i] for i in te])

    rede = criar_rede(X_tr.shape[1])
    treinar(rede, X_tr, y_eq[tr], y_pr[tr])

    _, _, p_eq, p_pr = forward(rede, X_te)
    print(f"teste  equipe {(p_eq.argmax(1) == y_eq[te]).mean():.0%}"
          f"  prioridade {(p_pr.argmax(1) == y_pr[te]).mean():.0%}")
    exemplo = "o motor da bomba 2 tá cheirando queimado"
    print(classificar(rede, tfidf, exemplo))
