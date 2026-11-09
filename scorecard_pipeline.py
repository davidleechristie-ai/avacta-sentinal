"""Combine price and public-source artifacts into one fail-closed report."""
import json
import os
from pathlib import Path
from evidence_scorecard import build
from downside_guard import assess
from retrospective import replay
from risk_event import build_event
from session_gate import session_gate
def main():
    directory=Path("artifacts")
    directory.mkdir(parents=True,exist_ok=True)
    price_path=directory/"openbb_probe.json"
    research_path=directory/"public_research.json"
    price=json.loads(price_path.read_text()) if price_path.exists() else {}
    research=json.loads(research_path.read_text()) if research_path.exists() else {}
    result=build(price,research)
    observations=price.get("observations",[])
    # A provisional intraday bar must not suppress a valid prior completed-session warning.
    latest_date=max((str(x.get("date",""))[:10] for x in observations),default=None)
    latest_gate=session_gate(latest_date)
    completed=[x for x in observations if session_gate(str(x.get("date",""))[:10])["status"]=="ACCEPTED"]
    downside=assess(completed)
    downside["latest_provider_session"]=latest_date
    downside["latest_provider_session_gate"]=latest_gate
    gate=session_gate(downside.get("latest_session"))
    downside["session_gate"]=gate
    if gate["status"]!="ACCEPTED":
        downside["status"]="PRICE_SESSION_"+gate["status"]
        downside["severity"]="UNKNOWN"
        downside["warnings"].append("PRICE_SESSION_"+gate["status"])
    result["downside_guard"]=downside
    event=build_event(downside)
    (directory/"risk_event.json").write_text(json.dumps(event,indent=2)+"\n")
    if downside["severity"] in ("HIGH","CRITICAL"):
        result["status"]="DOWNSIDE_RISK_WARNING"
    (directory/"downside_retrospective.json").write_text(json.dumps(replay(completed),indent=2)+"\n")
    (directory/"sentinel_scorecard.json").write_text(json.dumps(result,indent=2)+"\n")
    print("scorecard",result["status"],"downside_severity",downside["severity"],"trading_allowed",result["validated_for_trading"])
    if downside["severity"] in ("HIGH","CRITICAL"):
        print("::warning title=AVCT downside surveillance::"+downside["severity"]+": "+", ".join(downside["warnings"]))
    summary=os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary,"a") as out:
            out.write("## AVCT downside surveillance\n\n")
            out.write("**Severity:** "+downside["severity"]+"\n\n")
            out.write("**Signals:** "+(", ".join(downside["warnings"]) or "None confirmed")+"\n\n")
            out.write("Research warning only; not an automated trade instruction.\n")
if __name__=="__main__":main()
