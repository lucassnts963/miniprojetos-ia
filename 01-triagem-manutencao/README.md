# 01 · Triagem automática de ordens de manutenção

Recebe o texto do chamado ("vazamento de óleo na prensa") e devolve a **equipe** (mecânica, elétrica, instrumentação, automação), a **prioridade** (urgente, alta, média, baixa) e **as palavras que pesaram** na decisão.

> Paguei a LLM uma vez para gerar exemplos. Agora classifico chamados sem pagar nada por chamado.

## Como funciona
- **Dados (`dados/`):** 561 chamados de exemplo gerados uma única vez por uma LLM, em dois lotes. O lote 1 é mais formal; o lote 2 imita o jeito do operador escrever ("tá vazando", "parou tudo"). Para gerar mais, basta criar `dados/chamados_lote3.csv` no mesmo formato (`texto;equipe;prioridade`).
- **Texto → números (`vetorizador.py`):** TF-IDF em NumPy com palavras, pares de palavras e pedaços de 3 a 5 letras. Os pedaços fazem "vazando" e "vazamento" parecerem a mesma coisa, sem acento nem maiúscula atrapalhando.
- **Rede (`rede.py`):** NumPy puro, como na cobrinha. Tem uma camada oculta de 32 neurônios (ReLU) e **duas saídas** que compartilham essa camada: equipe e prioridade (softmax). O treino é por backprop + Adam, com dropout e L2. Diferente da cobrinha, aqui existe gabarito, então gradiente funciona melhor que evolução.
- **Explicação (`modelo.py`):** tira uma palavra por vez e mede quanto a confiança cai. As que mais derrubam são o "motivo".

## Resultado (validação cruzada, 5 partes)
Cada chamado é avaliado por um modelo que nunca o viu no treino.

| | acerto |
|---|---|
| Equipe | ~93% |
| Prioridade (exata) | ~67% |
| Prioridade (no máximo um nível de diferença) | ~93% |

- Com só o lote 1 (316 chamados), o acerto de equipe era de ~84%. **Mais exemplos foi o que mais melhorou**; mexer na rede quase não mudou nada.
- Prioridade é mais subjetiva: a fronteira entre "alta" e "média" varia até entre pessoas. O erro grave (urgente virando baixa, ou o contrário) é raro. A matriz de confusão aparece na saída do `treinar.py`.

## Como rodar
```bash
pip install -r requirements.txt
python treinar.py            # validação cruzada + treino final -> modelo.npz, historico.json
python treinar.py --rapido   # só o treino final
python triar.py "motor da bomba cheirando queimado"
python triar.py              # modo interativo
```

```
  o motor da bomba 2 tá cheirando queimado
  -> ELÉTRICA        89%   por causa de: motor, queimado
  -> ALTA            49%   por causa de: motor, cheirando
```

## Testar ao vivo
```bash
python ../bancada/servidor.py   # http://127.0.0.1:8765
```
Classifica enquanto você digita e mostra a equipe, a prioridade, as palavras que pesaram, o que a rede reconheceu e o caminho dentro da rede. Em **Ensinar a rede** você corrige um erro: o exemplo vai para `dados/chamados_correcoes.csv` e entra no próximo treino (**Retreinar e medir**, que leva uns dois minutos).

## Arquivos
| Arquivo | O que faz |
|---|---|
| `dados/chamados*.csv` | exemplos rotulados (todos os lotes são lidos) |
| `vetorizador.py` | TF-IDF em NumPy |
| `rede.py` | rede com duas saídas + treino (backprop, Adam) |
| `modelo.py` | junta os dois, salva/carrega, explica a decisão |
| `treinar.py` | validação cruzada, treino final, histórico por época (para a animação do vídeo) |
| `triar.py` | classifica chamados pela linha de comando |
| `video/cena_triagem.py` | cena 1080x1080 do LinkedIn com o modelo real decidindo (precisa de `pygame`) |

## Visual (vídeos do LinkedIn, 1080x1080, tema elucas.dev)
Duas versões, ambas com o modelo real decidindo e sem números na tela:

| Vídeo | Como gerar |
|---|---|
| `video/cena_triagem.mp4` (24 s): cena animada, chamados indo para as filas | `python video/cena_triagem.py` (precisa de `pygame`; `--still 6.5` salva um quadro) |
| `video/painel_triagem.mp4` (~34 s): o painel da bancada em uso, digitando chamados | com a bancada rodando: `../ferramentas/gravacao/venv/Scripts/python.exe video/gravar_painel.py` |

Os chamados ficam nas listas no topo de cada script. O `cena_triagem.py` imprime o que o modelo decidiu para cada um, para conferir antes de publicar.

