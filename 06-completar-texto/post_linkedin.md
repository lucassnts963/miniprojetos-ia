# Post LinkedIn: "Como uma LLM funciona", parte 1 (terça 06/10, vai junto com `video/linkedin_completar.mp4`)

Vídeo de 58 s, com trilha lo-fi: o teclado do celular → apostar no próximo pedaço (contando) → escolher e apostar de novo → contagem x rede neural → a escala → na prática (pedido vago x começo claro) → fechamento.

Miniatura: `video/miniatura_linkedin.png` (quadro aos 20 s): a frase sendo completada, com as apostas em barras. É o quadro que responde à pergunta de abertura (o que a IA faz quando "responde").

Você já pediu algo para uma IA e recebeu uma resposta genérica, que servia para qualquer empresa menos para a sua?

O problema quase nunca é a ferramenta. É não saber o que ela faz de verdade.

Acredito que o caminho para dominar qualquer tecnologia é conhecer a origem dela e como ela funciona. Quem entende o mecanismo sabe o que pedir, como pedir e quando desconfiar. Por isso, começo hoje uma série curta: como funciona a IA que escreve. 🧠

Parte 1: ela é uma máquina de completar texto.

Você já usa uma versão simples disso todo dia: o teclado do celular, sugerindo a próxima palavra.

A IA que escreve faz a mesma coisa, levada ao extremo:
✅ olha o texto que já existe;
✅ aposta em qual pedaço vem depois;
✅ escolhe um, cola no texto e aposta de novo.

Só isso. Resumir, traduzir, responder, programar: para ela, tudo é continuar um texto.

Para não ficar só na teoria, construí uma em miniatura, do zero, e deixei as apostas à mostra. É o que aparece no vídeo. Primeiro do jeito antigo, só contando o que costuma vir depois: ela enxerga poucas palavras para trás e perde o fio da conversa. Depois com uma rede que pesa o texto inteiro: o assunto se mantém.

A minha é minúscula, e erra bastante. As grandes leram uma parte enorme do que a humanidade escreveu. Mas a tarefa é a mesma.

💡 O que muda na prática
Se ela continua o que você começa, o começo é tudo. Pedido vago aceita qualquer continuação, e você recebe a mais comum. Antes de pedir, diga:
• o papel: quem ela deve ser;
• o contexto: os dados e a situação;
• o formato: como você quer a resposta.

🏭 Na indústria: em vez de "faça um relatório", dizer que ela é o planejador de manutenção, entregar as paradas do mês e pedir um resumo em tópicos para a diretoria.
🛒 No comércio: em vez de "responda este cliente", entregar o histórico do pedido, a política de troca e o tom da sua marca.

As aplicações são inúmeras. E, como gosto de dizer: a sua imaginação é o limite. 🚀

Qual foi o pedido que você fez a uma IA e que voltou mais longe do que você esperava? Me conta nos comentários 👇

#InteligenciaArtificial #IA #Produtividade #Industria40 #Inovacao #TransformacaoDigital

---

# Legenda curta: Stories / Status / Reels

A IA que escreve é uma máquina de completar texto. 🧠
Ela aposta no próximo pedaço, escolhe um e aposta de novo.
Por isso o começo é tudo: diga o papel, o contexto e o formato.
A sua imaginação é o limite. 🚀

#IA #InteligenciaArtificial #Produtividade

---

# O que sustenta cada frase
- **"Aposta em qual pedaço vem depois, escolhe um e aposta de novo":** é o funcionamento das LLMs (geração de um token por vez). "Pedaço" é o token: menor que uma palavra, assunto da parte 2.
- **"Para ela, tudo é continuar um texto":** vale para o modelo em si. Os produtos em volta acrescentam busca, ferramentas e memória; isso fica para as próximas partes. Se perguntarem, é simplificação assumida.
- **"Construí uma em miniatura, do zero":** `06-completar-texto/` (pedaços, contagem, rede, painel na bancada).
- **"Só contando, perde o fio; a rede mantém o assunto":** é o que o vídeo mostra, com textos gerados de verdade pelos dois métodos a partir de "A bomba hidráulica". A contagem pula para IBGE e habitantes; a rede segue falando de eixo, energia e máquina. Nos números, a rede acerta mais que a contagem, mas por margem pequena (README do projeto).
- **"A minha é minúscula, e erra bastante":** é verdade e está no vídeo: os textos gerados fazem sentido na forma, não no conteúdo ("a manutenção preventiva é o processo de reparação…", "a bomba hidráulica é uma subárea da mecânica…").
- **"Pedido vago recebe a continuação mais comum":** consequência do mecanismo, dita como orientação. O leque de continuações no vídeo é uma ilustração, não uma medição.
- **Regras:** sem números; "LLM" aparece só no nome da série, no vídeo; o texto fala "IA que escreve". Os termos novos ("pedaço") vêm explicados na mesma frase.

# Vídeo e coerência com o texto
- Teclado do celular (abertura), as três etapas (ideia e truque), contagem x rede (salto), "as grandes leram uma parte enorme" (escala), papel/contexto/formato com o exemplo do planejador de manutenção (na prática), assinatura (fechamento).
- As barras de apostas e os textos vêm do modelo treinado (`video/preparar.py` → `dados.json`). Se retreinar o modelo, rode `preparar.py` e renderize de novo.
- O exemplo do comércio está só no texto, não no vídeo.
