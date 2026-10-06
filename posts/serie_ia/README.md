# Série "IA sem mistério" (LinkedIn, Reels, Shorts e TikTok)

Como funciona a IA que escreve, em oito partes, para quem nunca viu o assunto. Termos técnicos sempre com uma metáfora.

| Pasta | Parte | Termo e metáfora |
|---|---|---|
| `parte1/` | Como a IA escreve um texto | previsão da próxima palavra: o teclado do celular |
| `parte2/` | Por que a IA erra contas | token: peça de montar; execução de código: calculadora de bolso |
| `parte3/` | Por que a IA esquece o que você disse | janela de contexto: mesa de trabalho; memória: caderno |
| `parte4/` | Como a IA decide o que importa | atenção: holofote |
| `parte5/` | Por que a IA inventa | alucinação: o aluno que chuta na prova |
| `parte6/` | Mesma pergunta, respostas diferentes | temperatura: o botão da ousadia |
| `parte7/` | Até quando a IA sabe das coisas | data de corte: o treino é uma fotografia |
| `parte8/` | Precisa sempre da IA mais potente? | modelo: a frota |

## O que tem em cada pasta
| Arquivo | O que é |
|---|---|
| `post.md` | texto do post do LinkedIn, legenda curta e a lista do que sustenta cada frase, com as fontes |
| `01.png` a `08.png` | o carrossel (1080x1350), para postar na ordem |
| `panorama.png`, `carrossel.pdf` | o painel inteiro e a versão em PDF |
| `carrossel.py` | o gerador das imagens |
| `short.mp4` | o short vertical narrado (partes 1 a 4) |
| `narracao.mp3`, `narracao.json` | a narração e a transcrição com tempos (partes 1 a 4; ficam só locais, fora do git) |

## Na raiz da série
| Arquivo | O que é |
|---|---|
| `artigo.md` | artigo com as fontes das partes 1 a 4 |
| `shorts_narracao.md` | roteiro de narração dos shorts (ElevenLabs v3) |
| `shorts_publicacao.md` | títulos, descrições e tags para YouTube Shorts, Reels e TikTok |
| `shorts.py` | gerador dos shorts (segue a narração quando ela existe) |
| `transcrever.py` | transcreve as narrações com o tempo de cada palavra |
| `base.py` | funções de desenho dos carrosséis |

## Como refazer
```bash
C:/dev/venv/Scripts/python.exe posts/serie_ia/parte5/carrossel.py                   # um carrossel
C:/dev/venv/Scripts/python.exe posts/serie_ia/transcrever.py                         # depois de trocar uma narração
ferramentas/venv-video/Scripts/python.exe posts/serie_ia/shorts.py 3                 # um short (ou "todos")
```
A parte 1 já foi publicada: não refaça as imagens dela sem necessidade.
