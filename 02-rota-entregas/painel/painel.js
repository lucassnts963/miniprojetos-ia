// Painel da bancada: menor rota pelas cidades.

const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const fmt = (v, d = 0) => Number(v).toLocaleString("pt-BR", { minimumFractionDigits: d, maximumFractionDigits: d });
const RED = "#E5484D", RED_SOFT = "#F08A8D", FG = "#ECECEF", MUTE = "#87878F";

const HTML = `
<div class="rt">
  <section class="c ctrl">
    <h1>Menor rota pelas cidades</h1>
    <p class="dica">Escolha de onde sair e quais cidades visitar. Distância em linha reta.</p>

    <label class="rot" for="rt-inicio">Partida</label>
    <input id="rt-inicio" list="rt-lista-cidades" autocomplete="off" spellcheck="false" placeholder="ex.: Belém/PA">
    <datalist id="rt-lista-cidades"></datalist>

    <span class="rot">Cidades</span>
    <div class="seg" id="rt-escopo">
      <button data-v="capitais" class="on">Capitais</button><button data-v="estados">Estados</button><button data-v="brasil">Brasil inteiro</button>
    </div>
    <div class="ufs" id="rt-ufs" hidden></div>

    <span class="rot">Distância</span>
    <div class="seg" id="rt-dist">
      <button data-v="reta" class="on">Linha reta</button><button data-v="estrada">Estrada</button><button data-v="comparar">Comparar</button>
    </div>
    <p class="dica" id="rt-dist-dica"></p>

    <span class="rot">Método</span>
    <div class="seg" id="rt-metodo">
      <button data-v="heuristica" class="on">Heurística</button><button data-v="exato">Exato</button><button data-v="genetico">Genético</button>
    </div>
    <p class="dica" id="rt-metodo-dica"></p>

    <div class="linha" id="rt-tempo-linha">
      <label class="rot" for="rt-tempo">Refinamento</label>
      <input type="range" id="rt-tempo" min="0" max="30" step="1" value="5"><span class="ms" id="rt-tempo-v">5 s</span>
    </div>
    <label class="check"><input type="checkbox" id="rt-volta"> voltar para a cidade de partida no final</label>

    <button class="btn" id="rt-calcular">Calcular rota</button>
    <div class="status" id="rt-status"></div>
  </section>

  <section class="c mapa">
    <div class="c-topo"><span class="rot" id="rt-mapa-titulo">Mapa</span><span class="dica" id="rt-hover"></span></div>
    <canvas id="rt-canvas"></canvas>
  </section>

  <section class="c stats" id="rt-stats"></section>

  <section class="c lista">
    <div class="c-topo"><span class="rot">Ordem de visita</span><input id="rt-filtro" placeholder="filtrar cidade…" spellcheck="false"></div>
    <ol id="rt-ordem"></ol>
  </section>
</div>`;

const DICAS = {
  heuristica: "Vizinho mais próximo, 2-opt e Or-opt, depois refinamento. Rápido para qualquer tamanho, sem prova de ótimo.",
  exato: "Programação linear inteira: devolve a menor rota com prova. Até LIM cidades aqui.",
  genetico: "O algoritmo genético da cobrinha: seleção, crossover OX e mutação. Até LIM cidades aqui.",
};

