"""Compare downside warning outcomes against all eligible sessions.

Descriptive matched-horizon baseline, not an executable trading backtest.
"""
from forward_signal_audit import audit

def compare(rows,horizons=(1,3,5,10),minimum_sessions=12):
    bars=sorted(rows,key=lambda r:r["date"])
    signals=audit(bars,horizons,minimum_sessions)
    summary={}
    for h in horizons:
        eligible=[]
        for i in range(minimum_sessions,len(bars)-h):
            a=float(bars[i]["close"]);b=float(bars[i+h]["close"])
            if a>0:eligible.append(100*(b/a-1))
        flagged=[e["future"][str(h)]["forward_close_return_pct"] for e in signals["events"] if e["future"][str(h)] is not None]
        baseline=sum(eligible)/len(eligible) if eligible else None
        signal_mean=sum(flagged)/len(flagged) if flagged else None
        summary[str(h)]={
            "all_eligible_sessions":len(eligible),
            "all_sessions_mean_return_pct":round(baseline,2) if baseline is not None else None,
            "all_sessions_decline_fraction":round(sum(x<0 for x in eligible)/len(eligible),3) if eligible else None,
            "signal_events":len(flagged),
            "signal_mean_return_pct":round(signal_mean,2) if signal_mean is not None else None,
            "signal_minus_baseline_pp":round(signal_mean-baseline,2) if signal_mean is not None and baseline is not None else None,
            "warning":"Overlapping outcomes and regime selection; this difference does not demonstrate forecast skill or tradable alpha"}
    return {"status":"RESEARCH_ONLY","baseline":"All eligible historical sessions from the same series, same forward horizon",
            "horizons":summary,"auto_trade":False}
