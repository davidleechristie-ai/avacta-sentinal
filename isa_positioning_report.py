"""Consolidated, forward-looking AVCT ISA research report.

All conditions are hypothetical. Never supplies an order, trade size or
calibrated probability. TraderMonty skills provide process, not a proven edge.
"""
from datetime import date

def build_report(decision, weekly, catalysts, overlay, pretrade, downside, levels=None):
    levels=levels or {}
    as_of=decision["as_of"]
    deadline=decision["isa_exit_deadline"]
    days=(date.fromisoformat(deadline)-date.fromisoformat(as_of)).days
    severity=downside.get("severity","UNKNOWN")
    pattern=weekly.get("weekly_trend_pattern","INSUFFICIENT_DATA")
    source_verified=decision.get("price_source_status") not in ("UNKNOWN","OPENBB_YFINANCE_UNVERIFIED")
    gate=decision.get("price_session_gate")=="ACCEPTED"
    events=[e for e in catalysts.get("catalysts",[]) if e.get("status") in ("UPCOMING","IN_WINDOW") and e.get("within_isa_horizon")]
    events.sort(key=lambda e:e["days_until_start"])
    if days<0:
        stance="EXIT_DEADLINE_PASSED"
        rationale="ISA exit deadline has passed; verify account status immediately."
    elif days<=14:
        stance="PRIORITISE_MANDATORY_EXIT"
        rationale="Mandatory ISA exit within fourteen calendar days takes precedence over technical setups."
    elif not gate or not source_verified:
        stance="DEFENSIVE_REVIEW_DATA_UNVERIFIED" if severity in ("HIGH","CRITICAL") else "WAIT_FOR_VERIFIED_EVIDENCE"
        rationale="Completed-session or independent price verification is missing; no executable entry trigger."
    elif severity in ("HIGH","CRITICAL"):
        stance="DEFENSIVE_HOLD_OR_REDUCE_REVIEW"
        rationale="Elevated downside evidence warrants a manual exposure review before any increase."
    elif pattern=="HIGHER_HIGHS_AND_LOWS" and weekly.get("weekly_breakout") is True:
        stance="CONSIDER_ADD_ONLY_AFTER_MANUAL_CHECKS"
        rationale="Weekly structure improved; catalyst and liquidity checks remain necessary."
    else:
        stance="HOLD_OR_WAIT_FOR_CONFIRMATION"
        rationale="No independently verified combination of price, volume and catalyst evidence supports adding."
    support=weekly.get("prior_eight_week_support_pence")
    resistance=weekly.get("prior_eight_week_resistance_pence")
    return {
        "report_type":"TRADERMONTY_AVCT_ISA_POSITIONING_RESEARCH",
        "as_of":as_of,"symbol":"AVCT.L","account_scope":"SHORT_TERM_ISA_ONLY",
        "isa_exit_deadline":deadline,"days_to_exit":days,
        "stance":stance,"rationale":rationale,
        "observed_close_pence":decision.get("observed_close"),
        "downside_severity":severity,
        "weekly_trend":pattern,
        "weekly_support_pence":support,"weekly_resistance_pence":resistance,
        "weekly_relative_volume":weekly.get("relative_weekly_volume"),
        "forward_levels":levels,
        "support_context":"BROKEN_PREVIOUS_SUPPORT" if weekly.get("prior_eight_week_support_pence") is not None and decision.get("observed_close") is not None and decision["observed_close"]<weekly["prior_eight_week_support_pence"] else "NOT_CONFIRMED_BROKEN",
        "next_catalyst":({"id":events[0]["id"],"days_until_start":events[0]["days_until_start"],
                          "source":events[0]["source"],"outcome":"NOT_VERIFIED"} if events else None),
        "scenario_matrix":{
            "bull":{"condition":"Independently verified higher-low, resistance breakout, supporting volume and favourable issuer-confirmed catalyst evidence",
                    "review":"Consider whether a tactical add improves risk/reward; never auto-buy"},
            "base":{"condition":"Mixed technical structure or catalyst outcomes still unverified",
                    "review":"Preserve flexibility and review exposure manually"},
            "bear":{"condition":"Confirmed support failure, sustained distribution, adverse clinical update or financing deterioration",
                    "review":"Review reducing exposure and deadline-adjusted exit plan"}},
        "event_positioning_rules":{
            "before_event":"Do not treat anticipation or volume alone as a verified clinical result; reassess gap and liquidity risk before increasing exposure",
            "on_announcement":"Compare primary-source disclosure with previously stated expectations; distinguish scientific mechanism, clinical efficacy and commercial partnerships",
            "after_event":"Recheck closing price, spread, volume and failed-breakout risk before changing stance; do not trade from an intraday unverified candle"},
        "change_to_consider_add":[
            "Independent completed-session OHLCV and executable bid/ask verification",
            "Weekly higher-high/higher-low structure plus a confirmed resistance breakout and supporting volume",
            "Primary-source catalyst review including what was already expected",
            "Manual pre-trade discipline and liquidity/risk checks"],
        "change_to_review_reduction":[
            "Independently verified breakdown below observed weekly support with weak recovery",
            "New adverse issuer-confirmed clinical or financing information",
            "Deadline approaching without sufficient liquidity or risk-adjusted upside"],
        "data_quality":{"independently_verified_price":source_verified,"completed_session_accepted":gate,
                        "catalyst_outcomes_verified":all(e.get("surprise_assessment")=="VERIFIED" for e in events) if events else False},
        "pretrade_gate":pretrade.get("decision","UNKNOWN"),
        "owner_approval_required":True,"auto_trade":False,"trade_signal":False,
        "confidence":"LOW_UNTIL_CROSS_VERIFIED",
        "probabilities":"NOT_CALIBRATED",
        "limitations":["Research hypotheses are not executable quotes or guarantees",
                       "Weekly OHLCV is not a human visual chart review",
                       "AIM spread, gaps and slippage can invalidate a stop-loss",
                       "SIPP is excluded; private holdings are not stored in GitHub"]}

