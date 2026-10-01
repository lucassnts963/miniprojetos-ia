# Post LinkedIn: pessoa em área de risco (visão computacional)

A sua empresa já é obrigada a separar gente de máquina em movimento. E se a câmera que já está instalada avisasse na hora em que alguém entra na área errada?

No último post, defendi que nem tudo precisa de IA: para achar a menor rota, a matemática clássica ganhou. Hoje é o outro lado da moeda.

Não existe fórmula para dizer "isso é uma pessoa". O padrão está na imagem, e é exatamente aí que a IA faz sentido.

O que eu montei é simples de explicar:
✅ você desenha, em cima da imagem da câmera, a área de risco: o corredor da empilhadeira, a zona de uma máquina;
✅ a IA encontra as pessoas no vídeo;
✅ uma regra de geometria verifica se alguém está pisando dentro da área. Se estiver, alerta.

Repara na divisão do trabalho: a IA só faz a parte que não tem fórmula, que é reconhecer a pessoa. Decidir se ela está dentro ou fora da área continua sendo uma conta simples.

E eu não treinei nada. Usei um modelo pronto, que já sabe reconhecer pessoas, e vídeos públicos de armazém para testar.

O que eu aprendi testando, e que ninguém conta no folder:
⚠️ de longe e de frente, funciona bem; com a câmera olhando de cima, ele deixa de ver gente;
⚠️ a contagem oscila de um instante para o outro, então o alerta só dispara quando a pessoa permanece na área;
⚠️ câmera filma pessoas: precisa de finalidade clara, aviso e cuidado com os dados. A ideia é registrar o evento, não vigiar ninguém.

Essa tecnologia apoia o técnico de segurança. Não substitui o treinamento, a sinalização nem a pessoa responsável.

E a mesma base serve para a operação:

🏭 Na indústria
• Pedestre na área de circulação de empilhadeira ou perto de máquina em movimento.
• Quantas pessoas há em cada área, e por quanto tempo.

🛒 No comércio e nos serviços
• Fila crescendo no caixa ou no balcão de atendimento.
• Acesso a estoque e a áreas restritas.

As aplicações são inúmeras. E, como gosto de dizer: a sua imaginação é o limite. 🚀

Na sua operação, onde uma câmera que já existe poderia avisar antes de o acidente acontecer? Me conta nos comentários 👇

#SegurancaDoTrabalho #VisaoComputacional #InteligenciaArtificial #Industria40 #Logistica #Inovacao

---

# Legenda curta: Stories / Status / Reels

A câmera já está lá. E se ela avisasse quando alguém entra na área da empilhadeira? 🚧
A IA reconhece a pessoa; uma regra simples diz se ela está na área de risco.
Apoia a segurança, não substitui. A sua imaginação é o limite. 🚀

#SegurancaDoTrabalho #IA #Logistica

---

# O que sustenta cada frase
- "Obrigada a separar gente de máquina": NR-11 (movimentação de materiais) e NR-12 (zonas de perigo de máquinas). O post não cita as normas pelo número para seguir a regra de não usar siglas técnicas; se quiser, dá para citar.
- "Não treinei nada, usei um modelo pronto e vídeos públicos": `detector.py` (modelo pré-treinado) e `baixar_videos.py` (bancos de vídeo com licença livre).
- "De longe e de frente funciona; de cima deixa de ver gente": teste do README. Nos três modelos testados, o operador sentado na empilhadeira, visto de cima, não foi detectado.
- "A contagem oscila, o alerta só dispara quando a pessoa permanece": regra dos quadros seguidos no `demo.py`.
- Sem números no texto (regra dos posts).

# Vídeo: ainda não existe
Sugestão coerente com o texto, gravada no painel da bancada (modo vídeo):
1. A imagem da câmera; a área de risco sendo desenhada no chão.
2. Pessoas marcadas em verde; alguém entra na área, fica vermelho e aparece o alerta.
3. A linha do tempo com os alertas do vídeo inteiro.
4. Fechamento: "A sua imaginação é o limite."
Atenção antes de publicar: os vídeos de teste mostram pessoas identificáveis e têm movimento de câmera. Para o vídeo do post, usar um trecho de plano aberto com a câmera parada e borrar os rostos.
