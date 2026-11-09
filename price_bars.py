"""Only structurally valid OHLCV bars can influence downside surveillance."""
from datetime import date
from decimal import Decimal,InvalidOperation
def clean_bars(rows):
    clean=[]
    rejected=[]
    for i,row in enumerate(rows):
        try:
            day=date.fromisoformat(str(row["date"])[:10]).isoformat()
            v={k:Decimal(str(row[k])) for k in ("open","high","low","close","volume")}
            if not all(x.is_finite() for x in v.values()):raise ValueError("nonfinite")
            if min(v[k] for k in ("open","high","low","close"))<=0 or v["volume"]<=0:
                raise ValueError("nonpositive price or volume")
            if v["high"]<max(v["open"],v["close"],v["low"]) or v["low"]>min(v["open"],v["close"],v["high"]):
                raise ValueError("inconsistent OHLCV")
            clean.append({"date":day,**{k:float(x) for k,x in v.items()}})
        except (KeyError,ValueError,TypeError,InvalidOperation) as exc:
            rejected.append({"row":i,"reason":str(exc)})
    clean.sort(key=lambda x:x["date"])
    unique={}
    for row in clean:
        if row["date"] in unique:rejected.append({"date":row["date"],"reason":"duplicate date"})
        unique[row["date"]]=row
    return list(unique.values()),rejected
