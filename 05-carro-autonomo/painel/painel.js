// Painel da bancada: carro autônomo (mundo simulado + neuroevolução).

const fmt = (v, d = 1) => Number(v).toLocaleString("pt-BR", { minimumFractionDigits: d, maximumFractionDigits: d });
const NOME_PISTA = { oval: "Oval (fácil)", circuito: "Circuito (médio)", serpente: "Serpente (difícil)" };
const ROTULO_ENTRADA = ["esq 90°", "esq 50°", "esq 25°", "frente", "dir 25°", "dir 50°", "dir 90°", "velocidade"];

const HTML = `
<div class="ca">
  <section class="c ctrl">
    <h1>Carro autônomo</h1>
    <p class="dica">Ninguém ensina o carro a dirigir. Cada carro tem uma rede neural sorteada; os que vão mais longe deixam filhos para a geração seguinte.</p>

    <label class="rot" for="ca-pista">Pista do treino</label>
    <select id="ca-pista"></select>

    <div class="linha"><span class="dica">carros</span><input type="range" id="ca-carros" min="10" max="80" step="5" value="40"><span class="ms" id="ca-carros-v"></span></div>
    <div class="linha"><span class="dica" title="chance de cada peso da rede mudar num filho">mutação</span><input type="range" id="ca-taxa" min="2" max="50" value="15"><span class="ms" id="ca-taxa-v"></span></div>
    <div class="linha"><span class="dica" title="quanto tempo de pista cada geração tem">tempo</span><input type="range" id="ca-seg" min="10" max="60" step="5" value="30"><span class="ms" id="ca-seg-v"></span></div>

    <button class="btn" id="ca-evoluir">Evoluir</button>
    <div class="linha acoes">
      <button class="btn sec" id="ca-uma">Uma geração</button>
      <button class="btn sec" id="ca-novo">Recomeçar</button>
    </div>
    <label class="check"><input type="checkbox" id="ca-rapido"> treino rápido (mostra uma geração a cada cinco)</label>
    <div class="status" id="ca-status"></div>

    <span class="rot">Objetos na pista</span>
    <div class="seg" id="ca-ferramenta">
      <button data-v="" class="on">nenhum</button><button data-v="cone">cone</button><button data-v="caixa">caixa</button><button data-v="apagar">apagar</button>
    </div>
    <p class="dica" id="ca-dica-obj">Escolha cone ou caixa e clique na pista. Valem a partir da próxima corrida.</p>
    <button class="btn sec" id="ca-limpar">Tirar todos os objetos</button>

    <span class="rot">Testar o campeão</span>
    <div class="linha">
      <select id="ca-pista-teste"></select>
      <button class="btn sec" id="ca-testar">Testar</button>
    </div>
    <button class="btn sec" id="ca-salvar">Salvar o campeão</button>
  </section>

  <section class="c tela">
    <div class="c-topo">
      <span class="rot" id="ca-titulo">Mundo</span>
      <span class="dica" id="ca-relogio"></span>
      <div class="linha">
        <div class="seg" id="ca-vel"><button data-v="1">1×</button><button data-v="2" class="on">2×</button><button data-v="4">4×</button><button data-v="8">8×</button></div>
        <button class="btn sec" id="ca-pular">Pular</button>
      </div>
    </div>
    <canvas id="ca-mundo"></canvas>
  </section>

  <section class="c stats">
    <div class="kpis">
      <div class="kpi grande"><b id="ca-k-ger">0</b><span>geração</span></div>
      <div class="kpi"><b id="ca-k-melhor">–</b><span>voltas do melhor</span></div>
      <div class="kpi"><b id="ca-k-recorde">–</b><span>recorde</span></div>
    </div>
    <span class="rot">Voltas por geração</span>
    <canvas id="ca-grafico" height="130"></canvas>
    <p class="dica leg"><i class="l1"></i>melhor <i class="l2"></i>média da população</p>
  </section>

  <section class="c rede">
    <span class="rot">O que o líder vê, pensa e faz</span>
    <canvas id="ca-rede" height="250"></canvas>
  </section>
</div>`;

