# Versioning

Two things are versioned here: each contract (by its schema major version)
and the repository as a whole (by release tags pinned to Edge releases).

## Schema versions

A schema lives at `schemas/<name>/v<N>.schema.json`. Its `$id` is
`https://github.com/ferrum-edge/ferrum-contracts/schemas/<name>/v<N>.schema.json`
and its `x-contract` block repeats `name` and `version`. CI rejects a schema
whose file name, `$id` and `x-contract` disagree.

The `$id` URLs are identifiers, not locations: nothing is served at them, and
a request to one returns 404. Resolve a schema by its path in a pinned tag
(for example
`https://raw.githubusercontent.com/ferrum-edge/ferrum-contracts/contracts-edge-0.9.8/schemas/diagnostic-ref/v1.schema.json`),
or load the files into your validator's schema registry by `$id`.

`N` is a major version. Within a major version only these changes are
allowed:

- a new optional property;
- a new value in an enumeration that the schema already declares open (for
  example Alloy's `anyOf` enumerations, which accept unknown strings);
- a clearer `description`, or a tighter pattern that every existing
  producer already meets and every fixture still passes;
- a new value in a closed enumeration that mirrors an Edge-owned
  vocabulary, under the rule in [Closed enumerations](#closed-enumerations).

Anything else is breaking and needs `v<N+1>.schema.json` next to the old
file: removing or renaming a property or a value, making an optional
property required, adding a value to any other closed enumeration, or
changing the meaning of a value. The old major stays in the repository
until every consumer in [adoption.md](adoption.md) has moved.

## Closed enumerations

Some schemas copy a closed Edge vocabulary. `diagnostic-ref` v1 lists the
eight `X-Gateway-Error` tokens in `gateway_error`, exactly as Edge's own
`openapi.yaml` does, and CI fails if that list and
`vocabularies/gateway-errors.json` differ.

On Edge's side a new token is additive: Edge v0.9.8 added `request_timeout`
without changing anything else. Contracts follow the same rule:

- **A token or class Edge adds is not a new major.** It is added to the
  vocabulary and to every schema enumeration that copies it, in the release
  tag for the Edge version that ships it, and listed under "Added" in
  `CHANGELOG.md`. The tag is what binds a consumer to an Edge release, so a
  consumer pinned to `contracts-edge-0.9.8` keeps validating exactly what
  Edge v0.9.8 emits.
- **Schemas stay closed; readers stay open.** The closed enumeration is the
  producer contract for that Edge release. A consumer that may meet a newer
  Edge than its pin must treat an unknown value as "unknown" (not as an
  error and never as any known value) when it interprets a payload, and
  should validate against the schema only in its own conformance tests.
  Alloy's schemas use the same strategy explicitly, with `anyOf` open
  enumerations.
- **Removing, renaming or re-meaning a value is breaking** and needs a new
  major of every schema that copies it.

Payloads that carry their own version keep it: `schema_version:
ferrum.diagnostic_ref.v1`, `schema: ferrum.diagnostic_report` with
`schema_version: 1.x`, `schema: ferrum.service_manifest` with
`schema_version: 1.x`, and the backend egress response's integer
`schema_version` (1 in `backend-egress-policy` v1, 2 in v2). The contract
major matches the payload major.

A schema with one major keeps its fixtures in `fixtures/<name>/valid/` and
`fixtures/<name>/invalid/`. Once a schema has a second major, every major keeps
its own fixtures in `fixtures/<name>/v<N>/valid/` and
`fixtures/<name>/v<N>/invalid/`, and `ci/validate.py` checks each directory
against its own major. `contracts-edge-0.9.13` introduced this layout for
`backend-egress-policy`, `vocabulary-backend-egress-policy` and
`admin-deployment-snapshot`.

### Majors added in contracts-edge-0.9.13

Edge `v0.9.13` changed two Edge-owned responses incompatibly, so each gets a
new major and keeps its v1 file for consumers of earlier Edge releases:

- `backend-egress-policy` v2: Edge emits `schema_version: 2` only, and
  `public_only_guaranteed` changes meaning (it now also requires
  `enforcement_scope=local-data-plane`). Removing a value and changing a
  value's meaning are breaking. The vocabulary shape follows as
  `vocabulary-backend-egress-policy` v2, and `vocabularies/backend-egress-policy.json`
  has `version: 2`.
- `admin-deployment-snapshot` v2: `api_spec_contents` becomes a required
  member and `api_specs[].spec_content` changes from a byte array to a
  `StoredContentDigest`. Both are breaking.

`admin-conditional-snapshot` and `admin-deployment-mutation-acknowledgement`
stay at v1: their wire shape did not change. Their tokens and bodies follow the
owner's runtime rules for the release a consumer talks to (for example, Edge
`v0.9.13` rejects tokens issued by `v0.9.12` with `412`).

### Additions in contracts-edge-0.9.14

Edge `v0.9.14` adds the CP-only `data_plane_attestation` object to the backend
egress response without changing `schema_version: 2`, and narrows which
failures report deployment `durable: unknown` without changing the enum. Both
fit within the current majors: `backend-egress-policy` v2 and
`vocabulary-backend-egress-policy` v2 gain optional properties, and
`admin-deployment-mutation-acknowledgement` v1 gains descriptions. The closed
v2 response schema in `contracts-edge-0.9.13` rejects a v0.9.14 CP response
that carries the object; that is the tag binding a consumer to the Edge release
it names. The new `ErrorClass` assignments for HTTP/2 resets and buffered read
errors reuse existing values, so `gateway-errors.json` only notes them.

## Vocabulary versions

A vocabulary file's `version` is the version of its shape
(`schemas/vocabulary-<name>/v<version>.schema.json`), not of its values.
The values change with Edge releases; `edge_release` names the Edge tag they
were read from. A vocabulary may also list entries that exist only on Edge
`main`; those are marked (`availability: unreleased`, or the
`main_branch_delta` block) and are never presented as released.

For the [published 0.9.11 release](releases/contracts-edge-0.9.11.md),
`edge_release: v0.9.11` identifies the actual immutable tagged owner source
`c764084b3b51c3f7ffde268c039688d35e49c553`. Edge distribution is recorded in
the Edge release itself. The canonical contracts tag points to
`390edbd5b2485af0988e02f7827fde778d76ae0a` and was published on 2026-10-04.
Prepared/pending schema annotations captured in that immutable source are
historical pre-publication wording, not a new approval requirement. Existing
first-availability entries and immutable released tag bytes stay historical.

Backend egress response version 2, current from Edge v0.9.13, and
`ferrum-private-reserved-v1` identify the owner's exact classifier and label
meanings. Version 2 narrowed `public_only_guaranteed` to local data-plane
enforcement; version 1 is retained for Edge v0.9.11 and v0.9.12. A change of
meaning requires versioned coordination. Producer labels remain strict; unknown labels grant
no known meaning or permission. Public-only publication additionally fails
closed on missing/unknown policy data, an unexpected namespace, a non-serving
scope or a false guarantee, as [the owner contract](admin-contracts.md) requires.
This safety decision does not turn an unknown label into a known class.

Conditional metadata v1 checks quoted strong token syntax and all four maps.
It cannot distinguish cryptographic row/namespace bindings or authorize restore;
the owner's HTTP precondition and transaction semantics remain authoritative.

The [published 0.9.12 release](releases/contracts-edge-0.9.12.md) refreshes all
five vocabulary `edge_release`/current Edge source pins to actually released
`v0.9.12`, `0d917701b63ef38210c49df830f48cf0457cbc7d`. The canonical
`contracts-edge-0.9.12` tag points to `31f0a21d707795be293d15837c2f77c3d84219d8`
and was published on 2026-10-05. First availability,
historical fixtures and other-owner unreleased annotations are preserved.
Deployment snapshot and acknowledgement are new v1 contracts; they do not
change the meaning of `admin-conditional-snapshot` v1. Their original strong
`deployment-v1-` token cannot substitute for backup namespace or row authority.
Open raw evidence/resource objects follow owner OpenAPI; producer labels are
strict and unknown acknowledgement states grant no cleanup/replay authority.
See [deployment-contracts.md](deployment-contracts.md) for runtime requirements.

## Formats

`format` is asserted, not only annotated: CI validates with jsonschema's
format checker, and `ci/validate.py` collects every `format` the schemas use
and fails if any JSON Schema 2020-12 standard format has no registered
checker (`date-time` needs the hash-pinned `rfc3339-validator`; `regex` is
built in). Formats outside that standard, such as Anvil's generated
`uint32`, remain annotations. Consumers that validate should enable format
assertion too.

## Release tags

Releases are git tags pinned to Edge releases:

| Tag | Meaning |
|---|---|
| `contracts-edge-X.Y.Z` | Contracts as of Ferrum Edge `vX.Y.Z`. Every vocabulary has `edge_release: vX.Y.Z`. |
| `contracts-edge-X.Y.Z-rN` | A later revision for the same Edge release (a fixture fix, a newly adopted non-Edge schema). `N` starts at 2. |

Tags are immutable. A tag is never moved, deleted or re-created; a mistake is
fixed with the next `-rN` tag. The repository's active "Immutable release
tags" ruleset enforces this: it blocks update and deletion of tags matching
`v*` and `contracts-*`. Consumers pin a tag, or the commit SHA a tag points
to, never a branch.

A `contracts-edge-X.Y.Z` tag describes Edge `vX.Y.Z`, but it may also carry
items that Edge has only on `main`, provided they are marked unreleased. A
consumer must not assume that an unreleased item exists on the Edge release
its tag names.

An Edge release that changes no contract source maps to the latest
`contracts-edge-*` tag and does not need a new tag. For example, Edge v0.9.10
contains no contract-source changes after v0.9.9, so it maps to
`contracts-edge-0.9.9`.

| Edge release | Contracts tag | Reason |
|---|---|---|
| `v0.9.8` | `contracts-edge-0.9.8` | Initial Edge-aligned contracts release |
| `v0.9.9` | `contracts-edge-0.9.9` | Refreshed Edge-owned contract sources |
| `v0.9.10` | `contracts-edge-0.9.9` | No contract-source changes after v0.9.9 |
| `v0.9.11` | `contracts-edge-0.9.11` | Edge admin contracts and accepted unchanged shared v1 freeze at `390edbd5b2485af0988e02f7827fde778d76ae0a` |
| `v0.9.12` | `contracts-edge-0.9.12` | Refreshed Edge-owned sources and deployment-v1 contracts from released owner `0d917701b63ef38210c49df830f48cf0457cbc7d`, tagged at `31f0a21d707795be293d15837c2f77c3d84219d8` |
| `v0.9.13` | `contracts-edge-0.9.13` | Backend egress policy v2 and deployment snapshot v2 from released owner `9b83115de7ec23ab51ec4feae6bed65e596db425`, tagged on the merge commit of its release PR |
| `v0.9.14` | `contracts-edge-0.9.14` | Optional CP `data_plane_attestation` within backend egress policy v2, narrowed deployment `durable` outcomes and error-classification notes from released owner `9bd4d5f9caa4ebe8f0ea13e76d8a6e2172eaca7d`, tagged on the merge commit of its release PR |

Consumers that need the Alloy-owned `[agents]` section of `service-manifest`
pin `contracts-edge-0.9.9-r2`; it is otherwise identical to
`contracts-edge-0.9.9`.

A non-Edge contract change, such as the Alloy-owned `[agents]` addition to
`service-manifest` in #8, is released as a revision of the latest applicable
Edge tag. Under the revision rule above, #8 is released as
`contracts-edge-0.9.9-r2`; it retains the Edge v0.9.9 mapping (and so also
v0.9.10) and does not claim that the change shipped in Edge.

`contracts-edge-0.9.14` is the latest tag, on the merge commit of its release
PR; its GitHub release records the tag commit. `contracts-edge-0.9.13` is on
the merge commit of its own release PR. `contracts-edge-0.9.12` is at
`31f0a21d707795be293d15837c2f77c3d84219d8`. [PR #15](https://github.com/ferrum-edge/ferrum-contracts/pull/15)
merged on 2026-10-05 at 13:57:00 UTC with exact reviewed second parent
`d9c84810152732524c54a9ed292dc59103f0619d` and that reviewed head's tree. Its
final-head hosted [run 37319873697](https://github.com/ferrum-edge/ferrum-contracts/actions/runs/37319873697)
and the sole applicable main PUSH [run 37320780987](https://github.com/ferrum-edge/ferrum-contracts/actions/runs/37320780987)
succeeded before tag creation; [release 403772929](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.12)
was published at 13:58:38 UTC. Historical
[`contracts-edge-0.9.11`](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.11)
remains at `390edbd5b2485af0988e02f7827fde778d76ae0a`, published on 2026-10-04
at 22:41:21 UTC. Historical 0.9.8, 0.9.9, 0.9.10 and r2 mappings remain unchanged.

Root has accepted the unchanged shared Alloy v1 freeze after reviewed owner and
consumer qualification. The release records **EXISTING**/implemented shared v1
metadata at owner `81cbb410d34ff5fba1f3d54cfd2e7ebccaed397e`, while retaining
owner-unreleased availability. Wire fields, bounds, fixtures and unknown-member/
open-enum reader behavior are unchanged. Full report parity includes descriptions
outside `$id`/`x-contract`, including historical PROPOSED wording in the owner
copy. Alloy remains unpublished, and the canonical publication grants no separate
Alloy crate publishing approval. Consumers continue using their recorded immutable
pins until their adoption PRs merge and qualify; publication alone does not update
those pins. Prepared/pending wording in the tagged source records the earlier
pre-publication state. See the release record for the subsequent publication facts.

See [release-process.md](release-process.md) for the release steps.
