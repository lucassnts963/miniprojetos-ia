# Miniprojetos de IA: do joguinho para a indústria

Série de posts no LinkedIn e vídeos no YouTube (@elucas.dev) mostrando aplicações reais dos mesmos conceitos do projeto **snake** (rede neural pequena + algoritmo genético / neuroevolução).

- Projeto de origem: `C:\dev\snake`, também em https://github.com/lucassnts963/snake
- Cada miniprojeto ganha sua própria pasta aqui: `C:\dev\miniprojetos-ia\<nn>-<slug>\`

---

## Ideias

### ⭐ Rápidas (1 dia ou menos)

#### 01 · Triagem automática de ordens de manutenção ← começar por aqui
- **O que faz:** recebe o texto do chamado ("vazamento de óleo na prensa") e devolve a **equipe** (mecânica, elétrica, instrumentação, automação) e a **prioridade** (urgente, alta, média, baixa).
- **Como:**
  - Gerar ~300 frases de exemplo uma única vez (com uma LLM ou à mão).
  - Transformar o texto em números com TF-IDF.
  - Treinar uma rede pequena (scikit-learn `MLPClassifier`, ou NumPy puro como na cobrinha).
- **Visual:** a cena de triagem do vídeo do LinkedIn, agora com o modelo real. Você digita o chamado e ele cai na fila certa. Ver `ferramentas/linkedin/sim_industry.py`.
- **Gancho:** "Paguei a LLM uma vez para gerar exemplos. Agora classifico chamados sem pagar nada por chamado."
- **Por que primeiro:** fecha a história do post da cobrinha, que já citava ordens de manutenção.

#### 02 · Otimizador de rota de entregas (algoritmo genético)
- **O que faz:** recebe de 20 a 30 pontos num mapa e acha a melhor ordem de visita (problema do caixeiro-viajante).
- **Como:** o mesmo GA da cobrinha (seleção, crossover, mutação), mas cada indivíduo é uma rota. Usar crossover do tipo OX ou PMX, porque a rota é uma permutação.
- **Visual:** gif ou vídeo da rota começando embaralhada e ficando limpa geração a geração.
- **Gancho:** "A mesma lógica que ensinou a cobrinha a jogar agora planeja rotas de entrega."

#### 03 · Escala de turnos (algoritmo genético)
- **O que faz:** monta a escala semanal de uma equipe respeitando folgas, turnos e ao menos um eletricista por turno.
- **Visual:** grade da escala com conflitos em vermelho, ficando verde a cada geração.
- **Gancho:** "Quanto tempo a sua liderança gasta montando escala todo mês?"

### Médias (2 a 3 dias)

#### 04 · Manutenção preditiva simulada
- Simular vibração e temperatura de um motor. Uma rede pequena aprende a avisar **antes** da falha.
- **Visual:** gráfico ao vivo com o alerta acendendo antes da quebra.

#### 05 · Roteador de LLM (modelo pequeno antes da API)
- Um classificador decide se a pergunta é simples (ele mesmo responde) ou complexa (vai para o ChatGPT ou o Claude).
- **Visual:** contador de custo, "tudo na LLM" contra "roteado".
- É o argumento de custo do post da cobrinha, provado na prática.

#### 06 · Previsão de demanda para reposição de estoque
- Uma rede pequena prevê a venda da próxima semana e sugere o ponto de reposição.
- **Visual:** curva prevista contra a real, com a reposição marcada.

#### 07 · Detector de pedido fora do padrão
- Marca pedidos com quantidade, valor ou horário estranhos (fraude ou erro de digitação).
- **Visual:** lista de pedidos passando, com os suspeitos piscando em vermelho.

**Sequência sugerida da série:** 01 → 02 → 05 → 04 → 03 → 06 → 07

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
