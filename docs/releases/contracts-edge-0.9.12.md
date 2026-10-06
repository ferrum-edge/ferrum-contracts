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

Edge's published assets and checksums, multi-arch image digests, and hosted
signature/SLSA/SBOM facts are Edge release facts. They are recorded in the
[Edge v0.9.12 GitHub release](https://github.com/ferrum-edge/ferrum-edge/releases/tag/v0.9.12)
and the Edge release record
[`docs/releases/v0.9.12.md`](https://github.com/ferrum-edge/ferrum-edge/blob/v0.9.12/docs/releases/v0.9.12.md);
this repository does not restate the digests.

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
