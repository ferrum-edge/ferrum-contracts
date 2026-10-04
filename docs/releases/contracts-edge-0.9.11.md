# contracts-edge-0.9.11 release record

2026-10-04 finalized inputs and prepared release contents. **PR #13 remains DRAFT;
canonical merge, tag and publication are pending.** Root has accepted the unchanged
shared Alloy v1 freeze in this candidate after reviewed owner/consumer qualification.
The latest published canonical release remains `contracts-edge-0.9.9-r2` at
`591c73a3f965fdab440c3a76b2707accdf491ba5`. Consumer pins remain as recorded
in [adoption.md](../adoption.md).

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
Linux GNU ABI and image-attestation release gates. Root verified actual downloaded
bytes for all 14 assets against GitHub API digests and all seven binary checksum
files. These are verified identities, not anticipated publication values:

| Published asset | SHA-256 |
|---|---|
| `ferrum-cni-linux-aarch64` | `sha256:c54b68605132a42eab941ce43d595cca878f3be79e8ae1ecda5cf05dd6450b8a` |
| `ferrum-cni-linux-aarch64.sha256` | `sha256:74273e45022ef49da473a56e2b81a208c06761ba66862dd9665b3e0c4642e019` |
| `ferrum-cni-linux-x86_64` | `sha256:d70b1a273eaf4d5e30d07ef41a07764f13cd9fe4274d9348b4b710172fc1a7ef` |
| `ferrum-cni-linux-x86_64.sha256` | `sha256:a7a3f44fb588b13e76643689336f8752d3b961a72c73c69b4b59121259d0b957` |
| `ferrum-edge-linux-aarch64` | `sha256:3f0c4a7334878963792c8c277f49f8b91af24bf2db59996e41ec3f7e41c7fbac` |
| `ferrum-edge-linux-aarch64.sha256` | `sha256:a2ea8f963d4d51fa446cd4642f0f0e68c84e1cd35b6a22724784e39c830b3eea` |
| `ferrum-edge-linux-x86_64` | `sha256:97cbd7cd277feee8f661e9d2cd97a6383be969fd2fc2b61143601614922f988f` |
| `ferrum-edge-linux-x86_64.sha256` | `sha256:e5ed7a4501dbd43a4832307eb80bb2aed0cd2dda1695e39665d1684f87553a2d` |
| `ferrum-edge-macos-aarch64` | `sha256:d9a535fda68f17c67e7a44de4c6c0d037145d8772067c7051fa9bd47a30e12ea` |
| `ferrum-edge-macos-aarch64.sha256` | `sha256:18fe8d150440edcce0833c77d002f2eff2b5c053a125671744c8262fcc6a30a4` |
| `ferrum-edge-macos-x86_64` | `sha256:83a59079dd5661af431c8dcacbc1139c6e3963f9a755e6f13b8e93b1570f59c8` |
| `ferrum-edge-macos-x86_64.sha256` | `sha256:3f0da056d146e57b78a2c4a2710ebd1e26a2933d2e68fbe684842fa0442bd325` |
| `ferrum-edge-windows-x86_64.exe` | `sha256:9bc7c9240fa0898a9efeb6e2dabb74c696772af0bb0ba2f7e57ab70c3d0a86e9` |
| `ferrum-edge-windows-x86_64.exe.sha256` | `sha256:456da9bd756e160d2a1b17d2af9fc50213b7715110c48be9589f2616c5ebbc83` |

Root anonymously read and hashed all three Docker Hub indexes and all six
amd64/arm64 platform manifests and config pairs. Default-image gateway and CNI
layer bytes match the corresponding release assets on both architectures.

