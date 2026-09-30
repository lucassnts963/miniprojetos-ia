"""Coordenadas dos municípios brasileiros (sede municipal) para a rota.

    python dados.py                 # gera dados/cidades.csv a partir da base do IBGE (baixa se não tiver)
    python dados.py --auditar X.csv # procura coordenadas suspeitas num arquivo estado,cidade,lat,lon

Fonte: github.com/kelvins/municipios-brasileiros (MIT), com código IBGE, UF e latitude/longitude
da sede de todos os 5.571 municípios. Validado aqui: uma amostra de 69 municípios caiu 100% dentro
dos polígonos oficiais da malha municipal do IBGE (servicodados.ibge.gov.br).

Uma base anterior (latlon.csv, com distritos) foi descartada: 757 municípios estavam a mais de
100 km do lugar certo (homônimos no estado errado, pontos no oceano). O auditor abaixo foi o que
achou esses erros e continua aqui para checar qualquer base nova.
"""
import csv
import os
import sys
import urllib.request

import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(HERE, "dados")
RAIO = 6371.0  # km
FONTE = "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/"
ILHAS = {"2605459"}  # Fernando de Noronha: não se chega por terra


def xyz(lat, lon):
    """Coordenadas no espaço 3D (esfera de raio 1): distância reta cresce junto com a distância real."""
    la, lo = np.radians(lat), np.radians(lon)
    return np.column_stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])


def km(corda):
    """Distância reta na esfera unitária -> distância pelo arco, em km."""
    return 2 * RAIO * np.arcsin(np.clip(corda / 2, 0, 1))


# ---------------- base do IBGE ----------------
def baixar():
    os.makedirs(DADOS, exist_ok=True)
    for nome in ("municipios.csv", "estados.csv"):
        destino = os.path.join(DADOS, nome.replace(".csv", "_ibge.csv"))
        if not os.path.exists(destino):
            urllib.request.urlretrieve(FONTE + nome, destino)


def preparar():
    baixar()
    with open(os.path.join(DADOS, "estados_ibge.csv"), encoding="utf-8-sig") as f:
        uf_de = {r["codigo_uf"]: r["uf"] for r in csv.DictReader(f)}
    with open(os.path.join(DADOS, "municipios_ibge.csv"), encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    linhas.sort(key=lambda r: (uf_de[r["codigo_uf"]], r["nome"]))
    with open(os.path.join(DADOS, "cidades.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["codigo_ibge", "estado", "cidade", "lat", "lon", "capital", "ilha"])
        for r in linhas:
            w.writerow([r["codigo_ibge"], uf_de[r["codigo_uf"]], r["nome"], r["latitude"], r["longitude"],
                        r["capital"], int(r["codigo_ibge"] in ILHAS)])
    return len(linhas)


def carregar(estados=None, incluir_ilhas=False, so_capitais=False):
    """Nomes 'Cidade/UF', lat e lon. estados: lista de UFs para filtrar."""
    caminho = os.path.join(DADOS, "cidades.csv")
    if not os.path.exists(caminho):
        preparar()
    with open(caminho, encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    if estados:
        estados = {e.upper() for e in estados}
        linhas = [r for r in linhas if r["estado"] in estados]
    if not incluir_ilhas:
        linhas = [r for r in linhas if r["ilha"] == "0"]
    if so_capitais:
        linhas = [r for r in linhas if r["capital"] == "1"]
    nomes = [f"{r['cidade']}/{r['estado']}" for r in linhas]
    lat = np.array([float(r["lat"]) for r in linhas])
    lon = np.array([float(r["lon"]) for r in linhas])
    return nomes, lat, lon


# ---------------- auditoria de bases ----------------
LAT_MIN, LAT_MAX, LON_MIN, LON_MAX = -34.0, 5.5, -74.5, -32.0  # Brasil, incluindo Fernando de Noronha
VIZINHOS = 12
LONGE_DO_ESTADO = 150.0  # km


def suspeitas(uf, lat, lon):
    """Motivo da suspeita de cada ponto ('' se ok). Heurística: confira os casos antes de descartar."""
    motivo = np.full(len(uf), "", dtype=object)
    fora = (lat < LAT_MIN) | (lat > LAT_MAX) | (lon < LON_MIN) | (lon > LON_MAX)
    motivo[fora] = "fora do Brasil"
    P = xyz(lat, lon)
    _, viz = cKDTree(P).query(P, k=VIZINHOS + 1)
    mesmo = (uf[viz[:, 1:]] == uf[:, None]).sum(1)
    perto_estado = np.full(len(uf), np.inf)
    for e in np.unique(uf):
        idx = np.where(uf == e)[0]
        if len(idx) < 2:
            continue
        d, _ = cKDTree(P[idx]).query(P[idx], k=min(len(idx), 30))
        for linha, dd in enumerate(d):
            outros = dd[dd > 1e-9]
            perto_estado[idx[linha]] = km(outros[0]) if len(outros) else np.inf
    # estados com poucos pontos (ex.: DF tem só Brasília) não têm vizinhos do mesmo estado para comparar
    pequeno = np.isin(uf, [e for e in np.unique(uf) if (uf == e).sum() < 5])
    isolado = (mesmo == 0) & (perto_estado > LONGE_DO_ESTADO) & ~pequeno & ~fora
    motivo[isolado] = [f"cercado por outro estado, {d:.0f} km do próprio" for d in perto_estado[isolado]]
    # longe demais do centro do estado, comparado ao espalhamento normal daquele estado
    ok = motivo == ""
    for e in np.unique(uf):
        m = uf == e
        base = m & ok
        if base.sum() < 5:
            continue
        centro = xyz(np.median(lat[base]), np.median(lon[base]))
        d = km(np.linalg.norm(P[m] - centro, axis=1))
        limite = 3.0 * np.percentile(km(np.linalg.norm(P[base] - centro, axis=1)), 75)
        for i, dd in zip(np.where(m)[0], d):
            if dd > limite and motivo[i] == "":
                motivo[i] = f"{dd:.0f} km do centro do estado (limite {limite:.0f})"
    return motivo


def auditar(caminho):
    try:
        with open(caminho, encoding="utf-8") as f:
            linhas = list(csv.DictReader(f))
    except UnicodeDecodeError:
        with open(caminho, encoding="latin-1") as f:
            linhas = list(csv.DictReader(f))
    uf = np.array([r["estado"] for r in linhas])
    lat = np.array([float(r["lat"]) for r in linhas])
    lon = np.array([float(r["lon"]) for r in linhas])
    motivo = suspeitas(uf, lat, lon)
    ruins = np.where(motivo != "")[0]
    print(f"{len(linhas)} pontos, {len(ruins)} suspeitos")
    for i in ruins:
        print(f"  {uf[i]} {linhas[i]['cidade']:<40} {lat[i]:9.4f} {lon[i]:9.4f}  {motivo[i]}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) > 2 and sys.argv[1] == "--auditar":
        auditar(sys.argv[2])
    else:
        print(f"{preparar()} municípios -> dados/cidades.csv")
