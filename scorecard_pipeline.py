"""Combine price and public-source artifacts into one fail-closed report."""
import json
import os
from pathlib import Path
from evidence_scorecard import build
from downside_guard import assess
from retrospective import replay
def main():
    directory=Path("artifacts")
    price_path=directory/"openbb_probe.json"
    research_path=directory/"public_research.json"
    price=json.loads(price_path.read_text()) if price_path.exists() else {}
    research=json.loads(research_path.read_text()) if research_path.exists() else {}
    result=build(price,research)
    observations=price.get("observations",[])
    downside=assess(observations)
    result["downside_guard"]=downside
    if downside["severity"] in ("HIGH","CRITICAL"):
        result["status"]="DOWNSIDE_RISK_WARNING"
    (directory/"downside_retrospective.json").write_text(json.dumps(replay(observations),indent=2)+"\n")
    directory.mkdir(parents=True,exist_ok=True)
    (directory/"sentinel_scorecard.json").write_text(json.dumps(result,indent=2)+"\n")
    print("scorecard",result["status"],"downside_severity",downside["severity"],"trading_allowed",result["validated_for_trading"])
    if downside["severity"] in ("HIGH","CRITICAL"):
        print("::warning title=AVCT downside surveillance::"+downside["severity"]+": "+", ".join(downside["warnings"]))
    summary=os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary,"a") as out:
            out.write("## AVCT downside surveillance\\n\\n")
            out.write("**Severity:** "+downside["severity"]+"\\n\\n")
            out.write("**Signals:** "+(", ".join(downside["warnings"]) or "None confirmed")+"\\n\\n")
            out.write("Research warning only; not an automated trade instruction.\\n")
if __name__=="__main__":main()
