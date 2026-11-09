"""Distinguish a fresh downside escalation from an ongoing warning."""
from downside_guard import assess
def transition(rows,minimum_sessions=12):
    if len(rows)<minimum_sessions:return {"status":"UNKNOWN","reason":"INSUFFICIENT_HISTORY"}
    current=assess(rows,minimum_sessions)
    previous=assess(rows[:-1],minimum_sessions) if len(rows)>minimum_sessions else {"severity":"UNKNOWN"}
    rank={"UNKNOWN":-1,"NORMAL":0,"WATCH":1,"HIGH":2,"CRITICAL":3}
    a,b=previous["severity"],current["severity"]
    if b not in rank or a not in rank:return {"status":"UNKNOWN"}
    if rank[b]>=2 and rank[b]>rank[a]:kind="NEW_ESCALATION"
    elif rank[b]>=2 and rank[b]==rank[a]:kind="PERSISTENT_RISK"
    elif rank[b]>=2:kind="RISK_DEESCALATING"
    elif rank[b]<rank[a]:kind="IMPROVING"
    else:kind="NO_ESCALATION"
    return {"status":kind,"previous_severity":a,"current_severity":b,
            "session":current.get("latest_session"),"trade_signal":False}
