# contracts-edge-0.9.20 release record

`contracts-edge-0.9.20` holds the contracts for published Ferrum Edge
`v0.9.20`. The tag is the merge commit of its release PR. The
[GitHub release](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.20)
records the Contracts tag identity, publication time and tag verification
evidence.

This is the first Contracts release under the signed-tag policy introduced in
#44. That policy requires an SSH-signed annotated tag made by an authorized
maintainer, with no unsigned fallback; see
[release-signing.md](../release-signing.md) for the trust files and the
consumer verification procedure. The tag object SHA, signer fingerprint,
trust-policy commit and verification result exist only after tagging, so they
belong to the GitHub release notes rather than to this file. Tags through
`contracts-edge-0.9.19` remain lightweight and unsigned.

## Edge source

Edge `v0.9.20` points to `e4a606a00352674daaef08636e3e359e6c48ba18`, the
merge commit of Edge PR #7016. The
[Edge release](https://github.com/ferrum-edge/ferrum-edge/releases/tag/v0.9.20)
was published at 08:58:10 UTC on 2026-11-03. It follows published `v0.9.19`
(`510ce7121c3d9754110d330a30a3bd9b7a7b278e`) directly. Its assets, checksums,
signed container indices, provenance, SBOMs and application qualification
belong to that owner release. Every owner source used here is read with
`git show v0.9.20:<path>` from the Edge repository at that immutable tag, and
compared with `v0.9.19` by `git diff v0.9.19 v0.9.20`. Edge `main` matched the
tag commit when the sources were read, so no vocabulary records a
`main_branch_delta`.

The tagged `openapi.yaml` has SHA-256
`8fa7232d96e1094578dee03cfa1966a4fdd9df77b8e027a9625f56ce6bfd355e`.
Relative to `v0.9.19` it changes only the `Proxy` and `Upstream` descriptions,
the `BackendCapabilityEntry` key description and the `/backend-capabilities`
response example, and the plugin
configuration components `WorkloadMetricsConfig`, `MeshAuthzPolicyScope` and
`MeshAuthzConfig`. `PluginConfigBase` and every admin, backup, egress,
deployment, attribution and diagnostic component are byte-identical.

## Vocabulary and schema changes

All five vocabulary `edge_release` values and their Edge source entries pin
`v0.9.20` and its full commit. Values observed in other products retain those
products' recorded provenance. No canonical schema needs a new major, and every
schema accepts the same payloads as in `contracts-edge-0.9.19`.

- **Gateway errors.** The 19 `ErrorClass` values, nine header tokens, 25
  reserved HTTP metric labels, class-to-token mapping and token-mapped
  rejection phases remain the same; `src/retry.rs` and
  `http_backend_failure_status_and_body` are unchanged. HTTP/1.1 and HTTP/2
  now frame pre-routing refusals for gRPC clients as HTTP/3 already did (Edge
  #6965 and #6969, issue #6943): native gRPC gets HTTP 200 Trailers-Only
  `grpc-status`, and gRPC-Web a status in its body trailer frame. gRPC-Web
  keeps the JSON `431` for the header limits and the plain HTTP answer at the
  hop limit and at the overload, stale-configuration and withdrawn
  client-trust fences. A WebSocket Upgrade or Extended CONNECT carrying a gRPC
  Content-Type, and every other CONNECT, keeps its HTTP refusal. The framed
  HTTP 200 refusals carry no `X-Gateway-Error` token; plain HTTP answers keep
  theirs. The HTTP/1.1 parse-layer contract changes to match: duplicate `Host`
  and combined `Content-Length` + `Transfer-Encoding` that reach the handler
  get the framed `INVALID_ARGUMENT` refusal for gRPC and gRPC-Web clients.
  These facts move from the `main_branch_delta` recorded by #43 into released
  provenance, with a new `docs/size_limits.md` source; the delta is removed.
  `protocol_error` also notes that a gRPC backend failure, a `CANCEL` reset
  included, observed at or after the client RPC deadline is settled as that
  deadline (`DEADLINE_EXCEEDED`, health-neutral) rather than charged to the
  backend (Edge #6973, #6979; issues #6022, #6976).
- **Plugin catalog.** Re-transcribed from the tag, not only repinned. The 82
  registered names, two removed names, failure policies, parity priorities,
  phases, protocols and rationales, response-body producer and WebSocket
  framing membership, and every `PluginConfigBase` pointer, config-required
  and scope conditional are unchanged; `src/plugins/builtin_parity.rs` and the
  `PluginConfigBase` block are byte-identical to `v0.9.19`. The OpenAPI
  provenance note records the closed nested components. Edge #6975 adds
  `lifecycle_hooks()` declarations to built-in plugins; each agrees with the
  catalog's `active_phases`, and the catalog gains no field for them.
- **Gateway headers.** Repinned; every header name, role, direction,
  availability and behavior is unchanged. `src/proxy/headers.rs`,
  `src/proxy/hop_limit.rs`, `src/plugins/grpc_web.rs` and
  `src/plugins/mesh/spiffe_identity.rs` change only by refactoring or hook
  declarations, and `refresh_backend_gateway_assertion_headers` is unchanged.
  The plugin-free header passthrough (Edge #6981) excludes reserved assertion
  names, so gateway-owned assertions keep their rules.
- **Attribution and egress.** `provisioned-by` names, bounds and open-set
  behavior are unchanged; `src/admin/provisioning.rs` is unchanged. Backend
  egress remains response `schema_version: 2` with classifier identifier
  `ferrum-private-reserved-v1`, the same labels, evaluation order, local
  public-only guarantee and optional CP data-plane attestation.
  `src/admin/backend_egress_policy.rs` and
  `src/grpc/backend_egress_attestation.rs` are unchanged; `src/config/env_config.rs`
  adds only the unrelated `FERRUM_HTTP_CLIENT_WRITE_TIMEOUT_SECONDS` setting.
- **Admin schemas.** Conditional backup v1, backend egress v2, deployment
  snapshot v2, mutation acknowledgement v1 and the egress vocabulary schema v2
  are re-read at the tag and repin their source metadata. `src/admin/` and
  their OpenAPI components are unchanged; `src/config/types.rs` changes only
  doc comments, and the owner admin docs only their wording. Their wire rules
  remain unchanged.
- **Diagnostic-ref freeze.** `src/diagnostic_ref.rs`, `src/retry.rs` and the
  diagnostic OpenAPI components are unchanged from `v0.9.19`. The recorded
  rejection phase is always one of the compiled-in labels, so no raw label is
  added and no fixture is needed. Following `docs/release-process.md`, canonical
  v1 is preserved byte for byte, including its historical provenance. Its
  SHA-256 is
  `11508c19f571b57be7e755b5f17409ebc73cd270debd015d1a4ea49a37950520`.

## Shipping plugin admission and runtime rules

Edge `v0.9.20` closes plugin configuration at every depth (Edge #6967 and
#6972, issue #6616). Plugin configs were already closed at their root; nested
objects that ignored unknown keys now reject them at admission and when stored
configuration is loaded. The pinned OpenAPI publishes the closure for
`workload_metrics` tracing providers, metrics, tag overrides and their
operations, and for `mesh_authz` policy scopes, target-ref attachments and
node-waypoint route upstreams. Policy `targetRefs` attachments require `name`,
plus `namespace` on `service` and `gateway`. The owner changelog lists the
further runtime-only closures in `mesh_authz`. Mesh Telemetry documents are
closed at every level. Custom plugins must export a config contract, which
does not affect the built-in catalog.
[plugin-config-admission.md](../plugin-config-admission.md#closed-nested-plugin-configs)
gives the details. Every rule recorded for `v0.9.19` is unchanged.

The owner's tagged
[upgrade guide](https://github.com/ferrum-edge/ferrum-edge/blob/e4a606a00352674daaef08636e3e359e6c48ba18/docs/upgrade_guide.md)
and `CHANGELOG.md` describe the remaining runtime changes, including the
client write-stall bound, waypoint RequestAuthentication scoping, NodeWaypoint
source rechecks and the refusal of a mesh HBONE CONNECT that declares a gRPC
Content-Type. None of them changes a contract here.

## Source paths and fixtures

All Edge paths in this section are at
`e4a606a00352674daaef08636e3e359e6c48ba18`:

- Errors: `src/retry.rs`, `src/proxy/mod.rs`, `docs/error_classification.md`,
  `docs/size_limits.md`.
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

No fixture is added: no vocabulary value, header, plugin entry, rejection-phase
label or schema rule changes. Prior fixtures, earlier schema majors, other
owners' availability and recorded consumer pin snapshots retain their original
bytes and identities.

## Validation and adoption

GitHub-hosted `Validate contracts` remains the schema, fixture, cross-reference
and pinned OpenAPI conformance gate. Local review used static source and diff
inspection, the SHA-256 of the exact tagged OpenAPI bytes, a standard-library
comparison of every catalog entry with the tagged registration, parity and
`PluginConfigBase` sources, and `git diff --check`. The release refresh
changes no validator, workflow, permissions or dependency pins.

Consumers targeting `v0.9.20` must stop sending unknown nested plugin config
keys, send `name` (and `namespace` where required) on policy `targetRefs`
attachments, and read `grpc-status` from framed pre-routing refusals. Each
consumer then qualifies its own pin/copy/checksum PR. A canonical Contracts
release alone does not change those pins, certify application integration or
publish another product.
