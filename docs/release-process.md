# Release process

A release is a tag on `main` that consumers pin. Tag names and immutability
rules are in [versioning.md](versioning.md).

## After an Edge release

When Ferrum Edge publishes `vX.Y.Z`:

1. Branch from `main` and refresh every vocabulary from the new tag. Read the
   owner's files with `git show vX.Y.Z:<path>` from a clean clone; never copy
   from another consumer.
   - `vocabularies/gateway-errors.json`: `src/retry.rs` (`ErrorClass`,
     `OBS_*`, `x_gateway_error_token_for_class`, `token_for_rejection_phase`)
     and `docs/error_classification.md`.
   - `vocabularies/gateway-headers.json`: `src/proxy/headers.rs`,
     `docs/admin_api.md`, `openapi.yaml`.
   - `vocabularies/provisioned-by.json`: `src/admin/provisioning.rs`,
     `docs/admin_api.md`.
   - `vocabularies/plugin-catalog.json`: `src/plugins/mod.rs`
     (`BUILTIN_PLUGIN_REGISTRATIONS`, `REMOVED_PLUGIN_REGISTRATIONS`),
     `src/plugins/builtin_parity.rs`, and the per-plugin `if`/`then` blocks
     of `PluginConfigBase` in `openapi.yaml`. Record the new
     `openapi.yaml` sha256 (`git show vX.Y.Z:openapi.yaml | shasum -a 256`).
2. Set `edge_release` to `vX.Y.Z` and every `provenance` commit to the tag's
   commit. Update each `main_branch_delta` against Edge `main`.
3. Re-check the schemas that track Edge `main` (`diagnostic-ref`) against the
   release. Move entries marked `unreleased` to the release that ships them.
4. Add or update fixtures for anything that changed, including at least one
   invalid fixture for each new rule.
5. Move the included `CHANGELOG.md` entries under `[Unreleased]` into a
   `[contracts-edge-X.Y.Z]` section.
6. Open a PR. The `Validate contracts` workflow must pass. An owner of each
   changed contract approves (see [ownership.md](ownership.md)).

## contracts-edge-0.9.11 completed publication

The [release record](releases/contracts-edge-0.9.11.md) pins published Edge
`v0.9.11` at `c764084b3b51c3f7ffde268c039688d35e49c553`, its qualified merge
parents/PR and OpenAPI hash. Root verified all 14 downloaded assets against API
digests and seven binary checksum files, three Docker Hub indexes/six platform
and config pairs, and default-image gateway/CNI bytes on amd64/arm64. All 20
Release jobs succeeded, including strict hosted signatures/SLSA/SBOM,
authenticated GHCR parity and Linux GNU ABI gates. GHCR remains private; Edge
image configs contain no revision label.

The new owner sources are `src/admin/conditional_snapshots.rs`, `preconditions.rs`,
`crud.rs`, `backup.rs`, `backend_egress_policy.rs`, admin routing, transaction
backends, `src/config/env_config.rs`, the admin docs and `openapi.yaml`.
Preserve complete stored credentials, all four coherent row maps, namespace
revision and atomic lease-fenced replacement, standard header semantics,
runtime refusals and unconditional restore. Transcribe bounded process policy
metadata without credentials/raw CIDRs or CP-to-DP attestation; see
[admin-contracts.md](admin-contracts.md).

Final Alloy annotations bind to qualified owner
`81cbb410d34ff5fba1f3d54cfd2e7ebccaed397e`, an ordinary squash of reviewed
PR #144. Its exact immutable sources, full report pairing, root/fresh owner
review and all 18 main PUSH jobs/checks qualify that owner commit. The ordinary
owner squash is not the canonical release/tag target and requires no second
parent. Root accepted the coordinated freeze: report and manifest shared v1 are
EXISTING/implemented in the published release, retaining owner-unreleased
availability. This is the authorized canonical metadata decision, not separate
prior human approval or Alloy crate publishing permission. Preserve every v1
wire field, bound, fixture and unknown-reader rule. Full report pairing includes
descriptions outside `$id`/`x-contract`; the manifest remains a transcription
with documented post-default/cross-field limits.

