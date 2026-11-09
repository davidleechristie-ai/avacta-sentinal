"""Evidence-limited AVCT.L technical observations, not trade recommendations."""
from statistics import mean

def assess_technicals(rows):
    """Use only valid, positive-volume sessions; avoid zero-volume synthetic bars."""
    bars = sorted((r for r in rows if r["volume"] > 0), key=lambda r: r["date"])
    result = {"price_reversal": "INSUFFICIENT_DATA", "sustained_volume": "INSUFFICIENT_DATA",
              "evidence": {}, "trade_signal": False}
    if len(bars) < 22:
        result["evidence"]["valid_sessions"] = len(bars)
        return result
    recent = bars[-22:]
    latest = recent[-1]
    prior20 = recent[-21:-1]
    resistance = max(r["high"] for r in prior20)
    avg20_volume = mean(r["volume"] for r in prior20)
    volume_ratio = latest["volume"] / avg20_volume if avg20_volume > 0 else 0
    higher_low = min(r["low"] for r in recent[-5:-2]) > min(r["low"] for r in recent[-10:-5])
    breakout = latest["close"] > resistance
    result["price_reversal"] = "CONFIRMED_TECHNICAL_PATTERN" if higher_low and breakout else "NOT_CONFIRMED"
    result["sustained_volume"] = "CONFIRMED_2_SESSIONS" if (
        latest["volume"] >= 1.5 * avg20_volume and
        recent[-2]["volume"] >= 1.5 * avg20_volume
    ) else "NOT_CONFIRMED"
    result["evidence"] = {
        "latest_session": latest["date"], "latest_close": latest["close"],
        "prior_20_session_high": round(resistance, 4),
        "higher_low": higher_low, "resistance_break": breakout,
        "latest_volume": latest["volume"], "average_prior_20_volume": round(avg20_volume),
        "latest_volume_ratio": round(volume_ratio, 3),
        "consecutive_high_volume_sessions": 2 if result["sustained_volume"] == "CONFIRMED_2_SESSIONS" else 0,
        "valid_sessions": len(bars),
    }
    return result
