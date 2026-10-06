# Ownership

This repository holds contracts that more than one Ferrum product reads or
writes. It does not own their meaning. Each contract has one owning product,
and that product's source code is the source of truth. The copy here is the
reviewed, versioned form that every other product pins.

## Rules

1. **Edge owns the gateway vocabularies.** `ErrorClass`, the `X-Gateway-Error`
   tokens, the gateway-owned headers, the `provisioned-by` attribution rules
   and the plugin catalog change only when Ferrum Edge changes them. Edge also
   owns conditional snapshot/restore semantics and backend egress metadata,
   including its versioned classifier and process/enforcement scope labels,
   and deployment-v1 original authority, partial mutation and acknowledgement.
2. **Each product owns its own schemas.** Anvil owns `DiagnosticFinding`, Alloy
   owns `diagnostic_report` and `service_manifest`, GitForgeOps owns its
   resource file envelope, and Edge owns `diagnostic_ref`.
3. **Changes land by pull request here.** The owner changes its code first (or
   in the same release), then opens a PR here that updates the schema or
   vocabulary, its fixtures, its `provenance`, and `CHANGELOG.md`. A PR that
   changes a contract without a matching owner commit is not merged.
4. **Consumers do not edit a contract to fit their code.** A consumer that
   needs a change asks the owner, in the owner's repository.
5. **Provenance is mandatory.** Every schema has `x-contract.provenance` and
   every vocabulary has `provenance`: owner repository, path, and the full
   commit SHA the content was read from. Fixture provenance is in
   [fixtures/README.md](../fixtures/README.md).

## Contracts and owners

| Contract | File here | Owner | Source of truth | Status |
|---|---|---|---|---|
| Gateway error vocabulary (`ErrorClass`, `X-Gateway-Error`) | `vocabularies/gateway-errors.json` | ferrum-edge | `src/retry.rs`, `docs/error_classification.md` | implemented |
| Gateway-owned headers | `vocabularies/gateway-headers.json` | ferrum-edge | `src/proxy/headers.rs`, `docs/admin_api.md`, `openapi.yaml` | implemented |
| `provisioned-by` label and `X-Ferrum-Provisioned-By` | `vocabularies/provisioned-by.json` | ferrum-edge | `src/admin/provisioning.rs`, `docs/admin_api.md` | implemented |
| Plugin catalog index | `vocabularies/plugin-catalog.json` | ferrum-edge | `src/plugins/mod.rs`, `src/plugins/builtin_parity.rs`, `openapi.yaml` | implemented |
| `ferrum.diagnostic_ref.v1` | `schemas/diagnostic-ref/v1.schema.json` | ferrum-edge | `openapi.yaml` (`DiagnosticRefLookup`), `src/diagnostic_ref.rs` | released in Edge v0.9.9 |
| Conditional backup metadata | `schemas/admin-conditional-snapshot/v1.schema.json` | ferrum-edge | `openapi.yaml` (`ConditionalBackupMetadata`, `ResourceETagMap`), `src/admin/conditional_snapshots.rs`, `preconditions.rs`, `backup.rs` | released in Edge v0.9.11; upstream distribution verified, canonical contracts-edge-0.9.11 published |
| Backend egress policy response and vocabulary | `schemas/backend-egress-policy/v1.schema.json`, `vocabularies/backend-egress-policy.json` | ferrum-edge | `openapi.yaml` (`BackendEgressPolicyResponse`), `src/admin/backend_egress_policy.rs`, `src/config/env_config.rs` | released in Edge v0.9.11; upstream distribution verified, canonical contracts-edge-0.9.11 published |
| Deployment snapshot | `schemas/admin-deployment-snapshot/v1.schema.json` | ferrum-edge | `openapi.yaml` (`DeploymentSnapshot`), `src/admin/deployment_mutations.rs`, `src/config/deployment_mutation.rs`, `db_backend.rs`, `db_loader.rs`, `mongo_store.rs` | released in Edge v0.9.12; upstream distribution verified, canonical contracts-edge-0.9.12 published |
| Deployment mutation acknowledgement | `schemas/admin-deployment-mutation-acknowledgement/v1.schema.json` | ferrum-edge | `openapi.yaml` (`DeploymentMutationAcknowledgement`), `src/admin/deployment_mutations.rs` | released in Edge v0.9.12; upstream distribution verified, canonical contracts-edge-0.9.12 published |
| `DiagnosticFinding` | `schemas/diagnostic-finding/v1.schema.json` | ferrum-anvil | `contracts/schemas/DiagnosticFinding.schema.json` (generated from Rust) | implemented |
| `ferrum.diagnostic_report` v1 | `schemas/diagnostic-report/v1.schema.json` | ferrum-alloy | `contracts/diagnostics/diagnostic-report.v1.schema.json` | implemented in Alloy; EXISTING shared v1 in published contracts-edge-0.9.11, owner unreleased |
| `ferrum.service_manifest` v1 | `schemas/service-manifest/v1.schema.json` | ferrum-alloy | `crates/ferrum-alloy-edge/src/manifest.rs` | implemented; EXISTING shared v1 in published contracts-edge-0.9.11, owner unreleased |
| GitForgeOps resource file envelope (`kind` + `spec`) | `schemas/gitforgeops-resource/v1.schema.json` | ferrum-edge-git-forge-ops | `src/config/schema.rs` (`Resource`) | implemented |

