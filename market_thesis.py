"""Evidence-constrained AVCT trading thesis: distinguish observation, hypothesis and proof."""
def build(report, scorecard):
    q=report.get("data_quality") or {}
    verified=bool(q.get("independently_verified_price"))
    factors=scorecard.get("factors") or {}
    shorts=factors.get("fca_short_exposure") or {}
    financing=factors.get("financing_dilution") or {}
    structure=(scorecard.get("technical_structure") or {}).get("events") or []
    last=structure[-1] if structure else {}
    catalyst=report.get("next_catalyst") or {}
    close=report.get("observed_close_pence")
    support=report.get("weekly_support_pence")
    try: broken=float(close)<float(support)
    except (TypeError,ValueError): broken=False
    short_known=shorts.get("status")=="VERIFIED_TREND"
    finance_known=financing.get("status")=="VERIFIED"
    thesis=("Former support is now a potential supply zone, not a buy trigger" if broken else
            "Price structure alone does not establish a favourable entry")
    mechanisms=[
      {"name":"Overhang / forced or discretionary supply","evidence":"A sustained inability to reclaim broken support would be consistent with persistent supply." if broken else "Requires verified turnover, failed rallies and available auction/order-book evidence.","missing":"Seller identity, broker inventory and verified transaction-level flows.","test":"Does price repeatedly reject the former support zone despite material turnover?"},
      {"name":"Short covering or speculative event positioning","evidence":"A rally before a scientific presentation can occur without a change in fundamental value.","missing":"Dated FCA position changes and borrow data; FCA thresholds conceal smaller positions.","test":"Does a rally persist after the event, or fade once anticipation and covering subside?"},
      {"name":"Fundamental repricing","evidence":"Would require genuinely incremental clinical, platform or commercial disclosure.","missing":"Primary-source comparison against prior guidance and an independently defensible valuation impact.","test":"Does the release change probability of technical success, commercial economics or funding needs?"},
    ]
    event_name=str(catalyst.get("id") or "the next disclosed catalyst")
    days=catalyst.get("days_until_start")
    event=("The "+event_name+" window starts in "+str(days)+" days. " if isinstance(days,int) and days>=0 else "")
    event+=("Separate what is already guided from genuinely new evidence. A warhead or partner-related technical reveal is not automatically proof of a commercial agreement, clinical efficacy or a near-term cash inflow.")
    position=("The ISA must be exited by "+str(report.get("isa_exit_deadline"))+
              ". A catalyst outside the remaining horizon has no direct trading value for this account; even a positive disclosure can gap down if expectations are higher.")
    view=("WATCH FOR EVENT-DRIVEN MISPRICING; NO VERIFIED EDGE YET" if not verified else
          "ASSESS EVENT ASYMMETRY AGAINST EXECUTABLE PRICE AND LIQUIDITY")
    if broken: view="BROKEN-SUPPORT OVERHANG VS CATALYST REPRICING — EDGE UNPROVEN"
    return {"view":view,"thesis":thesis,"mechanisms":mechanisms,"catalyst":event,"horizon":position,
      "discriminators":"Verify independent OHLCV and bid/ask; compare dated short disclosures; inspect issuer financing terms and cash runway; quantify what the event changes versus prior guidance.",
      "decision":"Do not add solely because price is down, and do not automatically sell solely because support broke. Evaluate exposure against event-gap risk, remaining ISA horizon and a verified alternative explanation for price weakness.",
      "confidence":"LOW — independent market data missing" if not verified else "CONDITIONAL — source checks still required",
      "limitations":"Hypotheses, not attributed flows, calibrated probabilities or executable orders. No automatic trading.",
      "auto_trade":False}
