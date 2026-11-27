# AGENTS.md - Ferrum contracts

Versioned wire contracts shared by the Ferrum products (Edge, Anvil, Alloy,
Nexus, Foundry, GitForgeOps), kept as data: JSON Schemas, machine-readable
vocabularies, and conformance fixtures. There is no application code, no
parser or client library, and no generated types or crates: consumers
generate or write their own types from the schemas. The only executable files
are the repository's own CI check, `ci/validate.py`, the stdlib-only generator
`ci/plugin_config_schemas.py`, their tests, `ci/test_*.py`, and the agent
dispatch launchers under `.agents/skills/` (repository tooling, not contract
content).
License: PolyForm Noncommercial 1.0.0 (`LICENSE`); commercial use needs the
commercial license in `LICENSE-COMMERCIAL.md`.

Proposal and adoption history: ferrum-edge/.github#4 (closed; adoption
completed).

## Layout

- `schemas/<name>/v<N>.schema.json`: JSON Schema 2020-12. `$id` is
  `https://github.com/ferrum-edge/ferrum-contracts/schemas/<name>/v<N>.schema.json`;
  `x-contract` carries `name`, `version`, `status` (`implemented` or
  `proposed`), `owner`, and `provenance` (required, and checked by CI, when
  the owner is another repository).
- `schemas/vocabulary-<v>/v<N>.schema.json`: the shape of `vocabularies/<v>.json`.
- `vocabularies/<v>.json`: Edge-owned vocabularies. `$schema` names the
  vocabulary schema; `edge_release` names the Edge tag the values came from.
- `fixtures/<name>/{valid,invalid}/*.json`: conformance payloads; a schema
  with several majors uses `fixtures/<name>/v<N>/{valid,invalid}/` per major.
  Provenance and the reason each invalid fixture fails: `fixtures/README.md`.
- `plugin-config-schemas/<plugin>.schema.json`: generated, never hand-edited.
  One standalone JSON Schema 2020-12 document per catalog plugin, made by
  `ci/plugin_config_schemas.py --openapi <pinned openapi.yaml> --write` from
  the file `config_schema_document` pins; regenerate whenever that pin moves.
- `resource-schemas/<Component>.schema.json`: generated the same way, one
  standalone document per Edge Admin API resource request schema
  (`ProxyCreate`, `UpstreamCreate`, `ConsumerCreate`, `PluginConfigCreate`,
  `GatewayTrustBundleCreate`); its README lists the Rust-only admission rules
  the schemas do not carry.
- `qualification/<name>/v<N>/*.json`: schema-valid (or invalid) payloads with
  the producer's own outcome for rules the schema cannot express; not
  fixtures. Layout and policy: `qualification/README.md`.
