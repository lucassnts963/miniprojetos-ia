"""Menor rota para visitar todas as cidades, partindo de uma cidade (problema do caixeiro-viajante).

    python rota.py --inicio "Belém/PA"                      # todas as cidades limpas (~10 mil)
    python rota.py --inicio "Curitiba/PR" --estados PR SC   # só alguns estados
    python rota.py --inicio "Belém/PA" --volta              # volta para a cidade de partida no final

    python rota.py --inicio "Belém/PA" --modo estrada       # distância pelas rodovias (matriz OSRM)
    python rota.py --inicio "Belém/PA" --modo comparar      # linha reta x estrada, nas mesmas cidades

Distância: por padrão, em linha reta sobre a Terra (haversine). Com --modo estrada, pelas rodovias
(ver estradas.py). A linha reta continua como comparativo.

Como funciona:
  1. vizinho mais próximo: sai da cidade inicial e vai sempre para a mais perto ainda não visitada;
  2. 2-opt: se dois trechos da rota se cruzam, inverte o pedaço do meio (descruza);
  3. Or-opt: tira um bloco de 1 a 3 cidades e encaixa num lugar melhor;
  4. repete 2 e 3 até nenhuma troca melhorar;
  5. busca local iterada: bagunça um trecho curto, otimiza de novo e só fica se melhorar.
  Para ser rápido com 10 mil cidades, cada cidade só testa trocas com as suas vizinhas mais próximas.

A rota ótima exata não é garantida (o problema é NP-difícil). Mas a árvore geradora mínima (MST)
dá um limite inferior garantido: nenhuma rota que passa por todas as cidades é menor que ela.
"""
import argparse
import math
import sys
import time
import unicodedata

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.spatial import ConvexHull, cKDTree

from dados import RAIO, carregar, xyz

VIZINHOS = 10


class Mapa:
    """Cidades e distâncias entre elas.

    Sem D: distância em linha reta sobre a Terra. Com D (matriz em km): distância pela estrada,
    e horas (opcional) guarda o tempo estimado de viagem entre cada par.
    """

    def __init__(self, nomes, lat, lon, D=None, horas=None):
        self.nomes, self.lat, self.lon = nomes, lat, lon
        self.P = xyz(lat, lon)
        self.n = len(nomes)
        self.D, self.horas = D, horas
        k = min(VIZINHOS + 1, self.n)
        if D is None:
            _, viz = cKDTree(self.P).query(self.P, k=k)
            self.viz = viz[:, 1:].tolist()
        else:
            sem_diag = D + np.diag(np.full(self.n, np.inf))
            viz = np.argpartition(sem_diag, k - 2, axis=1)[:, :k - 1]
            ordem = np.take_along_axis(sem_diag, viz, 1).argsort(1)
            self.viz = np.take_along_axis(viz, ordem, 1).tolist()
        self._p = self.P.tolist()

    def d(self, i, j):
        """Distância em km (i ou j = -1 significa 'fim do caminho': distância zero)."""
        if i < 0 or j < 0:
            return 0.0
        if self.D is not None:
            return float(self.D[i, j])
        a, b = self._p[i], self._p[j]
        corda = math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)
        return 2 * RAIO * math.asin(min(1.0, corda / 2))

    def comprimento(self, rota, volta=False):
        rota = np.asarray(rota)
        if self.D is not None:
            total = self.D[rota[:-1], rota[1:]].sum()
        else:
            corda = np.linalg.norm(np.diff(self.P[rota], axis=0), axis=1)
            total = (2 * RAIO * np.arcsin(np.clip(corda / 2, 0, 1))).sum()
        return float(total + (self.d(int(rota[-1]), int(rota[0])) if volta else 0.0))

    def horas_total(self, rota, volta=False):
        if self.horas is None:
            return None
        rota = np.asarray(rota)
        total = self.horas[rota[:-1], rota[1:]].sum()
        return float(total + (self.horas[rota[-1], rota[0]] if volta else 0.0))


