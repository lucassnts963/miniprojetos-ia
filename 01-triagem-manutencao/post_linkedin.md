# Post LinkedIn (vai junto com `video/linkedin_triagem.mp4`)

Vídeo de 50 s: a cena animada (visão geral e escala) seguida do painel da bancada em uso (por dentro, sem caixa-preta). Gerado juntando `video/cena_triagem.mp4` + `video/painel_triagem_continua.mp4` (`python video/gravar_painel.py --juntar`).

Quanto tempo a sua equipe perde lendo chamado por chamado só para decidir quem vai atender e o que é mais urgente?

No meu último post, mostrei uma IA aprendendo sozinha a jogar o jogo da cobrinha. 🐍 E deixei uma promessa no ar: o mesmo princípio serve para triar ordens de manutenção.

Então fui lá e fiz.

O operador escreve o problema do jeito dele, com as palavras dele. Coisas como "o motor da bomba tá cheirando queimado" ou "vazamento de óleo na prensa, pingando no chão".
Na hora, a IA diz:
✅ qual equipe deve atender: mecânica, elétrica, instrumentação ou automação;
✅ qual a prioridade: urgente, alta, média ou baixa;
✅ e o porquê: ela destaca as palavras que pesaram na decisão.

Esse último ponto faz toda a diferença. Não é uma caixa-preta. O supervisor enxerga o motivo de cada decisão e, quando ela erra, corrige. A correção vira aprendizado na próxima rodada.

💡 E o custo?
Usei uma LLM (ChatGPT, Claude etc.) uma única vez, só para gerar exemplos de chamados. A partir daí, a IA própria faz a triagem sozinha, sem pagar nada por chamado e sem mandar os dados da operação para fora da empresa.

No vídeo dá para ver os chamados chegando, a IA lendo cada um e mandando para a fila certa, até virar um fluxo contínuo.

E não para na manutenção. A mesma ideia serve para:

🏭 Na indústria
• Separar solicitações de serviço por área e criticidade.
• Encaminhar ocorrências de segurança e qualidade para quem precisa agir.

🛒 No comércio e nos serviços
• Mandar cada atendimento para o setor certo: financeiro, entrega, troca, suporte.
• Identificar as reclamações que não podem esperar.

As aplicações são inúmeras. E, como gosto de dizer: a sua imaginação é o limite. 🚀

Na sua empresa, quem faz essa triagem hoje, e quanto tempo isso consome? Me conta nos comentários 👇

#InteligenciaArtificial #Manutencao #Industria40 #Automacao #Inovacao #IA

---

# Legenda curta: Stories / Status / Reels

Lembra da IA que aprendeu sozinha a jogar a cobrinha? 🐍
Agora ela faz a triagem de ordens de manutenção: lê o chamado, escolhe a equipe, define a prioridade e mostra o porquê.
Sem pagar uma LLM a cada chamado. A sua imaginação é o limite. 🚀

#IA #Manutencao #Automacao

---

# Checagem de consistência com o vídeo
- Frases citadas no post aparecem digitadas no vídeo: "o motor da bomba 2 tá cheirando queimado" (o post corta o "2" para não ter número) e "vazamento de óleo na prensa, pingando no chão".
- As quatro equipes e as quatro prioridades do post são as mesmas do vídeo.
- "Destaca as palavras que pesaram": na cena, "por causa de" + palavras destacadas no card; no painel, as palavras marcadas em "o que pesou na decisão".
- "Até virar um fluxo contínuo": é a enxurrada do final do vídeo.
- "Quando ela erra, corrige": continua **fora** do vídeo (o painel no modo vídeo esconde "Ensinar a rede"). Tire esse trecho do post ou peça uma cena de correção.
- Os chamados que aparecem nas duas partes do vídeo têm a mesma decisão (conferido com o modelo atual). Se retreinar o modelo, renderize as duas partes de novo.
- Sem números no texto. "Uma única vez" descreve o método, não uma quantidade.
