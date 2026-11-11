"""Live OpenBB probe; fail closed and save diagnostics."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from openbb_adapter import ProviderUnavailable, fetch_avct_history
from data_quality import assess_history

def main():
    path = Path("artifacts/openbb_probe.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = fetch_avct_history()
        result["quality"] = assess_history(result["observations"])
        result["status"] = "STALE_BLOCKED" if result["quality"]["is_stale"] else "UNVERIFIED_PRICE_DATA"
        result["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
        result["dashboard_guidance"] = "Do not present an unverified or stale price as live; show last_completed_session_date and last_completed_close with their date."
        result["observations"] = [{key: str(value) for key, value in row.items()} for row in result["observations"]]
        status = 0
    except ProviderUnavailable as exc:
        result = {"generated_at_utc": datetime.now(timezone.utc).isoformat(), "status": "NO_VERIFIED_DATA", "reason": str(exc), "validated_for_trading": False}
        status = 2
    path.write_text(json.dumps(result, indent=2, default=str) + "\n")
    print(result["status"], path)
    if status:
        print("PROVIDER_ERROR:", result.get("reason", "unknown"))
    return status

if __name__ == "__main__":
    sys.exit(main())
