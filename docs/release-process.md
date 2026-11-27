# Release process

A release is a tag on `main` that consumers pin. Tag names and immutability
rules are in [versioning.md](versioning.md).

## After an Edge release

When Ferrum Edge publishes `vX.Y.Z`:

1. Branch from `main` and refresh every vocabulary from the new tag. Read the
   owner's files with `git show vX.Y.Z:<path>` from a clean clone; never copy
   from another consumer.
   - `vocabularies/gateway-errors.json`: `src/retry.rs` (`ErrorClass`,
     `OBS_*`, `x_gateway_error_token_for_class`, `token_for_rejection_phase`),
     `src/proxy/mod.rs` (`http_backend_failure_status_and_body`),
     `docs/error_classification.md`, and `docs/size_limits.md` ("gRPC and
     gRPC-Web framing of pre-routing refusals").
   - `vocabularies/gateway-headers.json`: `src/proxy/headers.rs`,
     `src/proxy/mod.rs` (`refresh_backend_gateway_assertion_headers`),
     `src/plugins/mod.rs` (`RequestContext` identity accessors),
     `src/plugins/mesh/{spiffe_identity,ext_authz}.rs`, `docs/plugins.md`
     ("Consumer Identity Headers"), `docs/admin_api.md`, `openapi.yaml`.
   - `vocabularies/provisioned-by.json`: `src/admin/provisioning.rs`,
     `docs/admin_api.md`.
   - `vocabularies/plugin-config-sensitivity.json`:
     `src/admin/plugin_config_projection.rs` and
     `src/plugins/utils/metadata_redaction.rs` (placeholders; `FieldSensitivity`,
     `PLUGIN_SENSITIVITY_SCHEMAS` with every shared rule set expanded,
     `KAFKA_SAFE_PRODUCER_PROPERTIES`). CI requires an entry for every
     catalog plugin.
   - `vocabularies/reserved-header-names.json`: `src/plugins/correlation_id.rs`
     (`RESERVED_HEADER_NAMES`, `is_reserved_header_name`).
   - `vocabularies/mcp-openapi-bridge.json`: `src/admin/api_specs/extractor.rs`
     (`X_FERRUM_MCP_*` key sets, `MAX_MCP_BRIDGE_*`) and
     `src/plugins/mcp_openapi_bridge.rs` (`MAX_BRIDGE_*`,
     `MAX_FORWARDED_REQUEST_HEADERS`, `ANNOTATION_KEYS`, `BridgeMethod`,
     `RESERVED_BRIDGE_HEADER_NAMES` / `_PREFIXES`).
   - `vocabularies/plugin-catalog.json`: `src/plugins/mod.rs`
     (`BUILTIN_PLUGIN_REGISTRATIONS`, `REMOVED_PLUGIN_REGISTRATIONS`),
     `src/plugins/builtin_parity.rs`, and the per-plugin `if`/`then` blocks
     of `PluginConfigBase` in `openapi.yaml`. Re-transcribe registration
     failure policies, parity phases/priorities/protocols and every
     `PluginConfigBase` conditional; do not refresh only their pins. Record the
     new `openapi.yaml` sha256 (`git show vX.Y.Z:openapi.yaml | shasum -a 256`)
     only after the owner configuration compatibility check below. Then
     regenerate the standalone plugin config schemas from that file:
     `git show vX.Y.Z:openapi.yaml > /tmp/openapi.yaml` and
     `python3 -I ci/plugin_config_schemas.py --openapi /tmp/openapi.yaml --write`
     (standard library only), and commit `plugin-config-schemas/`. CI fails a
     catalog re-pin whose generated files were not regenerated.
   - `vocabularies/backend-egress-policy.json`: `openapi.yaml`,
     `src/admin/backend_egress_policy.rs`,
     `src/grpc/backend_egress_attestation.rs`, `src/config/env_config.rs`, and
     the owner admin docs. A new response `schema_version` or a changed
     classifier, label or guarantee meaning needs a new major of the response
     and vocabulary schemas (Edge v0.9.13 moved both to v2).

   **Owner configuration compatibility check (from `contracts-edge-1.0.0`
   on).** The plugin catalog's JSON shape is versioned here, but the
   configuration schemas it points to are Edge's own API, governed by Edge's
   support policy ([versioning.md](versioning.md#stability-promise-for-contracts-edge-1),
   rule 5). Before re-pinning, compare the previously pinned file with the
   new one (`git diff <config_schema_document.commit> vX.Y.Z -- openapi.yaml`
   in a clean Edge clone) for `PluginConfigBase`, every component a plugin's
   `config_schema` pointer names and everything those components reach
   through `$ref`. Breaking for an existing configuration: a removed or
   renamed property, a property that becomes required, a removed enum
   value, a narrowed type, pattern, bound or length, an object closed with
   `additionalProperties: false`, a pointer that no longer resolves, a plugin
   whose `config_required_when_enabled` becomes true or that gains a
   `scope_constraint`, and a plugin moved to `removed_plugins`. Compatible: a
   new optional property, a new enum value, a widened bound, a new plugin. A
   breaking change is never re-pinned silently: the release PR names each one
   and the Edge release that made it, asks the Edge owner to confirm it is
   allowed by Edge's support policy (with an Edge upgrade note), and the
   release record and `CHANGELOG.md` list it under "Changed". For
   `contracts-edge-1.0.0` itself the comparison with `v0.9.21` is recorded in
   the same way; pre-1.0 changes are allowed, but are still listed.
2. Set `edge_release` to `vX.Y.Z` and every `provenance` commit to the tag's
   commit. Keep the `main_branch_delta` block in `plugin-catalog.json`,
   `gateway-headers.json` and `gateway-errors.json`; never remove it. Promote
   what the release ships into released entries, then reset each delta
   against Edge `main` as read for this PR: `commit` is that full Edge `main`
   commit (on Edge `main`'s history; the release commit itself when `main`
   has not moved past it), and `summary` lists only the contract-visible
   changes on Edge `main` after `vX.Y.Z`. When there are none, use the empty
   delta:

   ```json
   "main_branch_delta": {
     "repo": "ferrum-edge/ferrum-edge",
     "ref": "main",
     "commit": "<full Edge main commit>",
     "summary": "No contract-visible changes beyond vX.Y.Z (<full release commit>) at Edge main <full Edge main commit>."
   }
   ```

   The consumers' scheduled Edge `main` checks read `.main_branch_delta.commit`
   from this repository's `main`
   ([consumer-pins.md](consumer-pins.md#checking-against-edge-main)). The
   `contracts-edge-0.9.21` release PR (#88) removed the blocks, which left
   those checks without an anchor until #89 restored them; `ci/validate.py`
   now fails if any of the three vocabularies lacks the block or names a
   repository or branch other than Edge `main`.

   No tag through `contracts-edge-0.9.21` carries the block (since
   `contracts-edge-0.9.9`, each release removed it), so the first release
   that keeps it changes what consumers vendor. Prerequisite: consumers'
   tests tolerate the block
   ([consumer-pins.md](consumer-pins.md#required-checks)). The release PR
   names, in its body, every consumer test that asserts the block is absent,
   so that consumer changes the assertion in its re-pin PR; on 2026-11-27
   that was ferrum-foundry's `scripts/ferrum-contracts.test.mjs` (plugin
   catalog).
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

## Between releases

Edge `main` moves between releases. A delta sync PR (for example #90) reads
the Edge sources listed in step 1 at one full Edge `main` commit, sets each
`main_branch_delta.commit` to that commit, and records in each `summary`
every contract-visible change since the published release. It changes
nothing that describes the release: `edge_release`, `provenance` and
`config_schema_document` stay on the published tag, and entries for changes
that only `main` has are marked unreleased. It adds a `CHANGELOG.md` entry
under `[Unreleased]` and creates no tag. While an Edge release candidate is
validated, the synced commit is the candidate commit
([versioning.md](versioning.md#edge-release-candidates)).

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
new tag and updates its local copy. That consumer's
`contracts/ferrum-contracts/PIN` on its `main` is the authoritative record of
its pin; no PR here is needed for a consumer re-pin. The dated snapshot in
[adoption.md](adoption.md) is re-verified from those `PIN` files at the next
contracts release PR or adoption review. The `PIN` file and the checks its
drift test makes are defined in [consumer-pins.md](consumer-pins.md); a
consumer that has not converged yet moves to that format in the same PR.

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
