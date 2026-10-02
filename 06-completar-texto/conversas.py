"""Transforma o texto da base em conversas de treino, para a rede aprender o formato de chat.

Uma LLM de chat continua sendo uma máquina de completar texto: ela só foi treinada também em textos
com cara de conversa. Aqui as conversas saem da própria base, sem nada escrito à mão:

    Pergunta: O que é manutenção preventiva?
    Resposta: <as primeiras frases do artigo>

    python conversas.py        # mostra quantas conversas saíram e alguns exemplos
"""
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
SUJEITO = re.compile(r"^([A-ZÁÉÍÓÚÂÊÔÃÕÇ][^.,;:()\n]{2,48}?)(?: \([^)\n]*\))?,? (é|são|foi|foram|era|eram) "
                     r"(?:um|uma|o|a|os|as|uns|umas|considerad[oa]s?|definid[oa]s?) ")
FIM_DE_FRASE = re.compile(r"(?<=[a-zà-ú\)\d])\. (?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])")


def _comeco(texto, limite=330):
    """As primeiras frases do texto, até perto de `limite` caracteres."""
    frases, total = [], 0
    for f in FIM_DE_FRASE.split(texto):
        if frases and total + len(f) > limite:
            break
        frases.append(f)
        total += len(f)
    r = ". ".join(frases).strip()
    return r if r.endswith(".") else r + "."


def formato(pergunta, resposta=None):
    return f"Pergunta: {pergunta}\nResposta:" + ("" if resposta is None else f" {resposta}\n\n")


def montar(texto):
    """-> lista de conversas (texto pronto para treino), tiradas dos artigos."""
    conversas = []
    for artigo in texto.split("\n\n"):
        linhas = [l.strip() for l in artigo.split("\n") if l.strip()]
        if not linhas:
            continue
        m = SUJEITO.match(linhas[0])
        if not m:
            continue
        x, verbo = re.sub(r"^(Uma?|Os?|As?) ", "", m.group(1).strip()), m.group(2)
        resposta = _comeco(linhas[0])
        if len(resposta) < 60:
            continue
        o_que = "O que são" if verbo in ("são", "foram", "eram") else "O que é"
        for pergunta in (f"{o_que} {x}?", f"Fale sobre {x}.", f"Explique {x}."):
            conversas.append(formato(pergunta, resposta))
        for titulo, corpo in zip(linhas[1:], linhas[2:]):          # seções: um título curto seguido de um parágrafo
            if len(titulo) < 45 and titulo.endswith(".") and titulo.count(".") == 1 and len(corpo) > 200:
                conversas.append(formato(f"Fale sobre {x}: {titulo[:-1].lower()}.", _comeco(corpo)))
    return conversas


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    with open(os.path.join(AQUI, "dados", "corpus.txt"), encoding="utf-8") as f:
        c = montar(f.read())
    print(len(c), "conversas")
    for i in (0, 3, 400, 2001):
        print(c[i % len(c)])
