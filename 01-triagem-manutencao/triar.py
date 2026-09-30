"""Classifica chamados com o modelo treinado.

    python triar.py "vazamento de óleo na prensa"
    python triar.py            # modo interativo: digite um chamado por linha
"""
import sys

from modelo import Triagem

sys.stdout.reconfigure(encoding="utf-8")
if not sys.stdin.isatty():  # texto vindo de pipe/arquivo
    sys.stdin.reconfigure(encoding="utf-8")


def mostrar(r):
    print(f"\n  {r['texto']}")
    print(f"  -> {r['equipe']:<15} {r['conf_equipe']:.0%}   por causa de: {', '.join(r['motivo_equipe']) or '-'}")
    print(f"  -> {r['prioridade']:<15} {r['conf_prioridade']:.0%}   por causa de: {', '.join(r['motivo_prioridade']) or '-'}")


def main():
    modelo = Triagem.carregar()
    if len(sys.argv) > 1:
        mostrar(modelo.classificar(" ".join(sys.argv[1:])))
        return
    print("Digite o chamado (linha vazia para sair).")
    while True:
        try:
            texto = input("\n> ").strip()
        except EOFError:
            break
        if not texto:
            break
        mostrar(modelo.classificar(texto))


if __name__ == "__main__":
    main()