def montar_mapa(modo="reta", estados=None, incluir_ilhas=False, capitais=False):
    """Mapa no modo pedido. No modo estrada, cidades sem rota na matriz ficam de fora (e são listadas)."""
    nomes, lat, lon, cods = carregar(estados, incluir_ilhas, capitais, com_codigos=True)
    if modo == "reta":
        return Mapa(nomes, lat, lon), []
    import estradas
    tem = estradas.disponiveis()
    ok = [i for i, c in enumerate(cods) if c in tem]
    D = estradas.matriz([cods[i] for i in ok])
    # sem rota para quase ninguém (só por rio, sem balsa no mapa): fica de fora
    ruins = set(np.where(np.isnan(D).sum(1) > len(ok) / 2)[0].tolist())
    ok2 = [ok[k] for k in range(len(ok)) if k not in ruins]
    fora = [nomes[i] for i in range(len(nomes)) if i not in set(ok2)]
    D = estradas.matriz([cods[i] for i in ok2])
    H = estradas.matriz([cods[i] for i in ok2], "horas")
    if np.isnan(D).any():  # pares isolados sem rota: tratados como muito longe
        D = np.where(np.isnan(D), 1e6, D)
        H = np.where(np.isnan(H), 1e4, H)
    return Mapa([nomes[i] for i in ok2], lat[ok2], lon[ok2], D, H), fora


def achar(mapa, texto):
    """Índice da cidade pelo nome ('Belém/PA', 'belem pa', 'Belém')."""
    def n(s):
        s = unicodedata.normalize("NFKD", s.lower())
        return "".join(c for c in s if c.isalnum())
    alvo = n(texto)
    exatos = [i for i, nome in enumerate(mapa.nomes) if n(nome) == alvo]
    if exatos:
        return exatos[0]
    parecidos = [i for i, nome in enumerate(mapa.nomes) if n(nome).startswith(alvo)]
    if len(parecidos) == 1:
        return parecidos[0]
    opcoes = ", ".join(mapa.nomes[i] for i in parecidos[:8]) or "nenhuma"
    sys.exit(f"cidade '{texto}' não encontrada de forma única. Opções: {opcoes}")


# ---------------- 1. vizinho mais próximo ----------------
def vizinho_mais_proximo(mapa, inicio):
    if mapa.D is not None:  # distância pela estrada: procura na linha da matriz
        livre = np.ones(mapa.n, bool)
        livre[inicio] = False
        rota, atual = [inicio], inicio
        for _ in range(mapa.n - 1):
            atual = int(np.argmin(np.where(livre, mapa.D[atual], np.inf)))
            livre[atual] = False
            rota.append(atual)
        return rota
    arvore = cKDTree(mapa.P)
    livre = np.ones(mapa.n, bool)
    rota = [inicio]
    livre[inicio] = False
    atual = inicio
    for _ in range(mapa.n - 1):
        k = 16
        while True:
            _, idx = arvore.query(mapa.P[atual], k=min(k, mapa.n))
            cand = [j for j in np.atleast_1d(idx) if livre[j]]
            if cand:
                atual = int(cand[0])
                break
            if k >= mapa.n:
                raise RuntimeError("sem cidade livre")
            k *= 4
        livre[atual] = False
        rota.append(atual)
    return rota


