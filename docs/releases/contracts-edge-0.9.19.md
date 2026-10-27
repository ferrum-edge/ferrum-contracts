# contracts-edge-0.9.19 release record

`contracts-edge-0.9.19` holds the contracts for published Ferrum Edge
`v0.9.19`. The tag is the merge commit of its release PR. The
[GitHub release](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.19)
records the Contracts tag identity and publication time.

## Edge source

Edge `v0.9.19` points to `510ce7121c3d9754110d330a30a3bd9b7a7b278e`.
The [Edge release](https://github.com/ferrum-edge/ferrum-edge/releases/tag/v0.9.19)
was published at 07:01:07 UTC on 2026-10-27. Its assets, checksums, signed
container indices, provenance, SBOMs and application qualification belong to
that owner release. Publication facts come from the published GitHub release;
owner documentation captured before publication remains historical.
Every owner source used here is read with `git show v0.9.19:<path>` from the
Edge repository at that immutable tag.

Edge `v0.9.18` remains tagged at
`57966eb9d047378ef6ebf8aa97c94ebf96a38fa6` but was never published. Its
production ARM64 fat-LTO compiler exhausted host memory on attempts 2 and 3.
Edge `v0.9.19` carries those changes forward once and adds verified swap
capacity to the ARM64 producer without changing its optimization profile.
The owner records the evidence and recovery in
[`docs/releases/v0.9.18-arm64-recovery.md`](https://github.com/ferrum-edge/ferrum-edge/blob/510ce7121c3d9754110d330a30a3bd9b7a7b278e/docs/releases/v0.9.18-arm64-recovery.md)
and marks 0.9.18 as `TAGGED, NOT PUBLISHED` in its changelog. There is no
`contracts-edge-0.9.18`. This follows the 0.9.16/0.9.17 precedent: preserve the
failed publication's immutable owner tag and bind Contracts to the next
published owner release.

The tagged `openapi.yaml` has SHA-256
`610e2645961e7a5deca73468439be9c4a5b7070045099506c212a0a36b045e90`.

## Vocabulary and schema changes

All five vocabulary `edge_release` values and their Edge source entries pin
`v0.9.19` and its full commit. Values observed in other products retain those
products' recorded provenance. No canonical schema needs a new major.

- **Gateway headers.** Add `x-ferrum-peer-spiffe-id`, written to backend
  requests only with `spiffe_identity.forward_identity=true`. That hook first
  removes client copies with ASCII case-insensitive `_`/`-` equivalence, then
  writes the admitted identity when present. Forwarding defaults to false;
  the hook leaves the header unchanged when disabled. The shared folded
  `x-ferrum-*` request-trailer boundary always refuses client trailer copies.
  The independent `require_identity` and `allowed_trust_domains` options
  govern admission. Add the four gateway-asserted CUSTOM check headers:
  `x-ferrum-source-principal`, `x-ferrum-source-namespace`,
  `x-ferrum-source-service-account`, and `x-ferrum-request-principal`.
  These carry the authenticated source SPIFFE ID, its available Kubernetes
  components, and validated JWT `iss/sub`, respectively, to the authorization
  provider. Missing identity means an absent header. Provider admission
  refuses client/configured `x-ferrum-*` check-header sources, and the executor
  removes existing copies before stamping. These check assertions do not
  imply automatic backend forwarding.
- **Plugin catalog.** All 82 registered names, the two removed names,
  response-body producer membership, WebSocket framing membership and config
  pointers remain the same. Transcribe current registration/parity metadata:
  `stdout_logging` uses `keep_last_known_good`; `ai_token_metrics` priority
  becomes 4070; `request_transformer` includes WebSocket handshake headers and
  query parameters and names its contextual body hook. Authentication, mesh,
  rate-limiting, tracing, AI, WebSocket and SSE entries gain the owner's
  current lifecycle phases and rationales. In particular, `ws_frame_logging`
  records policy Close decisions and emits delivery observations after a
  successful destination send. Every per-plugin config-required and scope
  conditional is read from the tagged `PluginConfigBase`; the catalog now
  records `openapi_validator` as proxy-scoped.
- **Gateway errors.** The 19 `ErrorClass` values, nine header tokens, 25
  reserved HTTP metric labels and token-mapped rejection phases remain the
  same. Retain the corrected `connection_refused` prose: a typed rustls
  handshake error is `tls_error` only with setup-phase evidence and otherwise
  `connection_reset`; a reqwest pool cancellation remains
  `connection_pool_error`. The timeout handoff and hop-limit semantics remain
  those described in 0.9.17.
- **Attribution and egress.** `provisioned-by` names, bounds and open-set
  behavior are unchanged. Backend egress remains response `schema_version: 2`
  with classifier identifier `ferrum-private-reserved-v1`, the same scope and
  mode labels, evaluation-order vocabulary, local public-only guarantee and
  optional CP data-plane attestation. The CP's own policy is admission-only;
  reports remain DP self-descriptions, and publication still needs every
  expected serving DP. No classifier label or guarantee is invented here.
- **Admin schemas.** Re-read conditional backup v1, backend egress v2,
  deployment snapshot v2, mutation acknowledgement v1 and the current egress
  vocabulary schema at the owner tag and refresh their source metadata.
  Their wire rules remain unchanged. Original row/namespace/deployment-token
  authority, complete evidence and spec bytes, and explicit qualifying cleanup
  acknowledgements remain required. Open nested evidence is not a certificate
  of completeness or consumer DTO acceptance.
- **Diagnostic-ref freeze.** The tagged OpenAPI and `src/diagnostic_ref.rs`
  retain the existing v1 fields, reference/replica patterns, nine gateway
  tokens, mapped phases and open raw rejection-phase labels. Following
  `docs/release-process.md`, preserve canonical v1 byte for byte, including
  its historical provenance. Its SHA-256 is
  `11508c19f571b57be7e755b5f17409ebc73cd270debd015d1a4ea49a37950520`.
  This record binds the unchanged bytes to the v0.9.19 source verification.

## Shipping plugin admission and runtime rules

Every Edge-main behavior previously recorded in `docs/admin-contracts.md`
now ships in `v0.9.19`. The current OpenAPI pin contains those rules:

- Scoped operators cannot introduce gateway material/filesystem/native-library
  references outside the owner's admitted set, even when an `ns` claim is
  optional. The native-loader, command and gateway-file Kafka keys are refused
  for every token unless the process explicitly enables native config; scoped
  operators remain confined.
- Empty access-control allow-lists are refused. Claim-header maps gain bounds
  and reject reserved or duplicate backend-visible destinations with folded
  names. LDAP group-cache TTL, bounded JWKS provider sets, secret-valued OpenAPI
  bypass headers, mirror query-name admission, credentialed CORS restrictions
  and plugin resource/AI-pattern hard bounds are enforced.
- Transaction debugging and workload metrics use the new safe text/source
  declarations. Log-schema names refuse credential classes. Mirroring retains
  credential provenance through renames; MCP session headers are credential
  headers. Transaction-log metadata uses `[REDACTED]` outside the allowed set;
  spans omit disallowed gateway `mesh.*` attributes. Workload custom tags reach
  spans without the global metadata allowlist, with header/environment values
  redacted unless their source is declared safe.
- Security-header fields and configured overrides require recognized browser
  tokens. The later plugin hardening also governs duplicate backend policy
  spellings and quoted HSTS extensions.
- Ordinary plugin-config `PUT` and `DELETE` require `expected_proxy_ids`,
  including an explicit empty value when expecting no references. Missing,
  repeated or malformed input returns `400`; unexpected current associations
  return `412` without mutation. The namespace admission lease and supported
  backend transaction checks fence the comparison. A row ETag alone does not
  authorize detaching newly attached proxies. Standalone MongoDB retains its
  documented multi-document atomicity limit.

The pinned OpenAPI also carries the later production-launch plugin changes,
including ordered multi-location `key_auth`, RFC 9421 HMAC verification,
external-identity access rules, correlation-ID ownership, rate-limiting and
WebSocket bounds, and AI provider controls. These config schemas are referenced
at their exact owner document, rather than copied or approximated here. The
owner's tagged [upgrade guide](https://github.com/ferrum-edge/ferrum-edge/blob/510ce7121c3d9754110d330a30a3bd9b7a7b278e/docs/upgrade_guide.md)
and `CHANGELOG.md` describe the full migration and runtime requirements.

## Source paths and fixtures

All Edge paths in this section are at
`510ce7121c3d9754110d330a30a3bd9b7a7b278e`:

- Errors: `src/retry.rs`, `docs/error_classification.md`.
- Headers: `src/proxy/headers.rs`, `src/proxy/mod.rs`, `src/plugins/mod.rs`,
  `src/plugins/mesh/spiffe_identity.rs`, `src/plugins/mesh/ext_authz.rs`,
  `docs/plugins.md`, `docs/mesh.md`, `docs/plugin_execution_order.md`, the admin
  and deployment docs, and `openapi.yaml`; each entry records its own paths.
- Attribution: `src/admin/provisioning.rs`, `docs/admin_api.md`,
  `docs/hardening.md`, `openapi.yaml`.
- Catalog: `src/plugins/mod.rs`, `src/plugins/builtin_parity.rs`,
  `openapi.yaml` (`PluginConfigBase` and referenced config components).
- Egress: `src/admin/backend_egress_policy.rs`,
  `src/grpc/backend_egress_attestation.rs`, `src/config/env_config.rs`,
  `docs/admin_api.md`, `docs/cp_dp_mode.md`, `openapi.yaml`.
- Conditional/deployment schemas: `src/admin/conditional_snapshots.rs`,
  `preconditions.rs`, `backup.rs`, `deployment_mutations.rs`,
  `src/config/deployment_mutation.rs`, `db_backend.rs`, `db_loader.rs`,
  `mongo_store.rs`, `types.rs`, `docs/admin_backup_restore.md`,
  `docs/deployment_mutations.md`, `openapi.yaml`.
- Admission notes: `src/admin/crud.rs`,
  `src/admin/crud/scoped_references.rs`, `docs/admin_api.md`, `docs/plugins.md`,
  `docs/upgrade_guide.md`, `openapi.yaml`.

New fixtures copy the five mesh identity entries and four representative
changed plugin entries from the refreshed vocabularies. Each invalid fixture
changes exactly one field: availability loses its `v` prefix, or failure
policy becomes an unknown value. `fixtures/README.md` records the source and
`fixtures/invalid-expectations.json` records the required instance path and
keyword. Prior fixtures, earlier schema majors, other owners' availability and
recorded consumer pin snapshots retain their original bytes and identities.

## Validation and adoption

GitHub-hosted `Validate contracts` remains the schema, fixture, cross-reference
and pinned OpenAPI conformance gate. Local checks use isolated Python 3.13 with
the repository's hash-pinned Linux x86_64 dependencies, `python3 -I
ci/validate.py`, the exact tagged OpenAPI bytes and `git diff --check`. The
release refresh changes no validator, workflow, permissions or dependency pins.
The included bounded OpenAPI-download fix and its loopback tests are recorded
in the changelog.

Consumers targeting `v0.9.19` must adopt its plugin config/admission rules and
association parameter, then qualify their own pin/copy/checksum PRs. A canonical
Contracts release alone does not change those pins, certify application
integration or publish another product.
