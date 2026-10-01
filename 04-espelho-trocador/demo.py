"""Ações da bancada para o espelho do trocador: contar tubos e separar aberto / obstruído / tamponado."""
import base64
import json
import os
import re
import time

import cv2
import numpy as np

from explorar import classificar, detectar, filtrar_pela_grade, medir_interior

INFO = {"nome": "Espelho do trocador", "descricao": "Foto do espelho → contagem de tubos, obstruídos e tamponados"}

HERE = os.path.dirname(os.path.abspath(__file__))
PASTAS = [os.path.join(os.path.dirname(HERE), "inbox"), os.path.join(HERE, "fotos")]   # onde procurar fotos
ROTULOS = os.path.join(HERE, "rotulos")    # correções feitas no painel, uma por foto (fora do git)
EXTENSOES = (".jpg", ".jpeg", ".png", ".webp")
LADO_TELA = 1500
CLASSES = ["aberto", "obstruido", "tamponado"]


def _fotos():
    achadas = {}
    for pasta in PASTAS:
        if os.path.isdir(pasta):
            for nome in sorted(os.listdir(pasta)):
                if nome.lower().endswith(EXTENSOES):
                    achadas[nome] = os.path.join(pasta, nome)
    return achadas


def _ler(nome):
    caminho = _fotos().get(nome)
    if not caminho:
        raise FileNotFoundError(f"foto não encontrada: {nome}")
    img = cv2.imdecode(np.fromfile(caminho, dtype=np.uint8), cv2.IMREAD_COLOR)   # aceita acento no caminho
    if img is None:
        raise ValueError(f"não consegui abrir {nome}")
    return img


def _arquivo_rotulos(nome):
    return os.path.join(ROTULOS, re.sub(r"[^\w.-]+", "_", nome) + ".json")


def info(_):
    fotos = []
    for nome, caminho in _fotos().items():
        img = _ler(nome)
        fotos.append(dict(nome=nome, largura=img.shape[1], altura=img.shape[0],
                          tem_rotulos=os.path.exists(_arquivo_rotulos(nome))))
    return dict(fotos=fotos, classes=CLASSES, pastas=["inbox/", "04-espelho-trocador/fotos/"])


def imagem(p):
    """A foto reduzida para a tela (JPEG em base64) e os rótulos salvos, se existirem."""
    img = _ler(p["foto"])
    e = min(1.0, LADO_TELA / max(img.shape[:2]))
    tela = cv2.resize(img, None, fx=e, fy=e) if e < 1 else img
    ok, jpg = cv2.imencode(".jpg", tela, [cv2.IMWRITE_JPEG_QUALITY, 88])
    resp = dict(jpeg=base64.b64encode(jpg.tobytes()).decode("ascii"), largura=img.shape[1], altura=img.shape[0])
    arq = _arquivo_rotulos(p["foto"])
    if os.path.exists(arq):
        with open(arq, encoding="utf-8") as f:
            resp["rotulos"] = json.load(f)["tubos"]
    return resp


def analisar(p):
    """Detecta os tubos e classifica o miolo de cada um. Coordenadas e raio em pixels da foto original."""
    img = _ler(p["foto"])
    t0 = time.perf_counter()
    brutos = detectar(img, int(p.get("r_min", 8)), int(p.get("r_max", 16)), int(p.get("sensibilidade", 15)))
    if len(brutos) < 5:
        return dict(tubos=[], brutos=int(len(brutos)), passo=None, segundos=round(time.perf_counter() - t0, 2),
                    contagem={c: 0 for c in CLASSES})
    tubos, passo = filtrar_pela_grade(brutos, int(p.get("vizinhos", 3)))
    medidas = medir_interior(img, tubos)
    classes = classificar(medidas, float(p.get("p_escuro", 55)), float(p.get("p_claro", 93)),
                          float(p.get("p_saturacao", 45)))
    saida = [dict(x=round(float(x), 1), y=round(float(y), 1), r=round(float(r), 1), classe=str(c))
             for (x, y, r), c in zip(tubos, classes)]
    return dict(tubos=saida, brutos=int(len(brutos)), passo=round(passo, 1),
                segundos=round(time.perf_counter() - t0, 2),
                contagem={c: int((classes == c).sum()) for c in CLASSES})


def salvar_rotulos(p):
    """Guarda os tubos conferidos no painel (posição, raio e classe). É o gabarito para medir e treinar depois."""
    tubos = [dict(x=float(t["x"]), y=float(t["y"]), r=float(t["r"]), classe=t["classe"]) for t in p["tubos"]
             if t.get("classe") in CLASSES]
    os.makedirs(ROTULOS, exist_ok=True)
    with open(_arquivo_rotulos(p["foto"]), "w", encoding="utf-8") as f:
        json.dump(dict(foto=p["foto"], tubos=tubos), f, ensure_ascii=False)
    return dict(salvos=len(tubos), contagem={c: sum(t["classe"] == c for t in tubos) for c in CLASSES})


def apagar_rotulos(p):
    arq = _arquivo_rotulos(p["foto"])
    if os.path.exists(arq):
        os.remove(arq)
    return dict(apagado=True)


def enviar(p):
    """Recebe uma foto nova pelo painel e guarda em fotos/."""
    nome = re.sub(r"[^\w. ()-]+", "_", os.path.basename(p["nome"]))
    if not nome.lower().endswith(EXTENSOES):
        raise ValueError("envie uma imagem .jpg, .jpeg, .png ou .webp")
    dados = base64.b64decode(p["base64"])
    if cv2.imdecode(np.frombuffer(dados, np.uint8), cv2.IMREAD_COLOR) is None:
        raise ValueError("o arquivo não é uma imagem válida")
    os.makedirs(PASTAS[1], exist_ok=True)
    with open(os.path.join(PASTAS[1], nome), "wb") as f:
        f.write(dados)
    return dict(nome=nome)


ACOES = {"info": info, "imagem": imagem, "analisar": analisar, "salvar_rotulos": salvar_rotulos,
         "apagar_rotulos": apagar_rotulos, "enviar": enviar}
