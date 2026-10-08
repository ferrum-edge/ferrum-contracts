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
| [`fixtures/`](fixtures) | Payloads producers must emit and consumers must accept (`valid/`) or reject (`invalid/`); one `v<N>/` directory per major when a schema has several |
| [`docs/ownership.md`](docs/ownership.md) | Who owns each contract and how changes land |
| [`docs/versioning.md`](docs/versioning.md) | Schema versions and `contracts-edge-X.Y.Z` tags |
| [`docs/adoption.md`](docs/adoption.md) | Consumer pins, qualification evidence and remaining contract gaps |
| [`docs/release-process.md`](docs/release-process.md) | How a release is cut after an Edge release |
| [`docs/admin-contracts.md`](docs/admin-contracts.md) | Authoritative conditional snapshots, restore preconditions and process egress discovery |
| [`docs/deployment-contracts.md`](docs/deployment-contracts.md) | Original deployment authority, dependency-fenced partial writes and explicit cleanup acknowledgements |
| [`docs/releases/contracts-edge-0.9.15.md`](docs/releases/contracts-edge-0.9.15.md) | Edge v0.9.15 source, the `X-Authenticated-Identity` header, `Connection` nomination rules, the `route_protocol_admission` phase and plugin config schema changes |
| [`docs/releases/contracts-edge-0.9.14.md`](docs/releases/contracts-edge-0.9.14.md) | Edge v0.9.14 source, the CP data-plane egress attestation, narrowed deployment durable outcomes and error-classification notes |
| [`docs/releases/contracts-edge-0.9.13.md`](docs/releases/contracts-edge-0.9.13.md) | Edge v0.9.13 source, the v2 egress and deployment snapshot contracts, and what stayed unchanged |
| [`docs/releases/contracts-edge-0.9.12.md`](docs/releases/contracts-edge-0.9.12.md) | Actual canonical publication and pending consumer adoption |
| [`docs/releases/contracts-edge-0.9.11.md`](docs/releases/contracts-edge-0.9.11.md) | Actual canonical publication/owner evidence and pending consumer adoption |

Every file records where it came from: owner repository, path, and commit.
The latest contracts release is
[`contracts-edge-0.9.15`](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.15),
tagged on the merge commit of its release PR. It maps to Edge `v0.9.15` at
`25b37395ff61bfea0f3ffd189d9011c4984fa755` and adds no new major and no schema
rule: `gateway-headers.json` adds the gateway-owned `X-Authenticated-Identity`
header, narrows `X-Consumer-Username` to a mapped Consumer and records the
`Connection` nomination and `_`/`-` assertion rules; `diagnostic-ref` v1 keeps
its frozen bytes and gains fixtures for the `route_protocol_admission`
rejection phase; and the plugin catalog pins the `v0.9.15` `openapi.yaml`,
whose config schemas drop the LDAP `consumer_mapping` and add the plugin
secret, IPv6 prefix and MCP session rules. All five vocabularies are
refreshed. See the [release record](docs/releases/contracts-edge-0.9.15.md).

Historical
[`contracts-edge-0.9.14`](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.14)
at `ddbdd845733b7046c4393ac951011dafb774db33` (release 406650065, published
2026-10-08) maps to Edge `v0.9.14` at
`9bd4d5f9caa4ebe8f0ea13e76d8a6e2172eaca7d` and adds no new major: `backend-egress-policy` v2 gains
the optional CP-only `data_plane_attestation` object (`schema_version` stays
`2`), the deployment mutation acknowledgement describes the narrowed `durable`
outcomes, and `gateway-errors.json` notes the HTTP/2 reset and buffered read
reclassification without adding a class or token. See the
[release record](docs/releases/contracts-edge-0.9.14.md).

Historical
[`contracts-edge-0.9.13`](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.13)
is tagged on the merge commit of its release PR and maps to Edge `v0.9.13` at
`9b83115de7ec23ab51ec4feae6bed65e596db425` and adds new majors for two
response contracts Edge changed incompatibly: `backend-egress-policy` v2
(`schema_version: 2`; `public_only_guaranteed` requires local enforcement) and
`admin-deployment-snapshot` v2 (spec bytes as SHA-256 digests plus a separate
`api_spec_contents` copy). The v1 files stay for consumers of earlier Edge
releases. See the [release record](docs/releases/contracts-edge-0.9.13.md).

