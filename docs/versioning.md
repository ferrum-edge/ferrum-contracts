# Versioning

Two things are versioned here: each contract (by its schema major version)
and the repository as a whole (by release tags pinned to Edge releases).

## Schema versions

A schema lives at `schemas/<name>/v<N>.schema.json`. Its `$id` is
`https://github.com/ferrum-edge/ferrum-contracts/schemas/<name>/v<N>.schema.json`
and its `x-contract` block repeats `name` and `version`. CI rejects a schema
whose file name, `$id` and `x-contract` disagree.

`N` is a major version. Within a major version only these changes are
allowed:

- a new optional property;
- a new value in an enumeration that the schema already declares open (for
  example Alloy's `anyOf` enumerations, which accept unknown strings);
- a clearer `description`, or a tighter pattern that every existing
  producer already meets and every fixture still passes.

Anything else is breaking and needs `v<N+1>.schema.json` next to the old
file: removing or renaming a property, making an optional property
required, adding a value to a closed enumeration (an old consumer would
reject a new producer's payload), or changing the meaning of a value. The
old major stays in the repository until every consumer in
[adoption.md](adoption.md) has moved.

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

## Release tags

Releases are git tags pinned to Edge releases:

| Tag | Meaning |
|---|---|
| `contracts-edge-X.Y.Z` | Contracts as of Ferrum Edge `vX.Y.Z`. Every vocabulary has `edge_release: vX.Y.Z`. |
| `contracts-edge-X.Y.Z-rN` | A later revision for the same Edge release (a fixture fix, a newly adopted non-Edge schema). `N` starts at 2. |

Tags are immutable. A tag is never moved, deleted or re-created; a mistake is
fixed with the next `-rN` tag. Consumers pin a tag, or the commit SHA a tag
points to, never a branch.

The repository has no tag yet. The first planned tag is
`contracts-edge-0.9.8`; see [release-process.md](release-process.md).
