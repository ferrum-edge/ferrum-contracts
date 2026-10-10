# Conformance fixtures

`fixtures/<name>/valid/*.json` are payloads each producer must be able to emit
and each consumer must accept. `fixtures/<name>/invalid/*.json` must be
rejected. CI (`ci/validate.py`) checks both against `schemas/<name>/`, and also
checks every valid `diagnostic-finding` fixture against
`diagnostic-report#/$defs/Finding`. A schema with several majors keeps each
major's fixtures in `fixtures/<name>/v<N>/valid/` and
`fixtures/<name>/v<N>/invalid/`, checked against `v<N>.schema.json`
(`backend-egress-policy`, `vocabulary-backend-egress-policy` and
`admin-deployment-snapshot` since contracts-edge-0.9.13).

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
| `admin-conditional-snapshot/valid/metadata.json` | ferrum-edge `docs/admin_backup_restore.md`, "Conditional snapshots and restore" JSON example, transcribed. Illustrative opaque tokens are not credential-derived MACs. | `c764084b3b51c3f7ffde268c039688d35e49c553` (published v0.9.11; upstream distribution verified) |
| `admin-conditional-snapshot/valid/empty-maps.json` | Same metadata with empty resource maps, as emitted by `src/admin/conditional_snapshots.rs` `row_tags`/`serialize_snapshot` for an empty snapshot; token remains illustrative. | `c764084b3b51c3f7ffde268c039688d35e49c553` |
| `backend-egress-policy/v1/valid/default-control-plane.json` | ferrum-edge `openapi.yaml`, `/backend-egress-policy` `defaultControlPlane` example, transcribed field for field | `c764084b3b51c3f7ffde268c039688d35e49c553` |
| `backend-egress-policy/v1/valid/public-serving.json` | ferrum-edge `tests/integration/admin_backend_egress_policy_tests.rs` `serving_modes_report_the_proxy_policy_and_selected_namespace_scope`, field values completed from `src/admin/backend_egress_policy.rs` `handle_get` with `BackendAllowIps::Public`, no overlays and the production baseline | `c764084b3b51c3f7ffde268c039688d35e49c553` |
| `backend-egress-policy/v1/valid/public-with-allow-overrides.json`, `private-control-plane.json` | ferrum-edge `src/admin/backend_egress_policy.rs` `handle_get` and `src/config/env_config.rs` `BackendEgressPolicy::metadata`; sanitized transcriptions of public-with-allow-overlay and private-mode branches. No operator CIDRs, JWTs or credentials. | `c764084b3b51c3f7ffde268c039688d35e49c553` |
| `vocabulary-backend-egress-policy/v1/valid/v1.json`, `vocabulary-gateway-headers/valid/admin-standard-conditional.json` | Initial-candidate egress vocabulary snapshot and admin-header subset; owner paths/full provenance recorded in each fixture | `c764084b3b51c3f7ffde268c039688d35e49c553` |
| `admin-deployment-snapshot/v1/valid/empty-sql.json` | ferrum-edge/ferrum-edge `src/admin/deployment_mutations.rs` `snapshot`, `src/config/deployment_mutation.rs` `DeploymentSnapshot::representation`, `src/config/db_backend.rs` `ConditionalNamespaceSnapshot::representation`, and `src/config/db_loader.rs` `deployment_snapshot_tx`: transcribed complete empty SQL namespace, no registry record and zero watermark. The namespace fixes the owner integration test's `deployment-{UUID}` form to an illustrative all-zero UUID, avoiding the seeded `ferrum` registry row. Token is the illustrative all-zero form used in `tests/integration/admin_conditional_write_tests.rs`, not a captured MAC. | `0d917701b63ef38210c49df830f48cf0457cbc7d` (actual released v0.9.12) |
| `admin-deployment-snapshot/v1/valid/empty-mongodb.json` | Same owner snapshot/representation sources, with `src/config/mongo_store.rs` `deployment_snapshot_in_session`'s exact empty collection set instead of SQL tables. MongoDB embeds associations and credential uniqueness metadata; no separate SQL junction/credential-index collections are fabricated. | `0d917701b63ef38210c49df830f48cf0457cbc7d` |
| `admin-deployment-mutation-acknowledgement/valid/applied.json`, `durable-only.json` | ferrum-edge/ferrum-edge `src/admin/deployment_mutations.rs` `finish` success branches, transcribed. IDs `live`/`deployment` come from `tests/integration/admin_conditional_write_tests.rs` `assert_deployment_cancellation_and_live_ack` / `assert_deployment_mutation_contract`; those tests assert local applied versus CP durable-only cleanup authorization. | `0d917701b63ef38210c49df830f48cf0457cbc7d` |
| `admin-deployment-mutation-acknowledgement/valid/stale.json` | ferrum-edge/ferrum-edge `src/admin/deployment_mutations.rs` `store_error` precondition branch, transcribed with its exact error text and no success profile/target. | `0d917701b63ef38210c49df830f48cf0457cbc7d` |
| `backend-egress-policy/v2/valid/default-control-plane.json` | ferrum-edge `openapi.yaml`, `/backend-egress-policy` `defaultControlPlane` example (`schema_version: 2`), transcribed field for field | `9b83115de7ec23ab51ec4feae6bed65e596db425` (v0.9.13) |
| `backend-egress-policy/v2/valid/public-serving.json`, `public-control-plane.json`, `public-no-data-plane.json`, `public-unserved-namespace.json` | ferrum-edge `tests/integration/admin_backend_egress_policy_tests.rs` `public_only_is_never_guaranteed_without_local_enforcement` (CP `admission-only`, node agent `no-data-plane`, `unserved-namespace` for `other`, `local-data-plane` for `staging`), field values completed from `src/admin/backend_egress_policy.rs` `handle_get` with `BackendAllowIps::Public`, no overlays and the production baseline | `9b83115de7ec23ab51ec4feae6bed65e596db425` |
| `backend-egress-policy/v2/valid/public-with-allow-overrides.json`, `private-control-plane.json` | The v1 fixtures with `schema_version: 2`; `handle_get` gives both `public_only_guaranteed: false` in v2 as in v1 | `9b83115de7ec23ab51ec4feae6bed65e596db425` |
| `vocabulary-backend-egress-policy/v2/valid/v2.json` | `vocabularies/backend-egress-policy.json` at this release, copied | this repository |
| `admin-deployment-snapshot/v2/valid/empty-sql.json`, `empty-mongodb.json` | The v1 empty-state fixtures with `api_spec_contents: []`, as `src/admin/deployment_mutations.rs` `snapshot` emits for a namespace without specs; the empty `evidence` shape is unchanged in `src/config/deployment_mutation.rs` and `src/config/db_backend.rs`. Tokens stay illustrative. | `9b83115de7ec23ab51ec4feae6bed65e596db425` |
| `admin-deployment-snapshot/v2/valid/one-spec-sql.json` | Synthetic. `v2/valid/empty-sql.json` with one API spec in `api_specs` and `evidence.resources[5]`, shaped by `openapi.yaml` `DeploymentSnapshot`/`StoredContentDigest` and `src/config/db_backend.rs` `ApiSpecSnapshotView` (every field, `None` as `null`, `external_ref_snapshot: null`), and the matching `api_spec_contents` item from `src/admin/deployment_mutations.rs` `api_spec_content`. The spec document is the 75-byte `{"openapi":"3.1.0","info":{"title":"Fixture","version":"1.0.0"},"paths":{}}` written for the fixture; `content_hash` and `uncompressed_size` are its SHA-256 and length, and `spec_content` is the SHA-256 and length of the 88-byte gzip stream that `spec_content_base64` encodes. `resource_hash` is all zeros and the token is illustrative. The proxy the spec names and the raw `evidence.stored` rows are omitted: JSON conformance does not check evidence completeness. | `9b83115de7ec23ab51ec4feae6bed65e596db425` |
| `admin-deployment-mutation-acknowledgement/valid/snapshot-too-large-not-started.json`, `snapshot-too-large-not-committed.json` | ferrum-edge `src/admin/deployment_mutations.rs` `snapshot_too_large`, with the exact `SNAPSHOT_CONTENT_TOO_LARGE` message and `not_started` from `snapshot`, and the `NamespaceSnapshotTooLarge` message (`src/config/db_backend.rs`) with `not_committed` from `store_error` | `9b83115de7ec23ab51ec4feae6bed65e596db425` |
| `admin-deployment-mutation-acknowledgement/valid/not-started.json`, `unknown.json`, `committed-unconfirmed.json` | ferrum-edge/ferrum-edge `src/admin/deployment_mutations.rs` `unavailable`, with the exact `not_started`, `unknown` and `committed` arguments used by snapshot/admission, uncertain task/store and post-commit completion failure branches; literal source-body transcriptions. | `0d917701b63ef38210c49df830f48cf0457cbc7d` |
| `backend-egress-policy/v2/valid/control-plane-attestation-empty.json`, `control-plane-attestation-reported.json` | ferrum-edge `openapi.yaml`, `/backend-egress-policy` `defaultControlPlane` and `controlPlaneAttestingPublicOnlyDataPlanes` examples (CP with no connected data plane, and two reporting public-only data planes), transcribed field for field | `9bd4d5f9caa4ebe8f0ea13e76d8a6e2172eaca7d` (v0.9.14) |
| `backend-egress-policy/v2/valid/control-plane-attestation-unknown.json`, `control-plane-attestation-allow-overlay.json`, `control-plane-attestation-shared-node-id.json` | ferrum-edge `tests/integration/admin_backend_egress_policy_tests.rs` `control_plane_attests_connected_data_planes_of_the_selected_namespace` (the unknown `dp-old` step and the `dp-c` allow-overlay step) and `every_stream_of_one_node_id_is_counted_and_weakens_the_aggregate`, with each policy view and aggregate completed from `src/grpc/backend_egress_attestation.rs` (`ReportedEgressPolicy` serialization, `weaken`, `DataPlaneEgressSummary::from_reports`). The CP top-level fields are the `defaultControlPlane` example's; `connected_at` values are illustrative RFC 3339 times in the owner's `to_rfc3339` form. No CIDRs or credentials. | `9bd4d5f9caa4ebe8f0ea13e76d8a6e2172eaca7d` (v0.9.14) |
| `vocabulary-backend-egress-policy/v2/valid/data-plane-attestation.json` | `vocabularies/backend-egress-policy.json` at this release, copied | this repository |
| `admin-deployment-mutation-acknowledgement/valid/store-failure-not-committed.json` | ferrum-edge `src/admin/deployment_mutations.rs` `store_error`, which from v0.9.14 calls `unavailable("not_committed")` for a store failure inside the rolled-back mutation transaction; literal source-body transcription | `9bd4d5f9caa4ebe8f0ea13e76d8a6e2172eaca7d` (v0.9.14) |
| `diagnostic-ref/valid/route-protocol-admission.json` | The `plugin_rejection` example of ferrum-edge `openapi.yaml` (`GET /diagnostics/v1/refs/{ref}` `200`) with only `protocol` `http1`, `status` `403`, `detail.backend_target` and `detail.rejection` changed. `src/proxy/mod.rs` logs the refusal through `log_pre_backend_rejected_request`, which omits `backend_target` (null), and the rejection is the gateway rejection that `src/diagnostic_ref.rs` `DiagnosticRejection::new` records for `ROUTE_PROTOCOL_ADMISSION_PHASE` (no plugin hook phase and no rejecting plugin, so `source: gateway` and no `plugin`). `detail.rejection_phase` stays null because `src/retry.rs` `token_for_rejection_phase` maps the phase to no token. The fixture is the WebSocket upgrade refusal, a `403` on HTTP/1.1, which only an `all`-mode reference records. Reference, times and proxy are the example's illustrative values. | `25b37395ff61bfea0f3ffd189d9011c4984fa755` (v0.9.15) |
| `vocabulary-gateway-headers/valid/authenticated-identity.json` | `vocabularies/gateway-headers.json` at this release: its top-level members, the `src/proxy/headers.rs` provenance entry and the `X-Consumer-Username` and `X-Authenticated-Identity` entries, copied | this repository |
| `diagnostic-ref/valid/proxy-hop-limit.json`, `proxy-hops-invalid.json` | Owner `openapi.yaml` plugin-rejection example as already transcribed by the route-protocol fixture, with protocol/status/token and unrouted rejection detail changed to match `src/proxy/hop_limit.rs`, `src/proxy/mod.rs` `proxy_hop_limit_refusal_response` and its `record_admission_fence` call, `src/diagnostic_ref.rs` and `src/retry.rs`. All-mode references retain null token-mapped detail phase, null proxy/backend and not_dispatched; raw phases are proxy_hop_limit or proxy_hops_invalid. This fence emits no terminal transaction summary. Reference/times/duration are illustrative owner-example values, not captured traffic. | `669c574c1d1e88e84dccb26a8159939e6694644d` (v0.9.17) |
| `diagnostic-ref/valid/client-disconnect-upload.json` | Owner `openapi.yaml` plugin-rejection example with protocol/status/error class and rejection changed to the source's HTTP/1 upload refusal. `src/proxy/mod.rs` calls the client-disconnect helper with phase client_disconnect_upload_before_dispatch and include_backend_target=true; `src/diagnostic_ref.rs` maps its raw phase to no token. Illustrative matched proxy/backend coordinates and times remain from the owner example. | `669c574c1d1e88e84dccb26a8159939e6694644d` (v0.9.17) |
| `vocabulary-gateway-headers/valid/proxy-hops.json` | Current vocabulary's top-level metadata and X-Ferrum-Hops entry copied; owner provenance is carried inside the fixture. | this repository |

