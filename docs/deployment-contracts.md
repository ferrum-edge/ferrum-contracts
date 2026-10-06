# Edge deployment snapshot and mutation contracts

**Published canonical contracts-edge-0.9.12.** Edge `v0.9.12` ships this profile
at `0d917701b63ef38210c49df830f48cf0457cbc7d`, with
[verified distribution](releases/contracts-edge-0.9.12.md). The canonical tag
points to `31f0a21d707795be293d15837c2f77c3d84219d8`, published on 2026-10-05 at
13:58:38 UTC. Publication does not itself record a consumer pin, supported
publisher profile or advisory closure. Nexus #522, Foundry #544 and GitForgeOps
adoption require their own decisions and hosted qualification.

## Immutable owner sources and schema scope

All paths below belong to `ferrum-edge/ferrum-edge` at the full commit above:

| Source | Contract facts |
|---|---|
| [`openapi.yaml`](https://github.com/ferrum-edge/ferrum-edge/blob/0d917701b63ef38210c49df830f48cf0457cbc7d/openapi.yaml) | `/deployment-snapshot`, conditional proxy DELETE/API-spec PUT, `DeploymentSnapshot`, `DeploymentMutationAcknowledgement`, `ConditionalDeployment`, `DeploymentIfMatch`, `DeploymentMutationUnavailable` |
| [`src/admin/deployment_mutations.rs`](https://github.com/ferrum-edge/ferrum-edge/blob/0d917701b63ef38210c49df830f48cf0457cbc7d/src/admin/deployment_mutations.rs) | `parse_request`, keyed token, complete snapshot response, refusal bodies, durable/live/audit/lease acknowledgement |
| [`src/admin/mod.rs`](https://github.com/ferrum-edge/ferrum-edge/blob/0d917701b63ef38210c49df830f48cf0457cbc7d/src/admin/mod.rs), [`src/admin/api_specs/handlers.rs`](https://github.com/ferrum-edge/ferrum-edge/blob/0d917701b63ef38210c49df830f48cf0457cbc7d/src/admin/api_specs/handlers.rs) | Role/namespace/read-only gates, strict route dispatch, ordinary spec body parsing and conditional replacement |
| [`src/config/deployment_mutation.rs`](https://github.com/ferrum-edge/ferrum-edge/blob/0d917701b63ef38210c49df830f48cf0457cbc7d/src/config/deployment_mutation.rs), [`src/config/db_backend.rs`](https://github.com/ferrum-edge/ferrum-edge/blob/0d917701b63ef38210c49df830f48cf0457cbc7d/src/config/db_backend.rs) | Complete comparison representation, target ownership/dependency checks, original expected representation |
| [`src/config/db_loader.rs`](https://github.com/ferrum-edge/ferrum-edge/blob/0d917701b63ef38210c49df830f48cf0457cbc7d/src/config/db_loader.rs), [`src/config/mongo_store.rs`](https://github.com/ferrum-edge/ferrum-edge/blob/0d917701b63ef38210c49df830f48cf0457cbc7d/src/config/mongo_store.rs) | Coherent raw SQL/BSON evidence and entry/commit transaction fences |
| [`src/config/types.rs`](https://github.com/ferrum-edge/ferrum-edge/blob/0d917701b63ef38210c49df830f48cf0457cbc7d/src/config/types.rs) | Typed resources and full `ApiSpec` gzip bytes/external-reference evidence |
| [`docs/deployment_mutations.md`](https://github.com/ferrum-edge/ferrum-edge/blob/0d917701b63ef38210c49df830f48cf0457cbc7d/docs/deployment_mutations.md), [`docs/admin_api.md`](https://github.com/ferrum-edge/ferrum-edge/blob/0d917701b63ef38210c49df830f48cf0457cbc7d/docs/admin_api.md), [`docs/api_specs.md`](https://github.com/ferrum-edge/ferrum-edge/blob/0d917701b63ef38210c49df830f48cf0457cbc7d/docs/api_specs.md) | Owner recovery/adoption and preservation protocol |

The two new schemas transcribe the owner's machine-readable OpenAPI envelopes.
The protocol below transcribes owner code/docs where OpenAPI cannot express
HTTP headers, transaction behavior or consumer recovery decisions. Candidate
wording in the immutable owner docs predates the actual Edge publication;
the release record supplies the later verified facts.

`admin-deployment-snapshot` requires `profile`, `namespace`, `namespace_etag`,
`evidence`, `proxies`, `upstreams`, `plugin_configs` and `api_specs`. The owner
leaves the envelope, evidence and resource objects open. This schema preserves
that policy: it does not close raw metadata, invent nested required members,
or certify that a schema-valid object contains complete evidence. Its exact
quoted token pattern follows `parse_request`, including rejection of trailing
control bytes. Empty SQL and replica-set MongoDB fixtures transcribe the two
complete empty-state representations, with illustrative non-authorizing tokens.
They are not captured populated secret-bearing snapshots.

`admin-deployment-mutation-acknowledgement` requires exactly the three members
required by OpenAPI: `durable`, `live`, `recovery_cleanup_authorized`. `profile`,
`id` and `error` remain optional because owner refusals can omit profile/target.
Additional members remain open. A source-derived implication asserts that a
true cleanup flag requires `durable=committed` and `live=applied`. A consumer
must additionally require HTTP 200 and the expected profile/target; JSON
validation cannot attest status, audit admission, lease release or application.
The owner emits no `conditional_request` or `cleanup_safe` wire fields; use its
actual discriminator and acknowledgement members rather than inferred aliases.

## Complete original authority

Read `GET /deployment-snapshot` with an admin-role JWT and the intended
`X-Ferrum-Namespace`. No query string or resource filter is accepted. A success
is HTTP 200 with `Cache-Control: no-store` and exactly one strong quoted
`ETag` equal to `namespace_etag`: `"deployment-v1-<32 lowercase hex digits>"`.
Security audit admission precedes disclosure, independently of ordinary audit
enablement. There is no cached fallback. Missing/unavailable/undecodable state
is 503; standalone MongoDB is 501. Existing authentication, namespace and
read-only/topology gates remain authoritative.

The response is secret-complete. Keep the entire original response and token
encrypted, and exclude them from routine logs. Typed inspection arrays come
from the same primary snapshot as `evidence`. Full stored `api_specs` include
`spec_content` as numeric gzip bytes, content encoding/hash/size, ownership and
metadata, plus any stored `external_ref_snapshot` bytes and
`external_ref_digest`. A redacted projection or ordinary spec GET cannot replace
this original dependency authority.

The comparison representation is an object with `profile`, `resources` and
`stored`. `resources` is the owner's ordered tuple: proxies, consumers,
upstreams, plugin configs, trust bundles, specs, namespace record (or null),
and durable change watermark. It binds complete historical credentials and
associations, not just the target proxy. Reverted changes and delete/recreate
invalidate authority; lease maintenance and audit records do not.

SQL `stored` includes every column in `proxies`, `consumers`, `upstreams`,
`plugin_configs`, `proxy_plugins`, `api_specs`, `gateway_trust_bundles`,
`consumer_identity_index`, `consumer_credential_index` and `namespaces`.
Each column retains `column_type`, runtime `value_type` and lossless `value`;
typed nulls, float bits and blob bytes are preserved. MongoDB covers the
resource/spec/trust/identity/namespace collections with both `document` and
`bson_hex`, including embedded association metadata. Its credential
representations and uniqueness hashes live on consumer documents, rather
than a separate credential-index collection.

Unknown metadata in supported associations and arbitrary credential/config
maps is retained and fenced. An unrepresentable top-level MongoDB resource
shape refuses authority rather than dropping fields. Unknown collections are
not represented as deployable resources or mutated by this profile. The
schema's open objects do not override those owner representability checks.
This is a response/evidence contract; it grants no acceptance of a consumer's
`FullSnapshotSecretsDTO` as a mutation/restore request, no plaintext replacement
route, and no extra baseline-membership requirement.

Tokens use a distinct keyed `deployment-v1-` profile under the admin JWT secret;
replicas must share that secret and rotation invalidates authority. The
[conditional backup contract](admin-contracts.md) retains its own namespace
and row-tag semantics. Neither its namespace token nor any row token
authorizes deployment mutation, and this response does not authorize restore.

## Strict partial writes

Compare the complete original target specification, proxy, generated plugin
bodies, associations and stored external-reference evidence against the intended
deployment before sending its original token on exactly one `If-Match` field:

```text
DELETE /proxies/{id}?conditional=true&cleanup_orphaned_upstream=false
PUT /api-specs/{id}?conditional=true
```

Removal requires operator role; replacement requires admin role. Both require
namespace authorization and the existing writable/topology gates. PUT takes
the ordinary OpenAPI JSON/YAML body and preserves proxy identity. Exactly one
`conditional=true` is required; DELETE additionally requires exactly one
`cleanup_orphaned_upstream=false`. At most one `apply=sync` is supported.
Unknown/duplicate/invalid parameters, `apply=async`, missing/duplicate/list/
weak/wildcard/wrong-profile headers and a deployment token without its mode
return 400. Other mutation routes refuse deployment mode. No refusal falls
back to ordinary DELETE, ordinary PUT, or restore-minus-target.

Stale original authority returns 412 without mutation. This includes target
hosts, plugins, document-only spec fields and unrelated namespace changes.
Original evidence is compared inside the selected transaction under live
entry/commit admission fences on SQLite, PostgreSQL, MySQL and replica-set
MongoDB. Driver retries retain the original expected representation. Missing
or inconsistent ownership/dependencies and proven external references to
spec-owned upstreams refuse with 409 before selected writes. Unsupported
atomic topology is 501; unavailable/uncertain state or acknowledgements are
503. Ordinary validation/authentication errors can retain their legacy bodies.

Removal affects only the selected cascade. Hand-owned last-referenced upstreams
and shared association owners survive; no namespace orphan sweeper runs.
Replacement preserves unrelated resources, hand-added plugin rows/associations,
supported unknown metadata, historical credentials, trust revisions and
unchanged surviving timestamps. Matching resource bundles update spec metadata
and record a covering proxy change for this profile's acknowledgement. Neither
operation prepares a whole-namespace restore or performs late compensation.

## Explicit acknowledgement and retained recovery state

| Result | HTTP | `durable` | `live` | `recovery_cleanup_authorized` |
|---|---|---|---|---|
| Confirmed commit, covering local application, final audit admission and lease release | 200 | `committed` | `applied` | `true` |
| Confirmed CP/unserved/no serving coordinator commit | 200 | `committed` | `not_applicable` | `false` |
| Confirmed commit but live/audit/cursor/lease acknowledgement unavailable | 503 | `committed` | `unconfirmed` | `false` |
| Store/transport acknowledgement uncertain | 503 if available | `unknown` | `unconfirmed` | `false` |
| Stale evidence or dependency/ownership refusal | 412/409 | `not_committed` | `unconfirmed` | `false` |
| Initial mode/evidence/admission failure | 400/503 | `not_started` | `unconfirmed` | `false` |

Only a complete HTTP 200 acknowledgement with expected `profile=deployment-v1`
and target `id`, `durable=committed`, `live=applied` and explicit
`recovery_cleanup_authorized=true` permits automatic journal removal or
dependent cleanup. A covering local result carries `X-Ferrum-Config-Cursor`;
it does not attest every remote DP. CP consumers must independently qualify
downstream application while retaining recovery state.

Retain the encrypted original journal after every refusal, false or missing
flag, missing/unknown status, wrong profile/target, committed-but-not-live result,
audit/lease failure, cancellation or lost transport. Cancellation can leave an
owned transaction settling on the server. No 503 or fresh snapshot authorizes
automatic replay. Reconciliation may inspect current state; never refresh a
token solely to make the original destructive action pass.

This profile does not include unfinished Edge #6011 rejection-contract work.
The existing token vocabulary and ordinary error contracts remain those in the
released owner source. Public-only publisher profile decisions, Nexus Part B,
consumer adoption and packaged/four-store qualification remain separate work.
