# Adoption

All five consumer repositories pin selected contracts releases. The snapshot
below was read through the GitHub API on 2026-10-04; PIN files, test sources
and workflows were inspected at the full immutable `main` commits listed.
Consumer qualification is scoped to the files and behavior actually checked.
The proposal and adoption work tracked by
[ferrum-edge/.github#4](https://github.com/ferrum-edge/.github/issues/4) is
complete; that issue is closed. The later Alloy consumer work tracked by
[ferrum-alloy#27](https://github.com/ferrum-edge/ferrum-alloy/issues/27) remains
open pending coordinated owner qualification and the canonical shared freeze.

| Repository | `main` commit read (2026-10-04) | Pinned tag on `main` |
|---|---|---|
| ferrum-edge | `c764084b3b51c3f7ffde268c039688d35e49c553` | producer: actual tagged `v0.9.11` source for this draft; published release/assets verification pending; existing `v0.9.10` mapping is `contracts-edge-0.9.9`, also covered by r2 |
| ferrum-anvil | `c19c0a6abba896bfec972b3e083179c55ef8e38c` | [`PIN`](https://github.com/ferrum-edge/ferrum-anvil/blob/c19c0a6abba896bfec972b3e083179c55ef8e38c/contracts/ferrum-contracts/PIN): `contracts-edge-0.9.9-r2` |
| ferrum-alloy | `d7ddb3688e058ec3cc2e17d166a801aa0037b5b1` | [`PIN`](https://github.com/ferrum-edge/ferrum-alloy/blob/d7ddb3688e058ec3cc2e17d166a801aa0037b5b1/contracts/ferrum-contracts/PIN): `contracts-edge-0.9.9-r2` |
| ferrum-nexus | `559c350a5370335791cdc3082225dce6056cf547` | [`PIN`](https://github.com/ferrum-edge/ferrum-nexus/blob/559c350a5370335791cdc3082225dce6056cf547/contracts/ferrum-contracts/PIN): `contracts-edge-0.9.9` vocabularies; [`SERVICE-MANIFEST-PIN`](https://github.com/ferrum-edge/ferrum-nexus/blob/559c350a5370335791cdc3082225dce6056cf547/contracts/ferrum-contracts/SERVICE-MANIFEST-PIN): `contracts-edge-0.9.9-r2` manifest |
| ferrum-foundry | `f7eaa96605e2183cec664eccbfee600f46e35f72` | [`PIN`](https://github.com/ferrum-edge/ferrum-foundry/blob/f7eaa96605e2183cec664eccbfee600f46e35f72/contracts/ferrum-contracts/PIN): `contracts-edge-0.9.9-r2` |
| ferrum-edge-git-forge-ops | `76d76c796cafbaea9556e992381b6e2518ae4f69` | [`PIN`](https://github.com/ferrum-edge/ferrum-edge-git-forge-ops/blob/76d76c796cafbaea9556e992381b6e2518ae4f69/contracts/ferrum-contracts/PIN): `contracts-edge-0.9.9`, qualified Edge `v0.9.10` |

The checked tag identities are `contracts-edge-0.9.9` at
`25c4e9e00033d7941a1dd0ab733fa74e735546ae` and `contracts-edge-0.9.9-r2` at
`591c73a3f965fdab440c3a76b2707accdf491ba5`. The published r2 schema already
includes the Alloy-owned optional `[agents]` section. Alloy pins the diagnostic
schemas and vocabularies from r2, but does not vendor the service-manifest
schema. A tag pin therefore does not imply consumption of every file in it.

The previous snapshot inspected Edge main
`66f25f5f89f1dbd4f7d523f3c57e2ace7f59d017` and published
[v0.9.10](https://github.com/ferrum-edge/ferrum-edge/releases/tag/v0.9.10),
which changed no contract source after v0.9.9 and maps to 0.9.9, with r2 for
the Alloy addition. [Edge #6005](https://github.com/ferrum-edge/ferrum-edge/pull/6005)
has since merged as `c764084b3b51c3f7ffde268c039688d35e49c553`; its actual
unsigned lightweight `v0.9.11` tag was created at 19:46:47 UTC on 2026-10-04.
The [draft canonical candidate](releases/contracts-edge-0.9.11.md) reads those
owner sources. At handoff its release run was still in progress; published
assets/digests/attestations/ABI evidence remain unverified for this candidate.
The latest published canonical release remains r2. No consumer pin changes here.

## Draft admin and shared v1 adoption boundary

The new [admin contracts](admin-contracts.md) cover Edge #5992/#5994 source at
the immutable v0.9.11 commit: credential-complete consumer verification,
coherent conditional backup metadata/namespace restore and process egress
discovery. The schema/fixtures are a canonical publication candidate, not
evidence of consumer adoption. GitForgeOps must adopt complete verification
and coherent tokens; Nexus (GHSA-93rq-89vr-38pc part B), Foundry and other
publishers must check every relevant serving DP's policy and scope. CP policy
metadata cannot substitute for DP checks. Missing/unknown policy data or
incompatible scopes block public-only publication. No newly released patched
consumer version or pin is recorded by this draft.

Alloy report/manifest provenance is re-read at qualified owner
`d7ddb3688e058ec3cc2e17d166a801aa0037b5b1`, preserving wire fields, bounds,
paired descriptions and fixture semantics. Candidate metadata records the
qualified consumer slices below and the owner proposal at
`725914bee883b3a6248ee68bafec3040b1fa35d0`; that unmerged proposal is not
final approval or the final matched owner SHA. Root must supply the qualified
owner merge/decision before canonical merge and promote shared status only
with matching evidence. Report shared status and manifest status stay
**PROPOSED**. Alloy remains unpublished; no crate publishing approval follows.

After owner qualification and actual Edge publication verification, root
reviews/merges the canonical change, verifies its own merge/qualified second
parent and all applicable PUSH runs, and publishes the immutable tag. Only
then do consumer pins/checksums/local annotations move together, preserving
Alloy's full schema parity including descriptions. The existing consumer pins
remain the released adoption boundary.

Historical 2026-10-01 audit: all five consumers then pinned 0.9.9. Foundry
(#523) and GitForgeOps (#443) had moved from 0.9.8 and checked the mapping to
their qualified Edge release. The table above supersedes those current-pin
claims.

## Status by consumer

| Consumer | Contract | Consumer source and pinned copy | Status |
|---|---|---|---|
| ferrum-anvil | Gateway error vocabulary | Local release catalogs, finding labels, token mappings and `TOKENS` list; pinned copy at `contracts/ferrum-contracts/vocabularies/gateway-errors.json` | adopted: r2 pin; `contracts_adoption` checks hashes and local token/class parity |
| ferrum-anvil | Gateway-owned headers | `catalog/ferrum/ferrum-edge-*/outcomes.json`; pinned copy at `contracts/ferrum-contracts/vocabularies/gateway-headers.json` | adopted: CI checks released diagnostic headers against the pin; `X-Ferrum-Diagnostic-Ref` is released in Edge v0.9.9 |
| ferrum-anvil | `DiagnosticFinding` (owner) | `contracts/schemas/DiagnosticFinding.schema.json` remains the generated schema; pinned schema and valid/invalid fixtures are under `contracts/ferrum-contracts/` | adopted: CI checks schema parity (excluding `$id` and `x-contract`) and validates the pinned fixtures |
| ferrum-anvil | `diagnostic_ref` | `docs/g01-gateway-diagnostic-contract.md`; shared schema at `schemas/diagnostic-ref/v1.schema.json` | adopted: pinned at `contracts/ferrum-contracts/schemas/diagnostic-ref/v1.schema.json` (ferrum-anvil#271); `contracts_adoption` checks the reference pattern and lookup vocabularies against Anvil's reader (ferrum-anvil#274) |
| ferrum-anvil | `diagnostic_report` | `crates/anvil-diagnostics/src/import.rs`, dedicated desktop command and preview; pinned report schema and all report fixtures under `contracts/ferrum-contracts/` | consumer implemented and qualified in #312: bounded, unverified, read-only import; canonical shared status remains **PROPOSED** |
| ferrum-alloy | Gateway error vocabulary | Local token explanations in `crates/ferrum-alloy-diagnostics/src/catalog.rs` and `rules.rs`, plus `crates/ferrum-alloy-edge/src/contract.rs`; pinned vocabulary under `contracts/ferrum-contracts/` | adopted: the pin hashes the vocabulary; pairing CI checks local tokens and recorded meanings |
| ferrum-alloy | Gateway-owned headers | `crates/ferrum-alloy-edge/src/contract.rs`; pinned vocabulary at `contracts/ferrum-contracts/vocabularies/gateway-headers.json` | adopted: pairing CI checks the released diagnostic headers against the pin |
| ferrum-alloy | `diagnostic_report` (owner) | Local schema `contracts/diagnostics/diagnostic-report.v1.schema.json`; pinned schema and Finding fixtures under `contracts/ferrum-contracts/` | r2 adopted: CI checks schema parity and pinned Finding fixtures; Anvil now qualifies import of shared fixtures and an immutable real exporter report; canonical shared status remains **PROPOSED** |
| ferrum-alloy | `service_manifest` (owner) | `crates/ferrum-alloy-edge/src/manifest.rs`; fixtures `contracts/fixtures/manifests/*.toml` | owner parser/exporter implemented; shared schema remains **PROPOSED**, includes `[agents]` in r2, and is not vendored by Alloy; Nexus and Foundry qualify JSON preview consumption |
| ferrum-alloy | `diagnostic_ref` | `docs/edge-contract-inventory.md`; shared schema at `schemas/diagnostic-ref/v1.schema.json` | adopted in ferrum-alloy#117: pinned at `contracts/ferrum-contracts/schemas/diagnostic-ref/v1.schema.json`; pairing CI checks `EDGE_DIAGNOSTIC_REF_PATTERN` against the schema |
| ferrum-alloy | GitForgeOps envelope | `crates/ferrum-alloy-edge/src/export.rs` `gitforgeops_files` output | consumer qualified in GitForgeOps #461: CI generates two trees from an immutable Alloy CLI and validates them through the actual consumer loader, assembler and CLIs |
| ferrum-edge-git-forge-ops | Plugin catalog | `src/plugin_catalog.rs`; pinned copy at `contracts/ferrum-contracts/vocabularies/plugin-catalog.json` | adopted: `PIN` hashes the vocabulary and CI compares local names, priorities, retired names and reserved names |
| ferrum-edge-git-forge-ops | `provisioned-by` | `src/config/assembler.rs`; pinned copy at `contracts/ferrum-contracts/vocabularies/provisioned-by.json` | adopted: CI compares the local label and its usages with the pinned vocabulary |
| ferrum-edge-git-forge-ops | GitForgeOps envelope (owner) | Local `src/config/schema.rs` `Resource`; schema and valid/invalid envelope fixtures under `contracts/ferrum-contracts/` | adopted: 0.9.9 pin hashes the shared envelope schema and fixtures; CI checks the top-level envelope against `Resource` and qualifies actual Alloy-generated trees |
| ferrum-nexus | Plugin catalog | `shared/src/plugins.ts`; pinned copy at `contracts/ferrum-contracts/vocabularies/plugin-catalog.json` | adopted: `PIN` hashes the vocabulary and CI checks local plugin names against it |
| ferrum-nexus | `provisioned-by` | `server/src/ferrum-admin/client.ts` and test double; pinned vocabulary at `contracts/ferrum-contracts/vocabularies/provisioned-by.json` | adopted: CI checks the header and value against the pin |
| ferrum-nexus | `service_manifest` | `server/src/service-manifest/`, authenticated route; r2 schema, all shared manifest fixtures and invalid expectations under `contracts/ferrum-contracts/` | consumer implemented and qualified in #519: bounded, namespace-authorized, redacted JSON preview; canonical schema remains **PROPOSED** |
| ferrum-foundry | Plugin catalog | `src/lib/pluginConfigDefaults.ts`; pinned copy at `contracts/ferrum-contracts/vocabularies/plugin-catalog.json` | adopted: `PIN` hashes the vocabulary and CI checks local metadata and defaults against it |
| ferrum-foundry | `provisioned-by` | `server/proxy.ts`, `src/components/shared/ResourceLabels.tsx`, `scripts/mock-admin-gateway.mjs`; pinned vocabulary under `contracts/ferrum-contracts/` | adopted: CI checks header, value and label usage against the pin |
| ferrum-foundry | `service_manifest` | `server/service-manifest.ts`, authenticated route and preview card; r2 schema and all shared manifest fixtures under `contracts/ferrum-contracts/` | consumer implemented and qualified in #540: bounded, namespace-authorized, redacted JSON preview; canonical schema remains **PROPOSED** |

A contract copy is **adopted** when the consumer pins an immutable
`contracts-edge-*` tag or its commit and CI fails when its local copy differs.
The Alloy consumer qualifications below additionally exercise actual reader
or validator paths. Their limits do not imply production deployment, a shared
v1 freeze or a newly released contracts tag.

## ferrum-alloy#27 checklist

[ferrum-alloy#27](https://github.com/ferrum-edge/ferrum-alloy/issues/27)
tracks consumers of Alloy's contracts. The implemented portions of its
original checklist are separated from the remaining owner decision:

- [x] Anvil importer and cross-repository fixture/producer checks: #312.
- [x] GitForgeOps consumer validation of real generated files: #461.
- [x] Nexus and Foundry consumer-side manifest fixture tests and bounded
      presentation of the r2 fields, including agents: #519 and #540.
- [x] Foundry authenticated presentation ADR:
      [`docs/adr/0001-alloy-authenticated-presentation.md`](https://github.com/ferrum-edge/ferrum-foundry/blob/f7eaa96605e2183cec664eccbfee600f46e35f72/docs/adr/0001-alloy-authenticated-presentation.md).
- [ ] Owner/consumer agreement on matching immutable producer sources and
      the canonical shared v1 freeze; promote shared status only through a
      separately reviewed owner-backed contracts change.

These checks record consumer implementation and qualification only. They do
not complete the original combined Anvil requirement to mark the shared report
EXISTING, or the manifest requirement to freeze v1. Issue #27 stays open.

### Immutable hosted qualification

All four consumer PRs merged on 2026-10-04. The implementation evidence
describes merged source and hosted runs without claiming a new product release.
These are the final PR heads and their hosted evidence, distinct from the
`main` commits in the pin table:

| Consumer PR | Final head | Hosted evidence |
|---|---|---|
| [Anvil #312](https://github.com/ferrum-edge/ferrum-anvil/pull/312) | `591cb7343dc2cac3a3b540cdc7ba4dd7f2826c0d` | All 14 head checks passed: [CI](https://github.com/ferrum-edge/ferrum-anvil/actions/runs/37215403882), [Desktop E2E](https://github.com/ferrum-edge/ferrum-anvil/actions/runs/37215403895), [Lab](https://github.com/ferrum-edge/ferrum-anvil/actions/runs/37215403908). Main also passed 12 checks across its two push workflows. |
| [Foundry #540](https://github.com/ferrum-edge/ferrum-foundry/pull/540) | `ea322e9f584885c09e59fcbbbe255148754b476c` | [CI 37203276827](https://github.com/ferrum-edge/ferrum-foundry/actions/runs/37203276827): seven applicable gates passed; two publishing jobs skipped on the PR. |
| [GitForgeOps #461](https://github.com/ferrum-edge/ferrum-edge-git-forge-ops/pull/461) | `e06f986dfeabb9bcb0c546c74b646f01e1c2a932` | [Static Validation 37201275273](https://github.com/ferrum-edge/ferrum-edge-git-forge-ops/actions/runs/37201275273): required pairing and static gate passed; other applicable head checks passed. |
| [Nexus #519](https://github.com/ferrum-edge/ferrum-nexus/pull/519) | `77fdb767ec8ef04e88f13df9fb291bc77fbd0344` | All 11 head checks passed: [CI 37221116488](https://github.com/ferrum-edge/ferrum-nexus/actions/runs/37221116488) and [quickstart 37221116610](https://github.com/ferrum-edge/ferrum-nexus/actions/runs/37221116610). |

At the 2026-10-04 17:50 UTC API check, Nexus' main push
[CI 37221550909](https://github.com/ferrum-edge/ferrum-nexus/actions/runs/37221550909)
had completed successfully and all 10 main check runs had passed. This was
checked separately from the passed PR head.
Alloy's inspected main passed all 18 checks in
[CI 37218434984](https://github.com/ferrum-edge/ferrum-alloy/actions/runs/37218434984).
Its first diagnostic producer exists, but Alloy remains pre-release and
unpublished (`publish = false`). Qualification below binds to the specific
producer commits exercised, not arbitrary newer owner sources.

### Anvil diagnostic import boundary

[Anvil's import design and evidence](https://github.com/ferrum-edge/ferrum-anvil/blob/c19c0a6abba896bfec972b3e083179c55ef8e38c/docs/architecture/shared-diagnostics-import.md)
cover the report, standalone Finding, diagnostic reference and source-derived
CLI envelope. Native Linux/macOS/Windows
[run 37214333011](https://github.com/ferrum-edge/ferrum-anvil/actions/runs/37214333011),
at code commit `925e96253d36ea69a5f52a83a9c21602bb7557e4`, imports all 27
shared fixtures through the actual app and IPC. The real Alloy exporter golden
comes from producer `0c260f5379939ff46d681666bfbcd65b8518b08d`,
[run 37208769030](https://github.com/ferrum-edge/ferrum-alloy/actions/runs/37208769030),
artifact `11305688717`; its archive, report and source digests are pinned in
[`tests/fixtures/alloy/PIN`](https://github.com/ferrum-edge/ferrum-anvil/blob/c19c0a6abba896bfec972b3e083179c55ef8e38c/crates/anvil-diagnostics/tests/fixtures/alloy/PIN).
This is an actual exported report. CLI-envelope coverage wraps those facts
using the pinned CLI source; it is not a captured full CLI stdout golden.

The strict parser bounds input at 4 MiB, depth 32, 200,000 nodes, 2,048 decoded
UTF-8 bytes per string/key, 5,000 array entries and 128 object members, and
rejects duplicate keys. Schema and semantic validation precede redaction.
The preview is text-only, ephemeral, always unverified with unknown confidence;
reported trust and supplied findings remain claims and confer no authority.
It performs no apply, URL fetch, gateway lookup or persistence. Recognition
and credential-echo redaction are bounded: tiny credentials in arbitrary text
and unrecognized free-text secrets can remain. Importing Alloy's broader report
does not widen Anvil's standalone `DiagnosticFinding` contract.

### Manifest preview boundaries

[Foundry's preview](https://github.com/ferrum-edge/ferrum-foundry/blob/f7eaa96605e2183cec664eccbfee600f46e35f72/docs/alloy-manifest-preview.md)
authenticates and authorizes the namespace through its BFF, checks the pinned
r2 schema and all shared manifest fixtures, and returns bounded redacted
review output. Its hosted gateway test uses the real client and explicitly
submits two HTTP mappings, direct and active-health, to a disposable gateway.
That qualifies HTTP resource admission; the product preview has no production
apply, URL fetch or TLS-file read. The accepted ADR keeps Alloy out of the trace
store role. Diagnostic presentation, diagnostic import and trace queries remain
future work; the ADR does not supply implementation evidence for them.

[Nexus' preview](https://github.com/ferrum-edge/ferrum-nexus/blob/559c350a5370335791cdc3082225dce6056cf547/docs/service-manifest-preview.md)
uses the immutable r2 schema, all shared manifest fixtures and the canonical
invalid-expectations file, with checksum coverage. Tests exercise strict
schema/unknown/null checks, bounds, authentication, CSRF, namespace authorization
and redaction. Only allowlisted summary hints leave the preview. The pinned
asset is included in the production package; the real-Edge packaged acceptance
suite exercises preview. It performs no file or URL fetch, publication, apply,
diagnostic import or trace storage. Agents metadata is informational and cannot
install or select tools. Neither preview freezes the TOML producer or promises
production deployment semantics for every manifest field.

### GitForgeOps generated resource boundary

[GitForgeOps' consumer qualification](https://github.com/ferrum-edge/ferrum-edge-git-forge-ops/blob/76d76c796cafbaea9556e992381b6e2518ae4f69/docs/alloy-consumer.md)
pins Alloy producer `690aed7a9fa8458aeea4ac8416170c8daeb0470b` and its input,
source and lockfile hashes. The required `validator-pairing` job generates both
`orders-api.toml` and `plain-http.toml` resource trees with the actual pinned
CLI, then exercises GitForgeOps' strict loader, schema mirror, assembler,
released Edge validator and real `gitforgeops validate` CLI. Controls cover
unknown/null fields, unsafe paths, escaping symlinks and namespace associations.
This qualifies generated resource consumption, not service-manifest JSON
preview, gateway traffic, TLS handshakes or production apply. It supplies no
claim that human acceptance in GitForgeOps #266 passed.

## Historical drift found while seeding (2026-10-01)

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

- **Canonical owner qualification and shared freeze.** Reconcile the immutable
  Alloy producer revisions exercised above with the owner source and shared
  schema semantics before a coordinated freeze. The published report schema
  records owner `fa471ccb79a444aee04661880af2385596d9da45`; the manifest
  transcription records `4cba0f4a66f85bcee3140e3b92e299275a2507fb`. Their
  released metadata still contains historical no-consumer/untested wording.
  This draft re-reads owner sources at
  `d7ddb3688e058ec3cc2e17d166a801aa0037b5b1` and stages qualification annotations,
  retaining paired descriptions and shared **PROPOSED** statuses. Finalization
  needs the exact matched qualified owner merge, provenance/fixture review,
  owner approval and the normal hosted contracts gate. Any subsequent
  release follows [versioning.md](versioning.md) and
  [release-process.md](release-process.md); existing tags stay immutable.
  Root owns the coordinated freeze and eventual issue #27 status update.
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
