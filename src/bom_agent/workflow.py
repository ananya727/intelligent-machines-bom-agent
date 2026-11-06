from __future__ import annotations

import argparse
import json
from pathlib import Path
from dotenv import load_dotenv

from .models import BomResearch, ConfirmedRequirements, DiagramAnalysis
from .openai_steps import analyze_diagram, configured_client, research_candidates
from .render import write_page


def _read(path, model): return model.model_validate_json(Path(path).read_text())
def _write(path, model): Path(path).write_text(model.model_dump_json(indent=2)+"\n")


def collect_answers(analysis, supplied=None):
    answers=dict(supplied or {})
    for q in analysis.clarification_questions:
        if q.key not in answers:
            if supplied is not None:
                answers[q.key] = "Unknown - unresolved; human input required"
            else:
                print(f"\n{q.question}\nWhy: {q.why_critical}")
                answers[q.key]=input("> ").strip() or "Unknown - unresolved"
    return answers


def run(args):
    load_dotenv(); out=Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    client, model=configured_client()
    analysis=analyze_diagram(Path(args.image), client, model)
    _write(out.parent/"requirements.json", analysis)
    supplied=json.loads(Path(args.assumptions).read_text()) if args.assumptions else None
    confirmed=ConfirmedRequirements(analysis=analysis, human_assumptions=collect_answers(analysis, supplied))
    _write(out.parent/"confirmed_requirements.json", confirmed)
    bom=research_candidates(confirmed, client, model, out.parent / "research_batches")
    _write(out.parent/"bom.json", bom); write_page(out, confirmed, bom)
    print(f"Generated {out}")


def render_only(args):
    bom=_read(args.bom, BomResearch)
    confirmed_path=Path(args.confirmed) if args.confirmed else Path(args.bom).with_name("example_confirmed_requirements.json")
    write_page(Path(args.output), _read(confirmed_path, ConfirmedRequirements), bom)
    print(f"Generated {args.output}")


def main(argv=None):
    import sys
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "render":
        p=argparse.ArgumentParser(description="Render saved BOM JSON")
        p.add_argument("command"); p.add_argument("bom"); p.add_argument("--confirmed"); p.add_argument("--output", required=True)
        render_only(p.parse_args(argv)); return
    p=argparse.ArgumentParser(description="Diagram-to-interactive-BOM agent")
    p.add_argument("image"); p.add_argument("--assumptions"); p.add_argument("--output", default="generated/purchasing_page.html")
    run(p.parse_args(argv))


if __name__ == "__main__": main()

