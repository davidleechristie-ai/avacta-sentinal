"""Offline SVG price chart; completed-session observations only, not a trade signal."""
from html import escape
from math import isfinite

def render_chart(rows, levels=None, limit=70):
    levels=levels or {}
    valid=[]
    for bar in rows:
        try:
            close=float(bar["close"]); volume=float(bar["volume"])
            if isfinite(close) and close>0 and isfinite(volume) and volume>=0:
                valid.append((str(bar["date"]),close,volume))
        except (KeyError,ValueError,TypeError): pass
    bars=sorted(valid,key=lambda x:x[0])[-limit:]
    if len(bars)<3:
        return "<p>Insufficient completed-session price data to chart.</p>"
    annotations=[]
    for key,label,color in (("downside_candidates","Downside","#e7a66c"),("broken_support","Broken support","#d7bd76"),("overhead_resistance","Overhead","#77b9e6")):
        for item in (levels.get(key) or [])[:2]:
            try:
                value=float(item["level_pence"])
                if isfinite(value) and value>0:annotations.append((value,label,color))
            except (KeyError,ValueError,TypeError):pass
    prices=[b[1] for b in bars]+[x[0] for x in annotations]
    lo=min(prices);hi=max(prices);span=max(hi-lo,1.0);lo-=span*.1;hi+=span*.1
    def x(i):return 56+i*750/max(len(bars)-1,1)
    def y(v):return 30+(hi-v)*235/(hi-lo)
    points=" ".join(f"{x(i):.1f},{y(b[1]):.1f}" for i,b in enumerate(bars))
    maxvol=max(b[2] for b in bars) or 1
    parts=['<svg viewBox="0 0 850 370" role="img" aria-label="Completed-session AVCT close and volume with observed historical price levels" style="width:100%;height:auto;background:#0b1728;border-radius:12px">']
    for j in range(5):
        value=lo+(hi-lo)*j/4; yy=y(value)
        parts.append(f'<line x1="52" y1="{yy:.1f}" x2="815" y2="{yy:.1f}" stroke="#33465b" stroke-width="1"/><text x="5" y="{yy+4:.1f}" fill="#b9c9da" font-size="12">{value:.1f}p</text>')
    for i,b in enumerate(bars):
        height=55*b[2]/maxvol
        parts.append(f'<rect x="{x(i)-2:.1f}" y="{345-height:.1f}" width="4" height="{height:.1f}" fill="#456f91"/>')
    for value,label,color in annotations:
        yy=y(value)
        parts.append(f'<line x1="52" y1="{yy:.1f}" x2="815" y2="{yy:.1f}" stroke="{color}" stroke-dasharray="5 5" opacity=".8"/>')
        parts.append(f'<text x="808" y="{yy-5:.1f}" text-anchor="end" fill="{color}" font-size="11">{escape(label)} {value:.1f}p</text>')
    parts.append(f'<polyline fill="none" stroke="#d7e7fa" stroke-width="2.5" points="{points}"/>')
    parts.append(f'<circle cx="{x(len(bars)-1):.1f}" cy="{y(bars[-1][1]):.1f}" r="4" fill="#fff"/>')
    parts.append(f'<text x="55" y="365" fill="#b9c9da" font-size="12">{escape(bars[0][0])}</text><text x="815" y="365" text-anchor="end" fill="#b9c9da" font-size="12">{escape(bars[-1][0])}</text></svg>')
    return "".join(parts)