The existing backup/egress fixtures are canonical artifacts from published v0.9.11
owner source. Distribution evidence is recorded in the [release notes](../docs/releases/contracts-edge-0.9.11.md);
fixtures alone do not establish consumer adoption. Their schemas
check JSON conformance only: token authenticity, authorization, authoritative
state/coherence, audit admission and serving-DP policy are runtime requirements.
Existing Alloy fixtures are unchanged and retain their historical source
provenance; the candidate re-reads schema/manifest source at qualified Alloy
`81cbb410d34ff5fba1f3d54cfd2e7ebccaed397e` without altering fixture semantics.
All fixture bytes are retained. The egress vocabulary fixtures include the initial
candidate description from before upstream publication; that historical fixture
text is not current availability metadata. Current availability is recorded above
and in the release record.

The new deployment fixtures prepare canonical 0.9.12 artifacts from actual
released owner source. [The preparation record](../docs/releases/contracts-edge-0.9.12.md)
distinguishes verified Edge distribution from pending Contracts publication and
consumer adoption. Empty-state fixtures cover exact SQL versus MongoDB evidence
families; no populated secret-bearing HTTP golden or generated gzip bytes are
invented. Nested evidence is open in owner OpenAPI and requires runtime
completeness checks, including full raw/spec/external-reference retention.
Acknowledgement fixtures cover explicit success, CP durable-only, stale,
not-started, uncertain and committed-not-live results. Optional profile/target
on refusals remain optional; consumers must require expected success identity
and HTTP status in addition to the three required body fields. All pre-existing
fixtures retain their original bytes and provenance.

