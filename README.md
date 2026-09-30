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

The proposal and adoption tracking live in
[ferrum-edge/.github#4](https://github.com/ferrum-edge/.github/issues/4).

## Contents

| Path | What |
|---|---|
| [`vocabularies/`](vocabularies) | Edge-owned vocabularies: `ErrorClass` and `X-Gateway-Error` tokens, gateway-owned headers, `provisioned-by` values, and the plugin catalog index |
| [`schemas/`](schemas) | JSON Schemas (2020-12), one directory per contract, one file per major version |
| [`fixtures/`](fixtures) | Payloads producers must emit and consumers must accept (`valid/`) or reject (`invalid/`) |
| [`docs/ownership.md`](docs/ownership.md) | Who owns each contract and how changes land |
| [`docs/versioning.md`](docs/versioning.md) | Schema versions and `contracts-edge-X.Y.Z` tags |
| [`docs/adoption.md`](docs/adoption.md) | Which products consume which contract, and the local copies to replace |
| [`docs/release-process.md`](docs/release-process.md) | How a release is cut after an Edge release |

Every file records where it came from: owner repository, path, and commit.
No release is tagged yet; the first planned tag is `contracts-edge-0.9.8`.

## License

[PolyForm Noncommercial 1.0.0](LICENSE), the same as the rest of the suite.
