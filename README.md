# OneCarbon Completeness Check

Self-serve GHG source completeness screening tool. Sector picker \u2192 present/absent/unsure
checklist \u2192 on-screen gap summary \u2192 email-gated full report. Built to the locked spec in
`OneCarbon_Completeness_Tool_Sector_Spec_v1.md` and styled to the One17 brand system.

Stack: FastAPI + SQLite + static frontend (vanilla HTML/CSS/JS) \u2014 same pattern as
SG Legal Monitor and the golf scoring app, deployable to Railway.

## Structure

```
main.py            FastAPI app: serves static/ and the /api/submit lead-capture endpoint
gen_data.py         Regenerates static/sources.js from the sector spec (edit this, not sources.js directly)
static/
  index.html         Page structure (3 screens: sector / check / summary)
  style.css          One17 brand styling (DM Sans, sage/clay/charcoal, sharp corners, no shadows)
  app.js             All screening logic and state
  sources.js         Generated sector/source data \u2014 do not hand-edit, run gen_data.py instead
  assets/            One17 logo marks (colour + charcoal SVG)
requirements.txt
Procfile             Railway start command
```

## Run locally

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in RESEND_API_KEY
uvicorn main:app --reload --port 8000
```
Open http://localhost:8000

## Email delivery (Resend)

Wired up in `email_report.py`, sent from `main.py`'s `/api/submit` handler.

- Set `RESEND_API_KEY` (your existing key, same one your contact form uses) and
  `RESEND_FROM_EMAIL` in `.env` locally, or as environment variables in Railway.
- Sends from `chtan@one-17.com` by default (matches your verified sending domain) with
  `reply_to` also set to `chtan@one-17.com`.
- The report content \u2014 scope breakdown, unsure-item list, what-wasn't-screened note, and a
  soft CTA \u2014 is built in `build_report_html()`. Edit copy there; no frontend changes needed.
- If sending fails for any reason, the lead is still stored in SQLite (`email_sent: false` in
  the API response) rather than losing the submission \u2014 check server logs for the error.
- Per-source "unsure" prompts are currently generic ("worth confirming with the relevant team").
  If you want tailored one-line prompts per source (like the fire-suppression example we drafted
  earlier), that's a `prompts.py` lookup keyed by source id \u2014 flag if you want that built out.

## Regenerate source data

If the sector spec changes, edit the `MASTER` / `SECTOR_EXTRA` / `SECTOR_OPTIONAL` dicts in
`gen_data.py` (source of truth is `OneCarbon_Completeness_Tool_Sector_Spec_v1.md`), then:

```bash
python3 gen_data.py
```

This rewrites `static/sources.js`.

## Deploy to Railway

1. Push this repo to GitHub (or `railway up` directly from this folder).
2. Railway auto-detects Python; the `Procfile` sets the start command.
3. Point a CNAME from `check.one-17.com` (or your chosen subdomain) at the Railway-provided
   domain, and add it as a custom domain in the Railway project settings.
4. SQLite data lives in `data/leads.db` \u2014 on Railway this needs a persistent volume mounted
   at `/app/data`, otherwise leads are lost on redeploy. Add a volume in the Railway service
   settings if you want leads to persist across deploys.

## Known gaps to close before going live

- **No spam/rate limiting** on `/api/submit` \u2014 fine for a soft launch, worth adding basic
  throttling before heavy traffic (e.g. an NTU talk audience hitting it at once).
- **No admin view of leads yet** \u2014 for now, pull them directly from `data/leads.db`
  (`sqlite3 data/leads.db "SELECT * FROM leads;"`) or add a simple authenticated `/admin` route
  later.
- Optional-source toggle (edge-case sources like marine vessels, franchisor-specific items) is
  wired up per the spec's "optional" flags \u2014 test that the "show more" link appears only where
  the sector actually has optional items (Office-based, Logistics, Semiconductor).
