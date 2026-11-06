from __future__ import annotations

import html
from pathlib import Path
from .models import BomResearch, ConfirmedRequirements


def _evidence(item):
    value = html.escape(item.value or "Unknown - action required")
    if item.source_url:
        value += f'<br><a href="{html.escape(str(item.source_url), quote=True)}" target="_blank" rel="noopener">Source</a>'
    return value + f'<br><span class="status">{html.escape(item.status)}</span>'


def render_page(confirmed: ConfirmedRequirements, bom: BomResearch) -> str:
    cards=[]
    for c in bom.candidates:
        tech="".join(f"<li>{html.escape(e.claim)}: {_evidence(e)}</li>" for e in c.technical_evidence)
        gaps="".join(f"<li>{html.escape(g)}</li>" for g in c.qualification_gaps) or "<li>None recorded; human verification still required.</li>"
        rfq=html.escape(f"Please quote {c.manufacturer} {c.model}, including configured price, lead time, exact specifications, certifications, and operating-condition limits.", quote=True)
        cards.append(f'''<tr data-rec="{c.recommendation}"><td><b>{html.escape(c.manufacturer)} {html.escape(c.model)}</b><br>{html.escape(c.rationale)}</td><td>{_evidence(c.price)}</td><td>{_evidence(c.lead_time)}</td><td><ul>{tech}</ul></td><td><ul>{gaps}</ul><b>Next:</b> {html.escape(c.next_action)}</td><td><a class="btn" href="{html.escape(str(c.product_url or ''), quote=True)}" target="_blank">Supplier</a><button class="btn alt" data-rfq="{rfq}" onclick="copyRFQ(this)">Copy RFQ</button><select><option>Human review pending</option><option>Request quote</option><option>Trial</option><option>Reject</option></select></td></tr>''')
    assumptions="".join(f"<tr><th>{html.escape(k.replace('_',' ').title())}</th><td>{html.escape(str(v))}</td></tr>" for k,v in confirmed.human_assumptions.items())
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Interactive Purchasing BOM</title><style>
body{{font:15px/1.45 system-ui;margin:0;background:#f8f6ef;color:#17202a}}main{{max-width:1500px;margin:auto;padding:32px}}h1{{font-size:46px;margin:0}}h2{{margin-top:36px;border-bottom:2px solid}}.notice{{background:#fff4df;border-left:5px solid #b45309;padding:16px;margin:22px 0}}table{{width:100%;border-collapse:collapse;background:white}}th,td{{border:1px solid #d7d2c7;padding:10px;vertical-align:top;text-align:left}}thead{{background:#dff1f3}}ul{{padding-left:18px}}.wrap{{overflow:auto}}.btn{{border:0;border-radius:5px;padding:7px;background:#155e75;color:white;text-decoration:none;margin:2px;cursor:pointer}}.alt{{background:#475569}}.status{{font-size:12px;background:#ffedd5;padding:2px 6px;border-radius:20px}}select{{display:block;margin-top:8px}}small{{color:#59636e}}</style></head><body><main>
<small>INTELLIGENT MACHINES - PART 3</small><h1>Interactive purchasing workspace</h1><p>{html.escape(confirmed.analysis.process_summary)}</p><div class="notice"><b>Human decision required.</b> This page does not authorize purchases. Unknown or weakly supported facts remain qualification gaps.</div>
<h2>Confirmed assumptions</h2><table>{assumptions}</table><h2>Candidate BOM</h2><label>Filter: <select id="filter" onchange="filterRows()"><option value="all">All</option><option value="recommended">Recommended</option><option value="alternative">Alternatives</option><option value="not_qualified">Not qualified</option></select></label><div class="wrap"><table><thead><tr><th>Equipment</th><th>Price</th><th>Lead time</th><th>Technical evidence</th><th>Gaps and action</th><th>Human action</th></tr></thead><tbody id="bomRows">{''.join(cards)}</tbody></table></div>
<h2>Open decisions</h2><ul>{''.join(f'<li>{html.escape(x)}</li>' for x in bom.human_decisions_required)}</ul>
<script>function filterRows(){{let v=document.getElementById('filter').value;document.querySelectorAll('#bomRows tr').forEach(r=>r.hidden=v!=='all'&&r.dataset.rec!==v)}}async function copyRFQ(b){{try{{await navigator.clipboard.writeText(b.dataset.rfq);b.textContent='Copied'}}catch(e){{prompt('Copy RFQ:',b.dataset.rfq)}}}}</script></main></body></html>'''


def write_page(path: Path, confirmed: ConfirmedRequirements, bom: BomResearch):
    path.write_text(render_page(confirmed, bom), encoding="utf-8")

