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
| [`ci/`](ci) | Validator (`validate.py`), its tests and hash-pinned requirements; the workflow is [`.github/workflows/validate.yml`](.github/workflows/validate.yml) |
| [`vocabularies/`](vocabularies) | Edge-owned vocabularies: `ErrorClass` and `X-Gateway-Error` tokens, gateway-owned headers, `provisioned-by` values, and the plugin catalog index |
| [`schemas/`](schemas) | JSON Schemas (2020-12), one directory per contract, one file per major version |
| [`fixtures/`](fixtures) | Payloads producers must emit and consumers must accept (`valid/`) or reject (`invalid/`); one `v<N>/` directory per major when a schema has several |
| [`docs/ownership.md`](docs/ownership.md) | Who owns each contract and how changes land |
| [`docs/versioning.md`](docs/versioning.md) | Schema versions and `contracts-edge-X.Y.Z` tags |
| [`docs/adoption.md`](docs/adoption.md) | Consumer pins, qualification evidence and remaining contract gaps |
| [`docs/release-process.md`](docs/release-process.md) | How a release is cut after an Edge release |
| [`docs/admin-contracts.md`](docs/admin-contracts.md) | Authoritative conditional snapshots, restore preconditions, namespace-scoped admin authorization and process egress discovery |
| [`docs/deployment-contracts.md`](docs/deployment-contracts.md) | Original deployment authority, dependency-fenced partial writes and explicit cleanup acknowledgements |
| [`docs/plugin-config-admission.md`](docs/plugin-config-admission.md) | Edge plugin configuration admission changes reached through the plugin catalog's pinned `openapi.yaml` |
| [`docs/release-signing.md`](docs/release-signing.md) | Signed release tags: signer setup, consumer verification, rotation and revocation; trust policy in [`docs/allowed_signers`](docs/allowed_signers) and [`docs/revoked_signers`](docs/revoked_signers) |
| [`docs/releases/`](docs/releases) | Release records from `contracts-edge-0.9.11` on: Edge source, changes and what stayed unchanged |

Every file records where it came from: owner repository, path, and commit.
Latest: [`contracts-edge-0.9.19`](docs/releases/contracts-edge-0.9.19.md), for
Edge `v0.9.19` (Edge commit `510ce7121c3d9754110d330a30a3bd9b7a7b278e`). There
is no `contracts-edge-0.9.18`: Edge `v0.9.18` was tagged but never published.
Release history: [`CHANGELOG.md`](CHANGELOG.md) and [`docs/releases/`](docs/releases);
Edge-to-tag mapping: [docs/versioning.md](docs/versioning.md#release-tags).

## Consumers

See [docs/adoption.md](docs/adoption.md) for each consumer's pinned tag,
adoption status and remaining contract gaps.

## License

[PolyForm Noncommercial 1.0.0](LICENSE), the same as the rest of the suite.
