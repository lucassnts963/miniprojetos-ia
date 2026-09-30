// Painel da bancada: triagem de ordens de manutenção, classificando enquanto você digita.

const COR_PRIO = { URGENTE: "#E5484D", ALTA: "#F0963C", "MÉDIA": "#E1C850", BAIXA: "#8C8CA0" };
const RED = "#E5484D";

const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const pct = v => `${Math.round(v * 100)}%`;
const rgba = (hex, a) => {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${n >> 16}, ${(n >> 8) & 255}, ${n & 255}, ${a})`;
};

const HTML = `
<div class="tri">
  <section class="c entrada">
    <div class="c-topo">
      <div><h1>Triagem de ordens de manutenção</h1><span class="dica">Escreva do jeito que o operador escreveria. A rede decide a cada tecla.</span></div>
      <span class="ms" id="ms"></span>
    </div>
    <textarea id="texto" rows="1" spellcheck="false" placeholder="ex.: motor da bomba 2 cheirando queimado"></textarea>
    <div class="exemplos" id="exemplos"></div>
  </section>

  <section class="c decisao equipe">
    <span class="rot">Equipe</span>
    <div class="grande" id="eq-nome">—</div>
    <div class="conf" id="eq-conf">&nbsp;</div>
    <div class="barras" id="eq-barras"></div>
  </section>

  <section class="c decisao prio">
    <span class="rot">Prioridade</span>
    <div class="grande" id="pr-nome">—</div>
    <div class="conf" id="pr-conf">&nbsp;</div>
    <div class="barras" id="pr-barras"></div>
  </section>

  <section class="c termos">
    <span class="rot">O que a rede enxergou</span>
    <div class="dica" style="margin-top:6px">palavras e pares que empurraram a decisão (pedaços somados na palavra)</div>
    <div class="chips" id="termos"></div>
    <span class="rot">Palavras que ela nunca viu</span>
    <div class="chips" id="desconhecidas"></div>
  </section>

  <section class="c leitura">
    <div class="c-topo">
      <span class="rot">O que pesou na decisão</span>
      <div class="seg" id="seg"><button data-m="eq" class="on">equipe</button><button data-m="pr">prioridade</button></div>
    </div>
    <p class="frase" id="frase"></p>
    <div class="legenda">
      <span><i id="leg-cor"></i>puxou para a decisão</span>
      <span><i style="border:1px dashed var(--neg)"></i>puxou contra</span>
      <span>passe o mouse numa palavra para ver quanto</span>
    </div>
  </section>

  <section class="c rede">
    <div class="c-topo"><span class="rot">Dentro da rede</span><span class="dica">termos → camada oculta → saídas escolhidas</span></div>
    <svg id="grafo" viewBox="0 0 720 400" role="img" aria-label="Diagrama da rede neural"></svg>
  </section>

  <section class="c ensinar">
    <span class="rot">Ensinar a rede</span>
    <p class="dica" style="margin:8px 0 0">Errou? Escolha o certo e salve. O exemplo entra no próximo treino.</p>
    <div class="linha">
      <select id="sel-eq"></select>
      <select id="sel-pr"></select>
    </div>
    <div class="linha">
      <button class="btn" id="salvar">Salvar exemplo</button>
      <button class="btn sec" id="treinar">Retreinar e medir</button>
    </div>
    <div class="linha"><span class="status" id="status"></span></div>
  </section>

  <section class="c hist">
    <div class="c-topo"><span class="rot">Testados</span><button class="link" id="limpar">limpar</button></div>
    <ul id="hist"></ul>
  </section>

  <footer class="rodape" id="rodape"></footer>
