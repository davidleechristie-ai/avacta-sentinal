"""Primary-source catalyst registry and conditional ISA decision overlay.

No LLM-generated probabilities, no inferred partner identity, no trade orders.
"""
from datetime import date

CATALYSTS=[
 {"id":"AVA6207_EORTC_2026","start":"2026-11-18","end":"2026-11-20",
  "topic":"AVA6207 dual-payload presentation",
  "source":"https://avacta.com/avacta-to-present-the-precision-dual-payload-candidate-ava6207-at-the-2026-eortc-nci-aacr-symposium/",
  "expectation":"Presentation details; do not infer clinical efficacy or partner identity",
  "positive_surprise":"New independently verifiable technical or commercial evidence beyond prior disclosure",
  "negative_surprise":"Material delay, adverse new safety information, or weaker evidence than previously guided"},
 {"id":"TUMOUR_PK_2026_2027","start":"2026-12-01","end":"2027-03-31",
  "topic":"Tumour pharmacokinetic data window",
  "source":"https://avacta.com/news/",
  "expectation":"Late Q4 2026 / early Q1 2027 guidance; broad approximate window",
  "positive_surprise":"Issuer-confirmed tumour delivery data exceeding stated expectations",
  "negative_surprise":"Issuer-confirmed delay or unfavourable tumour delivery findings"}
]

def assess_catalysts(research,as_of,deadline="2027-01-29"):
    day=date.fromisoformat(str(as_of)[:10])
    limit=date.fromisoformat(deadline)
    sources=research.get("sources",{})
    issuer=sources.get("avacta_news",{})
    items=issuer.get("items",[]) if issuer.get("status")=="RETRIEVED" else []
    out=[]
    for event in CATALYSTS:
        start=date.fromisoformat(event["start"]);end=date.fromisoformat(event["end"])
        if end<day:status="WINDOW_PASSED_OUTCOME_UNVERIFIED"
        elif start<=day<=end:status="IN_WINDOW"
        elif start>limit:status="BEYOND_ISA_EXIT"
        else:status="UPCOMING"
        out.append({**event,"status":status,"days_until_start":(start-day).days,
                    "within_isa_horizon":start<=limit,
                    "issuer_news_retrieved":issuer.get("status")=="RETRIEVED",
                    "surprise_assessment":"NOT_VERIFIED",
                    "actual_outcome":"UNKNOWN",
                    "related_headlines":[x for x in items if event["id"].split("_")[0].lower() in x.get("title","").lower()][:5]})
    return {"as_of":day.isoformat(),"status":"PRIMARY_SOURCE_REVIEW_REQUIRED",
            "catalysts":out,"news_retrieval":issuer.get("status","UNKNOWN"),
            "note":"Headlines and dates are not proof of event outcome or market expectations; historical event windows are not precise scheduled dates",
            "auto_trade":False}

def combine(decision,weekly,catalysts):
    current=decision.get("decision","WAIT_FOR_CONFIRMATION")
    upcoming=[e for e in catalysts["catalysts"] if e["status"] in ("UPCOMING","IN_WINDOW") and e["within_isa_horizon"]]
    bearish=weekly.get("weekly_trend_pattern")=="LOWER_HIGHS_AND_LOWS"
    bullish=weekly.get("weekly_trend_pattern")=="HIGHER_HIGHS_AND_LOWS" and weekly.get("weekly_breakout") is True
    return {"action_hypothesis":current,
            "weekly_technical_context":"BEARISH" if bearish else "BULLISH_BREAKOUT" if bullish else "MIXED_OR_INSUFFICIENT",
            "catalyst_event_risk":"PRESENT" if upcoming else "NO_UPCOMING_VERIFIED_WINDOW",
            "next_catalysts":[{"id":e["id"],"status":e["status"],"days_until_start":e["days_until_start"]} for e in upcoming],
            "entry_permission":"NOT_GRANTED",
            "reason":"Catalysts can invalidate technical patterns; require independently verified outcomes, price and manual pre-trade approval",
            "probabilities":"NOT_CALIBRATED","auto_trade":False}
