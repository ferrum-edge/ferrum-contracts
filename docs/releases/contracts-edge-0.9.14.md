# contracts-edge-0.9.14 release record

`contracts-edge-0.9.14` holds the contracts for Ferrum Edge `v0.9.14`. The tag
is the merge commit of the release PR; the
[GitHub release](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.14)
for the tag records its commit and publication time. Every Edge-owned file in
the tag reads the owner at `v0.9.14`.

## Edge source

The Edge `v0.9.14` tag points to `@@EDGE_0914_COMMIT@@`, the merge of
[Edge #6050](https://github.com/ferrum-edge/ferrum-edge/pull/6050)
(first parent `@@EDGE_0914_PARENT1@@`, second parent
`@@EDGE_0914_PARENT2@@`).
[GitHub release @@EDGE_0914_RELEASE_ID@@](https://github.com/ferrum-edge/ferrum-edge/releases/tag/v0.9.14)
was published at @@EDGE_0914_PUBLISHED_AT@@. Edge `v0.9.14` has no
`docs/releases/v0.9.14.md`; its `CHANGELOG.md` `[0.9.14]` section and the
upgrade guide's "Upgrading to 0.9.14" are the owner's release notes. Edge's
assets, digests and attestations are recorded in that Edge release, not here.

`openapi.yaml` at the tag has SHA-256
`6d286649ae744691e2eeb7d16607c538ca02e31bdeaafe98ab07fc861e7b9da4`.

## Contract changes

No contract gets a new major. Each change below is an optional property, a
clearer description or a new fixture, which
[versioning.md](../versioning.md) allows within a major.

- **Backend egress policy: data-plane attestation.** Edge
  [#6029](https://github.com/ferrum-edge/ferrum-edge/pull/6029) (issue #6020,
  completing #5994) has every data plane report its mode and three presence
  flags on ConfigSync `Subscribe`. On a control plane
  (`enforcement_scope=admission-only`), `GET /backend-egress-policy` adds the
  optional `data_plane_attestation` object: one entry per live Subscribe stream
  for the selected namespace (`node_id`, `connected_at`, `attestation`
  `reported` or `unknown`, `policy`), with no build version, plus
  `connected_data_planes`, `reporting_data_planes`, `unknown_data_planes`, a
  field-wise `weakest_policy`, `weakest_policy_complete` and
  `all_connected_public_only_guaranteed`. The object is absent on every other
  response, and `schema_version` stays `2`. `backend-egress-policy` v2 gains
  the optional property, closed definitions for the attestation, entry and
  policy objects, and the owner's rules: the object only on `admission-only`,
  the mode class lists and `public_only_guaranteed` of each policy, the
  `attestation`/`policy` pairing, `weakest_policy` null exactly when no data
  plane reported, completeness requiring a non-empty set without unknown data
  planes, and the aggregate guarantee equal to completeness plus a public-only
  weakest policy. `vocabulary-backend-egress-policy` v2 gains the optional
  `data_plane_attestation_source`, `data_plane_attestation_statuses` and
  `data_plane_attestation_rule` members, and the egress vocabulary carries
  them. The CP's top-level `public_only_guaranteed` stays `false`.
- **`GET /cluster`.** The same change adds per-DP
  `backend_egress_policy_attestation` and `backend_egress_policy` and a
  cluster-wide `data_plane_backend_egress_policy` aggregate. This repository
  has no `/cluster` contract; the shapes are in the pinned owner OpenAPI
  (`ClusterStatusCp`, `ConnectedDpNode`, `DataPlaneEgressSummary`).
- **Deployment mutation durable outcomes.** Edge
  [#6027](https://github.com/ferrum-edge/ferrum-edge/pull/6027) (issue #6021)
  reports a `503` store failure before the mutation transaction as
  `durable: "not_started"` and one inside the rolled-back transaction as
  `durable: "not_committed"`. Only a failed commit or commit acknowledgement,
  or a lost settlement task, still reports `"unknown"`. The `durable` enum is
  unchanged. `admin-deployment-mutation-acknowledgement` v1 describes each
  value and gains a valid fixture for the `503` `not_committed` body. The same
  PR documents that a `deployment-v1` token fences the whole namespace and the
  peak server memory of `api_spec_contents`; `admin-deployment-snapshot` v2
  keeps its wire shape and records the fence in its descriptions and the peak
  memory in its `x-contract` and provenance text.
- **Error classification.** Edge
  [#6028](https://github.com/ferrum-edge/ferrum-edge/pull/6028) and
  [#6042](https://github.com/ferrum-edge/ferrum-edge/pull/6042) (issues #6019
  and #6022) classify a backend HTTP/2 `RST_STREAM` or `GOAWAY` with any reason
  except `NO_ERROR` as `protocol_error`, before the response headers, during a
  buffered read or while a body streams, and charge it to the target. The
  buffered collector's reqwest-reported read errors now report their real class,
  so a timeout reqwest reports there is `read_write_timeout` with `504`; these
  errors used to be `response_body_too_large`. The collector's own idle
  `backend_read_timeout_ms` timeout was already `read_write_timeout`. No `ErrorClass` value or `X-Gateway-Error` token
  is added or removed. `gateway-errors.json` notes the change in the
  `protocol_error`, `read_write_timeout` and `response_body_too_large`
  meanings.
- **Header descriptions.** `gateway-headers.json` `ETag` records that the
  conditional backup tag is a namespace state token for restore `If-Match`,
  not a response-byte validator. `If-Match` records the namespace-wide
  deployment fence and the narrowed `503` durable outcomes.

## Checked and unchanged

- `X-Gateway-Error` tokens, `ErrorClass` values, header names, provisioning
  values and plugin registrations are unchanged. `src/proxy/headers.rs`,
  `src/admin/provisioning.rs`, `src/plugins/builtin_parity.rs`,
  `src/admin/preconditions.rs` and `src/config/env_config.rs` are
  byte-identical to `v0.9.13`. `src/retry.rs` changes only classifier logic;
  `ErrorClass`, `x_gateway_error_token_for_class` and
  `token_for_rejection_phase` are unchanged.
- [#6039](https://github.com/ferrum-edge/ferrum-edge/pull/6039),
  [#6045](https://github.com/ferrum-edge/ferrum-edge/pull/6045) and
  [#6046](https://github.com/ferrum-edge/ferrum-edge/pull/6046) key built-in
  plugin trust on the registered concrete type (`Plugin` gains `Any` as a
  supertrait) and have auth plugins name the headers they strip.
  `BUILTIN_PLUGIN_REGISTRATIONS`, `REMOVED_PLUGIN_REGISTRATIONS`,
  `BUILTIN_PLUGIN_PARITY_META` and `PluginConfigBase` are unchanged, so the
  plugin catalog keeps its 82 plugins and their config pointers, now into the
  `v0.9.14` `openapi.yaml`.
- `diagnostic-ref` v1 sources (`src/diagnostic_ref.rs` and its OpenAPI
  components) are unchanged at `v0.9.14`. The schema file keeps its frozen v1
  bytes.
- `admin-conditional-snapshot` v1 keeps its shape; its provenance moves to
  `v0.9.14`. The v1 egress and deployment snapshot schemas keep their
  `v0.9.12` provenance and still describe Edge `v0.9.11` and `v0.9.12`.
- Other owners' schemas, availability notes and fixtures are unchanged.

## Fixtures and validation

New `backend-egress-policy` v2 valid fixtures transcribe the owner's two CP
OpenAPI examples (no connected data plane; two reporting public-only data
planes) and three steps of `admin_backend_egress_policy_tests.rs`: an unknown
data plane, a data plane with allow overrides, and two streams sharing one
`node_id`. Their `connected_at` values are illustrative. Twenty-one invalid
fixtures cover each new rule, the closed objects, the unknown labels, the
build version that namespace-scoped entries omit, and the `date-time` format.
The vocabulary has one new valid and two new invalid fixtures, and the
acknowledgement one new valid fixture. `fixtures/README.md` lists each one,
and `fixtures/invalid-expectations.json` records the expected path and keyword
of each invalid fixture.

The `Validate contracts` workflow is the conformance gate. Workflow,
permissions, action pins, Python dependencies and `ci/validate.py` are
unchanged.

## Consumers

A consumer pinned to `contracts-edge-0.9.13` keeps validating Edge `v0.9.13`
responses. Against Edge `v0.9.14`, its closed `backend-egress-policy` v2 schema
rejects a CP response that carries `data_plane_attestation`; it needs
`contracts-edge-0.9.14`. Responses with any other `enforcement_scope` are
unchanged.

A public-only publisher may now read a CP's `data_plane_attestation` and
require `all_connected_public_only_guaranteed=true` together with every
expected data-plane `node_id` present in `data_planes` (a stream count alone
can double-count a reconnecting node and hide a missing one). An absent
object, an unknown status or an empty set blocks publication. The reports are
self-descriptions from authenticated data planes, not cryptographic host
attestation. Deployment recovery consumers can treat `not_started` and
`not_committed` as definite non-commits, but neither authorizes cleanup or
replay. Consumer pins are recorded in [adoption.md](../adoption.md).
