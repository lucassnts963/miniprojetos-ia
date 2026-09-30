# 02 · Menor rota para visitar todas as cidades

Dada uma cidade de partida, em que ordem visitar todos os municípios (ou só alguns estados, ou só as capitais) percorrendo a menor distância? É o problema do caixeiro-viajante.

![rota saindo de Belém pelos 5.570 municípios](rota_belem.png)

## Dá para achar a menor rota?
| Tamanho | Resposta | Exemplo |
|---|---|---|
| até algumas centenas de cidades | **sim, com prova** (`exato.py`) | 27 capitais: 0,1 s · Paraíba (223): 15 s · Paraná (399): 7 min |
| milhares de cidades | **rota muito boa em segundos**, sem prova de que é a menor (`rota.py`) | Brasil (5.570): 129.201 km em ~1 min |

- O problema é NP-difícil: não se conhece um jeito de provar o ótimo para milhares de cidades num tempo razoável num computador comum.
- Para ter noção da qualidade, calibrei a heurística nos estados onde o ótimo foi provado: ela ficou **0,4% a 1,4% acima do ótimo** (Paraná, Paraíba, Sergipe) e acertou em cheio Rondônia e as capitais.
- Existe um limite inferior garantido, a árvore geradora mínima, e nenhuma rota fica abaixo dele. Para o Brasil, a rota está no máximo 14% acima do ótimo. Esse é o pior caso teórico; pelo que se viu nos estados, deve ficar bem mais perto.
- **Distância em linha reta** (sobre a esfera da Terra), não por estrada. Rota por estrada precisaria de um serviço de roteamento (ex.: OSRM) e de uma matriz de distâncias rodoviárias.

## Os dados
`dados/cidades.csv`: 5.571 municípios com a coordenada da sede, a partir de [kelvins/municipios-brasileiros](https://github.com/kelvins/municipios-brasileiros) (MIT). Validação: 69 municípios sorteados caíram 100% dentro dos polígonos oficiais da malha do IBGE.

- Fernando de Noronha fica fora por padrão (não se chega por terra). Use `--incluir-ilhas` para incluir.
- **Base descartada:** um `latlon.csv` anterior, com distritos, tinha 757 municípios deslocados mais de 100 km (Campo Grande/AL em Mato Grosso do Sul, Curral de Cima/PB a 3.747 km, pontos no oceano). O `python dados.py --auditar arquivo.csv` foi o que achou esses erros e serve para checar qualquer base nova.

## Como rodar
```bash
pip install -r requirements.txt
python dados.py                                          # prepara dados/cidades.csv (baixa a base se precisar)
python rota.py --inicio "Belém/PA"                       # Brasil inteiro -> rota.csv
python rota.py --inicio "Curitiba/PR" --estados PR SC    # só alguns estados
python rota.py --inicio "Belém/PA" --volta --tempo 120   # voltando ao início, com 2 min de refinamento
python exato.py --inicio "Belém/PA" --capitais           # ótimo comprovado
python genetico.py --inicio "Belém/PA" --capitais        # algoritmo genético (o da cobrinha)
python teste_rota.py                                     # testes
```

## Como funciona
| Arquivo | Método |
|---|---|
| `rota.py` | vizinho mais próximo → 2-opt (descruza trechos) + Or-opt (move blocos de 1 a 3 cidades) só entre cidades vizinhas → busca local iterada (bagunça um trecho curto e só fica se melhorar). Limite inferior pela árvore geradora mínima exata (triangulação de Delaunay na esfera). |
| `exato.py` | programação linear inteira: cada ligação é 0/1, cada cidade tem duas ligações; toda sub-rota que aparece vira uma restrição proibindo ela, até sobrar uma rota só (o ótimo, com prova). |
| `genetico.py` | o mesmo algoritmo genético da cobrinha, com rotas no lugar de cérebros: torneio, crossover OX (feito para permutações), mutação por inversão e por troca de lugar, elitismo. Bom para dezenas de cidades; nas capitais chegou ao ótimo comprovado. |
| `dados.py` | base do IBGE + auditor de coordenadas suspeitas |
