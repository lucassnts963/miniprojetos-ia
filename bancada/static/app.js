// Casca da bancada: lista os projetos e monta o painel de cada um.
// Um painel é um módulo ES em <projeto>/painel/painel.js que exporta montar(raiz, api).

const lista = document.getElementById("projetos");
const palco = document.getElementById("palco");
let desmontar = null;

function api(id) {
  return {
    id,
    async chamar(acao, payload = {}) {
      const r = await fetch(`/api/${id}/${acao}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const j = await r.json().catch(() => ({ erro: r.statusText }));
      if (!r.ok || j.erro) throw new Error(j.erro || r.statusText);
      return Object.assign(j.resultado ?? {}, j.resultado && typeof j.resultado === "object" ? { _ms: j.ms } : {});
    },
    // guarda preferências e histórico do painel no navegador (pode falhar em janela privada)
    ler(chave, padrao) {
      try { return JSON.parse(localStorage.getItem(`bancada:${id}:${chave}`)) ?? padrao; } catch { return padrao; }
    },
    gravar(chave, valor) {
      try { localStorage.setItem(`bancada:${id}:${chave}`, JSON.stringify(valor)); } catch { /* sem armazenamento */ }
    },
  };
}

function esc(s) {
  return String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
}

function erro(msg) {
  palco.innerHTML = `<div class="erro-caixa">${esc(msg)}</div>`;
}

async function painelGenerico(raiz, a) {
  const acoes = await a.chamar("__acoes").catch(() => []);
  raiz.innerHTML = `
    <div class="generico">
      <section class="c">
        <div class="c-topo"><span class="rot">Painel genérico</span><span class="dica">crie painel/painel.js para uma interface própria</span></div>
        <div class="linha" style="margin-bottom:10px">
          <select id="g-acao">${(Array.isArray(acoes) ? acoes : Object.values(acoes)).map(x => `<option>${esc(x)}</option>`).join("")}</select>
          <button class="btn" id="g-rodar">Executar</button>
          <span class="dica" id="g-ms"></span>
        </div>
        <textarea id="g-payload" spellcheck="false">{}</textarea>
      </section>
      <section class="c"><div class="rot" style="margin-bottom:10px">Resposta</div><pre id="g-saida">—</pre></section>
    </div>`;
  raiz.querySelector("#g-rodar").onclick = async () => {
    const saida = raiz.querySelector("#g-saida");
    try {
      const r = await a.chamar(raiz.querySelector("#g-acao").value, JSON.parse(raiz.querySelector("#g-payload").value || "{}"));
      raiz.querySelector("#g-ms").textContent = r._ms != null ? `${r._ms} ms` : "";
      saida.textContent = JSON.stringify(r, null, 2);
    } catch (e) {
      saida.textContent = e.message;
    }
  };
}

async function abrir(p) {
  for (const a of lista.querySelectorAll("a")) a.classList.toggle("ativo", a.dataset.id === p.id);
  if (desmontar) { try { desmontar(); } catch { /* ignora */ } desmontar = null; }
  palco.innerHTML = `<div class="vazio">Carregando ${esc(p.nome)}…</div>`;
  document.title = `${p.nome} · bancada`;
  const raiz = document.createElement("div");
  try {
    if (p.painel) {
      const mod = await import(`/p/${p.id}/painel.js?v=${Date.now()}`);
      palco.replaceChildren(raiz);
      desmontar = (await mod.montar(raiz, api(p.id))) || null;
    } else {
      palco.replaceChildren(raiz);
      await painelGenerico(raiz, api(p.id));
    }
  } catch (e) {
    erro(e.message);
  }
}

// Modo vídeo (?video=1): esconde a navegação e mostra a moldura elucas.dev para gravação.
// O roteiro de gravação controla título e legenda por window.bancada.
const MODO_VIDEO = new URLSearchParams(location.search).has("video");
if (MODO_VIDEO) document.body.classList.add("modo-video");
window.bancada = {
  video: MODO_VIDEO,
  titulo(eyebrow, titulo, capitulo = "", selo = "") {
    document.getElementById("vid-eyebrow").textContent = eyebrow;
    document.getElementById("vid-h").textContent = titulo;
    document.getElementById("vid-cap").textContent = capitulo;
    const s = document.getElementById("vid-selo");
    s.textContent = selo;
    s.hidden = !selo;
  },
  legenda(l1 = "", l2 = "") {
    const caixa = document.getElementById("vid-legenda");
    caixa.classList.remove("on");
    setTimeout(() => {
      document.getElementById("vid-l1").textContent = l1;
      document.getElementById("vid-l2").textContent = l2;
      if (l1 || l2) caixa.classList.add("on");
    }, caixa.textContent.trim() ? 350 : 0);
  },
};

async function iniciar() {
  let projetos;
  try {
    projetos = await (await fetch("/api/projetos")).json();
  } catch (e) {
    return erro("Não consegui falar com o servidor da bancada.");
  }
  if (!projetos.length) {
    palco.innerHTML = `<div class="vazio">Nenhum projeto com <code>demo.py</code> ainda.</div>`;
    return;
  }
  lista.innerHTML = projetos.map(p => `
    <li><a href="#${esc(p.id)}" data-id="${esc(p.id)}">
      <span class="num">${esc(p.numero)}</span>
      <span class="nome">${esc(p.nome)}</span>
      <span class="desc">${esc(p.descricao)}</span>
    </a></li>`).join("");
  const escolher = () => abrir(projetos.find(p => p.id === decodeURIComponent(location.hash.slice(1))) || projetos[0]);
  window.addEventListener("hashchange", escolher);
  escolher();
}

iniciar();
