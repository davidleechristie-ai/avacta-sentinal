# Avacta Sentinel — executable research integration

This public repository hosts a **read-only** hourly OpenBB integration probe for AVCT.L. It does not place trades or publish personal holdings.

## Status
GitHub Actions installs the actual `openbb` package on a hosted runner, executes the SDK API and preserves an evidence artifact. Price observations remain **unverified** until the instrument mapping, provider, date and venue are confirmed. Missing data must not become a trading signal.

The Anthropic financial-services skills `catalyst-calendar` and `thesis-tracker` are upstream research specifications, not Python plugins. Original source: https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/equity-research/skills

## Run
Use **Actions → Avacta Sentinel OpenBB probe → Run workflow**. Review the `avct-openbb-probe` artifact and job logs. The workflow also runs hourly at minute 19 UTC. It does not automatically feed ChatGPT's separate hourly Sentinel automation.

## Safety
No credentials or portfolio holdings in this public repository. Do not trade from an unverified data probe.

## Additional public-source integrations (2026-11-09)
The same hourly GitHub Actions workflow runs `research_pipeline.py` and preserves `artifacts/public_research.json`. It attempts:
- FCA current and historic ANSP CSVs, matched by Avacta name or ISIN GB00BYYW9G87. Missing company rows are **NOT_LISTED**, never zero short interest.
- Avacta's official issuer news page. Headlines are discovery leads; they do not verify financial outcomes.
- ClinicalTrials.gov API v2, using an Avacta search term. Registry matches require programme verification.
- An evidence-linked catalyst and thesis record based on the vendored Anthropic skill specifications.

These are executable adapters, **not yet proven in a live workflow run**. Each source reports an explicit UNAVAILABLE status on failure. No paid ORTEX, X API, broker research, or authenticated service is implied. No trading decisions or personal holdings are written to this public repository. The GitHub artifact is not yet ingested automatically by the separate ChatGPT hourly Sentinel automation.
