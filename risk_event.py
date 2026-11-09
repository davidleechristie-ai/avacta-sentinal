"""Public-data-only risk event. Designed for private notification integration later."""
import hashlib,json
def build_event(downside):
    severity=downside.get("severity","UNKNOWN")
    date=downside.get("latest_session")
    warnings=sorted(set(downside.get("warnings",[])))
    if severity not in ("HIGH","CRITICAL") or not date:
        return {"status":"NO_ACTIONABLE_RISK_EVENT","delivery":"NOT_CONFIGURED","trade_signal":False}
    key="AVCT.L|"+date+"|"+severity+"|"+",".join(warnings)
    return {"status":"RISK_EVENT","event_id":hashlib.sha256(key.encode()).hexdigest()[:20],
            "symbol":"AVCT.L","session":date,"severity":severity,"warnings":warnings,
            "message":"Review downside conditions; not a trade instruction.",
            "delivery":"NOT_CONFIGURED","trade_signal":False}
