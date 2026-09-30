"""Roda o demo.py de um projeto e atende pedidos da bancada por linhas JSON (stdin -> stdout).

Qualquer print do projeto vai para o stderr (terminal da bancada), para não quebrar o protocolo.
"""
import json
import os
import sys
import time
import traceback

pasta = sys.argv[1]
sys.path.insert(0, pasta)
os.chdir(pasta)
sys.stdin.reconfigure(encoding="utf-8")
canal = sys.stdout
canal.reconfigure(encoding="utf-8")
sys.stdout = sys.stderr


def _conv(o):
    if hasattr(o, "tolist"):  # arrays e números do NumPy
        return o.tolist()
    return str(o)


def enviar(obj):
    canal.write(json.dumps(obj, default=_conv) + "\n")
    canal.flush()


try:
    import demo
except Exception:  # noqa: BLE001
    enviar({"erro": "falha ao importar demo.py\n" + traceback.format_exc(limit=4)})
    sys.exit(1)

ACOES = dict(getattr(demo, "ACOES", {}))
enviar({"pronto": True})

for linha in sys.stdin:
    pedido = json.loads(linha)
    acao = pedido.get("acao")
    if acao == "__acoes":
        enviar({"resultado": sorted(ACOES), "ms": 0})
        continue
    fn = ACOES.get(acao)
    if fn is None:
        enviar({"erro": f"ação desconhecida: {acao} (disponíveis: {', '.join(sorted(ACOES))})"})
        continue
    try:
        t0 = time.perf_counter()
        resultado = fn(pedido.get("payload") or {})
        enviar({"resultado": resultado, "ms": round((time.perf_counter() - t0) * 1000, 1)})
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        enviar({"erro": traceback.format_exc(limit=3)})
