# Plugin config schemas

One self-contained JSON Schema 2020-12 document per built-in Ferrum Edge
plugin, `<plugin>.schema.json`, describing that plugin's `config` object when
the plugin is enabled. Each document is the component that the plugin
catalog's `config_schema.pointer` names in Edge's `openapi.yaml`, plus every
component it references, copied under `$defs` with `#/components/schemas/...`
references (and OpenAPI `discriminator.mapping` targets) rewritten to
`#/$defs/...`; every reference is resolved before a file is written. Each
`$id` names the Edge release it was generated from
(`.../plugin-config-schemas/edge-<ref>/<plugin>.schema.json`), so documents
for two Edge releases never share an identifier. `x-generated` records the source file
(repository, ref, commit, path, SHA-256, pointer) and the catalog's
`config_required_when_enabled` and `scope_constraint` for the plugin.

These files are generated. Never edit them by hand:

```sh
git -C <edge-clone> show <config_schema_document.commit>:openapi.yaml > /tmp/openapi.yaml
python3 -I ci/plugin_config_schemas.py --openapi /tmp/openapi.yaml --write
```

The generator uses only the Python standard library and its own YAML reader,
which refuses any construct outside the subset it implements. `ci/validate.py`
checks every document against the 2020-12 meta-schema and the catalog's pin,
and with `--fetch-openapi` (as CI runs it) compares the reader's parse of the
pinned file with PyYAML's (YAML 1.2 core resolvers) and the files byte for
byte with the generator output.

They are Edge's own configuration schemas, bound to the Edge release the
catalog pins and governed by Edge's support policy, not schema majors of this
repository ([versioning.md](../docs/versioning.md#stability-promise-for-contracts-edge-1),
rule 5). Whether Edge applies a plugin's schema at all depends on the plugin
being enabled; [plugin-config-admission.md](../docs/plugin-config-admission.md)
records release-specific admission rules.
