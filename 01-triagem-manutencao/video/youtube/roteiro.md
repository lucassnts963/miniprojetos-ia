# YouTube: Rede neural do zero em Python: triagem de chamados de manutenção

Vídeo tutorial 1920x1080, tema elucas.dev. Versão final: `out/triagem_do_zero_narrado.mp4` (6:55, narração + trilha lo-fi). Quem assistir deve conseguir reproduzir o código sozinho: todas as linhas de `tutorial/triagem_do_zero.py` aparecem na tela, com o número real da linha.

- Render: `render.py` (nesta pasta). Sem narração, usa as durações padrão de cada cena. Com `narr/timing.json`, segue a fala.
- Código mostrado: `01-triagem-manutencao/tutorial/triagem_do_zero.py` + `tutorial/chamados.csv` (vão no link da descrição). Os destaques do render apontam para trechos do código, não para números de linha: dá para mexer no tutorial e renderizar de novo.

### Produção (depois de gerar os áudios)
Coloque `parte01.mp3` … `parte04.mp3` em `narr/` e rode, a partir de `C:\dev\miniprojetos-ia`:
```bash
# 1. transcreve com timestamps por palavra (Python com faster-whisper + GPU)
C:\dev\venv\Scripts\python.exe ferramentas\narracao\pipeline.py transcrever 01-triagem-manutencao\video\youtube\narr
# 2. casa a fala com as cenas (âncoras e cues em narr\plano.json) -> narr\timing.json
C:\dev\venv\Scripts\python.exe ferramentas\narracao\pipeline.py sincronizar 01-triagem-manutencao\video\youtube\narr
# 3. renderiza de novo, agora no tempo da fala (Python com pygame + pygments)
C:\dev\snake\venv\Scripts\python.exe 01-triagem-manutencao\video\youtube\render.py
# 4. narração cortada por cena + música com ducking + vídeo
C:\dev\venv\Scripts\python.exe ferramentas\narracao\pipeline.py mixar 01-triagem-manutencao\video\youtube\narr 01-triagem-manutencao\video\youtube\out\video_silent.mp4 01-triagem-manutencao\video\youtube\out\triagem_do_zero_narrado.mp4
# 5. re-transcreve o final e confere o desvio de cada âncora
C:\dev\venv\Scripts\python.exe ferramentas\narracao\pipeline.py verificar 01-triagem-manutencao\video\youtube\narr 01-triagem-manutencao\video\youtube\out\triagem_do_zero_narrado.mp4
```
Se o passo 2 disser "âncora não encontrada", a voz trocou alguma palavra: veja em `narr/words.json` como o Whisper escreveu e ajuste a frase no `plano.json`.

---

## Publicação

**Título (opções)**
1. Rede neural do zero em Python: ela lê chamados de manutenção (só NumPy)
2. Construí uma rede neural camada por camada (e você pode copiar)
3. Classificador de texto do zero: TF-IDF + rede neural + backprop em NumPy

**Descrição**

Neste vídeo a gente escreve, linha por linha, uma rede neural que lê o texto de uma ordem de manutenção e decide a equipe (mecânica, elétrica, instrumentação ou automação) e a prioridade. Sem PyTorch, sem API: só NumPy.

Passo a passo: limpeza do texto, termos (palavras, pares e pedaços de letras), TF-IDF, inicialização de He, forward com ReLU e softmax, uma rede com duas saídas, entropia cruzada, backprop na mão, dropout, L2 e Adam, e o teste honesto com dados separados.

📄 Código completo e o CSV com os 561 chamados de exemplo: [LINK]

Capítulos
0:00 Intro
0:19 O caminho: do texto à decisão
0:44 Preparando o arquivo
1:05 Passo 1 · Os dados
1:31 Passo 2 · Limpando o texto
1:55 Passo 3 · Termos: palavras, pares e pedaços
2:23 Passo 4 · TF-IDF
3:05 Passo 5 · Os pesos da rede
3:38 Passo 6 · Forward, camada por camada
4:15 Passo 7 · A perda (entropia cruzada)
4:35 Passo 8 · Backprop
5:19 Passo 9 · Treino com Adam
5:53 Passo 10 · Testando de verdade
6:18 Resultado honesto
6:37 Como rodar

Música: HoliznaCC0, álbum *Public Domain Lofi* (CC0, domínio público).

**Tags:** rede neural do zero, neural network from scratch, numpy, python, tf-idf, backpropagation, softmax, adam optimizer, classificação de texto, nlp, manutenção industrial, machine learning, inteligência artificial, elucas.dev

---

## Narração para ElevenLabs v3 (copiar e colar)

