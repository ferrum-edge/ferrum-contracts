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
| Gateway-owned headers | `vocabularies/gateway-headers.json` | ferrum-edge | `src/proxy/headers.rs`, `src/proxy/mod.rs`, `src/plugins/mod.rs` (`RequestContext` identity accessors), `src/plugins/mesh/{spiffe_identity,ext_authz}.rs`, `docs/plugins.md`, `docs/admin_api.md`, `openapi.yaml` | implemented; v0.9.19 adds peer SPIFFE forwarding and CUSTOM check identity assertions |
| `provisioned-by` label and `X-Ferrum-Provisioned-By` | `vocabularies/provisioned-by.json` | ferrum-edge | `src/admin/provisioning.rs`, `docs/admin_api.md` | implemented |
| Plugin catalog index | `vocabularies/plugin-catalog.json` | ferrum-edge | `src/plugins/mod.rs`, `src/plugins/builtin_parity.rs`, `openapi.yaml` | implemented |
| `ferrum.diagnostic_ref.v1` | `schemas/diagnostic-ref/v1.schema.json` | ferrum-edge | `openapi.yaml` (`DiagnosticRefLookup`), `src/diagnostic_ref.rs` | released in Edge v0.9.9; v0.9.17 adds the mirrored `loop_detected` vocabulary token within v1; raw rejection phases stay open labels; re-checked unchanged at v0.9.19 with frozen canonical bytes |
| Conditional backup metadata | `schemas/admin-conditional-snapshot/v1.schema.json` | ferrum-edge | `openapi.yaml` (`ConditionalBackupMetadata`, `ResourceETagMap`), `src/admin/conditional_snapshots.rs`, `preconditions.rs`, `backup.rs` | released in Edge v0.9.11; wire shape unchanged through v0.9.19 |
| Backend egress policy response and vocabulary | `schemas/backend-egress-policy/v1.schema.json`, `v2.schema.json`, `vocabularies/backend-egress-policy.json` | ferrum-edge | `openapi.yaml` (`BackendEgressPolicyResponse`, `DataPlaneEgressAttestation`), `src/admin/backend_egress_policy.rs`, `src/grpc/backend_egress_attestation.rs`, `src/config/env_config.rs` | v1 emitted by Edge v0.9.11 and v0.9.12; v2 released in Edge v0.9.13, with optional CP `data_plane_attestation` from v0.9.14; unchanged through v0.9.19 |
| Deployment snapshot | `schemas/admin-deployment-snapshot/v1.schema.json`, `v2.schema.json` | ferrum-edge | `openapi.yaml` (`DeploymentSnapshot`, `StoredContentDigest`), `src/admin/deployment_mutations.rs`, `src/config/deployment_mutation.rs`, `db_backend.rs`, `db_loader.rs`, `mongo_store.rs` | v1 emitted by Edge v0.9.12; v2 released in Edge v0.9.13; v0.9.17 derives inspection lists from canonical evidence; shape retained through v0.9.19 |
| Deployment mutation acknowledgement | `schemas/admin-deployment-mutation-acknowledgement/v1.schema.json` | ferrum-edge | `openapi.yaml` (`DeploymentMutationAcknowledgement`, `NamespaceSnapshotTooLarge`), `src/admin/deployment_mutations.rs`, `src/config/deployment_mutation.rs` | released in Edge v0.9.12; shape unchanged through v0.9.19; v0.9.14 narrows the `durable: unknown` outcome |
| `DiagnosticFinding` | `schemas/diagnostic-finding/v1.schema.json` | ferrum-anvil | `contracts/schemas/DiagnosticFinding.schema.json` (generated from Rust) | implemented |
| `ferrum.diagnostic_report` v1 | `schemas/diagnostic-report/v1.schema.json` | ferrum-alloy | `contracts/diagnostics/diagnostic-report.v1.schema.json` | implemented in Alloy; EXISTING shared v1 in published contracts-edge-0.9.11, owner unreleased |
| `ferrum.service_manifest` v1 | `schemas/service-manifest/v1.schema.json` | ferrum-alloy | `crates/ferrum-alloy-edge/src/manifest.rs` | implemented; EXISTING shared v1 in published contracts-edge-0.9.11, owner unreleased |
| GitForgeOps resource file envelope (`kind` + `spec`) | `schemas/gitforgeops-resource/v1.schema.json` | ferrum-edge-git-forge-ops | `src/config/schema.rs` (`Resource`) | implemented |

Owner implementation, shared freeze and publication are separate facts. Both
Alloy contracts have `x-contract.status: implemented` and **EXISTING** shared v1
status from [contracts-edge-0.9.11](releases/contracts-edge-0.9.11.md). That
status does not release Alloy: its owner availability remains `unreleased`
(`publish = false`), and no separate crate publishing approval is implied.
Diagnostic-report pairing covers every description outside `$id`/`x-contract`,
so the copy keeps the owner's historical PROPOSED wording; current shared status
is recorded in `x-contract`. The manifest schema is a transcription of owner
code, with documented post-default/cross-field limits, not an owner-exported
schema. Release and consumer evidence: [releases/](releases) and
[adoption.md](adoption.md).

The Edge admin artifacts check metadata syntax/shape and owner-derived egress
invariants. [HTTP/runtime semantics](admin-contracts.md) and the
[deployment-v1 protocol](deployment-contracts.md), including credential
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

`main` requires:

- the status check **`Schemas, fixtures and vocabularies`** (the only job of
  the `Validate contracts` workflow, `.github/workflows/validate.yml`), and
- no approving reviews (ruleset 24239605; the repository is solo-maintained).

Changes land by pull request with all review threads resolved; force-push and
deletion are blocked. Ruleset 24979475 also requires the `validate.yml`
workflow from `main` to run (renaming or moving that file needs a ruleset
update).

If the job is renamed, update the required check in the same PR.