- `docs/`: `ownership.md`, `versioning.md`, `adoption.md`, `consumer-pins.md`
  (the consumer `PIN` format and the consumers' Edge `main` check),
  `release-process.md`, `admin-contracts.md`,
  `deployment-contracts.md`, `plugin-config-admission.md`,
  `release-signing.md`, the release trust policy `allowed_signers` and
  `revoked_signers`, and `releases/` (tagged release records).
- `ci/validate.py`, `ci/requirements.txt`: validation script and its
  hash-pinned dependencies. `ci/test_validate.py`: loopback tests for the
  bounded `--fetch-openapi` download and offline tests of the schema
  provenance check, the gateway-headers availability and unpublished Edge
  tag checks, the vocabulary `x-contract.instance` check, the
  `main_branch_delta` presence check, the
  `diagnostic-ref` values copied from `gateway-errors`, the
  `PluginConfigBase` parser and catalog parity check, the generated plugin
  config schema check, and the cross-contract fixture check.
  `ci/test_plugin_config_schemas.py`: the generator's YAML reader and output. `ci/test_release_signing.py`: offline
  tests of the documented release verification using public signed data;
  no keys are generated or private keys accessed. `.github/workflows/validate.yml`
  runs both.
- `.agents/skills/<name>-agents/` and `.claude/skills/<name>-agents/`: agent
  dispatch skills (Codex and Claude entrypoints, worker briefs, launchers)
  matching the ones in ferrum-edge, with this repository's validation and
  review rules. They are tooling and never part of a contracts release.

## Rules

- **Never invent contract content.** Every schema, vocabulary value and
  fixture comes from its owning repository, with repository, path and full
  commit SHA recorded in `provenance` (or in `fixtures/README.md`). If the
  owner has no machine-readable form, transcribe it and say so in a `note`;
  if it has none at all, record the gap in `docs/adoption.md` instead of
  guessing.
- Read owner sources from a clean clone at a tag or commit
  (`git show <ref>:<path>`), never from another consumer's copy.
- Mark anything that exists only on an owner's default branch
  (`availability: unreleased`, `main_branch_delta`, or
  `x-contract.edge_availability`). Never present it as released.
- Ownership, versioning and tags: `docs/ownership.md`, `docs/versioning.md`.
  Breaking changes need a new `v<N+1>` file; tags `contracts-edge-X.Y.Z`
  are immutable.
- Every schema needs at least one valid and one invalid fixture. An invalid
  fixture changes exactly one thing, `fixtures/README.md` says what, and
  `fixtures/invalid-expectations.json` records the instance path and keyword
  CI must see.
- Values a schema copies from a vocabulary (the `diagnostic-ref`
  `gateway_error` and `detail.rejection_phase` enums, the `ref` and
  `replica_id` patterns) must match the vocabulary; CI checks it. Closed-enum policy: `docs/versioning.md`.
- Update `CHANGELOG.md` under `[Unreleased]` in the same PR.
- Tagged content is immutable: the `[contracts-edge-*]` `CHANGELOG.md`
  sections, `docs/releases/contracts-edge-*.md`, schemas and vocabularies are
  committed before the tag. Write them in final form; never write status words
  such as `pending`, `prepared`, `draft`, `candidate` or `pre-publication` into
  them. Status lives in PR bodies and tracking issues, not in tagged files.
- JSON: 2-space indent, UTF-8, trailing newline, no duplicate keys. Keep key
  order stable so diffs stay reviewable.

## CI and supply chain

- The `Validate contracts` workflow is the gate: schemas against the 2020-12
  meta-schema, `$id`/version/file-name consistency, provenance of schemas
  owned by another repository, fixtures (valid pass,
  invalid fail with the expected path and keyword, formats asserted), vocabularies against their schemas plus cross-reference
  checks and the gateway-headers `availability` rule (a published Edge
  release no later than `edge_release`, and no unpublished Edge tag in any
  Edge release field), a `main_branch_delta` on Edge `main` in the
  plugin-catalog, gateway-headers and gateway-errors vocabularies, the diagnostic-finding to diagnostic-report cross-check,
  qualification cases (each `instance` passes its schema exactly when
  `schema_valid` says so, and recorded producer outcomes match the producer
  rule CI transcribes), and the
  plugin catalog's pointers, `config_required_when_enabled` and
  `scope_constraint` against the pinned Edge `openapi.yaml`, and
  `plugin-config-schemas/` (2020-12 meta-schema, catalog pin, and with the
  pinned file, byte equality with the generator and an independent PyYAML
  parse equal to the generator's YAML reader).
- Actions are pinned by full commit SHA with a version comment.
  `permissions: contents: read`; no secrets; `persist-credentials: false`.
- Python packages are pinned by version and sha256 in `ci/requirements.txt`
  and installed with `--require-hashes --only-binary=:all: --no-deps`.
  Update procedure: `docs/release-process.md`.
- Dependabot updates GitHub Actions and `ci/requirements.txt` weekly
  (`.github/dependabot.yml`).
- `main` requires the `Schemas, fixtures and vocabularies` check and no
  approving reviews (ruleset 24239605; the repository is solo-maintained).
  Changes land by pull request with all review threads resolved; force-push
  and deletion are blocked. Ruleset 24979475 also requires the
  `validate.yml` workflow from `main` to run (renaming or moving that file
  needs a ruleset update).

## PR and commit workflow

Commit messages use concise imperative mood. PRs need a summary, the list of
changes, and a test plan (normally: the `Validate contracts` workflow). A
contract change needs approval from a maintainer of its owning product.
Reference ferrum-edge/.github#4 as closed history; adoption is complete.
