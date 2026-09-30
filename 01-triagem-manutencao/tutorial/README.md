# Rede neural do zero: triagem de chamados de manutenção

Código do vídeo do [@elucas.dev](https://youtube.com/@elucas.dev). Um arquivo, só NumPy: lê o texto de uma ordem de manutenção e decide a **equipe** (mecânica, elétrica, instrumentação, automação) e a **prioridade** (urgente, alta, média, baixa).

```bash
pip install numpy
python triagem_do_zero.py
```

Saída esperada:
```
época  10  perda 1.023
...
época 100  perda 0.253
teste  equipe 98%  prioridade 59%
('ELÉTRICA', 'ALTA')
```

## Arquivos
- `triagem_do_zero.py`: o código do vídeo, dividido em 10 passos.
- `chamados.csv`: 561 chamados de exemplo (`texto;equipe;prioridade`), gerados uma única vez com uma LLM.

## Os 10 passos
| Passo | O que faz |
|---|---|
| 1 | lê o CSV e transforma as classes em números |
| 2 | limpa o texto: minúsculas, sem acento, só letras e números |
| 3 | gera os termos: palavras, pares de palavras e pedaços de 3 a 5 letras |
| 4 | TF-IDF: cada chamado vira um vetor com o peso de cada termo |
| 5 | cria os pesos da rede (inicialização de He) |
| 6 | forward: camada oculta com ReLU e duas saídas com softmax |
| 7 | perda: entropia cruzada das duas saídas |
| 8 | backprop: gradientes de trás para frente, com dropout |
| 9 | treino com Adam e L2 |
| 10 | teste com dados separados e uso num chamado novo |

## Sobre o resultado
O 98% da equipe é desse corte de teste, que teve sorte. Com validação cruzada, a equipe fica perto de 92% e a prioridade perto de 68%. A prioridade é o ponto fraco, porque a fronteira entre alta e média é subjetiva. Para melhorar, o que mais ajuda é ter mais exemplos.
