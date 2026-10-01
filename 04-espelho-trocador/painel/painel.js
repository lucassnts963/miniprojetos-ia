// Painel da bancada: espelho do trocador (contar tubos; aberto, obstruído, tamponado; corrigir e rotular).

const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const fmt = v => Number(v).toLocaleString("pt-BR");
const COR = { aberto: "#58D68D", obstruido: "#E5484D", tamponado: "#3CAAFF" };
const NOME = { aberto: "aberto", obstruido: "obstruído", tamponado: "tamponado" };
const ORDEM = ["aberto", "obstruido", "tamponado"];

const HTML = `
<div class="et">
  <section class="c ctrl">
    <h1>Espelho do trocador</h1>
    <p class="dica">Conta os tubos e separa aberto, obstruído e tamponado. Visão clássica, sem treino: serve para medir e para rotular.</p>

    <label class="rot" for="et-foto">Foto</label>
    <select id="et-foto"></select>
    <label class="btn sec envio">Enviar outra foto<input type="file" id="et-arquivo" accept="image/*" hidden></label>

    <span class="rot">Tamanho do tubo na foto (raio, em pixels)</span>
    <div class="linha"><span class="dica">mín</span><input type="range" id="et-rmin" min="3" max="60" value="8"><span class="ms" id="et-rmin-v"></span></div>
    <div class="linha"><span class="dica">máx</span><input type="range" id="et-rmax" min="5" max="90" value="16"><span class="ms" id="et-rmax-v"></span></div>

    <span class="rot">Detecção</span>
    <div class="linha"><span class="dica" title="menor = acha mais círculos, e mais falsos">exigência</span><input type="range" id="et-sens" min="8" max="30" value="15"><span class="ms" id="et-sens-v"></span></div>
    <div class="linha"><span class="dica" title="quantos vizinhos à distância de um passo um círculo precisa ter para contar como tubo">vizinhos</span><input type="range" id="et-viz" min="0" max="5" value="3"><span class="ms" id="et-viz-v"></span></div>

    <span class="rot">Classificação pelo miolo</span>
    <div class="linha"><span class="dica" title="percentil de brilho: abaixo disso é aberto">aberto até</span><input type="range" id="et-esc" min="10" max="90" value="55"><span class="ms" id="et-esc-v"></span></div>
    <div class="linha"><span class="dica" title="percentil de brilho: acima disso (e pouco saturado) é tamponado">tampão de</span><input type="range" id="et-cla" min="60" max="99" value="93"><span class="ms" id="et-cla-v"></span></div>

    <button class="btn" id="et-detectar">Detectar tubos</button>
    <div class="status" id="et-status"></div>
  </section>

  <section class="c tela">
    <div class="c-topo">
      <div class="seg" id="et-modo"><button data-v="ver" class="on">Ver</button><button data-v="corrigir">Corrigir</button></div>
      <span class="dica" id="et-dica-modo"></span>
      <div class="linha zoom">
        <label class="check"><input type="checkbox" id="et-mostrar" checked> círculos</label>
        <div class="seg" id="et-zoom"><button data-v="1" class="on">1×</button><button data-v="2">2×</button><button data-v="3">3×</button></div>
      </div>
    </div>
    <div class="palco" id="et-palco"><canvas id="et-canvas"></canvas></div>
  </section>

  <section class="c stats" id="et-stats"></section>
</div>`;

