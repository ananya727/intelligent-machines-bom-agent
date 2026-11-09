from __future__ import annotations

import base64
import html
import mimetypes
from pathlib import Path
from .models import BomResearch, ConfirmedRequirements


def _evidence(item):
    value = html.escape(item.value or "Unknown - action required")
    if item.source_url:
        value += f'<br><a href="{html.escape(str(item.source_url), quote=True)}" target="_blank" rel="noopener">Source</a>'
    return value + f'<br><span class="status">{html.escape(item.status)}</span>'


SUPPORTING_REQUIREMENTS = {"E1", "E12", "E13"}
SUPPORTING_CATEGORY_PHRASES = ("presentation tray", "loading", "handoff", "reject", "manual lid")


def _supporting_ids(confirmed: ConfirmedRequirements) -> set[str]:
    ids = set(SUPPORTING_REQUIREMENTS)
    for requirement in confirmed.analysis.equipment_requirements:
        category = requirement.category.lower()
        if any(phrase in category for phrase in SUPPORTING_CATEGORY_PHRASES):
            ids.add(requirement.id)
    return ids


def _diagram_html(diagram_path: Path | None) -> str:
    if not diagram_path or not diagram_path.exists():
        return ""
    mime = mimetypes.guess_type(diagram_path.name)[0] or "image/png"
    encoded = base64.b64encode(diagram_path.read_bytes()).decode()
    return f'''<h2>Input architecture</h2><p>The purchasing agent preserves this process design; it does not redesign the line.</p><figure><img class="diagram" src="data:{mime};base64,{encoded}" alt="Manufacturing process diagram used as the agent input"><figcaption>Process diagram used for this purchasing-agent run.</figcaption></figure>'''


