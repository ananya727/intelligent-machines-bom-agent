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
    response = client.responses.parse(
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
        text_format=DiagramAnalysis,
    )
    return response.output_parsed


def research_candidates(confirmed: ConfirmedRequirements, client: OpenAI, model: str, cache_dir: Path | None = None) -> BomResearch:
    requirements = confirmed.analysis.equipment_requirements
    results = []
    for start in range(0, len(requirements), 2):
        cache_file = cache_dir / f"batch_{start // 2 + 1:02d}.json" if cache_dir else None
        if cache_file and cache_file.exists():
            results.append(BomResearch.model_validate_json(cache_file.read_text()))
            continue
        research_input = {
            "process_summary": confirmed.analysis.process_summary,
            "equipment_requirements": [item.model_dump() for item in requirements[start:start + 2]],
            "human_assumptions": confirmed.human_assumptions,
        }
        prompt = f"""Research exact purchasable equipment candidates for these confirmed requirements:
{json.dumps(research_input, indent=2)}

Use live web search. Prefer manufacturer datasheets and official product pages; use distributors only for exact-model
price or stock evidence. Never infer one model's certification, price, lead time, or rating from another model or a
product family. Use null/unknown when evidence is absent. Record today's retrieval date ({date.today().isoformat()}).
Give a recommended option and useful alternative where evidence supports them. Preserve the input architecture.
Every factual claim must have its own source URL. Final purchasing remains a human decision."""
        response = client.responses.parse(
            model=model,
            max_output_tokens=4500,
            tools=[{"type": "web_search", "external_web_access": True}],
            tool_choice="required",
            include=["web_search_call.action.sources"],
            input=prompt + "\nBe concise. Return exactly one candidate per requirement in this batch. Limit technical_evidence to the two most decision-relevant claims per candidate.",
            text_format=BomResearch,
        )
        results.append(response.output_parsed)
        if cache_file:
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(response.output_parsed.model_dump_json(indent=2) + "\n")
    return BomResearch(
        candidates=[candidate for result in results for candidate in result.candidates],
        overall_uncertainties=list(dict.fromkeys(item for result in results for item in result.overall_uncertainties)),
        human_decisions_required=list(dict.fromkeys(item for result in results for item in result.human_decisions_required)),
    )


def configured_client() -> tuple[OpenAI, str]:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set. Copy .env.example to .env and add a key.")
    return OpenAI(), os.getenv("OPENAI_MODEL", "gpt-6-astra")

