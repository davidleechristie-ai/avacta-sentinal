"""Generate a self-contained, read-only decision dashboard from Sentinel research."""
from html import escape
from pathlib import Path
from math import isfinite
from market_thesis import build as build_market_thesis

def render(report, scorecard=None):
    scorecard=scorecard or {}
    def e(v):
        return escape("—" if v is None else str(v),quote=True)
    def number(v,suffix=""):
        if v is None:
            return "Not established"
        try:
            n=float(v)
            if not isfinite(n):
                return "Not established"
            return e(f"{n:,.2f}")+suffix
        except (TypeError,ValueError):
            return e(v)+suffix
    levels=report.get("forward_levels") or {}
    quality=report.get("data_quality") or {}
    audit=(scorecard.get("decision_intelligence") or {}).get("independent_price_evidence") or {}
    def audit_table():
        rows=[("Price corroboration",audit.get("status","NOT_VERIFIED")),
              ("Provider count",audit.get("independent_providers",0)),
              ("Verification reason",audit.get("reason","Not supplied")),
              ("Risk assessment",report.get("downside_severity","UNKNOWN")),
              ("Positioning confidence",report.get("confidence","UNKNOWN"))]
        return "".join("<tr><th scope='row'>"+e(k)+"</th><td>"+e(v)+"</td></tr>" for k,v in rows)
    structure=scorecard.get("technical_structure") or {}
    def structure_table():
        events=(structure.get("events") or [])[-6:]
        if not events:
            return "<p>No qualifying completed-session range-break observations.</p>"
        rows=[]
        for event in reversed(events):
            rows.append("<tr><td>"+e(event.get("date"))+"</td><td>"+e(event.get("kind","").replace("_"," "))+"</td><td>"+number(event.get("reference_level_pence"),"p")+"</td><td>"+e(event.get("volume_confirmation"))+"</td><td>"+e(event.get("next_session_status"))+"</td></tr>")
        return "<div style='overflow-x:auto'><table><thead><tr><th>Session</th><th>Observation</th><th>Range level</th><th>Volume</th><th>Follow-up</th></tr></thead><tbody>"+"".join(rows)+"</tbody></table></div>"
    performance=scorecard.get("forward_signal_audit") or {}
    chart=scorecard.get("technical_chart_html") or "<p>Chart unavailable until completed-session data is processed.</p>"
    weekly_chart=scorecard.get("weekly_chart_html") or "<p>Weekly chart unavailable until sufficient completed sessions are processed.</p>"
    def performance_table():
        summary=performance.get("summary") or {}
        if not summary:
            return "<p>No matured historical warning outcomes available.</p>"
        rows=[]
        for horizon in ("1","3","5","10"):
            item=summary.get(horizon) or {}
            count=item.get("evaluated_events",0)
            decline=item.get("subsequent_decline_fraction")
            mean=item.get("mean_forward_return_pct")
            rows.append("<tr><th scope='row'>"+e(horizon)+" sessions</th><td>"+e(count)+"</td><td>"+(e(round(decline*100,1))+"%" if decline is not None else "—")+"</td><td>"+(e(mean)+"%" if mean is not None else "—")+"</td></tr>")
        return "<table><thead><tr><th>Horizon</th><th>Events</th><th>Declined</th><th>Mean return</th></tr></thead><tbody>"+"".join(rows)+"</tbody></table>"
    catalyst=report.get("next_catalyst")
    scenarios=report.get("scenario_matrix") or {}
    events=report.get("event_positioning_rules") or {}
    def items(values):
        return "".join("<li>"+e(x)+"</li>" for x in values)
    def level_list(key):
        values=levels.get(key) or []
        return ", ".join(number(x.get("level_pence"),"p") for x in values) if values else "No historical level established"
    def scenario(name):
        x=scenarios.get(name,{})
        return '<section class="scenario"><h3>'+e(name.title())+'</h3><p>'+e(x.get("condition"))+'</p><small>'+e(x.get("review"))+'</small></section>'
    stance=report.get("stance","UNKNOWN")
    severity=report.get("downside_severity","UNKNOWN")
    quality_note="Independent price verification outstanding" if not quality.get("independently_verified_price") else "Price source flagged verified by upstream process; verify its provenance"
    verified=bool(quality.get("independently_verified_price"))
    thesis=build_market_thesis(report,scorecard)
    steer=thesis["view"]
    why=thesis["thesis"]+" "+thesis["decision"]
    evidence=thesis["catalyst"]+" "+thesis["horizon"]
    change=thesis["discriminators"]
    next_event=thesis["confidence"]
    mechanism_html="<section class='card section'><h2>Competing market explanations — what would distinguish them?</h2>"+ "".join("<h3>"+e(m["name"])+"</h3><p><strong>Current interpretation:</strong> "+e(m["evidence"])+"</p><p><strong>Critical missing evidence:</strong> "+e(m["missing"])+"</p><p><strong>Discriminating test:</strong> "+e(m["test"])+"</p>" for m in thesis["mechanisms"])+"<small>"+e(thesis["limitations"])+"</small></section>"
    html="""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Avacta Sentinel | ISA decision brief</title><style>
:root{color-scheme:dark;font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif;background:#0b1220;color:#e8eef7}
*{box-sizing:border-box}body{margin:0}main{max-width:1150px;margin:auto;padding:28px 20px 70px}
header{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;border-bottom:1px solid #2c394b;padding-bottom:22px}
.brand{font-weight:800;letter-spacing:.1em;color:#a5c8ed;font-size:13px}.meta{color:#aebed1;font-size:13px}
h1{font-size:clamp(27px,4vw,43px);margin:10px 0}h2{font-size:18px;margin:0 0 16px}h3{font-size:15px;margin:0 0 8px}
p{line-height:1.55;color:#cbd6e4}small,.subtle{color:#aebed1;line-height:1.5}
.decision-list{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:18px}.decision-item{border:1px solid #35465a;border-radius:12px;padding:14px;background:#101e30}.decision-item h3{color:#a5c8ed;font-size:12px;text-transform:uppercase;letter-spacing:.08em}.decision-item p{margin:8px 0 0}.hero{background:linear-gradient(130deg,#15273c,#111c2c);border:1px solid #35465a;border-radius:18px;padding:28px;margin:24px 0}
.eyebrow{font-size:12px;text-transform:uppercase;letter-spacing:.12em;color:#aebed1}.stance{font-size:clamp(20px,3vw,30px);font-weight:750;margin:12px 0;overflow-wrap:anywhere}
.pill{display:inline-block;border:1px solid #986945;background:#422d23;color:#ffd1aa;border-radius:20px;padding:6px 11px;font-size:12px;font-weight:700}
.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}.two{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.card,.scenario{background:#111c2c;border:1px solid #2a3a4f;border-radius:14px;padding:19px;min-width:0}
.value{font-size:25px;font-weight:750;margin:8px 0;overflow-wrap:anywhere;font-variant-numeric:tabular-nums}.label{font-size:12px;color:#aebed1}
.section{margin-top:28px}.scenario{border-top:3px solid #6b9dc9}
ul{margin:10px 0 0;padding-left:19px}li{margin:9px 0;color:#d0dae7;line-height:1.45}
.warning{border-left:4px solid #e5a25c;padding:14px 18px;background:#30271f;color:#ffdbb9;margin:20px 0}
table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:12px 8px;border-bottom:1px solid #2c394b;font-size:14px}th{color:#aebed1;font-weight:500;width:43%}.footer{margin-top:30px;border-top:1px solid #2c394b;padding-top:20px;color:#aebed1;font-size:12px}
a{color:#9ac7fb;overflow-wrap:anywhere}.kv{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media(max-width:760px){.decision-list{grid-template-columns:1fr}.grid,.two{grid-template-columns:1fr 1fr}.kv{grid-template-columns:1fr}}
@media(max-width:460px){.grid,.two{grid-template-columns:1fr}main{padding:18px 14px 50px}.hero{padding:20px}}
@media print{:root{color-scheme:light;background:white;color:#17202d}body{background:white}.card,.scenario,.hero{background:white;color:#17202d;border-color:#aaa}p,li,small,.subtle,.label{color:#344}a{color:#135b8a}.warning{background:#fff4e8;color:#653c13}}
</style></head><body><main>
<header><div><div class="brand">AVACTA SENTINEL / DECISION INTELLIGENCE</div><h1>ISA positioning brief</h1></div><div class="meta">AVCT.L · Research only<br>As of {{DATE}}</div></header>
<section class="hero"><div class="eyebrow">Sentinel decision brief · Short-term ISA</div><div class="stance">{{STEER}}</div><span class="pill">{{SEVERITY}} downside risk</span><div class="decision-list"><div class="decision-item"><h3>Why this steer</h3><p>{{WHY}}</p></div><div class="decision-item"><h3>Evidence observed</h3><p>{{EVIDENCE}}</p></div><div class="decision-item"><h3>What changes the view</h3><p>{{CHANGE}}</p></div></div><p><strong>Next catalyst:</strong> {{NEXT_EVENT}} · <strong>ISA exit:</strong> {{DEADLINE}}</p><div class="subtle">Research steer only · Independent price verification {{VERIFY_STATUS}} · Owner approval required · No automatic trades · Long-term SIPP excluded</div></section>
{{MECHANISMS}}
<div class="grid">
<div class="card"><div class="label">Observed completed close</div><div class="value">{{CLOSE}}</div><small>Unverified feed; not a live quote</small></div>
<div class="card"><div class="label">Days until ISA exit</div><div class="value">{{DAYS}}</div><small>Deadline {{DEADLINE}}</small></div>
<div class="card"><div class="label">Weekly structure</div><div class="value" style="font-size:17px">{{TREND}}</div><small>Chart image not reviewed</small></div>
<div class="card"><div class="label">Relative weekly volume</div><div class="value">{{VOLUME}}</div><small>Historical comparison</small></div></div>
<div class="warning"><strong>Data-quality gate:</strong> {{QUALITY}}. No executable entry permission is granted by this dashboard.</div>
<section class="card section"><h2>Annotated price and volume</h2><p>Completed-session closing prices, observed historical levels and volume. Prices remain independently unverified.</p>{{CHART}}<h3 style="margin-top:24px">Weekly trend · up to 26 trading weeks</h3><p>Weekly closing prices and summed volume. The latest week may be incomplete; annotations remain historical and unverified.</p>{{WEEKLY_CHART}}</section>
<section class="card section"><h2>Breakout and breakdown evidence</h2><p>Close-only breaks of the preceding ten-session range; volume support requires at least 1.5× the preceding ten-session median. Next-session follow-up is only assessed once completed. Observational and unverified.</p>{{STRUCTURE}}</section>
<div class="two section">
<section class="card"><h2>Technical map</h2><div class="kv">
<div><div class="label">Prior eight-week support</div><div class="value" style="font-size:21px">{{SUPPORT}}</div></div>
<div><div class="label">Prior eight-week resistance</div><div class="value" style="font-size:21px">{{RESISTANCE}}</div></div></div>
<p><strong>Support context:</strong> {{SUPPORT_CONTEXT}}</p>
<p><strong>Historical downside candidates:</strong> {{DOWNSIDE}}</p>
<p><strong>Overhead levels:</strong> {{OVERHEAD}}</p>
<small>These are unverified historical pivots, not price targets, order levels or guaranteed liquidity.</small></section>
<section class="card"><h2>Next catalyst</h2>{{CATALYST}}
<h3 style="margin-top:18px">Before / during / after</h3>{{EVENT_RULES}}</section></div>
<section class="section"><h2>Scenario playbook — no assigned probabilities</h2><div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(230px,1fr))">{{SCENARIOS}}</div></section>
<div class="two section">
<section class="card"><h2>Evidence required before considering an add</h2><ul>{{ADD}}</ul></section>
<section class="card"><h2>Evidence prompting a reduction review</h2><ul>{{REDUCE}}</ul></section></div>
<section class="card section"><h2>Historical warning outcomes</h2><p>Observed completed-session returns following new downside escalations. This is not a backtested trading strategy, execution result, or evidence of predictive accuracy.</p>{{PERFORMANCE}}<small>Small samples, overlapping signals, corporate actions, spreads and execution costs may distort comparisons. A holding benchmark and live decision journal are not yet available.</small></section>
<section class="card section"><h2>Evidence audit</h2><p>Verification and confidence are displayed separately from the decision hypothesis.</p><table>{{AUDIT}}</table></section>
<section class="card section"><h2>Safety & provenance</h2>
<ul><li>Completed-session accepted: {{SESSION}}</li><li>Independent price verification: {{VERIFIED}}</li><li>Pre-trade gate: {{PRETRADE}}</li><li>Catalyst outcomes verified: {{CATALYST_VERIFIED}}</li><li>All positions and order approvals remain outside this public workflow.</li></ul></section>
<div class="footer">Research decision support only. Not a broker order, personalised execution instruction or prediction. No automatic trades. The long-term SIPP is excluded. Prices are pence (GBp).</div>
</main></body></html>"""
    if catalyst:
        cat='<p><strong>'+e(catalyst.get("id"))+'</strong></p><p>'+e(catalyst.get("days_until_start"))+' days until window start · outcome unverified</p><a href="'+e(catalyst.get("source"))+'" rel="noopener noreferrer">Issuer source</a>'
    else:
        cat="<p>No upcoming registry event within the ISA horizon.</p>"
    rule_html="<ul>"+items([key.replace("_"," ").title()+": "+val for key,val in events.items()])+"</ul>"
    substitutions={
        "DATE":e(report.get("as_of")),"STANCE":e(stance.replace("_"," ")),"SEVERITY":e(severity),
        "STEER":e(steer),"WHY":e(why),"EVIDENCE":e(evidence),"CHANGE":e(change),
        "NEXT_EVENT":e(next_event),"VERIFY_STATUS":e("confirmed" if verified else "outstanding"),
        "MECHANISMS":mechanism_html,
        "RATIONALE":e(report.get("rationale")),"CLOSE":number(report.get("observed_close_pence"),"p"),
        "DAYS":e(report.get("days_to_exit")),"DEADLINE":e(report.get("isa_exit_deadline")),
        "TREND":e(str(report.get("weekly_trend","UNKNOWN")).replace("_"," ")),
        "VOLUME":number(report.get("weekly_relative_volume"),"×"),
        "QUALITY":e(quality_note),"SUPPORT":number(report.get("weekly_support_pence"),"p"),
        "RESISTANCE":number(report.get("weekly_resistance_pence"),"p"),
        "SUPPORT_CONTEXT":e(str(report.get("support_context","UNKNOWN")).replace("_"," ")),
        "DOWNSIDE":level_list("downside_candidates"),"OVERHEAD":level_list("overhead_resistance"),
        "CATALYST":cat,"EVENT_RULES":rule_html,
        "SCENARIOS":"".join(scenario(x) for x in ("bull","base","bear")),
        "ADD":items(report.get("change_to_consider_add",[])),
        "REDUCE":items(report.get("change_to_review_reduction",[])),
        "AUDIT":audit_table(),
        "CHART":chart,
        "STRUCTURE":structure_table(),
        "WEEKLY_CHART":weekly_chart,
        "PERFORMANCE":performance_table(),
        "SESSION":e(quality.get("completed_session_accepted")),
        "VERIFIED":e(quality.get("independently_verified_price")),
        "PRETRADE":e(report.get("pretrade_gate")),
        "CATALYST_VERIFIED":e(quality.get("catalyst_outcomes_verified"))
    }
    for key,value in substitutions.items():
        html=html.replace("{{"+key+"}}",value)
    return html

def write_dashboard(report,path,scorecard=None):
    Path(path).write_text(render(report,scorecard),encoding="utf-8")
