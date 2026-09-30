"""Rede neural pequena em NumPy puro: uma entrada, uma camada oculta e duas saídas.

    texto -> TF-IDF -> oculta (ReLU) -> equipe     (softmax, 4 classes)
                                     -> prioridade (softmax, 4 classes)

Diferente da cobrinha (neuroevolução), aqui existe um gabarito para cada chamado,
então o treino é por gradiente (backprop + Adam).
"""
import numpy as np

EQUIPES = ["MECÂNICA", "ELÉTRICA", "INSTRUMENTAÇÃO", "AUTOMAÇÃO"]
PRIORIDADES = ["URGENTE", "ALTA", "MÉDIA", "BAIXA"]


def softmax(z):
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


class RedeTriagem:
    NOMES = ("w1", "b1", "we", "be", "wp", "bp")

    def __init__(self, n_entrada, n_oculta=32, seed=0):
        rng = np.random.default_rng(seed)
        self.p = {
            "w1": rng.standard_normal((n_entrada, n_oculta)) * np.sqrt(2 / n_entrada),
            "b1": np.zeros(n_oculta),
            "we": rng.standard_normal((n_oculta, len(EQUIPES))) * np.sqrt(2 / n_oculta),
            "be": np.zeros(len(EQUIPES)),
            "wp": rng.standard_normal((n_oculta, len(PRIORIDADES))) * np.sqrt(2 / n_oculta),
            "bp": np.zeros(len(PRIORIDADES)),
        }

    def forward(self, X):
        """Retorna (ativações da oculta, prob. de equipe, prob. de prioridade)."""
        h = np.maximum(0, X @ self.p["w1"] + self.p["b1"])
        return h, softmax(h @ self.p["we"] + self.p["be"]), softmax(h @ self.p["wp"] + self.p["bp"])

    def prever(self, X):
        _, pe, pp = self.forward(X)
        return pe, pp

    def treinar(self, X, ye, yp, epocas=100, lr=0.002, l2=3e-3, dropout=0.5, lote=32, seed=0, ao_fim_da_epoca=None):
        rng = np.random.default_rng(seed)
        m = {k: np.zeros_like(v) for k, v in self.p.items()}
        v = {k: np.zeros_like(w) for k, w in self.p.items()}
        b1, b2, eps, passo = 0.9, 0.999, 1e-8, 0
        n = len(X)
        for epoca in range(epocas):
            ordem = rng.permutation(n)
            for ini in range(0, n, lote):
                idx = ordem[ini:ini + lote]
                x, te, tp = X[idx], ye[idx], yp[idx]
                k = len(idx)
                # forward com dropout na oculta
                z1 = x @ self.p["w1"] + self.p["b1"]
                h = np.maximum(0, z1)
                mask = (rng.random(h.shape) > dropout) / (1 - dropout)
                hd = h * mask
                pe = softmax(hd @ self.p["we"] + self.p["be"])
                pp = softmax(hd @ self.p["wp"] + self.p["bp"])
                # backward: gradiente da entropia cruzada com softmax = prob - gabarito
                de = pe.copy()
                de[np.arange(k), te] -= 1
                dp = pp.copy()
                dp[np.arange(k), tp] -= 1
                de /= k
                dp /= k
                g = {
                    "we": hd.T @ de, "be": de.sum(0),
                    "wp": hd.T @ dp, "bp": dp.sum(0),
                }
                dh = (de @ self.p["we"].T + dp @ self.p["wp"].T) * mask * (z1 > 0)
                g["w1"], g["b1"] = x.T @ dh, dh.sum(0)
                # Adam
                passo += 1
                for nome in self.NOMES:
                    gr = g[nome] + (l2 * self.p[nome] if nome.startswith("w") else 0)
                    m[nome] = b1 * m[nome] + (1 - b1) * gr
                    v[nome] = b2 * v[nome] + (1 - b2) * gr * gr
                    mh = m[nome] / (1 - b1 ** passo)
                    vh = v[nome] / (1 - b2 ** passo)
                    self.p[nome] -= lr * mh / (np.sqrt(vh) + eps)
            if ao_fim_da_epoca:
                ao_fim_da_epoca(epoca, self)
        return self

    def perda(self, X, ye, yp):
        _, pe, pp = self.forward(X)
        idx = np.arange(len(X))
        return float(-np.log(pe[idx, ye] + 1e-12).mean() - np.log(pp[idx, yp] + 1e-12).mean())

    def n_parametros(self):
        return sum(w.size for w in self.p.values())
