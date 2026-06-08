#!/usr/bin/env python3
"""
Rebuild assignment-1/roll-call.html with TWO difficulty modes:

  * Hard  - the original Name / Flag / Terrain criteria (unchanged), kept as the
            challenge mode.
  * Normal- an easier, friendlier set: Name / Location / Geography. Broader,
            more forgiving criteria (median ~9-10 valid answers per roll vs ~5
            on hard) while still never producing an impossible roll.

The start screen gets a Normal/Hard toggle. Every country carries a 6-bit mask
per set for BOTH modes; the page picks the right masks + labels from the toggle.

Hard data + aliases are lifted verbatim from the existing roll-call.html so the
challenge mode is byte-for-byte the same game. Normal masks are computed here
from country_data.csv and verified to have zero impossible rolls.

Run:  python3 build_normal.py
"""
import csv, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(os.path.dirname(HERE), "roll-call.html")
DATA = os.path.join(HERE, "country_data.csv")

# ---- 1. lift the existing (hard) game data verbatim -----------------------
old = open(HTML_PATH).read()
HARD_CRITERIA = json.loads(re.search(r"const CRITERIA = (\[.*?\]);", old).group(1))
HARD_COUNTRIES = json.loads(re.search(r"const COUNTRIES = (\[.*?\]);", old).group(1))
ALIASES = json.loads(re.search(r"const ALIASES = (\{.*?\});", old).group(1))

# ---- 2. normal-mode criteria (designed + verified in normal_criteria.py) --
def letters(name): return re.sub(r"[^a-z]", "", name.lower())

NORMAL = [
    ("Set 1 · Name", [
        ("Name has fewer than 8 letters", lambda r: len(letters(r["Country"])) < 8),
        ("Name has more than 7 letters",  lambda r: len(letters(r["Country"])) > 7),
        ("Name starts with a vowel",      lambda r: letters(r["Country"])[:1] in tuple("aeiou")),
        ("Name ends in the letter A",     lambda r: letters(r["Country"]).endswith("a")),
        ("Name contains the letter N",    lambda r: "n" in letters(r["Country"])),
        ("Name is a single word",         lambda r: " " not in r["Country"].strip()),
    ]),
    ("Set 2 · Location", [
        ("Located in Africa or Europe",   lambda r: r["Continent"] in ("Africa", "Europe")),
        ("Located in Asia or Oceania",    lambda r: r["Continent"] in ("Asia", "Oceania")),
        ("Lies north of the equator",     lambda r: r["Hemisphere"] in ("Northern", "Both")),
        ("Lies south of the equator",     lambda r: r["Hemisphere"] in ("Southern", "Both")),
        ("Crossed by the equator or a tropic line", lambda r: "Yes" in (
            r["Crosses_equator"], r["Crosses_tropic_of_cancer"], r["Crosses_tropic_of_capricorn"])),
        ("Lies in the tropics or further south", lambda r: r["Hemisphere"] in ("Southern", "Both")
            or "Yes" in (r["Crosses_tropic_of_cancer"], r["Crosses_equator"])),
    ]),
    ("Set 3 · Geography", [
        ("Has active volcanoes",          lambda r: r["Has_active_volcanoes"] == "Yes"),
        ("Is landlocked (no sea coast)",  lambda r: r["Landlocked"] == "Yes"),
        ("Is an island nation",           lambda r: r["Archipelago"] == "Yes"),
        ("Has a sea or ocean coastline",  lambda r: r["Landlocked"] == "No"),
        ("Borders four or more countries",lambda r: int(r["Bordering_countries"]) >= 4),
        ("Larger than 1,000,000 km²",lambda r: int(r["Area_km2"]) >= 1_000_000),
    ]),
]

NORMAL_CRITERIA = [[lbl for (lbl, _) in items] for (_, items) in NORMAL]
NORMAL_TAGS = [tag for (tag, _) in NORMAL]
HARD_TAGS = ["Set 1 · Name", "Set 2 · Flag", "Set 3 · Terrain"]

# ---- 3. compute normal masks per country, aligned to the game's order -----
def normkey(s): return re.sub(r"[^a-z]", "", (s or "").lower())
ROWS = {normkey(r["Country"]): r for r in csv.DictReader(open(DATA))}

