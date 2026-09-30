# Adoption

All five consumer repositories now pin selected contracts releases. Each row
below names the local copy checked against a pin, or explains what remains
unadopted. The paths were read from each repository's `main` at the commit in
the table header; proposal and tracking live in
[ferrum-edge/.github#4](https://github.com/ferrum-edge/.github/issues/4).

| Repository | Commit read |
|---|---|
| ferrum-edge | `v0.9.8` = `e27f2109216352c3fe9e67a7014611f3f66daa91`; `main` = `da45e9b1240ae6945a15a0f91912c810704c0362` |
| ferrum-anvil | `5861d23c497534d5b07907a4420e919f3e989d06` |
| ferrum-alloy | `bd72040ea265e9d21c24b8028888fe66c1f8f043` |
| ferrum-nexus | `9fdd33cc4e7ccc1b1628f7518e9604e907a1e6ac` |
| ferrum-foundry | `0aea505fed59b6424f14de81770b3e4391c70794` |
| ferrum-edge-git-forge-ops | `8d9dfd86d8441ba2d7ac92fd31d2cf87b461da41` |

## Status by consumer

| Consumer | Contract | Local copy to replace | Status |
|---|---|---|---|
| ferrum-anvil | Gateway error vocabulary | Local release catalogs, finding labels, token mappings and `TOKENS` list; pinned copy at `contracts/ferrum-contracts/vocabularies/gateway-errors.json` | adopted: `contracts/ferrum-contracts/PIN` pins `contracts-edge-0.9.8`; `contracts_adoption` checks hashes and local token/class parity |
| ferrum-anvil | Gateway-owned headers | `catalog/ferrum/ferrum-edge-*/outcomes.json`; pinned copy at `contracts/ferrum-contracts/vocabularies/gateway-headers.json` | adopted: CI checks the released diagnostic headers against the pin and explicitly treats `X-Ferrum-Diagnostic-Ref` as unreleased |
| ferrum-anvil | `DiagnosticFinding` (owner) | `contracts/schemas/DiagnosticFinding.schema.json` remains the generated schema; pinned schema and valid/invalid fixtures are under `contracts/ferrum-contracts/` | adopted: CI checks schema parity (excluding `$id` and `x-contract`) and validates the pinned fixtures |
| ferrum-anvil | `diagnostic_ref` | `docs/g01-gateway-diagnostic-contract.md`; Edge implementation is on `main` (ferrum-edge#5767, #5845), but no released tag contains it | not adopted: waits for an Edge release |
| ferrum-alloy | Gateway error vocabulary | Local token explanations in `crates/ferrum-alloy-diagnostics/src/catalog.rs` and `rules.rs`, plus `crates/ferrum-alloy-edge/src/contract.rs`; pinned vocabulary under `contracts/ferrum-contracts/` | adopted: the pin hashes the vocabulary; pairing CI checks local tokens and recorded meanings |
| ferrum-alloy | Gateway-owned headers | `crates/ferrum-alloy-edge/src/contract.rs`; pinned vocabulary at `contracts/ferrum-contracts/vocabularies/gateway-headers.json` | adopted: pairing CI checks the released diagnostic headers against the pin |
| ferrum-alloy | `diagnostic_report` (owner) | Local schema `contracts/diagnostics/diagnostic-report.v1.schema.json`; pinned schema and Finding fixtures under `contracts/ferrum-contracts/` | adopted: CI checks schema parity and validates pinned Finding fixtures; the shared status remains **PROPOSED** and Anvil import is not tested |
| ferrum-alloy | `service_manifest` (owner) | `crates/ferrum-alloy-edge/src/manifest.rs`; fixtures `contracts/fixtures/manifests/*.toml` | not adopted (proposed) |
| ferrum-alloy | `diagnostic_ref` | `docs/edge-contract-inventory.md`; Edge implementation is on `main` but is not in a released tag | not adopted: waits for an Edge release |
| ferrum-alloy | GitForgeOps envelope | `crates/ferrum-alloy-edge/src/export.rs` `gitforgeops_files` output | not adopted: GitForgeOps pins envelope fixtures, but Alloy's generated output is not validated in CI |
| ferrum-edge-git-forge-ops | Plugin catalog | `src/plugin_catalog.rs`; pinned copy at `contracts/ferrum-contracts/vocabularies/plugin-catalog.json` | adopted: `PIN` hashes the vocabulary and CI compares local names, priorities, retired names and reserved names |
| ferrum-edge-git-forge-ops | `provisioned-by` | `src/config/assembler.rs`; pinned copy at `contracts/ferrum-contracts/vocabularies/provisioned-by.json` | adopted: CI compares the local label and its usages with the pinned vocabulary |
| ferrum-edge-git-forge-ops | GitForgeOps envelope (owner) | Local `src/config/schema.rs` `Resource`; valid/invalid envelope fixtures under `contracts/ferrum-contracts/fixtures/gitforgeops-resource/` | partially adopted: CI hashes and parses the pinned fixtures against `Resource`; the shared envelope schema itself is not pinned |
| ferrum-nexus | Plugin catalog | `shared/src/plugins.ts`; pinned copy at `contracts/ferrum-contracts/vocabularies/plugin-catalog.json` | adopted: `PIN` hashes the vocabulary and CI checks local plugin names against it |
| ferrum-nexus | `provisioned-by` | `server/src/ferrum-admin/client.ts` and test double; pinned vocabulary at `contracts/ferrum-contracts/vocabularies/provisioned-by.json` | adopted: CI checks the header and value against the pin |
| ferrum-nexus | `service_manifest` | none yet | not adopted (proposed) |
| ferrum-foundry | Plugin catalog | `src/lib/pluginConfigDefaults.ts`; pinned copy at `contracts/ferrum-contracts/vocabularies/plugin-catalog.json` | adopted: `PIN` hashes the vocabulary and CI checks local metadata and defaults against it |
| ferrum-foundry | `provisioned-by` | `server/proxy.ts`, `src/components/shared/ResourceLabels.tsx`, `scripts/mock-admin-gateway.mjs`; pinned vocabulary under `contracts/ferrum-contracts/` | adopted: CI checks header, value and label usage against the pin |
| ferrum-foundry | `service_manifest` | none yet | not adopted (proposed) |

A consumer is **adopted** when it pins a `contracts-edge-*` tag (git
dependency, `include_str!`, or generated types) and its CI fails when its
local copy differs from the pinned contract.

## ferrum-alloy#27 checklist

[ferrum-alloy#27](https://github.com/ferrum-edge/ferrum-alloy/issues/27)
tracks consumers of Alloy's contracts. Its items, folded in here:

- [ ] Anvil: once Anvil has an importer, add a cross-repo CI check that
      Alloy's `diagnostic_report` fixtures import cleanly, and mark the report
      schema EXISTING as a shared contract. Anvil's adoption PR pins and checks
      `DiagnosticFinding`; it does not import Alloy's report. The report schema
      and Finding fixtures are pinned under `contracts/ferrum-contracts/`.
- [ ] GitForgeOps: validate the files `ferrum-alloy edge export --format
      gitforgeops` generates with GitForgeOps' own schema or validator in CI.
      GitForgeOps now checks pinned valid/invalid fixtures against its local
      `Resource`, but Alloy's generated files are not yet covered by that CI.
- [ ] Nexus/Foundry: agree on the manifest fields with the consumer before
      `service_manifest` v1 is frozen, then add a consumer-side fixture test.
- [ ] Foundry: write an ADR for the authenticated presentation boundary, so
      Alloy never becomes a trace store.

## Drift found while seeding

- Anvil's `ferrum.rs` test list has seven tokens. That is correct for its
  v0.9.5 and v0.9.7 catalogs, but the v0.9.8 catalog and Edge v0.9.8 have
  eight (`request_timeout`).
- Alloy's inventory and Anvil's G01 document still call `diagnostic_ref`
  proposed; Edge implements it on `main` (not yet in a release).
- Alloy's `diagnostic_report` Finding is a superset of Anvil's
  `DiagnosticFinding`: open enumerations, two more evidence sources
  (`gateway_telemetry`, `service_telemetry`), and two more properties
  (`supporting_observations`, `missing_evidence`). The fixture
  `fixtures/diagnostic-finding/invalid/alloy-only-evidence-source.json`
  records the difference.

## Follow-ups

- **Plugin config schemas are referenced, not vendored.** Edge publishes a
  config schema for all 82 built-in plugins in `openapi.yaml`
  (`components.schemas.*Config`, applied per `plugin_name` in
  `PluginConfigBase`). The catalog records each JSON Pointer and the file's
  sha256, and CI checks that every pointer resolves in that exact file. A
  later release should vendor each resolved schema as a standalone
  2020-12 schema (following `$ref`s), so consumers need not parse
  `openapi.yaml`.
- **`diagnostic_ref` is unreleased.** Re-check the schema against the Edge
  release that first ships it before tagging a release that claims it.
- **Generated types.** Add generated TypeScript types (Nexus, Foundry, Anvil
  desktop) and a Rust crate or `include_str!` entry point.
- **Drift checks in consumers.** Each consumer adds a CI job that compares its
  local copy with the pinned tag.
