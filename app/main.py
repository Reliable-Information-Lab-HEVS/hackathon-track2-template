"""Track 2 export control advisor — minimal skeleton. Implement your advisor here.

See README.md for the full contract (request blocks, response shape, citations).
"""

import json
import os
import time
import urllib.request
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Track 2 export control advisor")

# The data is mounted read-only at /corpus:
#   legislation/    20 PDFs   KMG, KMV, GKG, GKV, EmbG in de/fr/it/en
#   control_lists/   6 PDFs   dual-use list and Annex 3, de/fr/it only
#   parties/        public_sanctions.json, internal_flagged.json
CORPUS_DIR = os.environ.get("CORPUS_DIR", "/corpus")

# Inference endpoint (OpenAI-compatible) — see inference.env.example.
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
MODEL = os.environ.get("MODEL")  # default chat model, used when a request has no `model`

# A request may ask for any model the inference endpoint serves, in its optional
# `model` field. We check it against the endpoint's /models list, cached for a
# few minutes so the check does not eat into your rate limit.
MODELS_TTL_SECONDS = 600
_models_cache: tuple[float, set[str]] = (0.0, set())


def available_models() -> set[str]:
    global _models_cache
    fetched_at, models = _models_cache
    if time.monotonic() - fetched_at < MODELS_TTL_SECONDS:
        return models
    try:
        req = urllib.request.Request(
            f"{OPENAI_BASE_URL.rstrip('/')}/models",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            models = {m["id"] for m in json.load(resp)["data"]}
        _models_cache = (time.monotonic(), models)
    except Exception:
        pass  # endpoint unreachable: keep the last list we had
    return _models_cache[1]


class ModelNotAvailable(Exception):
    pass


@app.exception_handler(ModelNotAvailable)
def model_not_available(request: Request, exc: ModelNotAvailable) -> JSONResponse:
    return JSONResponse(status_code=400, content={"error": "model not available"})


def pick_model(requested: str | None) -> str:
    """The chat model for this request: the requested one, else the MODEL default.
    Never falls back silently: a model the endpoint does not serve is a 400."""
    if not requested or requested == MODEL:
        return MODEL
    if requested not in available_models():
        raise ModelNotAvailable()
    return requested


class Item(BaseModel):
    description: str | None = None
    # Free-form: any keys, any units, no guarantee a given parameter is present.
    specifications: dict[str, Any] | None = None


class Transaction(BaseModel):
    consignee: str | None = None
    end_user: str | None = None
    intermediaries: list[str] | None = None
    destination: str | None = None
    stated_end_use: str | None = None
    routing: list[str] | None = None
    value_chf: float | None = None


class Document(BaseModel):
    type: str | None = None
    text: str


class AdviseRequest(BaseModel):
    """At least one block is present. query / item / transaction appear at most
    once; documents is a list. When several are present they are related: the
    item is the product in the transaction and the query is scoped to both."""

    query: str | None = None
    item: Item | None = None
    transaction: Transaction | None = None
    documents: list[Document] | None = None
    model: str | None = None     # optional, not a block: chat model for this request


@app.post("/advise")
def advise(req: AdviseRequest) -> dict:
    model = pick_model(req.model)  # use this model for the chat completions
    # TODO: implement your advisor.
    

    response: dict[str, Any] = {"refer_to_authority": False}

    if req.query is not None:
        response["query"] = {"answer": "TODO: not implemented", "citations": []}

    if req.item is not None:
        response["classification"] = {
            "controlled": False,
            "regime": "none",          # war_materiel | specific_military | dual_use | none
            "entries": [],
            "deciding_text": "TODO: not implemented",
            "citations": [],
        }

    if req.transaction is not None:
        response["transaction"] = {
            # NO_LICENCE_REQUIRED | LICENCE_REQUIRED | PROHIBITED | REFER_TO_AUTHORITY
            "verdict": "REFER_TO_AUTHORITY",
            "authority": None,
            "answer": "TODO: not implemented",
            "citations": [],
        }

    return response


@app.get("/health")
def health() -> dict:
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
