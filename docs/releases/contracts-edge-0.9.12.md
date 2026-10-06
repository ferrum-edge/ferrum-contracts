# contracts-edge-0.9.12 release record

**Published on 2026-10-05 at 13:58:38 UTC.** The latest canonical release is
[`contracts-edge-0.9.12`](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.12)
at `31f0a21d707795be293d15837c2f77c3d84219d8`. It refreshes all five Edge
vocabularies and the plugin OpenAPI pin and adds separate deployment snapshot and
mutation acknowledgement schemas at actual released Edge source
`0d917701b63ef38210c49df830f48cf0457cbc7d`. Consumer pins are recorded in
[adoption.md](../adoption.md); 0.9.12 adoption is pending until consumer PRs
merge and qualify.

## Actual canonical publication

[PR #15](https://github.com/ferrum-edge/ferrum-contracts/pull/15) merged at
13:57:00 UTC on 2026-10-05 as `31f0a21d707795be293d15837c2f77c3d84219d8`. Its
first parent is `96228e1cc3341c6bd2dff3c47eea9efa45e0545e`; its exact second
parent is the final reviewed head `d9c84810152732524c54a9ed292dc59103f0619d`,
and the merge tree `1b480bf3e14e33d8a013247d2a30406159b6c04b` equals that head's
tree. The final-head hosted [run 37319873697](https://github.com/ferrum-edge/ferrum-contracts/actions/runs/37319873697)
succeeded. Every actual main PUSH workflow on the merge commit succeeded before
the immutable tag was created: the sole applicable [run 37320780987](https://github.com/ferrum-edge/ferrum-contracts/actions/runs/37320780987)
completed successfully at 13:57:20 UTC.

The unsigned lightweight `contracts-edge-0.9.12` tag points directly to that
merge commit. [GitHub release 403772929](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.12)
was published at 13:58:38 UTC with `draft: false` and `prerelease: false`.
Historical tags and their Edge mappings remain unchanged.

The [immutable tagged source record](https://github.com/ferrum-edge/ferrum-contracts/blob/31f0a21d707795be293d15837c2f77c3d84219d8/docs/releases/contracts-edge-0.9.12.md)
and its `[contracts-edge-0.9.12]` changelog section captured prepared/pending
wording before publication. These bytes are preserved; their prepared status is
not a new approval requirement or a claim that publication remains pending. This
documentation records the subsequent actual publication without changing the
tagged artifacts.

## Actual Edge source and release qualification

The immutable unsigned lightweight `v0.9.12` tag targets
`0d917701b63ef38210c49df830f48cf0457cbc7d`, the protected merge of
[Edge #6013](https://github.com/ferrum-edge/ferrum-edge/pull/6013). Its first
parent is `a9c758c6352765d13a7f61c4d7e3571c82a2d307`; its second parent is
exact reviewed final head `b277bbb1fc20ed7fb5d785165c7ced5650957a89`.
The merged tree equals the reviewed head tree
`5c431da087e7aa67be4851b681341b9843a15ad7`.
All 14 actual main PUSH workflows succeeded before tag creation. The root
qualification record, completed on 2026-10-05 at 12:54:40 UTC, distinguishes
those pre-tag gates from the later Release run.

[GitHub release 403693646](https://github.com/ferrum-edge/ferrum-edge/releases/tag/v0.9.12)
was published on 2026-10-05 at 12:33:02 UTC (`draft: false`, `prerelease: false`).
Actual [Release run 37298358313](https://github.com/ferrum-edge/ferrum-edge/actions/runs/37298358313)
completed successfully at 12:36:32 UTC with all 20 jobs successful, including
GNU ABI checks, strict authenticated image signature/SLSA/SPDX verification and
both final release join gates. Root inspected the actual steps/logs and the
immutable artifact identities; earlier PR checks are not substituted for these
release facts.

Root downloaded all 14 assets and matched bytes, sizes, names and GitHub API
SHA-256 digests, plus the exact binary names/digests in all seven checksum
sidecars. These are published identities, not anticipated values:

| Published asset | SHA-256 |
|---|---|
| `ferrum-cni-linux-aarch64` | `sha256:04e7dba5fdccb11d903002419be93324f81bf4c09ab6a5482741a613604923bb` |
| `ferrum-cni-linux-aarch64.sha256` | `sha256:b0122cbccc1d0e0ed1bde18e042821910fb34ad3c486f1a405f4ac4b830df06e` |
| `ferrum-cni-linux-x86_64` | `sha256:1233690f92cac8ccb39d0978e971fcd70a770090a0ecd0fc698cde00e5bb90d2` |
| `ferrum-cni-linux-x86_64.sha256` | `sha256:7e1565734ab4f87caa294723370d70acb9e313142b8ba3d40016255987e7405e` |
| `ferrum-edge-linux-aarch64` | `sha256:a4a1192d68f5ef1e8c699fa36ce93fd912110a248ab349dc301d0d66eadb1588` |
| `ferrum-edge-linux-aarch64.sha256` | `sha256:452cdbf0cd1f920d4161ffd2fb86d3925bd2da76e432014b2a320cfb11ec7882` |
| `ferrum-edge-linux-x86_64` | `sha256:1453b6ff9ae8bcea983adb7cc120ef2b78c3b292e0adb8e81233222ae4d46ce8` |
| `ferrum-edge-linux-x86_64.sha256` | `sha256:57232a1514bc9750774198792531107e946dff69220792bbceca534f25c579a8` |
| `ferrum-edge-macos-aarch64` | `sha256:8ca3e4ed5e28507c5440cd52cae4c29a7fe339104f9f3024b400b3ff58ddaba8` |
| `ferrum-edge-macos-aarch64.sha256` | `sha256:8862c48fc8b07b6fddca9d5d416ea9b0ac58fc1b6966bfbcd47df102f4ed0a7c` |
| `ferrum-edge-macos-x86_64` | `sha256:61770188a10457225482b3df162528d45a646f88e45b468451a9e59d183edd27` |
| `ferrum-edge-macos-x86_64.sha256` | `sha256:b10b1119e8b9ad3c5981397f122fb9bf30e1c5a0bfcdf590e4118a61745809c3` |
| `ferrum-edge-windows-x86_64.exe` | `sha256:c92d5f4dbf8cc014b062c1420cf3deda4e75874b3649262464228086f790e660` |
| `ferrum-edge-windows-x86_64.exe.sha256` | `sha256:800b622fa1a82d168a4f280ff45071ce697814230536fad3aaf31e190a1b0a65` |

Root anonymously verified raw Docker Hub index bytes against registry headers,
all six platform manifests and their config bytes against descriptor hashes,
and gateway/CNI layer bytes in the default image against the exact release
assets on both amd64 and arm64. No binary or container ran locally.

| Docker Hub image | Index digest | amd64 manifest | arm64 manifest |
|---|---|---|---|
| `docker.io/ferrumedge/ferrum-edge:v0.9.12` | `sha256:80526b59cbbdc2bfcc8bae9241da4e5395414cf07bf0be4effd4c73c51684ee4` | `sha256:96fda718b2d078090b16ebe06d02bec0b942ca5b8632bb78f5076221db3b6cb6` | `sha256:0d3bbf1fb471347711a188b50fdcfe0df444fc7be32256cb9ec6807f338742af` |
| `docker.io/ferrumedge/ferrum-edge:v0.9.12-ebpf` | `sha256:bc8e36fadc1e10bd858cccee40c5577d98591118b5e07c5f03c98bc02f02476a` | `sha256:58932b5869940bb74bf2d54382359af2e86417f59c1fb6bda9ddbd87bb752e68` | `sha256:1c989d85a841fbc46dfc8db3556363f2d352b8d5219a82f7e2b503debed40df1` |
| `docker.io/ferrumedge/ferrum-edge:v0.9.12-ebpf-tools` | `sha256:78df368075e38f4e37823debc200b72381153ec5dfdc0aa10782eaaa41519725` | `sha256:c76492a793e440c43c74f6844b5b5b5926ee2c5010c2e052b967d3796c591202` | `sha256:9fd7295669c4853cfba9f114ee3fc16c09d2d69e85319ce43837b2f4636af81c` |

[Hosted signing/attestation job 111763558319](https://github.com/ferrum-edge/ferrum-edge/actions/runs/37298358313/job/111763558319)
verified Docker Hub/authenticated GHCR platform parity, exact workflow identity,
repository, ref, push event, source commit and SLSA subjects, plus signatures
and signed per-platform SPDX SBOMs. This is hosted cryptographic verification;
root's independent checks cover metadata, downloaded bytes and identities.
Anonymous GHCR returns 401 and remains warn-only. Published configs lack an
image revision label; exact default gateway/CNI binary pairing supplies byte
identity without inventing that label or anonymous GHCR access. ABI qualification
is the actual hosted build/ABI/join gates, not local execution or a broader
consumer platform claim.

All actual pre-tag PUSH successes are recorded by their workflow identities:

| Workflow | Exact merge-commit run |
|---|---|
| NodeWaypoint eBPF Live Datapath | [37291682628](https://github.com/ferrum-edge/ferrum-edge/actions/runs/37291682628) |
| CNI Install Lifecycle Live | [37291682670](https://github.com/ferrum-edge/ferrum-edge/actions/runs/37291682670) |
| Multicluster Poller Partition Live | [37291682657](https://github.com/ferrum-edge/ferrum-edge/actions/runs/37291682657) |
| FIPS Build Policy | [37291682496](https://github.com/ferrum-edge/ferrum-edge/actions/runs/37291682496) |
| Ambient Host UDP Live Kernel | [37291682514](https://github.com/ferrum-edge/ferrum-edge/actions/runs/37291682514) |
| Coverage | [37291682474](https://github.com/ferrum-edge/ferrum-edge/actions/runs/37291682474) |
| CI | [37291682404](https://github.com/ferrum-edge/ferrum-edge/actions/runs/37291682404) |
| Gateway API Conformance | [37291682590](https://github.com/ferrum-edge/ferrum-edge/actions/runs/37291682590) |
| Istio Status CAS Live | [37291682497](https://github.com/ferrum-edge/ferrum-edge/actions/runs/37291682497) |
| H2 Guard Observation | [37291682435](https://github.com/ferrum-edge/ferrum-edge/actions/runs/37291682435) |
| Mesh E2E Sidecar Live Datapath | [37291682560](https://github.com/ferrum-edge/ferrum-edge/actions/runs/37291682560) |
| Multicluster Federation Live Datapath | [37291682468](https://github.com/ferrum-edge/ferrum-edge/actions/runs/37291682468) |
| Benchmark Harness Tests | [37291682563](https://github.com/ferrum-edge/ferrum-edge/actions/runs/37291682563) |
| Mesh Benchmark Lockfile | [37291682485](https://github.com/ferrum-edge/ferrum-edge/actions/runs/37291682485) |

## Published release contents

- Add `admin-deployment-snapshot` and
  `admin-deployment-mutation-acknowledgement` v1 schemas from the actual owner
  OpenAPI and runtime invariants, with source-transcribed empty SQL/MongoDB
  snapshots, durable/live/refusal acknowledgement fixtures and exact single-change
  invalid path/keyword expectations. Preserve the original conditional backup
  namespace/row contract and every historical valid fixture.
- Document complete secret-bearing raw/spec/external-reference authority, the
  strict original deployment token and the two dependency-fenced partial writes,
  and explicit body-based cleanup authorization. CP/unserved HTTP 200 remains
  cleanup false; uncertainty/refusal never authorizes replay or token refresh.
  See [deployment-contracts.md](../deployment-contracts.md).
- Refresh all five Edge vocabularies, catalog integrity/source pins and Edge-owned
  schema provenance at `0d917701b63ef38210c49df830f48cf0457cbc7d`.
  `openapi.yaml` SHA-256 is
  `f7242228d73d34ad2d7da3c989ec6ba15bb6ae1f2f4c94a8e0a181b000caae77`.
  Error tokens/classes, provisioning values, plugin registrations/lifecycle
  metadata, diagnostic-ref wire fields and egress classifier are unchanged from
  the previous owner pin. The plugin catalog retains all 82 exact config pointers
  into the newly pinned file; hosted validation must check their resolution.
- Preserve historical first availability and other-owner provenance/unreleased
  annotations, including the accepted Alloy shared v1 freeze at
  `81cbb410d34ff5fba1f3d54cfd2e7ebccaed397e`. This Edge release does not publish
  Alloy or promote another owner's default-branch feature. No obsolete
  `main_branch_delta` exists in the refreshed vocabulary files.
- Record actual Edge and Contracts publication separately from pending consumer
  adoption. Unfinished Edge #6011 rejection-contract work is absent from this
  release; no new HTTP capacity/native rejection semantics or tokens are added.
  Pending publisher profiles, Nexus Part B and advisory qualification remain
  pending.

The snapshot schema deliberately follows the open owner envelope. Nested raw
SQL/BSON/spec identity is not an owner-exported standalone schema, and the
fixtures do not capture populated secret-bearing HTTP responses. Runtime
completeness, cryptographic preconditions, audit, lease and live application
require the owner implementation. Consumer DTO acceptance is not inferred.
The existing hosted validator discovers the new schemas and fixtures without
exceptions; validator code, workflows, action pins, dependencies and permissions
are unchanged. Static inspection and `git diff --check` do not establish hosted
conformance.

## Completed finalization and pending adoption

1. Final canonical review, fresh independent review and Edge maintainer/code-owner
   approval completed for the changed contracts. The exact final reviewed head
   `d9c84810152732524c54a9ed292dc59103f0619d` passed hosted [run 37319873697](https://github.com/ferrum-edge/ferrum-contracts/actions/runs/37319873697),
   including every schema, fixture, vocabulary and pinned plugin OpenAPI pointer.
   No changed head inherited a prior success.
2. [PR #15](https://github.com/ferrum-edge/ferrum-contracts/pull/15) merged
   through the protected canonical path using a normal merge commit whose second
   parent equals that exact reviewed final head and whose tree matches it.
   Historical tags and releases are preserved.
3. The actual merge target `31f0a21d707795be293d15837c2f77c3d84219d8` and every
   applicable main PUSH workflow succeeded before tag creation; the sole
   applicable [run 37320780987](https://github.com/ferrum-edge/ferrum-contracts/actions/runs/37320780987)
   completed successfully. Earlier PR-head checks were not substituted for
   merge-commit qualification.
4. Root created the immutable unsigned lightweight `contracts-edge-0.9.12` tag
   at that qualified merge commit and published
   [release 403772929](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.12)
   at 13:58:38 UTC on 2026-10-05.
5. Consumer adoption remains pending. Coordinate consumer pin/checksum/copy
   adoption in Nexus #522, Foundry #544, GitForgeOps and other consumers, with
   original evidence, explicit acknowledgements, their own supported-profile
   decisions and hosted integration/packaged/four-store qualification as
   applicable. Record each adoption slice only after its PR merges and qualifies.
   No advisory completion or production apply qualification is delivered here.

The qualified Edge prerequisite does not approve pending consumer profiles. Root
owns profile decisions and advisory disposition. Local repository execution is
prohibited; static source/diff inspection and integrity hashing do not establish
hosted validation. This subsequent documentation update needs its own hosted
contracts gate and root review before landing.
