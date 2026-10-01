"""Exploração: contar os tubos do espelho de um trocador e separar aberto / obstruído / tamponado.

Tudo com visão clássica (OpenCV), sem treinar nada. Serve para medir até onde isso vai antes de
pensar num modelo treinado.

    python explorar.py "caminho/da/foto.jpeg" raio_min raio_max
"""
import os
import sys

import cv2
import numpy as np
from scipy.spatial import cKDTree

AQUI = os.path.dirname(os.path.abspath(__file__))
CORES = {"aberto": (120, 220, 90), "tamponado": (255, 170, 60), "obstruido": (60, 60, 235)}  # BGR


def detectar(img, r_min, r_max, param2=15):
    """Círculos de Hough com a iluminação igualada."""
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cinza = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(cinza)
    cinza = cv2.medianBlur(cinza, 5)
    c = cv2.HoughCircles(cinza, cv2.HOUGH_GRADIENT, dp=1, minDist=int(r_min * 1.7), param1=120, param2=param2,
                         minRadius=r_min, maxRadius=r_max)
    return np.zeros((0, 3)) if c is None else c[0]


def filtrar_pela_grade(circulos, vizinhos_min=3):
    """Tubo de verdade tem vários vizinhos a uma distância de um passo; furo de flange e ruído, não."""
    xy = circulos[:, :2]
    arv = cKDTree(xy)
    d, _ = arv.query(xy, k=2)
    passo = float(np.median(d[:, 1]))                      # distância típica entre tubos vizinhos
    n_viz = np.array([len(v) - 1 for v in arv.query_ball_point(xy, passo * 1.35)])
    return circulos[n_viz >= vizinhos_min], passo


def medir_interior(img, circulos):
    """Brilho, saturação e textura no miolo de cada círculo (60% do raio)."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    medidas = []
    for x, y, r in circulos:
        ri = max(2, int(r * 0.6))
        x0, y0 = int(x) - ri, int(y) - ri
        rec_v = hsv[y0:y0 + 2 * ri + 1, x0:x0 + 2 * ri + 1, 2]
        rec_s = hsv[y0:y0 + 2 * ri + 1, x0:x0 + 2 * ri + 1, 1]
        rec_g = cinza[y0:y0 + 2 * ri + 1, x0:x0 + 2 * ri + 1]
        if rec_v.size == 0:
            medidas.append((0, 0, 0))
            continue
        yy, xx = np.mgrid[:rec_v.shape[0], :rec_v.shape[1]]
        m = (yy - ri) ** 2 + (xx - ri) ** 2 <= ri * ri
        medidas.append((float(rec_v[m].mean()), float(rec_s[m].mean()), float(rec_g[m].std())))
    return np.array(medidas)


def classificar(medidas, p_escuro=55, p_claro=93, p_saturacao=45):
    """Regras simples em cima do brilho e da saturação, relativas à própria foto (percentis).

    aberto: miolo escuro (dá para ver o fundo do tubo);
    tamponado: miolo claro e pouco saturado (disco de metal liso);
    obstruído: o resto (miolo de brilho médio, cor de depósito).
    """
    classes = np.full(len(medidas), "obstruido", dtype=object)
    if not len(medidas):
        return classes
    v, s = medidas[:, 0], medidas[:, 1]
    classes[v <= np.percentile(v, p_escuro)] = "aberto"
    classes[(v >= np.percentile(v, p_claro)) & (s < np.percentile(s, p_saturacao))] = "tamponado"
    return classes


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    caminho, r_min, r_max = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    img = cv2.imread(caminho)
    brutos = detectar(img, r_min, r_max)
    tubos, passo = filtrar_pela_grade(brutos)
    medidas = medir_interior(img, tubos)
    classes = classificar(medidas)
    nome = os.path.splitext(os.path.basename(caminho))[0].replace(" ", "_")
    print(f"{os.path.basename(caminho)}: {len(brutos)} círculos brutos -> {len(tubos)} depois do filtro da grade "
          f"(passo {passo:.1f} px)")
    for c in CORES:
        print(f"   {c:<10} {(classes == c).sum()}")
    vis = img.copy()
    for (x, y, r), c in zip(tubos, classes):
        cv2.circle(vis, (int(x), int(y)), int(r), CORES[c], 2)
    cv2.imwrite(os.path.join(AQUI, "saida", f"classes_{nome}.jpg"), vis)
    np.save(os.path.join(AQUI, "saida", f"tubos_{nome}.npy"), np.column_stack([tubos, medidas]))
