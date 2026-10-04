# Edge admin snapshot and egress contracts

**Draft contracts-edge-0.9.11 candidate.** These surfaces exist at the immutable
Edge `v0.9.11` source commit `c764084b3b51c3f7ffde268c039688d35e49c553`.
Upstream publication evidence and the canonical release are pending root
verification; no consumer adoption of this candidate is asserted.

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
`ConsumerVerification`. This candidate does not substitute a narrower
credential model or validate authorization as JSON. `ETag` and `If-Match` are
standard HTTP headers; `gateway-headers.json` records Edge's admin semantics.

## Authoritative verification and replacement

| Route | Successful behavior | Refusals |
|---|---|---|
| `GET /consumers/{id}/verification` | `200`: admin-role, namespace-authorized read of the complete stored consumer and matching strong row `ETag`; security audit admission before response; `Cache-Control: no-store`; no cached fallback | `400` invalid input; `401` missing/invalid JWT; `403` role/namespace denial; `404` absent consumer; `503` unavailable authoritative state, tag key or audit admission |
| `GET /backup?conditional=true` | `200`: full unfiltered primary transaction snapshot; exact stored consumer fields; all four row-tag maps; header `ETag` equals `conditional.namespace_etag`; audit admission before response; `Cache-Control: no-store`; no cached fallback | `400` invalid opt-in/filter/namespace; `401` authentication; `403` authorization; `501` unsupported MongoDB topology; `503` unavailable authoritative snapshot, tag key or audit admission |
| `POST /restore?confirm=true` with namespace `If-Match` | Atomic compare and complete replacement in one transaction, including empty replacement and lease entry/commit fences; existing restore/live-apply response semantics; no new response `ETag` | `412` stale or weak-only tag; `400` malformed/empty header or wildcard; `501` unsupported topology; `503` unavailable state/lease; existing authentication, admission, body-size, confirmation, conflict and live-apply failures still apply |

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

`schemas/backend-egress-policy/v1.schema.json` transcribes
`BackendEgressPolicyResponse`; `vocabularies/backend-egress-policy.json` records
its v1 labels. Their common label/order definitions prevent vocabulary and
response drift without changing CI. The schema also asserts the handler's
exact mode class lists and guarantee calculation.

Validators must register both `backend-egress-policy/v1.schema.json` and
`vocabulary-backend-egress-policy/v1.schema.json` by `$id` from the same
immutable canonical pin. Response references resolve to the latter's `$defs`;
the identifier URLs are not served documents (see [versioning.md](versioning.md)).

`GET /backend-egress-policy` returns `200` with `Cache-Control: no-store`.
Viewer, operator and admin JWTs, including viewer-key JWTs, can read it on
writable/read-only listeners. Metrics tokens/CIDR allowlists and anonymous
requests cannot authorize it. Invalid namespace is `400`, missing/invalid JWT
is `401`, namespace claim/ceiling denial is `403`, with no policy fields.
A present `ns` claim always constrains this read even when claim enforcement
is off; missing claims are denied when enforcement is on. The namespace need
not have stored resources; an absent namespace header selects `ferrum`.

The response has `schema_version=1`,
`ip_classification=ferrum-private-reserved-v1`, and `policy_scope=process`.
It reads the immutable loaded policy from the serving `ProxyState`, otherwise
the loaded admin admission policy. It does not reread environment strings;
reloads do not change policy, and changes require process restart. No raw
CIDRs, addresses, counts, backend names, credentials or DNS probes are returned.

| `enforcement_scope` | Meaning |
|---|---|
| `local-data-plane` | This process serves the selected namespace |
| `unserved-namespace` | Its local data plane serves another namespace |
| `admission-only` | CP admission policy without a local proxy; no DP attestation |
| `no-data-plane` | No local proxy or CP admission scope, including node agents |

| `mode` | Allowed classes at the mode stage | Blocked classes at the mode stage |
|---|---|---|
| `both` (production default) | `public`, `private-reserved` | none |
| `public` | `public` | `private-reserved` |
| `private` | `private-reserved` | `public` |

`private-reserved` is Edge's versioned `is_private_ip` classifier, and `public`
is its complement. The pinned owner docs/code define exact IPv4/IPv6 ranges,
globally reachable IETF exceptions and recognized IPv4 embeddings. This
candidate adds no second classifier. Changes to classifier meaning require
versioned contract coordination.

Evaluation is fixed first-match precedence: `allow-cidrs`, `deny-cidrs`,
`dangerous-ranges`, `ip-mode`. Recognized embedded IPv4 candidates are checked;
ambiguous local-use NAT64 must pass both decodings and the literal IPv6 policy.
Explicit allows can bypass the deny overlay, dangerous baseline and mode.
The dangerous-range flag defaults true but still permits ordinary
loopback/RFC1918/ULA under `both`; it alone never establishes public-only egress.
The overlay flags disclose only whether loaded lists are nonempty.

`public_only_guaranteed` is true exactly when `mode=public` and
`allow_cidr_overrides_present=false`. Deny overrides only restrict. Even a
wholly public undisclosed allow list produces false; false does not prove a
private address is reachable. The schema accepts a true guarantee on CP
metadata because that is a policy fact, but CP metadata never attests its DPs.

A public-only publisher must recognize the complete v1 vocabulary, match its
namespace, require `local-data-plane` and `public_only_guaranteed=true`, and
check every serving DP again after replacement/restart. Missing/unknown
versions, labels or fields, authorization failure, unserved/CP-only scopes and
weaker policy block publication. Unknown values grant no known meaning or
permission. This is loaded-policy metadata, not external firewall attestation,
DNS ownership, a socket test or new enforcement on any outbound path. Existing
enforcement-path limitations in the owner's configuration docs remain applicable.
