"""Distâncias pelas rodovias entre os municípios (modo "estrada" da rota).

    python estradas.py          # baixa (154 MB) e monta dados/estradas.npz

Fonte: Saldanha, R. (2024). "Road distances and trip duration matrix for Brazilian municipalities".
Zenodo, doi:10.5281/zenodo.11400243, licença CC BY 4.0. Calculado com o OSRM (perfil carro) sobre a
malha do OpenStreetMap de maio de 2024, entre as sedes municipais do IBGE: 15,5 milhões de pares
entre 5.565 municípios (distância em metros e duração estimada da viagem).

Os arquivos grandes (zip e npz) ficam fora do git: este script refaz tudo.
"""
import os
import sys
import urllib.request
import zipfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(HERE, "dados")
ZIP = os.path.join(DADOS, "dist_brasil.zip")
NPZ = os.path.join(DADOS, "estradas.npz")
URL = "https://zenodo.org/api/records/11400243/files/dist_brasil.zip/content"
CREDITO = "Distâncias rodoviárias: Saldanha (2024), Zenodo 10.5281/zenodo.11400243, CC BY 4.0 (OSRM + OpenStreetMap)"


def montar():
    import pandas as pd
    os.makedirs(DADOS, exist_ok=True)
    if not os.path.exists(ZIP):
        print("baixando 154 MB do Zenodo...", flush=True)
        urllib.request.urlretrieve(URL, ZIP)
    with zipfile.ZipFile(ZIP) as z, z.open("dist_brasil.csv") as f:
        df = pd.read_csv(f, sep=";", decimal=",", dtype={"orig": "int32", "dest": "int32"})
    codigos = np.unique(np.concatenate([df["orig"].to_numpy(), df["dest"].to_numpy()]))
    idx = {c: i for i, c in enumerate(codigos)}
    n = len(codigos)
    km = np.full((n, n), np.nan, dtype=np.float32)
    horas = np.full((n, n), np.nan, dtype=np.float32)
    i = np.array([idx[c] for c in df["orig"].to_numpy()])
    j = np.array([idx[c] for c in df["dest"].to_numpy()])
    km[i, j] = km[j, i] = (df["dist"].to_numpy() / 1000.0).astype(np.float32)
    horas[i, j] = horas[j, i] = (df["dur"].to_numpy() / 60.0).astype(np.float32)
    np.fill_diagonal(km, 0)
    np.fill_diagonal(horas, 0)
    np.savez_compressed(NPZ, codigos=codigos, km=km, horas=horas)
    return n, len(df), int(np.isnan(km).sum())


_cache = {}


def matriz(codigos, tipo="km"):
    """Submatriz (float64) para esta lista de códigos IBGE, na mesma ordem. tipo: 'km' ou 'horas'."""
    if "npz" not in _cache:
        if not os.path.exists(NPZ):
            montar()
        d = np.load(NPZ)
        _cache["npz"] = {k: d[k] for k in ("codigos", "km", "horas")}
    base = _cache["npz"]
    pos = {int(c): i for i, c in enumerate(base["codigos"])}
    faltam = [c for c in codigos if int(c) not in pos]
    if faltam:
        raise KeyError(faltam)
    ix = np.array([pos[int(c)] for c in codigos])
    return base[tipo][np.ix_(ix, ix)].astype(np.float64)


def disponiveis():
    if not os.path.exists(NPZ):
        montar()
    return set(int(c) for c in np.load(NPZ)["codigos"])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    n, pares, nan = montar()
    print(f"{n} municípios, {pares:,} pares, {nan} células sem valor -> {NPZ}")