</div>`;

export async function montar(raiz, api) {
  raiz.innerHTML = `<link rel="stylesheet" href="${new URL("painel.css", import.meta.url)}">` + HTML;
  const $ = s => raiz.querySelector(s);
  const el = {
    texto: $("#texto"), ms: $("#ms"), exemplos: $("#exemplos"),
    eqNome: $("#eq-nome"), eqConf: $("#eq-conf"), eqBarras: $("#eq-barras"),
    prNome: $("#pr-nome"), prConf: $("#pr-conf"), prBarras: $("#pr-barras"),
    termos: $("#termos"), desconhecidas: $("#desconhecidas"), frase: $("#frase"), seg: $("#seg"), legCor: $("#leg-cor"),
    grafo: $("#grafo"), selEq: $("#sel-eq"), selPr: $("#sel-pr"), salvar: $("#salvar"), treinar: $("#treinar"),
    status: $("#status"), hist: $("#hist"), limpar: $("#limpar"), rodape: $("#rodape"),
  };

  let info = await api.chamar("info");
  let ultimo = null;
  let modo = api.ler("modo", "eq");
  let seq = 0;
  let rotuloMexido = false;
  let historico = api.ler("hist", []);

  el.selEq.innerHTML = info.equipes.map(e => `<option>${esc(e)}</option>`).join("");
  el.selPr.innerHTML = info.prioridades.map(p => `<option>${esc(p)}</option>`).join("");
  el.exemplos.innerHTML = info.exemplos.map(t => `<button type="button">${esc(t)}</button>`).join("");
  for (const b of el.seg.querySelectorAll("button")) b.classList.toggle("on", b.dataset.m === modo);

  // ---------- desenho ----------
  function barras(alvo, nomes, probs, cor) {
    const top = probs.indexOf(Math.max(...probs));
    alvo.innerHTML = nomes.map((n, i) => {
      const c = cor(n, i === top);
      return `<div class="barra ${i === top ? "top" : ""}"><span class="n">${esc(n)}</span>
        <span class="trilho"><span class="enche" style="width:${probs[i] * 100}%;background:${c}"></span></span>
        <span class="v">${pct(probs[i])}</span></div>`;
    }).join("");
  }

  function desenharDecisao(r) {
    if (!r || r.vazio) {
      el.eqNome.textContent = "—";
      el.prNome.textContent = "—";
      el.eqConf.innerHTML = el.prConf.innerHTML = "&nbsp;";
      barras(el.eqBarras, info.equipes, info.equipes.map(() => 0), () => "#3a3a42");
      barras(el.prBarras, info.prioridades, info.prioridades.map(() => 0), () => "#3a3a42");
      return;
    }
    const ce = Math.max(...r.prob_equipe), cp = Math.max(...r.prob_prioridade);
    el.eqNome.textContent = r.equipe;
    el.eqConf.textContent = `${pct(ce)} de confiança${ce < 0.6 ? " · na dúvida" : ""}`;
    el.prNome.innerHTML = `<span class="chip-prio" style="background:${COR_PRIO[r.prioridade]}">${esc(r.prioridade)}</span>`;
    el.prConf.textContent = `${pct(cp)} de confiança${cp < 0.5 ? " · na dúvida" : ""}`;
    if (!r.n_termos_ativos) {
      el.eqConf.textContent = el.prConf.textContent = "nenhuma palavra conhecida: é só um chute";
    }
    barras(el.eqBarras, info.equipes, r.prob_equipe, (n, top) => (top ? RED : "#3a3a42"));
    barras(el.prBarras, info.prioridades, r.prob_prioridade, (n, top) => rgba(COR_PRIO[n], top ? 1 : 0.4));
  }

  function desenharLeitura(r) {
    const cor = modo === "eq" ? RED : COR_PRIO[r?.prioridade] || RED;
    el.legCor.style.background = rgba(cor, 0.55);
    if (!r || r.vazio) {
      el.frase.innerHTML = `<span style="color:var(--mute)">Digite um chamado para ver quais palavras decidiram.</span>`;
      return;
    }
    const vals = r.tokens.map(t => t[modo]).filter(v => v != null);
    const escala = Math.max(0.05, ...vals.map(Math.abs));
    const alvo = modo === "eq" ? r.equipe : r.prioridade;
    el.frase.innerHTML = r.tokens.map(t => {
      const v = t[modo];
      if (v == null) return esc(t.t);
      const a = v / escala;
      const dica = `${v >= 0 ? "a favor de" : "contra"} ${alvo} (peso ${Math.round(Math.abs(a) * 100)}% da palavra mais forte)`;
      if (a > 0.08) return `<span class="w" title="${esc(dica)}" style="background:${rgba(cor, 0.1 + 0.55 * a)}">${esc(t.t)}</span>`;
      if (a < -0.15) return `<span class="w neg" title="${esc(dica)}">${esc(t.t)}</span>`;
      return `<span class="w" title="${esc(dica)}">${esc(t.t)}</span>`;
    }).join("");
  }

  function desenharTermos(r) {
    if (!r || r.vazio) {
      el.termos.innerHTML = el.desconhecidas.innerHTML = `<span class="dica">—</span>`;
      return;
    }
    el.termos.innerHTML = r.termos.map(t =>
      `<span class="termo" title="${esc(t.tipo)} · peso ${t.peso}" style="background:linear-gradient(90deg, ${rgba(RED, 0.22)} ${t.peso * 100}%, transparent 0)">${esc(t.termo)}<em>${esc(t.tipo)}</em></span>`
    ).join("") || `<span class="dica">nada que empurre a decisão</span>`;
    el.desconhecidas.innerHTML = r.desconhecidas.length
      ? r.desconhecidas.map(w => `<span class="termo nunca">${esc(w)}</span>`).join("") +
        `<div class="dica" style="width:100%;margin-top:6px">Mesmo sem conhecer a palavra, a rede aproveita pedaços dela que já viu (ex.: "cheirando" → "chei").</div>`
      : `<span class="dica">nenhuma: todas já apareceram no treino</span>`;
  }

  function desenharGrafo(r) {
    const g = r && !r.vazio ? r.grafo : null;
    const nH = info.n_oculta;
    const yH = j => 40 + j * (345 / Math.max(1, nH - 1));
    const termos = g ? g.termos : [];
    const yT = i => (termos.length <= 1 ? 212 : 50 + i * (325 / (termos.length - 1)));
    const yE = k => 70 + k * 30;
    const yP = k => 262 + k * 30;
    const curva = (x1, y1, x2, y2) => {
      const m = (x1 + x2) / 2;
      return `M${x1},${y1} C${m},${y1} ${m},${y2} ${x2},${y2}`;
    };
    let s = `
      <text x="196" y="18" text-anchor="end" class="rot-grupo">TERMOS</text>
      <text x="380" y="18" text-anchor="middle" class="rot-grupo">OCULTA</text>
      <text x="552" y="52" class="rot-grupo">EQUIPE</text>
      <text x="552" y="244" class="rot-grupo">PRIORIDADE</text>`;
    if (g) {
      const e = info.equipes.indexOf(r.equipe), p = info.prioridades.indexOf(r.prioridade);
      for (const [a, b, w] of g.a1) {
        s += `<path d="${curva(206, yT(a), 375, yH(b))}" fill="none" stroke="${RED}" stroke-opacity="${0.12 + 0.6 * w}" stroke-width="${0.6 + 2.2 * w}"/>`;
      }
      for (const [j, w] of g.ae) {
        s += `<path d="${curva(385, yH(j), 552, yE(e))}" fill="none" stroke="${RED}" stroke-opacity="${0.12 + 0.6 * w}" stroke-width="${0.6 + 2.4 * w}"/>`;
      }
      for (const [j, w] of g.ap) {
        s += `<path d="${curva(385, yH(j), 552, yP(p))}" fill="none" stroke="${COR_PRIO[r.prioridade]}" stroke-opacity="${0.12 + 0.6 * w}" stroke-width="${0.6 + 2.4 * w}"/>`;
      }
      termos.forEach((t, i) => {
        s += `<circle cx="200" cy="${yT(i)}" r="5" fill="${RED}"/>`;
        s += `<text x="190" y="${yT(i) + 4}" text-anchor="end">${esc(t.length > 22 ? t.slice(0, 21) + "…" : t)}</text>`;
      });
    }
    for (let j = 0; j < nH; j++) {
      const a = g ? g.oculta[j] : 0;
      s += `<circle cx="380" cy="${yH(j)}" r="4.4" fill="${a > 0 ? rgba(RED, 0.2 + 0.8 * a) : "#26262c"}" stroke="${a > 0.6 ? "#F08A8D" : "none"}"/>`;
    }
    info.equipes.forEach((n, k) => {
      const v = g ? r.prob_equipe[k] : 0;
      const top = g && n === r.equipe;
      s += `<circle cx="552" cy="${yE(k)}" r="7" fill="${v > 0.02 ? rgba(RED, 0.15 + 0.85 * v) : "#26262c"}" stroke="${top ? "#fff" : "none"}" stroke-width="1.5"/>`;
      s += `<text x="566" y="${yE(k) + 4}" class="rot-saida" style="fill:${top ? "var(--fg)" : "var(--mute)"}">${esc(n)}${g && !window.bancada?.video ? ` · ${pct(v)}` : ""}</text>`;
    });
    info.prioridades.forEach((n, k) => {
      const v = g ? r.prob_prioridade[k] : 0;
      const top = g && n === r.prioridade;
      s += `<circle cx="552" cy="${yP(k)}" r="7" fill="${v > 0.02 ? rgba(COR_PRIO[n], 0.15 + 0.85 * v) : "#26262c"}" stroke="${top ? "#fff" : "none"}" stroke-width="1.5"/>`;
      s += `<text x="566" y="${yP(k) + 4}" class="rot-saida" style="fill:${top ? "var(--fg)" : "var(--mute)"}">${esc(n)}${g && !window.bancada?.video ? ` · ${pct(v)}` : ""}</text>`;
    });
    el.grafo.innerHTML = s;
  }

  function desenharRodape() {
    const m = info.metricas || {};
    const med = m.acc_equipe != null
      ? `validação cruzada: equipe <b>${pct(m.acc_equipe)}</b> · prioridade <b>${pct(m.acc_prioridade)}</b> · prioridade com até um nível de diferença <b>${pct(m.prioridade_1_nivel)}</b>`
      : "sem medição (rode Retreinar e medir)";
    el.rodape.innerHTML = `
      <span><b>${info.n_exemplos}</b> exemplos no treino${info.n_correcoes ? ` (<b>${info.n_correcoes}</b> seus)` : ""}</span>
      <span><b>${info.n_termos.toLocaleString("pt-BR")}</b> termos</span>
      <span><b>${info.n_parametros.toLocaleString("pt-BR")}</b> parâmetros</span>
      <span>${med}</span>`;
  }

  function desenharHist() {
    el.hist.innerHTML = historico.length
      ? historico.map((h, i) => `<li data-i="${i}"><span class="cor" style="background:${COR_PRIO[h.prioridade]}"></span>
          <span><div class="t">${esc(h.texto)}</div><div class="s">${esc(h.equipe)} · ${esc(h.prioridade)}${h.corrigido ? " · ensinado" : ""}</div></span></li>`).join("")
      : `<li class="nada" style="cursor:default;background:none;grid-template-columns:1fr">Enter guarda o chamado aqui.</li>`;
  }

  function desenhar(r) {
    ultimo = r;
    desenharDecisao(r);
    desenharLeitura(r);
    desenharTermos(r);
    desenharGrafo(r);
    if (r && !r.vazio && !rotuloMexido) {
      el.selEq.value = r.equipe;
      el.selPr.value = r.prioridade;
    }
    el.ms.innerHTML = r && !r.vazio && r._ms != null ? `decidido em <b>${r._ms} ms</b> · ${r.n_termos_ativos} termos ativos · sem chamar nenhuma API` : "";
  }

  // ---------- ações ----------
  async function classificar() {
    const meu = ++seq;
    try {
      const r = await api.chamar("classificar", { texto: el.texto.value });
      if (meu === seq) desenhar(r);
    } catch (e) {
      if (meu === seq) status(e.message, "erro");
    }
  }

  // classifica a cada tecla: se já tem um pedido em andamento, roda de novo quando ele voltar
  // (com o texto mais recente), em vez de esperar a pessoa parar de digitar
  let emAndamento = false;
  let pendente = false;
  async function agendar() {
    if (emAndamento) { pendente = true; return; }
    emAndamento = true;
    await classificar();
    emAndamento = false;
    if (pendente) { pendente = false; agendar(); }
  }

  function ajustarAltura() {
    el.texto.style.height = "auto";
    el.texto.style.height = el.texto.scrollHeight + 2 + "px";
  }

  function guardar(extra = {}) {
    const texto = el.texto.value.trim();
    if (!texto || !ultimo || ultimo.vazio) return;
    historico = [{ texto, equipe: ultimo.equipe, prioridade: ultimo.prioridade, ...extra },
      ...historico.filter(h => h.texto !== texto)].slice(0, 30);
    api.gravar("hist", historico);
    desenharHist();
  }

  function status(msg, tipo = "") {
    el.status.className = `status ${tipo}`;
    el.status.innerHTML = msg;
  }

  function usar(texto) {
    el.texto.value = texto;
    rotuloMexido = false;
    ajustarAltura();
    el.texto.focus();
    classificar().then(() => guardar());
  }

  el.texto.addEventListener("input", () => { rotuloMexido = false; ajustarAltura(); agendar(); });
  el.texto.addEventListener("keydown", ev => {
    if (ev.key === "Enter" && !ev.shiftKey) { ev.preventDefault(); guardar(); }
  });
  el.exemplos.addEventListener("click", ev => { if (ev.target.tagName === "BUTTON") usar(ev.target.textContent); });
  el.hist.addEventListener("click", ev => {
    const li = ev.target.closest("li[data-i]");
    if (li) usar(historico[+li.dataset.i].texto);
  });
  el.limpar.onclick = () => { historico = []; api.gravar("hist", historico); desenharHist(); };
  el.seg.addEventListener("click", ev => {
    const m = ev.target.dataset?.m;
    if (!m) return;
    modo = m;
    api.gravar("modo", modo);
    for (const b of el.seg.querySelectorAll("button")) b.classList.toggle("on", b.dataset.m === modo);
    desenharLeitura(ultimo);
  });
  el.selEq.onchange = el.selPr.onchange = () => { rotuloMexido = true; };

  el.salvar.onclick = async () => {
    const texto = el.texto.value.trim();
    if (!texto) return status("Escreva um chamado primeiro.", "erro");
    try {
      const r = await api.chamar("corrigir", { texto, equipe: el.selEq.value, prioridade: el.selPr.value });
      const acertou = ultimo && el.selEq.value === ultimo.equipe && el.selPr.value === ultimo.prioridade;
      guardar({ equipe: el.selEq.value, prioridade: el.selPr.value, corrigido: true });
      info.n_correcoes = r.n_correcoes;
      status(`Salvo${acertou ? " (confirmando o acerto)" : ""}. Você já ensinou <b>${r.n_correcoes}</b> exemplo(s). Retreine para a rede aprender.`, "ok");
    } catch (e) {
      status(e.message, "erro");
    }
  };

  el.treinar.onclick = async () => {
    const antes = info.metricas || {};
    el.treinar.disabled = el.salvar.disabled = true;
    status(`<span class="spin"></span>Treinando e medindo com validação cruzada… (leva uns dois minutos)`);
    try {
      info = await api.chamar("retreinar");
      const m = info.metricas;
      const dif = (a, b) => (b == null ? "" : ` (antes ${pct(b)})`);
      status(`Pronto. Equipe <b>${pct(m.acc_equipe)}</b>${dif(m.acc_equipe, antes.acc_equipe)} · prioridade <b>${pct(m.acc_prioridade)}</b>${dif(m.acc_prioridade, antes.acc_prioridade)}`, "ok");
      desenharRodape();
      classificar();
    } catch (e) {
      status(e.message, "erro");
    } finally {
      el.treinar.disabled = el.salvar.disabled = false;
    }
  };

  desenhar(null);
  desenharHist();
  desenharRodape();
  el.texto.focus();
  // ?texto=... na URL abre já com um chamado (bom para compartilhar um caso)
  const inicial = new URLSearchParams(location.search).get("texto");
  if (inicial) usar(inicial);

  return () => { pendente = false; };
}