export async function montar(raiz, api) {
  raiz.innerHTML = `<link rel="stylesheet" href="${new URL("painel.css", import.meta.url)}">` + HTML;
  const $ = s => raiz.querySelector(s);
  const info = await api.chamar("info");
  const st = {
    escopo: api.ler("escopo", "capitais"), metodo: api.ler("metodo", "heuristica"), dist: api.ler("dist", "reta"),
    estados: api.ler("estados", ["PR"]), cid: null, res: null, anim: 0, hover: -1,
  };
  const canvas = $("#rt-canvas");
  const ctx = canvas.getContext("2d");

  // ---------- controles ----------
  $("#rt-ufs").innerHTML = info.ufs.map(u =>
    `<button data-uf="${u}" title="${info.por_uf[u]} municípios">${u}<em>${info.por_uf[u]}</em></button>`).join("");

  function segs() {
    const fora = st.cid && st.cid.fora ? st.cid.fora.length : 0;
    $("#rt-dist-dica").textContent = {
      reta: "Em linha reta sobre a Terra. Simples, mas subestima a viagem real.",
      estrada: `Pelas rodovias (OSRM + OpenStreetMap, com balsas mapeadas).${fora ? ` ${fora} cidade(s) sem rota ficam de fora.` : ""}`,
      comparar: "Planeja em linha reta e pela estrada, e mede as duas rotas na estrada.",
    }[st.dist];
    for (const [id, v] of [["#rt-escopo", st.escopo], ["#rt-metodo", st.metodo], ["#rt-dist", st.dist]])
      for (const b of raiz.querySelectorAll(`${id} button`)) b.classList.toggle("on", b.dataset.v === v);
    $("#rt-ufs").hidden = st.escopo !== "estados";
    for (const b of raiz.querySelectorAll("#rt-ufs button")) b.classList.toggle("on", st.estados.includes(b.dataset.uf));
    $("#rt-tempo-linha").hidden = st.metodo !== "heuristica";
    const lim = st.metodo === "exato" ? info.limite_exato : info.limite_genetico;
    const n = st.cid ? st.cid.n : 0;
    let dica = DICAS[st.metodo].replace("LIM", lim);
    if (st.metodo !== "heuristica" && n > lim) dica += ` São ${fmt(n)} cidades: use a heurística ou menos estados.`;
    $("#rt-metodo-dica").textContent = dica;
    $("#rt-calcular").disabled = st.metodo !== "heuristica" && n > lim;
  }

  async function carregarCidades() {
    st.res = null;
    const est = st.escopo === "estados" ? st.estados : [];
    if (st.escopo === "estados" && !est.length) {
      st.cid = { nomes: [], lat: [], lon: [], n: 0 };
    } else {
      st.cid = await api.chamar("cidades", { escopo: st.escopo, estados: est, distancia: st.dist });
    }
    $("#rt-lista-cidades").innerHTML = st.cid.nomes.map(n => `<option value="${esc(n)}">`).join("");
    const atual = $("#rt-inicio").value;
    if (!st.cid.nomes.includes(atual)) {
      const pref = ["Belém/PA", "Curitiba/PR", "São Paulo/SP"].find(n => st.cid.nomes.includes(n));
      $("#rt-inicio").value = pref || st.cid.nomes[0] || "";
    }
    $("#rt-mapa-titulo").textContent = `${fmt(st.cid.n)} cidades`;
    segs();
    desenhar();
    mostrarStats();
    mostrarLista();
  }

  $("#rt-escopo").onclick = ev => {
    const v = ev.target.closest("button")?.dataset.v;
    if (!v) return;
    st.escopo = v;
    api.gravar("escopo", v);
    carregarCidades();
  };
  $("#rt-dist").onclick = ev => {
    const v = ev.target.closest("button")?.dataset.v;
    if (!v) return;
    st.dist = v;
    api.gravar("dist", v);
    carregarCidades();
  };
  $("#rt-metodo").onclick = ev => {
    const v = ev.target.closest("button")?.dataset.v;
    if (!v) return;
    st.metodo = v;
    api.gravar("metodo", v);
    segs();
  };
  $("#rt-ufs").onclick = ev => {
    const uf = ev.target.closest("button")?.dataset.uf;
    if (!uf) return;
    st.estados = st.estados.includes(uf) ? st.estados.filter(x => x !== uf) : [...st.estados, uf];
    api.gravar("estados", st.estados);
    carregarCidades();
  };
  $("#rt-tempo").oninput = () => { $("#rt-tempo-v").textContent = `${$("#rt-tempo").value} s`; };
  $("#rt-filtro").oninput = mostrarLista;

  $("#rt-calcular").onclick = async () => {
    const btn = $("#rt-calcular");
    btn.disabled = true;
    const espera = st.metodo === "heuristica" ? ` (uns ${Number($("#rt-tempo").value) + 2} s)` : "";
    status(`<span class="spin"></span>Calculando${espera}…`);
    try {
      st.res = await api.chamar("resolver", {
        escopo: st.escopo, estados: st.escopo === "estados" ? st.estados : [], inicio: $("#rt-inicio").value,
        metodo: st.metodo, volta: $("#rt-volta").checked, tempo: Number($("#rt-tempo").value), distancia: st.dist,
      });
      status("");
      st.anim = performance.now();
      requestAnimationFrame(animar);
      mostrarStats();
      mostrarLista();
    } catch (e) {
      status(esc(e.message.split("\n").filter(Boolean).pop()), "erro");
    } finally {
      segs();
    }
  };

  function status(html, tipo = "") {
    const el = $("#rt-status");
    el.className = `status ${tipo}`;
    el.innerHTML = html;
  }

  // ---------- mapa ----------
  let proj = null;
  function ajustar() {
    const r = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.max(1, Math.round(r.width * dpr));
    canvas.height = Math.max(1, Math.round(r.height * dpr));
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const c = st.cid;
    if (!c || !c.n) { proj = null; return; }
    const la0 = Math.min(...c.lat), la1 = Math.max(...c.lat), lo0 = Math.min(...c.lon), lo1 = Math.max(...c.lon);
    const k = Math.cos(((la0 + la1) / 2) * Math.PI / 180);
    const w = Math.max((lo1 - lo0) * k, 0.01), h = Math.max(la1 - la0, 0.01);
    const pad = 28, esc_ = Math.min((r.width - 2 * pad) / w, (r.height - 2 * pad) / h);
    const ox = (r.width - w * esc_) / 2, oy = (r.height - h * esc_) / 2;
    proj = i => [ox + (c.lon[i] - lo0) * k * esc_, oy + (la1 - c.lat[i]) * esc_];
  }

  function desenhar(frac = 1) {
    ajustar();
    const r = canvas.getBoundingClientRect();
    ctx.clearRect(0, 0, r.width, r.height);
    const c = st.cid;
    if (!proj) {
      ctx.fillStyle = MUTE;
      ctx.font = "14px 'Plex Sans', sans-serif";
      ctx.fillText("Escolha as cidades.", 20, 30);
      return;
    }
    const tam = c.n > 2000 ? 1.2 : c.n > 300 ? 2 : 3.5;
    ctx.fillStyle = "rgba(236,236,239,0.55)";
    for (let i = 0; i < c.n; i++) {
      const [x, y] = proj(i);
      ctx.fillRect(x - tam / 2, y - tam / 2, tam, tam);
    }
    const res = st.res;
    if (res && res.n === c.n) {
      const o = res.ordem;
      const ate = Math.max(1, Math.floor((o.length - 1) * frac));
      if (res.comparar) {  // rota planejada em linha reta, por baixo, em cinza
        const oc = res.comparar.ordem;
        const ate2 = Math.max(1, Math.floor((oc.length - 1) * frac));
        ctx.strokeStyle = "rgba(150,150,162,0.75)";
        ctx.lineWidth = c.n > 2000 ? 0.6 : c.n > 300 ? 1 : 2;
        ctx.setLineDash(c.n > 300 ? [] : [6, 5]);
        ctx.beginPath();
        for (let k = 0; k <= ate2; k++) {
          const [x, y] = proj(oc[k]);
          k ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
        }
        ctx.stroke();
        ctx.setLineDash([]);
      }
      ctx.strokeStyle = RED;
      ctx.lineWidth = c.n > 2000 ? 0.7 : c.n > 300 ? 1.1 : 2;
      ctx.lineJoin = "round";
      ctx.beginPath();
      for (let k = 0; k <= ate; k++) {
        const [x, y] = proj(o[k]);
        k ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
      }
      if (res.volta && frac >= 1) ctx.lineTo(...proj(o[0]));
      ctx.stroke();
      // cidades do trecho atual
      const [xa, ya] = proj(o[ate]);
      ctx.fillStyle = FG;
      ctx.beginPath(); ctx.arc(xa, ya, 3.5, 0, 7); ctx.fill();
      const [x0, y0] = proj(o[0]);
      ctx.strokeStyle = RED_SOFT; ctx.lineWidth = 2.5;
      ctx.beginPath(); ctx.arc(x0, y0, 8, 0, 7); ctx.stroke();
      ctx.fillStyle = FG;
      ctx.font = "600 13px 'Plex Sans', sans-serif";
      ctx.fillText(c.nomes[o[0]].split("/")[0], x0 + 12, y0 - 10);
      if (c.n <= 40) {
        ctx.font = "11px 'Plex Mono', monospace";
        ctx.fillStyle = MUTE;
        for (let k = 1; k <= ate; k++) {
          const [x, y] = proj(o[k]);
          ctx.fillText(c.nomes[o[k]].split("/")[0], x + 6, y - 5);
        }
      }
    }
    if (st.hover >= 0) {
      const [x, y] = proj(st.hover);
      ctx.strokeStyle = FG; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.arc(x, y, 6, 0, 7); ctx.stroke();
    }
  }

  function animar(agora) {
    const dur = st.res && st.res.n > 2000 ? 3500 : 1800;
    const frac = Math.min(1, (agora - st.anim) / dur);
    desenhar(1 - Math.pow(1 - frac, 2));
    if (frac < 1) requestAnimationFrame(animar);
  }

  canvas.addEventListener("mousemove", ev => {
    if (!proj) return;
    const r = canvas.getBoundingClientRect();
    const mx = ev.clientX - r.left, my = ev.clientY - r.top;
    let melhor = -1, dmin = 14 * 14;
    for (let i = 0; i < st.cid.n; i++) {
      const [x, y] = proj(i);
      const d = (x - mx) ** 2 + (y - my) ** 2;
      if (d < dmin) { dmin = d; melhor = i; }
    }
    if (melhor !== st.hover) {
      st.hover = melhor;
      let txt = melhor >= 0 ? st.cid.nomes[melhor] : "";
      if (melhor >= 0 && st.res && st.res.n === st.cid.n) {
        const k = st.res.ordem.indexOf(melhor);
        txt += ` · parada ${fmt(k + 1)} · ${fmt(st.res.km_acumulado[k])} km`;
      }
      $("#rt-hover").textContent = txt;
      desenhar();
    }
  });
  canvas.addEventListener("click", () => {
    if (st.hover >= 0) $("#rt-inicio").value = st.cid.nomes[st.hover];
  });
  const obs = new ResizeObserver(() => desenhar());
  obs.observe(canvas);

  // ---------- números e lista ----------
  function mostrarStats() {
    const el = $("#rt-stats");
    const r = st.res;
    if (!r || !st.cid || r.n !== st.cid.n) {
      el.innerHTML = `<span class="rot">Resultado</span><p class="dica">Calcule uma rota para ver a distância e a qualidade. Clique no mapa para escolher a partida.</p>`;
      return;
    }
    const qual = r.otimo
      ? `<span class="selo ok">ótimo comprovado</span><p class="dica">Nenhuma ordem de visita é mais curta (${r.rodadas} rodadas, ${r.cortes} sub-rotas proibidas).</p>`
      : `<span class="selo">no máximo ${fmt(r.acima_do_limite * 100, 1)}% acima do ótimo</span>
         <p class="dica">Garantia pelo limite inferior (árvore geradora mínima: ${fmt(r.limite_inferior)} km). ${r.metodo === "genetico"
           ? "Para saber a distância real do ótimo, rode o Exato com as mesmas cidades."
           : "Na prática fica bem mais perto: nos estados onde o ótimo foi provado, a heurística ficou a 0,4–1,4%."}</p>`;
    const ganho = r.km_inicial ? `<div class="kpi"><b>${fmt((1 - r.km / r.km_inicial) * 100, 1)}%</b><span>mais curta que ${r.metodo === "genetico" ? "a 1ª geração" : "o vizinho mais próximo"}</span></div>` : "";
    const pelaEstrada = r.distancia !== "reta";
    const horas = r.horas != null ? `<div class="kpi"><b>${fmt(r.horas)} h</b><span>dirigindo (estimativa)</span></div>` : "";
    let comp = "";
    if (r.comparar) {
      const c = r.comparar;
      comp = `
        <table class="comp">
          <tr><th></th><th>no mapa</th><th>na estrada</th><th>horas</th></tr>
          <tr><td><i class="cinza"></i>planejada em linha reta</td><td>${fmt(c.km_no_mapa)} km</td><td>${fmt(c.km)} km</td><td>${fmt(c.horas)} h</td></tr>
          <tr><td><i class="verm"></i>planejada pela estrada</td><td></td><td><b>${fmt(r.km)} km</b></td><td><b>${fmt(r.horas)} h</b></td></tr>
        </table>
        <p class="dica">Planejar pela estrada economiza <b>${fmt(c.km - r.km)} km</b> (${fmt((1 - r.km / c.km) * 100, 1)}%) e
          ${fmt(c.horas - r.horas)} h. A linha reta subestima a viagem real em ${fmt((r.km / c.km_no_mapa - 1) * 100)}%.</p>`;
    }
    el.innerHTML = `
      <span class="rot">Resultado · ${esc({ heuristica: "heurística", exato: "exato", genetico: "genético" }[r.metodo])} · ${esc({ reta: "linha reta", estrada: "estrada", comparar: "comparação" }[r.distancia])}</span>
      <div class="kpis">
        <div class="kpi grande"><b>${fmt(r.km)} km</b><span>${fmt(r.n)} cidades${pelaEstrada ? " pela estrada" : " em linha reta"}${r.volta ? ", com volta" : ""}</span></div>
        ${horas}
        <div class="kpi"><b>${fmt(r.segundos, 1)} s</b><span>para calcular</span></div>
        ${ganho}
      </div>
      ${comp}
      ${qual}
      ${pelaEstrada ? `<p class="credito">${esc(info.credito_estradas)}</p>` : ""}
      ${r.historico ? `<span class="rot" style="margin-top:14px">Melhor rota por geração</span><canvas id="rt-hist"></canvas>` : ""}`;
    if (r.historico) {
      const cv = $("#rt-hist"), c2 = cv.getContext("2d");
      const dpr = window.devicePixelRatio || 1, w = cv.clientWidth, h = cv.clientHeight;
      cv.width = w * dpr; cv.height = h * dpr; c2.setTransform(dpr, 0, 0, dpr, 0, 0);
      const hs = r.historico, mx = Math.max(...hs), mn = Math.min(...hs);
      c2.strokeStyle = RED; c2.lineWidth = 2; c2.beginPath();
      hs.forEach((v, i) => {
        // rota mais longa no alto, mais curta embaixo: a curva desce conforme evolui
        const x = 4 + i / (hs.length - 1) * (w - 8), y = 6 + (1 - (v - mn) / (mx - mn || 1)) * (h - 12);
        i ? c2.lineTo(x, y) : c2.moveTo(x, y);
      });
      c2.stroke();
    }
  }

  function mostrarLista() {
    const el = $("#rt-ordem");
    const r = st.res;
    if (!r || !st.cid || r.n !== st.cid.n) { el.innerHTML = ""; return; }
    const f = $("#rt-filtro").value.trim().toLowerCase();
    const itens = [];
    for (let k = 0; k < r.ordem.length && itens.length < 300; k++) {
      const nome = st.cid.nomes[r.ordem[k]];
      if (f && !nome.toLowerCase().includes(f)) continue;
      itens.push(`<li><span class="k">${fmt(k + 1)}</span><span class="n">${esc(nome)}</span><span class="km">${fmt(r.km_acumulado[k])} km</span></li>`);
    }
    el.innerHTML = itens.join("") || `<li class="nada">nenhuma cidade com esse nome</li>`;
  }

  await carregarCidades();
  return () => obs.disconnect();
}
