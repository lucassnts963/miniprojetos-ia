// Painel da bancada: máquina de completar texto (apostas, continuação, a rede por dentro e o minichat).

const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const pct = v => (v * 100).toLocaleString("pt-BR", { maximumFractionDigits: v < 0.1 ? 1 : 0 }) + "%";
const visivel = p => esc(p).replace(/ /g, "<i>·</i>").replace(/\n/g, "<i>↵</i>");   // mostra o espaço que vai no pedaço
const ultimaLinha = e => esc(String(e.message || e).split("\n").filter(Boolean).pop());

const HTML = `
<div class="ct">
  <section class="c ctrl">
    <h1>Máquina de completar texto</h1>
    <p class="dica">Uma LLM faz uma coisa só: aposta em qual pedaço de texto vem depois. Aqui está uma em miniatura, treinada do zero, para ver as apostas por dentro.</p>

    <span class="rot">Modo</span>
    <div class="seg" id="ct-modo"><button data-v="completar" class="on">Completar</button><button data-v="chat">Minichat</button></div>

    <span class="rot">Quem completa</span>
    <div class="seg" id="ct-modelo"><button data-v="rede" class="on">Rede neural</button><button data-v="contagem">Só contagem</button></div>
    <p class="dica" id="ct-dica-modelo"></p>
    <div class="linha" id="ct-linha-ordem" hidden><span class="dica">olha os últimos</span><input type="range" id="ct-ordem" min="1" max="3" value="3"><span class="ms" id="ct-ordem-v"></span></div>

    <span class="rot">Como escolhe</span>
    <div class="linha"><span class="dica" title="0 = sempre a maior aposta; mais alto = arrisca mais">ousadia</span><input type="range" id="ct-temp" min="0" max="15" value="7"><span class="ms" id="ct-temp-v"></span></div>
    <div class="linha so-completar"><span class="dica">pedaços</span><input type="range" id="ct-quantos" min="5" max="120" step="5" value="40"><span class="ms" id="ct-quantos-v"></span></div>

    <button class="btn so-completar" id="ct-gerar">Completar</button>
    <div class="linha acoes so-completar">
      <button class="btn sec" id="ct-um">Um pedaço</button>
      <button class="btn sec" id="ct-limpar">Voltar ao começo</button>
    </div>
    <button class="btn sec so-chat" id="ct-nova">Nova conversa</button>
    <div class="status" id="ct-status"></div>

    <span class="rot" id="ct-rot-exemplos"></span>
    <div class="exemplos" id="ct-exemplos"></div>
  </section>

  <section class="c texto">
    <div class="so-completar bloco">
      <div class="c-topo"><span class="rot">Escreva o começo</span></div>
      <textarea id="ct-entrada" rows="3" spellcheck="false" placeholder="Escreva o começo de uma frase…"></textarea>
    </div>
    <div class="so-chat bloco">
      <div class="c-topo"><span class="rot">Minichat da base</span><span class="dica">só sabe o que estava nos textos do treino</span></div>
      <div class="conversa" id="ct-conversa"></div>
      <form class="linha" id="ct-form">
        <input type="text" id="ct-pergunta" placeholder="Pergunte algo: O que é…? Fale sobre…" autocomplete="off">
        <button class="btn" id="ct-enviar">Enviar</button>
      </form>
    </div>
    <div class="c-topo"><span class="rot" id="ct-rot-pedacos"></span><span class="dica" id="ct-conta"></span></div>
    <div class="pedacos" id="ct-pedacos"></div>
    <p class="dica leg"><i class="q q1"></i><span id="ct-leg-meu"></span> <i class="q q2"></i>escrito pela máquina (mais forte = aposta mais segura) <span id="ct-leg-olhar"><i class="q q3"></i>para onde a rede olhou</span></p>
  </section>

  <section class="c apostas">
    <div class="c-topo"><span class="rot">As apostas para o próximo pedaço</span><span class="dica" id="ct-usados"></span></div>
    <div id="ct-apostas"></div>
    <p class="dica so-completar">Clique numa aposta para escolher você mesmo o próximo pedaço.</p>
  </section>

  <section class="c rede" id="ct-sec-rede">
    <div class="c-topo"><span class="rot">A rede por dentro</span><span class="dica" id="ct-rede-info"></span></div>
    <canvas id="ct-rede"></canvas>
    <p class="dica">De baixo para cima: os últimos pedaços do texto entram, e cada camada refina a resposta. As linhas verdes mostram para onde o último pedaço olhou em cada camada (a atenção). À direita, o palpite que a rede daria se parasse naquela camada.</p>
  </section>

  <section class="c medida" id="ct-medida"></section>
</div>`;

