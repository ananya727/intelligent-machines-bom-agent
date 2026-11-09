# Intelligent Machines Part 3: Diagram to Purchasing Page

This lightweight Python demonstration turns a manufacturing-process diagram into an evidence-backed, interactive purchasing BOM.

## [Open the live purchasing webpage](https://ananya727.github.io/intelligent-machines-bom-agent/)

## [Open the simplified three-arm example](https://ananya727.github.io/intelligent-machines-bom-agent/simplified/)

The self-contained example is published from `docs/index.html`. Reviewers can inspect the original diagram, recommendations, evidence, qualification gaps, RFQ actions, and human decision controls without an API key or build step.

The checked-in example is a real run against my Part 1 process diagram. It detected 11 process steps and 13 equipment requirements, researched one candidate for every requirement, preserved unsupported values as unknown, and generated the HTML deterministically. The webpage distinguishes 10 core process purchases from 3 supporting items without changing the input architecture.

## Approach and reflection

For Part 3, I approached the problem by breaking down the process I'd followed manually in Part 2 and identifying which steps could be automated. I kept the implementation fairly lightweight, using AI to interpret the diagram and research equipment, with structured data and deterministic code for generating the purchasing webpage.

One thing that became clear was the importance of human review, particularly when confirming operating assumptions, evaluating certifications, and making purchasing decisions. The generated BOM is a starting point rather than a fully qualified purchasing list, since supplier pricing and lead times often require RFQs.

I also ran the same workflow on a simplified version of my original process diagram to explore the feedback on reducing moving parts.

### Architecture comparison

The second run uses the simpler Part 2 planning case: three robot arms instead of seven, one tray per index instead of two, manual grape placement, and manual lid closure rather than an automatic lid applicator. The agent preserved that input and extracted 9 process steps and 11 equipment requirements, compared with 11 steps and 13 requirements for the original diagram. The Part 2 model estimates approximately 135 acceptable trays/hour using a 22-second bottleneck, 2-second index, and 90% effectiveness. That lower rate reduces mechanisms and robot count, but the longer production window and staffing plan require customer approval before this architecture can replace the original higher-throughput case.

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

- [Live purchasing page](https://ananya727.github.io/intelligent-machines-bom-agent/) - published reviewer experience
- [`docs/index.html`](docs/index.html) - checked-in self-contained page
- [`docs/requirements.json`](docs/requirements.json) - real diagram interpretation
- [`docs/confirmed_requirements.json`](docs/confirmed_requirements.json) - requirements plus human assumptions
- [`docs/bom.json`](docs/bom.json) - live-researched candidates and claim-level evidence
- [`examples/process_diagram.png`](examples/process_diagram.png) - example input
- [`docs/simplified/index.html`](docs/simplified/index.html) - second purchasing page for the simplified architecture
- [`examples/simplified_process_diagram.png`](examples/simplified_process_diagram.png) - simplified three-arm input

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
generated/           real run artifacts; local runs also cache ignored research batches
docs/                GitHub Pages-ready copy of the reviewed output
tests/               focused renderer/evidence safety test
```

## AI usage

The vision model interprets the diagram. The research stage uses hosted web search to find exact equipment and source evidence. Pydantic validates intermediate JSON, and ordinary Python generates the final HTML. AI recommendations remain subject to human engineering and purchasing review.

Implementation references: [OpenAI image inputs](https://developers.openai.com/api/docs/guides/images-vision?api-mode=responses), [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses), and [web search](https://developers.openai.com/api/docs/guides/tools-web-search).
