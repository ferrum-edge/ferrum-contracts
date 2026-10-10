# contracts-edge-0.9.17 release record

`contracts-edge-0.9.17` holds the contracts for Ferrum Edge `v0.9.17`.
The tag is the merge commit of its release PR. The
[GitHub release](https://github.com/ferrum-edge/ferrum-contracts/releases/tag/contracts-edge-0.9.17)
records its immutable commit and publication time.

## Edge source

Edge `v0.9.17` points to `669c574c1d1e88e84dccb26a8159939e6694644d`, the merge of
[Edge #6162](https://github.com/ferrum-edge/ferrum-edge/pull/6162), with first
parent `4c81cb456f9723de42dbd7b0f09c3e3307d527d1` and reviewed second parent
`583444c07c06fde1bbc434f299cbe9315b09a33f`. The owner expressly adopted the
frozen ARM64 producer-policy repair after independent full application and
candidate-policy qualification; the documented migration admission failures
were retained. Canonical trusted-policy and all final-source publication
checks then qualified the selected owner source before protected dispatch.
The existing `v0.9.16` tag remains immutable and has no published release;
`v0.9.17` carries its changes once and restores the ARM64 producer host with
resource observations. Runtime Rust source and dependency versions match the
unpublished v0.9.16 tag; package-version and release-producer metadata change.
Every source in this Contracts release is read with `git show` at the actual
immutable published owner tag.

[Edge release 409158631](https://github.com/ferrum-edge/ferrum-edge/releases/tag/v0.9.17)
was published at 19:29:40 UTC on 2026-10-10. Edge assets, checksums, signed container
indices, provenance, SBOMs and hosted qualification belong to that Edge release.
This Contracts release does not sign application binaries or certify consumer
adoption. The owner's `CHANGELOG.md` and `docs/upgrade_guide.md` describe the
runtime changes.

`openapi.yaml` at the tag has SHA-256
`297b312ac1e7b2a7b7cfef74cdf4550063da0676edcee07d9652e3fb16d806b1`.

## Contract changes

No contract needs a new major. `diagnostic-ref` v1 adds `loop_detected` to
the closed enumerations that mirror Edge's vocabulary, under the documented
closed Edge-vocabulary exception. Existing fields, reference and replica
patterns, and historical owner introduction provenance remain intact.

- **Proxy hop budget.** `X-Ferrum-Hops` is a gateway-owned HTTP-family
  request assertion. The frontend reads one unsigned decimal count before
  routing and plugins; absence means zero. The configured limit defaults to
  10 and accepts 0–255. A count at the limit returns HTTP 508 with
  `X-Gateway-Error: loop_detected`, or native gRPC trailers-only
  `FAILED_PRECONDITION` without an HTTP 5xx token. Malformed, repeated,
  signed, fractional, empty or comma-folded fields return HTTP 400 or native
  gRPC `INVALID_ARGUMENT`, without a gateway-error token. HTTP 508 is never
  retried, even if configured as retryable. An outer gateway that relays
  a backend 508 labels it `backend_error`; only the refusing hop authors
  `loop_detected`.
- **Forwarded count protection.** With the limit enabled, the frontend
  stamps `received + 1` before Connection confinement. The count is
  reasserted after request plugins, later gateway-assertion refreshes and
  final backend-header-policy hooks; configured destinations are reserved
  with ASCII case-insensitive `_`/`-` equivalence. Local mesh delivery checks
  but preserves the count only for a local workload target that is not a
  gateway listener. Missing listener-port publication fails closed and
  increments. Request-scoped plugin HTTP calls and mirrors carry the ordinary
  forwarded count; batch/background sinks and shared cache refreshes do not.
  Opaque stream proxies have no request header. Zero disables the entire
  feature, including parsing and stamping, and leaves a client field as an
  ordinary header. A stamp can add one field after the frontend header-count
  check, so the next hop can refuse a request exactly at its limit with 431.
- **Bounded observability.** Header-token cardinality is nine, the reserved
  HTTP error-class metrics vocabulary is 25, and `ErrorClass` remains 19.
  The hop-limit fence currently emits status counters and bounded warnings,
  without a terminal transaction summary or `loop_detected` error-class
  metric row. In diagnostic `all` mode its reference has unrouted detail:
  `detail.rejection.phase: proxy_hop_limit`, `detail.rejection_phase: null`,
  no proxy or backend target, and `backend_dispatch: not_dispatched`.
  `proxy_hops_invalid` is the corresponding malformed-field raw phase and
  has no token. New valid fixtures reproduce those owner-derived `all`-mode
  responses; invalid fixtures change only the token-mapped detail field to
  the raw phase and record its expected `/detail/rejection_phase` enum error.
- **Existing timeout meaning.** `backend_timeout` begins when the backend
  dispatch calls `send()`, including while TCP/TLS connection setup is still
  in progress. It does not assert remote acceptance or receipt of bytes.
  `request_timeout` covers expiry before dispatch and during retry backoff.
  This corrects earlier prose to match existing owner handoff behavior; it
  introduces no new timeout value, meaning or schema major.
- **Upload and response terminal handling.** Successful upload collection
  requires transport END_STREAM. An observed cancellation finalizes as HTTP
  499 / native gRPC `CANCELLED`; it remains neutral to backend health,
  releases admission neutrally and is not retried. Malformed uploads retain
  400 / `INVALID_ARGUMENT`; buffered upload
  read timeouts retain 408 / `DEADLINE_EXCEEDED`; route-total deadlines retain
  504; and native HTTP/3 protocol failures retain 502 / `protocol_error` or
  native gRPC `UNAVAILABLE`. Raw diagnostic phases include the compiled-in
  `client_disconnect_upload_before_*`, `client_disconnect_terminal_request_body`, buffered
  upload, buffered authorization-expiry and invalid H3 upload labels. These
  are open `detail.rejection.phase` labels, not new token-mapped enums.
  Gateway-local request-buffer exhaustion preserves the trusted native
  gRPC flavor as trailers-only `RESOURCE_EXHAUSTED`; ordinary HTTP remains
  503, including mesh and Unix transport paths. gRPC-Web's buffered bridge
  removes stale initial terminal metadata after hooks and accounting, with
  its terminal frame encoded once; native trailers-only gRPC stays intact.
- **Plugin catalog and configuration.** Registered types, parity metadata,
  removed names and `PluginConfigBase` pointers are unchanged. Their pinned
  `openapi.yaml` now reserves hop-count destinations, records the explicit
  Lambda/Bedrock `allow_custom_endpoint_with_ambient_credentials` opt-in and
  clarifies identity display-claim precedence. Concrete built-in trust,
  native gRPC admission, transport-qualified bodyless CORS exceptions and
  Sidecar HTTP-listener CONNECT refusal are runtime composition rules, not
  invented per-type catalog properties. Config-chosen AWS endpoints use the
  official regional authority with ambient credentials unless the explicit
  custom-authority opt-in is configured. Owner-trusted process
  `AWS_LAMBDA_ENDPOINT_URL` remains an exception when the row selects no
  endpoint. Environment session tokens accompany environment key pairs,
  never complete config-provided pairs; a config session token belongs beside
  its config key pair.
- **Deployment ordering and authority.** Snapshot v2 and acknowledgement v1
  keep their wire rules. The owner derives `proxies`, `plugin_configs`,
  `upstreams` and `api_specs` from canonical evidence resource slots 0, 3,
  2 and 5, preserving ID ordering and proxy associations ordered by
  `plugin_config_id`. This aligns typed inspection lists with the evidence
  that the deployment token authenticates. Complete original evidence,
  gzip spec bytes and external references remain required for recovery.
  No refreshed-token replay or automatic cleanup is authorized; cleanup
  still requires the original token and an explicit qualifying acknowledgement.
- **Admin and cached reads.** A present admin JWT `ns` claim always bounds
  the caller, independent of the flag that additionally requires a claim.
  Fleet-global routes and metrics refuse bounded tokens; observability
  tenant tiers remain bounded. A cached read whose fallback cannot establish
  authoritative absence returns 503 rather than a false 404. These are
  authorization/runtime rules, not new JSON envelope fields.

## Provenance and unchanged contracts

All five vocabulary `edge_release` and current Edge-owned provenance pins
read the actual Edge release source. Conditional snapshot v1, backend egress
v2, deployment snapshot v2 and mutation acknowledgement v1 retain their wire
rules. Earlier major files and their historical provenance remain available.
Other owners' schemas, availability annotations, fixtures and consumer pins
remain unchanged.

## Validation and adoption

GitHub-hosted `Validate contracts` remains the schema, fixture and pinned
OpenAPI conformance gate. No validator, workflow, dependency, permissions or
gate exception is introduced. Consumer adoption requires each consumer's own
pin/copy/checksum PR and qualification; a canonical tag does not establish
that those changes have landed or release any unrelated application.
