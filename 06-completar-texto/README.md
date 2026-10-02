# 06 · Máquina de completar texto: uma LLM em miniatura, treinada do zero

Uma LLM faz uma coisa só: aposta em qual pedaço de texto vem depois. Este projeto constrói essa máquina em tamanho pequeno, para ver por dentro: os pedaços de texto, as apostas, a atenção, e um minichat que é a mesma máquina completando uma conversa.

**Estado:** código, treino e painel da bancada prontos. Post e vídeo do LinkedIn prontos (`post_linkedin.md`, `video/linkedin_completar.mp4`). Falta o vídeo do YouTube.

## Testar ao vivo
```bash
python ../bancada/servidor.py   # http://127.0.0.1:8765, projeto 06
```
- **Completar:** escreva um começo e veja as apostas para o próximo pedaço. "Completar" continua o texto; clicar numa aposta escolhe o pedaço você mesmo.
- **Rede neural x só contagem:** a contagem olha os últimos 1 a 3 pedaços numa tabela; a rede olha o texto inteiro.
- **A rede por dentro:** os últimos pedaços entram embaixo e sobem pelas camadas. As linhas verdes são a atenção do último pedaço em cada camada; à direita, o palpite que a rede daria se parasse naquela camada.
- **Minichat:** pergunta e resposta em laço. A conversa vira um texto só ("Pergunta: … Resposta:") e a rede completa a resposta; o painel mostra esse texto, pedaço por pedaço.

## Como rodar do zero
```bash
python baixar_textos.py   # artigos da Wikipédia em português -> dados/corpus.txt (fora do git)
python treinar.py         # pedaços -> contagem -> rede; salva em modelo/ (fora do git)
python teste.py           # testes das três peças
```
O treino levou cerca de 28 minutos numa placa de vídeo de notebook (MX570, 2 GB).

| Arquivo | O que faz |
|---|---|
| `pedacos.py` | quebra o texto em pedaços (BPE): letras que aparecem juntas viram um pedaço só; vocabulário de 3.000 |
| `contagem.py` | completar só contando o que vem depois dos últimos pedaços (a origem da ideia) |
| `rede.py` | transformer pequeno: 6 camadas, 4 cabeças de atenção, janela de 96 pedaços, 5,5 milhões de números |
| `conversas.py` | monta perguntas e respostas a partir dos próprios artigos, para a rede aprender o formato de chat |
| `treinar.py` | treina e mede tudo no trecho de texto guardado para teste |
| `demo.py` + `painel/` | painel da bancada |

## Resultado
Texto de treino: 9,4 MB (568 artigos, 2,7 milhões de pedaços) e 2.843 conversas montadas a partir deles. Medido nos 5% finais do texto, que ninguém viu no treino:

| Quem completa | Acerta o próximo pedaço de primeira | Certo entre as cinco primeiras apostas |
|---|---|---|
| Contagem, último pedaço | 15% | 36% |
| Contagem, últimos 2 | 27% | 48% |
| Contagem, últimos 3 | 29% | 44% |
| Rede neural | **34%** | **55%** |

- **A rede ganha da contagem, mas por pouco** neste tamanho de texto e de rede. A diferença que se vê a olho é outra: a contagem perde o assunto em poucas palavras; a rede mantém o assunto por frases.
- **O minichat acerta a forma antes do conteúdo.** Em sete perguntas de teste, todas as respostas vieram no formato de definição. Duas ficaram no assunto certo e começaram corretas (bomba hidráulica, trocador de calor) antes de desandar; as outras responderam sobre outro assunto, com a mesma segurança. Uma pergunta fora da base ("quem ganhou a copa de 2002?") recebeu a definição de uma escola. É o comportamento de "inventar" das LLMs, em versão ampliada.
- Não há medida de acerto do minichat em número: a conferência foi por leitura.

## Limites
- **É uma miniatura.** Serve para entender o mecanismo, não para usar como assistente.
- **Sabe só o que leu:** 568 artigos. A busca foi por assunto (indústria, logística, saúde, tecnologia…), então a cobertura é irregular.
- **As conversas de treino são mecânicas:** três jeitos de perguntar ("O que é…?", "Fale sobre…", "Explique…") e a resposta é o começo do artigo. Pergunta em outro formato sai do que ela conhece.
- **O "palpite por camada"** aplica a saída final ao estado de cada camada. É uma leitura aproximada: as camadas do meio não foram treinadas para serem lidas assim.
- **Texto da Wikipédia (CC BY-SA):** o corpus e o modelo ficam fora do repositório; `baixar_textos.py` refaz.
