# Architecture Map

This file stays intentionally short. Its job is to answer:

- Where does code for a given capability live?
- What boundaries should changes preserve?

## System overview

`vnstock` is a Python library for Vietnamese and related financial-market data retrieval, normalization, and analysis. It exposes beginner-friendly public APIs while routing work to source-specific providers for quotes, listings, company data, financials, trading data, funds, and selected international market data.

## Module map

- `vnstock/__init__.py`
  Owns public exports, lazy bootstrap, and compatibility-friendly import surface.
  May depend on internal package modules.
  Should remain thin and avoid source-specific logic.

- `vnstock/common/client.py`
  Owns the high-level `Vnstock` entrypoint that groups stock, FX, crypto, world index, and fund access.
  May depend on shared data maps and public-facing component builders.
  Should not absorb provider-specific scraping logic.

- `vnstock/api/`
  Owns stable adapter classes such as `Quote`, `Listing`, `Company`, `Finance`, and `Trading`.
  May depend on `vnstock.base`, `vnstock.config`, `vnstock.core.types`, and provider discovery.
  Should stay as thin orchestration layers that validate inputs, normalize compatibility parameters, and delegate.

- `vnstock/base.py` and `vnstock/core/registry.py`
  Own provider discovery, adapter delegation, retries, and registration.
  May depend on shared config and type helpers.
  Must remain the only place where provider resolution semantics are centralized.

- `vnstock/core/`
  Owns shared internals: config, registry, models, types, settings, and reusable utilities such as env/auth/header helpers.
  May be imported broadly by higher-level layers.
  Should not take dependencies on source-specific provider modules unless explicitly designed as bootstrap utilities.

- `vnstock/explorer/`
  Owns provider implementations for KBS, VCI, MSN, FMARKET, and misc data sources.
  These modules are where remote request behavior, parsing, and source-specific quirks belong.
  Do not make `api/` or `common/client.py` duplicate this logic.

- `vnstock/connector/`
  Owns connector-style integrations such as FMP and DNSE.
  These are API/integration adapters rather than the generic public surface.
  Keep authentication and external contract handling close to each connector.

- `tests/`
  Owns automated validation. `tests/unit/` covers thin adapters and utilities, `tests/integration/` covers live workflows.
  `tests/docs/` is an important source of truth for how the test suite is organized.

- `.github/workflows/`
  Owns CI expectations around testing, coverage, code quality, performance, and security scanning.

## Architectural invariants

- Public usage should flow through `vnstock/__init__.py`, `vnstock.common.client.Vnstock`, or the adapter classes in `vnstock/api/`.
- Adapters in `vnstock/api/` should remain thin. Source-specific network logic belongs in `vnstock/explorer/` or `vnstock/connector/`.
- Provider registration must stay explicit through `ProviderRegistry`; do not hardcode cross-package dispatch in multiple places.
- Preserve lazy-loading patterns that avoid circular-import deadlocks unless you are deliberately redesigning bootstrap behavior.
- Keep retries and boundary normalization centralized rather than reimplementing them ad hoc in many providers.
- Backward-compatibility shims for method names or parameters are part of the public contract and should not be removed casually.

## Cross-cutting concerns

- Provider registration: `vnstock/core/registry.py`
- Adapter dispatch and retry wrappers: `vnstock/base.py`
- Public bootstrap and lazy module loading: `vnstock/__init__.py`
- Top-level user API: `vnstock/common/client.py`
- Environment and local config behavior: `vnstock/core/utils/env.py`
- Auth/API-key placeholder behavior: `vnstock/core/utils/auth.py`
- Browser-like headers and request identity: `vnstock/core/utils/user_agent.py`
- CI and quality policy: `.github/workflows/` and `.github/TESTING.md`

## Data and boundary rules

- External responses are untrusted until parsed and normalized inside providers.
- Symbol mapping and source-specific parameter semantics should stay close to the responsible provider or shared constant layer.
- Avoid leaking raw remote-service quirks directly into the public API unless there is a compatibility reason.
- Financial data returned by the library is convenience data, not an authoritative trading system record.

## Known pressure points

- Provider registration and lazy import order are easy to break.
- Public adapter signatures must stay compatible with existing user code.
- Scraping/browser-like providers are sensitive to upstream HTML, headers, anti-bot behavior, and rate limits.
- Proxy and request-header utilities can change reliability and risk posture quickly.
- CI docs and test docs already contain operational knowledge; drifting away from them causes confusion.

## Related docs

- `README.md`
- `PRODUCT_SENSE.md`
- `QUALITY_GATES.md`
- `SECURITY.md`
- `docs/INDEX.md`
- `tests/docs/INDEX.md`
- `.github/TESTING.md`
