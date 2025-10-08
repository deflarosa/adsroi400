
# AdOptimizer ROI 400+ (Demo)

Sistema minimal per tracciare **spesa, fatturato e ROI (netto del taglio 30%)** per campagne Google/Facebook, con **riepilogo giornaliero** e **grafici giornalieri**.

## Requisiti
- Python 3.10+

## Installazione
```bash
cd adoptimizer_roi400
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Avvio
```bash
uvicorn app.main:app --reload
```
Apri il browser su: **http://127.0.0.1:8000/static/index.html**

## Configurazione (facoltativa)
Modifica `app/settings.py`:
- `HAIRCUT = 0.30`
- `TARGET_ROI_NETTO = 1.0`
- `PAYOUT_LORDO = 19.0`
- `USE_PAYOUT_MODE = True` (usa payout netto) oppure `False` (usa fatturato netto)

## API principali
- `POST /ingest` — Inserisce una riga oraria di campagna
- `POST /report/build/{YYYY-MM-DD}` — Costruisce il riepilogo del giorno
- `GET /report/daily/{YYYY-MM-DD}` — Riepilogo del giorno (lista per piattaforma/prodotto)
- `GET /report/range?start=YYYY-MM-DD&end=YYYY-MM-DD` — Storico riepiloghi
- `POST /decision` — Restituisce una raccomandazione (bid/budget) in base ai KPI
- `GET /config` — Mostra la configurazione attuale

## Demo rapida
1. Avvia il server (`uvicorn`)
2. Apri `http://127.0.0.1:8000/static/index.html`
3. Clicca **"Inserisci dati di esempio"**
4. Seleziona **Start** e **End** (es. ultimi 7 giorni) e clicca **"Carica storico"**

## Note
- Questo progetto è una base pronta per essere estesa con integrazioni **Google Ads API** e **Meta Marketing API**.
- I grafici usano **Chart.js** via CDN.


---

## Deploy su un sito (hosting gratuito o low-cost)

### Opzione A) Render.com (consigliato, 1 click via Docker)
1. Crea un nuovo repository **GitHub** e carica dentro tutti i file del progetto.
2. Su **Render.com** → **New** → **Blueprint** → collega il repo e seleziona `render.yaml`.
3. Conferma: Render creerà un **Web Service** Docker e avvierà il server `uvicorn`.
4. Quando lo stato è **Live**, apri l’URL pubblico e aggiungi `/static/index.html` alla fine per vedere la dashboard.
   - Esempio: `https://adoptimizer-roi400.onrender.com/static/index.html`

### Opzione B) Railway.app (semplice)
1. Importa il repo da GitHub su **Railway**.
2. Seleziona **Dockerfile** come metodo di deploy.
3. Porta: `8000`. Avvio: il comando del Dockerfile è già pronto.
4. Apri l’URL pubblico + `/static/index.html`.

### Opzione C) Replit (semplicissimo, ma meno performante)
1. Crea un nuovo Repl **Python**.
2. Carica cartella `app/` e `requirements.txt`, poi imposta comando run:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
3. Apri la pagina web generata da Replit + `/static/index.html`.

### Variabili di configurazione opzionali
Modifica `app/settings.py` oppure imposta env vars al build:
- `HAIRCUT` (default 0.30)
- `TARGET_ROI_NETTO` (default 1.0)
- `PAYOUT_LORDO` (default 19.0)
- `USE_PAYOUT_MODE` (`True`/`False`)

### Note importanti
- L’endpoint di **salute** è `/health` (utile per i provider di hosting).
- Tutti gli asset statici sono serviti da FastAPI su `/static/index.html`.
- Puoi collegare un dominio custom puntando al servizio web.
