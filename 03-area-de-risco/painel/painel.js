// Painel da bancada: pessoa em área de risco (detector pronto + área desenhada na imagem).

const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const fmt = (v, d = 0) => Number(v).toLocaleString("pt-BR", { minimumFractionDigits: d, maximumFractionDigits: d });
const RED = "#E5484D", VERDE = "#58D68D", FG = "#ECECEF", MUTE = "#87878F";
const NOMES_MODELO = { rapido: "Rápido", medio: "Médio", preciso: "Preciso" };

const HTML = `
<div class="ar">
  <section class="c ctrl">
    <h1>Pessoa em área de risco</h1>
    <p class="dica">Um detector de pessoas pronto e uma área desenhada no chão da imagem. Nada foi treinado aqui.</p>

    <label class="rot" for="ar-video">Vídeo</label>
    <select id="ar-video"></select>

    <span class="rot">Modelo</span>
    <div class="seg" id="ar-modelo"></div>
    <p class="dica" id="ar-modelo-dica"></p>

    <div class="linha">
      <label class="rot" for="ar-conf">Confiança mínima</label>
      <input type="range" id="ar-conf" min="0.2" max="0.95" step="0.05" value="0.5"><span class="ms" id="ar-conf-v">50%</span>
    </div>

    <span class="rot">Área de risco</span>
    <div class="linha">
      <button class="btn sec" id="ar-desenhar">Desenhar</button>
      <button class="btn sec" id="ar-exemplo">Exemplo</button>
      <button class="btn sec" id="ar-limpar">Limpar</button>
    </div>
    <p class="dica" id="ar-area-dica"></p>

    <span class="rot">Vídeo inteiro</span>
    <div class="linha">
      <label class="dica" for="ar-passo">analisar 1 a cada</label>
      <select id="ar-passo"><option value="5">5 quadros</option><option value="10" selected>10 quadros</option><option value="15">15 quadros</option><option value="30">30 quadros</option></select>
    </div>
    <div class="linha">
      <label class="dica" for="ar-pers">alertar depois de</label>
      <select id="ar-pers"><option value="1">1 quadro</option><option value="2" selected>2 seguidos</option><option value="3">3 seguidos</option><option value="5">5 seguidos</option></select>
    </div>
    <button class="btn" id="ar-analisar">Analisar o vídeo</button>
    <div class="status" id="ar-status"></div>
  </section>

  <section class="c tela">
    <div class="c-topo"><span class="rot" id="ar-titulo">Quadro</span><span class="ms" id="ar-ms"></span></div>
    <div class="palco"><canvas id="ar-canvas"></canvas></div>
    <div class="linha transporte">
      <button class="btn sec" id="ar-play" title="reproduzir os quadros analisados">▶</button>
      <input type="range" id="ar-quadro" min="0" max="0" step="1" value="0">
      <span class="ms" id="ar-tempo"></span>
    </div>
    <canvas id="ar-linha" title="pessoas na área ao longo do vídeo: clique para ir ao momento"></canvas>
  </section>

  <section class="c stats" id="ar-stats"></section>
</div>`;

const DICA_MODELO = {
  rapido: "Leve. Bom de perto; não enxerga pessoas longe da câmera.",
  medio: "Equilíbrio entre acerto e velocidade. Recomendado.",
  preciso: "Mais pesado e mais lento. Acha um pouco mais.",
};

