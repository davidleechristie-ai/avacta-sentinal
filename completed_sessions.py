"""Select completed historical sessions; staleness applies to the latest bar, not every historical bar."""
from datetime import date
from session_gate import session_gate
def completed_rows(rows,now=None):
    dates=[str(x.get("date",""))[:10] for x in rows]
    latest=max(dates,default=None)
    latest_status=session_gate(latest,now)
    accepted=[]
    for row in rows:
        value=str(row.get("date",""))[:10]
        try:
            d=date.fromisoformat(value)
        except ValueError:
            continue
        gate=session_gate(value,now)
        # Older historical observations remain valid as context even when >4 days old.
        # Only exclude future dates and today's unfinished daily candle.
        if gate["status"]=="PROVISIONAL" or gate.get("calendar_age_days",0)<0:
            continue
        accepted.append(row)
    return accepted,latest,latest_status