# ---------------- 2 e 3. busca local ----------------
class Rota:
    """Caminho com a primeira cidade fixa. volta=True fecha o ciclo de volta ao início.

    Nas contas, -1 quer dizer "depois do fim do caminho" (distância zero): assim o mesmo código
    serve para caminho aberto e para ciclo.
    """

    def __init__(self, mapa, rota, volta, conferir=False):
        self.m, self.volta, self.conferir = mapa, volta, conferir
        self.t = np.array(rota, dtype=np.int64)
        self.pos = np.empty(mapa.n, dtype=np.int64)
        self.pos[self.t] = np.arange(mapa.n)

    def prox(self, c):
        p = self.pos[c] + 1
        if p < self.m.n:
            return int(self.t[p])
        return int(self.t[0]) if self.volta else -1

    def ant(self, c):
        p = self.pos[c]
        return int(self.t[p - 1]) if p > 0 else -1

    def _aplicar(self, ganho, fazer):
        antes = self.m.comprimento(self.t, self.volta) if self.conferir else 0.0
        fazer()
        if self.conferir:
            depois = self.m.comprimento(self.t, self.volta)
            assert abs((antes - depois) - ganho) < 1e-6 * max(1.0, antes), (antes, depois, ganho)
            assert self.t[0] == self.inicio

    # ----- 2-opt: troca (u1, v1) + (u2, v2) por (u1, u2) + (v1, v2), invertendo o trecho do meio -----
    def _inverter_entre(self, u1, u2):
        i, j = sorted((int(self.pos[u1]), int(self.pos[u2])))
        seg = self.t[i + 1:j + 1][::-1].copy()
        self.t[i + 1:j + 1] = seg
        self.pos[seg] = np.arange(i + 1, j + 1)

    def dois_opt(self, c, olhar):
        d = self.m.d
        # aresta que sai de c (c -> prox) e aresta que chega em c (ant -> c)
        for sentido in (0, 1):
            if sentido == 0:
                u1, v1 = c, self.prox(c)
            else:
                u1, v1 = self.ant(c), c
            if u1 < 0 or v1 < 0:
                continue
            base = d(u1, v1)
            for w in self.m.viz[c]:
                ganho1 = base - d(c, w)
                if ganho1 <= 0:
                    break  # vizinhos em ordem de distância: os próximos só pioram
                if sentido == 0:
                    u2, v2 = w, self.prox(w)        # nova aresta (c, w) = (u1, u2)
                else:
                    u2, v2 = self.ant(w), w         # nova aresta (c, w) = (v1, v2)
                    if u2 < 0:
                        continue
                if w in (u1, v1) or u2 in (u1, v1) or v2 in (u1, v1) and v2 >= 0:
                    continue
                ganho = base + d(u2, v2) - d(u1, u2) - d(v1, v2)
                if ganho > 1e-7:
                    self._aplicar(ganho, lambda: self._inverter_entre(u1, u2))
                    for x in (u1, v1, u2, v2):
                        if x >= 0:
                            olhar[x] = True
                    return True
        return False

    # ----- Or-opt: move um bloco de 1 a 3 cidades (t[i..j]) para outro lugar, invertido ou não -----
    def or_opt(self, c, olhar):
        d, n = self.m.d, self.m.n
        i = int(self.pos[c])
        if i == 0:
            return False
        for tam in (1, 2, 3):
            j = i + tam - 1
            if j >= n:
                break
            p, q = int(self.t[i]), int(self.t[j])          # pontas do bloco
            a = int(self.t[i - 1])                          # antes do bloco
            b = self.prox(q)                                # depois do bloco (-1 = fim)
            if b >= 0 and i <= self.pos[b] <= j:
                break
            tirar = d(a, p) + d(q, b) - d(a, b)
            if tirar <= 1e-7:
                continue
            for ponta in (p, q):
                for v in self.m.viz[ponta]:
                    if i <= self.pos[v] <= j:
                        continue
                    # inserir entre (x, y) = (v, prox(v)) ou (ant(v), v)
                    for x in (v, self.ant(v)):
                        if x < 0 or i <= self.pos[x] <= j:
                            continue
                        y = b if x == a else self.prox(x)
                        if x == a:
                            continue  # é o lugar de onde o bloco saiu
                        if y >= 0 and i <= self.pos[y] <= j:
                            continue
                        for inv in (False, True):
                            e1, e2 = (q, p) if inv else (p, q)
                            por = d(x, e1) + d(e2, y) - d(x, y)
                            ganho = tirar - por
                            if ganho > 1e-7:
                                self._aplicar(ganho, lambda: self._mover(i, j, x, inv))
                                for z in (a, b, x, y, p, q):
                                    if z >= 0:
                                        olhar[z] = True
                                return True
        return False

    def _mover(self, i, j, x, inv):
        bloco = self.t[i:j + 1].copy()
        if inv:
            bloco = bloco[::-1]
        resto = np.concatenate([self.t[:i], self.t[j + 1:]])
        px = int(np.flatnonzero(resto == x)[0])
        self.t = np.concatenate([resto[:px + 1], bloco, resto[px + 1:]])
        self.pos[self.t] = np.arange(self.m.n)

    def otimizar(self, relatorio=None, olhar=None):
        """Aplica 2-opt e Or-opt até nenhuma troca melhorar. olhar: só estas cidades começam 'acordadas'."""
        self.inicio = int(self.t[0])
        if olhar is None:
            olhar = np.ones(self.m.n, bool)
        passos = 0
        mudou = True
        while mudou:
            mudou = False
            for c in range(self.m.n):
                while olhar[c]:
                    olhar[c] = False
                    if self.dois_opt(c, olhar) or self.or_opt(c, olhar):
                        passos += 1
                        mudou = True
                        if relatorio and passos % 2000 == 0:
                            relatorio(passos, self)
        return passos


