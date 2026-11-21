# Qualification cases

Fixtures (`fixtures/<name>/{valid,invalid}/`) say what a schema accepts and
rejects. Some producer rules apply after defaults, outside what JSON Schema
can express, so a payload can pass the schema and still be one the producer
refuses. A qualification case records such a payload, whether it passes the
schema (`schema_valid`), and the producer's own outcome. A case is not a
fixture: consumers must not treat a schema-valid case as one the producer
can export.

## Layout

- `qualification/<name>/v<N>/<case-set>.json` holds cases for schema
  `<name>` major `<N>`. The file names `contract`, `contract_version`, the
  producer `rule` it qualifies, and the `producer` revision the outcomes were read from (`repo`, `ref`, full
  `commit`, `paths`, `symbols`, and `availability: unreleased` when the
  revision exists only on the producer's default branch).
- Each case has an `id`, a `description`, `schema_valid`, the producer
  outcome, and the payload as `instance`.
- Released case sets are immutable like fixtures. A new producer revision with
  different outcomes adds a new case set or a new major; it does not rewrite
  cases already in a `contracts-edge-*` tag. `CHANGELOG.md` records every
  change under `[Unreleased]`.

`ci/validate.py` checks that each `instance` passes the schema exactly when
`schema_valid` is true. For each known `rule` it also transcribes the
producer rule and checks the recorded outcome against it. For
`alloy-derived-resource-id-limit`, every case is schema-valid and equals the
set's `base` (the one reviewed fixture Alloy exports for that contract major,
fixed in `ci/validate.py` by path and sha256; `plain-http.json` for
`service-manifest` v1, so a changed base fails until it is re-qualified) except
for `gateway.proxy_id`,
`gateway.correlation_id` and the optional removal of `gateway.otel_endpoint`
and `gateway.otel_root_sampling_ratio`, so the ID limit is the only producer
rule that can differ. The effective proxy ID must match Alloy's `valid_id`
grammar, and `derived_resource_ids` must be exactly the
IDs Alloy derives (`<proxy_id>-upstream` with a health check,
`<proxy_id>-correlation-id` unless correlation is disabled, and always
`<proxy_id>-otel-tracing`, with the proxy ID defaulting to `service.name`),
`edge_resource_id_max_length` must be 254, and `producer_exports` must be true
exactly when every derived ID fits. CI does not run the producer; a new rule
needs its own check in `ci/validate.py`. The producer's own tests are named
in `symbols`.

## Case sets

| Case set | Producer rule | Producer revision |
|---|---|---|
| [`service-manifest/v1/derived-id-limit.json`](service-manifest/v1/derived-id-limit.json) | Alloy always generates `<proxy_id>-otel-tracing` and refuses a manifest whose derived resource ID exceeds Edge's 254-character limit, with or without `gateway.otel_endpoint`: 241-character proxy IDs export, 242-character ones do not. The explicit-exporter pair is the control. (#80) | ferrum-alloy `db412da37564ffbe869e2b40530dbebf5afe7ac8` (main, unreleased) |

Consumer results for these cases are recorded in
[docs/adoption.md](../docs/adoption.md#service-manifest-derived-id-qualification).