## Invalid fixtures

| Fixture | Why it must fail |
|---|---|
| `diagnostic-ref/invalid/proxy-hop-limit-as-detail-phase.json`, `proxy-hops-invalid-as-detail-phase.json`, `client-disconnect-upload-as-detail-phase.json` | From each same-named valid response, change only detail.rejection_phase from null to its raw label. The closed token-mapped enum rejects it at /detail/rejection_phase; the top-level failure is oneOf. |
| `vocabulary-gateway-headers/invalid/proxy-hops-availability-without-v.json` | From valid/proxy-hops.json, change only headers[0].availability from v0.9.17 to 0.9.17, failing its Edge-tag pattern. |
| `backend-egress-policy/v2/invalid/previous-version.json` | From `v2/valid/default-control-plane.json`: change only `schema_version` to `1`; Edge v0.9.13 never emits it |
| `backend-egress-policy/v2/invalid/unknown-version.json` | From `v2/valid/default-control-plane.json`: change only `schema_version` to `3` |
| `backend-egress-policy/v2/invalid/unknown-classification.json` | From `v2/valid/default-control-plane.json`: change only `ip_classification` to `unknown` |
| `backend-egress-policy/v2/invalid/unknown-enforcement-scope.json` | From `v2/valid/default-control-plane.json`: change only `enforcement_scope` to `unknown` |
| `backend-egress-policy/v2/invalid/unknown-mode.json` | From `v2/valid/default-control-plane.json`: change only `mode` to `unknown` |
| `backend-egress-policy/v2/invalid/wrong-evaluation-stage.json` | From `v2/valid/default-control-plane.json`: change only evaluation index 0 from `allow-cidrs` to `ip-mode` |
| `backend-egress-policy/v2/invalid/leaked-cidr-field.json` | From `v2/valid/default-control-plane.json`: add only `allow_cidrs`; the closed response withholds raw CIDRs |
| `backend-egress-policy/v2/invalid/mode-class-mismatch.json` | From `v2/valid/public-serving.json`: change only the allowed mode list to `["private-reserved"]` |
| `backend-egress-policy/v2/invalid/false-public-guarantee.json` | From `v2/valid/public-serving.json`: change only the guarantee to false; a local data plane in public mode without allow overlays reports true |
| `backend-egress-policy/v2/invalid/allow-overlay-guarantee.json` | From `v2/valid/public-with-allow-overrides.json`: change only the guarantee to true; undisclosed allow overlays prevent certification |
| `backend-egress-policy/v2/invalid/admission-only-guarantee.json` | From `v2/valid/public-control-plane.json`: change only the guarantee to true; v2 never guarantees CP admission metadata |
| `backend-egress-policy/v2/invalid/no-data-plane-guarantee.json` | From `v2/valid/public-no-data-plane.json`: change only the guarantee to true |
| `backend-egress-policy/v2/invalid/unserved-namespace-guarantee.json` | From `v2/valid/public-unserved-namespace.json`: change only the guarantee to true |
| `vocabulary-backend-egress-policy/v2/invalid/previous-schema-version.json` | From `v2/valid/v2.json`: change only `schema_version` to `1` against the v2 shape |
| `vocabulary-backend-egress-policy/v2/invalid/unknown-mode.json` | From `v2/valid/v2.json`: change only modes index 0 to `unknown` |
| `backend-egress-policy/v2/invalid/attestation-on-local-data-plane.json` | From `v2/valid/public-serving.json`: add only the empty `data_plane_attestation` object; it is CP-only (`admission-only`) |
| `backend-egress-policy/v2/invalid/attestation-unknown-source.json` | From `v2/valid/control-plane-attestation-empty.json`: change only `source` to `configsync-heartbeat` |
| `backend-egress-policy/v2/invalid/attestation-leaked-cidr-field.json` | From `v2/valid/control-plane-attestation-reported.json`: add only `allow_cidrs` to the attestation object, which is closed (owner `unevaluatedProperties: false`) |
| `backend-egress-policy/v2/invalid/attestation-negative-count.json` | From `v2/valid/control-plane-attestation-empty.json`: change only `connected_data_planes` to `-1` |
| `backend-egress-policy/v2/invalid/attestation-missing-data-planes.json` | From `v2/valid/control-plane-attestation-empty.json`: remove only required `data_planes` |
| `backend-egress-policy/v2/invalid/weakest-policy-without-reports.json` | From `v2/valid/control-plane-attestation-empty.json`: change only `weakest_policy` to a public-only policy; it is null exactly when no data plane reported |
| `backend-egress-policy/v2/invalid/reports-without-weakest-policy.json` | From `v2/valid/control-plane-attestation-unknown.json`: change only `weakest_policy` to null although two data planes reported |
| `backend-egress-policy/v2/invalid/empty-set-complete.json` | From `v2/valid/control-plane-attestation-empty.json`: change only `weakest_policy_complete` to true; an empty set is never complete |
| `backend-egress-policy/v2/invalid/guarantee-with-unknown-data-plane.json` | From `v2/valid/control-plane-attestation-unknown.json`: change only `all_connected_public_only_guaranteed` to true; an unknown data plane makes the set incomplete |
| `backend-egress-policy/v2/invalid/guarantee-with-allow-overlay.json` | From `v2/valid/control-plane-attestation-allow-overlay.json`: change only `all_connected_public_only_guaranteed` to true; the weakest policy has allow overrides |
| `backend-egress-policy/v2/invalid/public-only-not-aggregated.json` | From `v2/valid/control-plane-attestation-reported.json`: change only `all_connected_public_only_guaranteed` to false; a complete public-only weakest policy makes it true |
| `backend-egress-policy/v2/invalid/weakest-policy-unknown-mode.json` | From `v2/valid/control-plane-attestation-shared-node-id.json`: change only `weakest_policy.mode` to `hybrid` |
| `backend-egress-policy/v2/invalid/entry-build-version.json` | From `v2/valid/control-plane-attestation-reported.json`: add only `ferrum_version` to `data_planes[0]`; namespace-scoped entries carry no build version |
| `backend-egress-policy/v2/invalid/entry-unknown-attestation.json` | From `v2/valid/control-plane-attestation-reported.json`: change only `data_planes[0].attestation` to `trusted` |
| `backend-egress-policy/v2/invalid/entry-reported-without-policy.json` | From `v2/valid/control-plane-attestation-reported.json`: change only `data_planes[1].policy` to null while `attestation` stays `reported` |
| `backend-egress-policy/v2/invalid/entry-unknown-with-policy.json` | From `v2/valid/control-plane-attestation-unknown.json`: change only `data_planes[2].policy` to a policy object while `attestation` stays `unknown` |
| `backend-egress-policy/v2/invalid/entry-connected-at-without-offset.json` | From `v2/valid/control-plane-attestation-reported.json`: drop only the UTC offset from `data_planes[0].connected_at`; RFC 3339 `date-time` requires it (format assertion) |
| `backend-egress-policy/v2/invalid/entry-policy-leaked-cidr-field.json` | From `v2/valid/control-plane-attestation-reported.json`: add only `allow_cidrs` to `data_planes[0].policy`; `DataPlaneEgressPolicy` is closed |
| `backend-egress-policy/v2/invalid/entry-policy-mode-class-mismatch.json` | From `v2/valid/control-plane-attestation-reported.json`: change only `data_planes[1].policy.mode_blocked_ip_classes` to `[]` for public mode |
| `backend-egress-policy/v2/invalid/entry-policy-false-public-guarantee.json` | From `v2/valid/control-plane-attestation-reported.json`: change only `data_planes[1].policy.public_only_guaranteed` to false; public mode without allow overrides reports true |
| `backend-egress-policy/v2/invalid/entry-policy-allow-overlay-guarantee.json` | From `v2/valid/control-plane-attestation-allow-overlay.json`: change only `data_planes[2].policy.public_only_guaranteed` to true; allow overrides prevent the guarantee |
| `vocabulary-backend-egress-policy/v2/invalid/unknown-attestation-status.json` | From `v2/valid/data-plane-attestation.json`: change only attestation status index 1 to `trusted` |
| `vocabulary-backend-egress-policy/v2/invalid/attestation-rule-missing.json` | From `v2/valid/data-plane-attestation.json`: remove only `data_plane_attestation_rule`; the three attestation members are present together or not at all |
| `admin-deployment-snapshot/v2/invalid/missing-api-spec-contents.json` | From `v2/valid/empty-sql.json`: remove only required `api_spec_contents` |
| `admin-deployment-snapshot/v2/invalid/spec-content-byte-array.json` | From `v2/valid/empty-sql.json`: change only `api_specs` to one item whose `spec_content` is the v0.9.12 byte-array form (empty) instead of a `StoredContentDigest` |
| `admin-deployment-snapshot/v2/invalid/spec-contents-extra-member.json` | From `v2/valid/empty-sql.json`: change only `api_spec_contents` to one item with an extra `spec_content` member; the owner closes these items |
| `admin-deployment-snapshot/v2/invalid/spec-missing-proxy-id.json` | From `v2/valid/one-spec-sql.json`: remove only required `proxy_id` from the `api_specs` item |
| `admin-deployment-snapshot/v2/invalid/spec-digest-uppercase-sha256.json` | From `v2/valid/one-spec-sql.json`: change only `spec_content.sha256` to uppercase hex; the owner emits lowercase |
| `admin-deployment-snapshot/v2/invalid/spec-digest-sha256-byte-array.json` | From `v2/valid/one-spec-sql.json`: change only `spec_content.sha256` to an empty array instead of a hex string |
| `admin-deployment-snapshot/v2/invalid/spec-digest-negative-len.json` | From `v2/valid/one-spec-sql.json`: change only `spec_content.len` to `-1` |
| `admin-deployment-snapshot/v2/invalid/spec-digest-string-len.json` | From `v2/valid/one-spec-sql.json`: change only `spec_content.len` to the string `"88"` |
| `admin-deployment-snapshot/v2/invalid/spec-digest-missing-len.json` | From `v2/valid/one-spec-sql.json`: remove only required `len` from `spec_content` |
| `admin-deployment-snapshot/v2/invalid/spec-digest-extra-member.json` | From `v2/valid/one-spec-sql.json`: add only a `bytes` member to `spec_content`; `StoredContentDigest` is closed |
| `admin-deployment-snapshot/v2/invalid/external-ref-byte-array.json` | From `v2/valid/one-spec-sql.json`: change only `external_ref_snapshot` to the v0.9.12 byte-array form (empty), which is neither a `StoredContentDigest` nor null |
| `admin-deployment-snapshot/v2/invalid/spec-contents-missing-external-ref.json` | From `v2/valid/one-spec-sql.json`: remove only required `external_ref_snapshot_base64` from the `api_spec_contents` item; the owner emits `null` when no snapshot is stored |
| `admin-deployment-snapshot/v2/invalid/spec-contents-numeric-id.json` | From `v2/valid/one-spec-sql.json`: change only the `api_spec_contents` item's `id` to the number `0` |
| `admin-deployment-snapshot/v2/invalid/spec-contents-base64-byte-array.json` | From `v2/valid/one-spec-sql.json`: change only `spec_content_base64` to an empty array instead of a base64 string |
| `admin-deployment-snapshot/v2/invalid/spec-contents-external-ref-byte-array.json` | From `v2/valid/one-spec-sql.json`: change only `external_ref_snapshot_base64` to an empty array instead of a base64 string or null |
| `admin-deployment-snapshot/v2/invalid/{missing-evidence,weak-token,row-token,token-list,token-with-line-break,unknown-profile,evidence-not-object,spec-not-object}.json` | The v1 invalid fixtures of the same name with `api_spec_contents: []` added, so each still makes only its original change against `v2/valid/empty-sql.json` |
| `admin-deployment-snapshot/v1/invalid/missing-evidence.json` | From `v1/valid/empty-sql.json`: remove only required `evidence` |
| `admin-deployment-snapshot/v1/invalid/weak-token.json` | From `v1/valid/empty-sql.json`: change only `namespace_etag` to its weak `W/` form |
| `admin-deployment-snapshot/v1/invalid/row-token.json` | From `v1/valid/empty-sql.json`: change only `namespace_etag` to the owner test's quoted `row-token`, outside deployment authority |
| `admin-deployment-snapshot/v1/invalid/token-list.json` | From `v1/valid/empty-sql.json`: change only `namespace_etag` to the two-token list used by the owner malformed-authority regression |
| `admin-deployment-snapshot/v1/invalid/token-with-line-break.json` | From `v1/valid/empty-sql.json`: append only a line break to `namespace_etag`; the parser requires exact original token bytes |
| `admin-deployment-snapshot/v1/invalid/unknown-profile.json` | From `v1/valid/empty-sql.json`: change only `profile` to `backup-v1`, outside the released deployment profile |
| `admin-deployment-snapshot/v1/invalid/evidence-not-object.json` | From `v1/valid/empty-sql.json`: change only `evidence` from an object to an array |
| `admin-deployment-snapshot/v1/invalid/spec-not-object.json` | From `v1/valid/empty-sql.json`: change only `api_specs` to an array containing a string rather than an object |
| `admin-deployment-mutation-acknowledgement/invalid/unknown-profile.json` | From `valid/applied.json`: change only `profile` to `backup-v1` |
| `admin-deployment-mutation-acknowledgement/invalid/unknown-durable.json` | From `valid/durable-only.json`: change only `durable` to `pending` |
| `admin-deployment-mutation-acknowledgement/invalid/unknown-live.json` | From `valid/durable-only.json`: change only `live` to `all_data_planes_applied`; local acknowledgement does not assert that state |
| `admin-deployment-mutation-acknowledgement/invalid/cleanup-not-boolean.json` | From `valid/durable-only.json`: change only cleanup authorization to the string `false` |
| `admin-deployment-mutation-acknowledgement/invalid/missing-cleanup-authorization.json` | From `valid/durable-only.json`: remove only required `recovery_cleanup_authorized` |
| `admin-deployment-mutation-acknowledgement/invalid/durable-only-cleanup.json` | From `valid/durable-only.json`: change only cleanup authorization to true; `live=not_applicable` violates its source-derived implication |
| `admin-deployment-mutation-acknowledgement/invalid/unknown-durable-cleanup.json` | From `valid/applied.json`: change only `durable` to `unknown`; true cleanup authorization requires committed state |
| `admin-deployment-mutation-acknowledgement/invalid/unconfirmed-cleanup.json` | From `valid/committed-unconfirmed.json`: change only cleanup authorization to true; unconfirmed live state cannot authorize cleanup |
| `admin-conditional-snapshot/invalid/missing-consumer-map.json` | From `valid/metadata.json`: remove only required `row_etags.consumers` |
| `admin-conditional-snapshot/invalid/weak-namespace-tag.json` | From `valid/metadata.json`: change only the namespace token to a weak `W/` tag |
| `admin-conditional-snapshot/invalid/token-with-line-break.json` | From `valid/metadata.json`: append only a line break to the namespace token; quoted entity-tag syntax has no trailing control bytes |
| `admin-conditional-snapshot/invalid/unquoted-row-tag.json` | From `valid/metadata.json`: remove only the quotes from the proxy row token |
| `admin-conditional-snapshot/invalid/unknown-row-map.json` | From `valid/metadata.json`: add only the unsupported `row_etags.api_specs` map; namespace coverage of API specs does not add a row map |
| `backend-egress-policy/v1/invalid/unknown-version.json` | From `v1/valid/default-control-plane.json`: change only `schema_version` to `2` |
| `backend-egress-policy/v1/invalid/unknown-classification.json` | From `v1/valid/default-control-plane.json`: change only `ip_classification` to `unknown` |
| `backend-egress-policy/v1/invalid/unknown-enforcement-scope.json` | From `v1/valid/default-control-plane.json`: change only `enforcement_scope` to `unknown` |
| `backend-egress-policy/v1/invalid/unknown-mode.json` | From `v1/valid/default-control-plane.json`: change only `mode` to `unknown` |
| `backend-egress-policy/v1/invalid/wrong-evaluation-stage.json` | From `v1/valid/default-control-plane.json`: change only evaluation index 0 from `allow-cidrs` to `ip-mode` |
| `backend-egress-policy/v1/invalid/mode-class-mismatch.json` | From `v1/valid/public-serving.json`: change only the allowed mode list to `["private-reserved"]` |
| `backend-egress-policy/v1/invalid/false-public-guarantee.json` | From `v1/valid/public-serving.json`: change only the guarantee to false; the owner emits true for public mode without allow overlays |
| `backend-egress-policy/v1/invalid/allow-overlay-guarantee.json` | From `v1/valid/public-with-allow-overrides.json`: change only the guarantee to true; undisclosed allow overlays prevent certification |
| `backend-egress-policy/v1/invalid/leaked-cidr-field.json` | From `v1/valid/default-control-plane.json`: add only `allow_cidrs`; the closed response withholds raw CIDRs |
| `vocabulary-backend-egress-policy/v1/invalid/unknown-mode.json` | From `v1/valid/v1.json`: change only modes index 0 to `unknown` |
| `vocabulary-backend-egress-policy/v1/invalid/short-commit.json` | From `v1/valid/v1.json`: shorten only provenance index 0's full commit SHA |
| `diagnostic-ref/invalid/unknown-schema-version.json` | `schema_version` is `ferrum.diagnostic_ref.v2` |
| `diagnostic-ref/invalid/malformed-ref.json` | `ref` is not `fd1_` plus 32 lowercase hex digits |
| `diagnostic-ref/invalid/granular-class-as-token.json` | `gateway_error` is an `ErrorClass` (`dns_lookup_error`), not an `X-Gateway-Error` token |
| `diagnostic-ref/invalid/detail-missing-backend-dispatch.json` | `detail.backend_dispatch` is required |
| `diagnostic-ref/invalid/created-at-not-rfc3339.json` | `created_at` is not an RFC 3339 `date-time` (format assertion) |
| `diagnostic-ref/invalid/uppercase-replica-id.json` | `replica_id` is uppercase instead of eight lowercase hexadecimal digits |
| `diagnostic-ref/invalid/route-protocol-admission-as-detail-phase.json` | From `valid/route-protocol-admission.json`: change only `detail.rejection_phase` to `route_protocol_admission`; that member carries the `X-Gateway-Error` token of the phase (`token_for_rejection_phase`), and this phase has none, so the label belongs only in `detail.rejection.phase` |
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
| `vocabulary-gateway-headers/invalid/availability-without-v.json` | From `valid/authenticated-identity.json`: change only the `X-Authenticated-Identity` `availability` to `0.9.15`; availability names an Edge tag (`v0.9.15`) or `unreleased` |
| `vocabulary-provisioned-by/invalid/untrimmed-value.json` | a value with leading whitespace; Edge trims the header |
| `vocabulary-provisioned-by/invalid/wrong-label-key.json` | label key `provisioned_by` |
| `vocabulary-plugin-catalog/invalid/unknown-protocol.json` | protocol `http2`; the catalog uses Edge's five protocol families |
| `vocabulary-plugin-catalog/invalid/unknown-websocket-framing-plugin.json` | `websocket_framing_plugins` contains a name not declared by Edge |
| `vocabulary-plugin-catalog/invalid/unknown-failure-policy.json` | failure policy `fail_open` |
| `vocabulary-plugin-catalog/invalid/bad-schema-pointer.json` | a config schema pointer that is not a component name |
