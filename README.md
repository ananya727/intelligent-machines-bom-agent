# Intelligent Machines Part 3 - Diagram to Purchasing Page

A lightweight Python agent that converts a manufacturing process diagram into an evidence-backed interactive BOM. It preserves the input architecture, asks for critical missing assumptions, researches exact equipment candidates, and leaves purchasing decisions with a human.

## Workflow

```text
diagram image -> structured requirements -> human assumptions
              -> evidence-backed candidate research -> BOM JSON -> HTML
```

The model handles image interpretation and web research. Python/Pydantic enforce the data contracts, and deterministic Python renders the final webpage.

## Safety and evidence rules

- No price, lead time, certification, or supplier link may be invented.
- Every commercial or technical claim needs a source URL and evidence status.
- Missing evidence becomes an explicit qualification gap or RFQ action.
- The workflow preserves stations and relationships from the diagram; it does not redesign the line.
- The webpage is decision support, never purchase authorization.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

Add your API key to `.env`, then run:

```bash
bom-agent examples/process_diagram.png \
  --assumptions examples/assumptions.json \
  --output generated/purchasing_page.html
```

Omit `--assumptions` for an interactive clarification step. Intermediate files are saved beside the output:

- `requirements.json` - diagram interpretation and questions
- `confirmed_requirements.json` - explicit human inputs
- `bom.json` - candidates, evidence, gaps, and recommendations
- `purchasing_page.html` - deterministic interactive deliverable

For a credential-free renderer check:

```bash
bom-agent render generated/example_bom.json --output generated/example_purchasing_page.html
```

## Tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## AI usage

The vision model extracts the process architecture and missing assumptions. A second model call uses hosted web search to identify and compare exact equipment. Structured outputs constrain both stages. Python performs validation and rendering. Humans confirm assumptions, resolve qualification gaps, and make final purchasing decisions.

The implementation follows official OpenAI guidance for [image inputs](https://developers.openai.com/api/docs/guides/images-vision?api-mode=responses), [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses), and [web search](https://developers.openai.com/api/docs/guides/tools-web-search).