export async function montar(raiz, api) {
  raiz.innerHTML = `<link rel="stylesheet" href="${new URL("painel.css", import.meta.url)}">` + HTML;
  const $ = s => raiz.querySelector(s);
  const css = n => getComputedStyle(raiz).getPropertyValue(n).trim();
  const COR = { pista: "#262b36", borda: "#8b93a3", meio: "rgba(255,255,255,.16)", carro: "rgba(210,216,228,.55)", morto: "rgba(210,216,228,.14)",
                lider: css("--red") || "#E5484D", raio: "rgba(88,214,141,.75)", cone: "#F5A524", caixa: "#b08968", pos: "#58D68D", neg: "#E5484D" };

  const info = await api.chamar("info");
  const st = {
    pista: api.ler("pista", "circuito"), objetos: api.ler("objetos", {}), ferramenta: "", vel: 2,
    rodando: false, ocupado: false, vivo: true, hist: info.estado.historico || [], geracao: info.estado.geracao || 0,
    grav: null, t: 0, pistaTela: null, pular: false, lider: null,
  };
  if (!info.pistas[st.pista]) st.pista = "circuito";
  if (info.estado.pista && info.estado.geracao) st.pista = info.estado.pista;
  st.pistaTela = st.pista;

  const opcoes = Object.keys(info.pistas).map(p => `<option value="${p}">${NOME_PISTA[p] || p}</option>`).join("");
  $("#ca-pista").innerHTML = opcoes; $("#ca-pista").value = st.pista;
  $("#ca-pista-teste").innerHTML = opcoes; $("#ca-pista-teste").value = st.pista;

  const objetos = p => st.objetos[p] || (st.objetos[p] = []);
  const status = (txt, classe = "") => { const e = $("#ca-status"); e.className = "status " + classe; e.innerHTML = txt; };

  // ---------- controles ----------
  function rotulos() {
    $("#ca-carros-v").textContent = $("#ca-carros").value;
    $("#ca-taxa-v").textContent = $("#ca-taxa").value + "%";
    $("#ca-seg-v").textContent = $("#ca-seg").value + " s";
  }
  for (const id of ["carros", "taxa", "seg"]) {
    const el = $("#ca-" + id);
    el.value = api.ler(id, el.value);
    el.addEventListener("input", () => { api.gravar(id, el.value); rotulos(); });
  }
  rotulos();

  function seg(sel, aoMudar) {
    $(sel).addEventListener("click", e => {
      const b = e.target.closest("button"); if (!b) return;
      $(sel).querySelectorAll("button").forEach(x => x.classList.toggle("on", x === b));
      aoMudar(b.dataset.v);
    });
  }
  seg("#ca-vel", v => { st.vel = +v; });
  seg("#ca-ferramenta", v => { st.ferramenta = v; canvas.style.cursor = v ? "crosshair" : "default"; });

  function kpis() {
    $("#ca-k-ger").textContent = st.geracao;
    const u = st.hist[st.hist.length - 1];
    $("#ca-k-melhor").textContent = u ? fmt(u.melhor) : "–";
    $("#ca-k-recorde").textContent = st.hist.length ? fmt(Math.max(...st.hist.map(h => h.melhor))) : "–";
    grafico();
  }

  // ---------- mundo ----------
  const canvas = $("#ca-mundo"), ctx = canvas.getContext("2d");
  let escala = 1;
  function ajustar() {
    const m = info.pistas[st.pistaTela].mundo, r = window.devicePixelRatio || 1;
    canvas.style.aspectRatio = `${m.largura} / ${m.altura}`;
    const w = canvas.clientWidth;
    if (w <= 0) return;
    canvas.width = w * r; canvas.height = w * m.altura / m.largura * r;
    escala = canvas.width / m.largura;
  }
  const obs = new ResizeObserver(() => { ajustar(); desenhar(); });
  obs.observe(canvas.parentElement);

  function caminho(pts, fechar) {
    pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y));
    if (fechar) ctx.closePath();
  }

  function desenharObjeto(o) {
    if (o.tipo === "cone") {
      ctx.fillStyle = COR.cone; ctx.beginPath(); ctx.arc(o.x, o.y, o.raio || 0.6, 0, 7); ctx.fill();
      ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.arc(o.x, o.y, (o.raio || 0.6) * 0.4, 0, 7); ctx.fill();
    } else if (o.tipo === "caixa") {
      const l = o.largura || 2, a = o.altura || 2;
      ctx.fillStyle = COR.caixa; ctx.fillRect(o.x - l / 2, o.y - a / 2, l, a);
      ctx.strokeStyle = "rgba(0,0,0,.45)"; ctx.lineWidth = 0.12; ctx.strokeRect(o.x - l / 2, o.y - a / 2, l, a);
    }
  }

  function carro(x, y, ang, cor, lider) {
    const c = info.carro;
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang);
    ctx.fillStyle = cor;
    ctx.beginPath(); ctx.roundRect(-c.comprimento / 2, -c.largura / 2, c.comprimento, c.largura, 0.5); ctx.fill();
    if (lider) { ctx.fillStyle = "rgba(0,0,0,.45)"; ctx.fillRect(c.comprimento * 0.1, -c.largura * 0.36, c.comprimento * 0.2, c.largura * 0.72); }
    ctx.restore();
  }

  function quadroAtual() {
    const g = st.grav; if (!g) return null;
    const f = Math.min(st.t / g.dt, g.x.length - 1), i = Math.floor(f), j = Math.min(i + 1, g.x.length - 1), k = f - i;
    return { g, i, j, k };
  }

  function desenhar() {
    const p = info.pistas[st.pistaTela];
    ctx.setTransform(escala, 0, 0, escala, 0, 0);
    ctx.clearRect(0, 0, p.mundo.largura, p.mundo.altura);
    const bordas = p.mundo.objetos.filter(o => o.tipo === "pista");
    ctx.fillStyle = COR.pista; ctx.beginPath(); bordas.forEach(b => caminho(b.pontos, true)); ctx.fill("evenodd");
    ctx.strokeStyle = COR.borda; ctx.lineWidth = 0.3; ctx.lineJoin = "round";
    bordas.forEach(b => { ctx.beginPath(); caminho(b.pontos, true); ctx.stroke(); });
    ctx.strokeStyle = COR.meio; ctx.lineWidth = 0.2; ctx.setLineDash([1.6, 1.6]);
    ctx.beginPath(); caminho(p.centro, true); ctx.stroke(); ctx.setLineDash([]);
    // linha de largada
    const [lx, ly, la] = p.largada, m = p.largura / 2;
    ctx.strokeStyle = "#fff"; ctx.lineWidth = 0.5; ctx.beginPath();
    ctx.moveTo(lx - Math.sin(la) * m, ly + Math.cos(la) * m); ctx.lineTo(lx + Math.sin(la) * m, ly - Math.cos(la) * m); ctx.stroke();
    objetos(st.pistaTela).forEach(desenharObjeto);

    const q = quadroAtual();
    if (!q) { carro(lx, ly, la, COR.carro, false); st.lider = null; redeViz(); return; }
    const { g, i, j, k } = q, n = g.x[i].length, L = g.lider;
    const em = (v, c) => v[i][c] + (v[j][c] - v[i][c]) * k;
    for (let c = 0; c < n; c++) if (c !== L && !g.vivo[i][c]) carro(em(g.x, c), em(g.y, c), em(g.ang, c), COR.morto, false);
    for (let c = 0; c < n; c++) if (c !== L && g.vivo[i][c]) carro(em(g.x, c), em(g.y, c), em(g.ang, c), COR.carro, false);
    const x = em(g.x, L), y = em(g.y, L), a = em(g.ang, L), ent = g.entradas[i];
    if (g.vivo[i][L]) {
      ctx.lineWidth = 0.14;
      info.sensores.forEach((s, r) => {
        const d = ent[r] * info.alcance, fx = x + Math.cos(a + s) * d, fy = y + Math.sin(a + s) * d;
        ctx.strokeStyle = COR.raio; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(fx, fy); ctx.stroke();
        ctx.fillStyle = COR.raio; ctx.beginPath(); ctx.arc(fx, fy, 0.35, 0, 7); ctx.fill();
      });
    }
    carro(x, y, a, COR.lider, true);
    st.lider = { ent, oculta: g.oculta[i], saida: g.saida[i] };
    const vivos = g.vivo[i].reduce((s, v) => s + v, 0);
    $("#ca-relogio").textContent = `${fmt(Math.min(st.t, (g.x.length - 1) * g.dt))} s · ${vivos} de ${n} na pista · ${fmt(ent[ent.length - 1] * info.carro.vel_max * 3.6, 0)} km/h`;
    redeViz();
  }

  // ---------- a rede do líder ----------
  const cRede = $("#ca-rede"), xr = cRede.getContext("2d");
  function redeViz() {
    const r = window.devicePixelRatio || 1, w = cRede.clientWidth, h = 250;
    if (!w) return;
    if (cRede.width !== w * r) { cRede.width = w * r; cRede.height = h * r; }
    xr.setTransform(r, 0, 0, r, 0, 0); xr.clearRect(0, 0, w, h);
    const [ne, no, ns] = info.rede, l = st.lider;
    const col = [110, w / 2 + 10, w - 120];
    const ys = (n, k) => 16 + (h - 32) * (n === 1 ? 0.5 : k / (n - 1));
    const pe = Array.from({ length: ne }, (_, k) => [col[0], ys(ne, k)]);
    const po = Array.from({ length: no }, (_, k) => [col[1], ys(no, k)]);
    const ps = [[col[2], h * 0.33], [col[2], h * 0.67]];
    xr.lineWidth = 1; xr.strokeStyle = "rgba(255,255,255,.06)";
    xr.beginPath();
    pe.forEach(a => po.forEach(b => { xr.moveTo(...a); xr.lineTo(...b); }));
    po.forEach(a => ps.forEach(b => { xr.moveTo(...a); xr.lineTo(...b); }));
    xr.stroke();
    const no_ = ([x, y], v, sinal) => {
      const a = Math.min(1, Math.abs(v));
      xr.fillStyle = "#1b1f27"; xr.beginPath(); xr.arc(x, y, 8, 0, 7); xr.fill();
      xr.globalAlpha = 0.15 + 0.85 * a; xr.fillStyle = sinal && v < 0 ? COR.neg : COR.pos;
      xr.beginPath(); xr.arc(x, y, 8, 0, 7); xr.fill(); xr.globalAlpha = 1;
    };
    xr.font = "11px " + (css("--mono") || "monospace"); xr.textBaseline = "middle";
    pe.forEach((p, k) => {
      no_(p, l ? l.ent[k] : 0, false);
      xr.fillStyle = css("--mute") || "#888"; xr.textAlign = "right"; xr.fillText(ROTULO_ENTRADA[k] || "", p[0] - 14, p[1]);
    });
    po.forEach((p, k) => no_(p, l ? l.oculta[k] : 0, true));
    const texto = l ? [
      l.saida[0] > 0.08 ? "vira à direita" : l.saida[0] < -0.08 ? "vira à esquerda" : "segue reto",
      l.saida[1] > 0.08 ? "acelera" : l.saida[1] < -0.08 ? "freia" : "solta o pé",
    ] : ["volante", "acelerador"];
    ps.forEach((p, k) => {
      no_(p, l ? l.saida[k] : 0, true);
      xr.fillStyle = css("--body") || "#ccc"; xr.textAlign = "left"; xr.fillText(texto[k], p[0] + 14, p[1]);
    });
  }

  // ---------- gráfico ----------
  const cGraf = $("#ca-grafico"), xg = cGraf.getContext("2d");
  function grafico() {
    const r = window.devicePixelRatio || 1, w = cGraf.clientWidth, h = 130;
    if (!w) return;
    cGraf.width = w * r; cGraf.height = h * r; xg.setTransform(r, 0, 0, r, 0, 0); xg.clearRect(0, 0, w, h);
    xg.strokeStyle = css("--line") || "#333"; xg.lineWidth = 1; xg.beginPath(); xg.moveTo(0, h - 0.5); xg.lineTo(w, h - 0.5); xg.stroke();
    if (!st.hist.length) return;
    const topo = Math.max(1, ...st.hist.map(p => p.melhor)) * 1.1, n = Math.max(st.hist.length - 1, 1);
    const linha = (chave, cor) => {
      xg.strokeStyle = cor; xg.lineWidth = 2; xg.beginPath();
      st.hist.forEach((p, i) => { const x = 4 + (w - 8) * i / n, y = h - 4 - (h - 12) * p[chave] / topo; i ? xg.lineTo(x, y) : xg.moveTo(x, y); });
      xg.stroke();
    };
    linha("media", "#6b7385"); linha("melhor", COR.lider);
    xg.fillStyle = css("--mute") || "#888"; xg.font = "11px " + (css("--mono") || "monospace");
    xg.fillText(fmt(topo / 1.1) + " voltas", 4, 10);
  }

  // ---------- reprodução ----------
  let ultimo = 0, aoTerminar = null;
  function tique(agora) {
    if (!st.vivo) return;
    const dt = Math.min(0.1, (agora - ultimo) / 1000); ultimo = agora;
    if (st.grav && aoTerminar) {
      st.t += dt * st.vel;
      const g = st.grav, fim = (g.x.length - 1) * g.dt + 0.6;
      desenhar();
      if (st.t >= fim || st.pular) { st.pular = false; const f = aoTerminar; aoTerminar = null; f(); }
    }
    requestAnimationFrame(tique);
  }
  requestAnimationFrame(t => { ultimo = t; tique(t); });

  function tocar(grav, pista, titulo) {
    st.grav = grav; st.t = 0; st.pular = false; st.pistaTela = pista;
    $("#ca-titulo").textContent = titulo;
    ajustar();
    return new Promise(ok => { aoTerminar = ok; });
  }

  // ---------- ações ----------
  async function umaGeracao(mostrar) {
    const r = await api.chamar("geracao", {
      pista: st.pista, carros: +$("#ca-carros").value, taxa: +$("#ca-taxa").value / 100, segundos: +$("#ca-seg").value,
      objetos: objetos(st.pista), gravar: mostrar,
    });
    st.geracao = r.estado.geracao; st.hist = r.estado.historico;
    kpis();
    status(`Geração ${st.geracao}: o melhor fez ${fmt(r.voltas)} ${r.voltas === 1 ? "volta" : "voltas"}.`);
    if (mostrar && r.gravacao) await tocar(r.gravacao, st.pista, `Geração ${st.geracao}`);
  }

  async function ciclo(continuo) {
    if (st.ocupado) return;
    st.ocupado = true; st.rodando = continuo;
    $("#ca-evoluir").textContent = continuo ? "Parar" : "Evoluir";
    try {
      do {
        const mostrar = !$("#ca-rapido").checked || !continuo || (st.geracao + 1) % 5 === 0;
        if (!mostrar) status(`<span class="spin"></span>Treinando a geração ${st.geracao + 1}…`);
        await umaGeracao(mostrar);
      } while (st.rodando && st.vivo);
    } catch (e) { status(String(e.message || e), "erro"); }
    st.ocupado = false; st.rodando = false;
    $("#ca-evoluir").textContent = "Evoluir";
  }

  $("#ca-evoluir").addEventListener("click", () => { if (st.rodando) { st.rodando = false; st.pular = true; } else ciclo(true); });
  $("#ca-uma").addEventListener("click", () => ciclo(false));
  $("#ca-pular").addEventListener("click", () => { st.pular = true; });

  async function recomecar() {
    st.rodando = false; st.pular = true;
    while (st.ocupado) await new Promise(r => setTimeout(r, 50));
    st.pular = false;
    const e = await api.chamar("reiniciar", { pista: st.pista, carros: +$("#ca-carros").value });
    st.geracao = 0; st.hist = e.historico; st.grav = null; st.pistaTela = st.pista;
    $("#ca-titulo").textContent = "Mundo"; $("#ca-relogio").textContent = "";
    status("População nova, com cérebros sorteados."); kpis(); ajustar(); desenhar();
  }
  $("#ca-novo").addEventListener("click", recomecar);
  $("#ca-pista").addEventListener("change", e => { st.pista = e.target.value; api.gravar("pista", st.pista); $("#ca-pista-teste").value = st.pista; recomecar(); });

  $("#ca-testar").addEventListener("click", async () => {
    if (st.ocupado) { status("Pare a evolução antes de testar.", "erro"); return; }
    st.ocupado = true;
    try {
      const p = $("#ca-pista-teste").value;
      const r = await api.chamar("testar", { pista: p, objetos: objetos(p) });
      status(`Campeão treinado em “${NOME_PISTA[r.treinado_em] || r.treinado_em}”, testado em “${NOME_PISTA[p]}”: ${fmt(r.voltas)} voltas${r.bateu ? ", e saiu da corrida" : ", sem bater"}.`, r.bateu ? "erro" : "ok");
      await tocar(r.gravacao, p, "Teste do campeão");
    } catch (e) { status(String(e.message || e).split("\n").filter(Boolean).pop(), "erro"); }
    st.ocupado = false;
  });

  $("#ca-salvar").addEventListener("click", async () => {
    try { const r = await api.chamar("salvar"); status(`Campeão salvo em ${r.arquivo}.`, "ok"); }
    catch (e) { status(String(e.message || e).split("\n").filter(Boolean).pop(), "erro"); }
  });

  // ---------- objetos ----------
  canvas.addEventListener("click", e => {
    if (!st.ferramenta) return;
    const b = canvas.getBoundingClientRect(), m = info.pistas[st.pistaTela].mundo;
    const x = (e.clientX - b.left) / b.width * m.largura, y = (e.clientY - b.top) / b.height * m.altura;
    const lista = objetos(st.pistaTela);
    if (st.ferramenta === "apagar") {
      let melhor = -1, dist = 2.5;
      lista.forEach((o, i) => { const d = Math.hypot(o.x - x, o.y - y); if (d < dist) { dist = d; melhor = i; } });
      if (melhor >= 0) lista.splice(melhor, 1);
    } else {
      lista.push(st.ferramenta === "cone" ? { tipo: "cone", x: +x.toFixed(2), y: +y.toFixed(2), raio: 0.6 }
                                           : { tipo: "caixa", x: +x.toFixed(2), y: +y.toFixed(2), largura: 2, altura: 2 });
    }
    api.gravar("objetos", st.objetos);
    if (!aoTerminar) desenhar();
  });
  $("#ca-limpar").addEventListener("click", () => { st.objetos[st.pistaTela] = []; api.gravar("objetos", st.objetos); if (!aoTerminar) desenhar(); });

  kpis(); ajustar(); desenhar();
  if (st.geracao) status(`Treino em andamento: geração ${st.geracao}. Clique em Evoluir para continuar.`);

  return () => { st.vivo = false; st.rodando = false; st.pular = true; obs.disconnect(); };
}
