"""Lookahead-free retrospective of downside warnings, using only observations available on each date."""
from downside_guard import assess
def replay(rows,minimum_sessions=12):
    bars=sorted((r for r in rows if float(r.get("volume",0))>0),key=lambda r:r["date"])
    timeline=[]
    for i in range(minimum_sessions-1,len(bars)):
        result=assess(bars[:i+1],minimum_sessions=minimum_sessions)
        timeline.append({"date":bars[i]["date"],"close":float(bars[i]["close"]),
                         "severity":result["severity"],"warnings":result["warnings"]})
    first=next((x for x in timeline if x["severity"] in ("HIGH","CRITICAL")),None)
    high_days=sum(x["severity"] in ("HIGH","CRITICAL") for x in timeline)
    critical_days=sum(x["severity"]=="CRITICAL" for x in timeline)
    first_date=first["date"] if first else None
    latest_close=float(bars[-1]["close"]) if bars else None
    first_close=first["close"] if first else None
    further_change=round(100*(latest_close/first_close-1),2) if first_close and latest_close else None
    return {"status":"RESEARCH_ONLY","observations":len(bars),
            "high_or_critical_sessions":high_days,"critical_sessions":critical_days,
            "first_warning_to_latest_close_pct":further_change,
            "first_warning_to_latest_close_note":"Descriptive price change, not avoidable loss or strategy return",
            "first_high_risk_warning":first,"timeline":timeline,
            "warning_coverage":"Historical counterfactual, not proof that an alert was delivered or an exit was executable",
            "trade_signal":False}
