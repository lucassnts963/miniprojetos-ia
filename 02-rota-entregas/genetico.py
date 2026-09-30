"""Algoritmo genético para a rota (a mesma lógica da cobrinha, agora com rotas no lugar de cérebros).

    python genetico.py --inicio "Belém/PA" --capitais
    python genetico.py --inicio "Curitiba/PR" --estados PR --geracoes 3000

Cada indivíduo é uma ordem de visita (permutação) que sempre começa na cidade inicial.
  seleção:  torneio (os mais curtos têm mais chance de ter filhos)
  crossover OX: o filho copia um trecho do pai e completa com as cidades da mãe, na ordem dela
                (nunca repete nem esquece cidade, porque a rota é uma permutação)
  mutação:  inverte um trecho (descruza) ou move uma cidade de lugar
  elitismo: os melhores passam direto para a próxima geração

Bom para rotas pequenas (dezenas de cidades). Para milhares, use rota.py (2-opt + Or-opt).
"""
import argparse
import sys
import time

import numpy as np

from dados import km
from rota import achar, montar_mapa


def matriz(mapa):
    if mapa.D is not None:  # modo estrada: a matriz já vem pronta
        return mapa.D
    P = mapa.P
    return km(np.linalg.norm(P[:, None, :] - P[None, :, :], axis=2))


def comprimentos(pop, D, volta):
    """pop: (individuos, n) -> km de cada rota."""
    tot = D[pop[:, :-1], pop[:, 1:]].sum(1)
    return tot + (D[pop[:, -1], pop[:, 0]] if volta else 0)


def ox(pai, mae, rng):
    """Crossover OX com a primeira cidade fixa."""
    n = len(pai)
    a, b = sorted(rng.choice(np.arange(1, n), 2, replace=False))
    filho = np.full(n, -1)
    filho[0] = pai[0]
    filho[a:b + 1] = pai[a:b + 1]
    usados = set(filho[filho >= 0].tolist())
    resto = [c for c in mae[1:] if c not in usados]
    livres = [i for i in range(1, n) if filho[i] < 0]
    filho[livres] = resto
    return filho


def mutar(ind, rng, taxa):
    n = len(ind)
    if rng.random() < taxa:  # inverte um trecho
        a, b = sorted(rng.choice(np.arange(1, n), 2, replace=False))
        ind[a:b + 1] = ind[a:b + 1][::-1]
    if rng.random() < taxa / 2:  # move uma cidade
        i, j = rng.choice(np.arange(1, n), 2, replace=False)
        c = ind[i]
        ind = np.insert(np.delete(ind, i), j, c)
    return ind


def evoluir(D, inicio, volta=False, pop_tam=200, geracoes=1500, elite=0.1, torneio=4, taxa=0.3, seed=0,
            ao_fim_da_geracao=None):
    rng = np.random.default_rng(seed)
    n = len(D)
    outras = np.array([c for c in range(n) if c != inicio])
    pop = np.array([np.concatenate([[inicio], rng.permutation(outras)]) for _ in range(pop_tam)])
    n_elite = max(1, int(pop_tam * elite))
    historico = []
    for g in range(geracoes):
        fit = comprimentos(pop, D, volta)
        ordem = np.argsort(fit)
        pop, fit = pop[ordem], fit[ordem]
        historico.append((float(fit[0]), float(fit.mean())))
        if ao_fim_da_geracao:
            ao_fim_da_geracao(g, pop[0], fit[0])
        nova = [pop[i].copy() for i in range(n_elite)]
        while len(nova) < pop_tam:
            pais = []
            for _ in range(2):
                cand = rng.integers(0, pop_tam, torneio)
                pais.append(pop[cand.min()])  # já ordenada: menor índice = menor rota
            nova.append(mutar(ox(pais[0], pais[1], rng), rng, taxa))
        pop = np.array(nova)
    fit = comprimentos(pop, D, volta)
    melhor = int(np.argmin(fit))
    return pop[melhor], float(fit[melhor]), historico


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--inicio", required=True)
    ap.add_argument("--estados", nargs="*")
    ap.add_argument("--capitais", action="store_true")
    ap.add_argument("--volta", action="store_true")
    ap.add_argument("--modo", choices=["reta", "estrada"], default="reta", help="linha reta ou pelas rodovias")
    ap.add_argument("--geracoes", type=int, default=1500)
    ap.add_argument("--populacao", type=int, default=200)
    args = ap.parse_args()

    mapa, fora = montar_mapa(args.modo, args.estados, capitais=args.capitais)
    if fora:
        print(f"sem rota por estrada (ficaram de fora): {', '.join(fora)}")
    if mapa.n > 300:
        sys.exit(f"{mapa.n} cidades é muito para o genético; use rota.py")
    inicio = achar(mapa, args.inicio)
    D = matriz(mapa)
    t0 = time.time()

    def mostrar(g, melhor, km_):
        if g % 250 == 0:
            print(f"geração {g:5d}  melhor {km_:,.0f} km", flush=True)

    rota, total, _ = evoluir(D, inicio, args.volta, args.populacao, args.geracoes, ao_fim_da_geracao=mostrar)
    print(f"\nmelhor rota: {total:,.0f} km ({time.time() - t0:.1f} s)")
    print(" -> ".join(mapa.nomes[c].split("/")[0] for c in rota))


if __name__ == "__main__":
    main()
