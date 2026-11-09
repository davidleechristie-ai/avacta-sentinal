"""Optional Twelve Data secondary daily feed. Independent of Yahoo/OpenBB.

Requires TWELVEDATA_API_KEY in the workflow environment. This module never
marks observations verified or places orders; the corroboration gate does that.
"""
import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

class SecondaryFeedUnavailable(RuntimeError):
    pass

def fetch_secondary(api_key=None, opener=urlopen):
    key=api_key if api_key is not None else os.environ.get("TWELVEDATA_API_KEY","")
    if not key:
        raise SecondaryFeedUnavailable("TWELVEDATA_API_KEY not configured")
    params=urlencode({"symbol":"AVCT","exchange":"LSE","interval":"1day",
                      "outputsize":"15","apikey":key})
    request=Request("https://api.twelvedata.com/time_series?"+params,
                    headers={"User-Agent":"AvactaSentinel/1.0"})
    try:
        with opener(request,timeout=20) as response:
            payload=json.load(response)
    except Exception as exc:
        raise SecondaryFeedUnavailable("Secondary provider request failed: "+type(exc).__name__) from exc
    if payload.get("status")=="error" or not isinstance(payload.get("values"),list):
        raise SecondaryFeedUnavailable("Secondary provider returned no usable series")
    bars=[]
    for item in payload["values"]:
        try:
            bars.append({"date":item["datetime"][:10],
                         **{field:float(item[field]) for field in ("open","high","low","close","volume")}})
        except (KeyError,TypeError,ValueError):
            continue
    bars.sort(key=lambda row:row["date"])
    if not bars:
        raise SecondaryFeedUnavailable("Secondary provider returned no valid OHLCV bars")
    return {"provider":"twelvedata","symbol":"AVCT","exchange":"LSE",
            "currency":payload.get("meta",{}).get("currency"),
            "observations":bars,"validated_for_trading":False}
