"""TraderMonty pre-trade discipline gate adapted to AVCT manual ISA workflow.

Offline fail-closed checklist, never a broker permission or order API.
Public scheduled jobs must not ingest private holdings.
"""
from math import isfinite

def check(candidate=None,market=None):
    if not candidate:
        return {"decision":"NO_ACTIONABLE_ORDERS","reasons":["No private manual order candidate supplied"],"auto_trade":False}
    if candidate.get("order_intent") not in ("ENTRY_READY","MANUAL_ORDER","ACTIONABLE"):
        return {"decision":"NO_ACTIONABLE_ORDERS","reasons":["Candidate is not an actionable manual entry"],"auto_trade":False}
    reasons=[]
    if candidate.get("symbol")!="AVCT.L":reasons.append("Instrument is not AVCT.L")
    for field in ("entry_in_written_plan","stop_predefined","size_within_plan"):
        if candidate.get(field) is not True:reasons.append(field+" must be explicitly confirmed")
    for field in ("planned_risk_gbp","actual_risk_gbp"):
        val=candidate.get(field)
        if isinstance(val,bool) or not isinstance(val,(int,float)) or not isfinite(val) or val<0:
            reasons.append(field+" missing or invalid")
    planned=candidate.get("planned_risk_gbp");actual=candidate.get("actual_risk_gbp")
    if isinstance(planned,(int,float)) and isinstance(actual,(int,float)) and not isinstance(planned,bool) and not isinstance(actual,bool):
        if isfinite(planned) and isfinite(actual) and actual>planned:reasons.append("Actual risk exceeds planned risk")
    if not market or market.get("independently_verified_price") is not True:
        reasons.append("Independent price and spread verification required")
    if market and market.get("circuit_breaker") in ("HALTED","COOLDOWN","TRADING_HALTED"):
        reasons.append("Circuit breaker blocks entry")
    if market and market.get("isa_exit_deadline_checked") is not True:
        reasons.append("ISA exit deadline review required")
    return {"decision":"REVIEW_REQUIRED" if reasons else "CHECKLIST_PASSED_MANUAL_REVIEW_ONLY",
            "reasons":reasons,
            "source_skill":"tradermonty/claude-trading-skills/pre-trade-discipline-gate",
            "note":"Never constitutes permission to trade; owner must independently approve manual order",
            "auto_trade":False}
