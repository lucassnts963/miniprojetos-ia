# Mundo simulado

Motor 2D simples, visto de cima, em NumPy puro. Serve de palco para os miniprojetos que precisam de simulação: você monta o mundo com objetos, solta corpos nele e mede o que acontece. Unidades em metros e segundos.

Primeiro uso: [05 · Carro autônomo](../05-carro-autonomo/).

## O que tem
| Arquivo | O que faz |
|---|---|
| `mundo.py` | `Mundo`: guarda o que é fixo (paredes, caixas, cones) e responde a três perguntas: até onde um raio enxerga, quem encostou em alguma coisa e como tirar um corpo de dentro da parede |
| `objetos.py` | o que se move: `Carros` (volante e acelerador, bate e para) e `Bolas` (quicam nas paredes) |
| `pistas.py` | `Pista`: gera pistas fechadas a partir de alguns pontos e mede o progresso de cada carro |
| `teste_mundo.py` | testes (`python mundo/teste_mundo.py`) |

Tudo trabalha em lote: `Carros(40, ...)` são quarenta carros em arrays, e cada passo da simulação move todos de uma vez. É isso que deixa uma geração inteira rodar em um ou dois segundos.

## Exemplo
```python
import numpy as np
from mundo import Mundo, Carros

mundo = Mundo(100, 60).bordas()            # sala de 100 x 60 m fechada por paredes
mundo.caixa(50, 30, largura=4, altura=4)   # uma caixa no meio
mundo.cone(30, 20)                         # um cone

carros = Carros(10, x=10, y=30, ang=0.0)   # dez carros na mesma largada
angulos = np.radians([-45, 0, 45])
for _ in range(200):
    visto = carros.sensores(mundo, angulos, alcance=30)          # (10, 3), de 0 (colado) a 1 (livre)
    volante = visto[:, 2] - visto[:, 0]                          # regra simples: vira para o lado mais livre
    carros.passo(mundo, volante, np.full(10, 0.5), dt=0.05)      # quem bate para (carros.vivo)
```

## Para criar outra situação
- **Outro cenário** (armazém, pátio, corredor): monte com `parede`, `linha`, `caixa`, `cone` e `bordas`. `mundo.descrever()` devolve tudo em formato simples, pronto para o painel desenhar; `mundo.adicionar({...})` recebe objetos vindos do painel.
- **Outro corpo** (empilhadeira, robô, pessoa andando): uma classe nova em `objetos.py` com o estado em arrays e um `passo(mundo, dt)` que usa `mundo.raios`, `mundo.toca` e `mundo.empurrar`. `Carros` e `Bolas` são os dois modelos.
- **Outro objetivo:** a nota de cada corpo é decidida por quem usa o mundo (no carro, os metros percorridos na pista).

## Limites (de propósito)
- 2D, visto de cima. Sem massa, atrito de pneu ou derrapagem: o carro segue o modelo de bicicleta.
- A colisão do corpo é um círculo. Os corpos não batem uns nos outros, só no cenário.
- Os objetos do cenário são fixos: nada é empurrado.
