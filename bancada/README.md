# Bancada: teste ao vivo dos miniprojetos

Interface no navegador para testar os modelos de cada miniprojeto. Só usa a biblioteca padrão do Python (o servidor não precisa de nada instalado).

```bash
python bancada/servidor.py                  # abre http://127.0.0.1:8765
python bancada/servidor.py --sem-navegador
```

Toda pasta `NN-nome/` com um `demo.py` aparece sozinha na barra lateral.

## Como funciona
- Cada projeto roda num **processo próprio**, usando a `venv/` da pasta dele se existir. Dependências e nomes de módulo (`modelo.py`, `rede.py`…) de um projeto não atrapalham os outros.
- Se algum `.py` da pasta mudar, o processo reinicia sozinho na próxima chamada. Não precisa reiniciar a bancada.
- Tudo o que o projeto imprimir aparece no terminal da bancada.
- O servidor só escuta em `127.0.0.1`.

## Contrato do `demo.py`
```python
INFO = {"nome": "Rota de entregas", "descricao": "Pontos no mapa → melhor ordem de visita"}

def resolver(payload):          # recebe o JSON enviado pelo painel
    return {"rota": [...]}      # devolve algo que vire JSON (arrays do NumPy são convertidos)

ACOES = {"resolver": resolver}  # nome da ação -> função
```
- `INFO` precisa ser um dicionário literal: a bancada lê esse valor sem importar o projeto.
- Uma exceção dentro da ação aparece como erro no painel. A bancada continua de pé.

## Painel próprio (opcional)
Sem painel, a bancada mostra um **painel genérico**: você escolhe a ação, escreve o JSON e vê a resposta. Bom para começar.

Para uma interface própria, crie `painel/painel.js` (e o que mais precisar em `painel/`):
```js
export async function montar(raiz, api) {
  raiz.innerHTML = `<link rel="stylesheet" href="${new URL("painel.css", import.meta.url)}"> ...`;
  const r = await api.chamar("resolver", { pontos: [...] });   // POST /api/<projeto>/resolver
  api.gravar("chave", valor); api.ler("chave", padrao);        // preferências no navegador
  return () => { /* limpeza ao trocar de projeto (opcional) */ };
}
```
Classes prontas em `static/app.css`: `.c` (card), `.rot` (rótulo), `.c-topo`, `.dica`, `.btn`, `.btn.sec`, `.link`. Os tokens de cor seguem o tema elucas.dev (`--ink`, `--card`, `--red`, `--fg`, `--body`, `--mute`, `--line`, `--glow`).

Exemplo completo: `01-triagem-manutencao/demo.py` + `01-triagem-manutencao/painel/`.

## Modo vídeo
`http://127.0.0.1:8765/?video=1#<projeto>` esconde a navegação e mostra a moldura elucas.dev (marca, selo, título, legenda e rodapé) em 1080x1080. O roteiro controla a moldura por `window.bancada.titulo(eyebrow, titulo, capitulo, selo)` e `window.bancada.legenda(linha1, linha2)`. O painel pode checar `window.bancada.video` para esconder números e o que não cabe (ver `body.modo-video` no `painel.css` da triagem).

Para gravar: `ferramentas/gravacao/gravador.py` (Playwright + Chrome instalado, captura por screencast e monta o MP4 com ffmpeg). Exemplo de roteiro: `01-triagem-manutencao/video/gravar_painel.py`.
