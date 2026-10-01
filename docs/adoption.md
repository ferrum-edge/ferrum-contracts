# Adoption

All five consumer repositories pin selected contracts releases. Each row
below names the local copy checked against a pin, or explains what remains
unadopted. Commit references are each repository's `origin/main` fetched on
2026-10-01. The proposal and adoption work tracked by
[ferrum-edge/.github#4](https://github.com/ferrum-edge/.github/issues/4) is
complete; that issue is closed.

| Repository | `origin/main` commit read | Pinned tag on `main` |
|---|---|---|
| ferrum-edge | `ee040d5e3281fde424aa65f5b18004852c5b53b0` | producer: Edge `v0.9.9` |
| ferrum-anvil | `89c7c9ac5e1eb922a688a8d9456db9b104b6d722` | `contracts-edge-0.9.9` |
| ferrum-alloy | `6163b183d131e558c378427c67037eeb283c10c9` | `contracts-edge-0.9.9` |
| ferrum-nexus | `7123ace572088913cca4aff2b161e1e1e51967c5f` | `contracts-edge-0.9.9` |
| ferrum-foundry | `f8842e8f53413d031e78f45f204777550a82ac7d` | `contracts-edge-0.9.8` |
| ferrum-edge-git-forge-ops | `6572da53994840b24f0420296a71738077ad3350` | `contracts-edge-0.9.8` |

Foundry and GitForgeOps have in-flight PRs to move their pins to
`contracts-edge-0.9.9`; the table records the pins currently on each
repository's `main`.

## Status by consumer

| Consumer | Contract | Local copy to replace | Status |
|---|---|---|---|
| ferrum-anvil | Gateway error vocabulary | Local release catalogs, finding labels, token mappings and `TOKENS` list; pinned copy at `contracts/ferrum-contracts/vocabularies/gateway-errors.json` | adopted: `contracts/ferrum-contracts/PIN` pins `contracts-edge-0.9.9`; `contracts_adoption` checks hashes and local token/class parity |
| ferrum-anvil | Gateway-owned headers | `catalog/ferrum/ferrum-edge-*/outcomes.json`; pinned copy at `contracts/ferrum-contracts/vocabularies/gateway-headers.json` | adopted: CI checks released diagnostic headers against the pin; `X-Ferrum-Diagnostic-Ref` is released in Edge v0.9.9 |
| ferrum-anvil | `DiagnosticFinding` (owner) | `contracts/schemas/DiagnosticFinding.schema.json` remains the generated schema; pinned schema and valid/invalid fixtures are under `contracts/ferrum-contracts/` | adopted: CI checks schema parity (excluding `$id` and `x-contract`) and validates the pinned fixtures |
| ferrum-anvil | `diagnostic_ref` | `docs/g01-gateway-diagnostic-contract.md`; shared schema at `schemas/diagnostic-ref/v1.schema.json` | not adopted: released in Edge v0.9.9; Anvil has not pinned the shared schema |
| ferrum-alloy | Gateway error vocabulary | Local token explanations in `crates/ferrum-alloy-diagnostics/src/catalog.rs` and `rules.rs`, plus `crates/ferrum-alloy-edge/src/contract.rs`; pinned vocabulary under `contracts/ferrum-contracts/` | adopted: the pin hashes the vocabulary; pairing CI checks local tokens and recorded meanings |
| ferrum-alloy | Gateway-owned headers | `crates/ferrum-alloy-edge/src/contract.rs`; pinned vocabulary at `contracts/ferrum-contracts/vocabularies/gateway-headers.json` | adopted: pairing CI checks the released diagnostic headers against the pin |
| ferrum-alloy | `diagnostic_report` (owner) | Local schema `contracts/diagnostics/diagnostic-report.v1.schema.json`; pinned schema and Finding fixtures under `contracts/ferrum-contracts/` | adopted: CI checks schema parity and validates pinned Finding fixtures; the shared status remains **PROPOSED** and Anvil import is not tested |
| ferrum-alloy | `service_manifest` (owner) | `crates/ferrum-alloy-edge/src/manifest.rs`; fixtures `contracts/fixtures/manifests/*.toml` | not adopted (proposed) |
| ferrum-alloy | `diagnostic_ref` | `docs/edge-contract-inventory.md`; shared schema at `schemas/diagnostic-ref/v1.schema.json` | not adopted: released in Edge v0.9.9; Alloy has not pinned the shared schema |
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

- Anvil's `ferrum.rs` test list has eight tokens, matching the v0.9.9
  vocabulary and Edge v0.9.9, including `request_timeout`.
- Edge v0.9.9 released `diagnostic_ref`; the Anvil release-status follow-up
  is complete.
- Alloy's `diagnostic_report` Finding is a superset of Anvil's
  `DiagnosticFinding`: open enumerations, two more evidence sources
  (`gateway_telemetry`, `service_telemetry`), and two more properties
  (`supporting_observations`, `missing_evidence`). The fixture
  `fixtures/diagnostic-finding/invalid/alloy-only-evidence-source.json`
  records the difference.

## Remaining follow-ups

- **Plugin config schemas are referenced, not vendored.** Edge publishes a
  config schema for all 82 built-in plugins in `openapi.yaml`
  (`components.schemas.*Config`, applied per `plugin_name` in
  `PluginConfigBase`). The catalog records each JSON Pointer and the file's
  sha256, and CI checks that every pointer resolves in that exact file. A
  later release should vendor each resolved schema as a standalone
  2020-12 schema (following `$ref`s), so consumers need not parse
  `openapi.yaml`.
- **Generated types.** Add generated TypeScript types (Nexus, Foundry, Anvil
  desktop) and a Rust crate or `include_str!` entry point.

Consumer drift checks now compare their local copies with the pinned tag; that
follow-up is complete.

## Candidate contracts

These contract-like copies were identified by the 2026-10-01 audit. They are
candidates for future adoption; this list does not add them to the shared
contract set.

- Nexus copies Edge's reserved `correlation_id` header names.
- Foundry copies Edge's plugin configuration sensitivity metadata from
  `pluginSensitivity.ts`.
- Alloy has a `gateway-diagnostic-ref` report fixture that is not yet part of
  the shared fixtures.
