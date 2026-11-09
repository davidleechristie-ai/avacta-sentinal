# October–November 2026 downside retrospective (research audit)

## Scope and limitations
Reviewed publicly quoted daily AVCT.L closes from 9 October to 6 November 2026. This is a *counterfactual rule replay*, not a record of alerts actually delivered. Sentinel's downside module was introduced on 9 November. The trading history, execution prices and intraday liquidity were not reconstructed, so no avoided-loss claim is made.

Historical price reference: https://uk.investing.com/equities/avacta-group-plc-historical-data
Secondary reference: https://markets.ft.markitdigital.com/data/equities/tearsheet/historical?s=AVCT%3ALSE

9 October close: 65.5p. 6 November close: 53.8p. Change: -11.7p (-17.86%). A static 24,265-share holding would decline in mark-to-market value by approximately £2,839; this is NOT the owner's realised or actual portfolio P&L because trades occurred.

## What the revised rules would have highlighted
Using the visible October/November subset and sufficient prior valid sessions:
- 26 October close 62.5p: approximately -8.1% versus the close five sessions earlier. The new 7% five-session decline warning would be HIGH.
- 27 October close 61.5p: below the preceding ten-session low of 62.0p; another HIGH warning. The recent closing-peak drawdown was approximately -10% (rounding matters).
- 2 November close 58.7p: below prior ten-session support of 60p, with approximately -14.1% drawdown from the 68.3p recent closing peak; CRITICAL under combined rules.
- 3 November close 57.5p: approximately -15.8% from that peak; CRITICAL under the independent 15% threshold.
- 6 November close 53.8p: approximately -21.2% from that peak; CRITICAL.

The exact earliest alert from the full dataset may differ because the demonstration window begins on 9 October. The automated replay is authoritative only after data-quality checks and historical-provider validation.

## Root causes
1. Bullish-only technical scorecard: no independent deterioration or broken-support escalation.
2. No capital-at-risk or position-size-aware private decision framework.
3. Financing/cash-runway evidence collected but not scored as a downside risk.
4. No backtested alert latency, false-positive rates, or demonstrated delivery.
5. Public data can include zero-volume bars and incomplete intraday sessions; data-quality uncertainty must be visible.
6. No private delivery channel integrated with GitHub Actions; workflow summaries are not push notifications.

## Remediation delivered
- Independent downside_guard.py with severity, explicit rules, and fail-closed unknown status.
- retrospective.py replays warnings using only observations available as of each historical date.
- Hourly scorecard includes downside_guard and separate downside_retrospective.json artifact.
- HIGH/CRITICAL surfaced in GitHub Actions warning and job summary.
- Automated tests cover support breaks, drawdowns, flat markets, incomplete history and no lookahead.

## Remaining gates
- Validate historical data and identify whether the current session is final.
- Add longer history and market-session calendars to reduce truncated lookbacks.
- Quantify alert lead time, false alarms, whipsaws, spreads, and hypothetical transaction costs.
- Integrate a private, permissioned delivery channel; GitHub summary alone does not proactively notify the owner.
- Keep holdings, tax information, and actual trades out of this public repository.
- No auto-trading. Warnings require human interpretation and execution decisions.
