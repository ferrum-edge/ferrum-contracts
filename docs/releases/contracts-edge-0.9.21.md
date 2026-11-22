# contracts-edge-0.9.21 release record

`contracts-edge-0.9.21` holds the contracts for published Ferrum Edge
`v0.9.21`. The tag is the merge commit of its release PR. The
[GitHub release](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.21)
records the Contracts tag identity, publication time and tag verification
evidence.

The tag is an SSH-signed annotated tag made by an authorized maintainer under
[release-signing.md](../release-signing.md), with no unsigned fallback. The
tag object SHA, signer fingerprint, trust-policy commit and verification
result exist only after tagging, so they belong to the GitHub release notes
rather than to this file.

## Edge source

Edge `v0.9.21` points to `f9915358c8032214f4034a17c28cdf72d14006c3`, the
merge commit of Edge PR #7472. The
[Edge release](https://github.com/ferrum-edge/ferrum-edge/releases/tag/v0.9.21)
(release 454250773) was published at 06:29:03 UTC on 2026-11-22. It follows
published `v0.9.20` (`e4a606a00352674daaef08636e3e359e6c48ba18`) directly. Its
assets, checksums, signed container indices, provenance, SBOMs and application
qualification belong to that owner release. Every owner source used here is
read with `git show v0.9.21:<path>` from the Edge repository at that immutable
tag, and compared with `v0.9.20` by `git diff v0.9.20 v0.9.21`.

When the sources were read, Edge `main` was at
`b233be97f0ae2c694d4ecff37b365099bd729055` (the merge of Edge PR #7473),
16 commits after the tag. The plugin catalog, gateway-headers and
gateway-errors vocabularies record it as their `main_branch_delta`: of their
sources only `src/proxy/headers.rs`, `src/proxy/mod.rs` and
`src/plugins/mod.rs` change there (Edge PR #7471, HTTP/1.1 hot paths), and no
header, error, plugin registration or configuration value changes.

The tagged `openapi.yaml` has SHA-256
`13c21d12d3028c8044ad2f467cbca6425d9bd2f3fce787d6fe7ae78316c21bee`.
`PluginConfigBase` changes only its descriptions. Many plugin configuration
components change (see below), and so do several admin components
(`components.headers.ResourceETag`, `components.parameters.IfMatch`, the
`/api-specs` and `/charges` operations, `Proxy`, `Upstream` and others). The
backup, egress, deployment, attribution and diagnostic components the
Edge-owned schemas cite are byte-identical, except that `ResourceETag` adds
the viewer-key rule.

## Vocabulary and schema changes

All five vocabulary `edge_release` values and their Edge source entries pin
`v0.9.21` and its full commit. Values observed in other products retain those
products' recorded provenance. No canonical schema needs a new major, and every
Edge-owned schema accepts the same payloads as in `contracts-edge-0.9.20`.

- **Plugin catalog.** Re-transcribed from the tag, not only repinned. The 82
  registered names, two removed names, classifications, priorities,
  protocols, response-body producers, WebSocket framing plugins and every
  `PluginConfigBase` pointer, config-required and scope conditional are
  unchanged. Five registration failure policies change (Edge #7369, issue
  #7144): `http_logging`, `udp_logging`, `statsd_logging`, `loki_logging` and
  `ws_frame_logging` move from `optional_fail_open` to
  `keep_last_known_good`, so every log sink is `keep_last_known_good`.
  `http_logging`, `tcp_logging`, `kafka_logging`, `loki_logging` and
  `udp_logging` add `on_ws_disconnect`; `request_transformer` adds
  `on_final_request_body_with_context` and `response_transformer`
  `finalize_client_visible_response_body` (Edge #7469, GHSA-pq95-952r-2x32).
  The `compression` rationale names zstd. The OpenAPI provenance note records
  the configuration component changes.
- **Gateway errors.** The 19 `ErrorClass` values, nine header tokens, 25
  reserved HTTP metric labels, class-to-token mapping and transcribed
  dispatch-failure statuses remain the same, and
  `http_backend_failure_status_and_body` and `docs/size_limits.md` are
  unchanged. `token_for_rejection_phase` no longer maps the raw phase
  `circuit_breaker` (Edge #7158), so `circuit_breaker_open` lists only its own
  phase. Class meanings record the phase-gated substring fallback (Edge
  #7213), the L4 route refusal (Edge #7185) and the relayed WebSocket upgrade
  refusal (Edge #7414, GHSA-7x2j-3389-2h35): a backend's own `3xx`-`5xx`
  answer to a WebSocket upgrade now reaches the client with its status and no
  `X-Gateway-Error`, where `v0.9.20` answered `502` with `backend_error`.
  `src/diagnostic_ref.rs` adds raw rejection phases that map to no token
  (`invalid_backend_path`, `websocket_upgrade_unavailable`,
  `mesh_transport_dispatch_required`, the four
  `request_body_refused_before_*` phases and `grpc_post_required`). On
  HTTP/1.1 and HTTP/2 more refusals reach gRPC-Web clients in gRPC-Web
  framing (Edge #7155).
- **Gateway headers.** Every header name, role, direction and availability
  is unchanged. Entries record their `v0.9.21` behavior: the shared WebSocket
  handshake strip set (Edge #7048, so HTTP/3 handshakes also strip
  `X-Ferrum-Original-Content-Encoding`), route-owned plugin assertions
  including `x-ferrum-peer-spiffe-id` (Edge #7064), gRPC-Web stamping of
  `X-Ferrum-Diagnostic-Ref` (Edge #7411), no row `ETag` for viewer-key tokens
  (Edge #7413), conditional consumer credential writes with `If-Match` (Edge
  #7412) and its refusal on `POST /api-specs` and `DELETE /api-specs/{id}`
  (Edge #7459), and per-destination mesh CUSTOM checks (Edge #7384, #7389).
  `refresh_backend_gateway_assertion_headers` is unchanged.
- **Attribution and egress.** `provisioned-by` names, bounds and open-set
  behavior are unchanged; `src/admin/provisioning.rs` is unchanged. Backend
  egress remains response `schema_version: 2` with the same labels,
  evaluation order, local public-only guarantee and optional CP data-plane
  attestation. `src/admin/backend_egress_policy.rs` and
  `src/grpc/backend_egress_attestation.rs` are unchanged, and so are the
  cited `src/config/env_config.rs` symbols. Data planes now use ConfigSync
  protocol revision 6, and the exact-build rule still holds.
- **Admin schemas.** Conditional backup v1, backend egress v2, deployment
  snapshot v2, mutation acknowledgement v1 and the egress vocabulary schema v2
  are re-read at the tag and repin their source metadata.
  `src/admin/conditional_snapshots.rs`, `preconditions.rs` and
  `deployment_mutations.rs`, `docs/admin_backup_restore.md`,
  `docs/deployment_mutations.md` and the cited symbols in `backup.rs`,
  `src/config/deployment_mutation.rs`, `db_backend.rs`, `db_loader.rs`,
  `mongo_store.rs` and `types.rs` are unchanged. `deployment_mutation.rs`
  drops the removed `pool_max_requests_per_connection` proxy column from its
  replaceable columns; the snapshot schema does not enumerate row columns.
  Their wire rules remain unchanged.
- **Diagnostic-ref freeze.** The diagnostic OpenAPI components are unchanged
  from `v0.9.20`. The new raw phases are open `rejection.phase` labels, and a
  gRPC-Web reference's `status: 200` is in range, so, following
  `docs/release-process.md`, canonical v1 is preserved byte for byte,
  including its historical provenance. Its SHA-256 is
  `11508c19f571b57be7e755b5f17409ebc73cd270debd015d1a4ea49a37950520`.

## Shipping plugin admission and runtime rules

Edge `v0.9.21` removes deprecated plugin configuration keys and values
(`hmac_auth` `ferrum-hmac-v1`, `ip_restriction` `mode`, the `jwks_auth`
`audience` alias, `mcp_gateway` and `workload_metrics` aliases, the
`response_caching` key toggles, `tcp_connection_throttle`
`cleanup_interval_seconds`, `ai_semantic_firewall` `privacy.log_raw_text`).
It adds the managed JWKS source, weighted mesh splits, `request_mirror`
`allow_plaintext`, the `external_identity` and `external_identity_authority`
trigger predicates and `access_control` authority binding. It narrows
gateway-dialed cleartext auth endpoints to loopback IP literals, matches
Consumer-name lists against mapped Consumers only, refuses duplicate-member
JSON in the transformers' body rules and canonicalizes `oidc_relying_party`
post-login redirects.
[plugin-config-admission.md](../plugin-config-admission.md#edge-v0921-plugin-configuration-changes)
gives the details, and
[admin-contracts.md](../admin-contracts.md#admin-authorization-and-write-rules)
the admin rules (managed JWKS records, the cross-namespace managed TLS delete
guard, conditional credential writes and primary-secret detail).

The owner's tagged
[upgrade guide](https://github.com/ferrum-edge/ferrum-edge/blob/f9915358c8032214f4034a17c28cdf72d14006c3/docs/upgrade_guide.md#upgrading-to-0921)
and `CHANGELOG.md` describe the remaining runtime changes, including the
`V001` baseline rebuild, Sidecar and NodeWaypoint VirtualService HTTP routes,
wildcard DestinationRules, fail-closed markers for refused Istio security
resources and the removal of `pool_max_requests_per_connection`. None of them
changes a contract here beyond what this record lists.

## Source paths and fixtures

All Edge paths in this section are at
`f9915358c8032214f4034a17c28cdf72d14006c3`:

- Errors: `src/retry.rs`, `src/proxy/mod.rs`, `docs/error_classification.md`,
  `docs/size_limits.md`, `src/diagnostic_ref.rs`.
- Headers: `src/proxy/headers.rs`, `src/proxy/mod.rs`, `src/proxy/hop_limit.rs`,
  `src/plugins/mod.rs`, `src/plugins/grpc_web.rs`,
  `src/plugins/mesh/spiffe_identity.rs`, `src/plugins/mesh/ext_authz.rs`,
  `docs/plugins.md`, `docs/mesh.md`, `docs/plugin_execution_order.md`, the admin
  and deployment docs, and `openapi.yaml`; each entry records its own paths.
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
- Admission notes: `docs/upgrade_guide.md`, `CHANGELOG.md`, `openapi.yaml`.

`diagnostic-ref` gains `valid/grpc-post-required.json` and
`invalid/grpc-post-required-as-detail-phase.json` for the new
`grpc_post_required` phase, recorded with the gRPC-Web `200`
([fixtures/README.md](../../fixtures/README.md#edge-v0921-refresh-fixtures)).
No other fixture changes for the Edge refresh. Prior fixtures, earlier schema
majors, other owners' availability and recorded consumer pin snapshots retain
their original bytes and identities.

This release also carries the Contracts changes merged since
`contracts-edge-0.9.20`: the tightened `service-manifest` v1 bounds and
`otel_endpoint` rule, the closed `gitforgeops-resource` v1 envelope, the
service-manifest qualification cases, the consumer `PIN` format and Edge
`main` check, validator fixes and the commercial license; `CHANGELOG.md` lists
them.

## Validation and adoption

GitHub-hosted `Validate contracts` remains the schema, fixture, cross-reference
and pinned OpenAPI conformance gate. Local review used static source and diff
inspection, the SHA-256 of the exact tagged OpenAPI bytes, a standard-library
comparison of every catalog entry with the tagged registration and parity
sources, a comparison of the `PluginConfigBase` block and of every cited
admin, egress, deployment and diagnostic OpenAPI component and Rust symbol
between `v0.9.20` and `v0.9.21`, and `git diff --check`. The release refresh
changes no validator, workflow, permissions or dependency pins.

Consumers targeting `v0.9.21` must stop sending the removed plugin config
keys, use loopback IP literals for gateway-dialed cleartext auth endpoints,
set `allow_plaintext` for a cleartext non-loopback mirror, and select
external principals with the new trigger predicates rather than Consumer-name
lists. Each consumer then qualifies its own pin/copy/checksum PR. A canonical
Contracts release alone does not change those pins, certify application
integration or publish another product.
