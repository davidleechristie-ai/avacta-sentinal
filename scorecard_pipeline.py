"""Combine price and public-source artifacts into one fail-closed report."""
import json
import os
from pathlib import Path
from evidence_scorecard import build
from downside_guard import assess
from retrospective import replay
from risk_event import build_event
from session_gate import session_gate
from completed_sessions import completed_rows
from price_bars import clean_bars
from risk_transition import transition
from decision_engine import build_decision
from forward_signal_audit import audit
from signal_baseline import compare
from tradermonty_technical_review import report as technical_review
from tradermonty_weekly import weekly_review
from tradermonty_catalyst_overlay import assess_catalysts, combine
from tradermonty_pretrade import check as pretrade_check
from isa_positioning_report import build_report, markdown as positioning_markdown
from forward_levels import map_levels
from sentinel_dashboard import write_dashboard
from technical_chart import render_chart, weekly_bars
from independent_price_verification import verify
from secondary_price_feed import fetch_secondary, SecondaryFeedUnavailable
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
    clean,rejected=clean_bars(observations)
    completed,latest_date,latest_gate=completed_rows(clean)
    downside=assess(completed)
    # A second independently sourced feed is not configured. Record the gap
    # explicitly rather than inferring verification from the primary provider.
    try:
        secondary=fetch_secondary()
        # Explicit currency normalization is essential: Yahoo AVCT.L bars are
        # quoted in GBp. Only compare when the second feed states its currency.
        currency=str(secondary.get('currency') or '').upper()
        if currency not in ('GBP','GBX','GBPENCE'):
            raise SecondaryFeedUnavailable('Secondary feed currency not confirmed as GBP/GBp')
        secondary_bars=secondary['observations']
        if currency=='GBP':
            secondary_bars=[{**bar,**{k:bar[k]*100 for k in ('open','high','low','close')}} for bar in secondary_bars]
        # Require completed sessions on both feeds; never compare provisional candles.
        second_completed,_,_=completed_rows(secondary_bars)
        corroboration=verify(completed,second_completed,'yfinance',secondary['provider'])
        corroboration['secondary_provider']=secondary['provider']
    except SecondaryFeedUnavailable as exc:
        corroboration=verify(completed,None,'yfinance',None)
        corroboration['reason']=str(exc)
    (directory/'independent_price_verification.json').write_text(json.dumps(corroboration,indent=2)+'\n')
    downside["latest_provider_session"]=latest_date
    downside["latest_provider_session_gate"]=latest_gate
    gate=session_gate(downside.get("latest_session"))
    downside["session_gate"]=gate
    downside["risk_transition"]=transition(completed)
    downside["rejected_price_bars"]=len(rejected)
    downside["price_data_provenance"]="OPENBB_YFINANCE_UNVERIFIED"
    if gate["status"]!="ACCEPTED":
        downside["status"]="PRICE_SESSION_"+gate["status"]
        downside["severity"]="UNKNOWN"
        downside["warnings"].append("PRICE_SESSION_"+gate["status"])
    result["downside_guard"]=downside
    result["decision_intelligence"]=build_decision(downside, price.get("quality",{}))
    result["decision_intelligence"]["independent_price_evidence"]=corroboration
    weekly=weekly_review(completed)
    catalysts=assess_catalysts(research,result["decision_intelligence"]["as_of"])
    result["trading_skill_overlay"]=combine(result["decision_intelligence"],weekly,catalysts)
    result["manual_pretrade_gate"]=pretrade_check()
    levels=map_levels(completed,downside.get("latest_close"))
    positioning=build_report(result["decision_intelligence"],weekly,catalysts,result["trading_skill_overlay"],result["manual_pretrade_gate"],downside,levels)
    result["isa_positioning"]=positioning
    (directory/"forward_levels.json").write_text(json.dumps(levels,indent=2)+"\n")
    (directory/"isa_positioning_report.json").write_text(json.dumps(positioning,indent=2)+"\n")
    (directory/"isa_positioning_report.md").write_text(positioning_markdown(positioning))
    performance=audit(completed)
    result["forward_signal_audit"]=performance
    result["technical_chart_html"]=render_chart(completed,levels)
    result["weekly_chart_html"]=render_chart(weekly_bars(completed),levels,limit=26)
    write_dashboard(positioning,directory/"sentinel_dashboard.html",result)
    (directory/"tradermonty_weekly.json").write_text(json.dumps(weekly,indent=2)+"\n")
    (directory/"tradermonty_catalysts.json").write_text(json.dumps(catalysts,indent=2)+"\n")
    (directory/"tradermonty_pretrade.json").write_text(json.dumps(result["manual_pretrade_gate"],indent=2)+"\n")
    (directory/"tradermonty_technical_review.json").write_text(json.dumps(technical_review(completed,downside,result["decision_intelligence"]),indent=2)+"\n")
    event=build_event(downside)
    (directory/"risk_event.json").write_text(json.dumps(event,indent=2)+"\n")
    if downside["severity"] in ("HIGH","CRITICAL"):
        result["status"]="DOWNSIDE_RISK_WARNING"
    (directory/"signal_baseline.json").write_text(json.dumps(compare(completed),indent=2)+"\n")
    (directory/"forward_signal_audit.json").write_text(json.dumps(audit(completed),indent=2)+"\n")
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
            out.write("**Decision hypothesis:** "+result["decision_intelligence"]["decision"]+"\n\n")
            out.write("**Source:** TraderMonty methodology; weekly chart review not performed automatically.\n\n")
            out.write("**ISA positioning:** "+positioning["stance"]+"\n\n")
            out.write("**Price verification:** "+str(positioning["data_quality"]["independently_verified_price"])+"\n\n")
            out.write("Download sentinel_dashboard.html from the run artifacts for the decision brief.\n\n")
            out.write("Research warning only; not an automated trade instruction.\n")
if __name__=="__main__":main()
