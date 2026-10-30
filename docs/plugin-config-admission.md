# Edge plugin configuration admission

The plugin catalog (`vocabularies/plugin-catalog.json`) points each built-in
plugin at its config schema in Edge's `openapi.yaml` and pins that file by
commit and SHA-256. This page records admission changes in the pinned document
that a product generating plugin configs must follow. They are owner config
rules and runtime refusals, not new envelope fields, vocabulary values or
schema majors. Namespace-scoped material-reference rules are in
[admin-contracts.md](admin-contracts.md#admin-authorization-and-write-rules).

`contracts-edge-0.9.19` pins Edge `v0.9.19` `openapi.yaml`
(`610e2645961e7a5deca73468439be9c4a5b7070045099506c212a0a36b045e90`), which
ships every change below. Further production-launch plugin changes are in the
pinned OpenAPI and the owner's
[upgrade guide](https://github.com/ferrum-edge/ferrum-edge/blob/510ce7121c3d9754110d330a30a3bd9b7a7b278e/docs/upgrade_guide.md).

## Native Kafka producer keys

Source: Edge PR
[#6551](https://github.com/ferrum-edge/ferrum-edge/pull/6551), issue #6539,
owner commit
[`803d0f972383521a116022ad70b3b56d6f9dacf9`](https://github.com/ferrum-edge/ferrum-edge/commit/803d0f972383521a116022ad70b3b56d6f9dacf9).

Edge `v0.9.17` and earlier admit these keys. From `v0.9.19`, `kafka_logging`
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

## Allow-lists, claim-header bounds and LDAP group cache

Source: Edge PRs
[#6635](https://github.com/ferrum-edge/ferrum-edge/pull/6635), owner commit
[`6f78ca1868d82aea7de74fd3738ca84720d7858b`](https://github.com/ferrum-edge/ferrum-edge/commit/6f78ca1868d82aea7de74fd3738ca84720d7858b),
[#6645](https://github.com/ferrum-edge/ferrum-edge/pull/6645), owner commit
[`7e5225af4d2b21f167a916afb17707091ab19804`](https://github.com/ferrum-edge/ferrum-edge/commit/7e5225af4d2b21f167a916afb17707091ab19804),
and [#6637](https://github.com/ferrum-edge/ferrum-edge/pull/6637), owner commit
[`fed841c6cbcb0d2e16f6ccbcc9df4447ad00b054`](https://github.com/ferrum-edge/ferrum-edge/commit/fed841c6cbcb0d2e16f6ccbcc9df4447ad00b054);
issues #6607, #6610, #6609, #6620 and #6611.

The catalog now pins
`v0.9.19` `openapi.yaml`, which enforces the changes below and admits the new
`ldap_auth` field. Edge `v0.9.17` admitted empty `access_control` allow-lists
and the older `claim_headers` objects, and rejected `group_cache_ttl_seconds`
as an unknown property. Every `config_schema.pointer` is unchanged.
From Edge `v0.9.19`:

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
  re-checking `required_groups`. The `v0.9.19` pin admits this field; the earlier
  `v0.9.17` schema rejects it (`additionalProperties: false`).

A product that generates these plugin configs should stop emitting empty
`access_control` allow-lists and `claim_headers` objects outside those bounds
before targeting Edge `v0.9.19`. The catalog pins that release
by its full commit and OpenAPI hash.

## Validator bypass, mirror allowlist, JWKS providers and CORS

Source: Edge PRs
[#6631](https://github.com/ferrum-edge/ferrum-edge/pull/6631) owner commit
[`bf43642fa30aef69acd6a4e904b9cb92551f39de`](https://github.com/ferrum-edge/ferrum-edge/commit/bf43642fa30aef69acd6a4e904b9cb92551f39de),
[#6634](https://github.com/ferrum-edge/ferrum-edge/pull/6634) owner commit
[`0be964e7b04d51a7b94e4b1430c8fadc68af7c2e`](https://github.com/ferrum-edge/ferrum-edge/commit/0be964e7b04d51a7b94e4b1430c8fadc68af7c2e),
[#6639](https://github.com/ferrum-edge/ferrum-edge/pull/6639) owner commit
[`7466d819cd93c9046865393bd9882235b3e07001`](https://github.com/ferrum-edge/ferrum-edge/commit/7466d819cd93c9046865393bd9882235b3e07001)
and [#6644](https://github.com/ferrum-edge/ferrum-edge/pull/6644) owner commit
[`b862d25f6872aea17b3c2740edae17a6836459d2`](https://github.com/ferrum-edge/ferrum-edge/commit/b862d25f6872aea17b3c2740edae17a6836459d2).

The catalog pins `v0.9.19` `openapi.yaml`, which enforces the changes
below; `v0.9.17` admitted the older configurations. Every
`config_schema.pointer` is unchanged. From Edge `v0.9.19`:

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
outside those bounds before targeting Edge `v0.9.19`. The catalog pins
that release by its full commit and OpenAPI hash.

## Hard resource bounds

Source: Edge PRs
[#6638](https://github.com/ferrum-edge/ferrum-edge/pull/6638) and
[#6640](https://github.com/ferrum-edge/ferrum-edge/pull/6640), issues #6612
and #6608; owner commits
[`ea18b5afa98ced1cdd733f0fd0c828d3c5f7f84b`](https://github.com/ferrum-edge/ferrum-edge/commit/ea18b5afa98ced1cdd733f0fd0c828d3c5f7f84b)
and
[`fab77df069598065acb64a98bff1020645f4d546`](https://github.com/ferrum-edge/ferrum-edge/commit/fab77df069598065acb64a98bff1020645f4d546).

Edge `v0.9.17` and earlier admit the larger values. The bounds ship in
`v0.9.19` and are published in
[`openapi.yaml`](https://github.com/ferrum-edge/ferrum-edge/blob/fab77df069598065acb64a98bff1020645f4d546/openapi.yaml)
and enforced by the plugin constructors. From Edge `v0.9.19` the
referenced plugin config components publish, and admission enforces, these
hard bounds:
- `response_caching` `max_entries` is at most `10000000`.
- `openapi_validator` `max_body_bytes` is at most `67108864`.
- `body_validator` `grpc_max_decompressed_size_bytes` is at most `67108864`. An inherited `FERRUM_MAX_REQUEST_BODY_SIZE_BYTES` default above that is clamped to it.
- `ai_prompt_shield` has `max_scan_bytes` at most `67108864`, `custom_patterns` at most 256 entries, and `patterns` at most 8 unique built-in names (a repeated name is refused).
- `ai_response_guard` has `max_scan_bytes` at most `67108864`, `pii_patterns` at most 8 unique built-in names (a repeated name is refused), `custom_pii_patterns` and `blocked_patterns` at most 256 entries each, and `blocked_phrases` at most 1024. Pattern `name` values are at most 128 characters, a custom `regex` that matches the empty string is refused, and each rendered `redaction_placeholder` is at most 512 UTF-8 bytes.

Catalog `config_schema` pointers are unchanged, and the `config_schema_document` pin is v0.9.19. There are no new envelope fields or vocabulary values.

## Telemetry redaction, mirror provenance and claim-header names

Source: Edge PRs
[#6654](https://github.com/ferrum-edge/ferrum-edge/pull/6654) owner commit
[`6535d61c58bd1102f3157ddee38f0aa334abd1b4`](https://github.com/ferrum-edge/ferrum-edge/commit/6535d61c58bd1102f3157ddee38f0aa334abd1b4),
[#6667](https://github.com/ferrum-edge/ferrum-edge/pull/6667) owner commit
[`4fa865c3bae0343655f279a9fddb3a31c2e8b72f`](https://github.com/ferrum-edge/ferrum-edge/commit/4fa865c3bae0343655f279a9fddb3a31c2e8b72f)
and [#6668](https://github.com/ferrum-edge/ferrum-edge/pull/6668) owner commit
[`1aeb94815087f23d0b8e55a32f38164b28daaa0e`](https://github.com/ferrum-edge/ferrum-edge/commit/1aeb94815087f23d0b8e55a32f38164b28daaa0e);
issues #6619, #6658 and #6656.

The catalog pins `v0.9.19`
`openapi.yaml`, which admits the two new fields below and enforces the
claim-header rules. The earlier `v0.9.17` schemas rejected those fields
(`additionalProperties: false`) and admitted the older claim-header spellings.
Every `config_schema.pointer` is unchanged. From Edge `v0.9.19`:

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
reserved or duplicate claim-header destinations before targeting Edge
`v0.9.19`. These changes add no envelope fields or vocabulary values; the
catalog pins the shipping OpenAPI.

## `security_headers` tokens

Source: Edge PRs
[#6685](https://github.com/ferrum-edge/ferrum-edge/pull/6685) owner commit
[`63cb25bab81c765b3a6dd243f8a0bdc722b1d68c`](https://github.com/ferrum-edge/ferrum-edge/commit/63cb25bab81c765b3a6dd243f8a0bdc722b1d68c)
and [#6705](https://github.com/ferrum-edge/ferrum-edge/pull/6705) owner commit
[`3e69a2d2f765f4a27d8d3aa5a1d4865f9f4c2e6a`](https://github.com/ferrum-edge/ferrum-edge/commit/3e69a2d2f765f4a27d8d3aa5a1d4865f9f4c2e6a),
issue #6617.

Edge `v0.9.17` and earlier admit any printable string.
From `v0.9.19`, `SecurityHeadersConfig`
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
values (for example `ALLOW-FROM`) before targeting Edge `v0.9.19`.
Catalog `config_schema` pointers are unchanged, and the `config_schema_document`
pin is v0.9.19. There are no new envelope
fields or vocabulary values.