export async function montar(raiz, api) {
  raiz.innerHTML = `<link rel="stylesheet" href="${new URL("painel.css", import.meta.url)}">` + HTML;
  const $ = s => raiz.querySelector(s);
  const info = await api.chamar("info");
  if (!info.videos.length) {
    $(".tela").innerHTML = `<p class="dica">Nenhum vídeo em <code>videos/</code>. Rode <code>python baixar_videos.py</code> na pasta do projeto.</p>`;
    return;
  }
  const st = {
    video: api.ler("video", "pexels_15170997.mp4"), modelo: api.ler("modelo", "medio"),
    areas: api.ler("areas", {}), desenhando: false, rascunho: [], quadro: null, img: null,
    analise: null, tocando: false, seq: 0, emAndamento: false, pendente: false,
  };
  if (!info.videos.some(v => v.arquivo === st.video)) st.video = info.videos[0].arquivo;
  const canvas = $("#ar-canvas"), ctx = canvas.getContext("2d");
  const linha = $("#ar-linha"), lctx = linha.getContext("2d");

  const video = () => info.videos.find(v => v.arquivo === st.video);
  const area = () => st.areas[st.video] ?? video().area_exemplo;
  const conf = () => Number($("#ar-conf").value);

  $("#ar-video").innerHTML = info.videos.map(v => `<option value="${esc(v.arquivo)}">${esc(v.descricao)}</option>`).join("");
  $("#ar-video").value = st.video;
  $("#ar-modelo").innerHTML = info.modelos.map(m => `<button data-v="${m}">${esc(NOMES_MODELO[m] || m)}</button>`).join("");

  function controles() {
    for (const b of raiz.querySelectorAll("#ar-modelo button")) b.classList.toggle("on", b.dataset.v === st.modelo);
    $("#ar-modelo-dica").textContent = DICA_MODELO[st.modelo] || "";
    $("#ar-conf-v").textContent = `${Math.round(conf() * 100)}%`;
    $("#ar-desenhar").textContent = st.desenhando ? "Concluir" : "Desenhar";
    $("#ar-desenhar").classList.toggle("ativo", st.desenhando);
    const a = area();
    $("#ar-area-dica").textContent = st.desenhando
      ? `Clique na imagem para marcar os cantos (${st.rascunho.length} ponto${st.rascunho.length === 1 ? "" : "s"}). Depois, Concluir.`
      : a.length >= 3 ? "Vale o ponto dos pés: o meio da base da caixa de cada pessoa." : "Sem área: desenhe uma ou use o exemplo.";
    const v = video();
    $("#ar-quadro").max = v.quadros - 1;
    $("#ar-titulo").textContent = `${v.largura}×${v.altura} · ${fmt(v.quadros / v.fps, 1)} s · ${info.dispositivo === "cuda" ? "GPU" : "CPU"}`;
  }

  // ---------- quadro ----------
  async function pedir(comImagem = true) {
    if (st.emAndamento) { st.pendente = true; return; }
    st.emAndamento = true;
    const indice = Number($("#ar-quadro").value);
    try {
      const r = await api.chamar("quadro", {
        video: st.video, indice, modelo: st.modelo, confianca: conf(), poligono: area(), imagem: comImagem || !st.img,
      });
      if (r.jpeg) {
        const img = new Image();
        await new Promise((ok, falha) => { img.onload = ok; img.onerror = falha; img.src = `data:image/jpeg;base64,${r.jpeg}`; });
        st.img = img;
      }
      st.quadro = r;
      $("#ar-ms").innerHTML = r.ms_deteccao != null ? `detecção em <b>${fmt(r.ms_deteccao)} ms</b>` : "detecção já calculada";
      desenhar();
      mostrarStats();
    } catch (e) {
      status(esc(e.message.split("\n").filter(Boolean).pop()), "erro");
    } finally {
      st.emAndamento = false;
      if (st.pendente) { st.pendente = false; pedir(true); }
    }
  }

  function desenhar() {
    if (!st.img) return;
    const larg = canvas.parentElement.clientWidth;
    const alt = Math.min(larg * st.img.height / st.img.width, 640);
    const w = alt * st.img.width / st.img.height;
    const dpr = window.devicePixelRatio || 1;
    canvas.style.width = `${w}px`;
    canvas.style.height = `${alt}px`;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(alt * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.drawImage(st.img, 0, 0, w, alt);
    const P = ([x, y]) => [x * w, y * alt];
    // área de risco
    const pts = st.desenhando ? st.rascunho : area();
    if (pts.length) {
      ctx.beginPath();
      pts.forEach((p, i) => { const [x, y] = P(p); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); });
      if (!st.desenhando) ctx.closePath();
      ctx.fillStyle = "rgba(229,72,77,0.22)";
      if (!st.desenhando && pts.length >= 3) ctx.fill();
      ctx.strokeStyle = RED; ctx.lineWidth = 2; ctx.setLineDash(st.desenhando ? [6, 5] : []);
      ctx.stroke(); ctx.setLineDash([]);
      for (const p of pts) { const [x, y] = P(p); ctx.fillStyle = RED; ctx.beginPath(); ctx.arc(x, y, 4, 0, 7); ctx.fill(); }
    }
    // pessoas
    for (const p of st.quadro?.pessoas || []) {
      const [x1, y1] = P(p.caixa.slice(0, 2)), [x2, y2] = P(p.caixa.slice(2));
      const cor = p.na_area ? RED : VERDE;
      ctx.strokeStyle = cor; ctx.lineWidth = p.na_area ? 3 : 2;
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
      const [fx, fy] = P(p.pes);
      ctx.fillStyle = cor; ctx.beginPath(); ctx.arc(fx, fy, 4, 0, 7); ctx.fill();
      const rot = `${Math.round(p.confianca * 100)}%`;
      ctx.font = "600 12px 'Plex Mono', monospace";
      const tw = ctx.measureText(rot).width + 8;
      ctx.fillStyle = cor; ctx.fillRect(x1, Math.max(0, y1 - 17), tw, 17);
      ctx.fillStyle = "#111"; ctx.fillText(rot, x1 + 4, Math.max(12, y1 - 4));
    }
    const nArea = (st.quadro?.pessoas || []).filter(p => p.na_area).length;
    if (nArea && !st.desenhando) {
      ctx.fillStyle = RED; ctx.fillRect(10, 10, 210, 30);
      ctx.fillStyle = "#fff"; ctx.font = "700 14px 'Plex Sans', sans-serif";
      ctx.fillText(`PESSOA NA ÁREA DE RISCO`, 20, 30);
    }
    desenharLinha();
  }

  // ---------- linha do tempo ----------
  function desenharLinha() {
    const w = linha.clientWidth, h = linha.clientHeight, dpr = window.devicePixelRatio || 1;
    linha.width = w * dpr; linha.height = h * dpr; lctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    lctx.clearRect(0, 0, w, h);
    const v = video(), a = st.analise;
    lctx.fillStyle = "rgba(255,255,255,0.05)"; lctx.fillRect(0, h - 6, w, 6);
    if (a) {
      const mx = Math.max(1, ...a.linha.map(x => x.pessoas));
      const bw = Math.max(2, w / a.linha.length - 1);
      a.linha.forEach(x => {
        const px = x.indice / (v.quadros - 1) * (w - bw);
        if (x.alerta) { lctx.fillStyle = "rgba(229,72,77,0.20)"; lctx.fillRect(px, 0, bw + 1, h - 6); }
        const hp = x.pessoas / mx * (h - 14);
        lctx.fillStyle = "rgba(135,135,143,0.55)"; lctx.fillRect(px, h - 6 - hp, bw, hp);
        const ha = x.na_area / mx * (h - 14);
        lctx.fillStyle = RED; lctx.fillRect(px, h - 6 - ha, bw, ha);
      });
    } else {
      lctx.fillStyle = MUTE; lctx.font = "12px 'Plex Sans', sans-serif";
      lctx.fillText("Analise o vídeo para ver a linha do tempo: cinza = pessoas, vermelho = na área.", 4, h / 2);
    }
    const pos = Number($("#ar-quadro").value) / Math.max(1, v.quadros - 1) * w;
    lctx.fillStyle = FG; lctx.fillRect(pos - 1, 0, 2, h);
    $("#ar-tempo").textContent = `${fmt(Number($("#ar-quadro").value) / v.fps, 1)} s`;
  }

  // ---------- números ----------
  function mostrarStats() {
    const q = st.quadro, a = st.analise;
    const n = q ? q.pessoas.length : 0, na = q ? q.pessoas.filter(p => p.na_area).length : 0;
    let h = `<span class="rot">Neste quadro</span>
      <div class="kpis">
        <div class="kpi"><b>${n}</b><span>pessoa${n === 1 ? "" : "s"} detectada${n === 1 ? "" : "s"}</span></div>
        <div class="kpi ${na ? "alerta" : ""}"><b>${na}</b><span>na área de risco</span></div>
      </div>`;
    if (a) {
      h += `<span class="rot">No vídeo inteiro</span>
      <div class="kpis">
        <div class="kpi ${a.eventos.length ? "alerta" : ""}"><b>${a.eventos.length}</b><span>alerta${a.eventos.length === 1 ? "" : "s"}</span></div>
        <div class="kpi"><b>${fmt(a.tempo_com_alerta, 1)} s</b><span>com gente na área, de ${fmt(a.duracao, 1)} s</span></div>
        <div class="kpi"><b>${a.quadros_analisados}</b><span>quadros analisados em ${fmt(a.segundos, 1)} s${a.quadros_por_s ? ` (${fmt(a.quadros_por_s, 1)}/s)` : ""}</span></div>
      </div>
      <div class="eventos">${a.eventos.map((e, i) => `<button data-i="${e.indice}">alerta ${i + 1}<em>${fmt(e.inicio, 1)} s – ${fmt(e.fim, 1)} s</em></button>`).join("") || `<span class="dica">nenhum alerta com esta área e estas regras</span>`}</div>`;
    } else {
      h += `<p class="dica">"Analisar o vídeo" percorre o vídeo, monta a linha do tempo e lista os alertas.</p>`;
    }
    h += `<p class="dica limite">Limites conhecidos: pessoa encoberta ou muito longe, e gente vista de cima (o operador sentado na empilhadeira não é detectado). A contagem oscila entre quadros, por isso o alerta pede quadros seguidos.</p>`;
    $("#ar-stats").innerHTML = h;
  }

  function status(html, tipo = "") {
    const el = $("#ar-status");
    el.className = `status ${tipo}`;
    el.innerHTML = html;
  }

  function invalidar() { st.analise = null; parar(); }

  // ---------- eventos ----------
  $("#ar-video").onchange = () => {
    st.video = $("#ar-video").value; api.gravar("video", st.video);
    st.desenhando = false; st.rascunho = []; st.img = null; invalidar();
    $("#ar-quadro").value = Math.floor(video().quadros / 2);
    controles(); pedir();
  };
  $("#ar-modelo").onclick = ev => {
    const m = ev.target.closest("button")?.dataset.v;
    if (!m) return;
    st.modelo = m; api.gravar("modelo", m); invalidar(); controles(); pedir(false);
  };
  $("#ar-conf").oninput = () => { invalidar(); controles(); pedir(false); };
  $("#ar-quadro").oninput = () => { parar(); pedir(); };
  $("#ar-desenhar").onclick = () => {
    if (st.desenhando) {
      if (st.rascunho.length >= 3) { st.areas[st.video] = st.rascunho; api.gravar("areas", st.areas); invalidar(); }
      st.desenhando = false; st.rascunho = [];
      controles(); pedir(false);
    } else {
      st.desenhando = true; st.rascunho = []; parar(); controles(); desenhar();
    }
  };
  $("#ar-exemplo").onclick = () => {
    delete st.areas[st.video]; api.gravar("areas", st.areas);
    st.desenhando = false; st.rascunho = []; invalidar(); controles(); pedir(false);
  };
  $("#ar-limpar").onclick = () => {
    st.areas[st.video] = []; api.gravar("areas", st.areas);
    st.desenhando = false; st.rascunho = []; invalidar(); controles(); pedir(false);
  };
  canvas.addEventListener("click", ev => {
    if (!st.desenhando) return;
    const r = canvas.getBoundingClientRect();
    st.rascunho.push([+((ev.clientX - r.left) / r.width).toFixed(4), +((ev.clientY - r.top) / r.height).toFixed(4)]);
    controles(); desenhar();
  });
  linha.addEventListener("click", ev => {
    const r = linha.getBoundingClientRect();
    $("#ar-quadro").value = Math.round((ev.clientX - r.left) / r.width * (video().quadros - 1));
    parar(); pedir();
  });
  $("#ar-stats").addEventListener("click", ev => {
    const i = ev.target.closest("button[data-i]")?.dataset.i;
    if (i == null) return;
    $("#ar-quadro").value = i; parar(); pedir();
  });

  $("#ar-analisar").onclick = async () => {
    const btn = $("#ar-analisar");
    btn.disabled = true; parar();
    const v = video(), passo = Number($("#ar-passo").value);
    status(`<span class="spin"></span>Analisando ${Math.ceil(v.quadros / passo)} quadros… (pode levar um minuto na primeira vez)`);
    try {
      st.analise = await api.chamar("analisar", {
        video: st.video, modelo: st.modelo, confianca: conf(), poligono: area(), passo, persistencia: Number($("#ar-pers").value),
      });
      status("");
      desenhar(); mostrarStats();
    } catch (e) {
      status(esc(e.message.split("\n").filter(Boolean).pop()), "erro");
    } finally {
      btn.disabled = false;
    }
  };

  // reprodução: percorre os quadros já analisados (a detecção está guardada, então é rápido)
  function parar() { st.tocando = false; $("#ar-play").textContent = "▶"; }
  $("#ar-play").onclick = async () => {
    if (st.tocando) return parar();
    if (!st.analise) return status("Analise o vídeo primeiro para reproduzir.", "erro");
    st.tocando = true; $("#ar-play").textContent = "❚❚";
    const quadros = st.analise.linha.map(x => x.indice);
    let k = quadros.findIndex(i => i >= Number($("#ar-quadro").value));
    if (k < 0 || k >= quadros.length - 1) k = 0;
    while (st.tocando && k < quadros.length) {
      $("#ar-quadro").value = quadros[k++];
      await pedir();
    }
    parar();
  };

  const obs = new ResizeObserver(() => desenhar());
  obs.observe(canvas.parentElement);
  $("#ar-quadro").value = Math.floor(video().quadros / 2);
  controles();
  mostrarStats();
  await pedir();
  return () => { parar(); obs.disconnect(); };
}
