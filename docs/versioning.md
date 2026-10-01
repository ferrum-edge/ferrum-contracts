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
`schema_version: 1.x`, and `schema: ferrum.service_manifest` with
`schema_version: 1.x`. The contract major matches the payload major.

Fixtures under `fixtures/<name>/` are checked against the latest major of
`<name>`. When a second major is added, its fixtures move to
`fixtures/<name>/v<N>/` and `ci/validate.py` is extended in the same PR.

## Vocabulary versions

A vocabulary file's `version` is the version of its shape
(`schemas/vocabulary-<name>/v<version>.schema.json`), not of its values.
The values change with Edge releases; `edge_release` names the Edge tag they
were read from. A vocabulary may also list entries that exist only on Edge
`main`; those are marked (`availability: unreleased`, or the
`main_branch_delta` block) and are never presented as released.

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

Consumers that need the Alloy-owned `[agents]` section of `service-manifest`
pin `contracts-edge-0.9.9-r2`; it is otherwise identical to
`contracts-edge-0.9.9`.

A non-Edge contract change, such as the Alloy-owned `[agents]` addition to
`service-manifest` in #8, is released as a revision of the latest applicable
Edge tag. Under the revision rule above, #8 is released as
`contracts-edge-0.9.9-r2`; it retains the Edge v0.9.9 mapping (and so also
v0.9.10) and does not claim that the change shipped in Edge.

See [release-process.md](release-process.md) for the release steps.
