# Plano de produção: semana de 05 a 09/10/2026 e a série "Como uma LLM funciona"

## Onde estamos
| Data | Post | Situação |
|---|---|---|
| já postado | 01 · Triagem de manutenção | no ar |
| já postado | 02 · Menor rota ("nem tudo precisa de IA") | no ar |
| seg 05/10 | Base de conhecimento viva: **carrossel** | agendado |
| seg 12/10 | Base de conhecimento viva: **vídeo** | agendado |

Na fila, sem data: 03 (área de risco), 04 (espelho do trocador), 05 (carro autônomo). Os três ainda dependem de vídeo.

## A série nova: "Como uma LLM funciona"
**Tese (do Lucas):** o caminho para dominar qualquer tecnologia é saber de onde ela veio e como funciona. Quem entende o mecanismo sabe o que pedir, como pedir e quando desconfiar.

**Fórmula de cada post**, para a série não virar aula solta:
1. **Abertura:** uma situação que o leitor já viveu usando IA no trabalho.
2. **O mecanismo:** uma ideia só, em linguagem comum, com uma analogia.
3. **O que muda na prática:** o que fazer diferente a partir de hoje.
4. **Fechamento assinatura** + pergunta.

**Ajuste nas regras dos posts:** a regra "sem detalhes técnicos" foi escrita para os posts de aplicação. Nesta série o assunto é o funcionamento, então o conceito entra, mas sem jargão solto: cada termo novo vem explicado na mesma frase, e continua valendo "sem números" e "sem nome de ferramenta". Confirmar com o Lucas.

## Semana de 05 a 09/10
A segunda já tem o carrossel agendado, então a série começa na terça. Se a ideia era segunda a sexta só com a série, ela desloca uma semana (12 a 16/10) e o episódio 5 entra na sexta.

| Dia | Post | Ideia central | O que muda na prática | Formato |
|---|---|---|---|---|
| seg 05/10 | Base de conhecimento viva | (agendado) | | carrossel contínuo |
| ter 06/10 | **Ep. 1 · De onde veio: uma máquina de completar texto** | A LLM foi treinada para uma tarefa só: prever o próximo pedaço de texto. Tudo o que ela faz (resumir, traduzir, responder) sai disso. | Ela continua o texto que você começa. Pedido vago, continuação vaga. Dê o papel, o contexto e o formato da resposta. | carrossel contínuo |
| qua 07/10 | **Ep. 2 · Ela não lê palavras: lê pedaços** | O texto é quebrado em pedaços menores que palavras, e cada pedaço vira números. Ela não enxerga letras nem faz conta como calculadora. | Por isso erra soma grande e contagem de letras. Para cálculo e dado exato, peça para usar uma ferramenta ou confira você. | vídeo curto animado |
| qui 08/10 | **Ep. 3 · Ela não tem memória: só vê o que está na conversa** | A cada resposta, ela relê a conversa inteira e nada mais. O que não está ali não existe para ela, e o espaço é limitado. | Dê o documento junto com a pergunta. É a ponte com o post de segunda: a base de conhecimento existe para colocar o contexto certo na frente dela. | carrossel contínuo |
| sex 09/10 | **Ep. 4 · Como ela decide o que importa: atenção** | Para escrever cada pedaço, ela pesa todos os anteriores e dá mais peso ao que parece relevante. | Organização ajuda: instrução clara, o mais importante em destaque, um exemplo do resultado esperado. Texto bagunçado dilui o que importa. | vídeo curto animado |

## Semana seguinte (12 a 16/10), rascunho
| Dia | Post | Ideia central | O que muda na prática |
|---|---|---|---|
| seg 12/10 | Base de conhecimento viva: vídeo | (agendado) | |
| ter 13/10 | **Ep. 5 · Por que ela inventa** | Ela sempre produz a continuação mais plausível, mesmo sem ter a informação. Plausível não é verdadeiro. | Peça a fonte, dê permissão para dizer "não sei", confira o que é crítico. |
| qua 14/10 | **Ep. 6 · Por que a mesma pergunta dá respostas diferentes** | A resposta é sorteada entre as continuações prováveis. | Para tarefa repetitiva, fixe o formato e dê exemplos; para ideias, aproveite a variação. |
| qui 15/10 | **Ep. 7 · O que ela aprendeu e até quando** | O conhecimento vem do treino e para numa data. | Assunto recente ou interno da empresa precisa vir no contexto. |
| sex 16/10 | **Ep. 8 · Nem tudo precisa da maior** | Modelo grande, modelo pequeno, modelo próprio: custo e velocidade. | Fecha a série e volta ao argumento do post da cobrinha. |

