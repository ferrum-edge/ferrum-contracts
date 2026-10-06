# contracts-edge-0.9.13 release record

`contracts-edge-0.9.13` holds the contracts for Ferrum Edge `v0.9.13`. The tag
is the merge commit of the release PR; the
[GitHub release](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.13)
for the tag records its commit and publication time. Every Edge-owned file in
the tag reads the owner at `v0.9.13`; nothing merged to Edge `main` after that
tag is included.

## Edge source

The Edge `v0.9.13` tag points to `9b83115de7ec23ab51ec4feae6bed65e596db425`,
the merge of [Edge #6026](https://github.com/ferrum-edge/ferrum-edge/pull/6026)
(first parent `fd02c5f45bb9dee86a52bc612fcefd0223d6157b`, second parent
`71c282279a38591c8c50fd11a1d0ba0c5be4a484`).
[GitHub release 404961860](https://github.com/ferrum-edge/ferrum-edge/releases/tag/v0.9.13)
was published at 17:04:49 UTC on 2026-10-06. Edge `v0.9.13` has no
`docs/releases/v0.9.13.md`; its `CHANGELOG.md` `[0.9.13]` section and the
upgrade guide's "Upgrading to 0.9.13" are the owner's release notes. Edge's
assets, digests and attestations are recorded in that Edge release, not here.

`openapi.yaml` at the tag has SHA-256
`5f3e50e217b22b97d068490bdad9563ea450097a2daf7df4f80ff61f98559a81`.

## Contract changes

Edge [#6017](https://github.com/ferrum-edge/ferrum-edge/pull/6017) (issues
#5994, #5999, #6012) changes two response contracts incompatibly:

- **Backend egress policy, new major v2.** `GET /backend-egress-policy` now
  reports `schema_version: 2` and never `1`. `public_only_guaranteed` is true
  only when `enforcement_scope` is `local-data-plane`, `mode` is `public` and
  no allow overrides are loaded; `admission-only`, `unserved-namespace` and
  `no-data-plane` always report `false`. Version 1 reported the policy-only
  value, so the same field changed meaning. `backend-egress-policy` v2,
  `vocabulary-backend-egress-policy` v2 and the egress vocabulary (now shape
  version 2) record it. The v1 files stay for consumers of Edge v0.9.11 and
  v0.9.12.
- **Deployment snapshot, new major v2.** `GET /deployment-snapshot` adds the
  required `api_spec_contents` array: one standard padded base64 copy of each
  stored gzip spec document and external-reference snapshot, outside the
  digested evidence, bounded at 256 MiB in total. `api_specs` items now require
  `id`, `proxy_id` and `spec_content`, and carry `spec_content` and
  `external_ref_snapshot` as `StoredContentDigest` (`sha256`, `len`) instead of
  byte arrays; the array is sorted by id and equals `evidence.resources[5]`.
  Raw SQL blobs become `{sha256, len}` and MongoDB rows carry `bson_sha256`
  (binary values as `binary_sha256`/`len`/`subtype`) instead of `bson_hex`.
  `admin-deployment-snapshot` v2 records the envelope; v1 stays for Edge
  v0.9.12.
- **Snapshot tokens.** Conditional backup namespace tags and `deployment-v1-`
  tokens now MAC a bounded SHA-256 of the canonical snapshot under the
  `namespace_snapshot.v2` and `deployment_snapshot.v2` domains. Their syntax is
  unchanged, so `admin-conditional-snapshot` v1 and the deployment token
  pattern stay as they are, but every tag issued by v0.9.12 or earlier fails
  closed with `412`. A namespace whose canonical representation exceeds 64 MiB
  (spec bytes count as digest and length) gets `507 Insufficient Storage` on
  `GET /backup?conditional=true`, conditional `POST /restore`,
  `GET /deployment-snapshot` and both conditional deployment mutations.
- **Acknowledgement bodies for `507`.** Deployment `507` bodies use the
  existing acknowledgement members: `durable` is `not_started` for a snapshot
  read or the pre-transaction check and `not_committed` inside the rolled-back
  mutation transaction, with `live: unconfirmed` and
  `recovery_cleanup_authorized: false`.
  `admin-deployment-mutation-acknowledgement` v1 already admits both and gains
  two valid fixtures transcribed from `snapshot_too_large`.

The `ETag` and `If-Match` entries in `gateway-headers.json` describe the new MAC
domains, the `412` for older tags and the `507` bound.

## Checked and unchanged

- `X-Gateway-Error` tokens, `ErrorClass` values, provisioning values and
  plugin registrations are unchanged: `src/retry.rs`, `src/proxy/headers.rs`,
  `src/admin/provisioning.rs`, `src/plugins/builtin_parity.rs` and
  `docs/error_classification.md` are byte-identical to `v0.9.12`, and
  `BUILTIN_PLUGIN_REGISTRATIONS` and `PluginConfigBase` did not change. The
  plugin catalog keeps its 82 plugins and their config pointers, now into the
  `v0.9.13` `openapi.yaml`.
- [#6024](https://github.com/ferrum-edge/ferrum-edge/pull/6024): native HTTP/3
  buffered uploads refused by the shared request-buffer budget return
  `503`/`RESOURCE_EXHAUSTED` with the existing `gateway_buffer_capacity`
  class. `Plugin::early_route_total` and `declares_request_input_mutations`
  are trait methods, not plugins, so the catalog does not change. The new
  `route_request_timeout_early_upload` rejection phase is logged with the
  existing `request_timeout` token; `token_for_rejection_phase` is unchanged.
- [#6015](https://github.com/ferrum-edge/ferrum-edge/pull/6015): a buffered
  gRPC expiry now writes one transaction summary and that path no longer logs
  `authorization_expired_grpc_precommit`. No contract file names that phase.
- `diagnostic-ref` v1 sources (`src/diagnostic_ref.rs` and its OpenAPI
  components) are unchanged at `v0.9.13`. The schema file keeps its frozen v1
  bytes, including its `v0.9.12` provenance, because consumers vendor it
  byte for byte (#19).
- Other owners' schemas, availability notes and fixtures are unchanged.

## Fixtures and validation

`docs/versioning.md` requires each major of a schema to keep its own
fixtures once a second major exists. `backend-egress-policy`,
`vocabulary-backend-egress-policy` and `admin-deployment-snapshot` now keep
`fixtures/<name>/v1/` (the earlier fixtures, byte for byte) and
`fixtures/<name>/v2/`, and `ci/validate.py` checks each directory against its
own major. Schemas with one major keep `fixtures/<name>/{valid,invalid}/`.

New v2 fixtures transcribe the owner's OpenAPI example and integration tests
(`admin_backend_egress_policy_tests.rs`
`public_only_is_never_guaranteed_without_local_enforcement`), and the empty
SQL and MongoDB deployment snapshots with `api_spec_contents: []`. Every new
rule has an invalid fixture, listed in `fixtures/README.md` with its expected
path and keyword. No populated spec bytes or captured tokens are included.

The `Validate contracts` workflow is the conformance gate. Workflow,
permissions, action pins and Python dependencies are unchanged.

## Consumers

A consumer pinned to `contracts-edge-0.9.12` that reads
`GET /backend-egress-policy` or `GET /deployment-snapshot` from Edge `v0.9.13`
needs the v2 schemas. Public-only publishers must recognize `schema_version: 2`
and still require `local-data-plane`; a `schema_version: 1` response fails
closed. Deployment recovery journals must re-read authority after the Edge
upgrade, verify each `api_spec_contents` value against its digest, and treat
`507` as deterministic for unchanged state. Consumer pins are recorded in
[adoption.md](../adoption.md).
