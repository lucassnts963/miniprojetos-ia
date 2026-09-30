"""Versão do vídeo do LinkedIn gravada no painel da bancada (1080x1080, tema elucas.dev).

Precisa da bancada rodando (python bancada/servidor.py) e da venv de ferramentas/gravacao:
    ..\\..\\ferramentas\\gravacao\\venv\\Scripts\\python.exe gravar_painel.py
"""
import asyncio
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(RAIZ, "ferramentas", "gravacao"))
from gravador import Gravador  # noqa: E402

URL = "http://127.0.0.1:8765/?video=1#01-triagem-manutencao"
SAIDA = os.path.join(HERE, "painel_triagem.mp4")

CHAMADOS = [
    # (texto, espera depois de digitar)
    ("o motor da bomba 2 tá cheirando queimado", 2.6),
    ("vazamento de óleo na prensa, pingando no chão", 2.4),
    ("CLP da linha 3 não comunica com a IHM", 2.4),
    ("painel soltando fumaça, parou tudo", 2.4),
    ("calibrar o transmissor de nível na parada", 2.6),
]


async def versao_juntar():
    """Continuação da cena_triagem no vídeo combinado: sem repetir as legendas que a cena já mostrou."""
    saida = os.path.join(HERE, "painel_triagem_continua.mp4")
    async with Gravador(URL, saida) as g:
        await g.titulo("IA NA PRÁTICA", "Triagem de ordens de manutenção", "triagem de manutenção", "INDÚSTRIA")
        await g.esperar(0.6)
        await g.iniciar()
        await g.legenda("Por dentro, a decisão muda a cada tecla.", "E vem com o porquê.")
        await g.esperar(0.8)
        texto, espera = CHAMADOS[0]
        await g.digitar("#texto", texto)
        await g.esperar(espera)
        await g.clicar('#seg [data-m="pr"]')
        await g.esperar(1.8)
        await g.clicar('#seg [data-m="eq"]')
        await g.esperar(0.4)
        await g.legenda("Nada de caixa-preta:", "dá para ver o que pesou em cada decisão.")
        for texto, espera in (CHAMADOS[2], CHAMADOS[3], CHAMADOS[4]):
            await g.digitar("#texto", texto)
            await g.esperar(espera)
        await g.legenda("As aplicações são inúmeras.", "A sua imaginação é o limite.")
        await g.esperar(3.0)


async def main():
    if "--juntar" in sys.argv:
        return await versao_juntar()
    async with Gravador(URL, SAIDA) as g:
        await g.titulo("IA NA PRÁTICA", "Triagem de ordens de manutenção", "triagem de manutenção", "INDÚSTRIA")
        await g.esperar(0.6)
        await g.iniciar()
        await g.legenda("Você escreve o chamado do seu jeito.", "A IA diz a equipe, a prioridade e o porquê.")
        await g.esperar(1.4)

        texto, espera = CHAMADOS[0]
        await g.digitar("#texto", texto)
        await g.esperar(espera)
        # mostra que a prioridade também tem motivo
        await g.clicar('#seg [data-m="pr"]')
        await g.esperar(1.8)
        await g.clicar('#seg [data-m="eq"]')
        await g.esperar(0.5)

        await g.legenda("Cada chamado vai para a equipe certa,", "na hora.")
        for texto, espera in CHAMADOS[1:3]:
            await g.digitar("#texto", texto)
            await g.esperar(espera)

        await g.legenda("Nada de caixa-preta:", "dá para ver o que pesou em cada decisão.")
        for texto, espera in CHAMADOS[3:]:
            await g.digitar("#texto", texto)
            await g.esperar(espera)

        await g.legenda("Sem pagar uma LLM a cada chamado.", "A sua imaginação é o limite.")
        await g.esperar(3.2)


if __name__ == "__main__":
    asyncio.run(main())
