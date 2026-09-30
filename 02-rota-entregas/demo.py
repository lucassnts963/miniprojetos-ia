"""Ações da bancada para a menor rota pelas cidades (ver ../bancada/README.md)."""
import time

import genetico as G
import rota as R
from exato import resolver_exato

INFO = {"nome": "Menor rota pelas cidades", "descricao": "Partida + cidades → ordem de visita mais curta"}

LIMITE_EXATO = 230
LIMITE_GENETICO = 120
_cache = {}


def _mapa(distancia, escopo, estados):
    """Mapa em linha reta ou pela estrada. No 'comparar', as cidades são as que têm rota por estrada."""
    modo = "reta" if distancia == "reta" else "estrada"
    chave = (modo, escopo, tuple(sorted(estados or [])))
    if chave not in _cache:
        _cache[chave] = R.montar_mapa(modo, estados if escopo == "estados" else None,
                                      capitais=(escopo == "capitais"))
    return _cache[chave]


def _reta_das_mesmas(estrada, escopo, estados):
    """Mapa em linha reta só com as cidades que existem no mapa pela estrada (mesma ordem)."""
    reta, _ = _mapa("reta", escopo, estados)
    pos = {n: i for i, n in enumerate(reta.nomes)}
    ix = [pos[n] for n in estrada.nomes]
    return R.Mapa(estrada.nomes, reta.lat[ix], reta.lon[ix])


def info(_):
    reta, _ = _mapa("reta", "brasil", [])
    ufs = sorted({n.rsplit("/", 1)[1] for n in reta.nomes})
    por_uf = {u: sum(1 for n in reta.nomes if n.endswith("/" + u)) for u in ufs}
    import estradas
    return dict(ufs=ufs, por_uf=por_uf, total=reta.n, limite_exato=LIMITE_EXATO, limite_genetico=LIMITE_GENETICO,
                credito_estradas=estradas.CREDITO)


def cidades(p):
    """Nomes e coordenadas do escopo escolhido (para escolher a partida e desenhar o mapa)."""
    m, fora = _mapa(p.get("distancia", "reta"), p.get("escopo", "brasil"), p.get("estados"))
    return dict(nomes=m.nomes, lat=[round(float(x), 4) for x in m.lat], lon=[round(float(x), 4) for x in m.lon],
                n=m.n, fora=fora)


def _um(m, inicio, metodo, volta, tempo):
    """Resolve com um método. Devolve ordem, km do ponto de partida do método e extras."""
    if metodo == "exato":
        if m.n > LIMITE_EXATO:
            raise ValueError(f"o exato vai até {LIMITE_EXATO} cidades aqui (são {m.n}); use a heurística")
        ordem, _, rodadas, cortes = resolver_exato(G.matriz(m), inicio, volta)
        if not volta and ordem[0] != inicio:
            ordem = ordem[::-1]
        return [int(c) for c in ordem], None, dict(otimo=True, rodadas=rodadas, cortes=cortes)
    if metodo == "genetico":
        if m.n > LIMITE_GENETICO:
            raise ValueError(f"o genético vai até {LIMITE_GENETICO} cidades aqui (são {m.n}); use a heurística")
        ordem, _, hist = G.evoluir(G.matriz(m), inicio, volta, pop_tam=150, geracoes=600)
        passo = max(1, len(hist) // 150)
        return [int(c) for c in ordem], hist[0][0], dict(historico=[round(h[0], 1) for h in hist[::passo]])
    ordem, km0, _ = R.resolver(m, inicio, volta, verboso=False, segundos=tempo)
    return [int(c) for c in ordem], km0, {}


def _resumo(m, ordem, volta, km0, extra):
    total = m.comprimento(ordem, volta)
    limite = R.mst_km(m)
    acum = [0.0]
    for a, b in zip(ordem, ordem[1:]):
        acum.append(acum[-1] + m.d(a, b))
    horas = m.horas_total(ordem, volta)
    return dict(ordem=ordem, km=round(total, 1), km_inicial=None if km0 is None else round(float(km0), 1),
                km_acumulado=[round(x, 1) for x in acum], limite_inferior=round(limite, 1),
                acima_do_limite=round(total / limite - 1, 4), horas=None if horas is None else round(horas, 1),
                **extra)


def resolver(p):
    distancia = p.get("distancia", "reta")
    escopo, estados = p.get("escopo", "brasil"), p.get("estados") or []
    metodo, volta, tempo = p.get("metodo", "heuristica"), bool(p.get("volta")), float(p.get("tempo", 5))
    m, fora = _mapa(distancia, escopo, estados)
    if m.n < 3:
        raise ValueError("escolha pelo menos 3 cidades")
    inicio = R.achar(m, p["inicio"])
    t0 = time.time()
    base = dict(metodo=metodo, distancia=distancia, n=m.n, inicio=m.nomes[inicio], volta=volta, fora=fora)
    if distancia != "comparar":
        ordem, km0, extra = _um(m, inicio, metodo, volta, tempo)
        return dict(base, **_resumo(m, ordem, volta, km0, extra), segundos=round(time.time() - t0, 2))
    # comparar: mesmas cidades, planejando em linha reta e pela estrada; as duas rodadas na estrada
    reta = _reta_das_mesmas(m, escopo, estados)
    o_reta, k0r, ex_r = _um(reta, inicio, metodo, volta, tempo)
    o_est, k0e, ex_e = _um(m, inicio, metodo, volta, tempo)
    plano_reta = _resumo(m, o_reta, volta, None, {})          # ordem da linha reta, medida na estrada
    plano_reta["km_no_mapa"] = round(reta.comprimento(o_reta, volta), 1)
    plano_reta["otimo_na_reta"] = bool(ex_r.get("otimo"))
    plano_est = _resumo(m, o_est, volta, k0e, ex_e)
    return dict(base, **plano_est, comparar=plano_reta, segundos=round(time.time() - t0, 2))


ACOES = {"info": info, "cidades": cidades, "resolver": resolver}
