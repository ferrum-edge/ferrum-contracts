# Changelog

All notable changes to the Ferrum contracts are recorded here. Releases are
tags named `contracts-edge-X.Y.Z` pinned to Ferrum Edge releases; see
[docs/versioning.md](docs/versioning.md).

## [Unreleased]

## [contracts-edge-0.9.8] - 2026-09-30

First delivery of ferrum-edge/.github#4. Targets the first tag,
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
