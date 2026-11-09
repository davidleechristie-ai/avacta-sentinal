"""Evidence-linked catalyst calendar and thesis tracker. No trade advice."""
from datetime import date
CATALYSTS=[
 {"id":"ava6207","topic":"AVA6207 payload disclosure","window":"Q4 2026","source":"https://avacta.com/news/"},
 {"id":"ava6103-pk","topic":"AVA6103 tumour PK/biopsy evidence","window":"late Q4 2026 / early Q1 2027","source":"https://avacta.com/interim-results-for-the-six-months-to-june-30-2026-and-business-update/"},
 {"id":"focus01-efficacy","topic":"FOCUS-01 initial efficacy","window":"H1 2027","source":"https://avacta.com/interim-results-for-the-six-months-to-june-30-2026-and-business-update/"}]
def build(sources):
    headlines=sources.get("avacta_news",{}).get("items",[])
    events=[]
    for item in CATALYSTS:
        terms={"ava6207":["ava6207"],"ava6103-pk":["ava6103","biopsy"],"focus01-efficacy":["focus-01","efficacy"]}[item["id"]]
        events.append({**item,"related_headlines":[h for h in headlines if any(t in h["title"].lower() for t in terms)][:8],"outcome":"UNVERIFIED"})
    return {"as_of":date.today().isoformat(),"catalysts":events,"thesis":{"short_interest":"REQUIRES_FCA_INTERPRETATION","financing":"REQUIRES_ISSUER_DOCUMENT_REVIEW","catalysts":"REQUIRES_EVENT_CONFIRMATION"},"trade_signal":False,"method":"Anthropic catalyst-calendar/thesis-tracker inspired evidence record; original skills remain upstream specifications"}