export async function montar(raiz, api) {
  raiz.innerHTML = `<link rel="stylesheet" href="${new URL("painel.css", import.meta.url)}">` + HTML;
  const $ = s => raiz.querySelector(s);
  const css = n => getComputedStyle(raiz).getPropertyValue(n).trim();
  const info = await api.chamar("info");
  const st = {
    modo: api.ler("modo", "completar"), modelo: api.ler("modelo", "rede"), gerado: [], vivo: true,
    ocupado: false, pendente: false, parar: false, gerando: false,
    conversa: [], contexto: "", rede: null,
  };
  const entrada = $("#ct-entrada");
  entrada.value = api.ler("texto", info.exemplos[0]);

  if (!info.pronto) {
    $(".ct").innerHTML = `<section class="c"><h1>Máquina de completar texto</h1><p class="dica">O modelo ainda não foi treinado. Na pasta do projeto, rode <code>python baixar_textos.py</code> e depois <code>python treinar.py</code>.</p></section>`;
    return;
  }

  const status = (t, c = "") => { const e = $("#ct-status"); e.className = "status " + c; e.innerHTML = t; };
  const base = () => st.modo === "chat" ? st.contexto : entrada.value;          // o texto antes do que a máquina escreveu
  const textoAtual = () => base() + st.gerado.map(g => g.pedaco).join("");
  const params = () => ({ modelo: st.modelo, ordem: +$("#ct-ordem").value, temperatura: +$("#ct-temp").value / 10 });
  const forca = p => (0.25 + 0.75 * Math.min(1, p * 1.6)).toFixed(2);

  function rotulos() {
    const o = +$("#ct-ordem").value;
    $("#ct-ordem-v").textContent = o + (o === 1 ? " pedaço" : " pedaços");
    const t = +$("#ct-temp").value / 10;
    $("#ct-temp-v").textContent = t === 0 ? "nenhuma" : t.toLocaleString("pt-BR", { minimumFractionDigits: 1 });
    $("#ct-quantos-v").textContent = $("#ct-quantos").value;
    $("#ct-linha-ordem").hidden = st.modelo !== "contagem";
    $("#ct-leg-olhar").hidden = st.modelo !== "rede";
    $("#ct-sec-rede").hidden = st.modelo !== "rede";
    $("#ct-dica-modelo").textContent = st.modelo === "rede"
      ? "Uma rede pequena, com a mesma arquitetura das LLMs. Olha o texto inteiro e pesa o que importa."
      : "Sem rede: uma tabela que conta o que costuma vir depois dos últimos pedaços. É a origem da ideia.";
    $("#ct-modelo").querySelectorAll("button").forEach(b => b.classList.toggle("on", b.dataset.v === st.modelo));
    $("#ct-modo").querySelectorAll("button").forEach(b => b.classList.toggle("on", b.dataset.v === st.modo));
    const chat = st.modo === "chat";
    raiz.querySelectorAll(".so-completar").forEach(e => { e.hidden = chat; });
    raiz.querySelectorAll(".so-chat").forEach(e => { e.hidden = !chat; });
    $("#ct-rot-pedacos").textContent = chat ? "O que a máquina realmente lê: a conversa vira um texto só" : "Como a máquina lê e continua (cada bloco é um pedaço)";
    $("#ct-leg-meu").textContent = chat ? "a conversa até aqui" : "o seu texto";
    $("#ct-rot-exemplos").textContent = chat ? "Perguntas para testar" : "Começos para testar";
    $("#ct-exemplos").innerHTML = (chat ? info.perguntas : info.exemplos).map(x => `<button class="link">${esc(x)}</button>`).join("");
  }
  for (const id of ["ordem", "temp", "quantos"]) {
    const el = $("#ct-" + id);
    el.value = api.ler(id, el.value);
    el.addEventListener("input", () => { api.gravar(id, el.value); rotulos(); if (id === "ordem") atualizar(); });
  }
  function seg(sel, chave) {
    $(sel).addEventListener("click", e => {
      const b = e.target.closest("button"); if (!b || st.gerando) return;
      st[chave] = b.dataset.v; api.gravar(chave, st[chave]);
      if (chave === "modo") st.gerado = [];
      rotulos(); atualizar();
    });
  }
  seg("#ct-modelo", "modelo"); seg("#ct-modo", "modo");

  $("#ct-exemplos").addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b || st.gerando) return;
    if (st.modo === "chat") { perguntar(b.textContent); return; }
    entrada.value = b.textContent; st.gerado = []; api.gravar("texto", entrada.value); atualizar();
  });

  // ---------- desenho ----------
  function desenharPedacos(lidos, olhar) {
    const corte = olhar ? lidos.length - olhar.length : lidos.length;      // pedaços fora da janela da rede
    const maior = olhar ? Math.max(...olhar, 1e-9) : 1;
    const nGer = st.gerado.length;
    const html = lidos.map((p, i) => {
      const ger = i >= lidos.length - nGer ? st.gerado[i - (lidos.length - nGer)] : null;
      const o = olhar && i >= corte ? olhar[i - corte] / maior : 0;
      return `<span class="p ${ger ? "ger" : "meu"}" style="${ger ? `--f:${forca(ger.p)};` : ""}--o:${o.toFixed(2)}" title="${ger ? `aposta de ${pct(ger.p)}` : ""}">${visivel(p)}</span>`;
    }).join("");
    $("#ct-pedacos").innerHTML = html || `<span class="dica">${st.modo === "chat" ? "Faça uma pergunta acima." : "Escreva um começo acima."}</span>`;
    $("#ct-conta").textContent = `${lidos.length} pedaços`;
  }

  function desenharApostas(apostas, usados) {
    const maior = Math.max(...apostas.map(a => a.p), 1e-9);
    $("#ct-apostas").innerHTML = apostas.map(a =>
      `<button class="aposta" data-p="${esc(a.pedaco)}" data-v="${a.p}"><span class="nome">${visivel(a.pedaco)}</span>` +
      `<span class="barra"><i style="width:${(a.p / maior * 100).toFixed(1)}%"></i></span><span class="ms">${pct(a.p)}</span></button>`).join("");
    $("#ct-usados").textContent = st.modelo === "contagem"
      ? (usados ? `decidiu olhando os últimos ${usados}` : "nunca viu nada parecido: chute")
      : `olhando ${usados} ${usados === 1 ? "pedaço" : "pedaços"} do texto`;
  }

  // ---------- a rede por dentro ----------
  const cRede = $("#ct-rede"), xr = cRede.getContext("2d");
  function desenharRede() {
    const d = st.rede;
    if (!d || st.modelo !== "rede") return;
    const r = window.devicePixelRatio || 1, w = cRede.clientWidth, L = d.camadas.length, n = d.pedacos.length;
    if (!w) return;
    const passoY = 46, h = 74 + L * passoY;
    cRede.style.height = h + "px"; cRede.width = w * r; cRede.height = h * r;
    xr.setTransform(r, 0, 0, r, 0, 0); xr.clearRect(0, 0, w, h);
    const mono = css("--mono") || "monospace", mute = css("--mute") || "#888", fg = css("--fg") || "#eee", red = css("--red") || "#E5484D";
    const esq = 86, dir = Math.min(230, w * 0.3), x = j => esq + (w - esq - dir) * (n === 1 ? 0.5 : j / (n - 1));
    const y = l => h - 46 - l * passoY;                         // l = 0 é a entrada; 1..L são as camadas
    $("#ct-rede-info").textContent = `${L} camadas · ${d.cfg.cabecas} cabeças de atenção · ${d.parametros.toLocaleString("pt-BR")} números ajustáveis`;

    xr.textBaseline = "middle"; xr.font = `12px ${mono}`;
    xr.fillStyle = mute; xr.textAlign = "left";
    xr.fillText("pedaços", 0, y(0));
    for (let l = 1; l <= L; l++) xr.fillText(`camada ${l}`, 0, y(l));
    // o caminho de cada pedaço para cima (cada posição passa por todas as camadas)
    xr.strokeStyle = "rgba(255,255,255,.06)"; xr.lineWidth = 1; xr.beginPath();
    for (let j = 0; j < n; j++) { xr.moveTo(x(j), y(0) - 12); xr.lineTo(x(j), y(L)); }
    xr.stroke();
    // a atenção do último pedaço, camada por camada
    for (let l = 1; l <= L; l++) {
      const o = d.camadas[l - 1].olhar, maior = Math.max(...o, 1e-9);
      for (let j = 0; j < n; j++) {
        const a = o[j] / maior;
        if (a < 0.04) continue;
        xr.strokeStyle = `rgba(88,214,141,${(0.12 + 0.85 * a).toFixed(2)})`; xr.lineWidth = 0.6 + 3.2 * a;
        xr.beginPath(); xr.moveTo(x(n - 1), y(l));
        xr.quadraticCurveTo((x(j) + x(n - 1)) / 2, y(l) - passoY * 0.18, x(j), y(l - 1) - (l === 1 ? 12 : 0)); xr.stroke();
      }
    }
    for (let l = 1; l <= L; l++) for (let j = 0; j < n; j++) {
      const ultimo = j === n - 1;
      xr.fillStyle = ultimo ? red : "#3a3d48";
      xr.beginPath(); xr.arc(x(j), y(l), ultimo ? 7 : 4, 0, 7); xr.fill();
    }
    // os pedaços de entrada
    xr.textAlign = "center"; xr.font = `13px ${mono}`;
    const larg = Math.max(34, (w - esq - dir) / Math.max(n - 1, 1) - 6);
    d.pedacos.forEach((p, j) => {
      let t = p.replace(/\n/g, "↵").trim() || "·";
      while (t.length > 1 && xr.measureText(t).width > larg) t = t.slice(0, -2) + "…";
      xr.fillStyle = j === n - 1 ? fg : mute;
      xr.fillText(t, x(j), y(0));
    });
    // o palpite de cada camada
    xr.textAlign = "left";
    d.camadas.forEach((c, i) => {
      const yy = y(i + 1), x0 = w - dir + 26, final = i === L - 1;
      xr.strokeStyle = "rgba(255,255,255,.14)"; xr.lineWidth = 1; xr.beginPath(); xr.moveTo(x(n - 1) + 10, yy); xr.lineTo(x0 - 8, yy); xr.stroke();
      xr.globalAlpha = 0.35 + 0.65 * Math.min(1, c.p * 2.5);
      xr.font = `${final ? 600 : 400} 14px ${mono}`; xr.fillStyle = final ? red : fg;
      xr.fillText((c.palpite.replace(/\n/g, "↵").trim() || "·").slice(0, 14), x0, yy);
      xr.globalAlpha = 1; xr.font = `11px ${mono}`; xr.fillStyle = mute; xr.textAlign = "right";
      xr.fillText(pct(c.p), w, yy); xr.textAlign = "left";
    });
    xr.font = `11px ${mono}`; xr.fillStyle = mute;
    xr.fillText("palpite se parasse aqui", w - dir + 26, y(L) - 24);
  }
  const obs = new ResizeObserver(desenharRede);
  obs.observe(cRede);

  // uma consulta por vez; se o texto mudar no meio, refaz ao terminar
  async function atualizar() {
    if (st.ocupado) { st.pendente = true; return; }
    st.ocupado = true;
    try {
      do {
        st.pendente = false;
        const r = await api.chamar("proximo", { texto: textoAtual(), ...params() });
        desenharPedacos(r.pedacos, r.olhar);
        desenharApostas(r.apostas, r.usados);
        st.rede = r.rede; desenharRede();
      } while (st.pendente && st.vivo);
      if (!st.gerando) status("");
    } catch (e) { status(ultimaLinha(e), "erro"); }
    st.ocupado = false;
  }

  entrada.addEventListener("input", () => { st.gerado = []; api.gravar("texto", entrada.value); atualizar(); });

  // mostra pedaço por pedaço, com as apostas de cada um; aoPedaco recebe o pedaço escolhido
  async function animar(passos, pausa, aoPedaco) {
    for (const passo of passos) {
      if (st.parar || !st.vivo) break;
      desenharApostas(passo.apostas, passo.usados);
      const escolhida = [...raiz.querySelectorAll(".aposta")].find(b => b.dataset.p === passo.pedaco);
      if (escolhida) escolhida.classList.add("on");
      await new Promise(ok => setTimeout(ok, pausa));
      st.gerado.push({ pedaco: passo.pedaco, p: passo.p });
      $("#ct-pedacos").insertAdjacentHTML("beforeend",
        `<span class="p ger" style="--f:${forca(passo.p)};--o:0" title="aposta de ${pct(passo.p)}">${visivel(passo.pedaco)}</span>`);
      $("#ct-conta").textContent = `${raiz.querySelectorAll("#ct-pedacos .p").length} pedaços`;
      if (aoPedaco) aoPedaco(passo);
    }
  }

  async function gerar(quantos) {
    if (st.gerando) { st.parar = true; return; }
    st.gerando = true; st.parar = false;
    $("#ct-gerar").textContent = "Parar";
    try {
      const r = await api.chamar("gerar", { texto: textoAtual(), quantos, ...params() });
      await animar(r.passos, quantos === 1 ? 250 : 110);
    } catch (e) { status(ultimaLinha(e), "erro"); }
    st.gerando = false;
    $("#ct-gerar").textContent = "Completar";
    atualizar();
  }
  $("#ct-gerar").addEventListener("click", () => gerar(+$("#ct-quantos").value));
  $("#ct-um").addEventListener("click", () => gerar(1));
  $("#ct-limpar").addEventListener("click", () => { st.parar = true; st.gerado = []; atualizar(); });
  $("#ct-apostas").addEventListener("click", e => {          // o usuário escolhe o próximo pedaço
    const b = e.target.closest(".aposta"); if (!b || st.gerando || st.modo === "chat") return;
    st.gerado.push({ pedaco: b.dataset.p, p: +b.dataset.v });
    atualizar();
  });

  // ---------- minichat ----------
  function desenharConversa() {
    const c = $("#ct-conversa");
    c.innerHTML = st.conversa.length ? st.conversa.map(([q, a]) =>
      `<div class="fala eu">${esc(q)}</div><div class="fala ia"><b>IA</b><span>${a === null ? '<span class="spin"></span>' : esc(a)}</span></div>`).join("")
      : `<p class="dica vazio">Pergunte sobre um assunto da base (indústria, manutenção, logística, energia, saúde…). A rede é minúscula: acerta o jeito de responder antes de acertar o conteúdo, e inventa com a mesma segurança com que acerta.</p>`;
    c.scrollTop = c.scrollHeight;
  }

  async function perguntar(pergunta) {
    pergunta = pergunta.trim();
    if (!pergunta || st.gerando) return;
    st.gerando = true; st.parar = false;
    $("#ct-enviar").disabled = true; $("#ct-pergunta").value = "";
    const historico = st.conversa.map(x => [...x]);
    st.conversa.push([pergunta, null]); desenharConversa();
    try {
      const r = await api.chamar("chat", { pergunta, historico, ...params() });
      st.contexto = r.contexto; st.gerado = [];
      const lidos = await api.chamar("proximo", { texto: r.contexto, ...params() });
      desenharPedacos(lidos.pedacos, lidos.olhar);
      st.rede = lidos.rede; desenharRede();
      const troca = st.conversa[st.conversa.length - 1];
      troca[1] = "";
      await animar(r.passos, 70, passo => {
        troca[1] += passo.pedaco;
        const bolha = raiz.querySelector("#ct-conversa .fala.ia:last-child span");
        if (bolha) bolha.textContent = troca[1].trim();
        $("#ct-conversa").scrollTop = $("#ct-conversa").scrollHeight;
      });
      troca[1] = troca[1].trim() || "(sem resposta)";
      desenharConversa();
    } catch (e) { st.conversa.pop(); desenharConversa(); status(ultimaLinha(e), "erro"); }
    st.gerando = false;
    $("#ct-enviar").disabled = false; $("#ct-pergunta").focus();
    atualizar();
  }
  $("#ct-form").addEventListener("submit", e => { e.preventDefault(); perguntar($("#ct-pergunta").value); });
  $("#ct-nova").addEventListener("click", () => {
    if (st.gerando) { st.parar = true; return; }
    st.conversa = []; st.contexto = ""; st.gerado = []; desenharConversa(); atualizar();
  });

  // ---------- a medida ----------
  const r = info.resultado;
  if (r) {
    const linhas = [["Só contagem, último pedaço", r.contagem["1"]], ["Só contagem, últimos 2", r.contagem["2"]],
                    ["Só contagem, últimos 3", r.contagem["3"]], ["Rede neural", r.rede]];
    $("#ct-medida").innerHTML = `<span class="rot">Medido em texto que nenhum dos dois viu</span>
      <table><tr><th></th><th>acerta de primeira</th><th>entre as cinco primeiras</th></tr>
      ${linhas.map(([n, v]) => `<tr${n === "Rede neural" ? ' class="on"' : ""}><td>${n}</td><td>${pct(v.top1)}</td><td>${pct(v.top5)}</td></tr>`).join("")}</table>
      <p class="dica">Treinada em ${r.pedacos_treino.toLocaleString("pt-BR")} pedaços de artigos da Wikipédia em português${r.conversas ? ` e em ${r.conversas.toLocaleString("pt-BR")} conversas montadas a partir deles` : ""}. A rede tem ${r.rede.parametros.toLocaleString("pt-BR")} números ajustáveis; as LLMs comerciais têm muitas ordens de grandeza a mais, mas a tarefa é a mesma.</p>`;
  }

  rotulos();
  desenharConversa();
  atualizar();
  return () => { st.vivo = false; st.parar = true; obs.disconnect(); };
}
