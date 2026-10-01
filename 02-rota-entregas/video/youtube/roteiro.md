# YouTube: Nem tudo precisa de IA: a menor rota pelas capitais em Python

Vídeo 1920x1080, tema elucas.dev. O foco é resolver um problema sem necessariamente usar IA, e mostrar com medições por que a IA não é a melhor ferramenta aqui e quais são as limitações dela (e as dos métodos clássicos também).

- Render: `render.py` (nesta pasta). Sem narração, usa as durações padrão; com `narr/timing.json`, segue a fala.
- Código mostrado: `02-rota-entregas/tutorial/rota_do_zero.py` + `tutorial/capitais.csv`. Todos os números do vídeo saem desse arquivo rodando (e do projeto, para o Brasil inteiro e para a estrada).

### Produção (depois de gerar os áudios)
Coloque `parte01.mp3` … `parte04.mp3` em `narr/` e rode, a partir de `C:\dev\miniprojetos-ia`:
```bash
C:\dev\venv\Scripts\python.exe ferramentas\narracao\pipeline.py transcrever 02-rota-entregas\video\youtube\narr
C:\dev\venv\Scripts\python.exe ferramentas\narracao\pipeline.py sincronizar 02-rota-entregas\video\youtube\narr
ferramentas\venv-video\Scripts\python.exe 02-rota-entregas\video\youtube\render.py
C:\dev\venv\Scripts\python.exe ferramentas\narracao\pipeline.py mixar 02-rota-entregas\video\youtube\narr 02-rota-entregas\video\youtube\out\video_silent.mp4 02-rota-entregas\video\youtube\out\rota_do_zero_narrado.mp4
C:\dev\venv\Scripts\python.exe ferramentas\narracao\pipeline.py verificar 02-rota-entregas\video\youtube\narr 02-rota-entregas\video\youtube\out\rota_do_zero_narrado.mp4
```

---

## Publicação

**Título (opções)**
1. Nem tudo precisa de IA: um método de 1954 venceu meu algoritmo genético
2. Caixeiro-viajante em Python: IA x matemática clássica (com prova)
3. A menor rota pelas 27 capitais: força bruta, genético e o ótimo comprovado

**Descrição**

Qual é a menor rota para visitar as 27 capitais do Brasil saindo de Belém? Neste vídeo eu resolvo o problema do caixeiro-viajante de cinco jeitos (força bruta, vizinho mais próximo, 2-opt, algoritmo genético e programação linear inteira) e comparo tempo, distância e garantia.

O algoritmo genético, o mesmo que ensinou a cobrinha a jogar, funciona, mas tem limitações claras: não sabe quando chegou no ótimo, muda de resposta a cada rodada, é lento e não prova nada. Um método clássico de 1954 acha a melhor rota, com prova, em centésimos de segundo. E o maior ganho de todos não veio do algoritmo: veio de trocar a distância em linha reta pela distância real pelas rodovias.

📄 Código completo e os dados: https://github.com/lucassnts963/miniprojetos-ia/tree/main/02-rota-entregas

Capítulos: (preencher com os tempos do `timing.json` depois da narração)

Distâncias rodoviárias: Saldanha (2024), Zenodo 10.5281/zenodo.11400243, CC BY 4.0 (OSRM + OpenStreetMap).
Música: HoliznaCC0, álbum *Public Domain Lofi* (CC0, domínio público).

**Tags:** caixeiro viajante, traveling salesman python, tsp, algoritmo genético, 2-opt, programação linear inteira, otimização, roteirização, logística, scipy milp, numpy, nem tudo precisa de ia, elucas.dev

---

## Narração para ElevenLabs v3 (copiar e colar)

Mesmas regras dos outros vídeos: Eleven v3, Stability "Creative" ou "Natural"; as tags entre colchetes não são lidas; números e nomes de código estão escritos como devem ser falados. São **4 partes**; salve como `parte01.mp3` … `parte04.mp3` em `video/youtube/narr/`. **Não mude as primeiras palavras de cada parágrafo** (são as âncoras da sincronia).

### Parte 1

```text
[curious] Qual é a menor rota para visitar as vinte e sete capitais do Brasil, saindo de Belém? [pause] Eu tentei com inteligência artificial... [mischievously] e ela perdeu para um método de mil novecentos e cinquenta e quatro.

[confident] Nem tudo precisa de IA.

[calm] Esse é o problema do caixeiro-viajante. Parece simples: é só testar todas as ordens e ficar com a menor. [pause] Só que, com vinte e sete cidades, existem quatrocentos SEPTILHÕES de ordens possíveis. No meu computador, testar todas levaria milhares de vezes a idade do universo.

[warm] Passo um: os dados. Um csv com as capitais, a latitude e a longitude. A função matriz km calcula a distância entre todos os pares, pela fórmula de haversine, que é a distância pelo arco da Terra. E a função comprimento soma os trechos de uma rota.

[calm] Passo dois: a força bruta. Gera todas as permutações e guarda a melhor. Com nove cidades são quarenta mil ordens, e sai na hora. [pause] Mas cada cidade a mais multiplica o trabalho. Com vinte cidades, já seriam dezenove mil anos.
```

### Parte 2

