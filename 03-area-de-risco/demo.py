"""Ações da bancada para "pessoa em área de risco" (ver ../bancada/README.md)."""
import base64
import os
import time

import cv2

from detector import MODELOS, Detector

INFO = {"nome": "Pessoa em área de risco", "descricao": "Vídeo + área desenhada → alerta quando alguém entra"}

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEOS = os.path.join(HERE, "videos")
LADO_DETECCAO = 1280   # o quadro é reduzido para este tamanho antes de detectar (como uma câmera comum)
LADO_TELA = 960        # tamanho da imagem enviada para o painel
CONF_MINIMA = 0.2      # guarda as detecções acima disso; o painel filtra pela confiança escolhida

DESCRICOES = {
    "pexels_15170997.mp4": "Plano aberto: pessoas longe da câmera",
    "pexels_4291727.mp4": "Vista de cima: empilhadeira e pessoas",
    "mixkit_23550.mp4": "Perto: três pessoas de frente",
}
# áreas de exemplo (x, y de 0 a 1 na imagem); no painel dá para desenhar outra
AREAS_EXEMPLO = {
    "pexels_15170997.mp4": [[0.02, 0.485], [0.50, 0.485], [0.72, 0.56], [0.02, 0.58]],
    "pexels_4291727.mp4": [[0.40, 0.08], [0.98, 0.08], [0.98, 0.95], [0.58, 0.95]],
    "mixkit_23550.mp4": [[0.20, 0.72], [0.80, 0.72], [0.96, 1.0], [0.04, 1.0]],
}

_detectores = {}
_capturas = {}
_cache = {}   # (video, modelo, quadro) -> [(x1, y1, x2, y2, confiança)] em coordenadas de 0 a 1


def _detector(modelo):
    if modelo not in _detectores:
        _detectores[modelo] = Detector(modelo, confianca=CONF_MINIMA)
    return _detectores[modelo]


def _captura(video):
    if video not in _capturas:
        caminho = os.path.join(VIDEOS, os.path.basename(video))
        if not os.path.exists(caminho):
            raise FileNotFoundError(f"{video} não está em videos/ (rode baixar_videos.py)")
        _capturas[video] = cv2.VideoCapture(caminho)
    return _capturas[video]


def _ler(video, indice):
    cap = _captura(video)
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(indice))
    ok, quadro = cap.read()
    if not ok:
        raise ValueError(f"não consegui ler o quadro {indice} de {video}")
    return quadro


def _redimensionar(quadro, lado):
    e = lado / max(quadro.shape[:2])
    return cv2.resize(quadro, None, fx=e, fy=e) if e < 1 else quadro


def _detectar(video, modelo, indice, quadro=None):
    chave = (video, modelo, int(indice))
    if chave not in _cache:
        q = _redimensionar(quadro if quadro is not None else _ler(video, indice), LADO_DETECCAO)
        h, w = q.shape[:2]
        _cache[chave] = [(x1 / w, y1 / h, x2 / w, y2 / h, s) for x1, y1, x2, y2, s in _detector(modelo).pessoas(q)]
    return _cache[chave]


def dentro(ponto, poligono):
    """O ponto está dentro do polígono? (traça uma linha para a direita e conta os cruzamentos)"""
    x, y = ponto
    n, cruzou = len(poligono), False
    for i in range(n):
        (x1, y1), (x2, y2) = poligono[i], poligono[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            cruzou = not cruzou
    return cruzou


def _avaliar(caixas, confianca, poligono):
    """Filtra pela confiança e marca quem está na área: vale o ponto dos pés (meio da base da caixa)."""
    saida = []
    for x1, y1, x2, y2, s in caixas:
        if s < confianca:
            continue
        pes = ((x1 + x2) / 2, y2)
        saida.append(dict(caixa=[round(v, 4) for v in (x1, y1, x2, y2)], confianca=round(s, 3),
                          pes=[round(pes[0], 4), round(pes[1], 4)],
                          na_area=bool(poligono and len(poligono) >= 3 and dentro(pes, poligono))))
    return saida


def info(_):
    videos = []
    for nome in sorted(os.listdir(VIDEOS)) if os.path.isdir(VIDEOS) else []:
        if not nome.endswith(".mp4"):
            continue
        cap = _captura(nome)
        n, fps = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), cap.get(cv2.CAP_PROP_FPS) or 25
        videos.append(dict(arquivo=nome, descricao=DESCRICOES.get(nome, nome), quadros=n, fps=round(fps, 2),
                           largura=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), altura=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                           area_exemplo=AREAS_EXEMPLO.get(nome, [])))
    return dict(videos=videos, modelos=list(MODELOS), dispositivo=_detector("medio").dev)