# ---------------- 4. busca local iterada ----------------
def iterar(r, segundos, seed=0, janela=60):
    """Bagunça um trecho curto (double-bridge: A B C D -> A C B D), otimiza de novo e só aceita se melhorar."""
    rng = np.random.default_rng(seed)
    m, n = r.m, r.m.n
    atual = m.comprimento(r.t, r.volta)
    fim = time.time() + segundos
    tentativas = aceitas = 0
    while time.time() < fim and n > 8:
        a0 = int(rng.integers(1, n - 4))
        a, b, c = sorted(rng.choice(np.arange(a0, min(n, a0 + janela)), 3, replace=False))
        if not (1 <= a < b < c):
            continue
        t_ant, pos_ant = r.t.copy(), r.pos.copy()
        r.t = np.concatenate([r.t[:a], r.t[b:c], r.t[a:b], r.t[c:]])
        r.pos[r.t] = np.arange(n)
        olhar = np.zeros(n, bool)
        for k in (a - 1, a, b - 1, b, c - 1, c):
            if 0 <= k < n:
                olhar[r.t[k]] = True
        r.otimizar(olhar=olhar)
        novo = m.comprimento(r.t, r.volta)
        tentativas += 1
        if novo < atual - 1e-6:
            atual, aceitas = novo, aceitas + 1
        else:
            r.t, r.pos = t_ant, pos_ant
    return tentativas, aceitas


# ---------------- limite inferior ----------------
def mst_km(mapa):
    """Árvore geradora mínima exata: nenhum caminho que passa por todas as cidades é menor que ela."""
    if mapa.D is not None:  # Prim direto na matriz de distâncias
        dentro = np.zeros(mapa.n, bool)
        dentro[0] = True
        melhor = mapa.D[0].copy()
        total = 0.0
        for _ in range(mapa.n - 1):
            j = int(np.argmin(np.where(dentro, np.inf, melhor)))
            total += melhor[j]
            dentro[j] = True
            melhor = np.minimum(melhor, mapa.D[j])
        return float(total)
    # na esfera, as arestas da árvore mínima estão na triangulação de Delaunay esférica
    P, inv = np.unique(np.round(mapa.P, 12), axis=0, return_inverse=True)
    hull = ConvexHull(P)
    ar = set()
    for s in hull.simplices:
        for a, b in ((s[0], s[1]), (s[1], s[2]), (s[0], s[2])):
            ar.add((min(a, b), max(a, b)))
    ar = np.array(sorted(ar))
    corda = np.linalg.norm(P[ar[:, 0]] - P[ar[:, 1]], axis=1)
    w = 2 * RAIO * np.arcsin(np.clip(corda / 2, 0, 1)) + 1e-9
    g = coo_matrix((w, (ar[:, 0], ar[:, 1])), shape=(len(P), len(P)))
    return float(minimum_spanning_tree(g).sum())


def resolver(mapa, inicio, volta=False, verboso=True, segundos=30):
    t0 = time.time()
    r0 = vizinho_mais_proximo(mapa, inicio)
    km0 = mapa.comprimento(r0, volta)
    if verboso:
        print(f"1. vizinho mais próximo: {km0:,.0f} km  ({time.time() - t0:.1f} s)", flush=True)
    r = Rota(mapa, r0, volta)

    def rel(p, rr):
        print(f"   ... {p} melhorias, {mapa.comprimento(rr.t, volta):,.0f} km", flush=True)

    passos = r.otimizar(rel if verboso else None)
    km1 = mapa.comprimento(r.t, volta)
    if verboso:
        print(f"2. 2-opt + Or-opt: {km1:,.0f} km  ({passos} melhorias, {time.time() - t0:.1f} s)", flush=True)
    if segundos > 0:
        tent, ok = iterar(r, segundos)
        km1 = mapa.comprimento(r.t, volta)
        if verboso:
            print(f"3. busca local iterada ({segundos:.0f} s): {km1:,.0f} km  ({ok} de {tent} tentativas melhoraram)",
                  flush=True)
    return r.t.tolist(), km0, km1


def salvar(mapa, rota, caminho):
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        f.write("ordem,cidade,lat,lon,km_acumulado" + (",horas_acumuladas" if mapa.horas is not None else "") + "\n")
        km_, h_ = 0.0, 0.0
        for k, c in enumerate(rota):
            if k:
                km_ += mapa.d(rota[k - 1], c)
                if mapa.horas is not None:
                    h_ += float(mapa.horas[rota[k - 1], c])
            extra = f",{h_:.1f}" if mapa.horas is not None else ""
            f.write(f'{k + 1},"{mapa.nomes[c]}",{mapa.lat[c]:.6f},{mapa.lon[c]:.6f},{km_:.1f}{extra}\n')


