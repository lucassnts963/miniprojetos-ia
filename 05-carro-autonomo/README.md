# 05 · Carro autônomo: uma rede neural aprende a dirigir sozinha

Ninguém ensina o carro a dirigir. Cada carro da população tem uma rede neural pequena com pesos sorteados; todos correm na mesma pista, e os que vão mais longe deixam filhos para a geração seguinte. É o mesmo princípio da [cobrinha](https://github.com/lucassnts963/snake), agora num [mundo simulado](../mundo/) feito para ser reaproveitado.

**Estado:** código e painel da bancada prontos. Faltam o post e os vídeos.

## Testar ao vivo
```bash
python ../bancada/servidor.py   # http://127.0.0.1:8765, projeto 05
```
- **Evoluir:** roda geração após geração e mostra a corrida de cada uma. O carro vermelho é o que foi mais longe; as linhas verdes são os sensores dele.
- **Treino rápido:** mostra só uma geração a cada cinco, para chegar logo num carro que dirige.
- **Objetos na pista:** escolha cone ou caixa e clique na pista. Os carros passam a treinar com eles.
- **Testar o campeão:** solta o melhor carro sozinho numa pista, que pode ser diferente da do treino.
- **O que o líder vê, pensa e faz:** a rede acendendo ao vivo, dos sensores até o volante e o acelerador.

Pelo terminal: `python treinar.py --pista circuito --geracoes 30` (salva o melhor em `cerebro.npz`).

## Como funciona
| Arquivo | O que faz |
|---|---|
| `cerebro.py` | a rede: 7 sensores de distância + a velocidade → 8 neurônios → volante e acelerador. São 90 números por carro (o genoma) |
| `evolucao.py` | `simular`: solta a população na pista e mede os metros de cada carro. `proxima_geracao`: os 4 melhores passam direto; o resto nasce de dois pais escolhidos por torneio, com mutação |
| `treinar.py` | treino pelo terminal |
| `demo.py` + `painel/` | painel da bancada |
| [`../mundo/`](../mundo/) | o mundo: pista, obstáculos, sensores, colisão e o modelo do carro |

- **A nota de cada carro** é o quanto ele avançou ao longo da linha do meio da pista. Só conta para a frente: dar ré ou cortar caminho não vale.
- **Sai da corrida** quem bate ou fica 4 segundos sem avançar.
- **Não há gradiente nem exemplo de "como dirigir":** a única informação é quem foi mais longe.

## Resultado
Medido com 40 carros, 30 s de pista por geração e 6 sorteios diferentes por pista (40 gerações cada):

| Pista | Primeira volta completa | Depois de 40 gerações |
|---|---|---|
| Oval | geração 1 a 3 | 3,1 voltas em 30 s |
| Circuito | geração 1 a 9 | 3,0 voltas |
| Serpente | geração 5 a 32 | 2,6 voltas |

- Nos 18 treinos o carro aprendeu a dar voltas. Uma geração leva de 1 a 3 segundos para simular.
- **Onde treina importa** (um treino de 30 gerações por pista, campeão testado por 40 s):

| Treinado em | Oval | Circuito | Serpente |
|---|---|---|---|
| Oval | 4,1 voltas | bate (0,2) | bate (0,2) |
| Circuito | 3,4 | 4,0 | bate (0,2) |
| Serpente | 4,1 | 4,0 | 2,9 |

Quem treinou na pista fácil só sabe virar para um lado e bate na primeira curva diferente. Quem treinou na difícil dirige nas três. Essa tabela vem de um sorteio só: serve de exemplo, não de média.

## Limites
- **A física é simples:** sem derrapagem, sem massa, colisão por um círculo. Serve para mostrar o aprendizado, não para validar um veículo.
- **O carro só conhece os sensores.** Ele não sabe onde está na pista nem para onde ela vai; reage ao que vê a até 30 m.
- **O aprendizado depende do sorteio inicial.** Cada recomeço dá uma história diferente.
- **A população vive na memória da bancada.** Se a bancada reiniciar, o treino recomeça; use "Salvar o campeão" para guardar o melhor.
