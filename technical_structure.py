"""Close-only breakout and retest observations; no predictive trading signals."""
from statistics import median
from math import isfinite

def assess_structure(rows, lookback=10, volume_window=10):
    valid=[]
    for bar in sorted(rows,key=lambda b:str(b.get("date",""))):
        try:
            close=float(bar["close"]);volume=float(bar["volume"])
            if isfinite(close) and close>0 and isfinite(volume) and volume>=0:
                valid.append({"date":str(bar["date"]),"close":close,"volume":volume})
        except (KeyError,ValueError,TypeError):pass
    if len(valid)<max(lookback+2,volume_window+2):
        return {"status":"INSUFFICIENT_DATA","events":[],"auto_trade":False}
    events=[]
    for i in range(max(lookback,volume_window),len(valid)):
        bar=valid[i];past=valid[i-lookback:i]
        ceiling=max(b["close"] for b in past)
        floor=min(b["close"] for b in past)
        prior_volumes=[b["volume"] for b in valid[i-volume_window:i] if b["volume"]>0]
        baseline=median(prior_volumes) if prior_volumes else None
        ratio=round(bar["volume"]/baseline,2) if baseline else None
        volume_support=ratio is not None and ratio>=1.5
        kind=None;level=None
        if bar["close"]>ceiling:
            kind="CLOSE_ABOVE_PRIOR_RANGE";level=ceiling
        elif bar["close"]<floor:
            kind="CLOSE_BELOW_PRIOR_RANGE";level=floor
        if kind:
            events.append({"date":bar["date"],"kind":kind,"close_pence":bar["close"],
                           "reference_level_pence":level,"relative_volume":ratio,
                           "volume_confirmation":"SUPPORTED" if volume_support else "NOT_CONFIRMED",
                           "price_verified":False})
    # A return inside the prior range on the next session invalidates a close-only break.
    for event in events:
        following=next((b for b in valid if b["date"]>event["date"]),None)
        if following:
            level=event["reference_level_pence"]
            failed=(event["kind"]=="CLOSE_ABOVE_PRIOR_RANGE" and following["close"]<=level) or (event["kind"]=="CLOSE_BELOW_PRIOR_RANGE" and following["close"]>=level)
            event["next_session_status"]="FAILED_NEXT_SESSION" if failed else "HELD_NEXT_SESSION"
        else:event["next_session_status"]="PENDING"
    return {"status":"OBSERVATIONAL_UNVERIFIED","method":"Close outside previous ten-session closing range; volume >=1.5x preceding ten-session median",
            "events":events[-12:],"auto_trade":False}
