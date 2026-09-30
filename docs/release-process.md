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
5. Move the `CHANGELOG.md` entries under `[Unreleased]` into a
   `[contracts-edge-X.Y.Z]` section.
6. Open a PR. The `Validate contracts` workflow must pass. An owner of each
   changed contract approves (see [ownership.md](ownership.md)).

## Tagging

After the PR merges, a maintainer tags the merge commit:

```sh
git fetch origin
git tag -s contracts-edge-X.Y.Z <merge-commit-sha> -m "Contracts for Ferrum Edge vX.Y.Z"
git push origin contracts-edge-X.Y.Z
```

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
  comment. Dependabot proposes updates weekly. Before accepting one, check
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
