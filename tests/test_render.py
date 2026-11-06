import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from bom_agent.models import *
from bom_agent.render import render_page


class RenderTests(unittest.TestCase):
    def test_unknowns_remain_unknown_and_human_controlled(self):
        analysis=DiagramAnalysis(process_summary="Line",process_steps=[],equipment_requirements=[],clarification_questions=[],extraction_uncertainties=[])
        confirmed=ConfirmedRequirements(analysis=analysis,human_assumptions={"temperature":"36-40 F"})
        unknown=Evidence(claim="price",value=None,source_url=None,source_title=None,retrieved_date=None,status="unknown")
        candidate=Candidate(requirement_id="r1",manufacturer="Maker",model="M1",product_url=None,recommendation="alternative",rationale="Needs evidence",price=unknown,lead_time=unknown,technical_evidence=[],qualification_gaps=["Certification"],next_action="RFQ")
        page=render_page(confirmed,BomResearch(candidates=[candidate],overall_uncertainties=[],human_decisions_required=["Approve only after evidence"]))
        self.assertIn("Unknown - action required",page)
        self.assertIn("Human review pending",page)
        self.assertNotIn("$0",page)


if __name__ == "__main__": unittest.main()
