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
  `<name>` major `<N>`. The file names `contract`, `contract_version`, and the
  `producer` revision the outcomes were read from (`repo`, `ref`, full
  `commit`, `paths`, `symbols`, and `availability: unreleased` when the
  revision exists only on the producer's default branch).
- Each case has an `id`, a `description`, `schema_valid`, the producer
  outcome, and the payload as `instance`.
- Released case sets are immutable like fixtures. A new producer revision with
  different outcomes adds a new case set or a new major; it does not rewrite
  cases already in a `contracts-edge-*` tag. `CHANGELOG.md` records every
  change under `[Unreleased]`.

`ci/validate.py` checks that each `instance` passes the schema exactly when
`schema_valid` is true, and that the recorded outcome agrees with the case's
own data (for derived IDs: every ID extends the effective proxy ID, and
`producer_exports` is true exactly when every derived ID fits the limit). It
does not run the producer. The producer's own tests are named in `symbols`.

## Case sets

| Case set | Producer rule | Producer revision |
|---|---|---|
| [`service-manifest/v1/derived-id-limit.json`](service-manifest/v1/derived-id-limit.json) | Alloy always generates `<proxy_id>-otel-tracing` and refuses a manifest whose derived resource ID exceeds Edge's 254-character limit, with or without `gateway.otel_endpoint`: 241-character proxy IDs export, 242-character ones do not. The explicit-exporter pair is the control. (#80) | ferrum-alloy `db412da37564ffbe869e2b40530dbebf5afe7ac8` (main, unreleased) |

Consumer results for these cases are recorded in
[docs/adoption.md](../docs/adoption.md#service-manifest-derived-id-qualification).
