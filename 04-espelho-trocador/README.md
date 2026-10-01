# 04 · Espelho do trocador de calor: contar tubos e achar obstruídos e tamponados (exploração)

Ideia: a partir de uma foto do espelho de um trocador casco e tubo, contar os tubos e separar três situações: **aberto**, **obstruído** e **tamponado**.

**Estado:** exploração com 2 fotos e visão clássica (OpenCV, sem treinar nada). Serve para saber até onde o caminho simples vai e o que pedir das próximas fotos. As fotos e as saídas ficam fora do git.

```bash
venv\Scripts\python explorar.py "caminho/da/foto.jpeg" raio_min raio_max   # raios em pixels
# foto de cima (1200x1600):  8 16      foto em ângulo (1600x1204): 10 22
```

## Testar ao vivo
```bash
python ../bancada/servidor.py   # http://127.0.0.1:8765, projeto 04
```
O painel lê as fotos de `inbox/` e de `04-espelho-trocador/fotos/` (dá para enviar outras pelo próprio painel).

- **Detectar:** ajuste o tamanho do tubo na foto (raio mínimo e máximo, em pixels), a exigência da detecção, o filtro de vizinhos e os limites de brilho da classificação. Os ajustes ficam guardados por foto.
- **Corrigir:** clique num tubo para trocar a classe (aberto → obstruído → tamponado), clique no vazio para criar um tubo, botão direito para remover. Zoom de 1× a 3×.
- **Salvar rótulos:** grava o que você conferiu em `rotulos/` (fora do git). É o gabarito que falta para medir o acerto e, depois, treinar um classificador de recortes.

O projeto usa um `venv/` próprio com OpenCV; a bancada escolhe esse Python sozinha.

## O que foi testado
1. **Achar os tubos:** círculos de Hough, com a iluminação igualada (CLAHE).
2. **Limpar pelo padrão da grade:** tubo de verdade tem vários vizinhos à distância de um passo; furo de flange e ruído não têm.
3. **Classificar o miolo de cada círculo** por brilho e saturação: escuro = aberto, claro e pouco saturado = tamponado, o resto = obstruído.

## Resultado
| | Foto de cima | Foto em ângulo |
|---|---|---|
| Círculos depois do filtro | 1.188 | 805 (de 1.606 brutos) |
| Contagem | boa nas áreas limpas; **perde tubos** na região de tubos salientes e marrons, e duplica alguns | **não funciona**: um quadrante inteiro ficou sem detecção e os outros têm círculos amontoados |
| Tamponados | a maioria dos discos claros é marcada certo | sem leitura confiável |
| Obstruídos | **não confiável**: muitos "obstruídos" são tubos abertos com o círculo descentrado | sem leitura confiável |

A conferência foi visual, em recortes ampliados (`saida/`). Não existe gabarito ainda: não se sabe o número real de tubos nem quais estão tamponados ou obstruídos, então não há taxa de acerto em número.

## Conclusões
- **Contar os tubos é viável.** Numa foto de cima, o método simples já acha a grande maioria. Para chegar perto de 100% falta usar o que se sabe do equipamento: o arranjo é uma grade regular (passo triangular), então dá para completar os tubos que faltam e tirar os duplicados pela grade, em vez de confiar só nos círculos.
- **Tamponado é o padrão mais fácil:** disco de metal claro e liso, diferente de tudo em volta.
- **Obstruído é o difícil, e hoje não dá para afirmar nada.** Nas fotos atuais, cada tubo tem uns 20 pixels de diâmetro e a compressão do WhatsApp apaga o miolo. Além disso, falta a definição: obstruído total, parcial, com depósito na boca? Precisa de exemplos apontados por quem conhece o equipamento.
- **Foto em ângulo não serve para o método simples.** Ou a foto é tirada de frente, ou é preciso corrigir a perspectiva antes (o contorno do espelho é um círculo conhecido: dá para "desentortar" a imagem).

## Caminho proposto
1. **Localizar** os tubos: círculos + ajuste da grade (clássico). Se não bastar, um detector treinado.
2. **Recortar** cada tubo e **classificar o recorte** em aberto / obstruído / tamponado com uma rede pequena. Cada foto rende cerca de mil recortes, então poucas fotos já dão um conjunto de treino razoável.
3. **Rotular:** já dá para fazer no painel (modo Corrigir). O método atual deixa os tubos pré-marcados para você conferir.

## O que pedir das próximas fotos
- **De frente**, com a câmera perpendicular ao espelho e o espelho inteiro no quadro.
- **Arquivo original**, sem passar pelo WhatsApp (que reduz e comprime). Quanto mais pixels por tubo, melhor: o ideal é pelo menos 40 a 50 pixels de diâmetro por tubo.
- **Luz uniforme**, sem sombra dura atravessando o espelho e sem reflexo forte.
- **Antes e depois da limpeza**, do mesmo equipamento, se der.
- **O gabarito:** o número de tubos (folha de dados ou desenho do feixe) e o mapa de tubos tamponados (relatório de inspeção). Sem isso não dá para medir acerto.
- **Exemplos do que é "obstruído"** apontados numa foto: três ou quatro tubos de cada tipo já ajudam a definir a classe.