export async function montar(raiz, api) {
  raiz.innerHTML = `<link rel="stylesheet" href="${new URL("painel.css", import.meta.url)}">` + HTML;
  const $ = s => raiz.querySelector(s);
  let info = await api.chamar("info");
  const st = { foto: api.ler("foto", null), img: null, dim: null, tubos: [], origem: null, sujo: false, modo: "ver", zoom: 1, analise: null };
  const canvas = $("#et-canvas"), ctx = canvas.getContext("2d"), palco = $("#et-palco");
  const SLIDERS = { rmin: "et-rmin", rmax: "et-rmax", sens: "et-sens", viz: "et-viz", esc: "et-esc", cla: "et-cla" };

  function listarFotos() {
    $("#et-foto").innerHTML = info.fotos.map(f => `<option value="${esc(f.nome)}">${esc(f.nome)}${f.tem_rotulos ? " ✓" : ""}</option>`).join("");
    if (!info.fotos.some(f => f.nome === st.foto)) st.foto = info.fotos[0]?.nome ?? null;
    if (st.foto) $("#et-foto").value = st.foto;
  }

  function parametros() {
    const p = api.ler(`params:${st.foto}`, null);
    if (p) for (const k in SLIDERS) if (p[k] != null) $("#" + SLIDERS[k]).value = p[k];
    rotulosSliders();
  }
  function lerParametros() {
    const p = {};
    for (const k in SLIDERS) p[k] = Number($("#" + SLIDERS[k]).value);
    return p;
  }
  function rotulosSliders() {
    const p = lerParametros();
    $("#et-rmin-v").textContent = `${p.rmin} px`; $("#et-rmax-v").textContent = `${p.rmax} px`;
    $("#et-sens-v").textContent = p.sens; $("#et-viz-v").textContent = p.viz;
    $("#et-esc-v").textContent = `${p.esc}%`; $("#et-cla-v").textContent = `${p.cla}%`;
  }

  // ---------- desenho ----------
  function desenhar() {
    if (!st.img) return;
    const base = palco.clientWidth - 2;
    const w = Math.min(base, st.img.width) * st.zoom, h = w * st.img.height / st.img.width;
    const dpr = window.devicePixelRatio || 1;
    canvas.style.width = `${w}px`; canvas.style.height = `${h}px`;
    canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.drawImage(st.img, 0, 0, w, h);
    if (!$("#et-mostrar").checked) return;
    const e = w / st.dim.largura;
    ctx.lineWidth = Math.max(1.5, 1.5 * st.zoom);
    for (const t of st.tubos) {
      ctx.strokeStyle = COR[t.classe];
      ctx.beginPath(); ctx.arc(t.x * e, t.y * e, t.r * e, 0, 7); ctx.stroke();
    }
  }

  function mostrarStats() {
    const n = st.tubos.length;
    const cont = Object.fromEntries(ORDEM.map(c => [c, st.tubos.filter(t => t.classe === c).length]));
    const origem = st.origem === "rotulos" ? "rótulos salvos (conferidos por você)" : st.origem === "deteccao" ? "detecção automática" : "";
    let h = `<span class="rot">Contagem${origem ? " · " + origem : ""}</span>
      <div class="kpis">
        <div class="kpi grande"><b>${fmt(n)}</b><span>tubos</span></div>
        ${ORDEM.map(c => `<div class="kpi"><b style="color:${COR[c]}">${fmt(cont[c])}</b><span>${NOME[c]}${n ? ` · ${Math.round(cont[c] / n * 100)}%` : ""}</span></div>`).join("")}
      </div>`;
    if (st.analise && st.origem === "deteccao") {
      h += `<p class="dica">${fmt(st.analise.brutos)} círculos brutos, ${fmt(st.analise.tubos.length)} depois do filtro da grade (passo de ${st.analise.passo ?? "?"} px), em ${String(st.analise.segundos).replace(".", ",")} s.</p>`;
    }
    h += `<div class="linha acoes">
        <button class="btn" id="et-salvar" ${n ? "" : "disabled"}>Salvar rótulos${st.sujo ? " *" : ""}</button>
        <button class="btn sec" id="et-apagar">Apagar salvos</button>
      </div>
      <p class="dica limite">O automático é um ponto de partida, não o resultado: na foto de frente ele perde tubos nas áreas escuras e erra "obstruído" com frequência; em foto tirada em ângulo, não funciona. Use Corrigir para acertar e salvar o gabarito.</p>`;
    $("#et-stats").innerHTML = h;
    $("#et-salvar").onclick = salvar;
    $("#et-apagar").onclick = apagar;
  }

  function modo() {
    for (const b of raiz.querySelectorAll("#et-modo button")) b.classList.toggle("on", b.dataset.v === st.modo);
    for (const b of raiz.querySelectorAll("#et-zoom button")) b.classList.toggle("on", Number(b.dataset.v) === st.zoom);
    $("#et-dica-modo").textContent = st.modo === "corrigir"
      ? "clique num tubo: troca a classe · clique no vazio: cria um tubo · botão direito: remove"
      : "";
    canvas.style.cursor = st.modo === "corrigir" ? "crosshair" : "default";
  }

  function status(html, tipo = "") {
    const el = $("#et-status");
    el.className = `status ${tipo}`;
    el.innerHTML = html;
  }
  const erro = e => status(esc(e.message.split("\n").filter(Boolean).pop()), "erro");

  // ---------- ações ----------
  async function abrir() {
    if (!st.foto) {
      $(".tela .palco").innerHTML = `<p class="dica" style="padding:20px">Nenhuma foto em ${info.pastas.map(esc).join(" nem em ")}. Use "Enviar outra foto".</p>`;
      return;
    }
    status(`<span class="spin"></span>Abrindo a foto…`);
    try {
      const r = await api.chamar("imagem", { foto: st.foto });
      const img = new Image();
      await new Promise((ok, falha) => { img.onload = ok; img.onerror = falha; img.src = `data:image/jpeg;base64,${r.jpeg}`; });
      st.img = img; st.dim = { largura: r.largura, altura: r.altura };
      st.analise = null; st.sujo = false;
      parametros();
      if (r.rotulos) { st.tubos = r.rotulos; st.origem = "rotulos"; status(""); desenhar(); mostrarStats(); }
      else { st.tubos = []; st.origem = null; desenhar(); mostrarStats(); await detectar(); }
    } catch (e) { erro(e); }
  }

  async function detectar() {
    const p = lerParametros();
    if (p.rmax <= p.rmin) return status("O raio máximo precisa ser maior que o mínimo.", "erro");
    api.gravar(`params:${st.foto}`, p);
    $("#et-detectar").disabled = true;
    status(`<span class="spin"></span>Detectando…`);
    try {
      const r = await api.chamar("analisar", {
        foto: st.foto, r_min: p.rmin, r_max: p.rmax, sensibilidade: p.sens, vizinhos: p.viz, p_escuro: p.esc, p_claro: p.cla,
      });
      st.analise = r; st.tubos = r.tubos; st.origem = "deteccao"; st.sujo = false;
      status(r.tubos.length ? "" : "Nenhum tubo encontrado: ajuste o tamanho do tubo (raio mínimo e máximo).", r.tubos.length ? "" : "erro");
      desenhar(); mostrarStats();
    } catch (e) { erro(e); } finally { $("#et-detectar").disabled = false; }
  }

  async function salvar() {
    try {
      const r = await api.chamar("salvar_rotulos", { foto: st.foto, tubos: st.tubos });
      st.sujo = false; st.origem = "rotulos";
      info = await api.chamar("info"); listarFotos();
      status(`Salvo: ${fmt(r.salvos)} tubos como gabarito desta foto.`, "ok");
      mostrarStats();
    } catch (e) { erro(e); }
  }

  async function apagar() {
    try {
      await api.chamar("apagar_rotulos", { foto: st.foto });
      info = await api.chamar("info"); listarFotos();
      status("Rótulos salvos desta foto apagados.");
      if (st.origem === "rotulos") st.origem = "deteccao";
      mostrarStats();
    } catch (e) { erro(e); }
  }

  // ---------- eventos ----------
  for (const k in SLIDERS) $("#" + SLIDERS[k]).oninput = rotulosSliders;
  $("#et-detectar").onclick = detectar;
  $("#et-foto").onchange = () => { st.foto = $("#et-foto").value; api.gravar("foto", st.foto); abrir(); };
  $("#et-mostrar").onchange = desenhar;
  $("#et-modo").onclick = ev => { const m = ev.target.closest("button")?.dataset.v; if (m) { st.modo = m; modo(); } };
  $("#et-zoom").onclick = ev => { const z = ev.target.closest("button")?.dataset.v; if (z) { st.zoom = Number(z); modo(); desenhar(); } };

  function tuboEm(ev) {
    const r = canvas.getBoundingClientRect();
    const e = st.dim.largura / r.width;
    const x = (ev.clientX - r.left) * e, y = (ev.clientY - r.top) * e;
    let melhor = -1, dmin = Infinity;
    st.tubos.forEach((t, i) => {
      const d = Math.hypot(t.x - x, t.y - y);
      if (d < t.r * 1.15 && d < dmin) { dmin = d; melhor = i; }
    });
    return { x, y, i: melhor };
  }
  canvas.addEventListener("click", ev => {
    if (st.modo !== "corrigir" || !st.dim) return;
    const { x, y, i } = tuboEm(ev);
    if (i >= 0) {
      st.tubos[i].classe = ORDEM[(ORDEM.indexOf(st.tubos[i].classe) + 1) % ORDEM.length];
    } else {
      const raios = st.tubos.map(t => t.r).sort((a, b) => a - b);
      const r = raios.length ? raios[raios.length >> 1] : (Number($("#et-rmin").value) + Number($("#et-rmax").value)) / 2;
      st.tubos.push({ x: +x.toFixed(1), y: +y.toFixed(1), r, classe: "aberto" });
    }
    st.sujo = true; desenhar(); mostrarStats();
  });
  canvas.addEventListener("contextmenu", ev => {
    if (st.modo !== "corrigir" || !st.dim) return;
    ev.preventDefault();
    const { i } = tuboEm(ev);
    if (i >= 0) { st.tubos.splice(i, 1); st.sujo = true; desenhar(); mostrarStats(); }
  });

  $("#et-arquivo").onchange = async ev => {
    const arq = ev.target.files[0];
    if (!arq) return;
    status(`<span class="spin"></span>Enviando ${esc(arq.name)}…`);
    try {
      const b64 = await new Promise((ok, falha) => {
        const leitor = new FileReader();
        leitor.onload = () => ok(String(leitor.result).split(",")[1]);
        leitor.onerror = falha;
        leitor.readAsDataURL(arq);
      });
      const r = await api.chamar("enviar", { nome: arq.name, base64: b64 });
      info = await api.chamar("info");
      st.foto = r.nome; api.gravar("foto", st.foto);
      listarFotos();
      await abrir();
    } catch (e) { erro(e); }
    ev.target.value = "";
  };

  const obs = new ResizeObserver(() => desenhar());
  obs.observe(palco);
  listarFotos();
  modo();
  mostrarStats();
  await abrir();
  return () => obs.disconnect();
}