def markdown(report):
    def fmt(x):
        return "unknown" if x is None else str(x)
    next_event=report["next_catalyst"]
    lines=[
        "# AVCT Sentinel — short-term ISA positioning",
        "",
        "**As of:** "+report["as_of"]+" | **Mandatory exit:** "+report["isa_exit_deadline"]+
        " ("+str(report["days_to_exit"])+" calendar days)",
        "",
        "## Decision hypothesis",
        "**"+report["stance"]+"**",
        "",
        report["rationale"],
        "",
        "**Confidence:** "+report["confidence"]+" | **Manual owner approval:** required",
        "",
        "## Technical evidence (GBp, not executable quotes)",
        "- Observed close: "+fmt(report["observed_close_pence"])+"p",
        "- Weekly trend: "+report["weekly_trend"],
        "- Prior weekly support / resistance: "+fmt(report["weekly_support_pence"])+
        "p / "+fmt(report["weekly_resistance_pence"])+"p",
        "- Weekly relative volume: "+fmt(report["weekly_relative_volume"]),
        "- Previous weekly support context: "+report["support_context"],
        "- Historical downside candidates: "+", ".join(str(x["level_pence"])+"p" for x in report["forward_levels"].get("downside_candidates",[])) if report["forward_levels"].get("downside_candidates") else "- Historical downside candidates: not established",
        "- Overhead resistance candidates: "+", ".join(str(x["level_pence"])+"p" for x in report["forward_levels"].get("overhead_resistance",[])) if report["forward_levels"].get("overhead_resistance") else "- Overhead resistance candidates: not established",
        "- Downside severity: "+report["downside_severity"],
        "",
        "## Next catalyst",
        ("- "+next_event["id"]+" in "+str(next_event["days_until_start"])+
         " days; outcome unverified. Source: "+next_event["source"]) if next_event else
        "- No upcoming registry event within ISA horizon",
        "",
        "## What would change the positioning?",
        "### Consider adding only after",
        *["- "+x for x in report["change_to_consider_add"]],
        "",
        "### Review reducing after",
        *["- "+x for x in report["change_to_review_reduction"]],
        "",
        "## Event-specific positioning checks",
        *["- **"+k.replace("_"," ").title()+"**: "+v for k,v in report["event_positioning_rules"].items()],
        "",
        "## Scenarios (not probabilities)",
        *["- **"+name.upper()+"**: "+item["condition"]+". "+item["review"] for name,item in report["scenario_matrix"].items()],
        "",
        "## Controls",
        "- Price independently verified: "+str(report["data_quality"]["independently_verified_price"]),
        "- Pre-trade gate: "+report["pretrade_gate"],
        "- No trade execution; private holdings and SIPP excluded.",
        "- Probability estimates not calibrated. Manual approval required.",
        ""
    ]
    return "\n".join(lines)
