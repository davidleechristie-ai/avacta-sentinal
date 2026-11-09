"""Prospective decision support, not an automated trading strategy.

Separates technical observations from a recommendation hypothesis. All price
levels are observations; no implied executable bid or offer.
"""
from datetime import date

def build_decision(downside, technical=None, as_of=None, deadline="2027-01-29"):
    technical=technical or {}
    as_of=date.fromisoformat(str(as_of or date.today())[:10])
    days=(date.fromisoformat(deadline)-as_of).days
    severity=downside.get("severity","UNKNOWN")
    transition=downside.get("risk_transition",{}).get("status","UNKNOWN")
    gate=downside.get("session_gate",{}).get("status","UNKNOWN")
    quality=downside.get("price_data_provenance","UNKNOWN")
    latest=downside.get("latest_close")
    support=downside.get("prior_10_session_support")
    reversal=technical.get("price_reversal",False)
    volume=technical.get("sustained_volume",False)
    reasons=[]
    if days<0:
        decision="EXIT_DEADLINE_PASSED"
        reasons.append("ISA exit deadline passed; verify account and holdings immediately")
    elif days<=14:
        decision="PLAN_FULL_EXIT"
        reasons.append("Mandatory exit within fourteen calendar days")
    elif gate!="ACCEPTED" or latest is None:
        decision="WAIT_FOR_VERIFIED_SESSION"
        reasons.append("Latest completed price session unavailable or stale")
    elif severity=="CRITICAL" and transition=="NEW_ESCALATION":
        decision="REVIEW_REDUCTION_URGENTLY"
        reasons.append("Fresh critical downside escalation")
    elif severity in ("HIGH","CRITICAL"):
        decision="DEFENSIVE_HOLD_OR_REDUCE"
        reasons.append("Elevated downside risk; no automatic dip-buying")
    elif reversal is True and volume is True:
        decision="CONSIDER_TACTICAL_ADD_AFTER_REVIEW"
        reasons.append("Reversal and supporting volume require independent verification")
    else:
        decision="WAIT_FOR_CONFIRMATION"
        reasons.append("Insufficient evidence for a higher-conviction add")
    return {
        "as_of":as_of.isoformat(),"isa_exit_deadline":deadline,"days_to_deadline":days,
        "decision":decision,"confidence":"LOW_UNTIL_CROSS_VERIFIED",
        "reasons":reasons,"downside_severity":severity,"risk_transition":transition,
        "price_session_gate":gate,"price_source_status":quality,
        "observed_close":latest,"observed_prior_support":support,
        "next_evidence_required":[
            "independently corroborated completed-session OHLCV and bid/ask spread",
            "relative volume and confirmed higher-low/resistance retest",
            "issuer-primary catalyst surprise versus market expectations",
            "verified financing and FCA short-position changes"],
        "invalidation":"New verified evidence overturning the price, catalyst, or financing thesis",
        "scenario_probabilities":"NOT_CALIBRATED",
        "trade_signal":False,"auto_trade":False,
        "disclaimer":"Research decision hypothesis only; no order execution or guarantee."}
