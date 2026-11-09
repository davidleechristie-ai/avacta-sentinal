# TraderMonty trading-skills integration — AVCT

Source: https://github.com/tradermonty/claude-trading-skills
License: MIT, copyright TraderMonty; see vendor/tradermonty/LICENSE.
Vendored source files are read-only research dependencies; upstream scripts are not executed on CI unless explicitly invoked by the tested adapter.

## Selected upstream skills
- **position-sizer**: Actual upstream Python implementation vendored as vendor/tradermonty/position_sizer.py. Called by tradermonty_adapter.py using GBp-to-GBP conversion and explicit private risk inputs. Does not create orders.
- **technical-analyst**: Upstream SKILL.md instructions vendored; primarily weekly *chart-image* analysis. Not a daily OHLCV calculation engine; weekly charts must be provided and independently checked. Do not fabricate probabilities.
- **pre-trade-discipline-gate**: Methodology retained for future private manual-order checklist. Its executable dependency chain is NOT installed or active.
- **signal-postmortem**: Methodology retained for research outcomes and future private decision journaling. Its executable dependency chain is NOT installed or active.

## AVCT-specific constraints
- AVCT.L is quoted in **pence (GBp)** while account risk is in **GBP**. Convert prices /100 before sizing.
- No executable stop is guaranteed on a thinly traded AIM stock; gaps, spread, auctions and slippage can exceed nominal risk.
- No automatic Kelly sizing without independently validated edge and sufficient sample size.
- No US-only screener assumptions or unverified FMP/Alpaca data.
- Do not write private ISA equity or holdings to public GitHub artifacts.
- Short-term ISA mandatory exit by 2027-01-29; long-term SIPP excluded.
- The upstream repository describes itself as a research and process toolkit, not a predictive signal service.
- All outputs are research proposals; owner alone authorizes any manual order.

## Next stages
1. Validate the upstream adapter against actual GitHub Actions tests.
2. Build chart-based technical report from verified weekly AVCT prices, not unverified intraday candles.
3. Connect an offline discipline checklist and signal postmortem using verified inputs.
4. Audit forecasting against unconditional drift and costs, never equate stars with predictive accuracy.
