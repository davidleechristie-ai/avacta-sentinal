"""Forward-looking AVCT support/resistance evidence from completed OHLCV bars.

Historical zones are observations, not executable orders. A broken support
must never be presented as the next support below the market.
"""
from statistics import mean

def map_levels(rows, as_of_close=None):
    bars=sorted((b for b in rows if b.get("volume",0)>0),key=lambda b:b["date"])
    if not bars:
        return {"status":"INSUFFICIENT_DATA","broken_support":[],"downside_candidates":[],
                "overhead_resistance":[],"auto_trade":False}
    close=float(as_of_close if as_of_close is not None else bars[-1]["close"])
    # Prior sessions only: avoid classifying the latest candle's own low as
    # an already-tested level. These are observed local pivots, not forecasts.
    prior=bars[:-1]
    pivots=[]
    for i in range(1,len(prior)-1):
        left,mid,right=prior[i-1],prior[i],prior[i+1]
        if mid["low"]<=left["low"] and mid["low"]<=right["low"]:
            pivots.append({"level_pence":float(mid["low"]),"kind":"PIVOT_LOW","session":mid["date"]})
        if mid["high"]>=left["high"] and mid["high"]>=right["high"]:
            pivots.append({"level_pence":float(mid["high"]),"kind":"PIVOT_HIGH","session":mid["date"]})
    recent=prior[-60:]
    # Include 10/20/60 session range boundaries, but clearly identify when
    # already broken. Deduplicate levels with a 1% proximity tolerance.
    for n in (10,20,60):
        window=recent[-n:]
        if len(window)>=n:
            pivots.append({"level_pence":float(min(b["low"] for b in window)),"kind":f"{n}_SESSION_LOW","session":window[-1]["date"]})
            pivots.append({"level_pence":float(max(b["high"] for b in window)),"kind":f"{n}_SESSION_HIGH","session":window[-1]["date"]})
    below=sorted((p for p in pivots if p["level_pence"]<close),key=lambda p:-p["level_pence"])
    above=sorted((p for p in pivots if p["level_pence"]>=close),key=lambda p:p["level_pence"])
    def distinct(seq,limit):
        result=[]
        for p in seq:
            if all(abs(p["level_pence"]-q["level_pence"])>max(.25,.01*q["level_pence"]) for q in result):
                result.append(p)
            if len(result)==limit:break
        return result
    # Prior support above close is BROKEN, not a fresh downside target.
    broken=distinct(sorted((p for p in above if "LOW" in p["kind"]),key=lambda p:p["level_pence"]),4)
    overhead=distinct(above,6)
    downside=distinct(below,4)
    return {"status":"OBSERVED_LEVELS_UNVERIFIED","as_of_session":bars[-1]["date"],
            "reference_close_pence":close,
            "broken_support":broken,"downside_candidates":downside,
            "overhead_resistance":overhead,
            "below_lowest_observed_level":len(downside)==0,
            "warning":"Candidate levels are historical pivots, not independently verified support, stop orders or guaranteed liquidity",
            "auto_trade":False}
