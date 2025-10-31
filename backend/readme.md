# Excel Viewer & AI Modifier — Backend (FastAPI)

> Backend service for enriching Excel data using deterministic rules and (optionally) OpenAI models.

---

##  Overview

This backend is part of the **Excel Viewer & AI Modifier** full-stack technical test.
It provides an API to:

* **Receive** an Excel file (`.xlsx`) from the frontend
* **Apply enrichment rules** (defined in JSON format)
* Optionally **use an LLM (OpenAI)** to enrich the data
* **Return** a modified Excel file ready for download

The goal is to simulate a lightweight AI-assisted **insurance underwriting** enrichment engine.

---

## Architecture

```
backend/
│
├── app/
│   ├── core/
│   │   ├── config.py           # Environment and OpenAI setup
│   │   └── security.py         # Simple API key-based access
│   │
│   ├── routers/
│   │   └── export.py           # Routes: /sample-data, /export
│   │
│   ├── services/
│   │   ├── llm_service.py      # LLMClient: enrichment via OpenAI or fallback rules
│   │   ├── rules_utils.py      # Utilities for reading and resolving rules
│   │   ├── transform_service.py# Pandas transformations and deterministic enrichments
│   │   ├── main.py             # FastAPI app initialization
│   │   └── schemas.py          # Shared types
│   │
│   └── __init__.py
│
├── data/
│   └── sample_test3.json       # JSON rule file for coverage templates
│
├── tests/                      # Unit tests (Pytest)
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_llm_path.py
│   ├── test_rules_utils.py
│   └── test_transform_service.py
│
├── Dockerfile
├── requirements.txt
├── pytest.ini
└── .env
```

---

## Features

### 1. **Endpoints**

| Method | Path           | Description                                              |
| ------ | -------------- | -------------------------------------------------------- |
| `GET`  | `/sample-data` | Returns the enrichment rules (`sample_test3.json`)       |
| `POST` | `/export`      | Accepts Excel file + sheet name → returns enriched Excel |

### 2. **Rule-driven enrichment**

* The backend reads `sample_test3.json` which defines coverage templates (`TRACTOS`, `REMOLQUES`) and logical assignment rules (`reglas_asignacion`).
* Each row is mapped to its coverage type based on `"TIPO DE UNIDAD"`.

### 3. **LLM-powered enrichment (optional)**

* Uses **OpenAI GPT-4o-mini** (or any provided model).
* When the environment has a valid `OPENAI_API_KEY`, it enriches rows via Chat Completions (`response_format=json_object`).
* If the key is not present, it automatically **falls back to deterministic rules**.

### 4. **Excel parsing**

* Uses `pandas` and `openpyxl` for flexible reading and cleaning.
* Handles irregular headers, merged cells, and missing names.
* Ensures data normalization before transformation.

### 5. **Export pipeline**

1. Parse uploaded Excel (`pandas.ExcelFile`)
2. Identify sheet and headers
3. Apply rules (via `LLMClient` or fallback logic)
4. Generate new Excel with added columns:

   ```
   DANOS MATERIALES LIMITES
   DANOS MATERIALES DEDUCIBLES
   ROBO TOTAL LIMITES
   ROBO TOTAL DEDUCIBLES
   ```
5. Return as downloadable `.xlsx` file.

---

##  Rule Example

`data/sample_test3.json` defines the enrichment rules:

```json
{
  "coberturas_por_tipo": {
    "TRACTOS": {
      "tipo_cobertura": "AMPLIA",
      "coberturas": {
        "DANOS MATERIALES": {"LIMITES": "VALOR CONVENIDO", "DEDUCIBLES": "10 %"},
        "ROBO TOTAL": {"LIMITES": "VALOR CONVENIDO", "DEDUCIBLES": "10 %"}
      }
    },
    "REMOLQUES": {
      "tipo_cobertura": "AMPLIA",
      "coberturas": {
        "DANOS MATERIALES": {"LIMITES": "VALOR CONVENIDO", "DEDUCIBLES": "5 %"},
        "ROBO TOTAL": {"LIMITES": "VALOR CONVENIDO", "DEDUCIBLES": "5 %"}
      }
    }
  }
}
```

Example output after enrichment:

| TIPO DE UNIDAD | Desci.                 | MOD  | NO.SERIE          | DANOS MATERIALES LIMITES | DANOS MATERIALES DEDUCIBLES | ROBO TOTAL LIMITES | ROBO TOTAL DEDUCIBLES |
| -------------- | ---------------------- | ---- | ----------------- | ------------------------ | --------------------------- | ------------------ | --------------------- |
| TRACTO         | TR FREIGHTLINER        | 2022 | 3AKJHPDV7NSNC4904 | VALOR CONVENIDO          | 10 %                        | VALOR CONVENIDO    | 10 %                  |
| TANQUE         | TANQUE ATRO 31,500 LTS | 2025 | 3ELDDMS51S6000787 | VALOR CONVENIDO          | 5 %                         | VALOR CONVENIDO    | 5 %                   |

---

## Tests

Unit tests are implemented using **pytest**, covering:

| Test file                   | Scope                                            |
| --------------------------- | ------------------------------------------------ |
| `test_api.py`               | Endpoint integration (`/sample-data`, `/export`) |
| `test_llm_path.py`          | LLMClient behavior (real & fallback)             |
| `test_rules_utils.py`       | Rule parsing utilities                           |
| `test_transform_service.py` | Deterministic transformation logic               |

Run all tests:

```bash
pytest -q
```

Expected result:

```
.......                                                                                                           [100%]
7 passed in 0.39s
```

---

## Docker Support

The project includes a ready-to-run Dockerfile:

```dockerfile
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY data ./data
COPY .env ./.env
EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
```

### Run locally

```bash
docker build -t excel-ai-backend .
docker run -p 8000:8000 excel-ai-backend
```

Access the API:

```
http://localhost:8000/docs
```

---

## 🧰 Requirements

```
fastapi
uvicorn[standard]
pandas
openpyxl
python-multipart
httpx
pydantic-settings
openai>=1.40.0
pytest
orjson
```

---

## ⚙️ Environment Variables (`.env`)

```bash
OPENAI_API_KEY=sk-xxxxx           # Optional (if you want real LLM enrichment)
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1
BACKEND_API_KEY=my_secret_key
```

---

## Design Decisions

* **Hybrid enrichment pipeline:** LLM is optional; the fallback rules guarantee deterministic results.
* **Extensible structure:** easy to add new rule formats or other AI models.
* **JSON-based rules:** the backend doesn’t hardcode logic — it reads from `sample_test3.json`.
* **Separation of concerns:** core logic is isolated in `services/`, keeping routers lightweight.
* **Unit tested:** every critical function is validated via `pytest`.

---

## Deployment Options

You can host this backend easily on:

| Platform                              | Notes                                     |
| ------------------------------------- | ----------------------------------------- |
| **Render**                            | Free tier, Dockerfile supported           |
| **Railway.app**                       | Fast CI/CD and .env integration           |
| **Fly.io**                            | Great for lightweight FastAPI apps        |
| **Google Cloud Run**                  | Serverless, scales automatically          |
| **Vercel / Netlify (with API route)** | Optional if integrated into same monorepo |

---

## Author

**Carmen Cecilia León**
Full-Stack Developer and Software Engineer
GitHub: [@kaikrmen](https://github.com/kaikrmen)