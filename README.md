# Intelligent Machines Part 3: Diagram to Purchasing Page

This lightweight Python demonstration turns a manufacturing-process diagram into an evidence-backed, interactive purchasing BOM.

## [Open the generated purchasing webpage](docs/index.html)

When GitHub Pages is enabled for `docs/`, the same self-contained page opens as a normal website without a download, API key, or build step. Intended Pages URL:

`https://ananya-tacta.github.io/intelligent-machines-bom-agent/`

The checked-in example is a real run against my Part 1 process diagram. It detected 11 process steps and 13 equipment requirements, researched one candidate for every requirement, preserved unsupported values as unknown, and generated the HTML deterministically.

## Workflow

```text
Process diagram image
        ↓
Vision extraction → structured process steps and equipment requirements
        ↓
Human checkpoint → operating conditions, certifications, utilities, constraints
        ↓
Live web research → exact candidates, evidence, unknowns, qualification gaps
        ↓
Validated BOM JSON
        ↓
Deterministic Python renderer → self-contained interactive HTML
        ↓
Human purchasing decision
```

The agent respects the diagram's architecture. It extracts the line that was drawn; it does not redesign or simplify it.

## Human checkpoints

People remain responsible for:

1. Confirming missing operating assumptions before sourcing.
2. Reviewing whether each candidate actually fits the application.
3. Resolving RFQs, trials, certifications, cleaning compatibility, utilities, and integration details.
4. Making the final purchasing decision.

Unknown prices, lead times, certifications, or specifications are never filled with estimates. They remain explicit qualification gaps and next actions.

## Run locally

Requirements: Python 3.10+ and an OpenAI API key with Responses API access.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

Add the API key to `.env` (ignored by Git), then run:

```bash
bom-agent examples/process_diagram.png \
  --assumptions examples/assumptions.json \
  --output generated/purchasing_page.html
```

Omit `--assumptions` to answer clarification questions interactively. The default model is `gpt-6.1-sol` to keep the demonstration economical. Research is processed in small saved batches, so interrupted runs resume without repeating completed searches.

Regenerate HTML from saved JSON without an API call:

```bash
bom-agent render generated/bom.json \
  --confirmed generated/confirmed_requirements.json \
  --output generated/purchasing_page.html
```

## Output artifacts

- [`docs/index.html`](docs/index.html) - GitHub Pages-ready purchasing page
- [`docs/requirements.json`](docs/requirements.json) - real diagram interpretation
- [`docs/confirmed_requirements.json`](docs/confirmed_requirements.json) - requirements plus human assumptions
- [`docs/bom.json`](docs/bom.json) - live-researched candidates and claim-level evidence
- [`examples/process_diagram.png`](examples/process_diagram.png) - example input

## Test result

The submission run produced:

- 11 process steps
- 13 equipment requirements
- 13 sourced candidates, with no missing or duplicate requirement IDs
- Qualification gaps on all 13 candidates
- Source URLs for every recorded technical-evidence claim
- 12 prices and 12 lead times left unknown because exact published evidence was unavailable
- 1 exact listing price and dispatch estimate, labeled `supplier_claim` rather than a quote

Run local checks:

```bash
python -m unittest discover -s tests -v
python -m py_compile src/bom_agent/*.py
```

## Limitations

- Diagram interpretation and web research are model-dependent and require human review.
- Public product pages rarely provide configured-system pricing or committed lead times; most production equipment remains RFQ-only.
- Supplier claims are evidence, not independent certification.
- The example does not validate robot reach, cycle time, food trials, controls integration, guarding, sanitation procedures, or jurisdiction-specific compliance.
- The candidate list is decision support, not an approved engineering BOM.
- The demonstration provides one candidate per detected requirement. A production workflow would broaden alternatives after architecture and qualification criteria are confirmed.

## Repository structure

```text
src/bom_agent/       vision, research, models, workflow, and renderer
examples/            input diagram and confirmed assumptions
generated/           real run artifacts and resumable research batches
docs/                GitHub Pages-ready copy of the reviewed output
tests/               focused renderer/evidence safety test
```

## AI usage

The vision model interprets the diagram. The research stage uses hosted web search to find exact equipment and source evidence. Pydantic validates intermediate JSON, and ordinary Python generates the final HTML. AI recommendations remain subject to human engineering and purchasing review.

Implementation references: [OpenAI image inputs](https://developers.openai.com/api/docs/guides/images-vision?api-mode=responses), [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses), and [web search](https://developers.openai.com/api/docs/guides/tools-web-search).
