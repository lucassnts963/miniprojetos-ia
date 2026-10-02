# Post LinkedIn: "IA sem mistério", parte 2 (quarta 07/10, vai com o carrossel)

**Carrossel:** `parte2/01.png` a `08.png` (1080x1350), `carrossel.pdf` e `panorama.png`. Para refazer: `python posts/serie_ia/parte2.py`.
- Quadros: capa → ela lê pedaços → a regra do corte → cada pedaço vira um número → por isso ela tropeça → com texto ela é ótima → na prática → fechamento.
- No rodapé, a frase atravessa os 8 quadros já cortada em pedaços: "A IA não lê palavras: ela corta o texto em pedaços, troca cada pedaço por um número e adivinha o próximo."
- Poste as 8 imagens na ordem.

Você já viu uma IA escrever um relatório inteiro em segundos e, logo depois, errar uma conta?

Parece contraditório. Não é. O motivo está no jeito como ela lê.

Esta é a parte 2 da série IA sem mistério. 🧠 Na parte 1, vimos que a IA escreve adivinhando a próxima palavra. Hoje, um ajuste nessa história: não é bem palavra.

Ela não lê palavras. Lê pedaços.

Antes de chegar à IA, todo texto é cortado em pedaços menores:
✅ palavra comum vira um pedaço só;
✅ palavra rara é montada com vários pedaços;
✅ cada pedaço é trocado por um número, e é só isso que ela enxerga.

Ela nunca vê letras. E um número grande também é cortado em pedaços.

Por isso, diante de uma conta, a IA não calcula: ela adivinha os pedaços do resultado, do mesmo jeito que adivinha palavras. Conta pequena ela já viu muitas vezes e acerta. Conta grande, que ela nunca viu igual, é palpite. Contar as letras de uma palavra dá o mesmo problema.

O outro lado da moeda: é esse mesmo mecanismo que a faz tão boa com linguagem. Resumir, reescrever, explicar, organizar.

💡 O que muda na prática
Texto é com ela. Número exato é com a calculadora.
• Peça a fórmula ou a planilha: ela monta a conta, a planilha calcula.
• Peça para usar a calculadora: muitas IAs têm uma, e avisam quando usam.
• Confira o que for crítico.

🏭 Na indústria: horas de parada, custos de manutenção e saldos de estoque somados "de cabeça" pela IA merecem conferência. Melhor pedir a planilha pronta.
🛒 No comércio: totais de pedido, descontos e comissões seguem a mesma regra.

As aplicações são inúmeras. E, como gosto de dizer: a sua imaginação é o limite. 🚀

Já pegou uma IA errando uma conta ou um total? Me conta nos comentários 👇

#InteligenciaArtificial #IA #Produtividade #Industria40 #Inovacao #TransformacaoDigital

---

# Legenda curta: Stories / Status / Reels

A IA não lê palavras: lê pedaços, e cada pedaço vira um número. 🧠
Por isso ela não calcula: adivinha o resultado.
Texto é com ela. Número exato é com a calculadora.
A sua imaginação é o limite. 🚀

#IA #InteligenciaArtificial #Produtividade

---

# O que sustenta cada frase
- **"Todo texto é cortado em pedaços; cada pedaço vira um número":** é a tokenização. "Pedaço" é o token.
- **Os cortes do carrossel são reais**, feitos pelo cortador do projeto 06 (`06-completar-texto/pedacos.py`, treinado em artigos em português): "almoxarifado" em seis pedaços, "empresa" em um, e os números embaixo de "a bomba parou de novo" são os números de verdade na lista dele. **Cada IA corta de um jeito:** numa IA comercial os cortes e os números são outros. Se perguntarem, é um exemplo do mecanismo, não o corte de uma IA específica.
- **O corte do número grande (quadro 5) é ilustração:** as IAs comerciais cortam números em grupos de poucos dígitos; o cortador do projeto 06 corta dígito por dígito. O quadro mostra a ideia.
- **"Não calcula: adivinha os pedaços do resultado":** vale para o modelo sozinho. Muitos produtos hoje acionam uma calculadora ou escrevem um programa para fazer a conta, e aí o resultado é confiável; por isso o post diz "muitas IAs têm uma".
- **"Conta pequena ela acerta; conta grande é palpite":** descrição correta em geral. Os modelos atuais acertam bastante coisa, e erram mais em multiplicações com muitos dígitos. O post não diz que ela sempre erra.
- **"Contar letras dá o mesmo problema":** consequência de ela ver pedaços e não letras; é um tropeço conhecido.
- **Coerência com a parte 1:** lá o gancho foi "por que ela erra contas simples". Aqui o título é "por que a IA erra contas" e o texto fala em conta grande, que é o que se sustenta.
- **Regras:** sem números no texto do post (os do carrossel são os exemplos de pedaço e de conta, sem medida de desempenho), sem nome de ferramenta, sem sigla.
