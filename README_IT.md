# PixelFeed

PixelFeed è una REST API costruita con FastAPI che simula un piccolo social media feed.
Gestisce utenti autenticati con JWT, creazione di post/commenti/like, upload di immagini e integrazione asincrona con servizi esterni (Mailgun per email e OpenAI per generazione immagini).

## Cosa fa
- Registrazione utente con conferma via email.
- Login con token Bearer (JWT) e protezione degli endpoint privati.
- Creazione post, commenti e like.
- Elenco post con ordinamento per più recenti, più vecchi o più apprezzati.
- Dettaglio post con commenti aggregati.
- Upload file immagine su storage locale.
- Generazione immagine opzionale su un post tramite prompt: il task salva il file, aggiorna il post e invia email di esito.

## Stack tecnico
- FastAPI + Uvicorn
- SQLite (via SQLAlchemy + `databases`)
- JWT (`python-jose`) + hashing password (`passlib`/Argon2)
- Task asincroni con `BackgroundTasks`
- Integrazioni esterne: Mailgun, OpenAI Images API
- Test con Pytest

## Ambienti
Il progetto è configurato per tre ambienti separati:
- `dev`: sviluppo locale (`DEV_...` nel file `.env`).
- `test`: test automatici con configurazione dedicata (DB separato e rollback forzato).
- `prod`: ambiente di produzione (`PROD_...` nel file `.env`).

La selezione avviene tramite `ENV_STATE` (`dev`, `test`, `prod`), letta in `src/config.py`.

## Avvio rapido
1. Configura `.env` (es. `ENV_STATE=dev`, `DEV_DATABASE_URL`, chiavi Mailgun/OpenAI).
2. Installa dipendenze:
   ```bash
   pip install -r requirements.txt
   ```
3. Avvia il server:
   ```bash
   uvicorn src.main:app --reload
   ```
4. Documentazione API disponibile su `/docs`.
