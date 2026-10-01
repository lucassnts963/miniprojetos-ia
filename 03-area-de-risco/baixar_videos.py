"""Baixa os vídeos de teste (bancos de vídeo com licença livre). Eles ficam fora do git.

    python baixar_videos.py

Licenças: Pexels License e Mixkit Stock Video Free License permitem uso gratuito, inclusive
comercial, sem atribuição. Não permitem redistribuir os vídeos originais soltos, por isso o
repositório guarda só este script. Há pessoas identificáveis: em material publicado, usar
planos abertos ou borrar os rostos.
"""
import os
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
AGENTE = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
VIDEOS = {
    # plano aberto, pessoas longe da câmera (o mais parecido com câmera de segurança)
    "pexels_15170997.mp4": "https://www.pexels.com/download/video/15170997/",
    # vista de cima: empilhadeira e pessoas
    "pexels_4291727.mp4": "https://www.pexels.com/download/video/4291727/",
    # três pessoas andando de frente para a câmera, de perto
    "mixkit_23550.mp4": "https://assets.mixkit.co/videos/23550/23550-720.mp4",
}

if __name__ == "__main__":
    os.makedirs(os.path.join(AQUI, "videos"), exist_ok=True)
    for nome, url in VIDEOS.items():
        destino = os.path.join(AQUI, "videos", nome)
        if os.path.exists(destino):
            print("já existe:", nome)
            continue
        req = urllib.request.Request(url, headers={"User-Agent": AGENTE})
        with urllib.request.urlopen(req) as r, open(destino, "wb") as f:
            f.write(r.read())
        print(f"baixado: {nome} ({os.path.getsize(destino) / 1e6:.1f} MB)")
