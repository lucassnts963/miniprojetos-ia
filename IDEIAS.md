# Miniprojetos de IA: do joguinho para a indústria

Série de posts no LinkedIn e vídeos no YouTube (@elucas.dev) mostrando aplicações reais dos mesmos conceitos do projeto **snake** (rede neural pequena + algoritmo genético / neuroevolução).

- Projeto de origem: `C:\dev\snake`, também em https://github.com/lucassnts963/snake
- Cada miniprojeto ganha sua própria pasta aqui: `C:\dev\miniprojetos-ia\<nn>-<slug>\`

---

## Ideias

### ⭐ Rápidas (1 dia ou menos)

#### 01 · Triagem automática de ordens de manutenção (feito: `01-triagem-manutencao/`)
- **O que faz:** recebe o texto do chamado ("vazamento de óleo na prensa") e devolve a **equipe** (mecânica, elétrica, instrumentação, automação) e a **prioridade** (urgente, alta, média, baixa).
- **Como:**
  - Gerar ~300 frases de exemplo uma única vez (com uma LLM ou à mão).
  - Transformar o texto em números com TF-IDF.
  - Treinar uma rede pequena (scikit-learn `MLPClassifier`, ou NumPy puro como na cobrinha).
- **Visual:** a cena de triagem do vídeo do LinkedIn, agora com o modelo real. Você digita o chamado e ele cai na fila certa. Ver `ferramentas/linkedin/sim_industry.py`.
- **Gancho:** "Paguei a LLM uma vez para gerar exemplos. Agora classifico chamados sem pagar nada por chamado."
- **Por que primeiro:** fecha a história do post da cobrinha, que já citava ordens de manutenção.

#### 02 · Menor rota pelas cidades (feito: `02-rota-entregas/`)
- **O que faz:** recebe de 20 a 30 pontos num mapa e acha a melhor ordem de visita (problema do caixeiro-viajante).
- **Como:** o mesmo GA da cobrinha (seleção, crossover, mutação), mas cada indivíduo é uma rota. Usar crossover do tipo OX ou PMX, porque a rota é uma permutação.
- **Visual:** gif ou vídeo da rota começando embaralhada e ficando limpa geração a geração.
- **Gancho:** "A mesma lógica que ensinou a cobrinha a jogar agora planeja rotas de entrega."

#### 03 · Pessoa em área de risco (visão computacional, sem treinar nada)
Mesmo cenário do 02 (armazém e logística), agora com câmera. Versão simples: um modelo pronto que já sabe achar pessoas + uma regra de geometria.

- **O que faz:** você desenha no chão da imagem a área de risco (o corredor da empilhadeira, a zona de uma máquina). O sistema marca cada pessoa no vídeo e avisa quando alguém entra na área.
  - **Segurança do trabalho (obrigação legal):** separar pedestre de máquina em movimento (NR-11, movimentação de materiais; NR-12, zonas de perigo de máquinas).
  - **Operação (o mesmo código, outra regra):** quantas pessoas há em cada área e por quanto tempo; doca ou corredor ocupado ou livre.
- **Como:**
  - Detector de pessoas já treinado (classe "pessoa" do COCO). Não precisa de dataset nem de treino.
  - Regra: o ponto dos pés da pessoa (meio da base da caixa) está dentro do polígono? É conta de geometria, sem IA.
  - Roda local, quadro a quadro, num vídeo.
- **Material disponível na internet para simular e testar:**
  - **Vídeos:** Pexels e Pixabay têm vídeos de armazém, empilhadeira e doca com licença livre (uso comercial, sem atribuição). Atenção: há pessoas identificáveis; para o vídeo do canal, preferir planos abertos ou borrar rostos.
  - **Modelo:** torchvision (BSD) traz detectores pré-treinados no COCO (`ssdlite320_mobilenet_v3_large`, `fasterrcnn_mobilenet_v3_large_fpn`). Alternativa mais fácil de usar: Ultralytics YOLO, mas a licença é AGPL (ok para demo, exige cuidado em produto).
  - **Para medir acerto:** COCO val2017 tem as caixas de pessoa anotadas (dá para calcular quantas pessoas o modelo acha e quantas inventa).
- **Por que aqui a IA faz sentido (ponte com o 02):** não existe fórmula para "isso é uma pessoa". O padrão está nos pixels. Já "está dentro da área?" é geometria: a parte que tem fórmula continua sem IA.
- **Limitações para dizer com honestidade:** pessoa encoberta ou longe da câmera, falso alarme, câmera baixa (os pés somem atrás de paletes); LGPD (finalidade, aviso, guardar só o evento, não identificar ninguém). Apoia o técnico de segurança, não substitui.
- **Visual:** o vídeo com a área de risco desenhada no chão; caixas verdes fora, vermelhas dentro; contador de eventos e uma linha do tempo dos alertas.
- **Gancho:** "A sua empresa já é obrigada a separar gente de empilhadeira. E se a câmera que já está lá avisasse na hora?"
- **Depois (se quiser ir além):** detecção de EPI (capacete e colete, NR-6). Aí precisa treinar, e há datasets públicos prontos: Hard Hat Workers (Roboflow, 7.035 imagens, domínio público) e Safety Helmet Detection (Kaggle, 5.000 imagens). Também: empilhadeira (não existe no COCO), contagem de paletes.
- **Era:** escala de turnos com algoritmo genético. Saiu porque o 02 já mostrou que otimização desse tipo se resolve melhor sem IA.

#### 04 · Espelho do trocador de calor: contar tubos, achar obstruídos e tamponados (em exploração)
- **O que faz:** a partir de uma foto do espelho de um trocador casco e tubo, conta os tubos e separa aberto, obstruído e tamponado.
- **Estado:** exploração com 2 fotos em `04-espelho-trocador/` (resultado e próximos passos no README de lá). Contar é viável numa foto de frente; tamponado é o padrão mais fácil; obstruído depende de fotos melhores e de exemplos rotulados.
- **Como (proposta):** localizar os tubos (círculos + grade regular), recortar cada um e classificar o recorte com uma rede pequena. Cada foto rende cerca de mil recortes.
- **Gancho:** "Quantas horas alguém passa contando tubo por tubo com uma lanterna na mão?"

#### 05 · Carro autônomo no mundo simulado (feito: `05-carro-autonomo/` + `mundo/`)
- **O que faz:** uma população de redes neurais pequenas aprende a dirigir um carro numa pista, sem ninguém ensinar: os carros que vão mais longe deixam filhos (o mesmo princípio da cobrinha).
- **Mundo simulado:** `mundo/` é um motor 2D simples (paredes, obstáculos, sensores de distância, colisão), feito para ser reaproveitado. Próximos usos possíveis: empilhadeira ou AGV num armazém, robô desviando de pessoas, braço ou esteira.
- **Visual:** a pista vista de cima, a população inteira correndo, os sensores do líder e a rede acendendo.
- **Gancho:** o mesmo raciocínio serve para AGV, empilhadeira autônoma e robô de limpeza: treinar no simulado antes de arriscar o equipamento de verdade.

#### 06 · Máquina de completar texto (código e painel prontos: `06-completar-texto/`)
- **O que faz:** uma LLM em miniatura treinada do zero em artigos em português: aposta no próximo pedaço de texto, continua frases e conversa num minichat. Compara a rede com o método antigo (só contar).
- **Série:** é o episódio 1 de "Como uma LLM funciona" (plano em `posts/plano_semana_2026-10-05.md`). Gera vídeo curto do LinkedIn e vídeo do YouTube.
- **Visual:** as apostas em barras, o texto crescendo pedaço por pedaço, a rede por dentro (atenção e palpite por camada) e o minichat.

### Médias (2 a 3 dias)

#### 07 · Manutenção preditiva simulada
- Simular vibração e temperatura de um motor. Uma rede pequena aprende a avisar **antes** da falha.
- **Visual:** gráfico ao vivo com o alerta acendendo antes da quebra.

#### 08 · Roteador de LLM (modelo pequeno antes da API)
- Um classificador decide se a pergunta é simples (ele mesmo responde) ou complexa (vai para o ChatGPT ou o Claude).
- **Visual:** contador de custo, "tudo na LLM" contra "roteado".
- É o argumento de custo do post da cobrinha, provado na prática.

#### 09 · Previsão de demanda para reposição de estoque
- Uma rede pequena prevê a venda da próxima semana e sugere o ponto de reposição.
- **Visual:** curva prevista contra a real, com a reposição marcada.

#### 10 · Detector de pedido fora do padrão
- Marca pedidos com quantidade, valor ou horário estranhos (fraude ou erro de digitação).
- **Visual:** lista de pedidos passando, com os suspeitos piscando em vermelho.

### Fora da numeração (método de trabalho, sem miniprojeto)

#### Base de conhecimento viva (LLM Wiki): post feito, vídeo do YouTube a produzir
- **Post do LinkedIn:** `posts/linkedin_llm_wiki.md`, com carrossel contínuo e vídeo animado em `posts/carrossel_llm_wiki/`.
- **Vídeo do YouTube (a fazer):** demonstrar o uso e ensinar a configurar e manter uma wiki mantida por IA. Quem assistir deve conseguir montar a sua.
- **Roteiro proposto:**
  1. O problema e a ideia do Karpathy: a IA mantém uma wiki em vez de reler tudo a cada pergunta.
  2. Demonstração de uso: uma pergunta feita no chat, a IA percorrendo as páginas e respondendo com a fonte.
  3. Configurar do zero: as pastas (entrada, fontes originais, wiki), o arquivo de regras para o agente, o índice e o registro cronológico.
  4. O primeiro documento: entra, é aprovado, vira página, e o índice e o registro são atualizados.
  5. Manter: perguntar, arquivar respostas que valem, rodar a auditoria (contradição, página vencida, órfã, lacuna).
  6. As adaptações do Lucas: aprovação humana antes de virar fonte, fidelidade à fonte, estado vivo (foco e pendências), regras duráveis, uma base por projeto subindo para a central.
  7. Limites e cuidados: dado sensível, o que não colocar, quando a wiki não compensa.
- **Material:** gravar numa **base de demonstração com conteúdo fictício** (por exemplo, a manutenção de uma bomba, a mesma história do vídeo do LinkedIn). Não gravar o vault real: tem dados pessoais e de terceiros.
- **Entregável junto do vídeo:** um repositório-modelo com as pastas, o arquivo de regras e dois ou três documentos de exemplo, para quem assiste copiar.
- **Reaproveitar:** a cena animada de `posts/video_llm_wiki.py` (documentos virando páginas, a IA percorrendo a rede) serve de abertura.

**Sequência sugerida da série:** 01 → 02 → 03 → 04 → 05 → 07 → 06 → 08 → 09 (01 e 02 feitos; 05 com código e painel prontos; o 03 fecha o trio do armazém, em versão simples: modelo pronto + regra)

---

## Regras dos posts no LinkedIn (definidas pelo Lucas)

- **Abrir com uma chamada de aplicação/solução** para empresas. O projeto vem depois, como demonstração.
- **Sem detalhes técnicos** nem nomes de tecnologia no post. O foco é **solução e aplicabilidade**.
- **Sem quantidades nem números** (nada de "150 cobras", "435 parâmetros", percentuais). Fale só do **método**.
- **Cuidado com inconsistências** entre texto e vídeo. Exemplo real: o texto falava de 150 cobras, mas o vídeo mostrava 15.
- **Fechamento assinatura:** "As aplicações são inúmeras. E, como gosto de dizer: a sua imaginação é o limite. 🚀" + uma pergunta para puxar comentários.
- Mostrar setores **industrial e comercial**.
- Referência de post aprovado: `C:\dev\snake\demo\post_linkedin.md`

## Vídeos

### LinkedIn (1080x1080) e Stories/Reels/Status (1080x1920, até 60 s)
- Visual: fundo `#12121c`, verde `#50dc78`, texto secundário `#a0a6c8`, fonte Segoe UI (Bold para títulos).
- Estrutura: abertura → **1 · APRENDIZADO** → cartão de transição → **2 · RESULTADO** → **3 · NA INDÚSTRIA** (cena animada de aplicação) → fechamento "A sua imaginação é o limite."
- **Velocidade do aprendizado:** o começo em **tempo real** (sem inteligência ainda), depois acelera, e no final **desacelera** para mostrar o resultado. Pedido explícito do Lucas.
- Legendas curtas, sem números.
- Script de referência: `ferramentas/linkedin/build.py` (ffmpeg + drawtext, com a função `ramp_clip` para velocidade variável) e `ferramentas/linkedin/sim_industry.py` (cena animada em Pygame).

