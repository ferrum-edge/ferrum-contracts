# contracts-edge-0.9.21 release record

`contracts-edge-0.9.21` holds the contracts for published Ferrum Edge
`v0.9.21`. The tag is the merge commit of its release PR. The
[GitHub release](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.21)
records the Contracts tag identity, publication time and tag verification
evidence.

This release follows the signed-tag policy in
[release-signing.md](../release-signing.md), requiring an SSH-signed annotated
tag made by an authorized maintainer with no unsigned fallback. The tag object
SHA, signer fingerprint, trust-policy commit and verification result exist only
after tagging and belong to the GitHub release notes rather than to this file.

## Edge source

Edge `v0.9.21` points to `f9915358c8032214f4034a17c28cdf72d14006c3`, the merge
commit of Edge PR #7472 (docs-only follow-up to PR #7470
`570d65ed2f7d44031ac2fe38cf0dcf5c01a08932`). The
[Edge release](https://github.com/ferrum-edge/ferrum-edge/releases/tag/v0.9.21)
was published at 06:29:03 UTC on 2026-11-22 (GitHub Release `454250773`). It
follows published `v0.9.20` (`e4a606a00352674daaef08636e3e359e6c48ba18`)
directly. Its assets, checksums, signed container indices, provenance, SBOMs
and application qualification belong to that owner release. Every owner source
used here is read with `git show v0.9.21:<path>` from the Edge repository at
that immutable tag, and compared with `v0.9.20` by `git diff v0.9.20 v0.9.21`.
Edge `main` at `b233be97f0ae2c694d4ecff37b365099bd729055` (after hot-path
throughput PR #7471 and publication-record PR #7473) carries no contract-visible
changes beyond `v0.9.21` (`openapi.yaml`, `src/retry.rs`,
`src/diagnostic_ref.rs`, `src/plugins/builtin_parity.rs`, `src/admin/` and all
plugin registrations and header sets are identical to the tag), so no
vocabulary records a `main_branch_delta`.

The tagged `openapi.yaml` has SHA-256
`13c21d12d3028c8044ad2f467cbca6425d9bd2f3fce787d6fe7ae78316c21bee` and
`info.version: 0.9.21`. `PluginConfigBase`'s `allOf` conditionals and every
diagnostic, conditional-backup, egress, deployment and attribution OpenAPI
component are byte-identical to `v0.9.20`; `PluginConfigBase` descriptions,
`IfMatch`, `ResourceETag` and referenced plugin configuration components carry
the `v0.9.21` rules summarized below and in
[plugin-config-admission.md](../plugin-config-admission.md) and
[admin-contracts.md](../admin-contracts.md).

## Vocabulary and schema changes

All five vocabulary `edge_release` values and their Edge source entries pin
`v0.9.21` and its full commit. Values observed in other products retain those
products' recorded provenance. No canonical schema needs a new major. The
Edge-owned schemas accept the same payloads as in `contracts-edge-0.9.20`; this
tag also ships the non-Edge v1 schema tightenings and Alloy derived-ID
qualification cases merged to `main` since `contracts-edge-0.9.20`
(`service-manifest` v1 Edge upper bounds, control-character rules and
cleartext `otel_endpoint` rule; `gitforgeops-resource` v1 strict envelope
closure; `qualification/service-manifest/v1/derived-id-limit.json`).

- **Plugin catalog.** Re-transcribed from the tag. The 82 registered names, two
  removed names, response-body producer and WebSocket framing membership, and
  every `PluginConfigBase` pointer, config-required and scope conditional are
  unchanged versus `contracts-edge-0.9.20` (`vocabularies/plugin-catalog.json`)
  and Edge `v0.9.20` (`src/plugins/mod.rs`, `src/plugins/builtin_parity.rs`,
  `openapi.yaml`). Five log-sink registration failure policies move from
  `optional_fail_open` to `keep_last_known_good` (Edge #7369): `http_logging`,
  `udp_logging`, `statsd_logging`, `loki_logging` and `ws_frame_logging`, so
  all nine log sinks are `keep_last_known_good`. In
  `src/plugins/builtin_parity.rs`, `http_logging`, `tcp_logging`,
  `kafka_logging`, `loki_logging` and `udp_logging` add `on_ws_disconnect`
  (Edge #7369); `request_transformer` adds
  `on_final_request_body_with_context` and `response_transformer` adds
  `finalize_client_visible_response_body` (Edge #7469); and `compression`
  names `zstd` in its `protocol_rationale`. The previous `main_branch_delta`
  is promoted into released metadata and removed.
- **Gateway errors.** The 19 `ErrorClass` values, nine header tokens, 25
  reserved HTTP metric labels, class-to-token mapping and
  `http_backend_failure_status_and_body` statuses remain the same as in
  `contracts-edge-0.9.20` (`vocabularies/gateway-errors.json`) and Edge
  `v0.9.20` (`src/retry.rs`, `src/proxy/mod.rs`).
  `token_for_rejection_phase` drops the `circuit_breaker` alias (Edge #7158):
  HTTP/3 now logs `circuit_breaker_open`, so `circuit_breaker_open`'s
  `rejection_phases` is `["circuit_breaker_open"]`. Post-connect
  classification is phase-gated in the boxed-error substring fallback, the
  tungstenite `Io` arm and `classify_body_error`, and UDP session failures
  classify from typed `io::Error` (Edge #7213). `StreamSetupKind` adds
  `L4RouteRefused` (`dispatch_policy_rejected`) and
  `BackendFirstBytesForward` (post-wire `io` class, fallback `request_error`;
  Edge #7185). Eight new raw rejection phases (none token-mapped) enter
  `src/diagnostic_ref.rs`: `invalid_backend_path`,
  `websocket_upgrade_unavailable`, `mesh_transport_dispatch_required`,
  `request_body_refused_before_{authenticate,authorize,before_proxy,dispatch}`
  and `grpc_post_required` (Edge #7156, #7157, #7163, #7411). On HTTP/1.1 and
  HTTP/2, gRPC-Web clients get framed HTTP `200` trailer-frame refusals for
  route-protocol admission, circuit-breaker-open (keeping
  `X-Gateway-Error: circuit_breaker_open`) and remaining native-gRPC branch
  refusals (Edge #7155), and `all`-mode gRPC-Web rejections resolve with status
  `200` (Edge #7411). A backend's 3xx–5xx answer to a WebSocket upgrade is
  relayed without `X-Gateway-Error` or `error_class` instead of a 502
  `backend_error` (Edge #7414). The previous `main_branch_delta` is promoted
  into released provenance and removed.
- **Gateway headers.** Repinned; no header name, prefix, role, direction or
  `not_headers` entry is added, removed or renamed, and `availability` retains
  the corrected first-published-release values (#59). HTTP/1.1, HTTP/2 and
  HTTP/3 WebSocket upgrades share `is_websocket_backend_request_strip_header`
  (Edge #7048), so HTTP/3 also strips `Content-Length`, `Expect`,
  `X-Ferrum-Original-Content-Encoding` and `x-grpc-web-mode`; WebSocket
  handshakes forward backend 101/200 headers under the backend-response strip
  and honor `preserve_host_header` (Edge #7414). Route-owned plugin assertions
  (`claim_headers`, `output_claim_headers`, `opa` `decision_request_headers`,
  `spiffe_identity` `forward_identity=true`) are enforced by
  `enforce_route_owned_request_assertions`, stripped from request trailers with
  `_`/`-` folding, and refuse untranslated gRPC-Web with 415 (Edge #7064).
  `X-Ferrum-Diagnostic-Ref` in `all` mode stamps recorded gRPC-Web rejections
  (status `200`) and appends `x-ferrum-diagnostic-ref` to an existing
  `Access-Control-Expose-Headers` header (Edge #7411). `If-Match` is evaluated
  on the four consumer credential routes (Edge #7412) and refused with `400`
  before lookup on `POST /api-specs` and `DELETE /api-specs/{id}` (Edge
  #7459). `ETag` is withheld from tokens verified by
  `FERRUM_ADMIN_JWT_VIEWER_SECRET` (Edge #7413). The previous
  `main_branch_delta` is promoted into released entries and removed.
- **Attribution and egress.** `provisioned-by` names, bounds and open-set
  behavior are unchanged versus `contracts-edge-0.9.20`
  (`vocabularies/provisioned-by.json`); `src/admin/provisioning.rs` and
  `components.parameters.ProvisionedBy` are byte-identical to `v0.9.20`.
  Backend egress remains response `schema_version: 2` with classifier
  `ferrum-private-reserved-v1`, the same scopes, modes, evaluation order,
  local public-only guarantee and optional CP data-plane attestation;
  `src/admin/backend_egress_policy.rs`,
  `src/grpc/backend_egress_attestation.rs` and the egress OpenAPI components
  are byte-identical to `v0.9.20`. ConfigSync moves to protocol revision 6
  (Edge #7338, #7371, #7417); CP and DP must run the same build.
- **Admin schemas.** Conditional backup v1, backend egress v2, deployment
  snapshot v2, mutation acknowledgement v1 and the egress vocabulary schema v2
  are re-read at the tag and repin their source metadata. Their OpenAPI
  components, `src/admin/conditional_snapshots.rs`, `src/admin/preconditions.rs`
  and `src/admin/deployment_mutations.rs` are byte-identical to `v0.9.20`.
  `src/admin/backup.rs` retires `api_specs.section_version: "1"` and empty
  `resource_hash` in restore bodies (Edge #7218). All five schemas' wire shapes
  remain unchanged versus `contracts-edge-0.9.20`
  (`schemas/admin-conditional-snapshot/v1.schema.json`,
  `schemas/backend-egress-policy/v2.schema.json`,
  `schemas/admin-deployment-snapshot/v2.schema.json`,
  `schemas/admin-deployment-mutation-acknowledgement/v1.schema.json` and
  `schemas/vocabulary-backend-egress-policy/v2.schema.json`).
- **Diagnostic-ref freeze.** The five `DiagnosticRef*` OpenAPI components are
  byte-identical to `v0.9.20`, and the nine `gateway_error` tokens and five
  token-mapped `detail.rejection_phase` tokens are unchanged versus
  `contracts-edge-0.9.20` (`schemas/diagnostic-ref/v1.schema.json`,
  `vocabularies/gateway-errors.json`; `status` already admits `200` and
  `detail.rejection.phase` is open). Following
  `docs/release-process.md`, canonical v1 is preserved byte for byte, including
  its historical provenance. Its SHA-256 is
  `11508c19f571b57be7e755b5f17409ebc73cd270debd015d1a4ea49a37950520`.

## Shipping plugin admission and admin rules

Edge `v0.9.21` ships the plugin admission and admin rules previously tracked on
Edge `main` plus the final `v0.9.21` hardening PRs (#7459–#7469). See
[plugin-config-admission.md](../plugin-config-admission.md#edge-v0921-admission-and-config-changes)
and [admin-contracts.md](../admin-contracts.md#admin-authorization-and-write-rules)
for the complete details:

- Removed obsolete plugin config keys and aliases across `hmac_auth`,
  `ip_restriction`, `jwks_auth`, `mcp_gateway`, `response_caching`,
  `tcp_connection_throttle`, `workload_metrics` and `ai_semantic_firewall`, and
  `Proxy.pool_max_requests_per_connection`.
- Gateway-dialed cleartext auth/sink endpoints narrowed to loopback IP literals
  (no `localhost`), `request_mirror.allow_plaintext` required for non-loopback
  cleartext mirrors, `api_chargeback_sink` TLS `verify_hostname` conditional,
  and `ai_response_guard` gRPC caps (`max_messages <= 1024`,
  `max_message_bytes <= 64 MiB`).
- Admin-managed JWKS (`providers[].jwks_source` on `jwks_auth` and
  `oidc_relying_party`, registered as TLS material), stricter `/admin/tls/jwks`
  admission, cross-namespace managed TLS delete guards, conditional consumer
  credential writes, explicit `If-Match` refusal on `POST`/`DELETE /api-specs`,
  viewer-key `ETag`/generation withholding, dedicated `/config/export`
  fingerprint key, and `charges:collect` billing-collector scope.
- `mesh_route_dispatch.weighted_splits`, `mesh_authz.node_waypoint_route_branches`,
  `PluginTriggerMatch` `external_identity` and `external_identity_authority`
  predicates, mapped-Consumer-only matching on consumer lists and
  realm-qualified limiter/chargeback keys, `access_control` `authority`
  binding, `oidc_relying_party` canonical post-login redirects and
  `post_login_default_path` control/backslash refusal, `api_chargeback`
  `1.0e+288` YAML 1.1-safe bounds, `mcp_gateway` operation path bounds,
  `a2a_gateway` fail-closed JSON-RPC classification, and duplicate-member JSON
  refusal across body-inspecting and transformer plugins.

The owner's tagged
[upgrade guide](https://github.com/ferrum-edge/ferrum-edge/blob/f9915358c8032214f4034a17c28cdf72d14006c3/docs/upgrade_guide.md)
and `CHANGELOG.md` describe the full rollout and runtime requirements,
including the `V001` baseline rebuild requirement for SQL datastores and
ConfigSync revision 6.

## Source paths and fixtures

All Edge paths in this section are at
`f9915358c8032214f4034a17c28cdf72d14006c3`:

- Errors and diagnostic phases: `src/retry.rs`, `src/diagnostic_ref.rs`,
  `src/proxy/mod.rs`, `src/http3/server.rs`, `docs/error_classification.md`,
  `docs/size_limits.md`, `openapi.yaml`.
- Headers: `src/proxy/headers.rs`, `src/proxy/mod.rs`, `src/proxy/hop_limit.rs`,
  `src/plugins/mod.rs`, `src/plugins/grpc_web.rs`,
  `src/plugins/mesh/spiffe_identity.rs`, `src/plugins/mesh/ext_authz.rs`,
  `src/admin/preconditions.rs`, `src/admin/conditional_snapshots.rs`,
  `src/admin/deployment_mutations.rs`, `src/admin/mod.rs`, `docs/plugins.md`,
  `docs/mesh.md`, `docs/plugin_execution_order.md`, `docs/admin_api.md`,
  `docs/admin_backup_restore.md`, `docs/deployment_mutations.md`,
  `docs/api_specs.md`, `openapi.yaml`.
- Attribution: `src/admin/provisioning.rs`, `docs/admin_api.md`,
  `docs/hardening.md`, `openapi.yaml`.
- Catalog: `src/plugins/mod.rs`, `src/plugins/builtin_parity.rs`,
  `openapi.yaml` (`PluginConfigBase` and referenced config components).
- Egress: `src/admin/backend_egress_policy.rs`,
  `src/grpc/backend_egress_attestation.rs`, `src/config/env_config.rs`,
  `docs/admin_api.md`, `openapi.yaml`.
- Conditional/deployment schemas: `src/admin/conditional_snapshots.rs`,
  `preconditions.rs`, `backup.rs`, `deployment_mutations.rs`,
  `src/config/deployment_mutation.rs`, `db_backend.rs`, `db_loader.rs`,
  `mongo_store.rs`, `types.rs`, `docs/admin_backup_restore.md`,
  `docs/deployment_mutations.md`, `openapi.yaml`.
- Admission notes: `src/admin/crud.rs`,
  `src/admin/crud/scoped_references.rs`, `docs/upgrade_guide.md`,
  `CHANGELOG.md`, `openapi.yaml`.

Four new fixtures cover the `v0.9.21` changes:
`vocabulary-plugin-catalog/valid/edge-0.9.21-metadata.json` (the refreshed
metadata for `http_logging`, `ws_frame_logging`, `request_transformer`,
`response_transformer` and `compression`) and its invalid counterpart
`edge-0.9.21-unknown-failure-policy.json`; and
`diagnostic-ref/valid/grpc-post-required.json` (an `all`-mode gRPC-Web
rejection reference resolving with `status: 200` and raw phase
`grpc_post_required`) and its invalid counterpart
`grpc-post-required-as-detail-phase.json`. `fixtures/README.md` records their
provenance and `fixtures/invalid-expectations.json` pins each invalid fixture's
expected path and keyword. Prior fixtures, earlier schema majors, other owners'
availability and recorded consumer pin snapshots retain their original bytes
and identities.

## Validation and adoption

GitHub-hosted `Validate contracts` remains the schema, fixture,
cross-reference, qualification and pinned OpenAPI conformance gate. Local
review used static source and diff inspection, the SHA-256 of the exact tagged
OpenAPI bytes, a standard-library comparison of every catalog entry with the
tagged registration, parity and `PluginConfigBase` sources, and
`git diff --check`. The release refresh changes no validator, workflow,
permissions or dependency pins.

Consumers targeting `v0.9.21` must stop emitting the removed plugin config
keys, follow the loopback-IP cleartext, `request_mirror.allow_plaintext`,
`access_control` `authority`, `external_identity` trigger and mapped-Consumer
rules, handle `keep_last_known_good` log-sink reloads and viewer-key `ETag`
omission, and adopt the tightened `service-manifest` and
`gitforgeops-resource` v1 rules where applicable. Each consumer then qualifies
its own pin/copy/checksum PR. A canonical Contracts release alone does not
change those pins, certify application integration or publish another product.
