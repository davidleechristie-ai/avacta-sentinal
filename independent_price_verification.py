"""Strict independent OHLCV corroboration. No implied provider independence."""
from datetime import date

def verify(primary,secondary,primary_provider=None,secondary_provider=None,price_tolerance=0.005,volume_tolerance=0.05):
    result={"status":"NOT_VERIFIED","independent_providers":0,"validated_for_trading":False,"checks":{}}
    if not primary or not secondary or not primary_provider or not secondary_provider:
        result["reason"]="Missing completed bars or provider identity";return result
    if str(primary_provider).lower()==str(secondary_provider).lower():
        result["reason"]="Same provider cannot independently corroborate itself";return result
    try:
        a,b=primary[-1],secondary[-1]
        ad,bd=str(a["date"])[:10],str(b["date"])[:10]
        if date.fromisoformat(ad)!=date.fromisoformat(bd):
            result["reason"]="Completed session dates differ";return result
        checks={}
        for field in ("open","high","low","close"):
            x,y=float(a[field]),float(b[field])
            checks[field]=x>0 and y>0 and abs(x-y)<=max(.01,price_tolerance*max(x,y))
        x,y=float(a["volume"]),float(b["volume"])
        checks["volume"]=x>0 and y>0 and abs(x-y)<=volume_tolerance*max(x,y)
        result["checks"]=checks
        if all(checks.values()):
            result.update(status="MATCHED",independent_providers=2,session=ad,reason="Two distinct providers agree within declared tolerances")
        else:result["reason"]="Completed OHLCV disagreement"
    except (KeyError,ValueError,TypeError,IndexError,OverflowError):
        result["reason"]="Invalid OHLCV observations"
    return result
