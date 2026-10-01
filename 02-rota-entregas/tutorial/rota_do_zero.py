"""Menor rota pelas capitais, do zero, de cinco jeitos.

Força bruta, vizinho mais próximo, 2-opt, algoritmo genético e o ótimo
com prova. Acompanha o vídeo do elucas.dev: nem tudo precisa de IA.
    pip install numpy scipy
    python rota_do_zero.py
"""
import csv
import itertools
import math
import time

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp


# ===== PASSO 1 · Os dados e a distância =====
def carregar(caminho):
    with open(caminho, encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    nomes = [l["cidade"] for l in linhas]
    lat = np.radians([float(l["lat"]) for l in linhas])
    lon = np.radians([float(l["lon"]) for l in linhas])
    return nomes, lat, lon


def matriz_km(lat, lon):
    # haversine: distância pelo arco da Terra, entre todos os pares
    dlat = lat[:, None] - lat[None, :]
    dlon = lon[:, None] - lon[None, :]
    a = (np.sin(dlat / 2) ** 2
         + np.cos(lat[:, None]) * np.cos(lat[None, :]) * np.sin(dlon / 2) ** 2)
    return 2 * 6371 * np.arcsin(np.sqrt(a))


def comprimento(rota, D):
    return D[rota[:-1], rota[1:]].sum()


# ===== PASSO 2 · Força bruta: testar todas as ordens =====
def forca_bruta(D, inicio, cidades):
    melhor, melhor_km = None, math.inf
    for ordem in itertools.permutations(cidades):
        rota = [inicio, *ordem]
        km = comprimento(rota, D)
        if km < melhor_km:
            melhor, melhor_km = rota, km
    return melhor


# ===== PASSO 3 · Vizinho mais próximo =====
def vizinho_mais_proximo(D, inicio):
    rota, livres = [inicio], set(range(len(D))) - {inicio}
    while livres:
        prox = min(livres, key=lambda c: D[rota[-1], c])
        rota.append(prox)
        livres.remove(prox)
    return rota


# ===== PASSO 4 · 2-opt: descruzar a rota =====
def dois_opt(rota, D):
    rota = rota[:]
    melhorou = True
    while melhorou:
        melhorou = False
        for i in range(1, len(rota) - 1):
            for j in range(i + 1, len(rota)):
                # inverte o trecho entre i e j
                nova = rota[:i] + rota[i:j + 1][::-1] + rota[j + 1:]
                if comprimento(nova, D) < comprimento(rota, D) - 1e-9:
                    rota, melhorou = nova, True
    return rota


# ===== PASSO 5 · Algoritmo genético (o da cobrinha) =====
def crossover_ox(pai, mae, rng):
    a, b = sorted(rng.choice(np.arange(1, len(pai)), 2, replace=False))
    meio = pai[a:b + 1]                          # trecho herdado do pai
    resto = [c for c in mae[1:] if c not in meio]  # o resto, na ordem da mãe
    return [pai[0]] + resto[:a - 1] + meio + resto[a - 1:]


def mutar(rota, rng, taxa=0.3):
    if rng.random() < taxa:
        a, b = sorted(rng.choice(np.arange(1, len(rota)), 2, replace=False))
        rota[a:b + 1] = rota[a:b + 1][::-1]
    return rota


def genetico(D, inicio, geracoes=600, populacao=150, seed=0):
    rng = np.random.default_rng(seed)
    outras = [c for c in range(len(D)) if c != inicio]
    pop = [[inicio] + [int(c) for c in rng.permutation(outras)]
           for _ in range(populacao)]
    for _ in range(geracoes):
        pop.sort(key=lambda r: comprimento(r, D))
        nova = pop[:populacao // 10]                 # elitismo
        while len(nova) < populacao:
            pai = pop[min(rng.integers(0, populacao, 4))]  # torneio
            mae = pop[min(rng.integers(0, populacao, 4))]
            nova.append(mutar(crossover_ox(pai, mae, rng), rng))
        pop = nova
    return min(pop, key=lambda r: comprimento(r, D))


# ===== PASSO 6 · O ótimo, com prova =====
def circuitos(usadas, n):
    """Separa as ligações escolhidas em grupos de cidades conectadas."""
    viz = {c: [] for c in range(n)}
    for i, j in usadas:
        viz[i].append(j)
        viz[j].append(i)
    grupos, vistas = [], set()
    for c in range(n):
        if c in vistas:
            continue
        grupo, pilha = set(), [c]
        while pilha:
            x = pilha.pop()
            if x not in grupo:
                grupo.add(x)
                pilha += viz[x]
        vistas |= grupo
        grupos.append(grupo)
    return grupos, viz


def exato(D, inicio):
    n = len(D) + 1                 # +1: cidade fantasma, a distância zero
    F = np.zeros((n, n))           # (é onde o caminho termina)
    F[:-1, :-1] = D
    arestas = list(itertools.combinations(range(n), 2))
    custo = [F[i, j] for i, j in arestas]
    grau = np.zeros((n, len(arestas)))
    for k, (i, j) in enumerate(arestas):
        grau[i, k] = grau[j, k] = 1
    regras = [LinearConstraint(grau, 2, 2)]      # cada cidade: 2 ligações
    minimo = np.zeros(len(arestas))
    minimo[arestas.index((inicio, n - 1))] = 1   # fantasma ligada ao início
    while True:
        r = milp(custo, constraints=regras, bounds=Bounds(minimo, 1),
                 integrality=np.ones(len(arestas)))
        usadas = [arestas[k] for k in np.flatnonzero(r.x > 0.5)]
        grupos, viz = circuitos(usadas, n)
        if len(grupos) == 1:                     # uma rota só: é o ótimo
            break
        for g in grupos:                         # proíbe cada sub-rota
            dentro = [float(i in g and j in g) for i, j in arestas]
            regras.append(LinearConstraint(dentro, -np.inf, len(g) - 1))
    rota, ant = [inicio], n - 1                  # anda do início até a fantasma
    while len(rota) < n - 1:
        prox = [c for c in viz[rota[-1]] if c != ant][0]
        ant = rota[-1]
        rota.append(prox)
    return rota


# ===== PASSO 7 · Comparar =====
def medir(nome, funcao):
    t0 = time.time()
    rota = funcao()
    print(f"{nome:<22}{comprimento(rota, D):>8,.0f} km{time.time() - t0:>8.2f} s")
    return rota


if __name__ == "__main__":
    nomes, lat, lon = carregar("capitais.csv")
    D = matriz_km(lat, lon)
    inicio = nomes.index("Belém")

    perto = [int(c) for c in np.argsort(D[inicio])[:9]]  # as 9 mais próximas
    sub = D[np.ix_(perto, perto)]
    t0 = time.time()
    forca_bruta(sub, 0, range(1, 9))
    print(f"força bruta, 9 cidades: {time.time() - t0:.1f} s"
          f" para {math.factorial(8):,} ordens")
    print(f"com 27 seriam {math.factorial(26):.1e} ordens\n")

    r = medir("vizinho mais próximo", lambda: vizinho_mais_proximo(D, inicio))
    medir("+ 2-opt", lambda: dois_opt(r, D))
    medir("algoritmo genético", lambda: genetico(D, inicio))
    otima = medir("exato (com prova)", lambda: exato(D, inicio))
    print("\n" + " -> ".join(nomes[c] for c in otima))
