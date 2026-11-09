"""Research-only technical replay; avoids forward-looking indicators and trading execution."""
from technical_scorecard import assess_technicals
def replay(rows,min_history=22,forward_sessions=5):
    bars=sorted((r for r in rows if r["volume"]>0),key=lambda r:r["date"])
    outcomes=[]
    for i in range(min_history-1,len(bars)-forward_sessions):
        evidence=assess_technicals(bars[:i+1])
        if evidence["price_reversal"]!="CONFIRMED_TECHNICAL_PATTERN":continue
        entry=bars[i]["close"]
        future=bars[i+forward_sessions]["close"]
        outcomes.append({"date":bars[i]["date"],"signal_close":entry,"future_close":future,
                         "forward_sessions":forward_sessions,"forward_return_pct":round(100*(future/entry-1),3),
                         "volume_confirmed":evidence["sustained_volume"]=="CONFIRMED_2_SESSIONS"})
    wins=sum(x["forward_return_pct"]>0 for x in outcomes)
    return {"status":"RESEARCH_ONLY","signals":len(outcomes),"positive_forward_returns":wins,
            "hit_rate":round(wins/len(outcomes),4) if outcomes else None,
            "observations":outcomes,"limitations":"No spread, slippage, market impact, corporate actions or regime validation; not a profitable-strategy claim","trade_signal":False}
