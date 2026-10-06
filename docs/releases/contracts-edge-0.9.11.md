# contracts-edge-0.9.11 release record

**Published on 2026-10-04 at 22:41:21 UTC.** The latest canonical release is
[`contracts-edge-0.9.11`](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.11)
at `390edbd5b2485af0988e02f7827fde778d76ae0a`. It includes root's accepted
unchanged shared Alloy v1 freeze after reviewed owner/consumer qualification.
Alloy remains unpublished with no separate crate publishing approval. Consumer
pins remain as recorded in [adoption.md](../adoption.md); 0.9.11 adoption is
pending until consumer PRs merge and qualify.

## Actual canonical publication

[PR #13](https://github.com/ferrum-edge/ferrum-contracts/pull/13) merged at
22:40:08 UTC on 2026-10-04 as `390edbd5b2485af0988e02f7827fde778d76ae0a`.
Its first parent is `d098c81a50f1baaa8c081d511868c74e957ddf43`; its exact
second parent is the final reviewed head `0cf926686f2164ad0b4de7b27e2eb5a25df6a261`.
Root reviewed the complete change and fresh independent final-delta review
reported no findings. The final-head [hosted run 37240041628](https://github.com/ferrum-edge/ferrum-contracts/actions/runs/37240041628)
succeeded with all 116 validation cases passing. Every actual main PUSH workflow
on the merge commit succeeded before the immutable tag was created: the sole
applicable [run 37240886730](https://github.com/ferrum-edge/ferrum-contracts/actions/runs/37240886730)
and required [Schemas, fixtures and vocabularies job 111549212572](https://github.com/ferrum-edge/ferrum-contracts/actions/runs/37240886730/job/111549212572)
completed successfully by 22:40:26 UTC.

The unsigned lightweight `contracts-edge-0.9.11` tag points directly to that
merge commit. [GitHub release 403239814](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.11)
was published at 22:41:21 UTC with `draft: false` and `prerelease: false`.
Historical tags and their Edge mappings remain unchanged.

The [immutable tagged source record](https://github.com/ferrum-edge/ferrum-contracts/blob/390edbd5b2485af0988e02f7827fde778d76ae0a/docs/releases/contracts-edge-0.9.11.md)
and its released changelog section captured prepared/draft/pending wording before
publication. Schema descriptions, `shared_status`, `coordinated_release` and
`edge_availability` annotations also retain that historical wording. These bytes
are preserved; their prepared status is not a new approval requirement or a
claim that publication remains pending. This documentation records the subsequent
actual publication without changing the tagged artifacts or qualification slices.

## Edge source and verified distribution

Edge's actual immutable unsigned lightweight `v0.9.11` tag was created at
19:46:47 UTC at `c764084b3b51c3f7ffde268c039688d35e49c553`, the merge of
[#6005](https://github.com/ferrum-edge/ferrum-edge/pull/6005). Its parents are
`3ce21ad101f164f70cb7f7f77fb033db828b9518` and the qualified PR head
`ff0a9d5152dc3cf2fd240158cbdf5551f511212e`.
Root recorded all 14 pre-tag main PUSH workflows successful and all nine
publication contexts from GitHub Actions app 15368, including trusted cross-PR
qualification of that exact second parent.

[Release 403215981](https://github.com/ferrum-edge/ferrum-edge/releases/tag/v0.9.11)
was published at 21:26:11 UTC. [Release run 37229572280](https://github.com/ferrum-edge/ferrum-edge/actions/runs/37229572280)
completed successfully at 21:30:12 UTC; all 20 jobs succeeded, including the
Linux GNU ABI and image-attestation release gates. Edge's published assets and
checksums, multi-arch image digests, and hosted signature/SLSA/SBOM facts are
Edge release facts, recorded in the
[Edge v0.9.11 GitHub release](https://github.com/ferrum-edge/ferrum-edge/releases/tag/v0.9.11)
and the Edge release record
[`docs/releases/v0.9.11.md`](https://github.com/ferrum-edge/ferrum-edge/blob/v0.9.11/docs/releases/v0.9.11.md);
this repository does not restate the digests.

The four refreshed Edge vocabularies and new admin artifacts read owner sources
at the tag commit, with plugin OpenAPI SHA-256
`687db80271512a367814ded6002ecce546eb190a347a57e32eca36af7d665020`.
Compared with r2's Edge v0.9.9 source
`234717ce41965cd1e2b5c6c761a25475c5d7628c`, error tokens/classes,
provisioning values, plugin registrations and lifecycle metadata are unchanged.
The previous vocabulary files contain no `main_branch_delta` to remove;
existing first-availability and historical companion observations are retained.

## Final Alloy owner and accepted shared v1 freeze

Final owner source is immutable main
`81cbb410d34ff5fba1f3d54cfd2e7ebccaed397e`, the ordinary squash of reviewed
[Alloy #144](https://github.com/ferrum-edge/ferrum-alloy/pull/144), final head
`c99be521b72c2ef46d25024bb39e682cd49fdf38`, merged at 22:03:34 UTC.
All 18 main check runs and all 18 jobs in the sole applicable main PUSH
[CI 37238543236](https://github.com/ferrum-edge/ferrum-alloy/actions/runs/37238543236)
completed successfully. Root read back the exact main SHA, reviewed the full
owner chain/new delta, and fresh independent review 4 reported no findings.
Successful older heads are not substituted for this final owner qualification.

| Immutable Alloy owner source | SHA-256 |
|---|---|
| [`contracts/diagnostics/diagnostic-report.v1.schema.json`](https://github.com/ferrum-edge/ferrum-alloy/blob/81cbb410d34ff5fba1f3d54cfd2e7ebccaed397e/contracts/diagnostics/diagnostic-report.v1.schema.json) | `88d880f0f3a1c9f6e2b7a1a2f9962cf517831714903577e9876baa9ce8d87979` |
| [`crates/ferrum-alloy-edge/src/manifest.rs`](https://github.com/ferrum-edge/ferrum-alloy/blob/81cbb410d34ff5fba1f3d54cfd2e7ebccaed397e/crates/ferrum-alloy-edge/src/manifest.rs) | `05d42db07c1e91a892aa3bee9194decb273dce4fcac1ce4e85b951cc3abfb250` |

The [owner qualification proposal](https://github.com/ferrum-edge/ferrum-alloy/blob/81cbb410d34ff5fba1f3d54cfd2e7ebccaed397e/docs/shared-contract-qualification.md)
is present at that qualified owner. Root accepted its coordinated freeze of
the current unchanged `ferrum.diagnostic_report` v1 and `ferrum.service_manifest`
v1 after reviewed owner/consumer qualification. This is root's authorized
canonical metadata decision, not a claim of prior separate human approval or
separate Alloy crate publishing approval. Both shared contracts are marked
**EXISTING** with `x-contract.status: implemented` in the published release;
Alloy remains unpublished and provenance retains `availability: unreleased`.
The `coordinated_release` annotation records the accepted decision and the
historical pre-publication state, replacing the obsolete pending-owner
`freeze_candidate` proposal. Actual canonical publication is recorded above.

Every v1 wire field, bound, fixture and unknown-reader rule is preserved.
Full diagnostic-report pairing with 81cbb includes every description outside
`$id`/`x-contract`. Historical PROPOSED wording in the copied owner descriptions
remains paired; `x-contract` and this record carry the current shared status.
The manifest remains a transcription of owner serde structs and validation,
not an owner-exported schema. Owner post-default validation includes derived
resource ID lengths and endpoint relationships not all asserted by this schema.
Consumer presentation bounds do not redefine producer validation.
Historical r2 schema/fixture/provenance bytes remain unchanged. Alloy's owner
pin/local annotations and consumer copies still need coordinated adoption PRs
with full hosted parity after publication; no downstream adoption is recorded here.

The [consumer ledger](../adoption.md#immutable-hosted-qualification) binds the
following slices, without claiming arbitrary newer sources are qualified:

| Consumer | Qualified PR head | Inspected main | Boundary |
|---|---|---|---|
| Anvil #312 | `591cb7343dc2cac3a3b540cdc7ba4dd7f2826c0d` | `c19c0a6abba896bfec972b3e083179c55ef8e38c` | Bounded read-only diagnostic import, unverified/unknown preview; canonical fixtures and a real pinned Alloy exporter golden |
| Foundry #540 | `ea322e9f584885c09e59fcbbbe255148754b476c` | `f7eaa96605e2183cec664eccbfee600f46e35f72` | Authenticated namespace-authorized redacted manifest preview, strict shared fixtures, HTTP gateway admission and accepted presentation ADR; no production apply or trace store |
| Nexus #519 | `77fdb767ec8ef04e88f13df9fb291bc77fbd0344` | `559c350a5370335791cdc3082225dce6056cf547` | Strict shared-fixture manifest preview, authentication/CSRF/namespace/redaction and packaged acceptance; no publication/apply/diagnostic import |
| GitForgeOps #461 | `e06f986dfeabb9bcb0c546c74b646f01e1c2a932` | `76d76c796cafbaea9556e992381b6e2518ae4f69` | Two actual pinned Alloy-generated resource trees through its strict loader/assembler/validator; no direct manifest JSON adoption or production apply |

## Published release contents

- Refresh the four existing Edge vocabularies and plugin OpenAPI integrity pin
  from published `v0.9.11` source, preserving existing vocabulary values and
  historical first availability.
- Add Edge-owned conditional backup metadata and backend egress policy response
  schemas, the egress vocabulary/shape, sanitized positive fixtures and precise
  single-mutation negative expectations for Edge #5992/#5994.
- Record standard HTTP admin `ETag`/`If-Match` semantics, credential-complete
  authoritative verification, coherent namespace snapshot/replacement, and
  process/DP scope limits in [admin-contracts.md](../admin-contracts.md).
- Finalize report and manifest shared v1 as EXISTING/implemented in the release
  at qualified Alloy owner 81cbb, with root's accepted unchanged-wire freeze and
  owner-unreleased availability. Preserve full report pairing and manifest
  transcription limits; grant no separate crate publishing permission.
- Record verified Edge distribution, qualified immutable owner/consumer slices,
  unchanged historical r2 pins, completed canonical publication and pending
  adoption. Workflow, permissions, dependencies and validator behavior are unchanged.

Canonical metadata does not patch a product advisory or qualify production apply,
performance, or arbitrary newer consumer sources. Read-only, redaction and
unknown-authority limits remain those of the qualified slices above.

## Completed finalization and pending adoption

1. Edge distribution qualification is complete for the exact immutable tag:
   published assets/digests, image identities/binary pairing, hosted attestations
   and ABI gates are recorded above. Keep GHCR access and image-label limits exact.
2. Alloy owner qualification and root's shared v1 metadata decision are complete
   for exact `81cbb410d34ff5fba1f3d54cfd2e7ebccaed397e`. Its ordinary owner
   squash is qualified by immutable source pairing, root/fresh owner review and
   every applicable main PUSH success; it is not a release/tag target and needs
   no approved second parent. Retain paired descriptions and owner-unreleased
   availability; earlier green runs never qualify a changed owner SHA.
3. Final canonical review and hosted validation completed at exact reviewed head
   `0cf926686f2164ad0b4de7b27e2eb5a25df6a261`, as recorded above. Prior whole
   45-file review, fresh review 3 and all 116 hosted validations at candidate
   `26a2797f15286da8e32002c4971b68013e134be9` remain historical evidence only;
   they were not substituted for final-head qualification.
4. Root merged PR #13 with the exact reviewed second parent, verified the target
   and all actual main PUSH successes, then published the immutable tag and
   release 403239814. The prepared release section in `CHANGELOG.md` and every
   historical released section/tag remain intact. No tag is moved or rewritten.
5. Consumer adoption remains pending. Coordinate consumer pin/checksum/local
   copy updates and Alloy's matching local annotations/descriptions in their own
   repositories with full hosted parity. Record adoption after those PRs merge
   and qualify, without extending the historical qualification slices above.
   Root owns issue disposition and any separate crate publishing permission.

Local repository execution is prohibited. Static source/diff inspection and
integrity hashing do not establish hosted validation. The publication runs above
qualify their exact immutable commits. This subsequent documentation update needs
its own hosted contracts gate and root review before landing.
