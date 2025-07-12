# ---------- configuration ----------
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSWx1lVogYUCffYh-s2sips9yysy8icxoUm1fWo-XgKeBmy3r7phiqpIdFUXVAZlE46To8YYhy-3TQO/pub?gid=1682242390&single=true&output=csv"
FUZZY_THRESHOLD = 60      # ↓ raise if you want stricter matches
CACHE_SECONDS   = 60      # reload sheet at most once per minute
# -----------------------------------


from flask import Flask, request, render_template_string
from rapidfuzz import process, fuzz
import pandas as pd, requests, time, io

app = Flask(__name__)

_last_load, _names, _tables = 0, [], []

def refresh():
    """Download the published-CSV sheet (if cache expired) and prep lists."""
    global _last_load, _names, _tables
    if time.time() - _last_load > CACHE_SECONDS:
        csv_text = requests.get(SHEET_CSV_URL, timeout=10).text
        df = pd.read_csv(io.StringIO(csv_text))               # pandas ≥2.0 OK
        _names  = df["Name"].fillna("").tolist()
        _tables = df["Table"].tolist()
        _last_load = time.time()

# ─── HTML template ────────────────────────────────────────────────────────────
HTML = """
<!doctype html><html lang=en><meta charset=utf-8>
<title>Trouvez votre table / Find your table</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  body   {font-family:sans-serif;text-align:center;
          margin:0 auto;max-width:600px;padding:1rem}
  h1     {font-size:2rem;margin:0.5rem 0;}
  #msg   {font-size:2rem;margin-top:1rem;}
  .banner{display:block;margin:1rem auto;max-width:30%;height:auto}
  input,button{font-size:1rem;padding:.7rem;border:1px solid #ccc;
               border-radius:6px;box-sizing:border-box;width:100%;margin:0.3rem 0}
  button {background:#6a5acd;color:white;border:none}
</style>

<h1>🌸 MARIA LUCIA QUINCEAÑERA 🌸</h1>
<h2>BIENVENUE / WELCOME / BIENVENIDO</h2>
<!-- NEW: responsive JPG -->
<img src="{{ url_for('static', filename='lu15.png') }}"
     alt="Event banner" class="banner">

<form action="/lookup">
  <input name="q" placeholder="Tapez votre nom / Type your name" value="{{ q|default('') }}">
  <button type="submit">Search</button>
</form>

{% if msg is defined %}
  <p id="msg">{{ msg|safe }}</p>
{% endif %}
</html>
"""
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/lookup")
def lookup():
    q = request.args.get("q", "").strip()
    if not q:
        return render_template_string(HTML, q=q)

    refresh()
    match = process.extractOne(q, _names,
                               scorer=fuzz.token_set_ratio,
                               score_cutoff=FUZZY_THRESHOLD)
    msg = (f"🪑 <b>Table {_tables[match[2]]}</b>."
           if match else "Nom introuvable – veuillez vérifier l'orthographe / Name not found – please check spelling")
    return render_template_string(HTML, q=q, msg=msg)

# ─── local runner ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)
