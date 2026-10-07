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
`@@EDGE_0914_COMMIT@@`. A control plane's egress response gains the optional
`data_plane_attestation` object within `schema_version: 2`, and the conditional
backup `ETag` is documented as a namespace state token. Both are described
below; the backup metadata shape is unchanged.

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
together with every expected data-plane `node_id` present in `data_planes`.
`connected_data_planes` counts streams, so a reconnect overlap can double-count
one node and a matching count alone does not prove that no node is missing; an
absent object, an unknown attestation status or an empty set
blocks publication. Missing/unknown
versions, labels or fields, authorization failure, unserved/CP-only scopes and
weaker policy block publication. Unknown values grant no known meaning or
permission. This is loaded-policy metadata, not external firewall attestation,
DNS ownership, a socket test or new enforcement on any outbound path. Existing
enforcement-path limitations in the owner's configuration docs remain applicable.
