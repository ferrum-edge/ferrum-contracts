# Ownership

This repository holds contracts that more than one Ferrum product reads or
writes. It does not own their meaning. Each contract has one owning product,
and that product's source code is the source of truth. The copy here is the
reviewed, versioned form that every other product pins.

## Rules

1. **Edge owns the gateway vocabularies.** `ErrorClass`, the `X-Gateway-Error`
   tokens, the gateway-owned headers, the `provisioned-by` attribution rules
   and the plugin catalog change only when Ferrum Edge changes them.
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
| `ferrum.diagnostic_ref.v1` | `schemas/diagnostic-ref/v1.schema.json` | ferrum-edge | `openapi.yaml` (`DiagnosticRefLookup`), `src/diagnostic_ref.rs` | implemented on Edge main, unreleased |
| `DiagnosticFinding` | `schemas/diagnostic-finding/v1.schema.json` | ferrum-anvil | `contracts/schemas/DiagnosticFinding.schema.json` (generated from Rust) | implemented |
| `ferrum.diagnostic_report` v1 | `schemas/diagnostic-report/v1.schema.json` | ferrum-alloy | `contracts/diagnostics/diagnostic-report.v1.schema.json` | implemented in Alloy; proposed as shared |
| `ferrum.service_manifest` v1 | `schemas/service-manifest/v1.schema.json` | ferrum-alloy | `crates/ferrum-alloy-edge/src/manifest.rs` | **proposed** |
| GitForgeOps resource file envelope (`kind` + `spec`) | `schemas/gitforgeops-resource/v1.schema.json` | ferrum-edge-git-forge-ops | `src/config/schema.rs` (`Resource`) | implemented |

`x-contract.status` is `implemented` when the owner produces or accepts the
contract today, and `proposed` when no consumer has agreed to it yet. A
proposed contract may change within its major version until a consumer
adopts it; the change is still recorded in `CHANGELOG.md`.

The vocabulary schemas (`schemas/vocabulary-*`) describe the shape of the
vocabulary files. This repository owns those shapes; the values inside the
vocabularies belong to Edge.

## Reviewers

A contract PR needs approval from a maintainer of the owning product. A PR
that changes the validation workflow or `ci/` needs approval from a
maintainer of this repository.
