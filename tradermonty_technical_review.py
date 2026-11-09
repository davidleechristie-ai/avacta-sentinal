"""Apply the selected TraderMonty technical-analyst *methodology* to AVCT.

The upstream skill is a weekly chart-reading checklist, not a quantitative
prediction model. This adapter produces an evidence inventory from completed
OHLCV bars and refuses to invent weekly chart findings or probabilities.
"""
from datetime import date

SOURCE="tradermonty/claude-trading-skills/skills/technical-analyst/SKILL.md"

def report(completed_bars, downside, decision):
    bars=sorted(completed_bars,key=lambda x:x["date"])
    latest=bars[-1] if bars else None
    recent=bars[-5:] if len(bars)>=5 else []
    closes=[float(x["close"]) for x in recent]
    volumes=[float(x["volume"]) for x in recent]
    low20=min((float(x["low"]) for x in bars[-20:]),default=None)
    high20=max((float(x["high"]) for x in bars[-20:]),default=None)
    return {
        "status":"RESEARCH_CHECKLIST_NOT_PREDICTIVE_MODEL",
        "source_skill":SOURCE,
        "symbol":"AVCT.L",
        "completed_sessions":len(bars),
        "last_completed_session":latest["date"] if latest else None,
        "technical_observations":{
            "recent_five_closes":closes,
            "recent_five_volumes":volumes,
            "twenty_session_low_pence":low20,
            "twenty_session_high_pence":high20,
            "downside_severity":downside.get("severity","UNKNOWN"),
            "risk_transition":downside.get("risk_transition",{}).get("status","UNKNOWN")},
        "weekly_chart_review":{
            "status":"NOT_PERFORMED",
            "required":["Verified weekly candlestick chart","Weekly trend and moving-average structure",
                        "Volume around support/resistance","Breakout, failed breakout and retest",
                        "Bull/base/bear evidence with explicit invalidation"]},
        "catalyst_overlay":{
            "status":"REQUIRES_INDEPENDENT_PRIMARY_EVIDENCE",
            "required":["Upcoming clinical and corporate dates","Actual announcement surprise versus prior guidance",
                        "Financing and dilution changes","FCA shorts and trading liquidity"]},
        "decision_reference":decision.get("decision"),
        "probabilities":"NOT_CALIBRATED",
        "price_source_status":downside.get("price_data_provenance","UNKNOWN"),
        "auto_trade":False}
