# Sepsis Resuscitation Agent

A Python rule-engine repository with a standalone browser-based **synthetic adult sepsis scenario calculator**. The original rule agents use generic demonstration thresholds and keywords; they are not a validated sepsis assessment or medical device.

> **For education and software testing only.** Do not submit real patient information. This project is not HIPAA-validated, does not implement clinical bundle compliance, and must not direct diagnosis, medication, vasopressor treatment, or fluid administration.

## Browser calculator

The static application in [`web/`](web/) calculates, for hypothetical adult examples:

- Percentage change between two lactate values (mmol/L).
- A 30 mL/kg *reference volume* and the fraction represented by a supplied crystalloid volume.
- Comparison of a user-specified antimicrobial administration interval with the context-dependent 2026 SSC timing reference.
- Display of a user-entered MAP, without automated clinical classification.
- Local JSON export of synthetic numbers.

The app uses JavaScript ES modules; it requires no account, API server, external font, network request, cookie, analytics, or browser storage. The browser never uploads calculator inputs. A static web server is recommended for local module loading.

**Clinical context:** The [2026 Surviving Sepsis Campaign adult guidelines](https://sccm.org/survivingsepsiscampaign/guidelines-and-resources/surviving-sepsis-campaign-adult-guidelines) supersede the 2021 guidance cited in historical modules. The 30 mL/kg recommendation is *conditional* for sepsis-induced hypoperfusion or septic shock, requires individualized assessment, and is not a universal target. Antibiotic timing depends on likelihood of infection and shock; a timing difference alone is not compliance. Repeated lactate values must be interpreted in context and should not drive ongoing fluid therapy to normalization.

## Run locally

Python 3.10+ is supported. From the repository root:

```bash
python -m pip install -e ".[server,test]"
python -m pytest -q
python cli.py audit --task-id DEMO-01 --primary 28 --secondary 5
python cli.py batch -i sample.csv -o results.csv
python cli.py serve --host 127.0.0.1 --port 8000
```

For the static calculator:

```bash
python -m http.server 8080 --directory web
```

Open `http://127.0.0.1:8080/` in a modern browser (Chrome, Firefox, Safari, Edge).

The legacy `sepsis_resuscitation.py` and `sepsis_resuscitation_agent/` entry points are retained for backward compatibility. An example file for the clinical-formatted legacy CLI is `sample_clinical.csv` (use `python -m sepsis_resuscitation_agent.cli batch -i sample_clinical.csv -o clinical-results.csv`). Their generic primary/secondary thresholds are illustrative only; they **do not** implement sepsis bundle timing, lactate clearance or patient-specific triage.

## Local API

Run `python cli.py serve` and inspect `http://127.0.0.1:8000/docs`. Available endpoints: `GET /health`, `GET /metrics`, `POST /api/audit`, `POST /api/chat`, and `GET /api/audit/logs`. The `/api/chat` adapter is a **deterministic mock**, not a live language model. This API is not authenticated; expose it only on trusted, local development networks and never use patient data.

## CSV and audit safeguards

Input and output CSV paths must remain under the working directory and must differ; boolean flags use strict `true/false`, `1/0` or `yes/no` parsing. A best-effort identifier regex screen rejects some recognizable sensitive strings, but it is **not** validated de-identification. Audit records are chained and HMAC-SHA256 signed and checked; by default the signing key is ephemeral, and the log is process-local. Set `AUDIT_SECRET_KEY` to a securely generated long random value for stable *in-process* signing. No persistence, key rotation, authorization, or immutable audit store is provided.

For a local container, copy `.env.example` to `.env`, set a secret key, then use `docker compose up --build`. Compose binds only to loopback by default. Do not expose this unauthenticated application publicly.

## Development and verification

- Python: `python -m pytest -q`
- Browser JS: `node --check web/app.mjs && node --test web/test_calculations.mjs`
- CI: GitHub Actions tests Python 3.10–3.12 and Node 22. The static site deployment job targets GitHub Pages on `master`; actual availability depends on repository Pages settings and successful deployment.
- Dependencies: Python standard library, Pydantic 2, optional FastAPI/Uvicorn, pytest/httpx for tests; no browser libraries.
- License: [MIT](LICENSE)

**Limitations:** Existing `enrichment.py` modules are generic placeholder scorers rather than clinically validated sepsis/ventilation/vasopressor models. No external LLM, live physiological monitoring, formal clinical validation, database, or production authentication is implemented.
