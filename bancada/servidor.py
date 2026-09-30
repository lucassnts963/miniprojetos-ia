"""Bancada: testa ao vivo os modelos dos miniprojetos no navegador.

    python bancada/servidor.py                  # abre http://127.0.0.1:8765
    python bancada/servidor.py --sem-navegador

Toda pasta NN-nome/ com um demo.py aparece na barra lateral. Cada projeto roda num
processo próprio (com a venv dele, se existir), então dependências e nomes de módulo
de um projeto não atrapalham os outros. Contrato do demo.py: ver bancada/README.md.
"""
import ast
import json
import os
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
FONTES = RAIZ / "ferramentas" / "youtube" / "fonts"
PORTA = int(os.environ.get("BANCADA_PORTA", 8765))
TIPOS = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
         ".css": "text/css; charset=utf-8", ".json": "application/json", ".svg": "image/svg+xml",
         ".png": "image/png", ".ttf": "font/ttf", ".woff2": "font/woff2"}


def ler_info(demo):
    """Lê o dicionário INFO do demo.py sem importar o projeto."""
    try:
        for no in ast.parse(demo.read_text(encoding="utf-8")).body:
            if isinstance(no, ast.Assign) and any(getattr(t, "id", None) == "INFO" for t in no.targets):
                return ast.literal_eval(no.value)
    except (SyntaxError, ValueError):
        pass
    return {}


def projetos():
    out = {}
    for d in sorted(RAIZ.glob("[0-9][0-9]-*")):
        demo = d / "demo.py"
        if demo.exists():
            info = ler_info(demo)
            out[d.name] = dict(id=d.name, numero=d.name[:2], nome=info.get("nome", d.name),
                               descricao=info.get("descricao", ""), painel=(d / "painel" / "painel.js").exists())
    return out


def python_do(pasta):
    for c in (pasta / "venv" / "Scripts" / "python.exe", pasta / "venv" / "bin" / "python"):
        if c.exists():
            return str(c)
    return sys.executable


class Worker:
    """Um processo por projeto, conversando por linhas JSON. Reinicia sozinho se o código mudar."""

    def __init__(self, pasta):
        self.pasta = pasta
        self.proc = None
        self.versao = None
        self.lock = threading.Lock()

    def _versao(self):
        return max(p.stat().st_mtime for p in self.pasta.glob("*.py"))

    def _iniciar(self):
        self.parar()
        self.proc = subprocess.Popen(
            [python_do(self.pasta), "-u", str(AQUI / "worker.py"), str(self.pasta)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding="utf-8", cwd=self.pasta)
        self.versao = self._versao()
        pronto = json.loads(self.proc.stdout.readline() or '{"erro": "o processo do projeto não iniciou"}')
        if "erro" in pronto:
            self.parar()
            raise RuntimeError(pronto["erro"])
        print(f"[bancada] {self.pasta.name} carregado ({python_do(self.pasta)})", flush=True)

    def chamar(self, acao, payload):
        with self.lock:
            if self.proc is None or self.proc.poll() is not None or self._versao() != self.versao:
                self._iniciar()
            self.proc.stdin.write(json.dumps({"acao": acao, "payload": payload}) + "\n")
            self.proc.stdin.flush()
            linha = self.proc.stdout.readline()
            if not linha:
                self.proc = None
                raise RuntimeError("o processo do projeto caiu (veja o terminal da bancada)")
            return json.loads(linha)

    def parar(self):
        if self.proc and self.proc.poll() is None:
            self.proc.kill()
        self.proc = None


WORKERS = {}
WORKERS_LOCK = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        if not str(args[1] if len(args) > 1 else "").startswith("2"):
            sys.stderr.write("[bancada] " + fmt % args + "\n")

    def _enviar(self, codigo, corpo, tipo):
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(corpo)

    def _json(self, codigo, obj):
        self._enviar(codigo, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def _arquivo(self, base, rel):
        base = base.resolve()
        alvo = (base / rel).resolve()
        if base not in alvo.parents or not alvo.is_file():
            return self._json(404, {"erro": "não encontrado"})
        self._enviar(200, alvo.read_bytes(), TIPOS.get(alvo.suffix.lower(), "application/octet-stream"))

    def do_GET(self):
        caminho = unquote(urlparse(self.path).path)
        if caminho == "/":
            return self._arquivo(AQUI / "static", "index.html")
        if caminho.startswith("/static/"):
            return self._arquivo(AQUI / "static", caminho[len("/static/"):])
        if caminho.startswith("/fonts/"):
            return self._arquivo(FONTES, caminho[len("/fonts/"):])
        if caminho == "/api/projetos":
            return self._json(200, list(projetos().values()))
        partes = caminho.strip("/").split("/", 2)
        if len(partes) == 3 and partes[0] == "p" and partes[1] in projetos():
            return self._arquivo(RAIZ / partes[1] / "painel", partes[2])
        self._json(404, {"erro": "não encontrado"})

    def do_POST(self):
        partes = unquote(urlparse(self.path).path).strip("/").split("/")
        if len(partes) != 3 or partes[0] != "api" or partes[1] not in projetos():
            return self._json(404, {"erro": "projeto ou rota desconhecida"})
        _, pid, acao = partes
        try:
            n = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(n) or b"{}")
            with WORKERS_LOCK:
                worker = WORKERS.setdefault(pid, Worker(RAIZ / pid))
            resp = worker.chamar(acao, payload)
        except Exception as e:  # noqa: BLE001 - qualquer falha vira mensagem no painel
            return self._json(500, {"erro": str(e)})
        if "erro" in resp:
            return self._json(500, resp)
        self._json(200, resp)


def main():
    servidor = ThreadingHTTPServer(("127.0.0.1", PORTA), Handler)
    url = f"http://127.0.0.1:{PORTA}"
    print(f"[bancada] {url}  ({len(projetos())} projeto(s) com demo.py)  Ctrl+C para sair", flush=True)
    if "--sem-navegador" not in sys.argv:
        threading.Timer(0.6, webbrowser.open, [url]).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        for w in WORKERS.values():
            w.parar()


if __name__ == "__main__":
    main()