Mesmas regras do vídeo da cobrinha:
- **Modelo:** Eleven v3. **Stability:** "Creative" ou "Natural".
- As tags entre colchetes dirigem a emoção e não são lidas. Reticências dão respiro e MAIÚSCULAS dão ênfase.
- Nomes de código e números estão escritos como devem ser falados.
- São **4 partes**, cada uma abaixo do limite de uma geração. Salve como `parte01.mp3` … `parte04.mp3` em `video/youtube/narr/`.
- **Não mude as primeiras palavras de cada parágrafo.** Elas são as âncoras que sincronizam a fala com as cenas (ver "Âncoras" no fim).

### Parte 1

```text
[excited] Olha só: eu escrevo o chamado do jeito que o operador escreveria... e a rede já responde. Equipe elétrica. [pause] Sem API, sem PáiTorch. Só NâmPai. [confident] E hoje você vai escrever cada linha disso comigo.

[calm] Uma rede neural do zero... camada por camada.

[warm] O caminho é esse: o texto vira palavras, as palavras viram termos, e os termos viram um vetor de números, com tê éfe ai dê éfe. Esse vetor passa por uma camada oculta de trinta e dois neurônios... e sai em DUAS respostas ao mesmo tempo: a equipe e a prioridade. [pause] Depois, a gente ensina a rede com três peças: a perda, o backprop e o otimizador Adam.

[calm] Cria um arquivo chamado triagem do zero ponto pai. A única dependência é o NâmPai: pip install nâmpai. O resto vem com o Python: csv, math, ri, unicodedata e o Counter. E duas listas com as classes: as quatro equipes e as quatro prioridades. A posição na lista vira o número da classe.

[warm] Passo um: os dados. São quinhentos e sessenta e um chamados num csv separado por ponto e vírgula: o texto, a equipe e a prioridade. Eu gerei esses exemplos uma única vez com uma LLM... e o arquivo está no link da descrição. A função carregar lê o arquivo e devolve os textos e dois vetores de gabarito: um para a equipe e outro para a prioridade. Mecânica vira zero, elétrica vira um... e assim por diante.
```

### Parte 2

```text
[calm] Passo dois: limpar o texto. Primeiro, tudo minúsculo. Depois, o éne éfe ká dê separa a letra do acento... e a gente joga o acento fora. Assim, óleo com acento e oleo sem acento viram a MESMA coisa. Por fim, uma expressão regular pega só letras e números. Vírgula, ponto, exclamação... tudo some.

[curious] Passo três: os termos. Palavra solta é pouco. Então cada chamado vira três tipos de termo: as palavras... os pares de palavras vizinhas, que pegam coisas como "não comunica"... e pedaços de três a cinco letras. [pause] Por que pedaços? Olha vazando e vazamento. São palavras diferentes, mas dividem vários pedaços. Então, se no treino só apareceu vazamento, a rede ainda reconhece vazando.

[confident] Passo quatro: transformar termos em números, com tê éfe ai dê éfe. No fit, a gente conta em quantos chamados cada termo aparece: esse é o dê éfe. Termo que aparece em menos de dois chamados fica de fora. O ai dê éfe dá peso alto para termo raro, como prensa, e peso baixo para termo que aparece em todo lugar, como "de". No transform, cada chamado vira um vetor do tamanho do vocabulário: mais de cinco mil posições... e quase todas zero. Onde o termo aparece, entra um mais o log da contagem, vezes o ai dê éfe. No final, a gente divide pelo tamanho do vetor, para chamado curto e chamado longo ficarem na mesma escala.

[warm] Passo cinco: a rede. Ela é só um dicionário de matrizes. W1 liga cada termo do vocabulário aos trinta e dois neurônios da camada oculta. Depois vêm DUAS saídas: W é, que liga a oculta às quatro equipes... e W pê, que liga às quatro prioridades. Os pesos começam aleatórios, multiplicados pela raiz de dois sobre o tamanho da entrada. É a inicialização de He, que combina com a rélu e evita que o sinal exploda ou suma. Somando tudo, são quase cento e setenta e cinco mil números.
```

### Parte 3

