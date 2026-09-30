# Conformance fixtures

`fixtures/<name>/valid/*.json` are payloads each producer must be able to emit
and each consumer must accept. `fixtures/<name>/invalid/*.json` must be
rejected. CI (`ci/validate.py`) checks both against the latest major of
`schemas/<name>/`, and also checks every valid `diagnostic-finding` fixture
against `diagnostic-report#/$defs/Finding`.

Fixtures are taken from the owners' existing fixtures or examples where they
exist. Where an owner keeps its fixtures in another format (TOML, YAML), the
JSON here is a field-for-field transcription with comments removed. Invalid
fixtures are a valid fixture with one change, listed below.

`valid/` and `invalid/` hold only `*.json` fixtures; CI fails on any other
file. Every invalid fixture has an entry in
[`invalid-expectations.json`](invalid-expectations.json) with the JSON
Pointer (`instance_path`, `""` for the root) and the JSON Schema `keyword`
of the error it must produce. CI requires exactly one top-level error and
that it, or an error nested under it (for `oneOf` / `anyOf`), matches the
entry, so a fixture cannot pass by failing for an unrelated reason.

## Provenance

| Fixture set | Source | Commit |
|---|---|---|
| `diagnostic-ref/valid/*` | ferrum-edge `openapi.yaml`, `GET /diagnostics/v1/refs/{ref}` `200` examples `connection_failure`, `tls_retry`, `plugin_rejection` | `f638465034734e335bde7e76c56e8c8244afba8a` (main) |
| `diagnostic-report/valid/*`, `diagnostic-report/invalid/unsupported-major.json` | ferrum-alloy `contracts/fixtures/reports/*.json`, copied byte for byte | `fa471ccb79a444aee04661880af2385596d9da45` |
| `diagnostic-finding/valid/ferrum-token-connection-failure.json` | Built from ferrum-anvil's `ferrum.token.connection_failure` rule output: rule `ferrum.marker` v1 (`crates/anvil-diagnostics/src/rules/ferrum_rules.rs`, `lib.rs` `Draft::new`) with the wording of `catalog/diagnostics/findings.en.json` | `c401a320dcc5d52f707a5d5c27e333587b7a5d86` |
| `diagnostic-finding/valid/ferrum-token-backend-error.json` | Built from the same rule for `backend_error` (scope and owner `unknown`, confidence `likely`, as asserted by the `ferrum_rules.rs` tests). Anvil keeps no JSON finding fixtures. | `c401a320dcc5d52f707a5d5c27e333587b7a5d86` |
| `service-manifest/valid/orders-api.json`, `plain-http.json` | ferrum-alloy `contracts/fixtures/manifests/orders-api.toml`, `plain-http.toml`, transcribed | `fa471ccb79a444aee04661880af2385596d9da45` |
| `gitforgeops-resource/valid/quickstart-*.json` | ferrum-edge-git-forge-ops `tests/fixtures/quickstart/resources/ferrum/{proxies,plugins,consumers,upstreams}/*.yaml`, transcribed | `36206d8de8929884f62c65a040f3a08d35bd5863` |
| `gitforgeops-resource/valid/mesh-minimal.json` | ferrum-edge-git-forge-ops `tests/fixtures/mesh-minimal/ferrum/mesh/minimal.yaml`, transcribed | `36206d8de8929884f62c65a040f3a08d35bd5863` |
| `vocabulary-*/valid/*` | Subsets of the vocabulary files in `vocabularies/` | this repository |

## Invalid fixtures

| Fixture | Why it must fail |
|---|---|
| `diagnostic-ref/invalid/unknown-schema-version.json` | `schema_version` is `ferrum.diagnostic_ref.v2` |
| `diagnostic-ref/invalid/malformed-ref.json` | `ref` is not `fd1_` plus 32 lowercase hex digits |
| `diagnostic-ref/invalid/granular-class-as-token.json` | `gateway_error` is an `ErrorClass` (`dns_lookup_error`), not an `X-Gateway-Error` token |
| `diagnostic-ref/invalid/detail-missing-backend-dispatch.json` | `detail.backend_dispatch` is required |
| `diagnostic-ref/invalid/created-at-not-rfc3339.json` | `created_at` is not an RFC 3339 `date-time` (format assertion) |
| `diagnostic-report/invalid/unsupported-major.json` | `schema_version` `2.0`; readers reject other majors (Alloy's own fixture) |
| `diagnostic-report/invalid/missing-collection.json` | `collection` is required |
| `diagnostic-report/invalid/uppercase-span-id.json` | `span_id` must be 16 lowercase hex digits |
| `diagnostic-report/invalid/finding-missing-owner.json` | a finding without `owner` |
| `diagnostic-finding/invalid/probability-confidence.json` | `confidence` is a percentage; Anvil never invents probabilities |
| `diagnostic-finding/invalid/missing-does-not-prove.json` | `does_not_prove` is required |
| `diagnostic-finding/invalid/alloy-only-evidence-source.json` | `gateway_telemetry` is an Alloy evidence source that Anvil's `DiagnosticFinding` does not accept |
| `service-manifest/invalid/unsupported-major.json` | `schema_version` `2.0` |
| `service-manifest/invalid/unknown-field.json` | unknown `upstream.backend_scheme` (the manifest uses `deny_unknown_fields`) |
| `service-manifest/invalid/base-path-without-trailing-slash.json` | `api.service_base_path` must end in `/` |
| `service-manifest/invalid/tls-path-with-http-scheme.json` | `server_ca_path` with `scheme = "http"` |
| `service-manifest/invalid/client-cert-without-key.json` | client certificate without its key |
| `service-manifest/invalid/http3-protocol.json` | `http3` is not a supported service protocol |
| `gitforgeops-resource/invalid/unknown-kind.json` | `kind` `Service` does not exist |
| `gitforgeops-resource/invalid/lowercase-kind.json` | `kind` is case-sensitive (`proxy`) |
| `gitforgeops-resource/invalid/missing-spec.json` | `spec` is required |
| `gitforgeops-resource/invalid/plugin-config-unknown-scope.json` | `scope` `tenant` is not `global`, `proxy` or `proxy_group` |
| `gitforgeops-resource/invalid/consumer-missing-username.json` | `Consumer.spec.username` is required |
| `vocabulary-gateway-errors/invalid/token-without-meaning.json` | a token without `meaning` |
| `vocabulary-gateway-errors/invalid/class-not-snake-case.json` | an error class spelled as its Rust variant |
| `vocabulary-gateway-errors/invalid/wrong-version.json` | `version` `2` against the v1 shape |
| `vocabulary-gateway-headers/invalid/prefix-without-trailing-dash.json` | a prefix entry whose name does not end in `-` |
| `vocabulary-gateway-headers/invalid/unknown-role.json` | `role` outside the closed set |
| `vocabulary-gateway-headers/invalid/short-commit.json` | a provenance commit that is not a full SHA |
| `vocabulary-provisioned-by/invalid/untrimmed-value.json` | a value with leading whitespace; Edge trims the header |
| `vocabulary-provisioned-by/invalid/wrong-label-key.json` | label key `provisioned_by` |
| `vocabulary-plugin-catalog/invalid/unknown-protocol.json` | protocol `http2`; the catalog uses Edge's five protocol families |
| `vocabulary-plugin-catalog/invalid/unknown-failure-policy.json` | failure policy `fail_open` |
| `vocabulary-plugin-catalog/invalid/bad-schema-pointer.json` | a config schema pointer that is not a component name |
