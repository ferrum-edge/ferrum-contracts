# Ferrum contracts

Versioned wire contracts shared by the Ferrum products:
[Edge](https://github.com/ferrum-edge/ferrum-edge),
[Anvil](https://github.com/ferrum-edge/ferrum-anvil),
[Alloy](https://github.com/ferrum-edge/ferrum-alloy),
[Nexus](https://github.com/ferrum-edge/ferrum-nexus),
[Foundry](https://github.com/ferrum-edge/ferrum-foundry) and
[GitForgeOps](https://github.com/ferrum-edge/ferrum-edge-git-forge-ops).

The contracts are kept as data, not prose: JSON Schemas, machine-readable
vocabularies, and conformance fixtures. Each product pins a tagged release,
and its CI fails when its local copy drifts from the pinned contract.

The proposal and adoption work tracked by
[ferrum-edge/.github#4](https://github.com/ferrum-edge/.github/issues/4) is
complete; the issue is closed and remains as project history.

## Contents

| Path | What |
|---|---|
| [`AGENTS.md`](AGENTS.md) | Repository guidance for contract provenance, schemas and releases |
| [`CHANGELOG.md`](CHANGELOG.md) | Changes recorded by contracts release |
| [`ci/`](ci) | Contract validation workflow and pinned dependencies |
| [`vocabularies/`](vocabularies) | Edge-owned vocabularies: `ErrorClass` and `X-Gateway-Error` tokens, gateway-owned headers, `provisioned-by` values, and the plugin catalog index |
| [`schemas/`](schemas) | JSON Schemas (2020-12), one directory per contract, one file per major version |
| [`fixtures/`](fixtures) | Payloads producers must emit and consumers must accept (`valid/`) or reject (`invalid/`) |
| [`docs/ownership.md`](docs/ownership.md) | Who owns each contract and how changes land |
| [`docs/versioning.md`](docs/versioning.md) | Schema versions and `contracts-edge-X.Y.Z` tags |
| [`docs/adoption.md`](docs/adoption.md) | Consumer pins, qualification evidence and remaining contract gaps |
| [`docs/release-process.md`](docs/release-process.md) | How a release is cut after an Edge release |
| [`docs/admin-contracts.md`](docs/admin-contracts.md) | Authoritative conditional snapshots, restore preconditions and process egress discovery |
| [`docs/releases/contracts-edge-0.9.11.md`](docs/releases/contracts-edge-0.9.11.md) | Prepared release notes, verified distribution/owner evidence and remaining publication gates |

Every file records where it came from: owner repository, path, and commit.
The latest published contracts release is
[`contracts-edge-0.9.9-r2`](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.9-r2),
which adds Alloy's optional service-manifest `[agents]` section to
[`contracts-edge-0.9.9`](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.9).
Both map to published Edge v0.9.9 and v0.9.10. The initial
[`contracts-edge-0.9.8`](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.8)
release remains available. This branch prepares `contracts-edge-0.9.11` from
Edge's actual unsigned lightweight `v0.9.11` tag at
`c764084b3b51c3f7ffde268c039688d35e49c553`. Edge's release assets, digests,
image identities, attestations and ABI gates are verified. Alloy owner
`81cbb410d34ff5fba1f3d54cfd2e7ebccaed397e` is qualified, and root has accepted
the unchanged shared v1 freeze. The canonical PR remains **DRAFT**, unmerged
and unpublished pending final review, hosted validation and publication gates.
Existing consumer pins are unchanged. See the [release record](docs/releases/contracts-edge-0.9.11.md).

The candidate adds metadata schemas for coherent admin conditional backup and
process-scoped backend egress discovery, plus the egress vocabulary and sanitized
fixtures. Standard HTTP `ETag`/`If-Match` admin semantics are documented against
the owner implementation. JSON validation checks shape and owner-derived
invariants; authorization, token validity and serving-DP enforcement remain
runtime requirements in [the admin contract](docs/admin-contracts.md).

## Consumers

See [docs/adoption.md](docs/adoption.md) for each consumer's pinned tag,
adoption status and remaining contract gaps.

The 2026-10-04 snapshot records qualified Anvil diagnostic import, GitForgeOps
validation of actual Alloy-generated resource trees, and Nexus/Foundry manifest
previews with their bounded trust and presentation rules. Anvil, Alloy and
Foundry pin r2; Nexus pins r2 for manifests and 0.9.9 for vocabularies;
GitForgeOps pins 0.9.9. The candidate marks the shared diagnostic report and
service manifest **EXISTING**/implemented after root's accepted coordinated v1
freeze, preserving all wire fields, bounds, fixtures and reader behavior.
Historical r2 metadata stays unchanged. Alloy remains unpublished; this decision
grants no separate crate publishing approval. [Alloy #27](https://github.com/ferrum-edge/ferrum-alloy/issues/27)
remains open for root disposition after canonical publication and adoption.

## License

[PolyForm Noncommercial 1.0.0](LICENSE), the same as the rest of the suite.