| Docker Hub image | Index digest | amd64 manifest | arm64 manifest |
|---|---|---|---|
| `docker.io/ferrumedge/ferrum-edge:v0.9.11` | `sha256:2476b502855940e28157858fc24008545cb3baeb3084c9610e1d4505cbe0d36e` | `sha256:7287d297e8f305c99143e148f910024e50fac0341e7fd89236325331fe405b22` | `sha256:738a68e81da5cc9c0dde8e8ed5ba9e9c6957fcbdd930070d60d8782c303bb9eb` |
| `docker.io/ferrumedge/ferrum-edge:v0.9.11-ebpf` | `sha256:3d4f5aedddca2fcb8ce4c24409201203ffbfb79779b37f0a1853e10944eef5b0` | `sha256:cc50378837fda0e1ceaaf29ea4c339dd00b6aa5f3f05881c667672fff794eb31` | `sha256:00e23af6398e6766816a18217da892f7a7a798035b27ed186ff03d8eb570ad71` |
| `docker.io/ferrumedge/ferrum-edge:v0.9.11-ebpf-tools` | `sha256:681d6d8b0ae7a00921a4899a8f0c5059225f0eeef1bf17bb13da10ebd4719aea` | `sha256:7496eeec1b3e6762b35ad4188cd0ff15dd8008f4457f4696db013549ae6b8697` | `sha256:f74f4eae5e647e23b51bf6a19bd332ab4ae6227a429fe56ef22efc6affc1eee3` |

