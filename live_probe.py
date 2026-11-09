"""Live OpenBB probe; fail closed and save diagnostics."""
import json
import sys
from pathlib import Path
from openbb_adapter import ProviderUnavailable, fetch_avct_history

def main():
    path = Path("artifacts/openbb_probe.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = fetch_avct_history()
        result["status"] = "UNVERIFIED_PRICE_DATA"
        result["observations"] = [{key: str(value) for key, value in row.items()} for row in result["observations"]]
        status = 0
    except ProviderUnavailable as exc:
        result = {"status": "NO_VERIFIED_DATA", "reason": str(exc), "validated_for_trading": False}
        status = 2
    path.write_text(json.dumps(result, indent=2, default=str) + "\n")
    print(result["status"], path)
    if status:
        print("PROVIDER_ERROR:", result.get("reason", "unknown"))
    return status

if __name__ == "__main__":
    sys.exit(main())
