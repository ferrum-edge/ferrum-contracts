"""Tests for ci/plugin_config_schemas.py: its YAML reader and the generator.

Run with: python -I -m unittest discover -s ci -p 'test_*.py'
Standard library only; nothing is downloaded.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "plugin_config_schemas", Path(__file__).resolve().parent / "plugin_config_schemas.py"
)
gen = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gen)
ROOT = Path(__file__).resolve().parent.parent


class YamlReaderTests(unittest.TestCase):
    def load(self, text: str):
        return gen.load_yaml(text)

    def test_block_mappings_and_sequences(self) -> None:
        text = (
            "a: 1\n"
            "b:\n"
            "  c: two\n"
            "  d:\n"
            "    - x\n"
            "    - 3\n"
            "e:\n"
            "- first\n"
            "- k: v\n"
            "  m: [1, 2]\n"
            "f: ~\n"
        )
        self.assertEqual(
            self.load(text),
            {"a": 1, "b": {"c": "two", "d": ["x", 3]}, "e": ["first", {"k": "v", "m": [1, 2]}], "f": None},
        )

    def test_core_schema_scalars(self) -> None:
        doc = self.load(
            "t: true\nf: False\nn: null\ne:\ni: -12\no: 0o17\nh: 0x1F\nx: 1.5\ny: 1.0e288\n"
            "s: yes\nv: 0.9.21\nq: '0042'\n"
        )
        self.assertEqual(
            doc,
            {"t": True, "f": False, "n": None, "e": None, "i": -12, "o": 15, "h": 31, "x": 1.5,
             "y": 1e288, "s": "yes", "v": "0.9.21", "q": "0042"},
        )

    def test_quoted_scalars_and_escapes(self) -> None:
        doc = self.load(
            'a: "tab\\there \\u00e9 \\"q\\" \\\\"\n'
            "b: 'it''s # not a comment'\n"
            'c: "x: y" # comment\n'
            "d: \"^(\\\\{[^{}]*\\\\})?$\"\n"
        )
        self.assertEqual(
            doc,
            {"a": 'tab\there \u00e9 "q" \\', "b": "it's # not a comment", "c": "x: y", "d": "^(\\{[^{}]*\\})?$"},
        )

    def test_flow_collections(self) -> None:
        doc = self.load(
            "a: [one, \"two, three\", 4, null]\n"
            "b: {type: object, minProperties: 1, not: {type: \"null\"}}\n"
            "c: [\n  x,\n  y\n]\n"
            "d: []\n"
            "e: {}\n"
        )
        self.assertEqual(
            doc,
            {"a": ["one", "two, three", 4, None],
             "b": {"type": "object", "minProperties": 1, "not": {"type": "null"}},
             "c": ["x", "y"], "d": [], "e": {}},
        )

    def test_block_scalars(self) -> None:
        text = (
            "lit: |\n"
            "  line one\n"
            "    indented\n"
            "\n"
            "  line three\n"
            "fold: >-\n"
            "  joined\n"
            "  words\n"
            "\n"
            "  new paragraph\n"
            "    kept\n"
            "  back\n"
            "keep: |+\n"
            "  x\n"
            "\n"
            "strip: |-\n"
            "  y\n"
            "after: z\n"
        )
        self.assertEqual(
            self.load(text),
            {
                "lit": "line one\n  indented\n\nline three\n",
                "fold": "joined words\nnew paragraph\n  kept\nback",
                "keep": "x\n\n",
                "strip": "y",
                "after": "z",
            },
        )

    def test_multi_line_plain_and_comments(self) -> None:
        text = (
            "# leading comment\n"
            "a: first\n"
            "  second\n"
            "\n"
            "  third # trailing\n"
            "b: 2 # two\n"
            "c:\n"
            "  # inside\n"
            "  - one\n"
        )
        self.assertEqual(self.load(text), {"a": "first second\nthird", "b": 2, "c": ["one"]})

    def test_refusals(self) -> None:
        cases = {
            "anchor": "a: &x 1\n",
            "alias": "a: *x\n",
            "tag": "a: !str 1\n",
            "duplicate key": "a: 1\na: 2\n",
            "tab indentation": "a:\n\tb: 1\n",
            "complex key": "? a\n: b\n",
            "non-finite number": "a: .inf\n",
            "unterminated flow": "a: [1, 2\n",
        }
        for label, text in cases.items():
            with self.subTest(label):
                with self.assertRaises(gen.YamlError):
                    self.load(text)


OPENAPI = """\
openapi: 3.1.0
info:
  title: t
  version: 0.0.0
components:
  schemas:
    PluginConfigBase:
      type: object
    AConfig:
      type: object
      additionalProperties: false
      properties:
        inner:
          $ref: "#/components/schemas/Inner"
        nested:
          $ref: "#/components/schemas/Holder/$defs/item"
    Inner:
      type: object
      properties:
        again:
          $ref: "#/components/schemas/Inner"
    Holder:
      $defs:
        item:
          type: string
    BConfig:
      type: string
      enum: [x, y]
    Unused:
      type: integer
