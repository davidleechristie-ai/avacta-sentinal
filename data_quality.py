"""Read-only market-data quality gates for AVCT.L."""
from datetime import date, datetime, timezone
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
    if age < 0 or age > 4:
        flags.append({"issue": "stale_or_future", "calendar_days": age})
    valid_volume = [r for r in clean if r["volume"] > 0]
    if len(valid_volume) < 10:
        flags.append({"issue": "insufficient_nonzero_volume_history", "count": len(valid_volume)})
    technicals = assess_technicals(clean)
    return {
        "status": "REVIEW_REQUIRED" if flags else "PRELIMINARY",
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