def quadro(p):
    """Um quadro do vídeo (JPEG em base64) com as pessoas detectadas e quem está na área."""
    video, indice, modelo = p["video"], int(p.get("indice", 0)), p.get("modelo", "medio")
    bruto = _ler(video, indice)
    t0 = time.perf_counter()
    ja_tinha = (video, modelo, indice) in _cache
    caixas = _detectar(video, modelo, indice, bruto)
    ms = (time.perf_counter() - t0) * 1000
    pessoas = _avaliar(caixas, float(p.get("confianca", 0.5)), p.get("poligono") or [])
    resp = dict(indice=indice, pessoas=pessoas, ms_deteccao=None if ja_tinha else round(ms, 1))
    if p.get("imagem", True):
        ok, jpg = cv2.imencode(".jpg", _redimensionar(bruto, LADO_TELA), [cv2.IMWRITE_JPEG_QUALITY, 82])
        resp["jpeg"] = base64.b64encode(jpg.tobytes()).decode("ascii")
    return resp


def analisar(p):
    """Percorre o vídeo (um quadro a cada `passo`) e monta a linha do tempo de pessoas na área e os alertas."""
    video, modelo = p["video"], p.get("modelo", "medio")
    confianca, poligono = float(p.get("confianca", 0.5)), p.get("poligono") or []
    passo, persistencia = max(1, int(p.get("passo", 5))), max(1, int(p.get("persistencia", 2)))
    cap = _captura(video)
    total, fps = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), cap.get(cv2.CAP_PROP_FPS) or 25
    t0 = time.perf_counter()
    novos = 0
    linha = []
    seguidos = 0
    for indice in range(0, total, passo):
        if (video, modelo, indice) not in _cache:
            novos += 1
        pessoas = _avaliar(_detectar(video, modelo, indice), confianca, poligono)
        n_area = sum(x["na_area"] for x in pessoas)
        seguidos = seguidos + 1 if n_area else 0
        # só alerta depois de alguns quadros seguidos com gente na área: uma detecção solta não dispara
        linha.append(dict(indice=indice, t=round(indice / fps, 2), pessoas=len(pessoas), na_area=n_area,
                          alerta=seguidos >= persistencia))
    eventos, aberto = [], None
    for x in linha:
        if x["alerta"] and aberto is None:
            aberto = x
        elif not x["alerta"] and aberto is not None:
            eventos.append(dict(inicio=aberto["t"], fim=x["t"], indice=aberto["indice"]))
            aberto = None
    if aberto is not None:
        eventos.append(dict(inicio=aberto["t"], fim=linha[-1]["t"], indice=aberto["indice"]))
    seg = time.perf_counter() - t0
    return dict(linha=linha, eventos=eventos, passo=passo, fps=round(fps, 2), quadros_analisados=len(linha),
                segundos=round(seg, 1), quadros_por_s=round(novos / seg, 1) if novos and seg > 0 else None,
                tempo_com_alerta=round(sum(e["fim"] - e["inicio"] for e in eventos), 1),
                duracao=round(total / fps, 1))


ACOES = {"info": info, "quadro": quadro, "analisar": analisar}
