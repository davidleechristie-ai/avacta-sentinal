"""Conservative FCA dated-series parser: no position guessing or silent zeroes."""
from datetime import date
from decimal import Decimal,InvalidOperation
import re
def _date(value):
    s=str(value).strip()
    for fmt in ("%Y-%m-%d","%d/%m/%Y","%d-%m-%Y","%d %B %Y"):
        try:
            from datetime import datetime
            return datetime.strptime(s[:30],fmt).date()
        except ValueError:pass
    return None
def _pct(value):
    try:
        n=Decimal(str(value).strip().replace("%","").replace(",",""))
        return float(n) if n.is_finite() and 0<=n<=100 else None
    except (InvalidOperation,ValueError,TypeError):return None
def parse(rows):
    points=[]
    for row in rows:
        dates=[(k,_date(v)) for k,v in row.items() if any(t in str(k).lower() for t in ("date","as at"))]
        values=[(k,_pct(v)) for k,v in row.items() if any(t in str(k).lower() for t in ("position","percentage","aggregate")) and not any(t in str(k).lower() for t in ("date","holder","name"))]
        dates=[(k,v) for k,v in dates if v]
        values=[(k,v) for k,v in values if v is not None]
        if len(dates)==1 and len(values)==1:
            points.append({"date":dates[0][1].isoformat(),"percent":values[0][1],"date_field":dates[0][0],"value_field":values[0][0]})
    return sorted(points,key=lambda x:x["date"])
def trend(sources):
    current=sources.get("fca_current",{})
    historic=sources.get("fca_historic",{})
    if current.get("status")!="MATCHED":
        return {"status":"UNKNOWN","reason":"No current FCA match; not equivalent to zero reported short exposure"}
    current_points=parse(current.get("rows",[]))
    history=parse(historic.get("rows",[])) if historic.get("status")=="MATCHED" else []
    if not current_points:
        return {"status":"REVIEW_REQUIRED","reason":"FCA field names or date format could not be parsed unambiguously","current_headers":current.get("headers",[])}
    latest=current_points[-1]
    earlier=[p for p in history+current_points if p["date"]<latest["date"] and p["value_field"]==latest["value_field"]]
    earlier.sort(key=lambda p:p["date"])
    if not earlier:
        return {"status":"REVIEW_REQUIRED","latest":latest,"reason":"No comparable earlier dated observation; cannot infer direction"}
    previous=earlier[-1]
    delta=round(latest["percent"]-previous["percent"],4)
    return {"status":"OBSERVED_CHANGE","latest":latest,"previous":previous,"change_percentage_points":delta,
            "direction":"FALLING" if delta<0 else "RISING" if delta>0 else "UNCHANGED",
            "source":current.get("source"),
            "caveat":"Published FCA reportable aggregate, not all short positions; verify publication dates and methodology before interpretation"}
