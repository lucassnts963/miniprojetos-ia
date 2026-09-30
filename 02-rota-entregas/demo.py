"""Ações da bancada para a menor rota pelas cidades (ver ../bancada/README.md)."""
import time

import numpy as np

import genetico as G
import rota as R
from dados import carregar
from exato import resolver_exato

INFO = {"nome": "Menor rota pelas cidades", "descricao": "Partida + cidades → ordem de visita mais curta"}

LIMITE_EXATO = 230
LIMITE_GENETICO = 120
_cache = {}


def _mapa(escopo, estados):
    chave = (escopo, tuple(sorted(estados or [])))
    if chave not in _cache:
        nomes, lat, lon = carregar(estados if escopo == "estados" else None, so_capitais=(escopo == "capitais"))
        _cache[chave] = R.Mapa(nomes, lat, lon)
    return _cache[chave]


def info(_):
    nomes, _, _ = carregar()
    ufs = sorted({n.rsplit("/", 1)[1] for n in nomes})
    por_uf = {u: sum(1 for n in nomes if n.endswith("/" + u)) for u in ufs}
    capitais, _, _ = carregar(so_capitais=True)
    return dict(ufs=ufs, por_uf=por_uf, total=len(nomes), capitais=capitais,
                limite_exato=LIMITE_EXATO, limite_genetico=LIMITE_GENETICO)


def cidades(p):
    """Nomes do escopo escolhido (para escolher a partida) e as coordenadas, para desenhar o mapa."""
    m = _mapa(p.get("escopo", "brasil"), p.get("estados"))
    return dict(nomes=m.nomes, lat=np.round(m.lat, 4).tolist(), lon=np.round(m.lon, 4).tolist(), n=m.n)


def resolver(p):
    escopo, estados = p.get("escopo", "brasil"), p.get("estados") or []
    m = _mapa(escopo, estados)
    if m.n < 3:
        raise ValueError("escolha pelo menos 3 cidades")
    inicio = R.achar(m, p["inicio"])
    volta = bool(p.get("volta"))
    metodo = p.get("metodo", "heuristica")
    t0 = time.time()
    extra = {}
    if metodo == "exato":
        if m.n > LIMITE_EXATO:
            raise ValueError(f"o exato vai até {LIMITE_EXATO} cidades aqui (são {m.n}); use a heurística")
        ordem, total, rodadas, cortes = resolver_exato(G.matriz(m), inicio, volta)
        if not volta and ordem[0] != inicio:
            ordem = ordem[::-1]
        km0 = None
        extra = dict(otimo=True, rodadas=rodadas, cortes=cortes)
    elif metodo == "genetico":
        if m.n > LIMITE_GENETICO:
            raise ValueError(f"o genético vai até {LIMITE_GENETICO} cidades aqui (são {m.n}); use a heurística")
        geracoes = int(p.get("geracoes", 600))
        ordem, total, hist = G.evoluir(G.matriz(m), inicio, volta, pop_tam=150, geracoes=geracoes)
        ordem = [int(c) for c in ordem]
        km0 = hist[0][0]
        passo = max(1, len(hist) // 150)
        extra = dict(historico=[round(h[0], 1) for h in hist[::passo]], geracoes=geracoes)
    else:
        segundos = float(p.get("tempo", 5))
        ordem, km0, total = R.resolver(m, inicio, volta, verboso=False, segundos=segundos)
    segundos_gastos = time.time() - t0
    limite = R.mst_km(m)
    total = float(m.comprimento(ordem, volta))
    acum = [0.0]
    for a, b in zip(ordem, ordem[1:]):
        acum.append(acum[-1] + m.d(a, b))
    return dict(
        metodo=metodo, n=m.n, inicio=m.nomes[inicio], volta=volta,
        ordem=[int(c) for c in ordem], km=round(total, 1), km_inicial=None if km0 is None else round(float(km0), 1),
        km_acumulado=[round(x, 1) for x in acum], limite_inferior=round(limite, 1),
        acima_do_limite=round(total / limite - 1, 4), segundos=round(segundos_gastos, 2), **extra)


ACOES = {"info": info, "cidades": cidades, "resolver": resolver}