Depois: ferramentas e agentes (a LLM que age), busca por significado, e um resumo "o que saber antes de colocar IA num processo".

## Produção
Reaproveitar o que já existe: o gerador de carrossel contínuo (`posts/carrossel_llm_wiki.py`) e a cena animada em Pygame (`posts/video_llm_wiki.py`), com o tema elucas.dev.

| Quando | O que fazer |
|---|---|
| sex 02/10 a dom 04/10 | Lucas aprova a lista de episódios e a fórmula. Texto dos quatro posts da semana. |
| seg 05/10 | Carrossel do ep. 1 e vídeo do ep. 2. Agendar ep. 1. |
| ter 06/10 | Carrossel do ep. 3. Agendar ep. 2. |
| qua 07/10 | Vídeo do ep. 4. Agendar ep. 3 e ep. 4. |
| qui 08/10 e sex 09/10 | Textos da semana seguinte; responder comentários. |

Cada post entrega: texto (`posts/serie_llm/epNN.md`), a peça visual, a legenda curta para Stories e a lista "o que sustenta cada frase".

## Cuidados
- **Cada afirmação técnica precisa estar certa.** A série é sobre entender o mecanismo; um erro aqui custa a credibilidade. Cada episódio leva a seção "o que sustenta cada frase", como os outros posts.
- **Analogia tem limite.** "Completar texto" explica muito, mas não tudo; onde a analogia falha, dizer que é simplificação.
- **Cinco posts por semana é um ritmo alto.** Se apertar, o formato mais barato é o carrossel; o vídeo fica para os episódios que pedem movimento (pedaços de texto, atenção).
- **Vídeo do YouTube:** a série pode virar um vídeo longo depois, juntando os episódios. Fica anotado, sem data.

---

## Atualização em 02/10: o que mudou no plano
- **Nome da série:** "IA sem mistério" (sem sigla), para quem nunca viu o assunto.
- **Formato:** só carrossel no LinkedIn (painel contínuo, com uma frase única no rodapé). O vídeo curto foi descartado; o tema fica para um vídeo longo no YouTube.
- **Termos técnicos valem nesta série, sempre com uma metáfora lúdica** (decisão do Lucas em 02/10): token = peça de montar, janela de contexto = mesa de trabalho, memória = caderno de anotações, atenção = holofote, execução de código = calculadora de bolso, prompt = o seu pedido. A parte 1 já estava agendada e ficou sem termos.
- **Palavra primeiro, pedaço depois:** a parte 1 fala em "próxima palavra"; a parte 2 corrige para "pedaços".

| Dia | Parte | Situação | Onde está |
|---|---|---|---|
| seg 05/10 | Base de conhecimento viva (carrossel) | agendado | `posts/carrossel_llm_wiki/` |
| ter 06/10 | 1 · Como a IA escreve um texto | **agendado** | `posts/serie_ia/parte1.md` + `parte1/` |
| qua 07/10 | 2 · Por que a IA erra contas (ela lê pedaços) | pronto para agendar | `posts/serie_ia/parte2.md` + `parte2/` |
| qui 08/10 | 3 · Por que ela esquece o que você disse (só vê a conversa) | pronto, aguardando aprovação | `posts/serie_ia/parte3.md` + `parte3/` |
| sex 09/10 | 4 · Como ela decide o que importa (atenção) | pronto, aguardando aprovação | `posts/serie_ia/parte4.md` + `parte4/` |

Cada parte termina anunciando a seguinte, então a ordem não pode mudar sem refazer o último quadro.
Os carrosséis novos usam `posts/serie_ia/base.py`.

## Shorts (Reels e YouTube Shorts)
Um short vertical por parte (1080x1920, de 41 a 46 s, animado, com narração e trilha lo-fi por trás), em `posts/serie_ia/shorts/parte1.mp4` a `parte4.mp4`. Gerador: `posts/serie_ia/shorts.py`. Mesmo roteiro e mesmos termos dos carrosséis; a legenda curta de cada `parteN.md` serve de descrição. Trilhas: "Tranquil Mindscape" nas partes 1 e 3, "Lucid" nas partes 2 e 4 (HoliznaCC0, CC0).
