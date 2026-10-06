# IA sem mistério: como funciona a IA que escreve, em quatro partes

Artigo de apoio da série do LinkedIn (partes 1 a 4, de 06 a 09/10/2026). Cada parte abaixo traz a explicação completa, o nome técnico de cada ideia e as fontes. Serve para publicar como artigo e para responder a quem pedir referência nos comentários.

Por Lucas Santos ([@elucas.dev](https://youtube.com/@elucas.dev))

---

Acredito que o caminho para dominar qualquer tecnologia é conhecer a origem dela e como ela funciona. Quem entende o mecanismo sabe o que pedir, como pedir e quando desconfiar.

A IA que escreve textos, a que está por trás das ferramentas de conversa, tem um nome técnico: modelo de linguagem de grande porte, ou LLM (do inglês *large language model*). Ela parece misteriosa, mas se apoia em poucas ideias. Este artigo passa por quatro delas:

1. ela escreve adivinhando a próxima palavra;
2. ela não lê palavras, lê pedaços;
3. ela não tem memória, só relê a conversa;
4. ela decide o que importa distribuindo atenção.

Em cada parte há uma seção "o que muda na prática", porque entender só vale se mudar o jeito de usar.

## Parte 1 · Como a IA escreve um texto

**A ideia.** Você já viu uma versão simples no teclado do celular: digita "Bom" e ele sugere "dia". O teclado não entende a conversa, só sabe o que costuma vir depois. Um modelo de linguagem faz a mesma coisa, levada ao extremo. Dado um texto, ele calcula a chance de cada continuação possível, escolhe uma, acrescenta ao texto e repete. O nome técnico desse jeito de escrever, uma parte de cada vez e sempre com base no que já foi escrito, é geração autorregressiva.

**A origem.** A ideia é antiga. Em 1948, Claude Shannon mostrou que dava para produzir sequências parecidas com inglês apenas contando quais letras e palavras costumam vir depois de quais. Em 1951, ele mediu o quanto a próxima letra de um texto é previsível a partir das anteriores. Os modelos atuais trocaram a tabela de contagens por uma rede neural, mas a tarefa continua a mesma: prever o que vem depois.

**De onde vêm os palpites.** Do treino. O modelo lê uma quantidade enorme de textos e é ajustado, repetidas vezes, para acertar a continuação. De tanto ler, aprende o que costuma vir depois do quê.

**O cuidado.** Ele não consulta um arquivo de respostas. O texto é escrito na hora, uma parte de cada vez. Por isso soa natural, e por isso pode sair errado com a mesma segurança de quando sai certo: nos dois casos, é só a continuação mais plausível.

**O que muda na prática.** Se a IA continua o que você começa, o começo é tudo. Pedido vago recebe a resposta mais comum. Antes de pedir, diga quem ela deve ser, qual é a situação e como você quer a resposta.

**Simplificação assumida.** Na parte 1 eu digo "palavra". A parte 2 corrige: são pedaços menores que palavras.

**Fontes**
- Shannon, C. E. (1948). [A Mathematical Theory of Communication](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf). É o artigo com as aproximações do inglês por contagem.
- Shannon, C. E. (1951). [Prediction and Entropy of Printed English](https://www.princeton.edu/~wbialek/rome/refs/shannon_51.pdf). Mede o quanto a próxima letra é previsível.
- [Language Models](https://cacm.acm.org/research/language-models/), Communications of the ACM. Conta a história dos modelos de linguagem, de Shannon aos atuais.
- [A Law of Next-Token Prediction in Large Language Models](https://arxiv.org/html/2408.13442v2). Descreve a geração como previsão do próximo token, um de cada vez.

## Parte 2 · Por que a IA erra contas

**A ideia.** A IA não lê palavras nem letras. Antes de chegar a ela, todo texto é picado em pedaços, como peças de montar. Cada peça se chama token, e o corte se chama tokenização. Uma palavra comum costuma virar um token só; uma palavra rara é montada com vários. Depois, cada token é trocado por um número, a posição dele numa lista chamada vocabulário. O modelo trabalha só com esses números.

**Por que isso atrapalha as contas.** Um número grande também vira tokens. Diante de uma conta, o modelo não calcula: ele prevê os tokens do resultado, do mesmo jeito que prevê palavras. Contas pequenas aparecem muito nos textos e ele acerta. Uma multiplicação grande, que ele nunca viu igual, é palpite, e os estudos mostram a precisão caindo conforme os números ganham dígitos. Contar as letras de uma palavra esbarra no mesmo problema: ele vê tokens, não letras.

**Como resolveram.** Escrever é o ponto forte do modelo, então as ferramentas passaram a usar isso. Em vez de adivinhar o resultado, a IA escreve a conta como um pequeno programa, um computador executa esse programa num ambiente isolado e devolve o número. O nome do recurso é execução de código. Os três grandes fabricantes descrevem o mesmo mecanismo. É por isso que a mesma IA que erra uma multiplicação "de cabeça" analisa uma planilha inteira sem tropeçar: nessa hora, quem calcula não é ela.

**O que muda na prática.** A ferramenta existe, mas nem sempre é acionada. Quando o número importa, veja se a IA fez a conta de verdade, peça "calcule usando código" ou "monte a planilha" e confira o que for crítico.

**Sobre os exemplos do carrossel.** Os cortes das palavras são reais, feitos pelo cortador de texto do meu projeto 06 (uma LLM em miniatura treinada em artigos em português). Cada IA tem o seu próprio corte; numa IA comercial, os tokens e os números são outros.

**Fontes**
- [What are tokens and how to count them?](https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them), ajuda da OpenAI. Explica que tokens podem ser de um caractere a uma palavra inteira.
- [Why can't powerful LLMs learn multiplication?](https://cs.uchicago.edu/news/why-cant-powerful-llms-learn-multiplication/), Universidade de Chicago.
- [Language Models are Symbolic Learners in Arithmetic](https://arxiv.org/pdf/2410.15580). Mostra a precisão caindo em multiplicações com mais dígitos.
- [Data analysis with ChatGPT](https://help.openai.com/en/articles/8437071-data-analysis-with-chatgpt), ajuda da OpenAI: o ChatGPT escreve e roda código Python para cálculos e análises.
- [Code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool), documentação do Claude, e o anúncio da [ferramenta de análise](https://claude.com/blog/analysis-tool).
- [Code execution](https://ai.google.dev/gemini-api/docs/code-execution), documentação do Gemini.

## Parte 3 · Por que a IA esquece o que você disse

**A ideia.** O modelo não tem memória. Entre uma resposta e outra, nada fica guardado nele. A cada mensagem, o programa em volta envia a conversa inteira de novo, e o modelo relê tudo.

**A mesa de trabalho.** Essa leitura tem um tamanho máximo. Pense numa mesa: cabe muito papel, mas não cabe tudo, e a IA só enxerga o que está em cima dela. O nome técnico da mesa é janela de contexto. A documentação do Claude a descreve como a "memória de trabalho" do modelo.

**Por que o combinado some.** Quando a conversa passa do limite, as partes mais antigas são resumidas ou descartadas, dependendo do produto. A regra combinada no começo pode sair da mesa. E uma conversa nova começa com a mesa vazia: o que foi explicado em outra conversa não está lá.

**Como resolveram.** As ferramentas ganharam um caderno de anotações, o recurso de memória. Elas guardam anotações sobre o usuário e colocam essas anotações na janela de contexto quando a conversa começa. Não é lembrança: é texto, relido como todo o resto. Em geral o usuário pode ver, editar e apagar o que está anotado.

**O que muda na prática.** Cuide do que está na mesa. Assunto novo, conversa nova. Em conversa longa, peça um resumo e recomece com ele. E entregue o documento junto com a pergunta, em vez de esperar que a IA "saiba" do seu equipamento, do seu contrato ou do seu cliente. É por isso que uma base de conhecimento organizada faz diferença: ela é o que coloca o papel certo na mesa.

**Fontes**
- [Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows), documentação do Claude. Define a janela de contexto como "working memory".
- [How do usage and length limits work?](https://support.claude.com/en/articles/11647753-how-do-usage-and-length-limits-work), ajuda do Claude. Explica o resumo das mensagens antigas quando a conversa se aproxima do limite.
- [Memory in ChatGPT](https://help.openai.com/en/articles/8590148-memory-faq), ajuda da OpenAI. Descreve as memórias salvas e o uso do histórico de conversas.

## Parte 4 · Como a IA decide o que importa

**A ideia.** Antes de escrever cada token, o modelo olha tudo o que veio antes e decide quanto cada trecho pesa, como um holofote que ilumina mais umas palavras que outras. O nome técnico é atenção. É o mecanismo central da arquitetura usada pelas LLMs, o Transformer, apresentada em 2017 no artigo "Attention Is All You Need".

**Para que serve.** É a atenção que faz o modelo ligar os pontos. Em "o técnico trocou o selo da bomba porque ele estava gasto", é ela que liga "ele" ao selo, e não ao técnico.

**O limite.** O peso é repartido entre tudo o que está na janela de contexto. Num texto curto, a instrução pesa muito. Num texto enorme, ela disputa espaço com todo o resto. Um estudo de Stanford, "Lost in the Middle", mediu o efeito: o desempenho é maior quando a informação relevante está no começo ou no fim do texto e cai quando ela está no meio. Os modelos mais novos melhoraram, mas o padrão ainda é citado.

**A dica de quem fabrica.** A documentação da Anthropic recomenda, para textos longos, colocar o material primeiro e o pedido (o prompt) por último, e relata melhora na qualidade das respostas com essa ordem.

**O que muda na prática.** Organização não é capricho, é o que faz a instrução pesar. Um pedido de cada vez. Destaque o que não pode faltar, com títulos, listas e a regra principal repetida no fim. E mostre um exemplo do resultado que você quer.

**Sobre os desenhos do carrossel.** As barras de peso nas frases são ilustração do mecanismo, não a medida de um modelo. No meu projeto 06 dá para ver a atenção de verdade, camada por camada, numa rede pequena.

**Fontes**
- Vaswani e colegas (2017). [Attention Is All You Need](https://arxiv.org/abs/1706.03762). O artigo que apresentou o Transformer.
- Liu e colegas (2024). [Lost in the Middle: How Language Models Use Long Contexts](https://aclanthology.org/2024.tacl-1.9/).
- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices), documentação do Claude. Traz a recomendação de documentos longos no topo e a pergunta no fim.

## Para fechar

As quatro ideias se encaixam. A IA escreve prevendo o próximo token (parte 1). Ela enxerga o texto como tokens e números (parte 2). Só existe para ela o que está na janela de contexto (parte 3). E, dentro dessa janela, a atenção decide o que pesa (parte 4).

Daí saem as quatro regras práticas da série:
- comece bem o pedido: quem ela deve ser, a situação e o formato da resposta;
- número exato se pede com conta feita por código, e se confere;
- o que ela precisa saber tem de estar na conversa;
- texto organizado, com o pedido no fim, pesa mais.

As aplicações são inúmeras. E, como gosto de dizer: a sua imaginação é o limite.

---

## Notas sobre este artigo
- **Consulta das fontes:** 02/10/2026. Páginas de ajuda e documentação mudam; vale reconferir os links antes de publicar.
- **O que li de cada fonte:** os resultados de busca e os resumos das páginas, não o texto integral de cada artigo científico. As afirmações usadas são as que aparecem nos resumos: Shannon e as contagens, a previsão do próximo token, a queda de precisão em multiplicações longas, o efeito do meio do texto e as descrições oficiais das ferramentas.
- **O que é opinião ou prática minha, sem fonte:** "o começo é tudo", "um pedido de cada vez", "destaque o que não pode faltar" e "mostre um exemplo". São orientações coerentes com o mecanismo, não resultados de medição.
- **Marcas:** os posts do LinkedIn não citam fabricantes. Aqui elas aparecem só nas fontes.
- **Carrosséis e posts de cada parte:** as pastas `parte1/` a `parte4/` (em cada uma, `post.md` e as imagens).
