# Consumer pins

A consumer vendors the contract files it uses under
`contracts/ferrum-contracts/` and records them in a `PIN` file in that
directory. The record holds the release tag, the tag's commit and one sha256 per
file. This document defines one format for that file and the checks every
consumer's drift test must make, so the same mistake fails in every consumer.
It also describes the scheduled check every consumer runs against Edge `main`
([Checking against Edge main](#checking-against-edge-main)).

The format is plain text. Its checksum rows are the line shape that `sha256sum`
and `shasum -a 256` print, so maintainers can check the hashes with stock tools
(see [Checking by hand](#checking-by-hand)). Each consumer parses and checks
it in its own language, in its own test. This repository ships no parser
([AGENTS.md](../AGENTS.md): no application code).

## Format

`PIN` is ASCII text with LF line endings and a final newline. It has no byte
order mark, no carriage returns, no blank lines, no comments, and no leading
or trailing spaces on any line. The lines are, in this order:

| Line | Form | Rule |
|---|---|---|
| 1 | `tag <tag>` | The pinned release tag. It matches `^contracts-edge-[0-9]+\.[0-9]+\.[0-9]+(-r([2-9]|[1-9][0-9]+))?$`: a revision number starts at 2 (see [versioning.md](versioning.md#release-tags)). |
| 2 | `commit <sha>` | The full commit the tag points to (the peeled tag), as 40 lowercase hex digits. |
| 3, optional | `edge_version <version>` | The Ferrum Edge release the consumer targets with this pin, such as `v0.9.20`. It matches `^v[0-9]+\.[0-9]+\.[0-9]+$`. Use it when the consumer's own checks depend on the Edge release (GitForgeOps does). |
| rest, at least one | `<sha256>  <path>` | One row per vendored file: 64 lowercase hex digits, **two** spaces, then the path. |

A single space separates a header key from its value. `tag` and `commit`
appear exactly once, and `edge_version` at most once, in the order above. A row is the `sha256sum` text-mode line for
that file, run from the vendored directory.

A row's `<path>` is the file's path in this repository at the tag. It is also
the file's path relative to the directory that holds `PIN`, because the copy
keeps the repository's layout. The path:

- uses `/` separators, and has no leading `/`, no trailing `/` and no empty
  segment;
- has segments that match `^[A-Za-z0-9._-]+$` and are not `.` or `..`;
- is not `PIN`: the `PIN` file at the top of the vendored directory never
  lists itself.

Rows are sorted by path, comparing the path strings byte by byte (for the
rows alone, `LC_ALL=C sort -k2` gives this order). Compare whole strings, not
path components: `a-b/x` sorts before `a/x`. A duplicate is then adjacent to
its twin, and a diff shows one line per changed file.

Example (`contracts-edge-0.9.20`, abbreviated):

```text
tag contracts-edge-0.9.20
commit 39da322083044c2e92617209e62983c92387f0ad
edge_version v0.9.20
a5c04514fa38df6b27182c142fcd7abcf9f0c8829a9f0a0b49e5cab80240e410  fixtures/diagnostic-finding/valid/ferrum-token-backend-error.json
9a30593787478a1be549e3ffdf7da377d2477b1b84722f07ae4fbc5ba4bcf338  schemas/diagnostic-finding/v1.schema.json
e848d644ed84e6e56c0e1125a1e050b92966c3643c2330cf281bd1dfa0ef2dea  vocabularies/gateway-errors.json
```

A consumer keeps **one** `PIN` per vendored directory, and that `PIN` lists
every file in it. A test that needs only some of the files selects them by
path from that one `PIN`. A consumer that needs a separately pinned set, such
as another tag, vendors it in its own directory with its own `PIN`.

## Required checks

Every consumer's drift test runs offline in CI and fails on each of the
following:

1. **Strict parse.** Any line that does not match its position in the
   [format](#format) fails the test. This covers an unknown key, a repeated or
   misplaced header, a malformed or uppercase hash, one or three spaces
   between hash and path, a path that breaks the path rules, and a blank,
   commented, CR-terminated or unterminated line. Unknown lines are never
   skipped.
2. **Headers.** `tag` and `commit` are present exactly once and
   `edge_version` at most once, in that order, with the forms above.
3. **No duplicates, sorted.** Paths are strictly ascending in byte order. This
   also refuses a path listed twice.
4. **Tree equality.** The set of row paths equals the set of files under the
   vendored directory, other than `PIN`. Every vendored file has exactly one
   row, and no row names a missing file. A symbolic link, or any entry that is
   neither a regular file nor a directory, fails the test. A test that
   compares rows with a hard-coded list instead of the filesystem does not
   meet this check.
5. **Content.** Each file's sha256, computed over its bytes as checked out,
   equals its row.

A consumer may add its own checks. Examples are a list of files it must pin,
or parity between a vendored vocabulary and its source code.

Some properties cannot be checked offline. The author of the pin/copy/checksum
PR establishes them before writing the `PIN`, from a clean clone of this
repository:

- a signed tag (`contracts-edge-0.9.20` and later) verifies as described in
  [release-signing.md](release-signing.md#verify-a-downloaded-tag). The
  existing tags through `contracts-edge-0.9.19` are lightweight and
  unsigned, so they have no signature to verify. Their commit is the
  immutable tag itself, read as in the next item;
- `commit` is `git rev-parse 'refs/tags/<tag>^{commit}'`;
- every vendored file is `git show <tag>:<path>` byte for byte. Copy files from
  the tag, never from `main` or from another consumer's copy;
- `edge_version`, when present, is an Edge release that
  [versioning.md](versioning.md#release-tags) maps to the tag. One tag can
  back several Edge releases: Edge `v0.9.10` maps to `contracts-edge-0.9.9`
  (and so to `-r2`).

Copies must keep their bytes on every platform CI runs on. Mark the vendored
directory `-text` in the consumer's `.gitattributes` (for example
`contracts/ferrum-contracts/** -text`), so a Windows checkout with
`core.autocrlf` does not rewrite line endings and break check 5.

## Checking by hand

From the consumer repository's root, in bash or zsh, with GNU coreutils or
macOS:

```bash
cd contracts/ferrum-contracts
# Content (check 5). On macOS use `shasum -a 256 -c` instead of `sha256sum -c`.
grep -E '^[0-9a-f]{64}  ' PIN | sha256sum -c
# Tree equality (check 4): no output means the sets are equal.
diff <(grep -E '^[0-9a-f]{64}  ' PIN | cut -c67-) \
     <(find . -type f ! -path ./PIN | sed 's|^\./||' | LC_ALL=C sort)
# Anything that is neither a regular file nor a directory: expect no output.
find . ! -type f ! -type d
```

These commands are a convenience and skip the strict parse (check 1). They do
not replace the consumer's test.

## Checking against Edge main

A `PIN` binds a consumer to an Edge release, so its drift test cannot see a
breaking change that has landed only on Edge `main`. Such a change reaches the
consumer when it re-pins to the next release, or when an operator upgrades
Edge and the consumer's writes start failing. Each consumer therefore also
runs a scheduled check against Edge `main`, apart from its required checks
(ferrum-contracts#76).

This repository records what Edge `main` changes in a `main_branch_delta`
object in `vocabularies/plugin-catalog.json`,
`vocabularies/gateway-headers.json` and `vocabularies/gateway-errors.json` on
this repository's `main`:

- `repo` and `ref` name Edge and its `main` branch.
- `commit` is the full Edge commit the delta was read at. It is the
  machine-readable anchor: fetch Edge sources at this commit, and compare them
  with the release the vocabulary names (`edge_release`, and the commits in
  `provenance` and `config_schema_document`).
- `summary` describes every contract-visible change between that release and
  `commit`: removed or renamed plugin config keys, changed plugin conditionals,
  the new `openapi.yaml` sha256, and header or error changes. It is for review;
  do not parse it.

A vendored copy holds the delta as of its tag. To read the current delta, fetch
the vocabulary from this repository's `main` at a resolved commit.

The check:

1. Runs on a weekly schedule and on `workflow_dispatch` (GitForgeOps runs it
   from its validator pin canary workflow when dispatched with
   `check: edge-main`), and is never a required check. It uses the consumer's own `GITHUB_TOKEN` and needs no
   cross-repository secret: `contents: read`, plus `issues: write` only on the
   job that files the issue.
2. Resolves Edge `main` to a commit and runs the consumer's compatibility
   checks (the table below) at that commit. A consumer that needs a running
   gateway or the `ferrum-edge` binary uses the `latest` image that Edge's
   `Main Latest Image` workflow publishes: it verifies the image's keyless
   Cosign signature from that workflow, reads the commit from the
   `org.opencontainers.image.revision` label, and requires that commit to be
   on Edge `main`'s history. A consumer that reads only Edge sources resolves
   `refs/heads/main` with `git ls-remote` and fetches those files at that
   commit.
3. Reads `main_branch_delta.commit` from this repository's `main` and
   compares it with the Edge commit under test. When that commit is ahead of
   the delta, the delta may not cover the newest changes yet; the report says
   so. An image-based report also says how many commits the image's revision
   trails the tip of Edge `main`.
4. On a scheduled run or a manual dispatch on the consumer's default branch,
   opens or updates one issue (found by its `<!-- edge-main-drift -->`
   marker) on drift, or when the check itself fails to run, naming the Edge
   commit when it was resolved and the failing checks; it closes the issue
   once such a run passes again. Foundry, Nexus, Alloy and Anvil also run the
   check on pull requests that change it; those runs, and dispatches from
   other branches, file no issue. Their verdict is in the run's step summary
   and log, with annotations where a check emits them (Nexus also uploads
   logs, traces and screenshots as an artifact). Anvil fails such a run on
   drift; the others can finish green while reporting the drift there.

Foundry, Nexus, GitForgeOps, Alloy and Anvil each run this check (ferrum-foundry#716,
ferrum-nexus#733, ferrum-edge-git-forge-ops#737, ferrum-alloy#314,
ferrum-anvil#578).

What each consumer's shipped workflow checks:

| Consumer | Workflow | Check against Edge `main` |
|---|---|---|
| ferrum-foundry | `.github/workflows/edge-main-drift.yml` | `scripts/edge-main-drift.mjs` compares the guided plugin schemas, the plugin sensitivity table and the server-owned subset `traffic_policy` fields with the Edge `main` sources; then, against gateways started from the signed Edge `latest` image, the Alloy preview and explicit HTTP resource mapping check (the preview's resources applied to the test gateway and read back), the seed and backup gateway contract, role and read-only capability parity, and the editors' save payloads |
| ferrum-nexus | `.github/workflows/edge-main-drift.yml` | The real-stack acceptance suite (`./e2e/run.sh`: data plane, single sign-on, browser journey) that its required `acceptance` job runs against the pinned release, with `FERRUM_EDGE_IMAGE` set to the signed Edge `latest` image |
| ferrum-edge-git-forge-ops | `.github/workflows/validator-pin-canary.yml`, job `edge-main-drift` | Resource-label compatibility, `gitforgeops validate` for every environment, and the lifecycle suite (`tests/lifecycle/run.sh`: apply, diff and traffic), all with the `ferrum-edge` binary taken from the signed Edge `latest` image |
| ferrum-alloy | `.github/workflows/edge-main-drift.yml` | The steps of its "Generated Edge configuration validates" CI job, run on the signed Edge `latest` image: `ferrum-edge validate` on the plain-HTTP and minimal generated fixtures, trace-context stripping through the minimal fixture, and `POST /api-specs` importing the exported agent-tool document and generating the expected `mcp_gateway` endpoint, namespace and exact tool set |
| ferrum-anvil | `.github/workflows/edge-main-drift.yml` | Against this repository's `main`: every vendored `PIN` path still exists, the imported error and diagnostic vocabularies, the `DiagnosticFinding` schema and every current `diagnostic-finding` fixture, and the `diagnostic-ref` schema against Anvil's reader, with every current `diagnostic-ref` fixture run through both (`main_branch_delta` is read for the report). Against Edge `main`'s `src/retry.rs`: the `X-Gateway-Error` tokens against Anvil's reader and its `ferrum.token.*` diagnostic keys, and the `ErrorClass` labels against the reader (`edge_main_vocabulary_matches_anvils_reader`) |

A failure is an early warning, not a blocked merge: it leaves time to ship a
compatible consumer release before Edge releases the change.

## Changing the format

This format has no version line. A change that would make a valid `PIN`
invalid is made only with a migration plan in [adoption.md](adoption.md),
because every consumer test would have to change at once. Consumers move to
this format at their next pin/copy/checksum PR, with no flag day. The
per-consumer state is tracked in
[adoption.md](adoption.md#pin-format-convergence).
