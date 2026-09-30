import io

p = "render.py"
s = io.open(p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


# --- cues vindos da narração ---
rep('''# ---------------- cenas ----------------
SCENES = []''', '''# ---------------- cenas ----------------
SCENES = []
import json as _json
_TIMING_PATH = os.path.join(HERE, "..", "narr", "timing.json")
TIMING = _json.load(open(_TIMING_PATH, encoding="utf-8"))["scenes"] if os.path.exists(_TIMING_PATH) else {}
_CUR = {"cues": {}, "dur": 0}


def C(name, default):
    """Momento (s) em que a narração diz a frase ligada a este cue; senão o padrão."""
    return _CUR["cues"].get(name, default)''')
rep('''        SCENES.append(dict(name=name, dur=dur, fn=fn, chapter=chapter))''',
    '''        tm = TIMING.get(name, {})
        SCENES.append(dict(name=name, dur=tm.get("dur", dur), fn=fn, chapter=chapter, cues=tm.get("cues", {})))''')
rep('''    content = pygame.Surface((W, H), pygame.SRCALPHA)
    sc["fn"](content, t)''', '''    content = pygame.Surface((W, H), pygame.SRCALPHA)
    _CUR["cues"] = sc["cues"]
    _CUR["dur"] = sc["dur"]
    sc["fn"](content, t)''')

# estrutura
rep('''        hl = grp == 2 and t > 5.5''', '''        hl = grp == 2 and t > C("hl", 5.5)''')
rep('''    b = appear(t, 7.5)
    if b > 0:''', '''    fl = C("flow", 7.5)
    b = appear(t, fl)
    if b > 0:''')
rep('''            ca = appear(t, 7.5 + i * 0.5)''', '''            ca = appear(t, fl + i * 0.5)''')
rep('''             (120, 890), alpha=appear(t, 10))''', '''             (120, 890), alpha=appear(t, fl + 2.5))''')

# sensores
rep('''    marks = [(0, None), (4.0, (41, 49)), (10.0, (51, 51)), (15.0, (52, 52))]''',
    '''    cp, cd, cc, cr = C("perigo", 4.0), C("direcao", 10.0), C("comida", 15.0), C("relativo", 20.0)
    marks = [(0, None), (cp, (41, 49)), (cd, (51, 51)), (cc, (52, 52))]''')
rep('''        (1.5, "11 entradas, todas 0 ou 1",''', '''        (C("n1", 1.5), "11 entradas, todas 0 ou 1",''')
rep('''        (4.0, "3 × perigo",''', '''        (cp, "3 × perigo",''')
rep('''        (10.0, "4 × direção atual",''', '''        (cd, "4 × direção atual",''')
rep('''        (15.0, "4 × onde está a comida",''', '''        (cc, "4 × onde está a comida",''')
rep('''        (20.0, "relativo = portável",''', '''        (cr, "relativo = portável",''')
rep('''    hl = active_hl(t, [(0, None), (4.0, 0), (10.0, 1), (15.0, 2), (20.0, None)])''',
    '''    hl = active_hl(t, [(0, None), (cp, 0), (cd, 1), (cc, 2), (cr, None)])''')

# cérebro
rep('''    marks = [(0, None), (2.0, (58, 64)), (8.0, (66, 70)), (14.0, (78, 81))]''',
    '''    ci, cf, cpar, cm = C("init", 2.0), C("forward", 8.0), C("params", 16.0), C("mut", 14.0)
    marks = [(0, None), (ci, (58, 64)), (cf, (66, 70)), (cm, (78, 81))]''')
rep('''    hl_layer = active_hl(t, [(0, None), (2.0, 1), (8.0, 3), (14.0, None)])''',
    '''    hl_layer = active_hl(t, [(0, None), (ci, 1), (cf, 3), (cpar, None)])''')
rep('''    a = appear(t, 16.0)''', '''    a = appear(t, cpar)''')
rep('''"center", appear(t, 17.5))''', '''"center", appear(t, max(cm, cpar + 2.5)))''')
rep('''    notes_small = {2.0: "3 camadas densas, init de He", 8.0: "forward = 2× ReLU + logits; argmax decide",
                   14.0: "mutate(): ruído gaussiano em ~10% dos pesos"}''',
    '''    notes_small = {ci: "3 camadas densas, init de He", cf: "forward = 2× ReLU + logits; argmax decide"}''')
rep('''    if cur and t < 16:''', '''    if cur and t < cpar:''')

# evolve()
rep('''    marks = [(0, None), (1.5, (229, 233)), (5.5, (242, 244)), (9.5, (246, 249))]''',
    '''    ca_, ce, cfi, ccr = C("aval", 1.5), C("elite", 5.5), C("filhos", 9.5), C("cross", 13.0)
    marks = [(0, None), (ca_, (229, 233)), (ce, (242, 244)), (cfi, (246, 249))]''')
rep('''    marks2 = [(0, None), (13.0, (280, 289))]''', '''    marks2 = [(0, None), (ccr, (280, 289))]''')
rep('''        (1.5, "avaliação justa",''', '''        (ca_, "avaliação justa",''')
rep('''        (5.5, "elitismo",''', '''        (ce, "elitismo",''')
rep('''        (9.5, "filhos",''', '''        (cfi, "filhos",''')
rep('''        (13.0, "crossover uniforme",''', '''        (ccr, "crossover uniforme",''')

# fitness
rep('''    marks = [(0, None), (1.5, (172, 173)), (6.0, (163, 166)), (10.5, (168, 170))]''',
    '''    cco, csh, cfo, cpr = C("comer", 1.5), C("shaping", 6.0), C("fome", 10.5), C("prof", 12.5)
    marks = [(0, None), (cco, (172, 173)), (csh, (163, 166)), (cfo, (168, 170))]''')
rep('''        (1.5, "comer é o que mais vale",''', '''        (cco, "comer é o que mais vale",''')
rep('''        (6.0, "reward shaping",''', '''        (csh, "reward shaping",''')
rep('''        (10.5, "morte por fome",''', '''        (cfo, "morte por fome",''')
rep('''         (100, 800), alpha=appear(t, 12.5))''', '''         (100, 800), alpha=appear(t, cpr))''')

# treino
rep('''        _feed["train"] = VideoFeed(11, 1404, 1404 / 25.0, "968:692:476:254", 700)
    img = _feed["train"].frame()''', '''        _feed["train"] = VideoFeed(11, 1404, 1404 / _CUR["dur"], "968:692:476:254", 700)
    img = _feed["train"].frame()''')
rep('''"// 06 · o treino — 100 gerações em 25 s"''', '''f"// 06 · o treino — 100 gerações em {_CUR['dur']:.0f} s"''')
rep('''        (1.0, "o painel mostra as 15 melhores",''', '''        (C("n1", 1.0), "o painel mostra as 15 melhores",''')
rep('''        (6.0, "começo: caos",''', '''        (C("caos", 6.0), "começo: caos",''')
rep('''        (12.0, "meio: estratégia emergente",''', '''        (C("estrategia", 12.0), "meio: estratégia emergente",''')
rep('''        (18.0, "fim: recorde de 58 comidas",''', '''        (C("fim", 18.0), "fim: recorde de 58 comidas",''')

# mente
rep('''    slow_until, slow_rate, fast_rate = 16.0, 2.2, 11.0''', '''    slow_until, slow_rate, fast_rate = C("fast", 16.0), 2.2, 11.0''')

# jogo real
rep('''    marks = [(0, None), (1.5, (464, 471)), (7.0, (473, 474))]''',
    '''    cv, cmm, cg = C("conv", 1.5), C("mesmo", 7.0), C("game", 11.5)
    marks = [(0, None), (cv, (464, 471)), (cmm, (473, 474))]''')
rep('''        (1.5, "converte pixels em grade",''', '''        (cv, "converte pixels em grade",''')
rep('''        (7.0, "mesmo build_state do treino",''', '''        (cmm, "mesmo build_state do treino",''')
rep('''        (11.5, "o game.py só chama decide()",''', '''        (cg, "o game.py só chama decide()",''')

io.open(p, "w", encoding="utf-8").write(s)
print("ok")
