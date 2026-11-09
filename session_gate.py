"""Fail-closed market-session freshness assessment for LSE daily candles."""
from datetime import datetime,date,time
from zoneinfo import ZoneInfo
def session_gate(session_date, now=None):
    now=now or datetime.now(ZoneInfo("Europe/London"))
    if now.tzinfo is None:raise ValueError("timezone-aware now required")
    local=now.astimezone(ZoneInfo("Europe/London"))
    d=date.fromisoformat(str(session_date)[:10]) if session_date else None
    if not d:return {"status":"UNKNOWN","reason":"No latest session"}
    age=(local.date()-d).days
    if age<0 or age>4:return {"status":"STALE","calendar_age_days":age}
    if d==local.date() and local.weekday()<5 and local.time()<time(17,0):
        return {"status":"PROVISIONAL","reason":"Daily candle may still change before the market close","calendar_age_days":age}
    return {"status":"ACCEPTED","calendar_age_days":age}
