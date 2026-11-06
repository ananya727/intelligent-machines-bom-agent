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
    bom=research_candidates(confirmed, client, model)
    _write(out.parent/"bom.json", bom); write_page(out, confirmed, bom)
    print(f"Generated {out}")


def render_only(args):
    bom=_read(args.bom, BomResearch)
    confirmed_path=Path(args.confirmed) if args.confirmed else Path(args.bom).with_name("example_confirmed_requirements.json")
    write_page(Path(args.output), _read(confirmed_path, ConfirmedRequirements), bom)
    print(f"Generated {args.output}")


def main(argv=None):
    p=argparse.ArgumentParser(description="Diagram-to-interactive-BOM agent")
    sub=p.add_subparsers(dest="command")
    r=sub.add_parser("render"); r.add_argument("bom"); r.add_argument("--confirmed"); r.add_argument("--output", required=True)
    p.add_argument("image", nargs="?"); p.add_argument("--assumptions"); p.add_argument("--output", default="generated/purchasing_page.html")
    args=p.parse_args(argv)
    if args.command=="render": render_only(args)
    elif args.image: run(args)
    else: p.error("provide an image or use the render subcommand")


if __name__ == "__main__": main()

