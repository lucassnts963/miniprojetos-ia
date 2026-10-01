# 03 · Pessoa em área de risco (visão computacional)

Um detector de pessoas pronto (pré-treinado, nada é treinado aqui) mais uma regra de geometria: avisar quando alguém entra numa área de risco desenhada no chão da imagem, como o corredor de uma empilhadeira (NR-11) ou a zona de uma máquina (NR-12). O mesmo código, com outra regra, conta pessoas por área.

**Estado:** detector testado nos vídeos, regra da área e painel na bancada prontos. Faltam os vídeos (LinkedIn e YouTube) e uma medição com gabarito.

## Como rodar
```bash
python -m venv venv
venv\Scripts\pip install torch torchvision opencv-python-headless
venv\Scripts\python baixar_videos.py       # 3 vídeos de teste (ficam fora do git)
venv\Scripts\python testar_detectores.py   # quadros anotados em testes/
```
Nesta máquina, o `venv` reaproveita o PyTorch com GPU de `C:\dev\venv` (arquivo `venv_geral.pth`) e instala só `torchvision==0.26.0` (com `--no-deps`) e o OpenCV.

## Testar ao vivo
```bash
python ../bancada/servidor.py   # http://127.0.0.1:8765, projeto 03
```
Escolha o vídeo e o modelo, desenhe a área de risco clicando na imagem (ou use a de exemplo) e veja as pessoas em verde (fora) ou vermelho (dentro). "Analisar o vídeo" percorre o vídeo inteiro e mostra a linha do tempo e a lista de alertas; o botão ▶ reproduz os quadros analisados.

- **A regra:** vale o ponto dos pés (o meio da base da caixa). Se ele cai dentro do polígono, a pessoa está na área. É geometria, sem IA.
- **Contra falso alarme:** o alerta só dispara depois de alguns quadros seguidos com gente na área.
- **Câmera fixa:** a área é desenhada na imagem, então só vale para câmera parada. Os vídeos de banco de imagens têm movimento de câmera: neles a área sai do lugar ao longo do vídeo, o que numa câmera de segurança real não acontece.

## Primeiro teste: o que os detectores prontos acertam e erram
Três modelos do torchvision pré-treinados no COCO, confiança mínima de 0,5, 12 quadros espalhados por vídeo, GPU MX570.

| Vídeo | `rapido` (SSDLite) | `medio` (Faster R-CNN MobileNet) | `preciso` (Faster R-CNN ResNet-50) |
|---|---|---|---|
| Perto, 3 pessoas de frente | 3 em quase todos os quadros | 3 (às vezes 4) | 3 (às vezes 4) |
| Plano aberto, pessoas longe | **0 na maioria dos quadros** | acha as pessoas (1 a 6 caixas) | acha as pessoas (0 a 5 caixas) |
| Vista de cima, com empilhadeira | 0 a 2 | 0 a 6 | 1 a 6 |
| Velocidade | 3 a 5 quadros/s | 5 a 8 quadros/s | 2 a 3 quadros/s |

O que se vê nos quadros anotados (`testes/`):
- **Perto e de frente, qualquer modelo resolve.**
- **Pessoas longe da câmera:** o modelo leve não enxerga ninguém. O médio e o preciso acham, com confiança alta (a pessoa isolada sai com 1,00).
- **Grupo de pessoas juntas:** o médio solta caixas repetidas sobre o mesmo grupo. A contagem oscila de um quadro para outro mesmo com a cena parada.
- **Vista de cima:** os dois pedestres são achados; **o operador sentado na empilhadeira, visto de cima, não é detectado por nenhum dos três.**
- **Velocidade:** nenhum chega a tempo real nesta placa. Para alerta de segurança, 5 quadros por segundo já servem (uma pessoa andando leva segundos para cruzar uma área).

Conclusão para seguir: usar o `medio` como padrão. Para a regra da área, tratar a oscilação entre quadros (exigir a pessoa na área por alguns quadros seguidos antes de alertar) e deixar claro que câmera de teto vendo as pessoas de cima é um ponto fraco de modelos treinados com fotos comuns.

Os números de quantas pessoas existem de verdade em cada quadro ainda não foram anotados à mão: a tabela mostra o que os modelos disseram, e a conferência foi visual, num quadro por vídeo.

## Arquivos
| Arquivo | O que faz |
|---|---|
| `detector.py` | carrega o modelo pronto e devolve as caixas das pessoas num quadro |
| `baixar_videos.py` | baixa os vídeos de teste (Pexels e Mixkit, licença livre) |
| `testar_detectores.py` | o teste acima |
| `demo.py` + `painel/` | painel da bancada: quadro com detecções, área de risco, análise do vídeo e alertas |
