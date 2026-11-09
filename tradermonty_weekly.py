"""Weekly OHLCV aggregation for TraderMonty chart-review methodology.

Only completed sessions are passed by caller. No probabilities are generated.
"""
from datetime import date
from statistics import mean

def weekly_review(rows):
    bars=sorted(rows,key=lambda r:r["date"])
    weeks={}
    for b in bars:
        d=date.fromisoformat(b["date"])
        key=f"{d.isocalendar().year}-W{d.isocalendar().week:02d}"
        if key not in weeks:
            weeks[key]={"week":key,"first_session":b["date"],"last_session":b["date"],
                        "open":float(b["open"]),"high":float(b["high"]),
                        "low":float(b["low"]),"close":float(b["close"]),"volume":0,"sessions":0}
        w=weeks[key]
        w["last_session"]=b["date"]
        w["high"]=max(w["high"],float(b["high"]))
        w["low"]=min(w["low"],float(b["low"]))
        w["close"]=float(b["close"])
        w["volume"]+=float(b["volume"])
        w["sessions"]+=1
    items=list(weeks.values())
    last=items[-1] if items else None
    previous=items[-2] if len(items)>=2 else None
    prior=items[-9:-1] if len(items)>=9 else items[:-1]
    support=min((w["low"] for w in prior),default=None)
    resistance=max((w["high"] for w in prior),default=None)
    avgvol=mean(w["volume"] for w in prior) if prior else None
    trend="INSUFFICIENT_DATA"
    if len(items)>=4:
        a,b=items[-4],items[-3]
        c,d=items[-2],items[-1]
        if c["high"]>a["high"] and d["high"]>b["high"] and c["low"]>a["low"] and d["low"]>b["low"]:
            trend="HIGHER_HIGHS_AND_LOWS"
        elif c["high"]<a["high"] and d["high"]<b["high"] and c["low"]<a["low"] and d["low"]<b["low"]:
            trend="LOWER_HIGHS_AND_LOWS"
        else:trend="MIXED"
    return {"source_methodology":"tradermonty/claude-trading-skills technical-analyst",
            "status":"WEEKLY_OHLCV_OBSERVATIONS_UNVERIFIED",
            "weeks_available":len(items),"last_week":last,
            "weekly_bars":items[-12:],"weekly_trend_pattern":trend,
            "prior_eight_week_support_pence":support,
            "prior_eight_week_resistance_pence":resistance,
            "relative_weekly_volume":round(last["volume"]/avgvol,3) if last and avgvol else None,
            "weekly_breakout":last["close"]>resistance if last and resistance is not None else None,
            "weekly_breakdown":last["close"]<support if last and support is not None else None,
            "weekly_chart_image_review":"NOT_PERFORMED",
            "probabilities":"NOT_CALIBRATED","auto_trade":False}
