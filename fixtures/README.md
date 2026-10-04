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
entry, so a fixture cannot pass by failing for an unrelated reason. An entry
may also carry `top_keyword`, which CI checks against the top-level error,
pinning a `oneOf` / `anyOf` failure to that keyword rather than to a single
branch of it.

## Provenance

| Fixture set | Source | Commit |
|---|---|---|
| `diagnostic-ref/valid/*` | ferrum-edge `openapi.yaml`, `GET /diagnostics/v1/refs/{ref}` `200` examples `connection_failure`, `tls_retry`, `plugin_rejection`; the fd2 reference form and replica id are documented in `docs/error_classification.md` | `234717ce41965cd1e2b5c6c761a25475c5d7628c` (v0.9.9) |
| `diagnostic-report/valid/*`, `diagnostic-report/invalid/unsupported-major.json` | ferrum-alloy `contracts/fixtures/reports/*.json`, copied byte for byte | `fa471ccb79a444aee04661880af2385596d9da45` |
| `diagnostic-finding/valid/ferrum-token-connection-failure.json` | Built from ferrum-anvil's `ferrum.token.connection_failure` rule output: rule `ferrum.marker` v1 (`crates/anvil-diagnostics/src/rules/ferrum_rules.rs`, `lib.rs` `Draft::new`) with the wording of `catalog/diagnostics/findings.en.json` | `c401a320dcc5d52f707a5d5c27e333587b7a5d86` |
| `diagnostic-finding/valid/ferrum-token-backend-error.json` | Built from the same rule for `backend_error` (scope and owner `unknown`, confidence `likely`, as asserted by the `ferrum_rules.rs` tests). Anvil keeps no JSON finding fixtures. | `c401a320dcc5d52f707a5d5c27e333587b7a5d86` |
| `service-manifest/valid/orders-api.json`, `plain-http.json` | ferrum-alloy `contracts/fixtures/manifests/orders-api.toml`, `plain-http.toml`, transcribed | `fa471ccb79a444aee04661880af2385596d9da45` |
| `service-manifest/valid/agents-enabled.json` | ferrum-alloy `contracts/fixtures/openapi/orders-api.toml`, transcribed | `4cba0f4a66f85bcee3140e3b92e299275a2507fb` |
| `gitforgeops-resource/valid/quickstart-*.json` | ferrum-edge-git-forge-ops `tests/fixtures/quickstart/resources/ferrum/{proxies,plugins,consumers,upstreams}/*.yaml`, transcribed | `36206d8de8929884f62c65a040f3a08d35bd5863` |
| `gitforgeops-resource/valid/mesh-minimal.json` | ferrum-edge-git-forge-ops `tests/fixtures/mesh-minimal/ferrum/mesh/minimal.yaml`, transcribed | `36206d8de8929884f62c65a040f3a08d35bd5863` |
| `vocabulary-*/valid/*` | Subsets of the vocabulary files in `vocabularies/` | this repository |
| `admin-conditional-snapshot/valid/metadata.json` | ferrum-edge `docs/admin_backup_restore.md`, "Conditional snapshots and restore" JSON example, transcribed. Illustrative opaque tokens are not credential-derived MACs. | `c764084b3b51c3f7ffde268c039688d35e49c553` (tagged v0.9.11; publication verification pending) |
| `admin-conditional-snapshot/valid/empty-maps.json` | Same metadata with empty resource maps, as emitted by `src/admin/conditional_snapshots.rs` `row_tags`/`serialize_snapshot` for an empty snapshot; token remains illustrative. | `c764084b3b51c3f7ffde268c039688d35e49c553` |
| `backend-egress-policy/valid/default-control-plane.json` | ferrum-edge `openapi.yaml`, `/backend-egress-policy` `defaultControlPlane` example, transcribed field for field | `c764084b3b51c3f7ffde268c039688d35e49c553` |
| `backend-egress-policy/valid/public-serving.json` | ferrum-edge `tests/integration/admin_backend_egress_policy_tests.rs` `serving_modes_report_the_proxy_policy_and_selected_namespace_scope`, field values completed from `src/admin/backend_egress_policy.rs` `handle_get` with `BackendAllowIps::Public`, no overlays and the production baseline | `c764084b3b51c3f7ffde268c039688d35e49c553` |
| `backend-egress-policy/valid/public-with-allow-overrides.json`, `private-control-plane.json` | ferrum-edge `src/admin/backend_egress_policy.rs` `handle_get` and `src/config/env_config.rs` `BackendEgressPolicy::metadata`; sanitized transcriptions of public-with-allow-overlay and private-mode branches. No operator CIDRs, JWTs or credentials. | `c764084b3b51c3f7ffde268c039688d35e49c553` |
| `vocabulary-backend-egress-policy/valid/v1.json`, `vocabulary-gateway-headers/valid/admin-standard-conditional.json` | Full egress vocabulary and admin-header subset of the candidate vocabulary files; owner paths/full provenance recorded in each fixture | `c764084b3b51c3f7ffde268c039688d35e49c553` |

New admin fixtures are draft canonical artifacts from the actual tagged owner
source, not evidence of upstream publication or consumer adoption. Their schemas
check JSON conformance only: token authenticity, authorization, authoritative
state/coherence, audit admission and serving-DP policy are runtime requirements.
Existing Alloy fixtures are unchanged and retain their historical source
provenance; the candidate re-reads schema/manifest source at qualified Alloy
`d7ddb3688e058ec3cc2e17d166a801aa0037b5b1` without altering fixture semantics.

