"""Public read-only research sources; never convert missing data to zero."""
import csv,io,json,urllib.request
from datetime import datetime,timezone
from html.parser import HTMLParser
from urllib.parse import urljoin
ISIN="GB00BYYW9G87"
FCA_CURRENT="https://www.fca.org.uk/publication/documents/aggregated-current-net-short-positions.csv"
FCA_HISTORIC="https://www.fca.org.uk/publication/documents/aggregated-historic-net-short-positions.csv"
AVACTA_NEWS="https://avacta.com/news/"
CLINICAL="https://clinicaltrials.gov/api/v2/studies?query.term=Avacta&pageSize=100&format=json"
def fetch(url):
    request=urllib.request.Request(url,headers={"User-Agent":"AvactaSentinelResearch/1.0","Accept":"text/html,application/json,text/csv,*/*"})
    with urllib.request.urlopen(request,timeout=25) as response:
        return response.read(8000000).decode("utf-8-sig","replace")
def fca_report(url):
    content=fetch(url)
    if "<html" in content[:300].lower(): raise ValueError("HTML response instead of FCA CSV")
    rows=list(csv.DictReader(io.StringIO(content)))
    if not rows: raise ValueError("Empty FCA CSV")
    matches=[r for r in rows if ISIN.lower() in " ".join(map(str,r.values())).lower() or "avacta" in " ".join(map(str,r.values())).lower()]
    return {"status":"MATCHED" if matches else "NOT_LISTED","source":url,"rows":matches,"headers":list(rows[0]),"total_rows":len(rows),"note":"Not listed does not mean zero total short interest; FCA reporting thresholds apply."}
class LinkParser(HTMLParser):
    def __init__(self): super().__init__();self.links=[];self.href=None;self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag=="a":self.href=dict(attrs).get("href");self.parts=[]
    def handle_data(self,data):
        if self.href is not None:self.parts.append(data)
    def handle_endtag(self,tag):
        if tag=="a":
            if self.href:
                title=" ".join("".join(self.parts).split());url=urljoin(AVACTA_NEWS,self.href)
                if len(title)>18 and url.startswith("https://avacta.com/") and url!=AVACTA_NEWS:self.links.append({"title":title,"url":url})
            self.href=None;self.parts=[]
def issuer_news():
    parser=LinkParser();parser.feed(fetch(AVACTA_NEWS));items=list({x["url"]:x for x in parser.links}.values())
    if not items:raise ValueError("Issuer page returned no parseable links")
    return {"status":"RETRIEVED","source":AVACTA_NEWS,"items":items[:40]}
def clinical_trials():
    payload=json.loads(fetch(CLINICAL));items=[]
    for study in payload.get("studies",[]):
        p=study.get("protocolSection",{});i=p.get("identificationModule",{});s=p.get("statusModule",{})
        items.append({"nct_id":i.get("nctId"),"title":i.get("briefTitle"),"status":s.get("overallStatus"),"url":"https://clinicaltrials.gov/study/"+str(i.get("nctId",""))})
    return {"status":"RETRIEVED" if items else "NO_MATCH","source":CLINICAL,"items":items}
def collect():
    out={"retrieved_at_utc":datetime.now(timezone.utc).isoformat(),"validated_for_trading":False,"sources":{}}
    tasks={"fca_current":lambda:fca_report(FCA_CURRENT),"fca_historic":lambda:fca_report(FCA_HISTORIC),"avacta_news":issuer_news,"clinical_trials":clinical_trials}
    for name,fn in tasks.items():
        try:out["sources"][name]=fn()
        except Exception as e:out["sources"][name]={"status":"UNAVAILABLE","error":f"{type(e).__name__}: {e}"}
    return out
