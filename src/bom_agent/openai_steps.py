from __future__ import annotations

import base64
import json
import mimetypes
import os
from datetime import date
from pathlib import Path

from openai import OpenAI

from .models import BomResearch, ConfirmedRequirements, DiagramAnalysis


def _schema(model):
    return {"type": "json_schema", "name": model.__name__, "strict": True, "schema": model.model_json_schema()}


def analyze_diagram(image: Path, client: OpenAI, model: str) -> DiagramAnalysis:
    mime = mimetypes.guess_type(image.name)[0] or "image/png"
    encoded = base64.b64encode(image.read_bytes()).decode()
    response = client.responses.create(
        model=model,
        instructions=(
            "Interpret the manufacturing process diagram exactly as drawn. Preserve its stations, flow, quantities, "
            "operators, inputs, outputs, and relationships. Do not redesign or simplify it. Extract equipment needs "
            "and ask only purchasing-critical questions, especially operating conditions, food contact, washdown, "
            "utilities, throughput, jurisdiction, and certifications. Treat unclear handwriting as uncertainty."
        ),
        input=[{"role": "user", "content": [
            {"type": "input_text", "text": "Extract the process and purchasing requirements from this diagram."},
            {"type": "input_image", "image_url": f"data:{mime};base64,{encoded}", "detail": "original"},
        ]}],
        text={"format": _schema(DiagramAnalysis)},
    )
    return DiagramAnalysis.model_validate_json(response.output_text)


def research_candidates(confirmed: ConfirmedRequirements, client: OpenAI, model: str) -> BomResearch:
    prompt = f"""Research exact purchasable equipment candidates for these confirmed requirements:
{confirmed.model_dump_json(indent=2)}

Use live web search. Prefer manufacturer datasheets and official product pages; use distributors only for exact-model
price or stock evidence. Never infer one model's certification, price, lead time, or rating from another model or a
product family. Use null/unknown when evidence is absent. Record today's retrieval date ({date.today().isoformat()}).
Give a recommended option and useful alternative where evidence supports them. Preserve the input architecture.
Every factual claim must have its own source URL. Final purchasing remains a human decision."""
    response = client.responses.create(
        model=model,
        tools=[{"type": "web_search", "external_web_access": True}],
        tool_choice="required",
        include=["web_search_call.action.sources"],
        input=prompt,
        text={"format": _schema(BomResearch)},
    )
    return BomResearch.model_validate_json(response.output_text)


def configured_client() -> tuple[OpenAI, str]:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set. Copy .env.example to .env and add a key.")
    return OpenAI(), os.getenv("OPENAI_MODEL", "gpt-6-astra")

