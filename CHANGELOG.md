# Changelog

All notable changes to the Ferrum contracts are recorded here. Releases are
tags named `contracts-edge-X.Y.Z` pinned to Ferrum Edge releases; see
[docs/versioning.md](docs/versioning.md).

## [Unreleased]

### Added

- `service-manifest` v1: optional `[agents]` configuration from Alloy PR #113
  (#8, closes #7).

### Changed

- Sync README, versioning, adoption, and release-process docs with the
  published contracts tags and current consumer pins.

## [contracts-edge-0.9.9] - 2026-10-01

Refreshes the Edge-owned vocabularies from Ferrum Edge v0.9.9, commit
`234717ce41965cd1e2b5c6c761a25475c5d7628c`.

### Changed

- `ci/validate.py` hardening from the seed review (#2): it now collects every
  `format` the schemas use and fails if a JSON Schema 2020-12 standard format
  has no registered checker, rejects duplicate cardinality surface names
  instead of letting the last one win, and can pin the top-level `oneOf` /
  `anyOf` keyword for an invalid fixture with an optional `top_keyword` in
  `fixtures/invalid-expectations.json`.
- Gateway headers: `X-Ferrum-Diagnostic-Ref` (#5845) and
  `X-Ferrum-Diagnostic-Owner-Replica` (#5868) move from unreleased to
  released in v0.9.9. The `x-consumer-*` reserved namespace also documents
  case-insensitive matching and `_`/`-` equivalence (#5880).
- `diagnostic-ref` v1: the released contract includes the fd2 reference form
  and replica identifier in Edge v0.9.9; valid and invalid fixtures cover the
  released form and its replica-id pattern.
- Plugin catalog: refreshes the `openapi.yaml` pin and `mcp_gateway` lifecycle
  phases; final-backend-header policy and final-request-body phases came from
  Edge #5905, and response-body normalization came from #5930. Built-in
  registrations and removed-plugin names are unchanged.
- Gateway error classes, tokens, and provisioning attribution have no value
  changes from v0.9.8; their source provenance now points to v0.9.9.

### Added

- Gateway-header vocabulary records `x-ferrum-mcp` as an OpenAPI extension
  field, not an HTTP header, from Edge #5930 (`docs/api_specs.md`).
- Plugin catalog adds the optional `websocket_framing_plugins` schema property
  and the released capability list (`waf`, `ws_frame_logging`,
  `ws_message_size_limiting`, `ws_rate_limiting`) from
  `BUILTIN_WEBSOCKET_FRAMING_PLUGINS` for `websocket_permessage_deflate`
  passthrough admission (#5853, #5869).

## [contracts-edge-0.9.8] - 2026-09-30

Initial delivery of the work tracked by ferrum-edge/.github#4, published as
`contracts-edge-0.9.8`.

### Added

- Gateway error vocabulary (`vocabularies/gateway-errors.json`): the 19
  `ErrorClass` values with their pre-wire flag, log kind and default
  `X-Gateway-Error` token, and the eight `X-Gateway-Error` tokens with their
  statuses, rejection phases and meaning. From Ferrum Edge v0.9.8
  (`src/retry.rs`, `docs/error_classification.md`). Unchanged on Edge `main`.
- Gateway-owned headers (`vocabularies/gateway-headers.json`): the
  `x-consumer-*`, `x-ferrum-*` and `x-path-param-*` namespaces, the reserved
  gateway assertions, `X-Gateway-Error` and `X-Gateway-Upstream-Status`,
  internal markers, mesh control headers, and the admin API `X-Ferrum-*`
  headers, from Edge v0.9.8. `X-Ferrum-Diagnostic-Ref` and
  `X-Ferrum-Diagnostic-Owner-Replica` are listed as unreleased (Edge `main`).
- `provisioned-by` attribution (`vocabularies/provisioned-by.json`): the label,
  the `X-Ferrum-Provisioned-By` header rules, and the values
  `ferrum-edge-git-forge-ops`, `ferrum-nexus` and `ferrum-foundry`.
- Plugin catalog index (`vocabularies/plugin-catalog.json`): all 82 built-in
  plugins of Edge v0.9.8 with failure policy, classification, priority,
  documented phases and protocols, response-body production, and a pointer to
  each plugin's config schema in Edge's `openapi.yaml` (pinned by sha256), plus
  the two removed plugin names.
- Schemas: `diagnostic-ref` v1 (`ferrum.diagnostic_ref.v1`, Edge `main`,
  unreleased), `diagnostic-finding` v1 (Anvil `DiagnosticFinding`),
  `diagnostic-report` v1 (Alloy `ferrum.diagnostic_report`),
  `service-manifest` v1 (Alloy, **proposed**), `gitforgeops-resource` v1
  (GitForgeOps resource file envelope), and one shape schema per vocabulary.
- Conformance fixtures for every schema and vocabulary, taken from the owners'
  fixtures and examples where they exist (`fixtures/README.md`).
- `Validate contracts` workflow and `ci/validate.py`, with hash-pinned
  validator dependencies (including `rfc3339-validator`, so `date-time` is
  asserted). CI also checks that each invalid fixture fails with its
  recorded instance path and keyword (`fixtures/invalid-expectations.json`),
  that values copied from vocabularies into schemas match, and that each
  plugin's config schema pointer is the one Edge's `PluginConfigBase`
  references for that plugin name.
- Dependabot for GitHub Actions and `ci/requirements.txt`; `.github/CODEOWNERS`.
- Docs: ownership, versioning, adoption status per consumer (including the
  ferrum-alloy#27 checklist), and the release process.
