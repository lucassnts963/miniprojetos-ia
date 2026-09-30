"""Grava a bancada (modo vídeo) em MP4, pilotando o Chrome instalado com o Playwright.

Captura por screencast (CDP): o Chrome manda um quadro JPEG a cada mudança na tela, com
horário. Cada quadro fica na tela até o próximo, então o vídeo sai no tempo real da
interação, sem depender da velocidade de captura. Depois o ffmpeg normaliza para 30 fps.

Uso (venv desta pasta, que tem o playwright):
    from gravador import Gravador
    async with Gravador("http://127.0.0.1:8765/?video=1#01-...", saida) as g:
        await g.legenda("linha 1", "linha 2")
        await g.digitar("#texto", "o motor ...")
        await g.esperar(2)
"""
import asyncio
import base64
import os
import shutil
import subprocess
import tempfile

from playwright.async_api import async_playwright

FFMPEG = shutil.which("ffmpeg") or r"C:\programs\bin\ffmpeg.exe"


class Gravador:
    def __init__(self, url, saida, tamanho=(1080, 1080), fade=0.4):
        self.url, self.saida, self.tamanho, self.fade = url, saida, tamanho, fade
        self.quadros = []  # (timestamp em s, jpeg em bytes)

    async def __aenter__(self):
        self._pw = await async_playwright().start()
        self.browser = await self._pw.chromium.launch(channel="chrome", headless=True)
        w, h = self.tamanho
        self.ctx = await self.browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
        self.page = await self.ctx.new_page()
        await self.page.goto(self.url)
        await self.page.wait_for_load_state("networkidle")
        await self.page.evaluate("document.fonts.ready.then(() => true)")
        return self

    async def iniciar(self):
        """Começa a gravar (chame depois de deixar a tela no estado inicial)."""
        self.cdp = await self.ctx.new_cdp_session(self.page)

        async def quadro(p):
            self.quadros.append((p["metadata"]["timestamp"], base64.b64decode(p["data"])))
            try:
                await self.cdp.send("Page.screencastFrameAck", {"sessionId": p["sessionId"]})
            except Exception:  # noqa: BLE001 - sessão encerrada no fim da gravação
                pass

        self.cdp.on("Page.screencastFrame", lambda p: asyncio.ensure_future(quadro(p)))
        w, h = self.tamanho
        await self.cdp.send("Page.startScreencast", {"format": "jpeg", "quality": 95,
                                                     "maxWidth": w, "maxHeight": h, "everyNthFrame": 1})
        # garante um quadro inicial mesmo sem mudança na tela
        await self.page.evaluate("document.body.style.outline = '0px solid transparent'")
        self.t_inicio = asyncio.get_event_loop().time()

    # ---------- ações do roteiro ----------
    async def esperar(self, s):
        await asyncio.sleep(s)

    async def js(self, codigo, *args):
        return await self.page.evaluate(codigo, *args)

    async def legenda(self, l1="", l2=""):
        await self.js("([a, b]) => window.bancada.legenda(a, b)", [l1, l2])

    async def titulo(self, eyebrow, titulo, capitulo="", selo=""):
        await self.js("([a, b, c, d]) => window.bancada.titulo(a, b, c, d)", [eyebrow, titulo, capitulo, selo])

    async def clicar(self, seletor):
        await self.page.click(seletor)

    async def digitar(self, seletor, texto, atraso=0.055, substituir=True):
        """Digita como uma pessoa. Com substituir, seleciona o que havia antes."""
        await self.page.click(seletor)
        if substituir:
            await self.page.keyboard.press("Control+A")
        await self.page.keyboard.type(texto, delay=atraso * 1000)

    # ---------- fim ----------
    async def __aexit__(self, *exc):
        try:
            await asyncio.sleep(0.3)
            await self.cdp.send("Page.stopScreencast")
            t_fim = self.quadros[-1][0] + 0.5 if self.quadros else 0
        finally:
            await self.browser.close()
            await self._pw.stop()
        if exc[0] is None:
            self._montar(t_fim)

    def _montar(self, t_fim):
        if not self.quadros:
            raise RuntimeError("nenhum quadro capturado")
        pasta = tempfile.mkdtemp(prefix="gravacao_")
        lista = os.path.join(pasta, "quadros.txt")
        qs = sorted(self.quadros)
        with open(lista, "w", encoding="utf-8") as f:
            for i, (ts, jpg) in enumerate(qs):
                nome = os.path.join(pasta, f"q{i:05d}.jpg")
                with open(nome, "wb") as g:
                    g.write(jpg)
                dur = (qs[i + 1][0] if i + 1 < len(qs) else t_fim) - ts
                f.write(f"file '{nome.replace(os.sep, '/')}'\nduration {max(dur, 0.001):.4f}\n")
            f.write(f"file '{os.path.join(pasta, f'q{len(qs) - 1:05d}.jpg').replace(os.sep, '/')}'\n")
        total = t_fim - qs[0][0]
        fades = f"fade=t=in:st=0:d={self.fade},fade=t=out:st={total - self.fade:.3f}:d={self.fade}"
        subprocess.run([FFMPEG, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista,
                        "-vf", f"fps=30,{fades},format=yuv420p", "-c:v", "libx264", "-preset", "medium",
                        "-crf", "16", "-an", self.saida], check=True)
        shutil.rmtree(pasta, ignore_errors=True)
        print(f"OK {self.saida}  ({total:.1f} s, {len(qs)} quadros capturados)")
