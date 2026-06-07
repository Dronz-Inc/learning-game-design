#!/usr/bin/env python3
"""
Generate the interactive HTML prototype (assignment-1/roll-call.html) from the
locked Option 1 criteria + country data. Self-contained: embeds, per country, a
6-bit mask for each of the three sets, plus the criteria labels and name aliases.
The page validates guesses and reveals answers on a loss (digital playtest only;
the printable PDF stays answer-free).
"""
import json
import os

import build_criteria as B
from traits_matrix import trait_masks
from final_criteria import SETS  # the locked 18 (label, key) grouped in 3 sets

M = trait_masks()
NAMES, IDX, pc = B.NAMES, B.IDX, B.popcount
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "roll-call.html")

CRITERIA = [[lbl for (lbl, _) in items] for (_, items) in SETS]
KEYS = [[k for (_, k) in items] for (_, items) in SETS]

def setmask(country, set_keys):
    bits = 0
    for i, k in enumerate(set_keys):
        if (M[k][2] >> IDX[country]) & 1:
            bits |= (1 << i)
    return bits

COUNTRIES = [{"n": n, "m": [setmask(n, KEYS[s]) for s in range(3)]} for n in NAMES]

# sanity: reproduce the 216 distribution from the embedded masks
dist0 = 0
for da in range(6):
    for db in range(6):
        for dc in range(6):
            cnt = sum(1 for c in COUNTRIES
                      if (c["m"][0] >> da) & 1 and (c["m"][1] >> db) & 1 and (c["m"][2] >> dc) & 1)
            if cnt == 0:
                dist0 += 1
assert dist0 == 0, f"embedded data has {dist0} impossible combos!"

ALIASES = {
    "usa": "United States", "us": "United States", "unitedstatesofamerica": "United States",
    "america": "United States",
    "uk": "United Kingdom", "britain": "United Kingdom", "greatbritain": "United Kingdom",
    "england": "United Kingdom",
    "uae": "United Arab Emirates", "emirates": "United Arab Emirates",
    "drc": "Democratic Republic of the Congo", "drcongo": "Democratic Republic of the Congo",
    "democraticrepublicofcongo": "Democratic Republic of the Congo",
    "congokinshasa": "Democratic Republic of the Congo", "zaire": "Democratic Republic of the Congo",
    "republicofthecongo": "Congo", "republicofcongo": "Congo", "congobrazzaville": "Congo",
    "ivorycoast": "Cote d'Ivoire", "cotedivoire": "Cote d'Ivoire",
    "capeverde": "Cabo Verde", "swaziland": "Eswatini", "easttimor": "Timor-Leste",
    "czechrepublic": "Czechia", "burma": "Myanmar", "macedonia": "North Macedonia",
    "holland": "Netherlands", "russianfederation": "Russia", "turkiye": "Turkey",
    "southkorea": "South Korea", "republicofkorea": "South Korea", "korea": "South Korea",
    "northkorea": "North Korea", "dprk": "North Korea",
    "bosnia": "Bosnia and Herzegovina", "stkittsandnevis": "Saint Kitts and Nevis",
    "stkitts": "Saint Kitts and Nevis", "stlucia": "Saint Lucia",
    "stvincentandthegrenadines": "Saint Vincent and the Grenadines",
    "stvincent": "Saint Vincent and the Grenadines",
    "vietnam": "Vietnam", "saotome": "Sao Tome and Principe",
    "gambia": "Gambia", "thegambia": "Gambia", "bahamas": "Bahamas", "thebahamas": "Bahamas",
}

HTML = r"""<!doctype html>
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
    <ol class="how">
      <li>Roll determines the round's three criteria automatically.</li>
      <li>Type a country and submit (Enter works too).</li>
      <li>Unrecognised spellings just ask you to retry; a valid-but-wrong answer ends the run.</li>
    </ol>
    <p style="margin-top:18px"><button class="big" onclick="startGame()">Start game</button></p>
  </div>

  <!-- PLAY -->
  <div id="playCard" class="card hide">
    <div class="dice" id="dice"></div>
    <div class="crit" id="crit"></div>
    <div class="row">
      <input type="text" id="guess" placeholder="Name a country..." autocomplete="off" spellcheck="false">
      <button onclick="submitGuess()">Submit</button>
    </div>
    <div class="row" style="justify-content:space-between;align-items:center">
      <span class="hint">Round criteria are independent &mdash; one country must satisfy all three.</span>
      <button class="ghost" onclick="giveUp()">Give up</button>
    </div>
    <div class="msg" id="msg"></div>
  </div>

  <!-- GAME OVER -->
  <div id="overCard" class="card center hide">
    <p>Game over</p>
    <div class="final"><span id="finalScore">0</span></div>
    <p class="hint">correct answers in a row</p>
    <div class="answers" id="answers"></div>
    <p style="margin-top:18px"><button class="big" onclick="startGame()">Play again</button></p>
  </div>

  <footer>Digital playtest &mdash; it checks your answer for you. The printable version is answer-free;
    you verify on a map.</footer>
</div>

<script>
const CRITERIA = __CRITERIA__;
const COUNTRIES = __COUNTRIES__;
const ALIASES = __ALIASES__;

function norm(s){
  return (s||"").normalize("NFD").replace(/[̀-ͯ]/g,"")
    .toLowerCase().replace(/[^a-z]/g,"");
}
const CANON = {};
COUNTRIES.forEach(c => { CANON[norm(c.n)] = c.n; });
Object.keys(ALIASES).forEach(k => { CANON[k] = ALIASES[k]; });
const BY_NAME = {}; COUNTRIES.forEach(c => BY_NAME[c.n] = c);

// proper unbiased d6 via crypto rejection sampling
function d6(){
  const buf = new Uint8Array(1);
  while(true){ crypto.getRandomValues(buf); if(buf[0] < 252) return (buf[0] % 6) + 1; }
}

let score=0, best=0, roundNo=0, dice=[1,1,1], valid=new Set(), playing=false;

function show(id, on){ document.getElementById(id).classList.toggle("hide", !on); }

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
  // render dice
  document.getElementById("dice").innerHTML =
    dice.map(d=>`<div class="die">${d}</div>`).join("");
  // render the three chosen criteria
  const tags=["Set 1 · Name","Set 2 · Flag","Set 3 · Terrain"];
  document.getElementById("crit").innerHTML = dice.map((d,s)=>
    `<div class="slot"><span class="num">⚂ ${d}</span><div class="tag">${tags[s]}</div>
       <div class="txt">${CRITERIA[s][d-1]}</div></div>`).join("");
  // compute valid answers for this round
  valid=new Set();
  COUNTRIES.forEach(c=>{
    if(((c.m[0]>>(dice[0]-1))&1) && ((c.m[1]>>(dice[1]-1))&1) && ((c.m[2]>>(dice[2]-1))&1))
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
</script>
</body>
</html>
"""

HTML = (HTML
        .replace("__CRITERIA__", json.dumps(CRITERIA))
        .replace("__COUNTRIES__", json.dumps(COUNTRIES, separators=(",", ":")))
        .replace("__ALIASES__", json.dumps(ALIASES)))

with open(OUT, "w") as f:
    f.write(HTML)
print(f"wrote {OUT}  ({len(COUNTRIES)} countries embedded, 0 impossible combos verified)")
