# Edge admin snapshot and egress contracts

This reference covers Edge's authoritative consumer verification, conditional
backup snapshots and restore preconditions, namespace-scoped admin
authorization and process backend egress discovery. The schemas check JSON
shape and owner-derived invariants only; canonical metadata alone does not
patch a product advisory or qualify a consumer integration. Plugin
configuration admission changes reached through the plugin catalog's pinned
`openapi.yaml` are in [plugin-config-admission.md](plugin-config-admission.md).

| Contracts release | Edge source | Change to this surface |
|---|---|---|
| [0.9.11](releases/contracts-edge-0.9.11.md) | `v0.9.11`, `c764084b3b51c3f7ffde268c039688d35e49c553` | Consumer verification, conditional backup metadata and namespace restore, process egress discovery (`backend-egress-policy` v1) |
| [0.9.12](releases/contracts-edge-0.9.12.md) | `v0.9.12`, `0d917701b63ef38210c49df830f48cf0457cbc7d` | Separate [deployment-v1 profile](deployment-contracts.md); backup/egress wire semantics unchanged. Deployment authority does not replace namespace/row tags or authorize whole restore |
| [0.9.13](releases/contracts-edge-0.9.13.md) | `v0.9.13`, `9b83115de7ec23ab51ec4feae6bed65e596db425` | Namespace token becomes a keyed MAC over a bounded snapshot digest (backup metadata stays v1); egress response moves to `schema_version: 2` (`backend-egress-policy` v2) |
| [0.9.14](releases/contracts-edge-0.9.14.md) | `v0.9.14`, `9bd4d5f9caa4ebe8f0ea13e76d8a6e2172eaca7d` | Optional CP `data_plane_attestation` within `schema_version: 2`; backup `ETag` documented as a namespace state token |
| [0.9.15](releases/contracts-edge-0.9.15.md) | `v0.9.15`, `25b37395ff61bfea0f3ffd189d9011c4984fa755` | Backup/egress sources byte-identical to `v0.9.14`; MongoDB batch/restore and TLS-reference [write rules](#admin-authorization-and-write-rules) |
| [0.9.17](releases/contracts-edge-0.9.17.md) | `v0.9.17`, `669c574c1d1e88e84dccb26a8159939e6694644d` | Wire shapes unchanged; [bounded-token authorization](#admin-authorization-and-write-rules) |
| [0.9.19](releases/contracts-edge-0.9.19.md) | `v0.9.19`, `510ce7121c3d9754110d330a30a3bd9b7a7b278e` | Wire shapes unchanged; [material-reference default-deny](#admin-authorization-and-write-rules) and the plugin-config [`expected_proxy_ids`](#authoritative-verification-and-replacement) precondition |
| [0.9.20](releases/contracts-edge-0.9.20.md) | `v0.9.20`, `e4a606a00352674daaef08636e3e359e6c48ba18` | Wire shapes and admin rules unchanged: `src/admin/` and the backup, egress and deployment OpenAPI components are byte-identical to `v0.9.19`; [closed nested plugin configs](plugin-config-admission.md#closed-nested-plugin-configs) |
| [0.9.21](releases/contracts-edge-0.9.21.md) | `v0.9.21`, `f9915358c8032214f4034a17c28cdf72d14006c3` | Wire shapes unchanged; `jwks_source` TLS material, `/admin/tls/jwks` admission, cross-namespace managed TLS delete guards, conditional consumer credential `If-Match`, explicit `If-Match` refusal on `POST`/`DELETE /api-specs`, viewer-key `ETag` withholding, `/config/export` fingerprint key, `charges:collect` scope and ConfigSync revision 6 |

## Admin authorization and write rules

These are owner runtime rules and OpenAPI descriptions, not envelope fields or
vocabulary values.

From Edge `v0.9.15`, on MongoDB, `POST /batch` and `POST /restore` (conditional
or not) attach a `scope: proxy` plugin config to its proxy in the same write,
as SQL already did (Edge #6065, #6074; rows written earlier are not
rewritten), and the owner documents that both paths reject a `proxy_id` that
does not exist in the namespace with `400` before anything is written. Where
the admin `ns` claim is enforced, a namespace-scoped `operator` that
introduces a `backend_tls_*` reference outside inline PEM, `system://` or a
`k8s://` Secret in the addressed namespace gets `400` (Edge #6094, issue
#6092); these are proxy and upstream field descriptions in the pinned OpenAPI.

From Edge `v0.9.17`, a present JWT `ns` claim always bounds the caller; the
namespace-scoped flag controls whether a claim is required, not whether a
present claim is enforced. Fleet-global routes and metrics return 403 for
bounded tokens, including allowlisted callers. Tenant observability routes
retain their tier restrictions. A cached read with no authoritative fallback
proof of absence returns 503 rather than a false 404.

From Edge `v0.9.19` (Edge PR
[#6316](https://github.com/ferrum-edge/ferrum-edge/pull/6316), issue #6092,
owner commit
[`d5417cd723120995666a7a14c6a4bc9022ba86a9`](https://github.com/ferrum-edge/ferrum-edge/commit/d5417cd723120995666a7a14c6a4bc9022ba86a9)),
gateway material references are default-deny for an `operator` token that
carries an `ns` claim, even when `FERRUM_ADMIN_REQUIRE_NAMESPACE_CLAIM=false`.

- **TLS material** admits only inline PEM, `system://` or a `k8s://` Secret
  in the addressed namespace. This covers proxy and upstream
  `backend_tls_client_cert_path`, `backend_tls_client_key_path` and
  `backend_tls_server_ca_cert_path`, `mesh_route_dispatch`
  `rules[].destination.backend_tls.{client_cert_path,client_key_path,server_ca_cert_path}`,
  `udp_logging` `dtls_cert_path`, `dtls_key_path` and `dtls_ca_cert_path`, and
  `soap_ws_security` `x509_signature.trusted_certs[]` and
  `saml.trusted_signing_certs[]`.
- **Gateway filesystem paths and native library settings** are refused with
  `400` whatever the value. This covers `kafka_logging`
  `ssl_certificate_location`, `ssl_key_location` and `ssl_ca_location`, and
  every `kafka_logging` `producer_config` key outside the owner's reviewed
  tuning-only list. It also covers `api_chargeback_sink`
  `clickhouse.tls.ca_file`, `clickhouse.tls.client_cert_file`,
  `clickhouse.tls.client_key_file` and `spool.dir`, the
  `ai_response_guard` and `ai_transcript_audit` `grpc.descriptor_path`,
  `body_validator` `protobuf_descriptor_path`, and `geo_restriction`
  `db_path`.
- **Non-built-in (custom) plugins**: such a token cannot introduce a custom
  plugin configuration or change an existing one's `plugin_name` or
  `config`. Other updates to an existing custom plugin (for example
  `enabled`) remain subject to ordinary validation.

A value already stored at the same field path (same array index) stays
admitted, and `admin` tokens are unaffected. The owner keeps the complete
classified set in
[`src/admin/crud/scoped_references.rs`](https://github.com/ferrum-edge/ferrum-edge/blob/d5417cd723120995666a7a14c6a4bc9022ba86a9/src/admin/crud/scoped_references.rs);
the refusal is `tls_reference_refusal` in
[`src/admin/crud.rs`](https://github.com/ferrum-edge/ferrum-edge/blob/d5417cd723120995666a7a14c6a4bc9022ba86a9/src/admin/crud.rs).
These rules are unchanged in Edge `v0.9.20`.

From Edge `v0.9.21` (`f9915358c8032214f4034a17c28cdf72d14006c3`), Edge PR
[#7373](https://github.com/ferrum-edge/ferrum-edge/pull/7373) (issue #7277,
owner commit
[`374297514e3b9e7ec6dc7782fe16c7e8eabddd6f`](https://github.com/ferrum-edge/ferrum-edge/commit/374297514e3b9e7ec6dc7782fe16c7e8eabddd6f))
registers `jwks_auth` and `oidc_relying_party` `providers[].jwks_source` as
TLS material. The field admits only a `managed://` reference to an
admin-managed JWKS record (`managed://jwks/<id>#jwks`), which a
namespace-bounded operator token cannot introduce. The same PR narrows
`POST`/`PUT /admin/tls/jwks`: `jwks_json` is admitted only with at least one
usable signing key, at most 1 MiB and 256 keys, and no duplicate usable
`kid`. The record checks apply to enabled configurations only. An enabled
plugin write, `POST /batch` or `POST /restore` row whose `jwks_source`
names a missing, wrong-kind or keyless record gets `400`. An enabled API-spec
`x-ferrum-plugins` entry gets `422` (Edge PR
[#7378](https://github.com/ferrum-edge/ferrum-edge/pull/7378)). A disabled
configuration is stored without the check, so it may be staged before its
JWKS record exists. `DELETE /admin/tls/jwks/{id}` returns `409` while an
enabled `jwks_auth` or `oidc_relying_party` configuration, or another
inventory reference, names the record; a disabled configuration does not
block the deletion. See [plugin-config-admission.md](plugin-config-admission.md#edge-v0921-admission-and-config-changes)
for the config schema changes.

From Edge `v0.9.21`, these admin rules also apply:

- **Managed TLS deletion across namespaces** (Edge PR
  [#7412](https://github.com/ferrum-edge/ferrum-edge/pull/7412), issue #7394,
  owner commit
  [`5f181df099adb0ba37f6d8cce1c6bb94e38c76b3`](https://github.com/ferrum-edge/ferrum-edge/commit/5f181df099adb0ba37f6d8cce1c6bb94e38c76b3)).
  `DELETE` of a managed certificate, CA bundle, CRL, OCSP response or JWKS
  record, or of an ACME certificate, returns `409` with the referencing
  resources in `used_by` while any configuration names the record. On a node
  with a configuration store (database and CP modes) the check covers every
  namespace in that store, not only the namespaces the node serves, and
  `used_by[].namespace` names the namespace of a reference found there.
  Disabled plugin configurations hold no reference. An unreadable store, a
  lapsed admission fence or a changed store topology is `503`. The delete
  holds every listed namespace's config admission lease until the record is
  removed, so configuration writes wait meanwhile; a first write into a
  namespace that has no rows can still race it.
- **Conditional credential writes and `/api-specs` `If-Match` refusal** (Edge
  PRs [#7412](https://github.com/ferrum-edge/ferrum-edge/pull/7412) and
  [#7459](https://github.com/ferrum-edge/ferrum-edge/pull/7459), issues #7393
  and #7439). `PUT`, `POST` and `DELETE /consumers/{consumer_id}/credentials/{cred_type}`
  and `DELETE /consumers/{consumer_id}/credentials/{cred_type}/{index}` take an
  optional `If-Match` with the Consumer's own `ETag` from
  `GET /consumers/{id}`. Any change to the Consumer since that read returns
  `412` and writes nothing; omitting the header keeps the write
  unconditional. `POST /api-specs` and `DELETE /api-specs/{id}` explicitly
  refuse `If-Match` with `400` before any lookup, including with the `ETag`
  from `GET /api-specs/{id}` (only `PUT /api-specs/{id}?conditional=true`
  accepts a `deployment-v1` token). The `If-Match` entry in
  `vocabularies/gateway-headers.json` records both rules.
- **Primary-secret detail** (Edge PR
  [#7413](https://github.com/ferrum-edge/ferrum-edge/pull/7413),
  GHSA-crqx-mp2f-v8c8 and GHSA-jjvr-vvwv-8qmh, owner commit
  [`45403deabb555a38306ff72dd766e180e785a18f`](https://github.com/ferrum-edge/ferrum-edge/commit/45403deabb555a38306ff72dd766e180e785a18f)).
  A token verified by `FERRUM_ADMIN_JWT_VIEWER_SECRET` receives no row
  `ETag`, and only a fleet-wide token verified by `FERRUM_ADMIN_JWT_SECRET`
  sees a non-null CP/DP trust `active_generation` on `/health` and `/status`.
  `GET /config/export` fingerprints
  are keyed by the new `FERRUM_ADMIN_CONFIG_EXPORT_FINGERPRINT_SECRET` (at
  least 32 characters, different from the admin, viewer and CP/DP JWT
  secrets), never by `FERRUM_ADMIN_JWT_SECRET`; without it the key is random
  per process, so fingerprints are not comparable across restarts or
  replicas. Only a token whose `scope` claim grants `charges:collect` is a
  billing collector on `GET /charges`: only its delivered responses count
  toward the two hand-offs that let an idle row be evicted. Every other
  read, including any viewer-key token, has no side effect.
- **Restore `api_specs` section and rollback guard** (Edge #7218). `POST /restore`
  retires `api_specs.section_version: "1"` and empty `resource_hash` values;
  an `incomplete` restore rollback retains the namespace admission guard until
  manual recovery.

**Unreleased on Edge `main`** (checked at
[`e333ba3fe51ffed19ce3b0a53140ba4340707589`](https://github.com/ferrum-edge/ferrum-edge/commit/e333ba3fe51ffed19ce3b0a53140ba4340707589),
through Edge PR [#7533](https://github.com/ferrum-edge/ferrum-edge/pull/7533),
the 1.0.0 release-notes refresh on top of Edge PR
[#7531](https://github.com/ferrum-edge/ferrum-edge/pull/7531), which prepares
version `1.0.0`; not tagged; the items below were first
recorded at
[`e837270d4b6c1c9756b80400d2a8e2e14b176ce4`](https://github.com/ferrum-edge/ferrum-edge/commit/e837270d4b6c1c9756b80400d2a8e2e14b176ce4)
through Edge PR [#7491](https://github.com/ferrum-edge/ferrum-edge/pull/7491)
unless they name a later PR; not in published `v0.9.21`; the versioned schemas
in this repository —
`admin-conditional-snapshot` v1, `admin-deployment-snapshot` v2,
`admin-deployment-mutation-acknowledgement` v1 and `backend-egress-policy` v2 —
keep unchanged wire shapes):

- **MongoDB `api_specs` BSON limits and restore validation**. Edge `v0.9.21`
  already checked `api_specs` documents against MongoDB's ~15 MiB BSON limit
  only after `bson::to_vec` succeeded: documents over ~15 MiB that serialized
  within BSON's 16 MiB ceiling returned `413` on unconditional `POST`/`PUT /api-specs`,
  `409` on conditional `PUT /api-specs/{id}?conditional=true`, and `503` on
  conditional `POST /restore?confirm=true` (where the check ran after local
  generation pins and leases), whereas documents whose binary fields exceeded
  BSON's 16 MiB serialization ceiling failed serialization first (`500` on
  unconditional `POST`/`PUT`, `503` `durable: "not_committed"` on conditional
  `PUT`, and `503` on conditional `POST /restore`). Edge `main` adds a raw-blob
  size pre-check and classifies BSON serialization size failures so all
  oversized cases reach `413` or `409`; moves the conditional
  `POST /restore?confirm=true` (with `If-Match`) preflight check ahead of local
  generation pins and mTLS admission leases and maps the typed size error to
  `413`; and adds an in-transaction check on conditional
  `PUT /api-specs/{id}?conditional=true` after merging retained unknown BSON
  fields, returning `409` (`durable: "not_committed"`, `live: "unconfirmed"`,
  `recovery_cleanup_authorized: false`) if the merged document exceeds the limit
  even when the incoming spec passed preflight (see
  [deployment-contracts.md](deployment-contracts.md#explicit-acknowledgement-and-retained-recovery-state)).
  `POST /restore` also validates `x-ferrum-proxy.plugins` association
  declarations on `api_specs` items with the same fail-closed parser
  `PUT /api-specs/{id}` uses (and both ordinary and conditional
  `PUT /api-specs/{id}` now abort before writing with `500` — returning a
  generic `500` error body without a `deployment-v1` acknowledgement on the
  conditional path — if decompressing the existing stored spec or parsing its
  `x-ferrum-proxy.plugins` declaration fails, where `v0.9.21` logged the error
  and continued with an empty association set; see
  [deployment-contracts.md](deployment-contracts.md#explicit-acknowledgement-and-retained-recovery-state)),
  marks `ApiSpecBackupItem.resource_hash` required in `openapi.yaml`, fails
  closed on conflicting repeated query flags (such as
  `?confirm=true&confirm=false`), and classifies corrupt/undecodable stored
  `api_specs` rows detected while capturing the unconditional restore's
  pre-clear rollback snapshot as `500` with `failure_class: "data_integrity"`
  before any deletion (whereas a corrupt stored `api_specs` row or persisted
  external-reference snapshot on the conditional backup/restore snapshot load
  returns `503` before any deletion). For unconditional
  restore failures, Edge `v0.9.21` emitted `503`
  `rollback: "not_needed_after_intervening_write"` for every failed clear
  followed by an intervening namespace lease — including ambiguous and
  potentially partial clears that retained the namespace admission guard and
  required manual recovery — and `503`
  `rollback: "skipped_after_intervening_write"` for an interrupted import
  rollback after an intervening lease. Edge `main` reserves `503`
  `rollback: "not_needed_after_intervening_write"` strictly for definitive
  atomic clear aborts (nothing deleted, no manual recovery required); emits
  `503` `rollback: "unknown_clear_outcome"` both when another writer acquired
  the lease and when admission cannot be reacquired after an ambiguous clear
  (guard retained, manual recovery required); and also emits `503`
  `rollback: "skipped_after_intervening_write"` (in addition to the existing
  interrupted-import-rollback case) when a potentially partial non-atomic clear
  loses the lease to an intervening writer (guard retained, manual recovery
  required).
- **API-spec admission refusals**. `POST /api-specs` and `PUT /api-specs/{id}`
  reject non-object (positional) `x-ferrum-plugins` entries and the reserved
  `$serde_json::private::RawValue` key at any nesting depth in declared
  `x-ferrum-plugins` `config` subtrees or generated/merged `x-ferrum-validate`
  / `x-ferrum-mcp` plugin configs with `400 MalformedExtension`. External-`$ref`
  admission also applies the 500,000-node ceiling to external JSON documents
  (`400 InvalidJson`, where `v0.9.21` used `serde_json::from_slice` without a
  parsed-node ceiling), enforces a 120-container document nesting depth ceiling
  (`400 InvalidJson`/`InvalidYaml`), enforces aggregate normalized (128 MiB)
  and compressed (64 MiB) snapshot caps (`422 SchemaTooLarge`), and extends
  `v0.9.21`'s disallowed-media-type allowlist with duplicate `Content-Type`
  header rejection and full media-type syntax validation (including parameters),
  returning `422 SchemaReference` for disallowed, malformed or repeated
  `Content-Type` headers.
- **API-spec conditional `GET` caching, content negotiation and read
  backpressure**. `GET /api-specs/{id}` and `GET /api-specs/by-proxy/{proxy_id}`
  read every `Accept` and `If-None-Match` header field line (`v0.9.21` read only
  the first) and give `application/*` precedence over `*/*` in `Accept`
  negotiation (so `Accept: application/*;q=0, */*;q=1` now returns `406` where
  `v0.9.21` served the stored representation). Verbatim representation `ETag`
  values (`"<content_hash>-json"` / `"<content_hash>-yaml"`) are unchanged from
  `v0.9.21`, whereas format-converted responses change from
  `"<content_hash>-<target>"` to `"<content_hash>-<target>-from-<stored>-v1"`
  (so cached `ETag`s for converted representations stop matching after upgrade
  and their `If-None-Match` revalidations no longer return `304`). Exact
  `If-None-Match` matches are evaluated before the recorded-size check and
  short-circuit to `304` from metadata without consuming codec slots or
  per-connection buffered response budget (even if the row's recorded
  `uncompressed_size` exceeds the decompression cap); otherwise (for `*`,
  non-matching tags or ordinary reads), a stored spec already known to exceed
  the decompression cap returns `500` before the connection budget is checked,
  while verbatim `If-None-Match: *` within the decompression cap short-circuits
  to `304` from metadata. Cross-format `If-None-Match: *` defers `304` until
  bounded conversion validation succeeds, and once decode or conversion begins
  a malformed spec or output exceeding the decompression cap returns `500` even
  if the connection budget runs out. When the per-connection buffered response
  budget is the blocking condition — during preflight, pre-decode reservation
  growth, or when valid content within the decompression cap exhausts the
  budget during gzip decoding or format conversion — ordinary reads and
  cross-format `If-None-Match: *` return `503` with `Retry-After: 1`.
- **`If-Match` refusal precedence, TLS rotation reporting and Admin OpenAPI
  alignment**. Where `v0.9.21` already checked the required role first on
  body-consuming mutating routes (and on `/api-specs` routes via their own
  dispatch arms), Edge `main` extends role-before-refusal to bodyless mutating
  routes that reach the shared refusal (such as
  `POST /backend-capabilities/refresh` and `POST /mesh/config-revision/reset`),
  returning `403` before refusing an unsupported `If-Match` header or
  unsupported deployment mode — for example, a `viewer` sending `If-Match` on
  `POST /backend-capabilities/refresh` now receives `403` where `v0.9.21`'s
  shared header refusal returned `400`, while an authorized caller on an
  unsupported route still receives `400`. When `POST /admin/tls/rotate/all`
  queues independent material-set watcher reloads and gateway SVID reload then
  fails, Edge `main` includes those already-queued surfaces in
  `accepted_surfaces` on the error response body (where `v0.9.21` returned the
  SVID error alone). The `/live`, `/health` and `/status` probes answer only
  `GET` and `HEAD` at runtime (`v0.9.21` dispatched them on the path alone, so
  any method reached them); a probe that used another method no longer reaches
  the probe handler and must switch to `GET` or `HEAD`. `openapi.yaml` adds
  `HEAD` for the three probes, `GET /consumers/{id}/verification` documents its existing
  `Cache-Control: no-store` response header, and `DeploymentSnapshot` explicitly
  types `api_specs[].id` and `api_specs[].proxy_id` as `string`.
- **Database outage mapping and port-scoped `listen_path` conflicts** (Edge PRs
  [#7484](https://github.com/ferrum-edge/ferrum-edge/pull/7484) and
  [#7485](https://github.com/ferrum-edge/ferrum-edge/pull/7485)). Transient
  database errors on `/api-specs` (such as pool timeout/closed or connection
  refused) return `503` (`{"error":"Database temporarily unavailable"}`)
  instead of `500`, and `listen_path` uniqueness is scoped by `listen_port`
  (affecting `409` route-conflict checks on proxies, API specs and batch
  writes).
- **Closed nested objects and JSON-object request bodies** (Edge PRs
  [#7520](https://github.com/ferrum-edge/ferrum-edge/pull/7520) and
  [#7524](https://github.com/ferrum-edge/ferrum-edge/pull/7524)). Edge
  `v0.9.21` already refused unknown keys in top-level resources and in some
  nested objects (stream `stream_match` criteria and arms, plugin trigger
  objects, and the mesh policy, authentication, telemetry and VirtualService
  route objects), but silently ignored them in the objects these PRs close.
  Edge `main` refuses them in every nested proxy
  and upstream object (`health_checks` and its `active`/`passive` blocks,
  `targets[]`, `service_discovery` and its provider objects, `subsets[]` and
  their `traffic_policy`, `port_overrides`, `locality_lb_setting`,
  `hash_on_cookie_config`, backend TLS and TCP keepalive settings,
  `circuit_breaker`, `retry` and its `backoff` variants, and `plugins[]`
  associations), in every native mesh resource object, and in the managed TLS,
  ACME, namespace, `/admin/tls/validate` and `/mesh/egress-scope/test` request
  bodies, which must also be JSON objects (a positional array is refused).
  Admin `POST`/`PUT` and `/batch` return `400` naming the key; `POST /restore`
  decodes the typed resources (proxies, consumers, plugin configs, upstreams)
  before deleting anything and refuses a backup carrying one with `400`, so
  nothing is restored; `POST`/`PUT /api-specs` refuse one in
  `x-ferrum-proxy`/`x-ferrum-upstream`; and in database and CP mode a stored
  row carrying one fails to load (MongoDB projects stored `plugins[]`
  associations onto `plugin_config_id` first). Stored API-spec documents in a
  backup's `api_specs.items` are copied without full extension admission
  (restore only checks that each `x-ferrum-proxy.plugins` entry is an object
  with a string `plugin_config_id`), so a stale `x-ferrum-*` key inside a
  stored spec restores successfully and is refused only when that spec is
  next submitted; review and re-submit source spec documents separately, even
  after a successful rehearsal restore. `health_checks.passive`
  drops `gateway_error_codes` and `split_external_local_origin_errors`
  (#7520). `labels`, plugin `config` and consumer `credentials` stay open.
  `openapi.yaml` marks the closed objects `additionalProperties: false`. The
  `admin-deployment-snapshot` v2 schema here keeps its resource objects open
  (`additionalProperties: true`) and `admin-conditional-snapshot` v1 carries
  only ETags, so neither changes; the owner's admission rules decide.
- **ConfigSync protocol revision 8** (Edge PRs #7520 and #7524). The build
  identity becomes `1.0.0+configsync.r8`: revision 7 removes the two
  passive-health fields and closes the passive object, revision 8 closes the
  other nested proxy, upstream and mesh objects. A `v0.9.21` peer
  (`0.9.21+configsync.r6`) is refused at `Subscribe`, and a `0.9.x` mesh data
  plane is refused at `MeshSubscribe`, so control planes and data planes must
  run the same build.
- **Database rebuild for `1.0.0`** (Edge PR
  [#7523](https://github.com/ferrum-edge/ferrum-edge/pull/7523)). The SQL
  `V001` baseline gets a new frozen identity, so a `1.0.0` binary refuses every
  SQL database created by a `0.9.x` release; the supported upgrade, also for
  MongoDB, is a fresh database populated with `POST /restore` from
  per-namespace `GET /backup` exports, following Edge's
  [rebuild procedure](https://github.com/ferrum-edge/ferrum-edge/blob/e333ba3fe51ffed19ce3b0a53140ba4340707589/docs/upgrade_guide.md#every-09x-database-is-rebuilt-and-restored-7523).
  A backup never carries the namespace registry row (description and
  timestamps), so the registry is recorded (`GET /namespaces`,
  `GET /namespaces/{name}`) and recreated (`POST /namespaces`, or
  `PUT /namespaces/{name}` for an existing one such as `ferrum`) before the
  restores; a registered namespace with no resources comes back only through
  that step. The backup *envelope* does not change, but the nested resource
  payloads `1.0.0` accepts are narrower: an export from `v0.9.21` whose
  upstreams still carry `gateway_error_codes` or
  `split_external_local_origin_errors` (which `v0.9.21` serialized when set),
  or any other key in a newly closed object, is refused by `POST /restore`
  with `400` before anything is restored. Remove those keys from the stored
  resources on `0.9.21` before the final export, and rehearse the restore on a
  scratch `1.0.0` database.
- **Runtime timestamp range** (Edge issue #7419 phases, PRs
  [#7511](https://github.com/ferrum-edge/ferrum-edge/pull/7511),
  [#7512](https://github.com/ferrum-edge/ferrum-edge/pull/7512),
  [#7513](https://github.com/ferrum-edge/ferrum-edge/pull/7513),
  [#7516](https://github.com/ferrum-edge/ferrum-edge/pull/7516),
  [#7517](https://github.com/ferrum-edge/ferrum-edge/pull/7517) and
  [#7527](https://github.com/ferrum-edge/ferrum-edge/pull/7527)). Parsed
  timestamps are held as UTC instants in years `-9999..=9999`, and a leap
  second (`:60`) is stored as the following second. An instant that `v0.9.21`
  (chrono) accepted outside that range, after conversion to UTC, now takes the
  site's existing invalid-timestamp path: the `GET /admin/tls/events` `since`
  filter returns `400` (its `invalid since timestamp: ` detail text changed;
  status and envelope did not), `transaction_debugger` refuses such a
  `capture_expires_at` (for example `9999-12-31T23:30:00-01:00`, which is
  UTC year 10000), `response_caching` treats such an HTTP date as
  unparseable, and `soap_ws_security` refuses it (a `9999-12-31T23:59:60Z`
  leap second is out of range). From #7527, a config document (file,
  backup, ConfigSync snapshot) whose `loaded_at`, or a ConfigSync delta whose
  `poll_timestamp`, is outside the range fails to decode instead of loading;
  a ConfigSync envelope version outside it is refused as unparseable; and a
  mesh slice version outside it is treated like any unparseable slice
  version. Rendered in-range timestamps, and the wire and storage text of these
  stamps, are byte-identical. Source: Edge `CHANGELOG.md` and
  `docs/upgrade_guide.md` at the commit above, as refreshed by Edge PR
  [#7533](https://github.com/ferrum-edge/ferrum-edge/pull/7533).

## Owner sources and artifact scope

The owner is `ferrum-edge/ferrum-edge`. Read the following paths at the full
`v0.9.11` commit `c764084b3b51c3f7ffde268c039688d35e49c553`, never a
consumer's copy:

- [`openapi.yaml`](https://github.com/ferrum-edge/ferrum-edge/blob/c764084b3b51c3f7ffde268c039688d35e49c553/openapi.yaml):
  `/consumers/{id}/verification`, `/backup`, `/restore`, `/backend-egress-policy`;
  parameters `IfMatch`/`NamespaceIfMatch`, header `ResourceETag`, and schemas
  `ConsumerVerification`, `ConditionalBackupMetadata`, `ResourceETagMap`,
  `BackupResponse`, `RestoreRequest`, `BackendEgressPolicyResponse`.
- [`docs/admin_api.md`](https://github.com/ferrum-edge/ferrum-edge/blob/c764084b3b51c3f7ffde268c039688d35e49c553/docs/admin_api.md)
  and [`docs/admin_backup_restore.md`](https://github.com/ferrum-edge/ferrum-edge/blob/c764084b3b51c3f7ffde268c039688d35e49c553/docs/admin_backup_restore.md).
- `src/admin/{conditional_snapshots,preconditions,crud,backup,backend_egress_policy,mod}.rs`
  and `src/config/{db_backend,db_loader,mongo_store,batch_atomicity,env_config}.rs`.

`schemas/admin-conditional-snapshot/v1.schema.json` transcribes only the
`conditional` metadata member of a backup. It requires `namespace_etag` and
all four maps in `row_etags`: `proxies`, `consumers`, `upstreams`,
`plugin_configs`. Empty maps are valid. Tokens must have quoted strong
entity-tag syntax and are opaque. A schema cannot verify their keyed MAC,
freshness, resource/namespace binding, authorization or snapshot coherence.
Fixtures contain illustrative tokens and no credentials.

The full backup, consumer verification and restore body shapes remain in the
pinned owner OpenAPI, including the historical credential fields allowed by
`ConsumerVerification`. This release does not substitute a narrower
credential model or validate authorization as JSON. `ETag` and `If-Match` are
standard HTTP headers; `gateway-headers.json` records Edge's admin semantics.

## Authoritative verification and replacement

| Route | Successful behavior | Refusals |
|---|---|---|
| `GET /consumers/{id}/verification` | `200`: admin-role, namespace-authorized read of the complete stored consumer and matching strong row `ETag`; security audit admission before response; `Cache-Control: no-store`; no cached fallback | `400` invalid input; `401` missing/invalid JWT; `403` role/namespace denial; `404` absent consumer; `503` unavailable authoritative state, tag key or audit admission |
| `GET /backup?conditional=true` | `200`: full unfiltered primary transaction snapshot; exact stored consumer fields; all four row-tag maps; header `ETag` equals `conditional.namespace_etag`; audit admission before response; `Cache-Control: no-store`; no cached fallback | `400` invalid opt-in/filter/namespace; `401` authentication; `403` authorization; `501` unsupported MongoDB topology; `503` unavailable authoritative snapshot, tag key or audit admission; `507` (v0.9.13) canonical representation over 64 MiB |
| `POST /restore?confirm=true` with namespace `If-Match` | Atomic compare and complete replacement in one transaction, including empty replacement and lease entry/commit fences; existing restore/live-apply response semantics; no new response `ETag` | `412` stale or weak-only tag (from v0.9.13, also any tag issued by v0.9.12 or earlier); `400` malformed/empty header or wildcard; `501` unsupported topology; `503` unavailable state/lease; `507` (v0.9.13) canonical representation over 64 MiB, nothing applied; existing authentication, admission, body-size, confirmation, conflict and live-apply failures still apply |

Row tags cover the complete stored row, including privately verified
credentials, rather than redacted response bytes. Ordinary consumer reads and
admin-only verification issue the same row tag. Use a row tag for `PUT`/`DELETE`
of its resource on `/proxies/{id}`, `/consumers/{id}`, `/upstreams/{id}` or
`/plugins/config/{id}`. Row `*` checks existence; weak tags never match, strong
lists match any member, malformed/empty headers return `400`. Comparison and
write serialize under the namespace admission lease across admin writers.
Cached row reads and write responses carry no tag: read the accepted state again.

From Edge `v0.9.19` (Edge PR #6744, forge-ops issue #569),
`PUT`/`DELETE /plugins/config/{id}` additionally require the
`expected_proxy_ids` query parameter: a comma-separated list of every proxy
the caller expects to reference the configuration (present-but-empty expects
none; absent, repeated, or malformed is `400`). A row tag cannot cover
association rows, which live on proxies and which those writes remove, so
the gateway compares the currently referencing proxies against the expected
set (plus a `proxy`-scoped `PUT`'s kept target) under the same namespace
admission lease and refuses with `412`, naming the unexpected proxies,
instead of silently detaching one attached after the caller's read. Clients
must send the parameter on every plugin-config update and delete once they
target Edge `v0.9.19`; earlier published gateways ignore it. No schema,
vocabulary, or fixture changes.

The namespace tag instead covers one coherent snapshot of all four resource
families, proxy/plugin associations, API-spec documents and ownership, gateway
trust bundles, namespace registry metadata, and the durable change watermark.
Registry metadata is covered but not exported or restored. Delete/recreate
and reverted mutations invalidate namespace tags; reads, lease maintenance,
audit events and missing-resource no-ops do not. Tags are keyed under the admin
JWT secret; replicas need the same secret, and rotation invalidates old tags.

From Edge v0.9.13 the namespace tag is a keyed MAC, in the
`namespace_snapshot.v2` domain, over a bounded SHA-256 of the canonical
snapshot. Stored API-spec documents, external-reference snapshots and other
binary values enter it as the SHA-256 and length of the stored bytes, so any
changed byte still invalidates the tag. Tags issued by v0.9.12 or earlier keep
their syntax but fail closed with `412`; re-read the backup after upgrading.
A namespace whose canonical representation (spec bytes excluded) exceeds
64 MiB gets `507` with no tag and nothing applied; the refusal is deterministic
for unchanged state. The metadata schema checks syntax only and is unchanged.

Edge v0.9.14 documents the conditional backup `ETag` (equal to
`conditional.namespace_etag`) as a namespace state token, not a validator of
the response bytes: two exports of unchanged state carry the same tag although
their bodies differ (`exported_at`). Use it only as the `If-Match` of a
conditional restore on the same namespace, never for HTTP caching or
`If-None-Match`.

Restore requires the namespace header token on the same `X-Ferrum-Namespace`.
A row token or `conditional` body metadata cannot authorize replacement.
Strong tag lists match any member, but namespace `*` is rejected. The
transaction compares state, clears and imports every chunk, restores ownership
and trust changes, records config changes and fences the lease at entry and
commit. Empty replacement still checks the precondition. Transaction failure
aborts replacement; an ambiguous MongoDB commit acknowledgement requires an
authoritative read before retry. Snapshot transactions require SQL or replica-set
MongoDB; this path never degrades to unconditional or chunked independent writes.

Omitting `If-Match` preserves unconditional restore. Body `conditional` metadata
is accepted and ignored by restore/batch. Existing body semantics still apply:
omitted resource collections are empty, legacy omission of API specs can require
`confirm_api_spec_deletion=true`, and omitted gateway trust bundles preserve
trust while an explicit empty list revokes it. Historical consumer credentials
are copied exactly by conditional reads (including rotation entries and fields);
they can require repair before restore admits them. Ordinary archival backup
keeps its existing credential canonicalization.

## Immutable process egress policy

`schemas/backend-egress-policy/v2.schema.json` transcribes
`BackendEgressPolicyResponse` as Edge v0.9.13 emits it (`schema_version: 2`);
`vocabularies/backend-egress-policy.json` (shape v2) records its labels.
`backend-egress-policy/v1.schema.json` and the v1 vocabulary shape describe
`schema_version: 1` from Edge v0.9.11 and v0.9.12. Each response major shares
its label/order definitions with the vocabulary shape of the same major, which
prevents vocabulary and response drift. Both majors assert the handler's exact
mode class lists and that release's guarantee calculation.

Validators must register `backend-egress-policy/v<N>.schema.json` and
`vocabulary-backend-egress-policy/v<N>.schema.json` of the same major by `$id`
from the same immutable canonical pin. Response references resolve to the latter's `$defs`;
the identifier URLs are not served documents (see [versioning.md](versioning.md)).

`GET /backend-egress-policy` returns `200` with `Cache-Control: no-store`.
Viewer, operator and admin JWTs, including viewer-key JWTs, can read it on
writable/read-only listeners. Metrics tokens/CIDR allowlists and anonymous
requests cannot authorize it. Invalid namespace is `400`, missing/invalid JWT
is `401`, namespace claim/ceiling denial is `403`, with no policy fields.
A present `ns` claim always constrains this read even when claim enforcement
is off; missing claims are denied when enforcement is on. The namespace need
not have stored resources; an absent namespace header selects `ferrum`.

The response has `schema_version=2` (Edge v0.9.13; `1` in v0.9.11 and v0.9.12),
`ip_classification=ferrum-private-reserved-v1`, and `policy_scope=process`.
It reads the immutable loaded policy from the serving `ProxyState`, otherwise
the loaded admin admission policy. It does not reread environment strings;
reloads do not change policy, and changes require process restart. No raw
CIDRs, addresses, counts, backend names, credentials or DNS probes are returned.

| `enforcement_scope` | Meaning |
|---|---|
| `local-data-plane` | This process serves the selected namespace |
| `unserved-namespace` | Its local data plane serves another namespace |
| `admission-only` | CP admission policy without a local proxy; its top-level fields attest no DP. From v0.9.14 the separate `data_plane_attestation` object reports its connected DPs |
| `no-data-plane` | No local proxy or CP admission scope, including node agents |

| `mode` | Allowed classes at the mode stage | Blocked classes at the mode stage |
|---|---|---|
| `both` (production default) | `public`, `private-reserved` | none |
| `public` | `public` | `private-reserved` |
| `private` | `private-reserved` | `public` |

`private-reserved` is Edge's versioned `is_private_ip` classifier, and `public`
is its complement. The pinned owner docs/code define exact IPv4/IPv6 ranges,
globally reachable IETF exceptions and recognized IPv4 embeddings. This
release adds no second classifier. Changes to classifier meaning require
versioned contract coordination.

Evaluation is fixed first-match precedence: `allow-cidrs`, `deny-cidrs`,
`dangerous-ranges`, `ip-mode`. Recognized embedded IPv4 candidates are checked;
ambiguous local-use NAT64 must pass both decodings and the literal IPv6 policy.
Explicit allows can bypass the deny overlay, dangerous baseline and mode.
The dangerous-range flag defaults true but still permits ordinary
loopback/RFC1918/ULA under `both`; it alone never establishes public-only egress.
The overlay flags disclose only whether loaded lists are nonempty.

In `schema_version: 2`, `public_only_guaranteed` is true exactly when
`enforcement_scope=local-data-plane`, `mode=public` and
`allow_cidr_overrides_present=false`; `admission-only`, `unserved-namespace`
and `no-data-plane` always report false, and the v2 schema rejects a true
guarantee for them. In `schema_version: 1` it was true for public mode without
allow overrides on any scope, including CP admission metadata. Deny overrides
only restrict. Even a wholly public undisclosed allow list produces false;
false does not prove a private address is reachable. The CP's own top-level
fields never attest its DPs.

### Data-plane attestation on a control plane (Edge v0.9.14)

From Edge v0.9.14 (#6029, issue #6020) every data plane reports bounded
metadata about its own loaded policy on ConfigSync `Subscribe`: the mode and
the dangerous-range, allow-override and deny-override presence flags, never
CIDRs, addresses or counts. On a CP (`enforcement_scope=admission-only`) the
response adds `data_plane_attestation`. It is optional and absent on every
other response, so `schema_version` stays `2` and `backend-egress-policy` v2
gains an optional property rather than a new major. The v2 schema rejects the
object on any other `enforcement_scope`.

| Member | Meaning |
|---|---|
| `source` | `configsync-subscribe` |
| `connected_data_planes` | Live Subscribe streams for the selected namespace, counted per stream, not per distinct `node_id` |
| `reporting_data_planes`, `unknown_data_planes` | Streams with and without a recognised report |
| `weakest_policy` | Field-wise least restrictive policy over the reporting streams (mode admitting the union of their classes, dangerous ranges blocked only if all block, allow overrides if any has them, deny overrides only if all have them); `null` exactly when none reported |
| `weakest_policy_complete` | True only when at least one stream is connected and every one reported |
| `all_connected_public_only_guaranteed` | True exactly when `weakest_policy_complete` and `weakest_policy.public_only_guaranteed` are true |
| `data_planes[]` | `node_id`, `connected_at`, `attestation` (`reported` or `unknown`) and `policy` (null when unknown), sorted by `node_id` then `connected_at`, with no build version |

Each `policy` uses the top-level field meanings for a local data plane:
`public_only_guaranteed` is true exactly for `mode=public` without allow
overrides. The schema asserts the mode class lists, that guarantee, the
`attestation`/`policy` pairing, and the summary implications above. It cannot
check that the counts add up or that `weakest_policy` is the combination of
the listed policies; consumers that rely on them must recompute.

The reports come from JWT-authenticated data planes running the CP's exact
build (ConfigSync protocol revision 3 from Edge `v0.9.14` through `v0.9.20`;
revision 6 from Edge `v0.9.21`), but each is the data plane's own
description, not a cryptographic attestation of its host. The set is a
point-in-time view: a data plane partitioned from the CP keeps serving its
cached config without being listed, and one using another CP is never seen.
Another namespace's streams never appear. On a CP the endpoint discloses the
namespace's DP `node_id`s, connection times and reported policies to
namespace-authorized `viewer` tokens.

Edge `v0.9.21` (`f9915358c8032214f4034a17c28cdf72d14006c3`) uses ConfigSync
protocol revision 6 (build identity `<crate version>+configsync.r6`). Revision
4 came with Edge PR
[#7338](https://github.com/ferrum-edge/ferrum-edge/pull/7338) (owner commit
[`ad7063e1cc0a688e98fe049fafccc7ee1a836b32`](https://github.com/ferrum-edge/ferrum-edge/commit/ad7063e1cc0a688e98fe049fafccc7ee1a836b32),
a snapshot JSON change), and revision 5 with Edge PR
[#7371](https://github.com/ferrum-edge/ferrum-edge/pull/7371) (issue #7233,
owner commit
[`6289427f35b3213cc366f748d71c1349b5420694`](https://github.com/ferrum-edge/ferrum-edge/commit/6289427f35b3213cc366f748d71c1349b5420694)),
which adds `MeshConfig.virtual_service_http_routes` and
`MeshSlice.http_routes`. Revision 6 came with Edge PR
[#7417](https://github.com/ferrum-edge/ferrum-edge/pull/7417)
(GHSA-rxwj-x6c6-f4j5, owner commit
[`da5e350c21995afd9badf2832da99fe5cc6fa963`](https://github.com/ferrum-edge/ferrum-edge/commit/da5e350c21995afd9badf2832da99fe5cc6fa963)):
plugin triggers gain the `external_identity` and
`external_identity_authority` predicates, which an earlier peer's closed
`PluginTriggerMatch` refuses. A CP and DP from different builds still refuse
each other at `Subscribe`, so the exact-build rule above holds. The
attestation sources (`src/grpc/backend_egress_attestation.rs`,
`src/admin/backend_egress_policy.rs`) and the egress OpenAPI components are
unchanged from `v0.9.20`, so `backend-egress-policy` v2 is unaffected.

`GET /cluster` (admin-only) gains per-DP `backend_egress_policy_attestation`
and `backend_egress_policy` and a cluster-wide
`data_plane_backend_egress_policy` aggregate with the same summary members.
This repository has no `/cluster` contract; its shapes are in the pinned owner
OpenAPI (`ClusterStatusCp`, `ConnectedDpNode`, `DataPlaneEgressSummary`,
`DataPlaneEgressPolicy`).

A public-only publisher must recognize `schema_version: 2` and its complete
vocabulary, match its namespace, require `local-data-plane` and `public_only_guaranteed=true`, and
check every serving DP again after replacement/restart. A publisher that cannot
reach every DP's admin API may instead read the CP's `data_plane_attestation`
for its namespace and require `all_connected_public_only_guaranteed=true`
together with a count of distinct `node_id` values in `data_planes` that reaches
the number of data-plane processes it expects for the namespace. Each Edge DP
process reports its own random `node_id`; `connected_data_planes` counts
streams, so a reconnect overlap can double-count one process. An absent
object, an unknown attestation status or an empty set blocks publication. Missing/unknown
versions, labels or fields, authorization failure, unserved/CP-only scopes and
weaker policy block publication. Unknown values grant no known meaning or
permission. This is loaded-policy metadata, not external firewall attestation,
DNS ownership, a socket test or new enforcement on any outbound path. Existing
enforcement-path limitations in the owner's configuration docs remain applicable.
