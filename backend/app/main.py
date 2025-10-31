from __future__ import annotations
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .routers import export
from .services.llm_service import LLMClient
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

app = FastAPI(title="Excel Viewer & AI Modifier", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/llm/status")
def llm_status(probe: bool = False):
    llm = LLMClient()
    status = {
        "enabled": llm.enabled,
        "model": llm.model if llm.enabled else "",
        "probed": False,
        "ok": False,
        "error": "",
    }
    if not llm.enabled or not probe:
        return status

    try:
        resp = llm.client.chat.completions.create(
            model=llm.model,
            messages=[
                {"role": "system", "content": "Return a JSON object with {'alive': true} only."},
                {"role": "user", "content": '{"request":"health"}'},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        text = (resp.choices[0].message.content or "").strip()
        import orjson
        data = orjson.loads(text)
        status["probed"] = True
        status["ok"] = bool(isinstance(data, dict) and data.get("alive") is True)
        return status
    except Exception as e:
        status["probed"] = True
        status["ok"] = False
        status["error"] = repr(e)
        return status

app.include_router(export.router, tags=["export"])
