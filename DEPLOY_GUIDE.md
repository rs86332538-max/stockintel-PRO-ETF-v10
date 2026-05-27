# STOCK PRO 10X — Online med Login
## Trin-for-trin guide (Railway — gratis tier)

---

## HVAD ER INKLUDERET I DENNE PAKKE

| Fil | Formål |
|-----|--------|
| `auth_server.py` | **Ny** — Login-wrapper der beskytter hele appen |
| `login.html` | **Ny** — Dansk login-side |
| `server.py` | Uændret original |
| `etf_core.py` | Uændret original |
| `xtrackers_data.py` | Uændret original |
| `etf-database.json` | Uændret original |
| `index.html` | Uændret original |
| `etf.html` | Uændret original |
| `Procfile` | **Ny** — Fortæller Railway hvad der skal startes |
| `requirements.txt` | **Ny** — Python-pakkeliste |
| `nixpacks.toml` | **Ny** — Build-konfiguration |

---

## TRIN 1 — Opret konto på Railway

1. Gå til **https://railway.app**
2. Klik **"Start a New Project"** → log ind med GitHub
3. Railway giver dig 500 gratis timer/måned (nok til privat brug)

---

## TRIN 2 — Upload filerne til GitHub

Du skal have filerne på GitHub for at Railway kan hente dem.

**Mulighed A — GitHub.com (ingen installation)**
1. Gå til **https://github.com/new** og opret et **privat** repository
   - Name: `stockpro` (eller hvad du vil)
   - Sæt til **Private** ← VIGTIGT, så koden ikke er offentlig
2. Klik **"uploading an existing file"**
3. Drag-and-drop ALLE filer fra denne mappe
4. Klik **"Commit changes"**

**Mulighed B — Git fra terminal**
```bash
git init
git add .
git commit -m "Stock Pro 10X"
git remote add origin https://github.com/DIT-BRUGERNAVN/stockpro.git
git push -u origin main
```

---

## TRIN 3 — Deploy på Railway

1. På Railway: klik **"New Project" → "Deploy from GitHub repo"**
2. Vælg dit `stockpro` repository
3. Railway detecterer automatisk Python og starter deployment

---

## TRIN 4 — Sæt dine login-oplysninger (VIGTIGT!)

Gå til dit projekt på Railway → **Settings → Variables** og tilføj:

| Variable | Værdi | Eksempel |
|----------|-------|---------|
| `APP_USERNAME` | Dit brugernavn | `thomas` |
| `APP_PASSWORD` | Din adgangskode | `MinHemmeligeKode123!` |
| `SECRET_KEY` | Lang tilfældig streng | `xK9#mP2$qR7nL5vW8aB3cD6eF1gH4iJ0` |

> **Tip:** Brug en adgangskode med store/små bogstaver + tal + tegn.
> SECRET_KEY kan være hvad som helst langt og tilfældigt — den bruges
> til at kryptere session-cookies.

Klik **"Deploy"** efter du har sat variablerne.

---

## TRIN 5 — Få din URL

1. Gå til **Settings → Domains** i Railway
2. Klik **"Generate Domain"**
3. Du får en URL som: `https://stockpro-production-xxxx.up.railway.app`

Det er din personlige adresse. Gem den!

---

## SÅDAN BRUGER DU DET

- Gå til din Railway-URL i browseren
- Du ser login-siden
- Log ind med dit brugernavn + adgangskode
- Du er inde! Sessionen holder i 30 dage (du logger ikke ud automatisk)
- Log ud via: `https://din-url.railway.app/logout`

---

## SIKKERHED

✅ Al trafik krypteres med HTTPS (Railway håndterer det)
✅ Session-cookies er HMAC-signerede (kan ikke falskes)
✅ Adgangskoden sendes aldrig i klartekst i URL'en
✅ Forkert login → fejlbesked, ingen information om hvad der er forkert
✅ Sessions udløber automatisk efter 30 dage

---

## LOKALT BRUG (som før)

Vil du stadig køre lokalt (uden login)?
```bash
python server.py
```

Vil du teste login lokalt:
```bash
APP_USERNAME=admin APP_PASSWORD=test SECRET_KEY=test-key python auth_server.py
```
Åbn: http://localhost:7722/

---

## FEJLFINDING

**"server.py ikke fundet"** — Alle filer skal ligge i SAMME mappe.

**"500 intern fejl"** — Tjek Railway logs under **Deployments → View Logs**

**Siden er langsom første gang** — Railway "vækker" appen op. Det tager ~5 sek.
Gratis Railway-plan sætter appen i dvale efter 5 min inaktivitet.

**Vil du undgå dvale?** — Opgrader til Railway Hobby-plan ($5/md) eller brug
UptimeRobot til at pinge din URL hvert 4. minut (gratis).

---

## PRIS

| Plan | Pris | Timer/måned |
|------|------|-------------|
| Free | $0 | 500 timer |
| Hobby | $5/md | Ubegrænset |

Til privat brug er Free-planen fint nok.
