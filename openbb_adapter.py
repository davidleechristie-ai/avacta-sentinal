"""Read-only adapter using the actual OpenBB SDK. No trading signals."""
from datetime import date

class ProviderUnavailable(RuntimeError):
    pass

def fetch_avct_history(start_date="2026-10-01"):
    try:
        from openbb import obb
    except ImportError as exc:
        raise ProviderUnavailable("OpenBB SDK is not installed") from exc
    try:
        result = obb.equity.price.historical(symbol="AVCT.L", start_date=start_date, provider="yfinance")
        frame = result.to_dataframe()
    except Exception as exc:
        raise ProviderUnavailable(f"OpenBB AVCT.L provider failed: {type(exc).__name__}: {exc}") from exc
    if frame is None or frame.empty:
        raise ProviderUnavailable("Provider returned no AVCT.L observations")
    observations = frame.reset_index().to_dict(orient="records")
    return {"symbol": "AVCT.L", "provider": getattr(result, "provider", "unspecified"), "observations": observations, "validated_for_trading": False}