## Invalid fixtures

| Fixture | Why it must fail |
|---|---|
| `admin-conditional-snapshot/invalid/missing-consumer-map.json` | From `valid/metadata.json`: remove only required `row_etags.consumers` |
| `admin-conditional-snapshot/invalid/weak-namespace-tag.json` | From `valid/metadata.json`: change only the namespace token to a weak `W/` tag |
| `admin-conditional-snapshot/invalid/token-with-line-break.json` | From `valid/metadata.json`: append only a line break to the namespace token; quoted entity-tag syntax has no trailing control bytes |
| `admin-conditional-snapshot/invalid/unquoted-row-tag.json` | From `valid/metadata.json`: remove only the quotes from the proxy row token |
| `admin-conditional-snapshot/invalid/unknown-row-map.json` | From `valid/metadata.json`: add only the unsupported `row_etags.api_specs` map; namespace coverage of API specs does not add a row map |
| `backend-egress-policy/invalid/unknown-version.json` | From `valid/default-control-plane.json`: change only `schema_version` to `2` |
| `backend-egress-policy/invalid/unknown-classification.json` | From `valid/default-control-plane.json`: change only `ip_classification` to `unknown` |
| `backend-egress-policy/invalid/unknown-enforcement-scope.json` | From `valid/default-control-plane.json`: change only `enforcement_scope` to `unknown` |
| `backend-egress-policy/invalid/unknown-mode.json` | From `valid/default-control-plane.json`: change only `mode` to `unknown` |
| `backend-egress-policy/invalid/wrong-evaluation-stage.json` | From `valid/default-control-plane.json`: change only evaluation index 0 from `allow-cidrs` to `ip-mode` |
| `backend-egress-policy/invalid/mode-class-mismatch.json` | From `valid/public-serving.json`: change only the allowed mode list to `["private-reserved"]` |
| `backend-egress-policy/invalid/false-public-guarantee.json` | From `valid/public-serving.json`: change only the guarantee to false; the owner emits true for public mode without allow overlays |
| `backend-egress-policy/invalid/allow-overlay-guarantee.json` | From `valid/public-with-allow-overrides.json`: change only the guarantee to true; undisclosed allow overlays prevent certification |
| `backend-egress-policy/invalid/leaked-cidr-field.json` | From `valid/default-control-plane.json`: add only `allow_cidrs`; the closed response withholds raw CIDRs |
| `vocabulary-backend-egress-policy/invalid/unknown-mode.json` | From `valid/v1.json`: change only modes index 0 to `unknown` |
| `vocabulary-backend-egress-policy/invalid/short-commit.json` | From `valid/v1.json`: shorten only provenance index 0's full commit SHA |
| `diagnostic-ref/invalid/unknown-schema-version.json` | `schema_version` is `ferrum.diagnostic_ref.v2` |
| `diagnostic-ref/invalid/malformed-ref.json` | `ref` is not `fd1_` plus 32 lowercase hex digits |
| `diagnostic-ref/invalid/granular-class-as-token.json` | `gateway_error` is an `ErrorClass` (`dns_lookup_error`), not an `X-Gateway-Error` token |
| `diagnostic-ref/invalid/detail-missing-backend-dispatch.json` | `detail.backend_dispatch` is required |
| `diagnostic-ref/invalid/created-at-not-rfc3339.json` | `created_at` is not an RFC 3339 `date-time` (format assertion) |
| `diagnostic-ref/invalid/uppercase-replica-id.json` | `replica_id` is uppercase instead of eight lowercase hexadecimal digits |
| `diagnostic-report/invalid/unsupported-major.json` | `schema_version` `2.0`; readers reject other majors (Alloy's own fixture) |
| `diagnostic-report/invalid/missing-collection.json` | `collection` is required |
| `diagnostic-report/invalid/uppercase-span-id.json` | `span_id` must be 16 lowercase hex digits |
| `diagnostic-report/invalid/finding-missing-owner.json` | a finding without `owner` |
| `diagnostic-finding/invalid/probability-confidence.json` | `confidence` is a percentage; Anvil never invents probabilities |
| `diagnostic-finding/invalid/missing-does-not-prove.json` | `does_not_prove` is required |
| `diagnostic-finding/invalid/alloy-only-evidence-source.json` | `gateway_telemetry` is an Alloy evidence source that Anvil's `DiagnosticFinding` does not accept |
| `service-manifest/invalid/unsupported-major.json` | `schema_version` `2.0` |
| `service-manifest/invalid/agents-unknown-key.json` | adds unknown `agents.read_only`; Alloy's agents object denies unknown fields |
| `service-manifest/invalid/agents-bad-namespace.json` | `agents.namespace` contains a space, outside the 1-64 character `A-Za-z0-9_-` rule |
| `service-manifest/invalid/agents-enabled-not-boolean.json` | `agents.enabled` is a string instead of a boolean |
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
| `vocabulary-plugin-catalog/invalid/unknown-websocket-framing-plugin.json` | `websocket_framing_plugins` contains a name not declared by Edge |
| `vocabulary-plugin-catalog/invalid/unknown-failure-policy.json` | failure policy `fail_open` |
| `vocabulary-plugin-catalog/invalid/bad-schema-pointer.json` | a config schema pointer that is not a component name |