"""


def catalog_for(openapi: bytes, plugins=None) -> dict:
    return {
        "config_schema_document": {
            "repo": "ferrum-edge/ferrum-edge",
            "ref": "v9.9.9",
            "commit": "a" * 40,
            "path": "openapi.yaml",
            "sha256": hashlib.sha256(openapi).hexdigest(),
            "openapi": "3.1.0",
        },
        "plugins": plugins
        if plugins is not None
        else [
            {"name": "b_plugin", "config_schema": {"document": "openapi.yaml", "pointer": "#/components/schemas/BConfig"}},
            {
                "name": "a_plugin",
                "config_schema": {
                    "document": "openapi.yaml",
                    "pointer": "#/components/schemas/AConfig",
                    "config_required_when_enabled": True,
                    "scope_constraint": "global",
                },
            },
        ],
    }


class GeneratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.openapi = OPENAPI.encode("utf-8")
        self.catalog = catalog_for(self.openapi)

    def test_documents_are_self_contained(self) -> None:
        files = gen.build(self.catalog, self.openapi)
        self.assertEqual(
            sorted(files), ["plugin-config-schemas/a_plugin.schema.json", "plugin-config-schemas/b_plugin.schema.json"]
        )
        doc = json.loads(files["plugin-config-schemas/a_plugin.schema.json"])
        self.assertEqual(doc["$schema"], gen.SCHEMA_DIALECT)
        self.assertEqual(doc["$id"], f"{gen.ID_BASE}/a_plugin.schema.json")
        self.assertEqual(doc["$ref"], "#/$defs/AConfig")
        self.assertEqual(sorted(doc["$defs"]), ["AConfig", "Holder", "Inner"])
        self.assertEqual(doc["$defs"]["AConfig"]["properties"]["inner"], {"$ref": "#/$defs/Inner"})
        self.assertEqual(doc["$defs"]["AConfig"]["properties"]["nested"], {"$ref": "#/$defs/Holder/$defs/item"})
        self.assertEqual(doc["$defs"]["Inner"]["properties"]["again"], {"$ref": "#/$defs/Inner"})
        self.assertEqual(doc["x-generated"]["source"]["pointer"], "#/components/schemas/AConfig")
        self.assertEqual(doc["x-generated"]["scope_constraint"], "global")
        self.assertTrue(doc["x-generated"]["config_required_when_enabled"])
        self.assertNotIn("#/components/", json.dumps(doc["$defs"]))

    def test_output_is_deterministic(self) -> None:
        first = gen.build(self.catalog, self.openapi)
        reordered = dict(self.catalog, plugins=list(reversed(self.catalog["plugins"])))
        self.assertEqual(first, gen.build(reordered, self.openapi))
        for data in first.values():
            self.assertTrue(data.endswith(b"\n"))

    def test_a_different_file_than_the_pin_is_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "sha256"):
            gen.build(self.catalog, self.openapi + b"\n")

    def test_references_outside_components_schemas_are_refused(self) -> None:
        for ref in ("other.yaml#/X", "#/components/parameters/X", "#/components/schemas/Missing"):
            with self.subTest(ref=ref):
                openapi = OPENAPI.replace('"#/components/schemas/Inner"\n        nested', f'"{ref}"\n        nested', 1).encode()
                with self.assertRaises(ValueError):
                    gen.build(catalog_for(openapi), openapi)

    def test_a_pointer_inside_a_component_is_refused_as_a_root(self) -> None:
        plugins = [{"name": "p", "config_schema": {"document": "openapi.yaml", "pointer": "#/components/schemas/Holder/$defs/item"}}]
        with self.assertRaises(ValueError):
            gen.build(catalog_for(self.openapi, plugins), self.openapi)

    def test_compare_reports_missing_extra_and_changed_files(self) -> None:
        files = gen.build(self.catalog, self.openapi)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gen.write(root, files)
            self.assertEqual(gen.compare(root, files), [])
            (root / gen.OUTPUT_DIR / "stale.schema.json").write_text("{}\n")
            target = root / "plugin-config-schemas/a_plugin.schema.json"
            target.write_bytes(target.read_bytes().replace(b"AConfig", b"Changed", 1))
            (root / "plugin-config-schemas/b_plugin.schema.json").unlink()
            problems = gen.compare(root, files)
            self.assertEqual(len(problems), 3, problems)
            self.assertTrue(any("b_plugin" in p and "missing" in p for p in problems))
            self.assertTrue(any("stale" in p and "remove" in p for p in problems))
            self.assertTrue(any("a_plugin" in p and "differs" in p for p in problems))
            gen.write(root, files)
            self.assertEqual(gen.compare(root, files), [])


class RepositoryTests(unittest.TestCase):
    """The committed files carry the catalog's pin (the byte comparison with the
    pinned openapi.yaml runs in ci/validate.py --fetch-openapi)."""

    def test_committed_files_name_the_pinned_openapi(self) -> None:
        catalog = json.loads((ROOT / gen.CATALOG).read_text(encoding="utf-8"))
        document = catalog["config_schema_document"]
        names = sorted(p["name"] for p in catalog["plugins"] if p.get("config_schema"))
        files = sorted(p.name for p in (ROOT / gen.OUTPUT_DIR).iterdir() if p.name != "README.md")
        self.assertEqual(files, [f"{name}.schema.json" for name in names])
        for name in names:
            doc = json.loads((ROOT / gen.OUTPUT_DIR / f"{name}.schema.json").read_text(encoding="utf-8"))
            self.assertEqual(doc["x-generated"]["source"]["sha256"], document["sha256"], name)
            self.assertEqual(doc["x-generated"]["source"]["commit"], document["commit"], name)


if __name__ == "__main__":
    unittest.main()
