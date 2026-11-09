"""Read-only adapter for vendored TraderMonty position-sizer.

Requires an explicit, private account-risk budget and independently verified
entry/stop in GBP. Does not infer user holdings from public GitHub artifacts.
"""
import importlib.util
import json
from pathlib import Path

SCRIPT=Path(__file__).parent/"vendor"/"tradermonty"/"position_sizer.py"

def size_proposal(account_equity_gbp, entry_pence, stop_pence, risk_pct=1.0, max_position_pct=100.0):
    if not SCRIPT.is_file():
        return {"status":"UNAVAILABLE","reason":"Upstream position sizer missing","auto_trade":False}
    if not (0 < stop_pence < entry_pence and account_equity_gbp>0 and 0<risk_pct<=2 and 0<max_position_pct<=100):
        return {"status":"REVIEW_REQUIRED","reason":"Invalid or unsafe risk inputs","auto_trade":False}
    spec=importlib.util.spec_from_file_location("tradermonty_position_sizer",SCRIPT)
    module=importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    params=module.SizingParameters(account_size=account_equity_gbp,entry_price=entry_pence/100,
        stop_price=stop_pence/100,risk_pct=risk_pct,max_position_pct=max_position_pct)
    result=module.calculate_position(params)
    return {"status":"RESEARCH_PROPOSAL","source":"tradermonty/claude-trading-skills position-sizer",
        "currency":"GBP","input_price_unit":"GBp","result":result,
        "warnings":["Assumes stop fills at stated price; AIM gaps, spread and liquidity can make realized losses greater",
                    "Account equity, stop and spread must be verified privately before manual decision"],
        "auto_trade":False}
