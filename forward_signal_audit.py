"""Lookahead-free evaluation of forward downside warnings.

This is an observational signal audit, NOT a strategy return: no hypothetical
fills, bid/ask assumptions, trading costs or claims of avoidable losses.
"""
from downside_guard import assess
from risk_transition import transition

def audit(rows, horizons=(1, 3, 5, 10), minimum_sessions=12):
    bars=sorted(rows,key=lambda r:r["date"])
    events=[]
    for i in range(minimum_sessions,len(bars)):
        past=bars[:i+1]
        state=assess(past,minimum_sessions)
        change=transition(past,minimum_sessions)
        if change["status"]!="NEW_ESCALATION":
            continue
        start=float(bars[i]["close"])
        if start<=0:continue
        future={}
        for h in horizons:
            if i+h<len(bars):
                finish=float(bars[i+h]["close"])
                window=bars[i+1:i+h+1]
                future[str(h)]={
                    "forward_close_return_pct":round(100*(finish/start-1),2),
                    "worst_close_return_pct":round(100*(min(float(x["close"]) for x in window)/start-1),2),
                    "best_close_return_pct":round(100*(max(float(x["close"]) for x in window)/start-1),2)}
            else:future[str(h)]=None
        events.append({"session":bars[i]["date"],"severity":state["severity"],
                       "observed_close":start,"future":future})
    stats={}
    for h in horizons:
        returns=[e["future"][str(h)]["forward_close_return_pct"] for e in events if e["future"][str(h)] is not None]
        stats[str(h)]={"evaluated_events":len(returns),
                       "subsequent_decline_count":sum(x<0 for x in returns),
                       "subsequent_decline_fraction":round(sum(x<0 for x in returns)/len(returns),3) if returns else None,
                       "mean_forward_return_pct":round(sum(returns)/len(returns),2) if returns else None}
    return {"status":"RESEARCH_ONLY","method":"Walk-forward event evaluation with no future observations used in signal generation",
            "horizons_sessions":list(horizons),"events":events,"summary":stats,
            "limitations":"Overlapping events, survivorship, corporate actions, raw vs adjusted prices, spread and execution costs not modelled; not calibrated predictive accuracy",
            "auto_trade":False}