### YouTube (1920x1080), público dev: aqui pode ser técnico
- **Tema elucas.dev:**

  | Token | Cor |
  |---|---|
  | ink (fundo) | `#0C0C0F` |
  | card | `#16161A` |
  | red | `#E5484D` |
  | redSoft | `#F08A8D` |
  | fg | `#ECECEF` |
  | body | `#B4B4BC` |
  | mute | `#87878F` |
  | line | rgba 255,255,255 a 9% |
  | glow | vermelho a 18% |

- Fontes IBM Plex Sans e Mono (em `ferramentas/youtube/fonts/`). Fundo com grade de pontos, "elucas.dev" no topo à esquerda, "@elucas.dev" no rodapé, capítulo atual no canto inferior direito.
- Conteúdo: estrutura do projeto, código com destaque de sintaxe e linhas destacadas **em sincronia com a narração**, diagramas, e a visualização **ao vivo** do modelo decidindo (ativações, decisão e motivo).
- Script de referência: `ferramentas/youtube/render.py` (Pygame → ffmpeg; cenas com `@scene`, cues lidos de `timing.json`).

### Narração (ElevenLabs v3)
1. Escrever o roteiro com audio tags do v3 (`[excited]`, `[curious]`, `[whispers]`, `[pause]`…), reticências para pausas, MAIÚSCULAS para ênfase e números por extenso.
   - Dividir em partes de até ~2.500 caracteres.
   - Stability "Creative" ou "Natural".
   - Referência: `C:\dev\snake\demo\youtube_roteiro.md`
