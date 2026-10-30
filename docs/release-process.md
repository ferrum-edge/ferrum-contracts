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
     `src/proxy/mod.rs` (`refresh_backend_gateway_assertion_headers`),
     `src/plugins/mod.rs` (`RequestContext` identity accessors),
     `src/plugins/mesh/{spiffe_identity,ext_authz}.rs`, `docs/plugins.md`
     ("Consumer Identity Headers"), `docs/admin_api.md`, `openapi.yaml`.
   - `vocabularies/provisioned-by.json`: `src/admin/provisioning.rs`,
     `docs/admin_api.md`.
   - `vocabularies/plugin-catalog.json`: `src/plugins/mod.rs`
     (`BUILTIN_PLUGIN_REGISTRATIONS`, `REMOVED_PLUGIN_REGISTRATIONS`),
     `src/plugins/builtin_parity.rs`, and the per-plugin `if`/`then` blocks
     of `PluginConfigBase` in `openapi.yaml`. Re-transcribe registration
     failure policies, parity phases/priorities/protocols and every
     `PluginConfigBase` conditional; do not refresh only their pins. Record the
     new `openapi.yaml` sha256 (`git show vX.Y.Z:openapi.yaml | shasum -a 256`).
   - `vocabularies/backend-egress-policy.json`: `openapi.yaml`,
     `src/admin/backend_egress_policy.rs`,
     `src/grpc/backend_egress_attestation.rs`, `src/config/env_config.rs`, and
     the owner admin docs. A new response `schema_version` or a changed
     classifier, label or guarantee meaning needs a new major of the response
     and vocabulary schemas (Edge v0.9.13 moved both to v2).
2. Set `edge_release` to `vX.Y.Z` and every `provenance` commit to the tag's
   commit. Update each `main_branch_delta` against Edge `main`.
3. Re-check Edge-owned schemas (`diagnostic-ref`, conditional backup metadata,
   backend egress policy, deployment snapshot and mutation acknowledgement)
   against the release, reading the owner sources listed in
   [admin-contracts.md](admin-contracts.md#owner-sources-and-artifact-scope) and
   [deployment-contracts.md](deployment-contracts.md#immutable-owner-sources-and-schema-scope).
   Move entries marked `unreleased` only when that owner release actually
   ships them. Preserve unrelated owners' unreleased markers.
   Consumers vendor `diagnostic-ref` v1 byte for byte, so its bytes stay
   frozen while its wire contract is unchanged; a new label in the open
   `rejection.phase` (Edge v0.9.15 `route_protocol_admission`) gets fixtures,
   not new bytes. An incompatible owner change
   adds `v<N+1>.schema.json` and keeps the earlier major
   ([versioning.md](versioning.md)).
4. Add or update fixtures for anything that changed, including at least one
   invalid fixture for each new rule. A schema with several majors keeps each
   major's fixtures in `fixtures/<name>/v<N>/`.
5. Move the included `CHANGELOG.md` entries under `[Unreleased]` into a
   `[contracts-edge-X.Y.Z]` section and write the release record
   (`docs/releases/contracts-edge-X.Y.Z.md`) in final form. Both are tagged
   content and must not carry status words; see
   [Release records and publication status](#release-records-and-publication-status).
6. Open a PR. Repository tooling is not executed locally: local review uses
   static source/diff inspection and integrity hashing, and the GitHub-hosted
   `Validate contracts` workflow on the exact PR head is the gate. An owner of
   each changed contract approves (see [ownership.md](ownership.md)).

## Release records and publication status

The release record and the `[contracts-edge-X.Y.Z]` `CHANGELOG.md` section are
committed before the tag, so their bytes are immutable once the tag exists.
Write them in final form, in descriptive or present tense, and never write
status words such as `pending`, `prepared`, `draft`, `candidate`, `unreleased`
or `pre-publication` into tagged content.

Publication status lives outside the tagged content:

- the PR body records review, hosted-validation and merge state;
- the tracking issue records consumer adoption and follow-up work; and
- the GitHub release notes record facts that only exist after the tag (tag SHA,
  release id, publish timestamp, CI run ids).

Do not open a cleanup PR after each release to rewrite a release record or
changelog section. If a record is wrong, correct it in the next release PR, or
link the Edge release and its release record instead of editing tagged history.
Historical per-release evidence is in [releases/](releases) and each GitHub
release.

## Tagging

Every future release, including a revision (`-rN`), requires an SSH-signed
annotated tag made by an authorized maintainer. If the approved signing key
or trusted verification policy is unavailable, stop publication. There is no
unsigned fallback. See [Release signing](release-signing.md) for approval,
setup, public trust files, consumer verification, rotation and revocation.

After the release PR merges and its merge commit passes the required checks,
the authorized maintainer performs the following in the configured release
checkout. Set `RELEASE_TAG` to the actual authorized version,
`RELEASE_COMMIT` to its full merge commit SHA, and `TRUSTED_SIGNERS` and
`TRUSTED_REVOKED_KEYS` to absolute paths to the independently reviewed public
trust files. These commands are publication steps, not permission to publish.

```sh
set -eu
: "${RELEASE_TAG:?Set the actual authorized release tag}"
: "${RELEASE_COMMIT:?Set the full qualified merge commit SHA}"
: "${TRUSTED_SIGNERS:?Set the approved allowed_signers path}"
: "${TRUSTED_REVOKED_KEYS:?Set the approved revoked_signers path}"
test -f "$TRUSTED_SIGNERS"
test -r "$TRUSTED_SIGNERS"
test -f "$TRUSTED_REVOKED_KEYS"
test -r "$TRUSTED_REVOKED_KEYS"
git fetch origin
test "$(git config --get gpg.format)" = ssh
git merge-base --is-ancestor "$RELEASE_COMMIT" origin/main
git tag -s "$RELEASE_TAG" "$RELEASE_COMMIT" -m "Ferrum Contracts $RELEASE_TAG"
git -c gpg.ssh.allowedSignersFile="$TRUSTED_SIGNERS" \
    -c gpg.ssh.revocationFile="$TRUSTED_REVOKED_KEYS" \
    -c gpg.openpgp.program=false -c gpg.x509.program=false \
    verify-tag "refs/tags/$RELEASE_TAG"
test "$(git rev-parse "refs/tags/$RELEASE_TAG^{commit}")" = "$RELEASE_COMMIT"
git rev-parse "refs/tags/$RELEASE_TAG"
git push origin "refs/tags/$RELEASE_TAG:refs/tags/$RELEASE_TAG"
```

Record the printed tag object SHA separately from the commit SHA. Before
creating a GitHub release, verify the remote tag from a clean consumer clone
using the [documented test](release-signing.md#verify-a-downloaded-tag).

Existing tags through `contracts-edge-0.9.19` are lightweight and unsigned.
Preserve them; never describe them as signed or replace them to add a signature.

Then create a GitHub release for the tag with the changelog section as its
notes, plus both object SHAs, the public signer fingerprint, trust-policy
commit, verification result and CI evidence. Never move or delete a pushed
tag; use a separately authorized `contracts-edge-X.Y.Z-rN` for a correction.
The existing immutable-tag rules remain in force. A GitHub release's
`immutable` field is separate from tag protection and cryptographic verification.

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
