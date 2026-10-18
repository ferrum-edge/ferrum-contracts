# Edge admin snapshot and egress contracts

**Published contracts-edge-0.9.11.** These surfaces
shipped in Edge `v0.9.11` at immutable source
`c764084b3b51c3f7ffde268c039688d35e49c553`, with verified upstream distribution
recorded in the [release notes](releases/contracts-edge-0.9.11.md). The canonical
tag points to `390edbd5b2485af0988e02f7827fde778d76ae0a`; release 403239814
was published on 2026-10-04 at 22:41:21 UTC. Prepared/pending wording captured in
the immutable source is historical. Downstream adoption remains pending until
consumer PRs merge and qualify. Canonical metadata alone does not patch a product
advisory or qualify a consumer integration.

The [published 0.9.12 deployment contracts](deployment-contracts.md) read
actually released owner `0d917701b63ef38210c49df830f48cf0457cbc7d` and add a
separate original deployment-token partial mutation profile. The current
backup/egress schema provenance is re-read there with unchanged wire semantics.
This document preserves the published 0.9.11 namespace/row/restore profile;
deployment authority does not replace those tags or authorize whole restore.
Contracts 0.9.12 is published at `31f0a21d707795be293d15837c2f77c3d84219d8`;
downstream adoption remains pending.

[Contracts 0.9.13](releases/contracts-edge-0.9.13.md) reads Edge `v0.9.13` at
`9b83115de7ec23ab51ec4feae6bed65e596db425`. The backup metadata keeps its v1
shape, but its namespace token is now a keyed MAC over a bounded snapshot
digest, and the egress response moves to `schema_version: 2` with
`backend-egress-policy` v2. Both changes are described below.

[Contracts 0.9.14](releases/contracts-edge-0.9.14.md) reads Edge `v0.9.14` at
`9bd4d5f9caa4ebe8f0ea13e76d8a6e2172eaca7d`. A control plane's egress response gains the optional
`data_plane_attestation` object within `schema_version: 2`, and the conditional
backup `ETag` is documented as a namespace state token. Both are described
below; the backup metadata shape is unchanged.

