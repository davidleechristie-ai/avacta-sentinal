"""Conservative, auditable five-factor evidence assessment. Never issues trades."""
from datetime import date,datetime
from decimal import Decimal,InvalidOperation
import re
WEIGHTS={"price_reversal":25,"sustained_volume":20,"fca_short_exposure":15,"financing_dilution":20,"catalyst_timing":20}
def _date(value):
    try:return date.fromisoformat(str(value)[:10])
    except (ValueError,TypeError):return None
def _percentage(value):
    try:
        raw=str(value).strip().replace("%","").replace(",","")
        number=Decimal(raw)
        return float(number) if number.is_finite() and 0<=number<=100 else None
    except (InvalidOperation,ValueError,TypeError):return None
def short_exposure(sources):
    current=sources.get("fca_current",{})
    historic=sources.get("fca_historic",{})
    if current.get("status")!="MATCHED":
        return {"status":"UNKNOWN","reason":"No current FCA match; not evidence of zero short interest","source":current.get("source")}
    rows=current.get("rows",[])
    parsed=[]
    for row in rows:
        for key,value in row.items():
            label=str(key).lower()
            if "position" in label or "percentage" in label or "short" in label and ("%" in label or "size" in label):
                pct=_percentage(value)
                if pct is not None:parsed.append((key,pct))
    return {"status":"REVIEW_REQUIRED","reported_fields":parsed,"current_rows":len(rows),
            "historic_rows":len(historic.get("rows",[])),
            "reason":"Compare dated, consistently defined FCA aggregates before scoring trend; reporting thresholds apply",
            "source":current.get("source")}
def financing(sources):
    items=sources.get("avacta_news",{}).get("items",[])
    keywords=("placing","fundrais","subscription","convertible","financing","cash runway","dilution")
    matches=[{"title":x.get("title"),"url":x.get("url")} for x in items if any(k in x.get("title","").lower() for k in keywords)]
    return {"status":"REVIEW_REQUIRED" if matches else "UNKNOWN","relevant_headlines":matches[:12],
            "reason":"Headline matches are not proof of financing completion or available runway"}
def catalyst(sources,research,as_of=None,exit_date=date(2027,1,31)):
    as_of=as_of or date.today()
    events=research.get("catalysts",[])
    return {"status":"REVIEW_REQUIRED" if events else "UNKNOWN","days_to_isa_deadline":(exit_date-as_of).days,
            "events":[{"id":e.get("id"),"window":e.get("window"),"outcome":e.get("outcome"),"source":e.get("source")} for e in events],
            "reason":"Narrative event windows do not establish precise event dates or outcomes"}
def build(price,research,as_of=None):
    quality=price.get("quality",{})
    sources=research.get("sources",{})
    details={
        "price_reversal":{"status":quality.get("price_reversal","UNKNOWN"),"source":"OpenBB/Yahoo Finance"},
        "sustained_volume":{"status":quality.get("sustained_volume","UNKNOWN"),"source":"OpenBB/Yahoo Finance"},
        "fca_short_exposure":short_exposure(sources),
        "financing_dilution":financing(sources),
        "catalyst_timing":catalyst(sources,research.get("research",{}),as_of=as_of)}
    return {"status":"EVIDENCE_REVIEW_REQUIRED","weights":WEIGHTS,"factors":details,
            "score_0_100":None,"reason":"No arbitrary points assigned to unknown or unverified factors",
            "validated_for_trading":False,"trade_signal":False}