def normal_masks(country_name):
    r = ROWS[normkey(country_name)]
    out = []
    for (_, items) in NORMAL:
        bits = 0
        for i, (_, pred) in enumerate(items):
            if pred(r):
                bits |= (1 << i)
        out.append(bits)
    return out

COUNTRIES = []
for c in HARD_COUNTRIES:
    COUNTRIES.append({"n": c["n"], "h": c["m"], "e": normal_masks(c["n"])})

# ---- 4. verify: zero impossible rolls in BOTH modes -----------------------
def impossible(key):
    bad = 0
    for a in range(6):
        for b in range(6):
            for d in range(6):
                if not any((c[key][0] >> a) & 1 and (c[key][1] >> b) & 1 and (c[key][2] >> d) & 1
                           for c in COUNTRIES):
                    bad += 1
    return bad

assert impossible("h") == 0, "hard mode regressed!"
assert impossible("e") == 0, "normal mode has impossible rolls!"

MODES = {
    "normal": {"label": "Normal", "key": "e", "criteria": NORMAL_CRITERIA, "tags": NORMAL_TAGS,
               "blurb": "Easier, friendlier criteria — name, where it is, and its geography."},
    "hard":   {"label": "Hard", "key": "h", "criteria": HARD_CRITERIA, "tags": HARD_TAGS,
               "blurb": "The original challenge — name, flag, and terrain. Tighter answers."},
}