[Contracts 0.9.15](releases/contracts-edge-0.9.15.md) reads Edge `v0.9.15` at
`25b37395ff61bfea0f3ffd189d9011c4984fa755`. The backup metadata, restore
preconditions and egress response are unchanged; their sources
(`conditional_snapshots.rs`, `preconditions.rs`, `backup.rs`,
`backend_egress_policy.rs`, `backend_egress_attestation.rs` and their OpenAPI
components) are byte-identical to `v0.9.14`. Two owner changes touch the same
admin surface without a contract here. On MongoDB, `POST /batch` and
`POST /restore` (conditional or not) now attach a `scope: proxy` plugin config
to its proxy in the same write, as SQL already did (Edge #6065, #6074; rows
written earlier are not rewritten), and the owner documents that both paths
reject a `proxy_id` that does not exist in the namespace with `400` before
anything is written. Where the admin `ns` claim is enforced, a
namespace-scoped `operator` that introduces a `backend_tls_*` reference outside
inline PEM, `system://` or a `k8s://` Secret in the addressed namespace gets
`400` (Edge #6094, issue #6092); these are proxy and upstream field
descriptions in the pinned OpenAPI.

[Contracts 0.9.17](releases/contracts-edge-0.9.17.md) reads Edge `v0.9.17`
at `669c574c1d1e88e84dccb26a8159939e6694644d`. The conditional backup and
backend egress wire shapes remain unchanged. A present JWT `ns` claim always
bounds the caller; the namespace-scoped flag controls whether a claim is
required, not whether a present claim is enforced. Fleet-global routes and
metrics return 403 for bounded tokens, including allowlisted callers. Tenant
observability routes retain their tier restrictions. A cached read with no
authoritative fallback proof of absence returns 503 rather than a false 404.
These are runtime authorization/availability rules, not new envelope fields.

**Edge `main`, unreleased (Edge PR
[#6316](https://github.com/ferrum-edge/ferrum-edge/pull/6316), issue #6092,
owner commit
[`d5417cd723120995666a7a14c6a4bc9022ba86a9`](https://github.com/ferrum-edge/ferrum-edge/commit/d5417cd723120995666a7a14c6a4bc9022ba86a9)).**
No Edge release contains this change yet; v0.9.17 and earlier keep the
behavior described above. On Edge `main`, gateway material references are
default-deny for an `operator` token that carries an `ns` claim, even when
`FERRUM_ADMIN_REQUIRE_NAMESPACE_CLAIM=false`.

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
[`src/admin/crud.rs`](https://github.com/ferrum-edge/ferrum-edge/blob/d5417cd723120995666a7a14c6a4bc9022ba86a9/src/admin/crud.rs). These rules are owner
OpenAPI descriptions and a runtime refusal, not new envelope fields or
vocabulary values. The release refresh records the Edge tag that ships it.

**Edge `main`, unreleased (Edge PR
[#6551](https://github.com/ferrum-edge/ferrum-edge/pull/6551), issue #6539,
owner commit
[`803d0f972383521a116022ad70b3b56d6f9dacf9`](https://github.com/ferrum-edge/ferrum-edge/commit/803d0f972383521a116022ad70b3b56d6f9dacf9)).**
No Edge release contains this change yet; v0.9.17 and earlier admit these keys. On Edge `main`, `kafka_logging`
`producer_config` keys that load native code, run a host command, or make
librdkafka read or write a gateway file are refused for **every** token,
`admin` included (`400` on a direct plugin-config write, `422` on an API-spec
import or replacement through `x-ferrum-plugins`; config loads and snapshot
publication reject the generation): `plugin.library.paths`, `ssl.engine.location`,
`ssl.engine.id`, `ssl.providers`, `sasl.kerberos.kinit.cmd`,
`sasl.kerberos.keytab`, `sasl.oauthbearer.assertion.private.key.file`,
`sasl.oauthbearer.assertion.file`,
`sasl.oauthbearer.assertion.jwt.template.file`, `https.ca.location` and
`offset.store.path`. Matching ignores case and a `topic.` prefix, and applies
to disabled rows, API-spec imports and every node's snapshot publication. A node that
sets `FERRUM_KAFKA_ALLOW_NATIVE_CONFIG=true` admits them for unconfined
tokens; an `ns`-claimed `operator` still cannot introduce or change them. The
owner keeps the list as `KAFKA_NATIVE_PRODUCER_KEYS` in
[`src/admin/crud/scoped_references.rs`](https://github.com/ferrum-edge/ferrum-edge/blob/803d0f972383521a116022ad70b3b56d6f9dacf9/src/admin/crud/scoped_references.rs). This is an owner runtime refusal and
OpenAPI description text, not a new envelope field or vocabulary value.

**Edge `main`, unreleased plugin-config admission (Edge PRs
[#6635](https://github.com/ferrum-edge/ferrum-edge/pull/6635), owner commit
[`6f78ca1868d82aea7de74fd3738ca84720d7858b`](https://github.com/ferrum-edge/ferrum-edge/commit/6f78ca1868d82aea7de74fd3738ca84720d7858b),
[#6645](https://github.com/ferrum-edge/ferrum-edge/pull/6645), owner commit
[`7e5225af4d2b21f167a916afb17707091ab19804`](https://github.com/ferrum-edge/ferrum-edge/commit/7e5225af4d2b21f167a916afb17707091ab19804),
and [#6637](https://github.com/ferrum-edge/ferrum-edge/pull/6637), owner commit
[`fed841c6cbcb0d2e16f6ccbcc9df4447ad00b054`](https://github.com/ferrum-edge/ferrum-edge/commit/fed841c6cbcb0d2e16f6ccbcc9df4447ad00b054);
issues #6607, #6610, #6609, #6620 and #6611).** No Edge release
contains these changes yet, and the catalog's `config_schema_document` stays
pinned to the `v0.9.17` `openapi.yaml`. That pinned schema still admits the
empty `access_control` allow-lists and the `claim_headers` objects described
below, but it does not know `group_cache_ttl_seconds`, so it rejects an
`ldap_auth` config that sets it. Every `config_schema.pointer` is unchanged.
On Edge `main`:

- `AccessControlConfig`: `allowed_consumers` and `allowed_groups` gain
  `minItems: 1` and lose `default: []`. A present but empty allow-list is
  refused at config validation instead of meaning "no allow restriction";
  omit the key for that. Empty deny-lists stay valid.
- `IpRestrictionConfig`: `mode` is marked `deprecated: true`. It never changed
  the admission decision and still loads; it only selects the rejection reason
  for an address that is both outside `allow` and on `deny`.
- `JwksAuthConfig` (global and per-provider),
  `Oauth2IntrospectionConfig` and `OidcRelyingPartyConfig` `claim_headers`:
  `maxProperties: 16`. The runtime
  also refuses claim paths over 256 bytes or containing whitespace/control
  characters, header names over 128 bytes, two mappings naming one header, and
  the strict reserved-destination list `output_claim_headers` already used
  (stated in the property descriptions, not as schema keywords). A resolved
  claim value that is not a valid header value or exceeds 8192 bytes leaves
  the destination absent.
- `Oauth2IntrospectionConfig` description: a JSON `null` `exp`,
  `active_until` or `expires_in` in an introspection response reads as
  omitted (Edge PR #6637, issue #6611).
- `LdapAuthConfig`: new optional `group_cache_ttl_seconds` (integer, default
  `60`, `0`–`86400`) bounding how long a cached credential is admitted without
  re-checking `required_groups`. Validating such a config against the pinned
  `v0.9.17` schema fails (`additionalProperties: false`) until the release
  refresh moves the pin.

A product that generates these plugin configs should stop emitting empty
`access_control` allow-lists and `claim_headers` objects outside those bounds
before it targets a release that ships them. The release refresh moves the
`openapi.yaml` pin and records the Edge tag.

**Edge `main`, unreleased plugin-config hardening (Edge PRs
[#6631](https://github.com/ferrum-edge/ferrum-edge/pull/6631) owner commit
[`bf43642fa30aef69acd6a4e904b9cb92551f39de`](https://github.com/ferrum-edge/ferrum-edge/commit/bf43642fa30aef69acd6a4e904b9cb92551f39de),
[#6634](https://github.com/ferrum-edge/ferrum-edge/pull/6634) owner commit
[`0be964e7b04d51a7b94e4b1430c8fadc68af7c2e`](https://github.com/ferrum-edge/ferrum-edge/commit/0be964e7b04d51a7b94e4b1430c8fadc68af7c2e),
[#6639](https://github.com/ferrum-edge/ferrum-edge/pull/6639) owner commit
[`7466d819cd93c9046865393bd9882235b3e07001`](https://github.com/ferrum-edge/ferrum-edge/commit/7466d819cd93c9046865393bd9882235b3e07001)
and [#6644](https://github.com/ferrum-edge/ferrum-edge/pull/6644) owner commit
[`b862d25f6872aea17b3c2740edae17a6836459d2`](https://github.com/ferrum-edge/ferrum-edge/commit/b862d25f6872aea17b3c2740edae17a6836459d2)).**
No Edge release contains these changes yet; the catalog's
`config_schema_document` stays pinned to the `v0.9.17` `openapi.yaml`, which
still admits the configurations below. Every `config_schema.pointer` is
unchanged. On Edge `main`:

- `OpenapiValidatorConfig` `bypass.header_present`: each value must be a
  secret string of 16–4096 visible ASCII characters
  (`pattern: "^[!-~]+$(?![\\s\\S])"`, `minLength: 16`, `maxLength: 4096`). A
  `null` (presence-only) value is refused at construction.
- `RequestMirrorConfig` `forward_sensitive_query_allowlist` items: the
  pattern now admits only visible ASCII without `% + = & ? # / @ ;` or
  surrounding whitespace (brackets such as `filter[key]` are allowed). Entries
  that are not credential-shaped names, built-in or by operator pattern, are
  still refused at construction (runtime-only rule). The description of
  credential-shaped header and query names that are stripped by default widens
  accordingly.
- `JwksAuthConfig` `providers`: `maxItems: 64`. The runtime also refuses a
  set where the providers sharing one `issuer`, plus those without an
  `issuer`, exceed 8, and at most 8 providers may omit `issuer` (stated in
  the description, not as schema keywords).
- `CorsConfig` descriptions: with `allow_credentials`, a `*.suffix` origin
  over a single label, a numeric label, a public suffix or a domain with
  Public Suffix List rules beneath it is refused. A credentialed `regex`
  origin must provably pin the host (runtime-only rule).

A product that generates these plugin configs should stop emitting
presence-only `bypass.header_present` entries and `jwks_auth` provider sets
outside those bounds before it targets a release that ships them. The release
refresh moves the `openapi.yaml` pin and records the Edge tag.

**Edge `main`, unreleased (Edge PRs
[#6638](https://github.com/ferrum-edge/ferrum-edge/pull/6638) and
[#6640](https://github.com/ferrum-edge/ferrum-edge/pull/6640), issues #6612
and #6608; owner commits
[`ea18b5afa98ced1cdd733f0fd0c828d3c5f7f84b`](https://github.com/ferrum-edge/ferrum-edge/commit/ea18b5afa98ced1cdd733f0fd0c828d3c5f7f84b)
and
[`fab77df069598065acb64a98bff1020645f4d546`](https://github.com/ferrum-edge/ferrum-edge/commit/fab77df069598065acb64a98bff1020645f4d546)).**
No Edge release contains these changes yet; v0.9.17 and earlier admit the
larger values. The bounds are published in
[`openapi.yaml`](https://github.com/ferrum-edge/ferrum-edge/blob/fab77df069598065acb64a98bff1020645f4d546/openapi.yaml)
and enforced by the plugin constructors. On Edge `main` the
referenced plugin config components publish, and admission enforces, these
hard bounds:
- `response_caching` `max_entries` is at most `10000000`.
- `openapi_validator` `max_body_bytes` is at most `67108864`.
- `body_validator` `grpc_max_decompressed_size_bytes` is at most `67108864`. An inherited `FERRUM_MAX_REQUEST_BODY_SIZE_BYTES` default above that is clamped to it.
- `ai_prompt_shield` has `max_scan_bytes` at most `67108864`, `custom_patterns` at most 256 entries, and `patterns` at most 8 unique built-in names (a repeated name is refused).
- `ai_response_guard` has `max_scan_bytes` at most `67108864`, `pii_patterns` at most 8 unique built-in names (a repeated name is refused), `custom_pii_patterns` and `blocked_patterns` at most 256 entries each, and `blocked_phrases` at most 1024. Pattern `name` values are at most 128 characters, a custom `regex` that matches the empty string is refused, and each rendered `redaction_placeholder` is at most 512 UTF-8 bytes.

Catalog `config_schema` pointers are unchanged, and the `config_schema_document` pin stays at v0.9.17 until the release refresh. There are no new envelope fields or vocabulary values.

**Edge `main`, unreleased telemetry redaction, mirror provenance and claim-header
admission (Edge PRs
[#6654](https://github.com/ferrum-edge/ferrum-edge/pull/6654) owner commit
[`6535d61c58bd1102f3157ddee38f0aa334abd1b4`](https://github.com/ferrum-edge/ferrum-edge/commit/6535d61c58bd1102f3157ddee38f0aa334abd1b4),
[#6667](https://github.com/ferrum-edge/ferrum-edge/pull/6667) owner commit
[`4fa865c3bae0343655f279a9fddb3a31c2e8b72f`](https://github.com/ferrum-edge/ferrum-edge/commit/4fa865c3bae0343655f279a9fddb3a31c2e8b72f)
and [#6668](https://github.com/ferrum-edge/ferrum-edge/pull/6668) owner commit
[`1aeb94815087f23d0b8e55a32f38164b28daaa0e`](https://github.com/ferrum-edge/ferrum-edge/commit/1aeb94815087f23d0b8e55a32f38164b28daaa0e);
issues #6619, #6658 and #6656).** No Edge release contains these changes yet;
the catalog's `config_schema_document` stays pinned to the `v0.9.17`
`openapi.yaml`, which rejects the two new fields below (both components set
`additionalProperties: false`) and still admits the claim-header spellings
below. Every `config_schema.pointer` is unchanged. On Edge `main`:

- `TransactionDebuggerConfig`: new optional `safe_text_fields` (array of
  strings, each matching `^\s*[A-Za-z0-9_.-]{1,128}\s*$`). A nonempty list
  requires `log_request_body` or `log_response_body` to be `true` (a new
  `if`/`then` rule). In captured `text/plain` bodies a `name=value` /
  `name: value` line is kept only when every field name parses cleanly and is
  listed there. Credential-shaped entries are refused at construction
  (runtime-only rule).
- `WorkloadMetricsConfig`: new optional `safe_tag_sources` (at most 64
  strings of 1–256 characters). A `custom_header_tags` or `custom_env_tags`
  source not declared there is copied as `[REDACTED]`; credential-shaped
  entries are refused at construction. The `custom_header_tags` and
  `custom_env_tags` descriptions now state that fail-closed copy, and
  `custom_env_tags` names the credential classes it rejects as sources.
- `SummaryLogSchema` description and its `static_fields` description:
  `rename` targets, `static_fields` keys and `derived_fields` names that match
  a credential-class name (for example `session_id`, `client_assertion`,
  `gpg_passphrase`) are refused at compile time, beside the existing
  sensitive-substring rule.
- `RequestMirrorConfig` description: credentials keep provenance through
  `request_transformer` renames, and a header or query value equal to a
  credential value seen on the request is withheld under whatever name it
  now has.
- `McpGatewayConfig` `sessions.upstream_session_header` description: both
  configured session header names are registered as credential headers for
  the route (redacted from diagnostics and policy calls, withheld from
  `request_mirror`, bound into replay partitions).
- `JwksAuthConfig` `output_claim_headers` and the `claim_headers`
  descriptions on `JwksAuthConfig`, `Oauth2IntrospectionConfig` and
  `OidcRelyingPartyConfig`: in both forms, reserved names and duplicate
  destinations are compared case-insensitively with `_` treated as `-`
  (`X_Real_IP` is reserved, `X_Tenant_Id` duplicates `X-Tenant-Id`).

The metadata allowlist itself is runtime behavior, not a schema keyword:
transaction-log metadata values are emitted only under the owner's exact
built-in keys or names an operator lists in `FERRUM_LOG_SAFE_METADATA_KEYS`,
and every other value is written as `[REDACTED]`. Trace spans apply the same
allowlist to gateway-set `mesh.*` attributes but omit a disallowed attribute
instead of emitting a placeholder. Custom tags declared on `workload_metrics`
(`custom_tags`, `custom_header_tags`, `custom_env_tags`) reach spans without
the global allowlist: a header or environment tag whose source is not listed in
`safe_tag_sources` carries `[REDACTED]`, and a tag name that matches the
sensitive-name rules is dropped. A Kubernetes RequestAuthentication that
Ferrum refuses now makes its selected workloads answer inbound HTTP requests
with `503` instead of being dropped. A product that generates these plugin configs should stop
emitting credential-shaped log-schema names and underscore spellings of
reserved or duplicate claim-header destinations before it targets a release
that ships them. There are no new envelope fields or vocabulary values. The
release refresh moves the `openapi.yaml` pin and records the Edge tag.

**Edge `main`, unreleased `security_headers` token admission (Edge PRs
[#6685](https://github.com/ferrum-edge/ferrum-edge/pull/6685) owner commit
[`63cb25bab81c765b3a6dd243f8a0bdc722b1d68c`](https://github.com/ferrum-edge/ferrum-edge/commit/63cb25bab81c765b3a6dd243f8a0bdc722b1d68c)
and [#6705](https://github.com/ferrum-edge/ferrum-edge/pull/6705) owner commit
[`3e69a2d2f765f4a27d8d3aa5a1d4865f9f4c2e6a`](https://github.com/ferrum-edge/ferrum-edge/commit/3e69a2d2f765f4a27d8d3aa5a1d4865f9f4c2e6a),
issue #6617).** No Edge release contains these changes yet; v0.9.17 and
earlier admit any printable string. On Edge `main`, `SecurityHeadersConfig`
publishes, and admission enforces:
- `content_type_options`, `frame_options` and `referrer_policy` strings must be
  `nosniff`; `DENY` or `SAMEORIGIN`; or a comma-separated list of
  Referrer-Policy tokens (`no-referrer`, `no-referrer-when-downgrade`,
  `origin`, `origin-when-cross-origin`, `same-origin`, `strict-origin`,
  `strict-origin-when-cross-origin`, `unsafe-url`). Matching is ASCII
  case-insensitive with optional surrounding spaces and tabs; `""` still
  disables the header.
- `set` gains `patternProperties` for `X-Content-Type-Options`,
  `X-Frame-Options` and `Referrer-Policy` (case-insensitive names) holding
  their values to the same tokens, with an empty value refused.

A product that generates `security_headers` configs should stop emitting other
values (for example `ALLOW-FROM`) before it targets a release that ships them.
Catalog `config_schema` pointers are unchanged, and the `config_schema_document`
pin stays at v0.9.17 until the release refresh. There are no new envelope
fields or vocabulary values.

## Owner sources and artifact scope

The owner is `ferrum-edge/ferrum-edge`. Read the following paths at the full
commit above, never a consumer's copy:

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

On Edge `main` (unreleased; Edge PR #6744, forge-ops issue #569),
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
target a release that ships it; earlier gateways ignore it. No schema,
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
build (ConfigSync protocol revision 3), but each is the data plane's own
description, not a cryptographic attestation of its host. The set is a
point-in-time view: a data plane partitioned from the CP keeps serving its
cached config without being listed, and one using another CP is never seen.
Another namespace's streams never appear. On a CP the endpoint discloses the
namespace's DP `node_id`s, connection times and reported policies to
namespace-authorized `viewer` tokens.

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
