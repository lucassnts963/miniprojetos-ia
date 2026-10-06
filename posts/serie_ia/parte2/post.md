# Post LinkedIn: "IA sem mistério", parte 2 (quarta 07/10, vai com o carrossel)

**Carrossel:** `01.png` a `08.png` (nesta pasta) (1080x1350), `carrossel.pdf` e `panorama.png`. Para refazer: `python posts/serie_ia/parte2/carrossel.py`.
- Quadros: capa → ela lê pedaços → a regra do corte → cada pedaço vira um número → por isso ela tropeça → como resolveram (ela escreve a conta, um computador calcula) → na prática → fechamento.
- No rodapé, a frase atravessa os 8 quadros já cortada em pedaços: "A IA não lê palavras: ela corta o texto em pedaços, troca cada pedaço por um número e adivinha o próximo."
- Poste as 8 imagens na ordem.

Você já viu uma IA escrever um relatório inteiro em segundos e, logo depois, errar uma conta?

Parece contraditório. Não é. O motivo está no jeito como ela lê.

Esta é a parte 2 da série IA sem mistério. 🧠 Na parte 1, vimos que a IA escreve adivinhando a próxima palavra. Hoje, um ajuste nessa história: não é bem palavra.

Ela não lê palavras. Lê pedaços.

Antes de chegar à IA, todo texto é picado em pedaços, como peças de montar. Cada peça tem nome: token. E o corte também: tokenização.
✅ palavra comum vira um token só;
✅ palavra rara é montada com vários tokens;
✅ cada token é trocado por um número, e é só isso que ela enxerga.

Ela nunca vê letras. E um número grande também vira tokens.

Por isso, diante de uma conta, a IA não calcula: ela adivinha os tokens do resultado, do mesmo jeito que adivinha palavras. Conta pequena ela já viu muitas vezes e acerta. Conta grande, que ela nunca viu igual, é palpite. Contar as letras de uma palavra dá o mesmo problema.

🔧 Como resolveram
Escrever é com ela. Então as IAs de hoje ganharam uma calculadora de bolso, chamada execução de código: em vez de adivinhar o resultado, ela escreve a conta como um pequeno programa, um computador executa e devolve o número certo. Ela só redige a resposta.

É por isso que a mesma IA que erra uma multiplicação "de cabeça" analisa uma planilha inteira sem tropeçar: nessa hora, quem calcula não é ela.

💡 O que muda na prática
A ferramenta existe, mas nem sempre é usada. Quando o número importa:
• veja se ela fez a conta de verdade: em geral dá para abrir e ver o programa que rodou;
• se não fez, peça: "calcule usando código" ou "monte a planilha";
• confira o que for crítico.

🏭 Na indústria: horas de parada, custos de manutenção e saldos de estoque somados "de cabeça" pela IA merecem conferência. Melhor pedir a planilha pronta.
🛒 No comércio: totais de pedido, descontos e comissões seguem a mesma regra.

As aplicações são inúmeras. E, como gosto de dizer: a sua imaginação é o limite. 🚀

Já pegou uma IA errando uma conta ou um total? Me conta nos comentários 👇

#InteligenciaArtificial #IA #Produtividade #Industria40 #Inovacao #TransformacaoDigital

---

# Legenda curta: Stories / Status / Reels

A IA não lê palavras: lê pedaços, e cada pedaço vira um número. 🧠
Sozinha, ela não calcula: adivinha o resultado.
A solução: ela escreve a conta e um computador calcula.
A sua imaginação é o limite. 🚀

#IA #InteligenciaArtificial #Produtividade

---

# O que sustenta cada frase
- **"Todo texto é cortado em pedaços; cada pedaço vira um número":** é a tokenização. "Pedaço" é o token.
- **Os cortes do carrossel são reais**, feitos pelo cortador do projeto 06 (`06-completar-texto/pedacos.py`, treinado em artigos em português): "almoxarifado" em seis pedaços, "empresa" em um, e os números embaixo de "a bomba parou de novo" são os números de verdade na lista dele. **Cada IA corta de um jeito:** numa IA comercial os cortes e os números são outros. Se perguntarem, é um exemplo do mecanismo, não o corte de uma IA específica.
- **O corte do número grande (quadro 5) é ilustração:** as IAs comerciais cortam números em grupos de poucos dígitos; o cortador do projeto 06 corta dígito por dígito. O quadro mostra a ideia.
- **"Não calcula: adivinha os pedaços do resultado":** vale para o modelo sozinho.
- **"Como resolveram: ela escreve a conta como um programa e um computador executa":** pesquisado nas páginas oficiais (02/10/2026), sem citar marcas no post:
  - ChatGPT: "writes and runs Python code" num ambiente isolado para cálculos e análise de dados ([ajuda da OpenAI](https://help.openai.com/en/articles/8437071-data-analysis-with-chatgpt)).
  - Claude: ferramenta de execução de código, que roda Python num ambiente isolado para análise e "complex calculations" ([documentação](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool)); o anúncio da ferramenta de análise fala em respostas "mathematically precise and reproducible" ([blog](https://claude.com/blog/analysis-tool)).
  - Gemini: "code execution", em que o modelo gera e roda Python e usa o resultado na resposta ([documentação](https://ai.google.dev/gemini-api/docs/code-execution)).
- **"Nem sempre é usada":** a ferramenta depende do plano, da configuração e de a IA decidir acioná-la; por isso a orientação de conferir e de pedir. O exemplo do quadro 6 (48392 × 7615 = 368.505.080) foi calculado de verdade.
- **"Sem ferramenta, a multiplicação grande falha":** estudos recentes mostram a precisão caindo com o número de dígitos ([Universidade de Chicago](https://cs.uchicago.edu/news/why-cant-powerful-llms-learn-multiplication/)).
- **"Conta pequena ela acerta; conta grande é palpite":** descrição correta em geral. Os modelos atuais acertam bastante coisa, e erram mais em multiplicações com muitos dígitos. O post não diz que ela sempre erra.
- **"Contar letras dá o mesmo problema":** consequência de ela ver pedaços e não letras; é um tropeço conhecido.
- **Coerência com a parte 1:** lá o gancho foi "por que ela erra contas simples". Aqui o título é "por que a IA erra contas" e o texto fala em conta grande, que é o que se sustenta.
- **Termos técnicos (regra da série):** token, tokenização, vocabulário e execução de código, cada um com a sua metáfora (peças de montar, calculadora de bolso).
- **Regras:** sem números no texto do post (os do carrossel são os exemplos de pedaço e de conta, sem medida de desempenho), sem nome de ferramenta, sem sigla.
