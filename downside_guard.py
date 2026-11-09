"""Independent downside surveillance. Warnings are research outputs, not trade orders."""
from statistics import mean
def assess(rows, minimum_sessions=12):
    bars=sorted((r for r in rows if float(r.get("volume",0))>0),key=lambda r:r["date"])
    result={"status":"INSUFFICIENT_DATA","severity":"UNKNOWN","warnings":[],"trade_signal":False,"auto_trade":False}
    if len(bars)<minimum_sessions:return {**result,"valid_sessions":len(bars)}
    latest=bars[-1];previous=bars[-2];close=float(latest["close"])
    if close<=0:return {**result,"status":"INVALID_DATA"}
    prior10=bars[-11:-1]
    prior_support=min(float(b["low"]) for b in prior10)
    peak=max(float(b["close"]) for b in bars[-21:])
    drawdown=100*(close/peak-1) if peak else 0
    closes=[float(b["close"]) for b in bars[-6:]]
    decline5=100*(close/closes[0]-1)
    below_support=close<prior_support
    consecutive_down=sum(closes[i]<closes[i-1] for i in range(1,len(closes)))
    warnings=[]
    if below_support:warnings.append("CLOSE_BELOW_PRIOR_10_SESSION_SUPPORT")
    if drawdown<=-10:warnings.append("DRAWDOWN_AT_LEAST_10_PERCENT")
    if decline5<=-7:warnings.append("FIVE_SESSION_DECLINE_AT_LEAST_7_PERCENT")
    if consecutive_down>=4:warnings.append("FOUR_OR_MORE_DECLINING_CLOSES_IN_FIVE_SESSIONS")
    severity="CRITICAL" if (below_support and drawdown<=-10) or drawdown<=-15 else "HIGH" if (below_support or drawdown<=-10 or decline5<=-7) else "WATCH" if consecutive_down>=4 else "NORMAL"
    return {"status":"ASSESSED","severity":severity,"warnings":warnings,
            "latest_session":latest["date"],"latest_close":close,
            "prior_10_session_support":round(prior_support,4),
            "close_below_support":below_support,
            "recent_peak_close":round(peak,4),"drawdown_from_recent_peak_pct":round(drawdown,2),
            "five_session_return_pct":round(decline5,2),
            "declining_closes_last_five":consecutive_down,
            "valid_sessions":len(bars),"trade_signal":False,"auto_trade":False,
            "interpretation":"A risk warning is not an instruction to sell; investigate news, liquidity, and execution risk."}
