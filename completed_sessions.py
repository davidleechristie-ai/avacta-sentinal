"""Completed-session selection, independent of wall-clock tests."""
from session_gate import session_gate
def completed_rows(rows,now=None):
    dates=[str(x.get("date",""))[:10] for x in rows]
    latest=max(dates,default=None)
    latest_status=session_gate(latest,now)
    accepted=[x for x in rows if session_gate(str(x.get("date",""))[:10],now)["status"]=="ACCEPTED"]
    return accepted,latest,latest_status