```text
[confident] Passo seis: o forward, camada por camada. Primeiro, a camada oculta: o vetor de entrada vezes W1, mais o viés. Isso dá trinta e dois números, positivos e negativos. Depois vem a rélu: o que é negativo vira zero. [pause] É isso que deixa a rede aprender coisas que não são uma linha reta. Por fim, cada saída multiplica a oculta pelos próprios pesos, e o soft max transforma esses números em probabilidades que somam um. Repara que as duas saídas leem a MESMA camada oculta: o que a rede aprende sobre a equipe ajuda na prioridade... e vice-versa.

[calm] Passo sete: como medir o erro. A entropia cruzada olha só a probabilidade que a rede deu para a resposta certa... e tira menos o log. Se ela deu noventa por cento, a perda é pequena. Se deu dez por cento, a perda explode. E como a rede tem duas saídas, a perda total é a soma das duas.

[excited] Passo oito: o backprop, de trás para frente. E aqui tem um presente da matemática: o gradiente do soft max com a entropia cruzada é só a probabilidade menos o gabarito. [pause] Com isso, o gradiente dos pesos de saída é a oculta transposta vezes esse erro. Depois, o erro volta para a camada oculta: a gente soma o que vem das DUAS saídas... e zera onde a rélu estava desligada e onde o dropout desligou o neurônio. O dropout, lá no começo da função, desliga metade dos neurônios a cada lote, para a rede não decorar. Por último, o gradiente de W1 é a entrada transposta vezes esse erro. [curious] E tem um detalhe bonito: como a entrada é quase toda zero, só mudam as linhas dos termos que estavam no chamado.
```

### Parte 4

```text
[warm] Passo nove: o treino. A cada época, a gente embaralha os dados e anda em lotes de trinta e dois. Para cada lote: calcula os gradientes, soma o L2, que segura os pesos perto de zero... e aplica o Adam. O Adam guarda duas médias: a do gradiente, que dá a direção, e a do gradiente ao quadrado, que ajusta o tamanho do passo de cada peso. A correção com o número do passo só compensa o começo, quando as médias ainda estão zeradas. [pause] Olha a perda caindo: cem épocas... em poucos segundos.

[confident] Passo dez: testar de verdade. Separa oitenta por cento para treino e vinte para teste. E atenção: o tê éfe ai dê éfe só pode aprender o vocabulário com o treino. Se olhar o teste, é cola. Treina, roda o forward no teste e compara. Aqui deu noventa e oito por cento na equipe e cinquenta e nove na prioridade. E o chamado do começo? Elétrica.

[calm] Sendo honesto: esse corte teve sorte. Com validação cruzada, a equipe fica perto de noventa e dois por cento. A prioridade é o ponto fraco, porque a fronteira entre alta e média é subjetiva até para gente. E o que mais melhorou o resultado foi ter mais exemplos... não uma rede maior.

[warm] Para rodar: baixa o csv da descrição, coloca na mesma pasta do arquivo e roda python triagem do zero ponto pai.

[excited] O código completo está na descrição. E, como eu sempre digo... a sua imaginação é o limite. Até a próxima!
```

---

## Âncoras (cena ↔ começo da fala)

Usadas no `sync` para casar a narração com as cenas do `render.py`. A cena começa quando a narração diz a âncora. Os cues destacam as linhas de código na hora em que a frase é dita.

| Cena | Parte | Âncora | Cues (frase → destaque) |
|---|---|---|---|
| hook | 01 | "olha só eu escrevo" | |
| titulo | 01 | "uma rede neural do zero" | |
| mapa | 01 | "o caminho é esse" | palavras: "o texto vira", tfidf: "e os termos viram", oculta: "esse vetor passa", saidas: "e sai em", treino: "depois a gente ensina" |
| setup | 01 | "cria um arquivo" | numpy: "a única dependência", imports: "o resto vem", classes: "e duas listas" |
| dados | 01 | "passo um" | csv: "são quinhentos", carregar: "a função carregar", y: "mecânica vira" |
| palavras | 02 | "passo dois" | lower: "primeiro tudo", acento: "depois o", regex: "por fim uma" |
| termos | 02 | "passo três" | w: "as palavras", b: "os pares", c: "e pedaços", comp: "por que pedaços" |
| tfidf | 02 | "passo quatro" | df: "no fit", mindf: "termo que aparece em menos", idf: "o ai dê", transform: "no transform", tf: "onde o termo", norma: "no final" |
| pesos | 02 | "passo cinco" | w1: "w1 liga", saidas: "depois vêm", he: "os pesos começam", total: "somando tudo" |
| forward | 03 | "passo seis" | z1: "primeiro a camada", relu: "depois vem a", saidas: "por fim cada", compart: "repara que" |
| perda | 03 | "passo sete" | log: "a entropia cruzada", p90: "se ela deu", p10: "se deu dez", soma: "e como a rede" |
| backprop | 03 | "passo oito" | dsaida: "e aqui tem", gsaida: "com isso", dh: "depois o erro", mascara: "o dropout lá", gw1: "por último", esparso: "e tem um detalhe" |
| adam | 04 | "passo nove" | lote: "a cada época", l2: "calcula os gradientes", mv: "o adam guarda", hat: "a correção", curva: "olha a perda" |
| teste | 04 | "passo dez" | split: "separa oitenta", fit: "e atenção", acc: "treina roda", exemplo: "e o chamado do começo" |
| honesto | 04 | "sendo honesto" | |
| rodar | 04 | "para rodar" | |
| outro | 04 | "o código completo" | |