```text
[warm] Passo três: a ideia mais óbvia. Sai de Belém e vai sempre para a cidade mais perto que ainda falta. É o vizinho mais próximo. É instantâneo... mas deixa as cidades que sobraram para o final, e a rota termina com saltos enormes. Treze mil trezentos e noventa e sete quilômetros.

[confident] Passo quatro: consertar. Quando dois trechos se cruzam, inverter o pedaço do meio descruza a rota, e ela encurta. Esse é o dois-opt: testa as inversões e fica com as que melhoram. Caiu para doze mil novecentos e quarenta e sete quilômetros... em centésimos de segundo.

[excited] Passo cinco: agora, a IA. É o mesmo algoritmo genético que ensinou a cobrinha a jogar: uma população de rotas aleatórias, as melhores têm filhos, e os filhos sofrem mutação. [pause] O detalhe está no cruzamento. Uma rota não pode repetir nem esquecer cidade. Então o filho copia um trecho do pai... e completa com as outras cidades, na ordem em que aparecem na mãe. [calm] Seiscentas gerações depois: treze mil e três quilômetros. Depois de alguns segundos de espera.
```

### Parte 3

```text
[calm] E aqui aparecem as limitações. Primeira: ele não sabe quando chegou. Rodei doze vezes, mudando só a semente aleatória. Ele achou a melhor rota em quatro. Nas outras oito, ficou até sete por cento acima. Segunda: cada rodada dá uma resposta diferente. Terceira: é lento, e piora rápido com mais cidades. Quarta: tem vários botões para ajustar, como população, mutação e gerações. [pause] E nenhuma dessas rodadas consegue PROVAR que a rota é a menor.

[confident] Passo seis: a matemática. Cada ligação entre duas cidades vira uma variável: zero ou um, usa ou não usa. A regra é que toda cidade tem exatamente duas ligações. A gente pede a solução mais barata... e ela vem errada: sete circuitos soltos. [pause] Então a gente proíbe cada um desses circuitos e resolve de novo. Três circuitos. Dois. Um. [excited] Repara que o custo só sobe a cada rodada: ele é um piso, e nenhuma rota fica abaixo dele. Quando o piso vira uma rota de verdade, acabou: é a menor, com prova. Dantzig, Fulkerson e Johnson fizeram isso em mil novecentos e cinquenta e quatro.

[calm] O placar. Vizinho mais próximo: rápido e ruim. Dois-opt: rápido e bom. Genético: lento e sem garantia. Exato: doze mil oitocentos e quarenta e dois quilômetros, em centésimos de segundo, com prova.
```

### Parte 4

```text
[calm] Mas o método exato também tem limite. Provei o ótimo da Paraíba, com duzentas e vinte e três cidades, em quinze segundos. O Paraná, com trezentas e noventa e nove, levou sete minutos. Para os mais de cinco mil municípios do Brasil, não dá para provar. Aí entra a heurística: dois-opt só entre cidades vizinhas, mais alguns refinamentos, resolve o Brasil em um minuto. E nos estados em que eu tinha a prova, ela ficou a menos de um e meio por cento do ótimo.

[curious] E o maior ganho nem veio do algoritmo. Até aqui, a distância era em linha reta. Quando troquei pela distância real pelas rodovias, a viagem ficou quarenta e sete por cento maior do que o mapa dizia. E planejar direto pela estrada economizou quinze por cento, comparado com seguir o plano da linha reta. O dado certo valeu mais que qualquer algoritmo.

[warm] Então, quando usar IA? Quando NÃO existe fórmula. Ler um chamado de manutenção, reconhecer um capacete numa imagem: ali o padrão está nos dados, e é isso que uma rede aprende. Aqui, o objetivo é uma conta exata, com regras claras. Problema assim pede otimização, não aprendizado.

[calm] E isso sai do mapa. Num armazém, a mesma conta define a ordem de separação de um pedido: mesmo separador, mesma velocidade, metade da caminhada.

[warm] Para rodar: pip install nâmpai e sáipai, e python rota do zero ponto pai. O código está na descrição.

[excited] No próximo vídeo, aí sim, um problema que precisa de IA: visão computacional no armazém. E, como eu sempre digo... a sua imaginação é o limite. Até a próxima!
```

---

## De onde vem cada número falado
| Fala | Origem |
|---|---|
| "quatrocentos septilhões de ordens" | 26! = 4,03 × 10²⁶ |
| "milhares de vezes a idade do universo" | 200 mil ordens/s na força bruta → 6,4 × 10¹³ anos; universo: 1,4 × 10¹⁰ |
| "nove cidades, quarenta mil ordens" · "vinte cidades, dezenove mil anos" | 8! = 40.320; 19! ordens ÷ 200 mil/s |
| 13.397 km · 12.947 km · 13.003 km em alguns segundos · 12.842 km em centésimos | saída do `rota_do_zero.py` |
| "doze vezes, achou em quatro, até sete por cento acima" | `genetico` com sementes 0 a 11: ótimo em 4; pior 13.799 km (+7,5%) |
| "sete circuitos, três, dois, um" e o custo subindo | rodadas do `exato`: 12.160 → 12.689 → 12.709 → 12.842 km |
| "mil novecentos e cinquenta e quatro" | Dantzig, Fulkerson e Johnson, *Solution of a Large-Scale Traveling-Salesman Problem* (49 cidades) |
| Paraíba 223 em 15 s · Paraná 399 em 7 min · Brasil em 1 min · "menos de um e meio por cento" | `exato.py` e `rota.py` do projeto (README) |
| "quarenta e sete por cento" · "quinze por cento" | `rota.py --modo comparar`, Brasil saindo de Belém |
| "metade da caminhada" | `video/cena_picking.py`: 52 a 60% menos entre os pedidos sorteados |

O tempo em segundos muda de máquina para máquina e entre medições (o genético ficou entre 2,7 e 4 s); por isso a narração fala em ordens de grandeza ("centésimos de segundo", "alguns segundos") e o número exato aparece só na tela.