def render_page(confirmed: ConfirmedRequirements, bom: BomResearch, diagram_path: Path | None = None) -> str:
    cards=[]
    supporting_ids = _supporting_ids(confirmed)
    for c in bom.candidates:
        role = "Supporting equipment" if c.requirement_id in supporting_ids else "Core process equipment"
        tech="".join(f"<li>{html.escape(e.claim)}: {_evidence(e)}</li>" for e in c.technical_evidence)
        gaps="".join(f"<li>{html.escape(g)}</li>" for g in c.qualification_gaps) or "<li>None recorded; human verification still required.</li>"
        rfq=html.escape(f"Please quote {c.manufacturer} {c.model}, including configured price, lead time, exact specifications, certifications, and operating-condition limits.", quote=True)
        cards.append(f'''<tr data-rec="{c.recommendation}"><td><span class="role">{role}</span><br><b>{html.escape(c.manufacturer)} {html.escape(c.model)}</b><br>{html.escape(c.rationale)}</td><td>{_evidence(c.price)}</td><td>{_evidence(c.lead_time)}</td><td><ul>{tech}</ul></td><td><ul>{gaps}</ul><b>Next:</b> {html.escape(c.next_action)}</td><td><a class="btn" href="{html.escape(str(c.product_url or ''), quote=True)}" target="_blank" rel="noopener">Supplier</a><button class="btn alt" data-rfq="{rfq}" onclick="copyRFQ(this)">Copy RFQ</button><select><option>Human review pending</option><option>Request quote</option><option>Trial</option><option>Reject</option></select></td></tr>''')
    assumptions="".join(f"<tr><th>{html.escape(k.replace('_',' ').title())}</th><td>{html.escape(str(v))}</td></tr>" for k,v in confirmed.human_assumptions.items())
    diagram = _diagram_html(diagram_path)
    core_count = sum(c.requirement_id not in supporting_ids for c in bom.candidates)
    support_count = len(bom.candidates) - core_count
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Interactive Purchasing BOM</title><style>
body{{font:15px/1.45 system-ui;margin:0;background:#f8f6ef;color:#17202a}}main{{max-width:1500px;margin:auto;padding:32px}}h1{{font-size:46px;margin:0}}h2{{margin-top:36px;border-bottom:2px solid}}.notice{{background:#fff4df;border-left:5px solid #b45309;padding:16px;margin:22px 0}}.summary{{display:flex;gap:12px;flex-wrap:wrap;margin:18px 0}}.metric{{background:white;border:1px solid #d7d2c7;border-radius:8px;padding:10px 14px}}figure{{margin:16px 0}}.diagram{{display:block;max-width:100%;height:auto;background:white;border:1px solid #d7d2c7}}figcaption{{color:#59636e;margin-top:6px}}table{{width:100%;border-collapse:collapse;background:white}}th,td{{border:1px solid #d7d2c7;padding:10px;vertical-align:top;text-align:left}}thead{{background:#dff1f3}}ul{{padding-left:18px}}.wrap{{overflow:auto}}.wrap table{{min-width:1150px}}.btn{{display:inline-block;border:0;border-radius:5px;padding:7px;background:#155e75;color:white;text-decoration:none;margin:2px;cursor:pointer}}.alt{{background:#475569}}.status,.role{{display:inline-block;font-size:12px;background:#ffedd5;padding:2px 6px;border-radius:20px;margin-bottom:4px}}.role{{background:#dff1f3}}select{{display:block;margin-top:8px}}small,figcaption{{color:#59636e}}details{{background:white;border:1px solid #d7d2c7;padding:12px}}summary{{cursor:pointer;font-weight:700}}</style></head><body><main>
<small>INTELLIGENT MACHINES - PART 3</small><h1>Interactive purchasing workspace</h1><p>{html.escape(confirmed.analysis.process_summary)}</p><div class="notice"><b>Human decision required.</b> This page does not authorize purchases. Unknown or weakly supported facts remain qualification gaps.</div>
<div class="summary"><div class="metric"><b>{core_count}</b> core process purchases</div><div class="metric"><b>{support_count}</b> supporting items</div><div class="metric"><b>{len(bom.candidates)}</b> total requirements covered</div></div>
{diagram}
<h2>Confirmed assumptions</h2><table>{assumptions}</table>
<h2>Integration and qualification requirements</h2><ul><li>Controls, station interfaces, and safeguarding require integrator design.</li><li>Food-contact materials, sanitation method, cold operation, and applicable ingress ratings require configuration-specific evidence.</li><li>Representative product and packaging trials must confirm handling, inspection, closure, and throughput.</li><li>Site utilities and jurisdiction-specific certifications remain human approval gates.</li></ul>
<h2>Candidate BOM</h2><p>Core equipment implements the process stations. Supporting equipment covers loading, accepted-product handoff, and reject/rework handling. Linked specifications are supplier claims, not independent certification.</p><label>Recommendation filter: <select id="filter" onchange="filterRows()"><option value="all">All</option><option value="recommended">Recommended</option><option value="alternative">Alternatives</option><option value="not_qualified">Not qualified</option></select></label><div class="wrap"><table><thead><tr><th>Equipment and role</th><th>Price</th><th>Lead time</th><th>Published technical evidence</th><th>Gaps and action</th><th>Human action</th></tr></thead><tbody id="bomRows">{''.join(cards)}</tbody></table></div>
<h2>Open decisions</h2><details><summary>Show detailed human decisions from the sourcing run</summary><ul>{''.join(f'<li>{html.escape(x)}</li>' for x in bom.human_decisions_required)}</ul></details>
<script>function filterRows(){{let v=document.getElementById('filter').value;document.querySelectorAll('#bomRows tr').forEach(r=>r.hidden=v!=='all'&&r.dataset.rec!==v)}}async function copyRFQ(b){{try{{await navigator.clipboard.writeText(b.dataset.rfq);b.textContent='Copied'}}catch(e){{prompt('Copy RFQ:',b.dataset.rfq)}}}}</script></main></body></html>'''


def write_page(path: Path, confirmed: ConfirmedRequirements, bom: BomResearch, diagram_path: Path | None = None):
    path.write_text(render_page(confirmed, bom, diagram_path), encoding="utf-8")

