# Nem tudo precisa de IA: a menor rota pelas capitais, do zero

Código do vídeo do [@elucas.dev](https://youtube.com/@elucas.dev). Um arquivo que resolve o mesmo problema de cinco jeitos e compara distância, tempo e garantia: qual é a menor rota para visitar as 27 capitais do Brasil saindo de Belém?

```bash
pip install numpy scipy
python rota_do_zero.py
```

Saída esperada (os tempos mudam de máquina para máquina):
```
força bruta, 9 cidades: 0.2 s para 40,320 ordens
com 27 seriam 4.0e+26 ordens

vizinho mais próximo    13,397 km    0.00 s
+ 2-opt                 12,947 km    0.01 s
algoritmo genético      13,003 km    2.67 s
exato (com prova)       12,842 km    0.04 s
```

## Os passos
| Passo | O que faz | Garantia |
|---|---|---|
| 1 | lê `capitais.csv` e monta a matriz de distâncias (haversine) | |
| 2 | força bruta: testa todas as ordens | ótimo, mas só até ~10 cidades |
| 3 | vizinho mais próximo | nenhuma |
| 4 | 2-opt: inverte trechos enquanto a rota encurta | nenhuma |
| 5 | algoritmo genético (seleção por torneio, crossover OX, mutação por inversão) | nenhuma |
| 6 | exato: programação linear inteira, proibindo sub-rotas até sobrar uma rota só | ótimo, com prova |
| 7 | compara os métodos | |

## Por que não IA aqui
Medido com este código, rodando o genético 12 vezes (sementes 0 a 11):
- **não sabe quando chegou:** achou a melhor rota em 4 das 12 rodadas; nas outras ficou até 7,5% acima;
- **cada rodada dá uma resposta diferente** (é aleatório);
- **é lento:** segundos, contra centésimos de segundo do método exato, e piora rápido com mais cidades;
- **tem vários parâmetros para ajustar** (população, mutação, gerações, torneio);
- **não prova nada:** mesmo quando acerta, não tem como saber que acertou.

O método exato tem estrutura para explorar: cada rodada dá um custo que é um piso (nenhuma rota fica abaixo), e quando o piso vira uma rota de verdade, ela é a menor. É a ideia de Dantzig, Fulkerson e Johnson (1954).

O exato também tem limite: com centenas de cidades leva minutos, e com milhares não fecha. Aí entram as heurísticas (2-opt entre vizinhos e refinamentos), que estão no projeto completo, uma pasta acima.

IA faz sentido quando não existe fórmula: ler um texto, reconhecer algo numa imagem. Aqui o objetivo é uma conta exata com regras claras.