Owner implementation, shared freeze and publication are separate facts. Both
Alloy contracts now have `x-contract.status: implemented` and **EXISTING** shared
v1 status in the [published 0.9.11 release](releases/contracts-edge-0.9.11.md).
Root accepted the unchanged wire freeze on 2026-10-04 after reviewed owner and
[consumer qualification](adoption.md). This is the authorized canonical metadata
decision, not an invented prior human approval or separate Alloy crate publishing
approval. Alloy's owner availability remains `unreleased` (`publish = false`).

Final provenance reads qualified owner
`81cbb410d34ff5fba1f3d54cfd2e7ebccaed397e`, the ordinary squash of Alloy #144;
its sole applicable main PUSH workflow and all 18 jobs/checks passed. Full
diagnostic-report pairing includes every description outside `$id`/`x-contract`.
The copied report retains historical PROPOSED wording in those owner descriptions;
current shared status is recorded in `x-contract` and these docs. The manifest
remains a transcription of owner code, with documented post-default/cross-field
limits, not an owner-exported schema. Every v1 field, bound and fixture is retained.

Canonical publication is complete: PR #13 merged at
`390edbd5b2485af0988e02f7827fde778d76ae0a`, main PUSH validation succeeded,
and release 403239814 was published on 2026-10-04 at 22:41:21 UTC. Prepared/pending
wording in the immutable tagged source is historical, not a new approval
requirement. Existing r2 bytes and consumer pins remain historical; owner
pin/local annotations and consumer copies still need coordinated adoption PRs
that merge with full hosted parity before the ledger records new pins.

The new Edge artifacts check metadata syntax/shape and owner-derived egress
invariants. [HTTP/runtime semantics](admin-contracts.md), including credential
verification, audit admission, snapshot coherence, lease fences and serving-DP
checks, remain the owning implementation's responsibility; schema conformance
alone grants no authorization or enforcement attestation.

Consumer fixture tests or previews do not automatically promote schema
metadata, freeze v1 or publish a contracts tag. Root's accepted coordinated
metadata decision is recorded in the published release with owner provenance and
consumer evidence. Future contract changes require fixture review and owner
approval under the rules above.
All contracts follow [versioning.md](versioning.md), and every change is
recorded in `CHANGELOG.md`; published tags remain immutable.

The vocabulary schemas (`schemas/vocabulary-*`) describe the shape of the
vocabulary files. This repository owns those shapes; the values inside the
vocabularies belong to Edge.

The [0.9.12 release](releases/contracts-edge-0.9.12.md) reads Edge-owned
sources at actual released `0d917701b63ef38210c49df830f48cf0457cbc7d`.
Backup metadata, egress labels and diagnostic-ref wire content are retained;
their current provenance is re-read at that owner. Deployment-v1 is a separate
profile, with separate schemas and [runtime protocol](deployment-contracts.md).
OpenAPI leaves raw evidence/resource objects open and acknowledgement
profile/target optional for refusals; consumers must retain complete original
evidence and require explicit success identity/cleanup authorization. Schema
conformance cannot supply those runtime guarantees. The changed Edge contracts
were reviewed by the Edge maintainer and published as `contracts-edge-0.9.12`
at `31f0a21d707795be293d15837c2f77c3d84219d8` on 2026-10-05. Alloy and other
owners retain their own availability and adoption boundaries.

## Reviewers

A contract PR needs approval from a maintainer of the owning product. A PR
that changes the validation workflow or `ci/` needs approval from a
maintainer of this repository.

Today the org has one maintainer, so `.github/CODEOWNERS` maps every path to
@jeremyjpj0916. When per-product teams exist, replace that line with one
entry per contract file (for example `schemas/diagnostic-finding/` to the
Anvil team, `vocabularies/` to the Edge team) and keep `ci/` and
`.github/` with this repository's maintainers.

## Branch protection

`main` should require:

- the status check **`Schemas, fixtures and vocabularies`** (the only job of
  the `Validate contracts` workflow, `.github/workflows/validate.yml`), and
- review from a code owner.

If the job is renamed, update the required check in the same PR.