[PR #13](https://github.com/ferrum-edge/ferrum-contracts/pull/13) completed final
review at `0cf926686f2164ad0b4de7b27e2eb5a25df6a261`; root reviewed the full
change and fresh independent final-delta review reported no findings. Hosted
[run 37240041628](https://github.com/ferrum-edge/ferrum-contracts/actions/runs/37240041628)
passed at that final head, including all 116 validation cases. The earlier
`26a2797f15286da8e32002c4971b68013e134be9` candidate's 45-file review, fresh
review 3 and 116-check hosted validation remain historical evidence; they were
not substituted for final-head qualification.

PR #13 merged at 22:40:08 UTC on 2026-10-04 as
`390edbd5b2485af0988e02f7827fde778d76ae0a`. Its first parent is
`d098c81a50f1baaa8c081d511868c74e957ddf43`; its **second parent equals the
exact final reviewed PR head**, `0cf926686f2164ad0b4de7b27e2eb5a25df6a261`.
Every actual main PUSH workflow succeeded before tag creation: sole applicable
[run 37240886730](https://github.com/ferrum-edge/ferrum-contracts/actions/runs/37240886730)
and required [Schemas, fixtures and vocabularies job 111549212572](https://github.com/ferrum-edge/ferrum-contracts/actions/runs/37240886730/job/111549212572).
The immutable unsigned lightweight `contracts-edge-0.9.11` tag points to that
merge commit; [release 403239814](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.11)
was published at 22:41:21 UTC. Earlier PR-head checks were not substituted for
merge-commit qualification.

The immutable tag captured prepared/pending prose and annotations before
publication, including the `[contracts-edge-0.9.11]` changelog section. That
historical wording is preserved and is not a new approval requirement. The
release record and current documentation record the subsequent publication;
the released section and every historical tag remain unchanged.

Consumer pins/checksums/local copies and Alloy's matching local
annotations/descriptions still need coordinated adoption PRs with full hosted
parity. Record new adoption only after those PRs merge and qualify. Existing r2
bytes and consumer snapshots remain historical. Canonical metadata does not
patch a product advisory or qualify production apply/performance. Root owns
issue disposition and separate publishing permission.

Documentation updates use static source/diff inspection and integrity hashing
only; repository execution is prohibited locally. GitHub-hosted `Validate contracts`
is the schema/fixture/OpenAPI gate. The existing validator discovers the added
files and shared label/order references without workflow, permission, dependency
or validation exceptions.

## Tagging

After the PR merges, a maintainer tags the merge commit. When a signing key
is configured, create a signed annotated tag:

```sh
git fetch origin
git tag -s contracts-edge-X.Y.Z <merge-commit-sha> -m "Contracts for Ferrum Edge vX.Y.Z"
git push origin contracts-edge-X.Y.Z
```

If signing is unavailable, a lightweight tag is acceptable:

```sh
git fetch origin
git tag contracts-edge-X.Y.Z <merge-commit-sha>
git push origin contracts-edge-X.Y.Z
```

The tags published so far are lightweight and unsigned. Do not describe
existing tags as signed.

Then create a GitHub release for the tag with the changelog section as its
notes. Never move or delete a pushed tag; publish `contracts-edge-X.Y.Z-rN`
instead.

A revision tag (`-rN`) follows the same steps for a change that is not an
Edge release: a new or changed non-Edge schema, a fixture fix, or a
provenance correction.

## Consumers

Each consumer then opens a PR in its own repository that moves its pin to the
new tag and updates its local copy, and records the change in
[adoption.md](adoption.md) here.

## Maintaining the validation workflow

- **Actions** are pinned by full commit SHA with the release in a trailing
  comment. Dependabot proposes updates weekly for Actions and for
  `ci/requirements.txt`; check that a pip update carries the hash of every
  file pip will install (for `rpds-py`, the CPython 3.13 manylinux x86_64
  wheel). Before accepting one, check
  that the SHA is the tagged commit of that release
  (`gh api repos/<owner>/<action>/tags`).
- **Validator packages** are pinned in `ci/requirements.txt` with sha256
  hashes and installed with `--require-hashes --only-binary=:all:
  --no-deps`. To update a package, read the version's file list from
  `https://pypi.org/pypi/<name>/<version>/json`, download the wheel, and
  confirm `shasum -a 256` matches the published digest before editing the
  file. `rpds-py` is compiled: its hash must be the wheel for the workflow's
  Python version and runner architecture (CPython 3.13, manylinux x86_64).
  Every dependency, including transitive ones, must be listed because pip
  runs with `--no-deps`.
- The workflow has `permissions: contents: read`, uses no secrets, and
  downloads only the pinned PyPI wheels and the Edge `openapi.yaml` at the
  commit the plugin catalog pins (checked against its sha256).
