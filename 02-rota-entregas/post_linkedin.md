# Post LinkedIn: menor rota pelas cidades (vai junto com `video/linkedin_rota.mp4`)

Vídeo de 54 s, com trilha lo-fi: o método (rotas evoluindo e a melhor rota com prova) → o dado certo (mapa x estrada, Brasil inteiro) → na prática (separação de pedidos no armazém).

Miniatura: `video/miniatura_linkedin.png` (quadro aos 45 s do vídeo): os dois armazéns, com a rota otimizada já em "pedido separado" e a outra ainda andando, e as barras de caminhada. É o quadro que responde à pergunta de abertura (rodando mais do que precisava).

Quanto a sua operação gasta por dia rodando mais do que precisava?

Entregas, visitas técnicas, rotas de vendedores, coleta de amostras, manutenção em campo. Toda empresa que coloca gente na estrada enfrenta a mesma pergunta: em que ordem visitar cada lugar para rodar o mínimo possível?

Nos últimos posts, mostrei uma IA aprendendo a jogar a cobrinha sozinha 🐍 e depois uma IA lendo e triando ordens de manutenção. Desta vez, levei aquele mesmo método da cobrinha para o problema das rotas: rotas embaralhadas que evoluem, geração após geração, até ficarem curtas.

Funcionou. Mas o resultado mais interessante foi outro.

💡 Nem tudo precisa de IA.
Um método matemático clássico, bem mais antigo que qualquer IA da moda, chegou à melhor rota possível. Não uma rota "boa": a melhor, com prova de que não existe outra mais curta. E em uma fração do tempo.

🛣️ E o maior ganho nem veio do método.
No começo, a distância entre as cidades era calculada em linha reta, como no mapa. Quando troquei pela distância real pelas estradas, a história mudou: a rota que parecia a mais curta no mapa atravessava rios e baías que, na estrada, viram desvios enormes. Planejar com o dado certo economizou muito mais do que qualquer ajuste de algoritmo.

A lição que eu levo para qualquer projeto:
✅ primeiro, entender bem o problema e ter o dado certo;
✅ depois, escolher a ferramenta mais simples que resolve;
✅ IA entra quando ela é, de fato, o melhor caminho.

🏭 Na indústria
• Separação de pedidos no armazém: o separador anda menos entre as prateleiras e o pedido fica pronto antes.
• Rotas de manutenção em campo e visitas técnicas.
• Sequência de coleta de matéria-prima entre fornecedores.

🛒 No comércio e nos serviços
• Entregas do dia com menos quilômetros e menos horas de motorista.
• Roteiro de vendedores e representantes pela região.

As aplicações são inúmeras. E, como gosto de dizer: a sua imaginação é o limite. 🚀

E na sua empresa: qual problema está esperando uma "IA" quando, na verdade, precisa de um dado melhor ou de uma solução mais simples? Me conta nos comentários 👇

#Logistica #Otimizacao #InteligenciaArtificial #Industria40 #Dados #Inovacao

---

# Legenda curta: Stories / Status / Reels

A rota mais curta no mapa nem sempre é a mais curta na estrada. 🛣️
Testei o método da cobrinha, testei matemática clássica, e o que mais fez diferença foi usar a distância real pelas estradas.
Nem tudo precisa de IA. A sua imaginação é o limite. 🚀

#Logistica #Otimizacao #IA

---

# O que sustenta cada frase (para não prometer o que o projeto não fez)
- "O mesmo método da cobrinha funcionou": o algoritmo genético (`genetico.py`) chegou à melhor rota nas capitais em uma rodada e ficou perto dela em outras.
- "Um método clássico chegou à melhor rota possível, com prova, em uma fração do tempo": `exato.py` (programação linear inteira) provou o ótimo das capitais em menos de 1 s; o genético leva dezenas de segundos.
- "A rota que parecia mais curta no mapa atravessava rios e baías": `rota.py --modo comparar`. Exemplo das capitais: saindo de Belém, a rota em linha reta vai primeiro a Macapá, que pela estrada exige balsa e desvio.
- "Economizou muito mais do que qualquer ajuste de algoritmo": no Brasil inteiro, planejar pela estrada rodou bem menos que seguir, na estrada, a ordem planejada em linha reta; entre os métodos, as diferenças foram pequenas perto disso.
- Sem números no texto (regra dos posts). Os números estão no README do projeto, se alguém perguntar nos comentários.

# Vídeo (`video/linkedin_rota.mp4`) e o que ele mostra
1. **O método** (`cena_metodo.mp4`): a melhor rota de cada geração do genético pelas capitais, encolhendo; depois a melhor rota possível, com o selo "com prova" (método exato).
2. **O dado certo** (`cena_estrada.mp4`): Brasil inteiro, rota planejada no mapa x planejada pela estrada; barras com os quilômetros rodados na estrada pelas duas (mesma escala).
3. **Na prática** (`cena_picking.mp4`): dois armazéns, mesmo pedido e mesma velocidade; o algoritmo calcula a ordem antes de o separador sair; o da rota otimizada termina antes e anda bem menos.
- Tudo calculado de verdade (`cenas_mapa.py`, `cena_picking.py`); nenhuma rota é desenhada à mão. Sem números na tela.
- Coerência com o texto: "o mesmo método da cobrinha funcionou" (cena 1), "melhor rota possível, com prova" (cena 1), "distância real pelas estradas" (cena 2), "separação de pedidos" (cena 3), fechamento com a frase de assinatura (cena 3).
- No armazém, a lista chega em ordem de código de produto (aleatória em relação às prateleiras). Entre pedidos sorteados, a rota otimizada andou de 52% a 60% menos; na prática, o ganho depende de como a lista já vem ordenada.