def comparar(reta, estrada, inicio_txt, volta, segundos):
    """Mesmo conjunto de cidades: a rota planejada em linha reta, rodada na estrada, contra a planejada na estrada."""
    ir = achar(reta, inicio_txt)
    ie = achar(estrada, inicio_txt)
    print("planejando em linha reta...", flush=True)
    rr, _, km_reta = resolver(reta, ir, volta, verboso=False, segundos=segundos)
    print("planejando pela estrada...", flush=True)
    re_, _, km_est = resolver(estrada, ie, volta, verboso=False, segundos=segundos)
    # a ordem da linha reta, percorrida de verdade pela estrada
    pos = {n: i for i, n in enumerate(estrada.nomes)}
    rr_na_estrada = [pos[reta.nomes[c]] for c in rr]
    km_reta_estrada = estrada.comprimento(rr_na_estrada, volta)
    print(f"\n{'':<34}{'km no mapa':>14}{'km na estrada':>16}{'horas':>9}")
    print(f"{'planejada em linha reta':<34}{km_reta:>14,.0f}{km_reta_estrada:>16,.0f}"
          f"{estrada.horas_total(rr_na_estrada, volta):>9,.0f}")
    print(f"{'planejada pela estrada':<34}{'':>14}{km_est:>16,.0f}{estrada.horas_total(re_, volta):>9,.0f}")
    print(f"\nplanejar pela estrada economiza {km_reta_estrada - km_est:,.0f} km "
          f"({1 - km_est / km_reta_estrada:.1%}) em relação a planejar em linha reta")
    print(f"a linha reta subestima a viagem real em {km_est / km_reta - 1:.0%}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--inicio", required=True, help='cidade de partida, ex.: "Belém/PA"')
    ap.add_argument("--estados", nargs="*", help="só estas UFs (padrão: todas)")
    ap.add_argument("--volta", action="store_true", help="volta para a cidade de partida no final")
    ap.add_argument("--incluir-ilhas", action="store_true", help="inclui Fernando de Noronha (não se chega por terra)")
    ap.add_argument("--capitais", action="store_true", help="só as capitais")
    ap.add_argument("--modo", choices=["reta", "estrada", "comparar"], default="reta",
                    help="distância em linha reta, pelas rodovias, ou as duas lado a lado")
    ap.add_argument("--tempo", type=float, default=30, help="segundos de busca local iterada (0 desliga)")
    ap.add_argument("--saida", default="rota.csv")
    args = ap.parse_args()

    if args.modo == "comparar":
        estrada, fora = montar_mapa("estrada", args.estados, args.incluir_ilhas, args.capitais)
        nomes_ok = set(estrada.nomes)
        nomes, lat, lon = carregar(args.estados, args.incluir_ilhas, args.capitais)
        ix = [i for i, n in enumerate(nomes) if n in nomes_ok]
        reta = Mapa([nomes[i] for i in ix], lat[ix], lon[ix])
        print(f"{estrada.n} cidades nos dois modos" + (f" ({len(fora)} sem rota por estrada ficaram de fora)" if fora else ""))
        comparar(reta, estrada, args.inicio, args.volta, args.tempo)
        return

    mapa, fora = montar_mapa(args.modo, args.estados, args.incluir_ilhas, args.capitais)
    if fora:
        print(f"sem rota por estrada (ficaram de fora): {', '.join(fora)}")
    inicio = achar(mapa, args.inicio)
    tipo = "pela estrada" if args.modo == "estrada" else "em linha reta"
    print(f"{mapa.n} cidades {tipo}, partindo de {mapa.nomes[inicio]}{' (com volta)' if args.volta else ''}")
    rota, km0, km1 = resolver(mapa, inicio, args.volta, segundos=args.tempo)
    assert rota[0] == inicio and sorted(rota) == list(range(mapa.n)), "rota inválida"
    if mapa.horas is not None:
        print(f"   tempo estimado de direção: {mapa.horas_total(rota, args.volta):,.0f} h")

    lim = mst_km(mapa)
    print(f"   limite inferior (árvore geradora mínima): {lim:,.0f} km")
    print(f"   a rota está no máximo {km1 / lim - 1:.1%} acima da ótima (garantido; na prática bem menos)")
    salvar(mapa, rota, args.saida)
    print(f"rota salva em {args.saida}")
    if args.modo == "estrada":
        import estradas
        print(estradas.CREDITO)


if __name__ == "__main__":
    main()
