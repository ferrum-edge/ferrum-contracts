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
| [`.agents/skills/`](.agents/skills) | Agent dispatch skills (Claude entrypoints in [`.claude/skills/`](.claude/skills)); repository tooling, not contract content |
| [`ci/`](ci) | Validator (`validate.py`), its tests and hash-pinned requirements; the workflow is [`.github/workflows/validate.yml`](.github/workflows/validate.yml) |
| [`vocabularies/`](vocabularies) | Edge-owned vocabularies: `ErrorClass` and `X-Gateway-Error` tokens, gateway-owned headers, `provisioned-by` values, the plugin catalog index, plugin config sensitivity, reserved header names, and `x-ferrum-mcp` bridge admission |
| [`schemas/`](schemas) | JSON Schemas (2020-12), one directory per contract, one file per major version |
| [`fixtures/`](fixtures) | Payloads producers must emit and consumers must accept (`valid/`) or reject (`invalid/`); one `v<N>/` directory per major when a schema has several |
| [`qualification/`](qualification) | Producer outcomes for payloads the schema accepts but the producer may refuse (rules applied after defaults); not fixtures |
| [`docs/ownership.md`](docs/ownership.md) | Who owns each contract and how changes land |
| [`docs/versioning.md`](docs/versioning.md) | Schema versions, `contracts-edge-X.Y.Z` tags, the Edge release-candidate policy and the `contracts-edge-1.*` stability promise |
| [`docs/adoption.md`](docs/adoption.md) | Consumer pins, qualification evidence and remaining contract gaps |
| [`docs/consumer-pins.md`](docs/consumer-pins.md) | The consumer `PIN` file format and the checks every consumer drift test makes |
| [`docs/release-process.md`](docs/release-process.md) | How a release is cut after an Edge release |
| [`docs/admin-contracts.md`](docs/admin-contracts.md) | Authoritative conditional snapshots, restore preconditions, namespace-scoped admin authorization and process egress discovery |
| [`docs/deployment-contracts.md`](docs/deployment-contracts.md) | Original deployment authority, dependency-fenced partial writes and explicit cleanup acknowledgements |
| [`docs/plugin-config-admission.md`](docs/plugin-config-admission.md) | Edge plugin configuration admission changes reached through the plugin catalog's pinned `openapi.yaml` |
| [`docs/release-signing.md`](docs/release-signing.md) | Signed release tags: signer setup, consumer verification, rotation and revocation; trust policy in [`docs/allowed_signers`](docs/allowed_signers) and [`docs/revoked_signers`](docs/revoked_signers) |
| [`docs/releases/`](docs/releases) | Release records from `contracts-edge-0.9.11` on: Edge source, changes and what stayed unchanged |

Every file records where it came from: owner repository, path, and commit.
Latest release: [`contracts-edge-0.9.21`](docs/releases/contracts-edge-0.9.21.md),
for published Edge `v0.9.21` (Edge commit
`f9915358c8032214f4034a17c28cdf72d14006c3`). Contracts tags only published
Edge releases, never an Edge prerelease or release candidate; while an Edge
candidate is validated, consumers stay on the latest release and
`main_branch_delta` names the candidate commit
([policy](docs/versioning.md#edge-release-candidates)). From
`contracts-edge-1.0.0`, cut when Edge `v1.0.0` is published, the
[stability promise](docs/versioning.md#stability-promise-for-contracts-edge-1)
applies. There is no `contracts-edge-0.9.18`: Edge `v0.9.18` was tagged but
never published.
Release history: [`CHANGELOG.md`](CHANGELOG.md) and [`docs/releases/`](docs/releases);
Edge-to-tag mapping: [docs/versioning.md](docs/versioning.md#release-tags).

## Consumers

See [docs/adoption.md](docs/adoption.md) for each consumer's pinned tag,
adoption status and remaining contract gaps.

## License

Copyright (c) 2026 Ferrum Edge LLC

Licensed under the [PolyForm Noncommercial License 1.0.0](LICENSE), the same as the rest of the suite.

**TL;DR**: Permitted noncommercial use is defined by [LICENSE](LICENSE) (PolyForm Noncommercial 1.0.0). For-profit infrastructure use and evaluation with anticipated commercial application require a [commercial license](LICENSE-COMMERCIAL.md). See [LICENSE](LICENSE) and [LICENSE-COMMERCIAL.md](LICENSE-COMMERCIAL.md) for the controlling terms and use-case table.
