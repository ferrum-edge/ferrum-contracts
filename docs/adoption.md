# Adoption

No product consumes this repository yet. Each row below names the local copy
a product keeps today and should replace with a pinned release. The paths
were read from each repository's `main` at the commit in the table header;
proposal and tracking live in
[ferrum-edge/.github#4](https://github.com/ferrum-edge/.github/issues/4).

| Repository | Commit read |
|---|---|
| ferrum-edge | `v0.9.8` = `e27f2109216352c3fe9e67a7014611f3f66daa91`; `main` = `f638465034734e335bde7e76c56e8c8244afba8a` |
| ferrum-anvil | `c401a320dcc5d52f707a5d5c27e333587b7a5d86` |
| ferrum-alloy | `fa471ccb79a444aee04661880af2385596d9da45` |
| ferrum-nexus | `06254cfd124ce679bf7b93108c0edb1778160d00` |
| ferrum-foundry | `8d075206e2fabf05283e0fb3c998d2fccf655293` |
| ferrum-edge-git-forge-ops | `36206d8de8929884f62c65a040f3a08d35bd5863` |

## Status by consumer

| Consumer | Contract | Local copy to replace | Status |
|---|---|---|---|
| ferrum-anvil | Gateway error vocabulary | `catalog/ferrum/ferrum-edge-{0.9.5,0.9.7,0.9.8}/outcomes.json` (`public_tokens`, `error_classes`); `catalog/diagnostics/findings.en.json` (`ferrum.token.*` entries); `crates/anvil-diagnostics/src/rules/ferrum_rules.rs` (`token_scope`, `token_owner`); `crates/anvil-diagnostics/src/ferrum.rs` test `TOKENS` (seven tokens, no `request_timeout`) | not adopted |
| ferrum-anvil | Gateway-owned headers | `catalog/ferrum/ferrum-edge-*/outcomes.json` (`headers`) | not adopted |
| ferrum-anvil | `DiagnosticFinding` (owner) | `contracts/schemas/DiagnosticFinding.schema.json` stays the generator output; CI should fail when it differs from `schemas/diagnostic-finding/v1.schema.json` minus `$id` and `x-contract`. Generated TypeScript: `apps/desktop/src/generated/contracts.ts` | not adopted |
| ferrum-anvil | `diagnostic_ref` | `docs/g01-gateway-diagnostic-contract.md` still says "Proposal"; Edge implements it on `main` (ferrum-edge#5767, #5845) | not adopted |
| ferrum-alloy | Gateway error vocabulary | `crates/ferrum-alloy-edge/src/contract.rs` `GATEWAY_ERROR_TOKENS`; `crates/ferrum-alloy-diagnostics/src/catalog.rs` `EDGE_GATEWAY_ERROR_TOKENS`; rule `alloy.r007` in `crates/ferrum-alloy-diagnostics/src/rules.rs`; the manual checklist in `.github/workflows/edge-bump.yml` | not adopted |
| ferrum-alloy | Gateway-owned headers | `crates/ferrum-alloy-edge/src/contract.rs` `GATEWAY_ERROR`, `GATEWAY_UPSTREAM_STATUS` | not adopted |
| ferrum-alloy | `diagnostic_report` (owner) | `contracts/diagnostics/diagnostic-report.v1.schema.json`; replace `crates/ferrum-alloy-diagnostics/tests/schema_parity.rs` Finding checks with the shared fixture cross-check (`fixtures/diagnostic-finding/valid` must pass `diagnostic-report#/$defs/Finding`) | not adopted |
| ferrum-alloy | `service_manifest` (owner) | `crates/ferrum-alloy-edge/src/manifest.rs`; fixtures `contracts/fixtures/manifests/*.toml` | not adopted (proposed) |
| ferrum-alloy | `diagnostic_ref` | `docs/edge-contract-inventory.md` marks G01 **PROPOSED** and "not implemented in Edge" | not adopted |
| ferrum-alloy | GitForgeOps envelope | `crates/ferrum-alloy-edge/src/export.rs` `gitforgeops_files` output is never validated | not adopted |
| ferrum-edge-git-forge-ops | Plugin catalog | `src/plugin_catalog.rs` (`BUILTIN_PLUGINS`, 82 names; `RETIRED_PLUGIN_NAMES`; `RESERVED_PLUGIN_NAMES`) | not adopted |
| ferrum-edge-git-forge-ops | `provisioned-by` | `src/config/assembler.rs` literals `provisioned-by` / `ferrum-edge-git-forge-ops`; tests `tests/unit/validator_labels_tests.rs`, `.github/scripts/tests/test_validator_labels.py` | not adopted |
| ferrum-edge-git-forge-ops | GitForgeOps envelope (owner) | `src/config/schema.rs` `Resource` | not adopted |
| ferrum-nexus | Plugin catalog | `shared/src/plugins.ts` (`PROVIDER_PLUGINS`, `PLUGIN_CATEGORIES`, `FIRST_CLASS_PLUGIN_FIELDS`) | not adopted |
| ferrum-nexus | `provisioned-by` | `server/src/ferrum-admin/client.ts` `'x-ferrum-provisioned-by': 'ferrum-nexus'`; test double `server/src/test/mock-ferrum-edge.ts` | not adopted |
| ferrum-nexus | `service_manifest` | none yet | not adopted (proposed) |
| ferrum-foundry | Plugin catalog | `src/lib/pluginConfigDefaults.ts` (`PLUGIN_METADATA`, `DEFAULT_PLUGIN_CONFIGS`) | not adopted |
| ferrum-foundry | `provisioned-by` | `server/proxy.ts` `'x-ferrum-provisioned-by': 'ferrum-foundry'`; `src/components/shared/ResourceLabels.tsx`; `scripts/mock-admin-gateway.mjs` | not adopted |
| ferrum-foundry | `service_manifest` | none yet | not adopted (proposed) |

A consumer is **adopted** when it pins a `contracts-edge-*` tag (git
dependency, `include_str!`, or generated types) and its CI fails when its
local copy differs from the pinned contract.

## ferrum-alloy#27 checklist

[ferrum-alloy#27](https://github.com/ferrum-edge/ferrum-alloy/issues/27)
tracks consumers of Alloy's contracts. Its items, folded in here:

- [ ] Anvil: once Anvil has an importer, add a cross-repo CI check that
      Alloy's contract fixtures import cleanly, and mark the report schema
      EXISTING as a shared contract. (The report fixtures are now in
      `fixtures/diagnostic-report/`.)
- [ ] GitForgeOps: validate the files `ferrum-alloy edge export --format
      gitforgeops` generates with GitForgeOps' own schema or validator in CI.
      (`schemas/gitforgeops-resource/v1` checks the envelope today.)
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