[Hosted signing/attestation job 111535236475](https://github.com/ferrum-edge/ferrum-edge/actions/runs/37229572280/job/111535236475)
verified Docker Hub/GHCR image identity parity, signatures, strict SLSA commit
and subject identity, and signed per-platform SBOMs. GHCR remains private;
the existing anonymous GHCR smoke is warn-only. Published Edge configs have
no image revision label. Default-image binary pairing supplies exact byte
identity; downstream image revision checks remain separate product requirements.
Nothing was executed locally for this distribution inspection.

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
is present at that qualified owner. Root now accepts its coordinated freeze of
the current unchanged `ferrum.diagnostic_report` v1 and `ferrum.service_manifest`
v1 after reviewed owner/consumer qualification. This is root's authorized
canonical metadata decision, not a claim of prior separate human approval or
separate Alloy crate publishing approval. Both shared contracts are marked
**EXISTING** with `x-contract.status: implemented` in this release candidate;
Alloy remains unpublished and provenance retains `availability: unreleased`.
The `coordinated_release` annotation records the decision and pending canonical
publication, replacing the obsolete pending-owner `freeze_candidate` proposal.

Every v1 wire field, bound, fixture and unknown-reader rule is preserved.
Full diagnostic-report pairing with 81cbb includes every description outside
`$id`/`x-contract`. Historical PROPOSED wording in the copied owner descriptions
remains paired; `x-contract` and this record carry the current shared status.
The manifest remains a transcription of owner serde structs and validation,
not an owner-exported schema. Owner post-default validation includes derived
resource ID lengths and endpoint relationships not all asserted by this schema.
Consumer presentation bounds do not redefine producer validation.
Historical r2 schema/fixture/provenance bytes remain unchanged. After canonical
publication, Alloy's owner pin/local annotations and consumer copies move
together with full hosted parity; no downstream adoption has happened here.

The [consumer ledger](../adoption.md#immutable-hosted-qualification) binds the
following slices, without claiming arbitrary newer sources are qualified:

| Consumer | Qualified PR head | Inspected main | Boundary |
|---|---|---|---|
| Anvil #312 | `591cb7343dc2cac3a3b540cdc7ba4dd7f2826c0d` | `c19c0a6abba896bfec972b3e083179c55ef8e38c` | Bounded read-only diagnostic import, unverified/unknown preview; canonical fixtures and a real pinned Alloy exporter golden |
| Foundry #540 | `ea322e9f584885c09e59fcbbbe255148754b476c` | `f7eaa96605e2183cec664eccbfee600f46e35f72` | Authenticated namespace-authorized redacted manifest preview, strict shared fixtures, HTTP gateway admission and accepted presentation ADR; no production apply or trace store |
| Nexus #519 | `77fdb767ec8ef04e88f13df9fb291bc77fbd0344` | `559c350a5370335791cdc3082225dce6056cf547` | Strict shared-fixture manifest preview, authentication/CSRF/namespace/redaction and packaged acceptance; no publication/apply/diagnostic import |
| GitForgeOps #461 | `e06f986dfeabb9bcb0c546c74b646f01e1c2a932` | `76d76c796cafbaea9556e992381b6e2518ae4f69` | Two actual pinned Alloy-generated resource trees through its strict loader/assembler/validator; no direct manifest JSON adoption or production apply |

## Prepared release notes

- Refresh the four existing Edge vocabularies and plugin OpenAPI integrity pin
  from published `v0.9.11` source, preserving existing vocabulary values and
  historical first availability.
- Add Edge-owned conditional backup metadata and backend egress policy response
  schemas, the egress vocabulary/shape, sanitized positive fixtures and precise
  single-mutation negative expectations for Edge #5992/#5994.
- Record standard HTTP admin `ETag`/`If-Match` semantics, credential-complete
  authoritative verification, coherent namespace snapshot/replacement, and
  process/DP scope limits in [admin-contracts.md](../admin-contracts.md).
- Finalize report and manifest shared v1 as EXISTING/implemented in the candidate
  at qualified Alloy owner 81cbb, with root's accepted unchanged-wire freeze and
  owner-unreleased availability. Preserve full report pairing and manifest
  transcription limits; grant no separate crate publishing permission.
- Record verified Edge distribution, qualified immutable owner/consumer slices,
  unchanged historical r2 pins and the remaining canonical publication/adoption
  gates. Workflow, permissions, dependencies and validator behavior are unchanged.

Canonical metadata does not patch a product advisory or qualify production apply,
performance, or arbitrary newer consumer sources. Read-only, redaction and
unknown-authority limits remain those of the qualified slices above.

## Root finalization and publication order

1. Edge distribution qualification is complete for the exact immutable tag:
   published assets/digests, image identities/binary pairing, hosted attestations
   and ABI gates are recorded above. Keep GHCR access and image-label limits exact.
2. Alloy owner qualification and root's shared v1 metadata decision are complete
   for exact `81cbb410d34ff5fba1f3d54cfd2e7ebccaed397e`. Its ordinary owner
   squash is qualified by immutable source pairing, root/fresh owner review and
   every applicable main PUSH success; it is not a release/tag target and needs
   no approved second parent. Retain paired descriptions and owner-unreleased
   availability; earlier green runs never qualify a changed owner SHA.
3. Review the final canonical head and fixtures with root/fresh review and the
   owning maintainers; require hosted `Schemas, fixtures and vocabularies` success
   at that exact head. PR #13 stays draft pending these gates. Prior whole 45-file
   review, fresh review 3 and all 116 hosted validations at candidate
   `26a2797f15286da8e32002c4971b68013e134be9` are historical evidence only.
4. Root merges the approved canonical PR with a **merge commit whose second parent
   equals the exact final reviewed PR head**. Verify that target, the unique
   associated PR and all applicable main PUSH workflow successes, then publish
   the immutable `contracts-edge-0.9.11` tag and release notes. The release section
   is prepared in `CHANGELOG.md`; unrelated `[Unreleased]` work and every historical
   released section/tag are retained. No tag is moved or rewritten.
5. Only after canonical tag publication, coordinate consumer pin/checksum/local
   copy updates and Alloy's matching local annotations/descriptions in their own
   repositories with full hosted parity. Record adoption after those PRs qualify.
   Root owns issue disposition and any separate crate publishing permission.

Local repository execution is prohibited. Static source/diff inspection and
integrity hashing do not establish hosted validation. This new candidate SHA
requires its own hosted contracts gate and root/fresh review before landing.
