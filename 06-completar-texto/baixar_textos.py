"""Monta o texto de treino: artigos da Wikipédia em português sobre indústria, tecnologia e o dia a dia das empresas.

    python baixar_textos.py        # -> dados/corpus.txt (fica fora do git; o texto é CC BY-SA, da Wikipédia)

Busca artigos por assunto, baixa o texto puro de cada um e junta tudo num arquivo só.
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "dados", "corpus.txt")
API = "https://pt.wikipedia.org/w/api.php"
AGENTE = "miniprojetos-ia/1.0 (https://github.com/lucassnts963/miniprojetos-ia; projeto educativo)"

ASSUNTOS = """manutenção industrial, manutenção preventiva, bomba hidráulica, motor elétrico, trocador de calor, caldeira,
válvula, compressor, turbina, rolamento, soldagem, usinagem, siderurgia, mineração, alumínio, petróleo, refinaria,
indústria química, papel e celulose, engenharia mecânica, engenharia elétrica, engenharia civil, construção civil,
concreto, ponte, estrada, ferrovia, porto, logística, armazém, cadeia de suprimentos, transporte rodoviário, estoque,
qualidade, produção em massa, linha de montagem, automação industrial, robô industrial, sensor, controlador lógico,
segurança do trabalho, equipamento de proteção, energia elétrica, usina hidrelétrica, energia solar, energia eólica,
planejamento, gestão de projetos, cronograma, orçamento, contabilidade, administração, recursos humanos, contrato,
direito do trabalho, comércio, varejo, atacado, marketing, vendas, atendimento ao cliente, banco, economia do Brasil,
agricultura, pecuária, café, soja, alimento, hospital, medicina, enfermagem, farmácia, vacina, saúde pública,
computador, programação, banco de dados, internet, inteligência artificial, aprendizado de máquina, rede neural,
linguagem natural, matemática, estatística, probabilidade, física, química, biologia, geografia do Brasil,
história do Brasil, cidade, estado do Brasil, rio, clima, educação, universidade, escola""".replace("\n", " ").split(",")


def api(**p):
    p.update(format="json", formatversion="2")
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(p), headers={"User-Agent": AGENTE})
    for tentativa in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            time.sleep(2 + 3 * tentativa)
            erro = e
    raise erro


def limpar(t):
    t = re.split(r"\n==+ *(Referências|Ver também|Ligações externas|Bibliografia|Notas)[^\n]*==+", t)[0]
    t = re.sub(r"\n==+ *([^=\n]+?) *==+\n", r"\n\1.\n", t)          # título de seção vira frase curta
    t = re.sub(r"\{\displaystyle[^\n]*", " ", t)                    # resto de fórmula
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n{2,}", "\n", t).strip()


def main(por_assunto=40, alvo_mb=9.0):
    titulos = []
    for a in ASSUNTOS:
        r = api(action="query", list="search", srsearch=a.strip(), srlimit=por_assunto, srnamespace=0)
        titulos += [x["title"] for x in r["query"]["search"]]
        time.sleep(0.1)
    titulos = list(dict.fromkeys(titulos))
    print(len(titulos), "artigos encontrados", flush=True)
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    total = 0
    with open(SAIDA, "w", encoding="utf-8") as f:
        for i in range(0, len(titulos), 20):                         # 20 artigos por pedido
            textos, cont = {}, {}
            while True:                                              # o texto completo vem um artigo por resposta
                r = api(action="query", prop="extracts", explaintext=1, exlimit="max",
                        titles="|".join(titulos[i:i + 20]), **cont)
                for pg in r["query"]["pages"]:
                    if pg.get("extract"):
                        textos[pg["title"]] = pg["extract"]
                if "continue" not in r:
                    break
                cont = r["continue"]
            for t in map(limpar, textos.values()):
                if len(t) > 1500:
                    f.write(t + "\n\n")
                    total += len(t)
            if i % 400 == 0:
                print(f"{i}/{len(titulos)}  {total / 1e6:.1f} MB", flush=True)
            if total > alvo_mb * 1e6:
                break
            time.sleep(0.15)
    print(f"OK {SAIDA}  {total / 1e6:.1f} MB")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