2. O Lucas gera os áudios e coloca na pasta do projeto (`parte01.mp3`, `parte02.mp3`…).
3. Transcrever com timestamps por palavra: `ferramentas/narracao/tx.py`. Usa o faster-whisper `medium` na GPU, com o Python de `C:\dev\venv`, a mesma base de `C:\dev\scripts\transcribe`.
4. `ferramentas/narracao/sync.py`: mapeia frases-âncora para cenas e cues e gera `timing.json`. A duração de cada cena passa a seguir a fala (fala entra 0,55 s depois do início da cena, com 0,9 s de respiro no fim).
5. Renderizar o vídeo lendo o `timing.json`.
6. `ferramentas/narracao/mix.py`: posiciona os trechos, normaliza a narração em −16 LUFS e faz ducking da música.
7. `ferramentas/narracao/verify.py`: re-transcreve o áudio final e confere o desvio de cada âncora.

### Música
- Lo-fi **CC0 (domínio público, sem crédito obrigatório)** do HoliznaCC0, álbum *Public Domain Lofi*, baixada do Free Music Archive: https://freemusicarchive.org/music/holiznacc0/public-domain-lofi
- Já baixadas em `ferramentas/musica/`: `tranquil_mindscape.mp3`, `lucid.mp3`, `tokyo_sunset.mp3`, `when_i_was_human.mp3`.
- Pixabay bloqueia download automatizado (Cloudflare). O FMA funciona com curl: o link do mp3 aparece no HTML da página da faixa.

## Observações técnicas
- ffmpeg 9 em `C:\programs\bin`. GPU MX570 (NVENC disponível; CUDA funciona com o faster-whisper).
- Os scripts em `ferramentas/` foram escritos para o projeto snake e têm caminhos fixos (`C:/dev/snake/...`, pasta temporária da sessão). Ajuste os caminhos antes de reutilizar.
- Os scripts de vídeo usam Pygame (`SDL_VIDEODRIVER=dummy`) e enviam os quadros para o ffmpeg via stdin.
- O Git desta máquina não tem `user.name` nem `user.email` globais. Commits como `Lucas Santos <lucassnts963@gmail.com>`, usando `git -c` só no comando.
