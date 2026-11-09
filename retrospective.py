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
    return {"status":"RESEARCH_ONLY","observations":len(bars),
            "first_high_risk_warning":first,"timeline":timeline,
            "warning_coverage":"Historical counterfactual, not proof that an alert was delivered or an exit was executable",
            "trade_signal":False}
