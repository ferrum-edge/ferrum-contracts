# Changelog

All notable changes to the Ferrum contracts are recorded here. Releases are
tags named `contracts-edge-X.Y.Z` pinned to Ferrum Edge releases; see
[docs/versioning.md](docs/versioning.md).

## [Unreleased]

## [contracts-edge-0.9.14] - 2026-10-07

Contracts for Ferrum Edge `v0.9.14`
(`@@EDGE_0914_COMMIT@@`). See the
[release record](docs/releases/contracts-edge-0.9.14.md).

### Added

- `backend-egress-policy` v2 optional `data_plane_attestation` for Edge #6029
  (issue #6020): the CP-only object listing each live ConfigSync Subscribe
  stream of the namespace with its self-reported policy, the field-wise
  `weakest_policy`, `weakest_policy_complete` and
  `all_connected_public_only_guaranteed`. `schema_version` stays `2`. The
  schema asserts the object only on `admission-only`, closes the attestation,
  entry and policy objects, and checks the policy mode lists and guarantee, the
  `attestation`/`policy` pairing and the summary implications. Five valid
  fixtures (empty, reported, unknown, allow-overlay and shared `node_id` sets)
  and twenty-one invalid fixtures (#18).
- `vocabulary-backend-egress-policy` v2 optional
  `data_plane_attestation_source`, `data_plane_attestation_statuses` and
  `data_plane_attestation_rule`, present together or not at all, with one valid
  and two invalid fixtures.
- An `admin-deployment-mutation-acknowledgement` valid fixture for the `503`
  `durable: "not_committed"` body (Edge #6027).
- Release record `docs/releases/contracts-edge-0.9.14.md`.

### Changed

- Repin all five Edge vocabularies and the egress, conditional snapshot,
  deployment snapshot v2 and acknowledgement schema provenance to `v0.9.14`;
  the plugin catalog pins `openapi.yaml` SHA-256
  `6d286649ae744691e2eeb7d16607c538ca02e31bdeaafe98ab07fc861e7b9da4`. Error
  tokens and classes, header names, provisioning values and plugin
  registrations are unchanged. `diagnostic-ref` v1 keeps its frozen bytes.
- `vocabularies/backend-egress-policy.json` carries the attestation source,
  statuses and rule, and its consumer rule describes CP attestation as an
  alternative to reading every DP.
- `admin-deployment-mutation-acknowledgement` v1 describes each `durable`
  value: from Edge v0.9.14 only commit or commit-acknowledgement uncertainty
  reports `unknown`, and pre-commit store failures report `not_started` or
  `not_committed` (Edge #6027, issue #6021). The enum is unchanged.
- `admin-deployment-snapshot` v2 records the namespace-wide token fence and the
  `api_spec_contents` peak memory that Edge v0.9.14 documents.
- `gateway-errors.json` notes the Edge #6028/#6042 reclassification in the
  `protocol_error`, `read_write_timeout` and `response_body_too_large`
  meanings: a backend HTTP/2 reset other than `NO_ERROR` is `protocol_error`
  and charged to the target, and buffered read errors report their real class
  (a buffered read timeout is `504`). No class or token is added or removed.
- `gateway-headers.json` `ETag` describes the conditional backup tag as a
  namespace state token, and `If-Match` the namespace-wide deployment fence and
  the narrowed `503` durable outcomes.
- Admin, deployment, ownership, adoption, versioning and release-process
  docs, `README.md` and `fixtures/README.md` describe the Edge v0.9.14 changes
  and mapping.
- Name Ferrum Edge LLC as the copyright holder in the `LICENSE` Required Notice.

## [contracts-edge-0.9.13] - 2026-10-06

Contracts for Ferrum Edge `v0.9.13`
(`9b83115de7ec23ab51ec4feae6bed65e596db425`). See the
[release record](docs/releases/contracts-edge-0.9.13.md).

### Added

- `backend-egress-policy` v2 and `vocabulary-backend-egress-policy` v2 for
  Edge #6017: `schema_version` 2, and `public_only_guaranteed` is true only
  with `enforcement_scope=local-data-plane`, public mode and no allow
  overrides. v2 fixtures cover the OpenAPI example, every non-serving scope
  and the narrowed guarantee rule (#18).
- `admin-deployment-snapshot` v2 for Edge #6017: required
  `api_spec_contents` (one base64 copy of the stored spec bytes, outside the
  evidence) and `api_specs` items whose `spec_content` and
  `external_ref_snapshot` are `StoredContentDigest` (`sha256`, `len`). v2
  fixtures carry the empty SQL and MongoDB snapshots forward, add a synthetic
  one-spec SQL snapshot, and have an invalid fixture for each new rule.
- Two `admin-deployment-mutation-acknowledgement` valid fixtures for the `507`
  `NamespaceSnapshotTooLarge` bodies (`durable` `not_started` and
  `not_committed`).
- Release record `docs/releases/contracts-edge-0.9.13.md`.

### Changed

- `vocabularies/backend-egress-policy.json` moves to shape version 2 with
  `schema_version: 2` and the local-enforcement guarantee and consumer rules.
  The v1 response and vocabulary schemas stay for Edge v0.9.11 and v0.9.12;
  their availability notes now say which Edge releases emit them.
- `admin-deployment-snapshot` v1 stays for Edge v0.9.12; its availability
  note records that v0.9.13 rejects v0.9.12 tokens with `412`.
- Repin all five Edge vocabularies and the conditional snapshot, deployment
  and acknowledgement schema provenance to `v0.9.13`; the plugin catalog pins
  `openapi.yaml` SHA-256
  `5f3e50e217b22b97d068490bdad9563ea450097a2daf7df4f80ff61f98559a81`. Error
  tokens and classes, header names, provisioning values and plugin
  registrations are unchanged. `diagnostic-ref` v1 keeps its frozen bytes.
- `gateway-headers.json` `ETag` and `If-Match` describe the
  `namespace_snapshot.v2` and `deployment_snapshot.v2` MAC domains, the `412`
  for tags issued by v0.9.12 or earlier, and the 64 MiB `507` bound.
- Schemas with several majors keep fixtures in `fixtures/<name>/v<N>/`, one
  directory per major, and `ci/validate.py` checks each against its own major,
  as `docs/versioning.md` requires. Existing v1 fixtures moved unchanged.
- Admin, deployment, ownership, adoption, versioning and release-process docs
  describe the v2 contracts and the Edge v0.9.13 mapping.
- Record the `contracts-edge-0.9.12` publication at
  `31f0a21d707795be293d15837c2f77c3d84219d8` (PR #15, release 403772929,
  13:58:38 UTC on 2026-10-05, Edge `v0.9.12` at
  `0d917701b63ef38210c49df830f48cf0457cbc7d`) and refresh the consumer pin
  table to the values verified on 2026-10-06 (#17).
- Release process: release records and `[contracts-edge-*]` changelog sections
  are tagged content, written in final form without status words; publication
  status belongs in PR bodies and tracking issues (#18).
- Move Edge distribution evidence (asset/Docker digests and hosted
  signature/SLSA/SBOM facts) out of contracts docs; link the Edge GitHub
  Release and its `docs/releases/vX.md` record instead (#18).
- Correct the `main` protection text in `AGENTS.md` and `docs/ownership.md`: it
  requires the `Schemas, fixtures and vocabularies` check and no approving
  reviews (ruleset 24239605; solo maintainer), not a code-owner review (#18).

### Removed

- The GPT-6.1 Sol worker skill, which this project does not use (#16).

## [contracts-edge-0.9.12] - 2026-10-05

Published 2026-10-05 at 13:58:38 UTC as GitHub release 403772929, tag at
`31f0a21d707795be293d15837c2f77c3d84219d8` (merge of #15), pinned to Ferrum Edge
`v0.9.12` (`0d917701b63ef38210c49df830f48cf0457cbc7d`). See the
[release record](docs/releases/contracts-edge-0.9.12.md).

### Added

- Separate deployment snapshot and mutation acknowledgement v1 schemas from
  actual owner OpenAPI/handlers for Edge #6010/#6012, with source-transcribed
  empty SQL/replica-set MongoDB snapshots, durable/live/refusal fixtures and
  exact single-change invalid expectations. Preserve owner required/optional
  fields and open evidence/resource shapes; assert the source's cleanup-true
  implication without treating JSON validation as runtime authorization.
- Document secret-complete original raw/spec/external-reference evidence,
  distinct strong deployment tokens, strict conditional proxy removal/spec
  replacement and explicit acknowledgement-based recovery cleanup. CP/unserved
  HTTP 200 is cleanup false; refusal/uncertainty prohibits replay or refreshed
  authority. Original namespace/row backup and restore semantics are retained.
- Record actual Edge release 403693646, all 20 successful Release jobs, all 14
  pre-tag main PUSH successes, verified asset/sidecar and Docker Hub identities,
  default-image gateway/CNI byte pairing and hosted cryptographic/ABI gates.
  Preserve private GHCR and absent image revision-label limits.

### Changed

- Refresh all five Edge vocabulary release/provenance pins, diagnostic-ref and
  existing admin schema provenance to immutable v0.9.12 owner
  `0d917701b63ef38210c49df830f48cf0457cbc7d`; pin OpenAPI SHA-256
  `f7242228d73d34ad2d7da3c989ec6ba15bb6ae1f2f4c94a8e0a181b000caae77`.
  Tokens/classes, provisioning values, plugin catalog metadata/pointers,
  diagnostic-ref wire fields and egress classifier are unchanged. Extend
  standard ETag/If-Match documentation for the separate deployment profile.
- Distinguish published Contracts 0.9.11 from prepared 0.9.12 throughout current
  docs and artifact descriptions. Preserve historical release sections/records,
  fixtures, first availability, Alloy's accepted unchanged shared v1 freeze and
  other-owner unreleased annotations. Unfinished Edge #6011 rejection-contract
  work is not released here. Nexus Part B, Foundry's guarded-write decision,
  consumer qualification and advisory disposition remain separate pending work.
- Keep validator behavior, workflow/action/dependency pins and permissions
  unchanged. Only static inspection/integrity hashing/diff checks run locally;
  GitHub-hosted validation is the conformance gate.
- Prepare `contracts-edge-0.9.12` against actually released, root-qualified Edge
  `v0.9.12`, `0d917701b63ef38210c49df830f48cf0457cbc7d`. The prepared
  contents below require their own canonical review/hosted/protected merge/PUSH
  and immutable tag/release gates. At preparation time the latest published
  Contracts was 0.9.11; consumer adoption and pending publisher profile decisions
  are unchanged.
- Record actual `contracts-edge-0.9.11` publication at
  `390edbd5b2485af0988e02f7827fde778d76ae0a` after PR #13 and main PUSH
  validation, including release 403239814 at 22:41:21 UTC on 2026-10-04 and
  root's accepted unchanged shared v1 freeze. Update current release mappings
  and documentation; preserve the prepared wording in the released section/tag
  as historical, existing consumer pins and qualification slices, and Alloy's
  unpublished status with no separate crate publishing approval. Consumer
  adoption remains pending until its PRs merge and qualify.

## [contracts-edge-0.9.11] - 2026-10-04

Published 2026-10-04 at 22:41:21 UTC as GitHub release 403239814, tag at
`390edbd5b2485af0988e02f7827fde778d76ae0a`. Root has accepted the unchanged
shared Alloy v1 freeze in this release. See the
[release record](docs/releases/contracts-edge-0.9.11.md) for verified Edge
distribution, final qualified Alloy owner and publication order.

### Added

- Conditional snapshot metadata and backend egress response schemas, the egress
  vocabulary/shape, sanitized fixtures and exact negative path/keyword expectations
  for Edge #5992/#5994. Keep strict producer validation, opaque token/runtime
  authorization boundaries and unknown-value reader semantics; public-only
  publication requires serving-DP scope.
- Standard HTTP admin `ETag`/`If-Match`, credential-complete verification,
  coherent namespace tokens, atomic replacement/lease fences, runtime refusal
  statuses and the unconditional restore exception in the admin contract docs.
- Add shared GPT-6.1 Sol worker skills for Codex and Claude with optional fast mode.

### Changed

- Refresh all four existing Edge vocabularies from published v0.9.11,
  `c764084b3b51c3f7ffde268c039688d35e49c553`, and update the pinned OpenAPI
  SHA-256. Error tokens/classes, provisioning values, plugin registrations and
  lifecycle metadata are unchanged from r2. No obsolete `main_branch_delta`
  exists in these files; historical first-availability entries are retained.
- Finalize diagnostic-report and service-manifest shared v1 as EXISTING/implemented
  in the candidate at qualified Alloy owner
  `81cbb410d34ff5fba1f3d54cfd2e7ebccaed397e`, with root's accepted coordinated
  freeze and owner-unreleased availability. Preserve every wire field, bound,
  fixture, unknown-reader rule and full report description pairing. The manifest
  remains an owner-code transcription with post-default/cross-field limits.
  No separate prior human approval, Alloy crate publishing permission or new
  consumer pin is implied.
- Synchronize README, ownership, adoption, versioning and release process with
  verified Edge distribution, all 18 final Alloy main PUSH jobs/checks and the
  remaining canonical review/hosted validation/merge/tag gates. Ordinary owner
  squash qualification uses exact source/CI evidence; release/tag targets still
  require an exact reviewed PR second parent and all main PUSH successes.
  The existing hosted validator auto-discovers new artifacts; workflow,
  permissions, dependencies and validator behavior are unchanged.
- Refresh the adoption ledger from immutable 2026-10-04 consumer PIN files,
  test/workflow sources and hosted evidence for Alloy #27: Anvil diagnostic
  import, GitForgeOps generated resource validation, Nexus/Foundry manifest
  previews and Foundry's accepted presentation ADR. Record the split Nexus
  pins, the published r2 `[agents]` addition and the Edge v0.9.10 mapping.
- Clarify owner implementation versus shared qualification in the earlier
  adoption-only refresh: shared schemas were PROPOSED pending an owner-backed
  canonical freeze. That refresh changed no schemas, pins, tags or release status;
  the coordinated freeze decision is now recorded in this release.

## [contracts-edge-0.9.9-r2] - 2026-10-01

Revision of `contracts-edge-0.9.9` for an Alloy-owned schema change. The
Edge-owned vocabularies are unchanged and still describe Ferrum Edge v0.9.9,
which also covers v0.9.10 (no contract-source changes).

### Added

- `service-manifest` v1: optional `[agents]` configuration from Alloy PR #113
  (#8, closes #7).

### Changed

- Sync README, versioning, adoption, and release-process docs with the
  published contracts tags and current consumer pins.

## [contracts-edge-0.9.9] - 2026-10-01

Refreshes the Edge-owned vocabularies from Ferrum Edge v0.9.9, commit
`234717ce41965cd1e2b5c6c761a25475c5d7628c`.

### Changed

- `ci/validate.py` hardening from the seed review (#2): it now collects every
  `format` the schemas use and fails if a JSON Schema 2020-12 standard format
  has no registered checker, rejects duplicate cardinality surface names
  instead of letting the last one win, and can pin the top-level `oneOf` /
  `anyOf` keyword for an invalid fixture with an optional `top_keyword` in
  `fixtures/invalid-expectations.json`.
- Gateway headers: `X-Ferrum-Diagnostic-Ref` (#5845) and
  `X-Ferrum-Diagnostic-Owner-Replica` (#5868) move from unreleased to
  released in v0.9.9. The `x-consumer-*` reserved namespace also documents
  case-insensitive matching and `_`/`-` equivalence (#5880).
- `diagnostic-ref` v1: the released contract includes the fd2 reference form
  and replica identifier in Edge v0.9.9; valid and invalid fixtures cover the
  released form and its replica-id pattern.
- Plugin catalog: refreshes the `openapi.yaml` pin and `mcp_gateway` lifecycle
  phases; final-backend-header policy and final-request-body phases came from
  Edge #5905, and response-body normalization came from #5930. Built-in
  registrations and removed-plugin names are unchanged.
- Gateway error classes, tokens, and provisioning attribution have no value
  changes from v0.9.8; their source provenance now points to v0.9.9.

### Added

- Gateway-header vocabulary records `x-ferrum-mcp` as an OpenAPI extension
  field, not an HTTP header, from Edge #5930 (`docs/api_specs.md`).
- Plugin catalog adds the optional `websocket_framing_plugins` schema property
  and the released capability list (`waf`, `ws_frame_logging`,
  `ws_message_size_limiting`, `ws_rate_limiting`) from
  `BUILTIN_WEBSOCKET_FRAMING_PLUGINS` for `websocket_permessage_deflate`
  passthrough admission (#5853, #5869).

## [contracts-edge-0.9.8] - 2026-09-30

Initial delivery of the work tracked by ferrum-edge/.github#4, published as
`contracts-edge-0.9.8`.

### Added

- Gateway error vocabulary (`vocabularies/gateway-errors.json`): the 19
  `ErrorClass` values with their pre-wire flag, log kind and default
  `X-Gateway-Error` token, and the eight `X-Gateway-Error` tokens with their
  statuses, rejection phases and meaning. From Ferrum Edge v0.9.8
  (`src/retry.rs`, `docs/error_classification.md`). Unchanged on Edge `main`.
- Gateway-owned headers (`vocabularies/gateway-headers.json`): the
  `x-consumer-*`, `x-ferrum-*` and `x-path-param-*` namespaces, the reserved
  gateway assertions, `X-Gateway-Error` and `X-Gateway-Upstream-Status`,
  internal markers, mesh control headers, and the admin API `X-Ferrum-*`
  headers, from Edge v0.9.8. `X-Ferrum-Diagnostic-Ref` and
  `X-Ferrum-Diagnostic-Owner-Replica` are listed as unreleased (Edge `main`).
- `provisioned-by` attribution (`vocabularies/provisioned-by.json`): the label,
  the `X-Ferrum-Provisioned-By` header rules, and the values
  `ferrum-edge-git-forge-ops`, `ferrum-nexus` and `ferrum-foundry`.
- Plugin catalog index (`vocabularies/plugin-catalog.json`): all 82 built-in
  plugins of Edge v0.9.8 with failure policy, classification, priority,
  documented phases and protocols, response-body production, and a pointer to
  each plugin's config schema in Edge's `openapi.yaml` (pinned by sha256), plus
  the two removed plugin names.
- Schemas: `diagnostic-ref` v1 (`ferrum.diagnostic_ref.v1`, Edge `main`,
  unreleased), `diagnostic-finding` v1 (Anvil `DiagnosticFinding`),
  `diagnostic-report` v1 (Alloy `ferrum.diagnostic_report`),
  `service-manifest` v1 (Alloy, **proposed**), `gitforgeops-resource` v1
  (GitForgeOps resource file envelope), and one shape schema per vocabulary.
- Conformance fixtures for every schema and vocabulary, taken from the owners'
  fixtures and examples where they exist (`fixtures/README.md`).
- `Validate contracts` workflow and `ci/validate.py`, with hash-pinned
  validator dependencies (including `rfc3339-validator`, so `date-time` is
  asserted). CI also checks that each invalid fixture fails with its
  recorded instance path and keyword (`fixtures/invalid-expectations.json`),
  that values copied from vocabularies into schemas match, and that each
  plugin's config schema pointer is the one Edge's `PluginConfigBase`
  references for that plugin name.
- Dependabot for GitHub Actions and `ci/requirements.txt`; `.github/CODEOWNERS`.
- Docs: ownership, versioning, adoption status per consumer (including the
  ferrum-alloy#27 checklist), and the release process.
