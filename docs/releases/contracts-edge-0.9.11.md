# contracts-edge-0.9.11 release candidate

2026-10-04 input snapshot. **DRAFT; not merged, tagged, frozen or published.**
The latest published canonical release remains `contracts-edge-0.9.9-r2` at
`591c73a3f965fdab440c3a76b2707accdf491ba5`. Consumer pins remain as recorded
in [adoption.md](../adoption.md).

## Source and qualification record

Edge's actual immutable unsigned lightweight `v0.9.11` tag was created at
19:46:47 UTC at `c764084b3b51c3f7ffde268c039688d35e49c553`, the merge of
[#6005](https://github.com/ferrum-edge/ferrum-edge/pull/6005). Its parents are
`3ce21ad101f164f70cb7f7f77fb033db828b9518` and the qualified PR head
`ff0a9d5152dc3cf2fd240158cbdf5551f511212e`.
Root recorded all 14 main PUSH workflows successful and all nine publication
contexts from GitHub Actions app 15368, including trusted cross-PR qualification
of that exact second parent. This is tag/source qualification, not proof that
assets were published.

At handoff, [Release run 37229572280](https://github.com/ferrum-edge/ferrum-edge/actions/runs/37229572280)
was still in progress. Root has not supplied verified published release/assets,
digests, attestations or ABI evidence for this candidate. Canonical merge and
publication remain blocked on those actual upstream facts. No patched product
release, new consumer pin or crate publishing approval is asserted here.

The four refreshed Edge vocabularies and new admin artifacts read owner sources
at the tag commit, with plugin OpenAPI SHA-256
`687db80271512a367814ded6002ecce546eb190a347a57e32eca36af7d665020`.
Compared with r2's Edge v0.9.9 source
`234717ce41965cd1e2b5c6c761a25475c5d7628c`, error tokens/classes,
provisioning values, plugin registrations and lifecycle metadata are unchanged.
The previous vocabulary files contain no `main_branch_delta` to remove;
existing first-availability and historical companion observations are retained.

Alloy owner source was read at `d7ddb3688e058ec3cc2e17d166a801aa0037b5b1`,
qualified by all 18 main checks in its sole
[PUSH run 37218434984](https://github.com/ferrum-edge/ferrum-alloy/actions/runs/37218434984).
The owner [freeze proposal](https://github.com/ferrum-edge/ferrum-alloy/blob/725914bee883b3a6248ee68bafec3040b1fa35d0/docs/shared-contract-qualification.md)
at `725914bee883b3a6248ee68bafec3040b1fa35d0` passed all 19 proposal checks
and root's whole-scope/fresh review 7, but was not merged at handoff. It is
proposal evidence, not the final matched owner provenance or an approved freeze.
The separate diagnostic round 13 is outside producer wire/schema/pin scope.
Root must supply the exact final qualified owner merge SHA before canonical merge.

The [consumer ledger](../adoption.md#immutable-hosted-qualification) binds the
following slices, without claiming arbitrary newer sources are qualified:

| Consumer | Qualified PR head | Inspected main | Boundary |
|---|---|---|---|
| Anvil #312 | `591cb7343dc2cac3a3b540cdc7ba4dd7f2826c0d` | `c19c0a6abba896bfec972b3e083179c55ef8e38c` | Bounded read-only diagnostic import, unverified/unknown preview; canonical fixtures and a real pinned Alloy exporter golden |
| Foundry #540 | `ea322e9f584885c09e59fcbbbe255148754b476c` | `f7eaa96605e2183cec664eccbfee600f46e35f72` | Authenticated namespace-authorized redacted manifest preview, strict shared fixtures, HTTP gateway admission and accepted presentation ADR; no production apply or trace store |
| Nexus #519 | `77fdb767ec8ef04e88f13df9fb291bc77fbd0344` | `559c350a5370335791cdc3082225dce6056cf547` | Strict shared-fixture manifest preview, authentication/CSRF/namespace/redaction and packaged acceptance; no publication/apply/diagnostic import |
| GitForgeOps #461 | `e06f986dfeabb9bcb0c546c74b646f01e1c2a932` | `76d76c796cafbaea9556e992381b6e2518ae4f69` | Two actual pinned Alloy-generated resource trees through its strict loader/assembler/validator; no direct manifest JSON adoption or production apply |

## Candidate release notes

- Refresh the four existing Edge vocabularies and plugin OpenAPI integrity pin
  from actual `v0.9.11` source, preserving the existing vocabulary values.
- Add Edge-owned conditional backup metadata and backend egress policy response
  schemas, the egress vocabulary/shape, sanitized positive fixtures and precise
  single-mutation negative expectations for Edge #5992/#5994.
- Record standard HTTP admin `ETag`/`If-Match` semantics, credential-complete
  authoritative verification, coherent namespace snapshot/replacement, and
  process/DP scope limits in [admin-contracts.md](../admin-contracts.md).
- Stage Alloy shared v1 freeze annotations/provenance as a proposal. Retain
  report owner `implemented` / shared **PROPOSED** and manifest **PROPOSED**
  status until final matched owner qualification. Preserve every v1 wire field,
  bound, fixture and description outside `$id`/`x-contract`.

Alloy's report descriptions are part of full owner pairing. Historical
no-consumer wording remains in paired schema descriptions until an owner-backed
coordinated annotation change; the newer qualification record lives in candidate
metadata/docs. The manifest transcription also retains its existing boundary:
owner validation after defaults includes derived resource ID lengths and
endpoint relationships not all asserted by the shared schema. This draft neither
tightens consumer presentation bounds into producer rules nor weakens parity.

## Root finalization and publication order

1. Verify actual Edge release completion, published assets and their immutable
   digests, attestations/ABI evidence, and agreement with the qualified tag.
2. Supply the matched final Alloy owner merge commit, its exact approved second
   parent and all applicable main PUSH successes. Reconcile status, provenance,
   descriptions and the owner decision; do not qualify a newer head using an
   earlier green run. Keep the draft pending if the decision is still absent.
3. Review this canonical diff and fixtures with the owning maintainers; require
   hosted `Schemas, fixtures and vocabularies` success at the final candidate.
   Remove pending candidate annotations only when supported by actual evidence.
4. Root merges the approved canonical PR, verifies that merge commit and its
   second parent, the uniquely associated PR and all applicable main PUSH runs,
   then publishes the immutable `contracts-edge-0.9.11` tag and release notes.
   Move only the included changes out of `[Unreleased]`; retain unrelated entries
   and all historical released sections/tags unchanged.
5. Only after canonical tag publication, coordinate consumer pin/checksum/local
   copy updates and Alloy's matching local annotations/descriptions in their own
   repositories with full hosted parity. Update adoption evidence after those
   PRs qualify. Root owns issue disposition and any separate publishing approval.

Local repository execution was prohibited for candidate preparation. Static
source/diff inspection and the OpenAPI integrity hash do not establish hosted
validation; root opens the draft after the branch push and owns subsequent CI.
