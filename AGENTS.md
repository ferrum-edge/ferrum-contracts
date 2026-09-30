# AGENTS.md - Ferrum contracts

Versioned wire contracts shared by the Ferrum products (Edge, Anvil, Alloy,
Nexus, Foundry, GitForgeOps), kept as data: JSON Schemas, machine-readable
vocabularies, and conformance fixtures. There is no application code. The
only executable file is the repository's own CI check, `ci/validate.py`.
License: PolyForm Noncommercial 1.0.0.

Proposal and adoption tracking: ferrum-edge/.github#4.

## Layout

- `schemas/<name>/v<N>.schema.json`: JSON Schema 2020-12. `$id` is
  `https://github.com/ferrum-edge/ferrum-contracts/schemas/<name>/v<N>.schema.json`;
  `x-contract` carries `name`, `version`, `status` (`implemented` or
  `proposed`), `owner`, and `provenance`.
- `schemas/vocabulary-<v>/v<N>.schema.json`: the shape of `vocabularies/<v>.json`.
- `vocabularies/<v>.json`: Edge-owned vocabularies. `$schema` names the
  vocabulary schema; `edge_release` names the Edge tag the values came from.
- `fixtures/<name>/{valid,invalid}/*.json`: conformance payloads. Provenance
  and the reason each invalid fixture fails: `fixtures/README.md`.
- `docs/`: `ownership.md`, `versioning.md`, `adoption.md`, `release-process.md`.
- `ci/validate.py`, `ci/requirements.txt`: validation script and its
  hash-pinned dependencies. `.github/workflows/validate.yml` runs them.

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
  fixture changes exactly one thing, and `fixtures/README.md` says what.
- Update `CHANGELOG.md` under `[Unreleased]` in the same PR.
- JSON: 2-space indent, UTF-8, trailing newline, no duplicate keys. Keep key
  order stable so diffs stay reviewable.

## CI and supply chain

- The `Validate contracts` workflow is the gate: schemas against the 2020-12
  meta-schema, `$id`/version/file-name consistency, fixtures (valid pass,
  invalid fail), vocabularies against their schemas plus cross-reference
  checks, the diagnostic-finding to diagnostic-report cross-check, and the
  plugin catalog's pointers into the pinned Edge `openapi.yaml`.
- Actions are pinned by full commit SHA with a version comment.
  `permissions: contents: read`; no secrets; `persist-credentials: false`.
- Python packages are pinned by version and sha256 in `ci/requirements.txt`
  and installed with `--require-hashes --only-binary=:all: --no-deps`.
  Update procedure: `docs/release-process.md`.
- Dependabot updates GitHub Actions weekly (`.github/dependabot.yml`).

## PR and commit workflow

Commit messages use concise imperative mood. PRs need a summary, the list of
changes, and a test plan (normally: the `Validate contracts` workflow). A
contract change needs approval from a maintainer of its owning product.
Reference ferrum-edge/.github#4 without a closing keyword until adoption is
complete.
