"""Primeiro teste: três detectores prontos nos três vídeos. Salva um quadro anotado de cada em testes/.

    python testar_detectores.py
"""
import sys, time, os, cv2, numpy as np
from detector import Detector, MODELOS
saida = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testes")
os.makedirs(saida, exist_ok=True)
videos = ["pexels_15170997", "pexels_4291727", "mixkit_23550"]
cores = {"rapido": (80, 200, 255), "medio": (80, 255, 120), "preciso": (77, 72, 229)}
for modelo in MODELOS:
    det = Detector(modelo, confianca=0.5)
    for v in videos:
        cap = cv2.VideoCapture(f"videos/{v}.mp4"); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        contagens, tempos, amostra = [], [], None
        for k, f in enumerate(np.linspace(0, n - 1, 12).astype(int)):
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(f)); ok, q = cap.read()
            if not ok: continue
            if max(q.shape[:2]) > 1280:  # reduz 4K para o tamanho de uma câmera comum
                e = 1280 / max(q.shape[:2]); q = cv2.resize(q, None, fx=e, fy=e)
            t0 = time.perf_counter(); cx = det.pessoas(q); dt = time.perf_counter() - t0
            if k > 0: tempos.append(dt)
            contagens.append(len(cx))
            if k == 6:
                for x1, y1, x2, y2, s in cx:
                    cv2.rectangle(q, (int(x1), int(y1)), (int(x2), int(y2)), cores[modelo], 3)
                    cv2.putText(q, f"{s:.2f}", (int(x1), int(y1) - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, cores[modelo], 2)
                amostra = q
        cv2.imwrite(os.path.join(saida, f"det_{modelo}_{v}.png"), amostra)
        print(f"{modelo:<8} {v:<16} pessoas por quadro {contagens}  {1/np.mean(tempos):5.1f} quadros/s ({det.dev})", flush=True)
