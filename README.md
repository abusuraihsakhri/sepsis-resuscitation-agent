# Sepsis Resuscitation Agent

> **Domain:** Privacy-Preserving Healthcare & Federated Computing  
> **Reference Guidelines & Standards:** `HIPAA Safe Harbor §164.514 & Differential Privacy RDP`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Sepsis Resuscitation Agent** is an advanced analytical and computational platform implementing Surviving Sepsis 1h/3h Bundle & Dynamic Lactate Clearance Tracker. It provides multi-agent clinical decision support with privacy-preserving safeguards.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Core Algorithmic & Evaluation Engines

- **`Severity`** — dedicated module for severity evaluation and state verification.
- **`DomainKnowledgeRegistry`**: Enterprise domain rules, guideline matrices, and evidence benchmarks.
- **`AgentAlert`** — dedicated module for agent alert evaluation and state verification.
- **`BundleClockTimerAgent`**: Specialized Sub-Agent 1 for bundle compliance timing
- **`LactateKineticsAgent`**: Specialized Sub-Agent 2 for lactate clearance tracking
- **`VasopressorTitrationAgent`**: Specialized Sub-Agent 3 for vasopressor titration monitoring

### 🛡️ Security & Privacy

- **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
- **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation.
- **Path Traversal Protection:** All file operations validated to prevent directory traversal attacks.
- **Secure Key Management:** HMAC keys generated via `secrets.token_hex()` with environment variable override.

---

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/sepsis-resuscitation-agent.git
cd sepsis-resuscitation-agent

# Install dependencies
pip install fastapi uvicorn pydantic pytest

# Set up environment configuration
cp .env.example .env
# Edit .env and set a secure AUDIT_SECRET_KEY
```

### Generating a Secure Audit Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 💻 CLI Quickstart & Usage

### 1. Single Case Audit
```bash
python cli.py audit --task-id CASE-001 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Batch Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 3. Query the Assistant
```bash
python cli.py chat "What is the system status?"
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Unique task/case identifier | Required |
| `target_identifier` | Entity or patient key | Required |
| `primary_metric` | Primary measurement value | Required |
| `secondary_metric` | Secondary kinetic/confidence score | Optional |
| `status_descriptor` | Status code or phenotype | Optional |
| `is_critical_flag` | Emergency escalation trigger | Optional |

---

## 🌐 REST API Endpoints

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| GET | `/health` | Health check and system metadata |
| GET | `/metrics` | Prometheus operational metrics |
| POST | `/api/audit` | Submit task for multi-agent evaluation |
| POST | `/api/chat` | Query the supervisory assistant |
| GET | `/api/audit/logs` | Retrieve and verify HMAC audit trail |

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

### Docker Compose (Recommended)

```bash
# Set up environment
cp .env.example .env
# Edit .env with your secure AUDIT_SECRET_KEY

# Build and run
docker-compose up --build
```

### Docker Direct

```bash
docker build -t sepsis-resuscitation-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secure-key sepsis-resuscitation-agent
```

---

## 📁 Project Structure

```
sepsis-resuscitation-agent/
├── agents/                         # Core multi-agent architecture
│   ├── __init__.py                 # Package version
│   ├── api.py                      # FastAPI REST endpoints
│   ├── base.py                     # Security, PHI guard, HMAC audit
│   ├── learning.py                 # Bayesian calibration engine
│   ├── llm_factory.py              # LLM provider abstraction
│   ├── metrics.py                  # Prometheus metrics exporter
│   ├── models.py                   # Pydantic data schemas
│   ├── streamer.py                 # WebSocket telemetry
│   ├── supervisor.py               # Master orchestrator
│   └── workers.py                  # Specialized worker agents
├── sepsis_resuscitation_agent/     # Clinical coordinator package
│   ├── agents.py                   # Clinical sub-agents
│   ├── cli.py                      # Clinical CLI interface
│   ├── engine.py                   # Clinical algorithmic engine
│   ├── models.py                   # Clinical data models
│   └── server.py                   # Clinical FastAPI server
├── tests/                          # Test suites
│   ├── test_enrichment.py          # Enrichment module tests
│   └── test_sepsis_resuscitation_agent.py  # Security & integration tests
├── web/                            # Operations console
│   └── index.html                  # Web dashboard
├── cli.py                          # Main CLI entry point
├── sepsis_resuscitation.py         # Core engine module
├── enrichment.py                   # Feature enrichment suite
├── simulator.py                    # High-throughput simulator
├── pyproject.toml                  # Project configuration
├── Dockerfile                      # Container build
├── docker-compose.yml              # Container orchestration
└── .github/workflows/ci.yml        # CI/CD pipeline
```

---

## 🛡️ Security Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Path Traversal Protection:** All file I/O operations validated against working directory boundaries.
* **Secure Key Generation:** Uses `secrets.token_hex(32)` for cryptographically strong HMAC keys.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
