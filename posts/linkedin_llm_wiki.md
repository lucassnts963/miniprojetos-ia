# Post LinkedIn: base de conhecimento viva (LLM Wiki)

Post fora da numeração dos miniprojetos: não tem código nem painel, é um método de trabalho. Vem depois do post 02 ("nem tudo precisa de IA").

**Carrossel:** `carrossel_llm_wiki/01.png` a `08.png` (1080x1350), mais `carrossel.pdf` e `panorama.png`. É um painel contínuo cortado em 8: a linha vermelha e as ilustrações atravessam as emendas. Para refazer: `python posts/carrossel_llm_wiki.py`.
- Para o efeito contínuo, poste as **8 imagens, na ordem**, como post de várias fotos. O PDF (documento) mostra uma página por vez, com espaço entre elas.
- **Vídeo:** `carrossel_llm_wiki/video.mp4` (1080x1080, 47 s, com a trilha lo-fi), animado: documentos soltos (e-mail, anotação, ata, relatório, foto, planilha) → cada um passa pela aprovação e vira uma página ligada às outras → a rede cresce → uma pergunta no chat → a IA percorre as páginas ligadas → resposta com a fonte → fechamento. Para refazer: `ferramentas/venv-video/Scripts/python.exe posts/video_llm_wiki.py`. Use o carrossel **ou** o vídeo no post, não os dois.
- **O exemplo do vídeo é fictício** (a bomba que parou, o selo mecânico): é uma encenação do método, não a gravação de uma base real. Se perguntarem, diga isso.
- **Coerência com o texto:** "o material novo espera a minha aprovação" (a entrada com o visto), "ligado ao que já existia" (as ligações da rede), "toda afirmação aponta para a fonte" (as etiquetas de fonte na resposta). Sem números na tela.
- Quadros: capa → o problema → a ideia → como funciona → adaptações (gente aprova) → adaptações (acompanha o trabalho) → onde se aplica → fechamento.

Onde está o conhecimento da sua empresa: num lugar que qualquer pessoa consulta, ou na cabeça de quem está há mais tempo na casa?

Procedimento em uma pasta, histórico em e-mail, decisão em ata que ninguém relê, lição aprendida que se perde quando a obra termina. Quando alguém sai de férias ou troca de empresa, parte da resposta vai junto.

No último post, defendi que nem tudo precisa de IA. Hoje é o outro lado: um trabalho em que ela é, de fato, o melhor caminho. 🧠

A ideia é do pesquisador Andrej Karpathy. Em vez de perguntar a uma IA que relê todos os documentos do zero a cada pergunta, a IA mantém uma base de conhecimento organizada, uma espécie de wiki. Cada documento novo é lido, resumido e ligado ao que já existia. O conhecimento se acumula.

A parte chata, que faz toda wiki de empresa morrer (atualizar, cruzar referências, manter coerência), fica com a IA. Com as pessoas fica o que importa: escolher as fontes e fazer boas perguntas.

Uso esse método no meu dia a dia, com algumas adaptações minhas:
✅ nada entra sem passar por mim: o material novo espera a minha aprovação;
✅ toda afirmação aponta para a fonte; se não está no documento, a IA não escreve;
✅ o original nunca é alterado;
✅ um espaço para o que está vivo: foco do momento e pendências;
✅ o que se repete vira regra, e a regra passa a valer sempre;
✅ cada projeto tem a sua base, e o que serve para todos sobe para a base central;
✅ de tempos em tempos, uma auditoria aponta contradições e informação vencida.

Onde isso se aplica:

🏭 Indústria e PCM: histórico de cada equipamento, o que já falhou e como foi resolvido, procedimentos e lições de cada parada.
📅 Planejamento: premissas, restrições e o porquê de cada mudança de plano.
🏗️ Construção e projetos, pequenos ou grandes: do diário de obra ao contrato, das atas às pendências com o cliente.
🛒 Comercial: histórico de clientes, propostas, objeções e o que fechou negócio.
🗂️ Administrativo: políticas, processos e respostas para as dúvidas que voltam sempre.
⚖️ Direito: contratos, cláusulas, prazos e o histórico de cada caso.
🩺 Saúde: protocolos e material de estudo sempre com a fonte à mão, com o cuidado que dados sensíveis exigem.

A IA não substitui quem conhece o assunto. Ela faz o conhecimento de quem conhece continuar disponível.

As aplicações são inúmeras. E, como gosto de dizer: a sua imaginação é o limite. 🚀

E na sua empresa: qual conhecimento hoje depende de uma única pessoa? Me conta nos comentários 👇

#GestaoDoConhecimento #InteligenciaArtificial #PCM #Planejamento #Industria40 #Inovacao

---

# Legenda curta: Stories / Status / Reels

O conhecimento da sua empresa está num lugar que todos consultam, ou na cabeça de alguém? 🧠
Uma base viva, mantida pela IA e aprovada por gente: cada documento novo entra, é resumido e ligado ao que já existia.
A sua imaginação é o limite. 🚀

#GestaoDoConhecimento #IA #PCM

---

# O que sustenta cada frase (para não prometer o que não existe)
- **A ideia de Karpathy:** fontes originais imutáveis, uma wiki mantida pela IA e um documento de regras; três operações (ingerir, consultar, auditar), mais um índice e um registro cronológico. A comparação com "reler tudo a cada pergunta" é a crítica dele ao modo tradicional.
- **"Uso no meu dia a dia":** é o vault pessoal do Lucas. O post não cita o conteúdo dele.
- **Cada adaptação existe no vault, nas regras escritas:**
  - aprovação humana: o material fica numa caixa de entrada e só vira fonte depois de aprovado;
  - fidelidade à fonte: regra suprema do schema;
  - original imutável: já é da proposta original, mantido;
  - o que está vivo: pasta de estado (foco, pendências, ideias ativas);
  - regras duráveis: só entram com evidência de padrão repetido;
  - bases por projeto: cada projeto com a sua wiki, e o que transcende o projeto sobe para a central;
  - auditoria: contradição, página vencida, duplicada, órfã e lacuna.
- **Setores:** indústria, PCM, planejamento, construção e projetos têm uso real no vault (equipamentos, manutenções, diários, contratos). Comercial, administrativo, direito e saúde são **aplicações possíveis**, não casos testados: o texto diz "onde isso se aplica", sem afirmar resultado.
- **Saúde e direito:** a ressalva de dados sensíveis está no texto de propósito. Se alguém perguntar, a resposta honesta é que dado de paciente ou de cliente exige ambiente e contrato adequados.
- Sem números e sem nomes de ferramenta (regra dos posts). O nome do Karpathy fica como crédito da ideia.
