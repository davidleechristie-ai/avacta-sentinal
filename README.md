# Avacta Sentinel — executable research integration

This public repository hosts a **read-only** hourly OpenBB integration probe for AVCT.L. It does not place trades or publish personal holdings.

## Status
GitHub Actions installs the actual `openbb` package on a hosted runner, executes the SDK API and preserves an evidence artifact. Price observations remain **unverified** until the instrument mapping, provider, date and venue are confirmed. Missing data must not become a trading signal.

The Anthropic financial-services skills `catalyst-calendar` and `thesis-tracker` are upstream research specifications, not Python plugins. Original source: https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/equity-research/skills

## Run
Use **Actions → Avacta Sentinel OpenBB probe → Run workflow**. Review the `avct-openbb-probe` artifact and job logs. The workflow also runs hourly at minute 19 UTC. It does not automatically feed ChatGPT's separate hourly Sentinel automation.

## Safety
No credentials or portfolio holdings in this public repository. Do not trade from an unverified data probe.
