# contracts-edge-0.9.15 release record

`contracts-edge-0.9.15` holds the contracts for Ferrum Edge `v0.9.15`. The tag
is the merge commit of the release PR; the
[GitHub release](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.15)
for the tag records its commit and publication time. Every Edge-owned file in
the tag reads the owner at `v0.9.15`.

## Edge source

The Edge `v0.9.15` tag points to `25b37395ff61bfea0f3ffd189d9011c4984fa755`, the merge of
[Edge #6103](https://github.com/ferrum-edge/ferrum-edge/pull/6103)
(first parent `b4f3b39863c4aeb1e32431cdc0d8b983d9ac1c07`, second parent
`ba667a64c9bf1a3289d49f98e5fb205f5c42d3a3`).
[GitHub release 407222520](https://github.com/ferrum-edge/ferrum-edge/releases/tag/v0.9.15)
was published at 20:11:03 UTC on 2026-10-08. Edge `v0.9.15` has no
`docs/releases/v0.9.15.md`; its `CHANGELOG.md` `[0.9.15]` section and the
upgrade guide's "Upgrading to 0.9.15" are the owner's release notes. Edge's
assets, digests and attestations are recorded in that Edge release, not here.

`openapi.yaml` at the tag has SHA-256
`f6c7d8b1d247060c4d0ae66e5c149ad3d76721addb8176eff45b6fc3d1b4d6b2`.

## Contract changes

No contract gets a new major, and no schema file changes its wire rules. The
changes are vocabulary values and descriptions, provenance, and new fixtures,
which [versioning.md](../versioning.md) allows within a major.

- **External identity header.** Edge
  [#6088](https://github.com/ferrum-edge/ferrum-edge/pull/6088) (issue #6082)
  sends `X-Consumer-Username` only for a gateway Consumer that the
  authentication flow mapped, and sends an external identity or display claim
  without a mapped Consumer as the new gateway-owned `X-Authenticated-Identity`.
  External authentication no longer maps a principal to a Consumer by matching
  a username, ID or custom ID. For `jwks_auth` and `oauth2_introspection` the
  display claim is the provider `consumer_header_claim`, then the global
  `consumer_header_claim`, then the provider's effective
  `consumer_identity_claim`. `X-Authenticated-Identity` follows the
  `x-consumer-*` rules: client copies are removed before any plugin runs,
  plugin copies are scrubbed before dispatch, `_` matches `-`, it is forbidden
  in request trailers, and it is refused as a configured header destination at
  config load. The two headers are never sent together. `gateway-headers.json`
  adds the `X-Authenticated-Identity` entry (availability `v0.9.15`) and
  records the narrower `X-Consumer-Username` and `X-Consumer-Custom-Id`
  meaning, the extended `x-consumer-` check and the `RequestContext` and
  `refresh_backend_gateway_assertion_headers` sources.
- **Connection nominations and assertion spellings.** Edge
  [#6090](https://github.com/ferrum-edge/ferrum-edge/pull/6090) (issue #6087)
  removes the fields a client's `Connection` header nominates at HTTP/1.1 and
  HTTP/3 ingress, before any plugin runs, and rewrites `Connection` to keep
  only `close` and the request hop-by-hop names. `Host`, `Content-Length`,
  `Expect`, `Forwarded`, the `X-Forwarded-*` fields, `X-Real-IP` and the
  configured `FERRUM_REAL_IP_HEADER` are protected. Gateway assertions are
  written afterwards, so a nomination cannot remove them, and a nominated
  `Authorization` is removed before authentication. `claim_headers`
  destinations, `x-geo-country` and `x-path-param-*` now match `_` as `-`
  when client values are removed. The vocabulary has no entry for `Connection`
  or the forwarding fields, and its v1 roles have none for a standard client
  header, so the rule is recorded in the `src/proxy/headers.rs` provenance
  note and the top-level description. The `X-Geo-Country` and `x-path-param-`
  entries record the `_`/`-` equivalence.
- **Route protocol admission.** The same change refuses a native gRPC or
  WebSocket request whose flavor's plugin view omits an authentication or
  admission plugin that the route's HTTP view runs: `403` (trailers-only
  `PERMISSION_DENIED` for native gRPC) with rejection phase
  `route_protocol_admission`, a new label in `src/diagnostic_ref.rs`
  `GATEWAY_REJECTION_PHASES`. `diagnostic-ref` v1 already admits it:
  `detail.rejection.phase` is an open label of at most 64 characters, and the
  OpenAPI `DiagnosticRef*` components are byte-identical to `v0.9.14`.
  `token_for_rejection_phase` maps the phase to no `X-Gateway-Error` token, so
  `detail.rejection_phase` and `gateway_error` stay null. A new valid fixture
  records the `all`-mode reference of the WebSocket refusal (`source:
  gateway`, no plugin, no `backend_target`), and an invalid fixture puts the
  label in `detail.rejection_phase`, which only carries token-mapped phases.
- **Plugin config schemas.** `PluginConfigBase`, the 82 registered built-ins,
  `REMOVED_PLUGIN_REGISTRATIONS` and `BUILTIN_PLUGIN_PARITY_META` are
  unchanged, so every catalog pointer stays and now resolves into the
  `v0.9.15` `openapi.yaml`. The components it reaches change: `LdapAuthConfig`
  drops `consumer_mapping` and stays closed, so a config that still sets it is
  refused (#6088); the `jwks_auth` and `oauth2_introspection` display claims
  select `X-Authenticated-Identity` (#6088); plugin-config environment
  references take a `FERRUM_PLUGIN_SECRET_<NAME>` name pattern with
  `maxLength` 256 (`api_chargeback_sink` `clickhouse.password_ref`,
  `ai_semantic_firewall` `provider.api_key_env`, `workload_metrics` Lightstep
  `access_token_env`/`accessTokenEnv`, `ProxyAlertsEnvName`), and the
  `ai_stream_router` `api_key` and `serverless_function` Azure/GCP fallback
  descriptions name that namespace
  ([#6089](https://github.com/ferrum-edge/ferrum-edge/pull/6089), issue
  #6086); `rate_limiting` adds `ipv6_prefix` (`1`–`128`, default `64`),
  `mcp_gateway` adds `sessions.max_sessions_per_principal` (minimum `1`,
  default `128`) and `body_validator` `grpc_max_decompressed_size_bytes` has
  minimum `1` ([#6079](https://github.com/ferrum-edge/ferrum-edge/pull/6079));
  and `soap_ws_security` `content_type.allow_mtom` describes strict MTOM
  framing with the first part as root
  ([#6077](https://github.com/ferrum-edge/ferrum-edge/pull/6077)). The
  catalog's `openapi.yaml` provenance note lists these changes.
- **Request-admission gating is not a catalog field.** #6090 adds
  `Plugin::gates_request_admission()`, which defaults to `is_auth_plugin()`.
  Among built-ins, `soap_ws_security`, `openapi_validator` in `block` mode,
  `mcp_gateway`, `request_deduplication` with `enforce_required`,
  `ai_prompt_shield`, `ai_rate_limiter`, `ai_tool_governor`,
  `ai_semantic_firewall` and `rate_limiting` with `mcp_tool_calls` gate on
  both flavors, `graphql` with a protection rule on native gRPC, and
  `a2a_gateway` with a deny policy on WebSocket. The answer depends on the
  instance's config and on the flavor views built for the route, so it is not
  a property of the plugin type; the catalog keeps its per-type `protocols`,
  and the owner's `docs/plugin_execution_order.md` "Protocol Support" is the
  reference.
- **Error vocabulary note.** `gateway-errors.json` notes that
  `route_protocol_admission` maps to no token. No class, token or meaning
  changes.

## Checked and unchanged

- `src/retry.rs`, `docs/error_classification.md`, `src/admin/provisioning.rs`,
  `src/plugins/builtin_parity.rs` and `src/admin/preconditions.rs` are
  byte-identical to `v0.9.14`. `ErrorClass`, `x_gateway_error_token_for_class`
  and `token_for_rejection_phase` are unchanged, so `gateway-errors.json` and
  `provisioned-by.json` only repin. The `src/plugins/mod.rs` changes are the
  `RequestContext` identity accessors, the HBONE relay field from
  [#6083](https://github.com/ferrum-edge/ferrum-edge/pull/6083) and
  `gates_request_admission()`; no registration changes.
- `diagnostic-ref` v1 keeps its frozen bytes. Its OpenAPI components are
  unchanged, and the only `src/diagnostic_ref.rs` change is the new phase
  label, which the open `phase` string already admits.
- Backend egress policy sources (`src/admin/backend_egress_policy.rs`,
  `src/grpc/backend_egress_attestation.rs` and the `openapi.yaml`
  components) are unchanged; `src/config/env_config.rs` adds only unrelated
  settings (`FERRUM_PER_IP_IPV6_PREFIX`,
  `FERRUM_HTTP3_CONNECT_UDP_MAX_SESSIONS_PER_IP`,
  `FERRUM_HTTP3_MAX_UNVALIDATED_HANDSHAKES`,
  `FERRUM_MESH_TENANT_TLS_FILE_ROOTS`). `backend-egress-policy` v2, the egress
  vocabulary and its v2 shape repin to `v0.9.15`.
- `src/admin/deployment_mutations.rs`, `src/admin/conditional_snapshots.rs`,
  `src/admin/backup.rs`, `src/config/deployment_mutation.rs`,
  `docs/deployment_mutations.md` and `docs/admin_backup_restore.md` are
  byte-identical to `v0.9.14`, and the snapshot and acknowledgement OpenAPI
  components are unchanged. The `src/config/{db_backend,db_loader,mongo_store,types}.rs`
  changes serve plugin-graph admission, consumer deltas and MongoDB batch
  attachments, not the snapshot or acknowledgement shapes.
  `admin-conditional-snapshot` v1, `admin-deployment-snapshot` v2 and
  `admin-deployment-mutation-acknowledgement` v1 repin to `v0.9.15` with
  unchanged rules.
- Admin API description changes have no contract file here.
  [#6094](https://github.com/ferrum-edge/ferrum-edge/pull/6094) (issue #6092)
  documents that a namespace-scoped `operator` gets `400` for an out-of-namespace
  `backend_tls_*` reference where the `ns` claim is enforced; these are proxy
  and upstream field descriptions in `openapi.yaml` and `docs/admin_api.md`,
  with no new status code or field.
  [#6065](https://github.com/ferrum-edge/ferrum-edge/pull/6065) documents that
  `POST /batch` and `POST /restore` attach a proxy-scoped plugin config to its
  proxy on MongoDB as on SQL. Neither changes the conditional backup metadata,
  the restore preconditions or the deployment profile.
- Edge `main` at `ffb264d5b7825bf2fb74863e833c90ddb4dc9fdb` adds h2 0.4.20 and
  change-log paging after `v0.9.15`. The paging change touches `db_backend.rs`,
  `db_loader.rs` and `mongo_store.rs`, pinned sources of `admin-deployment-snapshot`
  v2, but leaves the pinned functions unchanged, and no vocabulary cites those
  files, so no vocabulary carries a `main_branch_delta`.
- Other owners' schemas, availability notes and fixtures are unchanged.

## Fixtures and validation

`diagnostic-ref` gains one valid fixture (the `all`-mode reference of a
`route_protocol_admission` WebSocket refusal, derived from the owner's
`plugin_rejection` example) and one invalid fixture (the label in
`detail.rejection_phase`). `vocabulary-gateway-headers` gains one valid
fixture copied from this release's vocabulary (`X-Consumer-Username` and
`X-Authenticated-Identity`) and one invalid fixture whose `availability` is
not an Edge tag. `fixtures/README.md` lists each one, and
`fixtures/invalid-expectations.json` records the expected path and keyword of
each invalid fixture.

The `Validate contracts` workflow is the conformance gate. Workflow,
permissions, action pins, Python dependencies and `ci/validate.py` are
unchanged.

## Consumers

A consumer pinned to `contracts-edge-0.9.14` keeps validating Edge `v0.9.14`
payloads, and every schema in this release accepts the same payloads. What
changes is header meaning on Edge `v0.9.15`: a backend or consumer that reads
`X-Consumer-Username` for a JWKS, OIDC, introspection, LDAP or SOAP identity
must read `X-Authenticated-Identity` for the external display value, and must
not treat that value as proof of a mapped Consumer. A consumer that resolves
diagnostic references should expect `rejection.phase:
"route_protocol_admission"` with no `X-Gateway-Error` token. A consumer that
validates plugin configs against the catalog's pinned `openapi.yaml` sees the
`v0.9.15` config rules, including the refused LDAP `consumer_mapping` and the
`FERRUM_PLUGIN_SECRET_<NAME>` environment references. Consumer pins are
recorded in [adoption.md](../adoption.md).