# ---- 5. emit the page -----------------------------------------------------
HTML = TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Roll Call - a country-naming streak game</title>
<style>
  :root{
    --ink:#1f2933; --muted:#67727e; --line:#e3e8ee; --bg:#f7f5ef; --card:#fff;
    --accent:#2e7d5b; --accent2:#c0563b; --gold:#d8a23a;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
    font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
  .wrap{max-width:760px;margin:0 auto;padding:26px 18px 60px;}
  header h1{font-size:34px;margin:0 0 2px;letter-spacing:.3px;}
  header p{margin:0;color:var(--muted);}
  .scorebar{display:flex;gap:10px;align-items:center;margin:18px 0;flex-wrap:wrap;}
  .badge{background:var(--card);border:1px solid var(--line);border-radius:10px;
    padding:8px 14px;font-weight:600;}
  .badge b{color:var(--accent);font-size:20px;}
  .card{background:var(--card);border:1px solid var(--line);border-radius:14px;
    padding:20px;box-shadow:0 1px 0 rgba(0,0,0,.02);}
  .dice{display:flex;gap:14px;justify-content:center;margin:6px 0 18px;}
  .die{width:54px;height:54px;border-radius:12px;border:2px solid var(--ink);
    display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:700;
    background:#fff;}
  .crit{display:grid;grid-template-columns:1fr;gap:10px;margin-bottom:18px;}
  @media(min-width:620px){.crit{grid-template-columns:repeat(3,1fr);}}
  .slot{border:1px solid var(--line);border-radius:12px;padding:12px 14px;background:#fafbfc;}
  .slot .tag{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);}
  .slot .txt{font-size:17px;font-weight:600;margin-top:4px;}
  .slot .num{float:right;color:var(--muted);font-variant-numeric:tabular-nums;}
  .row{display:flex;gap:10px;margin-top:6px;}
  input[type=text]{flex:1;padding:13px 14px;font-size:17px;border:1px solid var(--line);
    border-radius:10px;background:#fff;}
  input[type=text]:focus{outline:none;border-color:var(--accent);}
  button{cursor:pointer;border:0;border-radius:10px;padding:13px 18px;font-size:16px;
    font-weight:600;background:var(--ink);color:#fff;}
  button.ghost{background:#fff;color:var(--ink);border:1px solid var(--line);}
  button.big{font-size:19px;padding:16px 28px;background:var(--accent);}
  .toggle{display:inline-flex;border:1px solid var(--line);border-radius:12px;overflow:hidden;
    margin:4px 0 6px;background:#fff;}
  .toggle button{background:#fff;color:var(--muted);border:0;border-radius:0;padding:11px 22px;
    font-size:16px;}
  .toggle button.on{background:var(--accent);color:#fff;}
  .modeline{color:var(--muted);font-size:14px;margin:4px 0 0;min-height:20px;}
  .msg{min-height:24px;margin-top:12px;font-weight:600;}
  .ok{color:var(--accent);} .bad{color:var(--accent2);}
  .answers{margin-top:10px;background:#fbf3ee;border:1px solid #f0d9cd;border-radius:10px;padding:12px 14px;}
  .answers b{color:var(--accent2);}
  .center{text-align:center;}
  .hint{color:var(--muted);font-size:14px;}
  .hide{display:none;}
  .final{font-size:40px;font-weight:800;color:var(--gold);}
  ol.how{margin:8px 0 0;padding-left:20px;color:var(--muted);font-size:14px;}
  footer{color:var(--muted);font-size:13px;margin-top:22px;text-align:center;}
</style>
</head>
<body>
<div class="wrap">
  <div id="errbar" style="display:none;background:#c0392b;color:#fff;padding:10px 12px;border-radius:8px;margin-bottom:12px;font-weight:600;"></div>
  <header>
    <h1>Roll Call</h1>
    <p>Name a country that fits all three rolled criteria. How long a streak can you make?</p>
  </header>

  <div class="scorebar">
    <span class="badge">Streak <b id="score">0</b></span>
    <span class="badge">Best <b id="best">0</b></span>
    <span class="badge">Round <b id="round">-</b></span>
  </div>

  <!-- START -->
  <div id="startCard" class="card center">
    <p>Press start. Three dice pick one criterion from each set. Name any country that satisfies
       <b>all three</b> &mdash; from memory, no map &mdash; then submit. Correct keeps the streak alive;
       one wrong answer ends the game.</p>
    <p style="margin-top:14px;font-weight:600">Difficulty</p>
    <div class="toggle" id="modeToggle">
      <button type="button" data-mode="normal">Normal</button>
      <button type="button" data-mode="hard">Hard</button>
    </div>
    <p class="modeline" id="modeBlurb"></p>
    <ol class="how">
      <li>Roll determines the round's three criteria automatically.</li>
      <li>Type a country and submit (Enter works too).</li>
      <li>Unrecognised spellings just ask you to retry; a valid-but-wrong answer ends the run.</li>
    </ol>
    <p style="margin-top:18px"><button class="big" id="startBtn" type="button">Start game</button></p>
  </div>

  <!-- PLAY -->
  <div id="playCard" class="card hide">
    <div class="dice" id="dice"></div>
    <div class="crit" id="crit"></div>
    <div class="row">
      <input type="text" id="guess" placeholder="Name a country..." autocomplete="off" spellcheck="false">
      <button id="submitBtn" type="button">Submit</button>
    </div>
    <div class="row" style="justify-content:space-between;align-items:center">
      <span class="hint">Round criteria are independent &mdash; one country must satisfy all three.</span>
      <button class="ghost" id="giveupBtn" type="button">Give up</button>
    </div>
    <div class="msg" id="msg"></div>
  </div>

  <!-- GAME OVER -->
  <div id="overCard" class="card center hide">
    <p>Game over</p>
    <div class="final"><span id="finalScore">0</span></div>
    <p class="hint">correct answers in a row</p>
    <div class="answers" id="answers"></div>
    <p style="margin-top:18px"><button class="big" id="againBtn" type="button">Play again</button></p>
  </div>

  <footer>Digital playtest &mdash; it checks your answer for you. The printable version is answer-free;
    you verify on a map.</footer>
</div>

<script>
const MODES = __MODES__;
const COUNTRIES = __COUNTRIES__;
const ALIASES = __ALIASES__;
let mode = "normal";

function norm(s){
  return (s||"").normalize("NFD").replace(/[̀-ͯ]/g,"")
    .toLowerCase().replace(/[^a-z]/g,"");
}
const CANON = {};
COUNTRIES.forEach(c => { CANON[norm(c.n)] = c.n; });
Object.keys(ALIASES).forEach(k => { CANON[k] = ALIASES[k]; });

// proper unbiased d6 via crypto rejection sampling (Math.random fallback)
function d6(){
  const c = (typeof crypto!=="undefined" && crypto.getRandomValues) ? crypto : null;
  if(c){ const buf=new Uint8Array(1);
    for(let i=0;i<10;i++){ c.getRandomValues(buf); if(buf[0]<252) return (buf[0]%6)+1; } }
  return Math.floor(Math.random()*6)+1;
}

let score=0, best=0, roundNo=0, dice=[1,1,1], valid=new Set(), playing=false;

function show(id, on){ document.getElementById(id).classList.toggle("hide", !on); }

function setMode(m){
  mode = m;
  document.querySelectorAll("#modeToggle button").forEach(b =>
    b.classList.toggle("on", b.getAttribute("data-mode")===m));
  document.getElementById("modeBlurb").textContent = MODES[m].blurb;
  best = 0; setScore();  // best streak is per-difficulty
}

function startGame(){
  score=0; roundNo=0; setScore();
  show("startCard",false); show("overCard",false); show("playCard",true);
  playing=true; nextRound();
}

function setScore(){
  document.getElementById("score").textContent=score;
  document.getElementById("best").textContent=best;
  document.getElementById("round").textContent = playing ? roundNo : "-";
}

function nextRound(){
  roundNo++; setScore();
  dice=[d6(),d6(),d6()];
  const M = MODES[mode], key = M.key;
  // render dice
  document.getElementById("dice").innerHTML =
    dice.map(d=>`<div class="die">${d}</div>`).join("");
  // render the three chosen criteria
  document.getElementById("crit").innerHTML = dice.map((d,s)=>
    `<div class="slot"><span class="num">⚂ ${d}</span><div class="tag">${M.tags[s]}</div>
       <div class="txt">${M.criteria[s][d-1]}</div></div>`).join("");
  // compute valid answers for this round
  valid=new Set();
  COUNTRIES.forEach(c=>{
    const m=c[key];
    if(((m[0]>>(dice[0]-1))&1) && ((m[1]>>(dice[1]-1))&1) && ((m[2]>>(dice[2]-1))&1))
      valid.add(c.n);
  });
  const g=document.getElementById("guess"); g.value=""; g.focus();
  document.getElementById("msg").textContent="";
}

function submitGuess(){
  if(!playing) return;
  const raw=document.getElementById("guess").value.trim();
  if(!raw) return;
  const canon = CANON[norm(raw)];
  const msg=document.getElementById("msg");
  if(!canon){
    msg.className="msg bad";
    msg.textContent=`"${raw}" isn't a country I recognise — check the spelling and try again.`;
    return;
  }
  if(valid.has(canon)){
    score++; if(score>best) best=score;
    msg.className="msg ok"; msg.textContent=`✓ ${canon} fits — nice! Next round...`;
    document.getElementById("guess").value="";
    setScore();
    setTimeout(nextRound, 750);
  } else {
    gameOver(canon);
  }
}

function giveUp(){ if(playing) gameOver(null); }

function gameOver(badGuess){
  playing=false; if(score>best) best=score; setScore();
  show("playCard",false); show("overCard",true);
  document.getElementById("finalScore").textContent=score;
  const ans=[...valid].sort();
  const lead = badGuess
    ? `<b>${badGuess}</b> doesn't fit this round. `
    : `You gave up. `;
  const list = ans.length
    ? `Valid answers were (${ans.length}): ${ans.join(", ")}.`
    : `Actually there were no valid answers — that shouldn't happen, please report it!`;
  document.getElementById("answers").innerHTML = lead + list;
  document.getElementById("best").textContent=best;
}

document.addEventListener("keydown", e=>{
  if(e.key==="Enter" && !document.getElementById("playCard").classList.contains("hide"))
    submitGuess();
});

// surface any error visibly instead of failing silently
window.onerror=function(message,src,line,col){
  var b=document.getElementById("errbar");
  if(b){ b.style.display="block"; b.textContent="Error: "+message+" (line "+line+")"; }
  return false;
};

// wire buttons (works even where inline handlers are blocked)
function wire(){
  var map={startBtn:startGame, submitBtn:submitGuess, giveupBtn:giveUp, againBtn:startGame};
  for(var id in map){ var el=document.getElementById(id); if(el) el.addEventListener("click", map[id]); }
  document.querySelectorAll("#modeToggle button").forEach(b =>
    b.addEventListener("click", ()=>setMode(b.getAttribute("data-mode"))));
  setMode("normal");
}
wire();
</script>
</body>
</html>
"""

HTML = (HTML
        .replace("__MODES__", json.dumps(MODES, separators=(",", ":")))
        .replace("__COUNTRIES__", json.dumps(COUNTRIES, separators=(",", ":")))
        .replace("__ALIASES__", json.dumps(ALIASES, separators=(",", ":"))))

with open(HTML_PATH, "w") as f:
    f.write(HTML)
print(f"wrote {HTML_PATH}")
print(f"  {len(COUNTRIES)} countries, 2 modes, 0 impossible rolls in both (verified)")
