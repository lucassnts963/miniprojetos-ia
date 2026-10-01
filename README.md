# Miniprojetos de IA: do joguinho para a indústria

Série do [@elucas.dev](https://youtube.com/@elucas.dev) mostrando aplicações reais dos mesmos conceitos do projeto [snake](https://github.com/lucassnts963/snake) (rede neural pequena + algoritmo genético), sem API de LLM por decisão.

| # | Projeto | O que faz |
|---|---|---|
| 01 | [Triagem de ordens de manutenção](01-triagem-manutencao/) | lê o texto do chamado e decide a equipe e a prioridade, explicando o porquê. Rede neural em NumPy puro. Inclui o [tutorial do zero](01-triagem-manutencao/tutorial/) do vídeo. |
| 02 | [Menor rota pelas cidades](02-rota-entregas/) | ordem de visita de todos os municípios (ou de alguns estados) pela menor distância: heurística para milhares de cidades, ótimo comprovado para centenas, distância pelas rodovias e o algoritmo genético da cobrinha. Inclui o [tutorial "nem tudo precisa de IA"](02-rota-entregas/tutorial/). |
| 03 | [Pessoa em área de risco](03-area-de-risco/) | visão computacional com um detector pronto: avisa quando alguém entra numa área desenhada na imagem (em andamento). |
| 04 | [Espelho do trocador](04-espelho-trocador/) | conta os tubos numa foto do espelho e separa aberto, obstruído e tamponado; com painel para corrigir e rotular (em exploração). |
| 05 | [Carro autônomo](05-carro-autonomo/) | uma rede neural pequena aprende a dirigir sozinha numa pista, por neuroevolução. Roda no [mundo simulado](mundo/), um motor 2D reaproveitável (paredes, obstáculos, sensores e colisão). |

Ideias e regras da série: [IDEIAS.md](IDEIAS.md).

## Ferramentas
| Pasta | Para quê |
|---|---|
| [bancada/](bancada/) | interface no navegador para testar os modelos ao vivo (`python bancada/servidor.py`); cada projeto com `demo.py` aparece sozinho. **Todo projeto tem painel.** |
| `ferramentas/youtube/` | tema elucas.dev (`tema.py`) e motor de cenas (`video.py`) dos vídeos do YouTube |
| `ferramentas/narracao/` | transcrição, sincronia com as cenas e mixagem da narração (`pipeline.py`) |
| `ferramentas/gravacao/` | grava a bancada em vídeo (Playwright) |
| `ferramentas/musica/` | lo-fi CC0 de HoliznaCC0 (*Public Domain Lofi*, domínio público) e `trilha.py`, que coloca a música num vídeo |

Cada projeto tem o próprio README e `requirements.txt`.
