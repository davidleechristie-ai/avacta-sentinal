"""Read-only market-data quality gates for AVCT.L."""
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal, InvalidOperation
from technical_scorecard import assess_technicals

def assess_history(observations, as_of=None):
    as_of = as_of or datetime.now(timezone.utc).date()
    clean = []
    flags = []
    for index, row in enumerate(observations):
        try:
            d = date.fromisoformat(str(row["date"])[:10])
            values = {key: Decimal(str(row[key])) for key in ("open", "high", "low", "close", "volume")}
            if not all(v.is_finite() for v in values.values()):
                raise ValueError("nonfinite")
            if min(values[k] for k in ("open", "high", "low", "close")) <= 0:
                raise ValueError("nonpositive price")
            if values["volume"] < 0 or values["high"] < max(values["open"], values["close"], values["low"]) or values["low"] > min(values["open"], values["close"], values["high"]):
                raise ValueError("inconsistent OHLCV")
            if values["volume"] == 0:
                flags.append({"date": d.isoformat(), "issue": "zero_volume"})
            clean.append({"date": d.isoformat(), **{k: float(v) for k, v in values.items()}})
        except (KeyError, ValueError, TypeError, InvalidOperation) as exc:
            flags.append({"row": index, "issue": "invalid_ohlcv", "detail": str(exc)})
    clean.sort(key=lambda x: x["date"])
    unique = {r["date"]: r for r in clean}
    if len(unique) != len(clean):
        flags.append({"issue": "duplicate_dates"})
    clean = list(unique.values())
    if not clean:
        return {"status": "BLOCKED", "reason": "no_valid_observations", "flags": flags, "validated_for_trading": False}
    last = clean[-1]
    age = (as_of - date.fromisoformat(last["date"])).days
    # A daily OHLC bar dated today is potentially unfinished while AIM is open.
    # Never label it a completed close or use it as a confirmed daily signal.
    now = datetime.now(timezone.utc)
    market_open = as_of == now.date() and now.weekday() < 5 and (now.hour < 17)
    completed = [r for r in clean if date.fromisoformat(r["date"]) < as_of] if market_open else clean
    completed_last = completed[-1] if completed else None
    completed_age = (as_of - date.fromisoformat(completed_last["date"])).days if completed_last else None
    stale = completed_age is None or completed_age > 4 or (completed_last and date.fromisoformat(completed_last["date"]) > as_of)
    if age < 0 or stale:
        flags.append({"issue": "stale_or_future", "calendar_days": completed_age})
    if market_open and last["date"] == as_of.isoformat():
        flags.append({"issue": "unfinished_current_session", "date": last["date"]})
    valid_volume = [r for r in clean if r["volume"] > 0]
    if len(valid_volume) < 10:
        flags.append({"issue": "insufficient_nonzero_volume_history", "count": len(valid_volume)})
    technicals = assess_technicals(completed) if len(completed) >= 10 and not stale else {"price_reversal": "UNKNOWN", "sustained_volume": "UNKNOWN", "evidence": "Blocked: stale or insufficient completed-session history"}
    return {
        "status": "STALE_BLOCKED" if stale else ("REVIEW_REQUIRED" if flags else "PRELIMINARY"),
        "data_as_of_utc": now.isoformat(),
        "last_observation_date": last["date"],
        "last_completed_session_date": completed_last["date"] if completed_last else None,
        "last_completed_close": completed_last["close"] if completed_last else None,
        "current_session_observation": last if market_open and last["date"] == as_of.isoformat() else None,
        "is_stale": bool(stale),
        "market_session_status": "OPEN_OR_UNFINISHED" if market_open else "CLOSED_OR_NON_TRADING_DAY",
        "latest": last, "observations": len(clean),
        "valid_volume_sessions": len(valid_volume),
        "flags": flags,
        "validated_for_trading": False,
        "price_reversal": technicals["price_reversal"],
        "sustained_volume": technicals["sustained_volume"],
        "technical_evidence": technicals["evidence"],
        "fca_short_exposure": "NOT_ASSESSED",
        "financing_dilution": "NOT_ASSESSED",
        "catalyst_timing": "NOT_ASSESSED"
    }
