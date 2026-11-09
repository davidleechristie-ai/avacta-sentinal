"""Run public-source collectors; write machine-readable evidence artifact."""
import json
from pathlib import Path
from public_sources import collect
from catalyst_tracker import build
def main():
    result=collect();result["research"]=build(result["sources"])
    path=Path("artifacts/public_research.json");path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2,default=str)+"\n")
    for name,data in result["sources"].items():print(name,data["status"])
    print("Evidence artifact:",path)
    return 0 if any(x["status"] in ("MATCHED","NOT_LISTED","RETRIEVED") for x in result["sources"].values()) else 2
if __name__=="__main__":raise SystemExit(main())
