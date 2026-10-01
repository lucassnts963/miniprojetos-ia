"""Detector de pessoas pronto (pré-treinado no COCO, via torchvision). Nada é treinado aqui.

    from detector import Detector
    det = Detector("rapido")            # ou "preciso"
    caixas = det.pessoas(quadro_bgr)    # [(x1, y1, x2, y2, confiança), ...]
"""
import torch
from torchvision.models import detection as D

PESSOA = 1  # índice da classe "person" no COCO
MODELOS = {
    # leve: roda em tempo real até em CPU, mas perde pessoas pequenas
    "rapido": (D.ssdlite320_mobilenet_v3_large, D.SSDLite320_MobileNet_V3_Large_Weights.DEFAULT),
    # intermediário
    "medio": (D.fasterrcnn_mobilenet_v3_large_fpn, D.FasterRCNN_MobileNet_V3_Large_FPN_Weights.DEFAULT),
    # mais pesado e mais preciso
    "preciso": (D.fasterrcnn_resnet50_fpn_v2, D.FasterRCNN_ResNet50_FPN_V2_Weights.DEFAULT),
}


class Detector:
    def __init__(self, modelo="medio", confianca=0.5, dispositivo=None):
        construtor, pesos = MODELOS[modelo]
        self.nome = modelo
        self.confianca = confianca
        self.dev = dispositivo or ("cuda" if torch.cuda.is_available() else "cpu")
        self.rede = construtor(weights=pesos).eval().to(self.dev)

    @torch.no_grad()
    def pessoas(self, quadro_bgr):
        """Caixas (x1, y1, x2, y2, confiança) das pessoas num quadro do OpenCV (BGR)."""
        rgb = torch.from_numpy(quadro_bgr[:, :, ::-1].copy()).permute(2, 0, 1).float().div(255).to(self.dev)
        r = self.rede([rgb])[0]
        ok = (r["labels"] == PESSOA) & (r["scores"] >= self.confianca)
        caixas = r["boxes"][ok].cpu().tolist()
        notas = r["scores"][ok].cpu().tolist()
        return [(*c, s) for c, s in zip(caixas, notas)]