Historical
[`contracts-edge-0.9.12`](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.12)
at `31f0a21d707795be293d15837c2f77c3d84219d8` was published on 2026-10-05 at
13:58:38 UTC after [PR #15](https://github.com/ferrum-edge/ferrum-contracts/pull/15)
merged and its main PUSH validation succeeded. It maps to Edge's actual unsigned
lightweight `v0.9.12` tag at `0d917701b63ef38210c49df830f48cf0457cbc7d`.
Edge's release assets, digests, image identities, attestations and ABI gates are
recorded in the [Edge v0.9.12 release](https://github.com/ferrum-edge/ferrum-edge/releases/tag/v0.9.12).
That release refreshed all five Edge vocabularies and the plugin OpenAPI
pin and added separate deployment snapshot and mutation acknowledgement schemas.

Historical
[`contracts-edge-0.9.11`](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.11)
at `390edbd5b2485af0988e02f7827fde778d76ae0a` was published on 2026-10-04 at
22:41:21 UTC and maps to Edge's `v0.9.11` tag at
`c764084b3b51c3f7ffde268c039688d35e49c553`; it includes Alloy owner
`81cbb410d34ff5fba1f3d54cfd2e7ebccaed397e` and root's accepted unchanged shared
v1 freeze. Historical
[`contracts-edge-0.9.9-r2`](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.9-r2)
adds Alloy's optional service-manifest `[agents]` section to
[`contracts-edge-0.9.9`](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.9);
both retain their Edge v0.9.9/v0.9.10 mappings. The initial
[`contracts-edge-0.9.8`](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.8)
release remains available. Prepared/pending wording in the immutable 0.9.11 and
0.9.12 tagged sources records their pre-publication state; it is not a new
approval requirement. Consumer pins are refreshed in
[docs/adoption.md](docs/adoption.md), and 0.9.12 adoption remains pending until
the consumer PRs merge and qualify. See the
[release records](docs/releases/contracts-edge-0.9.12.md).

The 0.9.12 release added separate deployment snapshot and mutation
acknowledgement schemas plus refreshed Edge provenance from actually released
Edge `v0.9.12` at `0d917701b63ef38210c49df830f48cf0457cbc7d`. Complete original
secret-bearing evidence and its deployment token fence partial proxy removal and
API-spec replacement. Cleanup requires the explicit owner acknowledgement; even
HTTP 200 can be durable-only and prohibit cleanup. The existing backup/row
contracts keep their semantics. See [the deployment contract](docs/deployment-contracts.md)
and [release record](docs/releases/contracts-edge-0.9.12.md) for provenance and
verified Edge facts. Other-owner unreleased features and pending publisher
profiles are not promoted.

The 0.9.11 release adds metadata schemas for coherent admin conditional backup and
process-scoped backend egress discovery, plus the egress vocabulary and sanitized
fixtures. Standard HTTP `ETag`/`If-Match` admin semantics are documented against
the owner implementation. JSON validation checks shape and owner-derived
invariants; authorization, token validity and serving-DP enforcement remain
runtime requirements in [the admin contract](docs/admin-contracts.md).

## Consumers

See [docs/adoption.md](docs/adoption.md) for each consumer's pinned tag,
adoption status and remaining contract gaps.

The 2026-10-06 snapshot records qualified Anvil diagnostic import, GitForgeOps
validation of actual Alloy-generated resource trees, and Nexus/Foundry manifest
previews with their bounded trust and presentation rules. Alloy, Foundry and
GitForgeOps now pin `contracts-edge-0.9.12`; Anvil pins `contracts-edge-0.9.11`;
Nexus pins `contracts-edge-0.9.9` for vocabularies and `contracts-edge-0.9.9-r2`
for the manifest. The published release marks the shared diagnostic report
and service manifest **EXISTING**/implemented after root's accepted coordinated v1
freeze, preserving all wire fields, bounds, fixtures and reader behavior.
Historical r2 metadata stays unchanged. Alloy remains unpublished; this decision
grants no separate crate publishing approval. [Alloy #27](https://github.com/ferrum-edge/ferrum-alloy/issues/27)
remains open for root disposition after coordinated adoption.

## License

[PolyForm Noncommercial 1.0.0](LICENSE), the same as the rest of the suite.
