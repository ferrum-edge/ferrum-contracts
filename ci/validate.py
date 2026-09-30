#!/usr/bin/env python3
"""Validate the ferrum-contracts repository.

Checks, in order:

1. Layout: every schema lives at schemas/<name>/v<N>.schema.json, its `$id`
   is BASE/<name>/v<N>.schema.json, and its `x-contract` block names the same
   <name> and <N>.
2. Every schema is valid against the JSON Schema 2020-12 meta-schema.
3. Fixtures: every file under fixtures/<name>/valid/ must validate against
   the latest version of schema <name>, and every file under
   fixtures/<name>/invalid/ must fail it. Each schema needs at least one of
   each.
4. Vocabularies: every vocabularies/<v>.json validates against the schema its
   `$schema` names, which must be schemas/vocabulary-<v>/v<version>.
5. Vocabulary consistency checks that JSON Schema cannot express (unique
   values, cross-references between vocabularies).
6. Cross-contract fixture checks (for example: every valid Anvil
   DiagnosticFinding fixture is also a valid Alloy diagnostic_report Finding).
7. Optional (--openapi PATH or --fetch-openapi): the Edge openapi.yaml the
   plugin catalog pins has the recorded sha256, and every config_schema
   pointer names a component schema in it. --fetch-openapi downloads that
   file from raw.githubusercontent.com at the pinned commit.

Exit status is 0 when every check passes and 1 otherwise. Only the Python
standard library and the pinned packages in ci/requirements.txt are used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

BASE = "https://github.com/ferrum-edge/ferrum-contracts/schemas"
META = "https://json-schema.org/draft/2020-12/schema"
SCHEMA_FILE = re.compile(r"^v([1-9][0-9]*)\.schema\.json$")
NAME = re.compile(r"^[a-z][a-z0-9-]*$")

# (fixture set, target schema name, JSON pointer fragment inside the target)
CROSS_CHECKS = [
    ("diagnostic-finding", "diagnostic-report", "#/$defs/Finding"),
]


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.checked = 0

    def fail(self, where: Path | str, message: str) -> None:
        self.errors.append(f"{where}: {message}")

    def ok(self) -> None:
        self.checked += 1


def load_json(path: Path, report: Report):
    def no_duplicates(pairs):
        seen = {}
        for key, value in pairs:
            if key in seen:
                raise ValueError(f"duplicate key {key!r}")
            seen[key] = value
        return seen

    try:
        text = path.read_text(encoding="utf-8")
        return json.loads(text, object_pairs_hook=no_duplicates)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        report.fail(path, f"not valid JSON: {exc}")
        return None


def first_error(validator: Draft202012Validator, instance) -> str | None:
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
    if not errors:
        return None
    err = errors[0]
    location = "/".join(str(p) for p in err.absolute_path) or "(root)"
    more = f" (+{len(errors) - 1} more)" if len(errors) > 1 else ""
    return f"at {location}: {err.message}{more}"


def load_schemas(root: Path, report: Report) -> dict[str, dict[int, dict]]:
    schemas: dict[str, dict[int, dict]] = {}
    schema_root = root / "schemas"
    for entry in sorted(schema_root.iterdir()):
        if not entry.is_dir():
            report.fail(entry, "only schema directories may live under schemas/")
            continue
        name = entry.name
        if not NAME.match(name):
            report.fail(entry, "schema directory names are lowercase kebab-case")
        for path in sorted(entry.iterdir()):
            match = SCHEMA_FILE.match(path.name)
            if not match:
                report.fail(path, "schema files are named v<N>.schema.json")
                continue
            version = int(match.group(1))
            schema = load_json(path, report)
            if schema is None:
                continue
            if schema.get("$schema") != META:
                report.fail(path, f"$schema must be {META}")
            expected_id = f"{BASE}/{name}/v{version}.schema.json"
            if schema.get("$id") != expected_id:
                report.fail(path, f"$id must be {expected_id}, found {schema.get('$id')!r}")
            contract = schema.get("x-contract")
            if not isinstance(contract, dict):
                report.fail(path, "missing x-contract object")
            else:
                if contract.get("name") != name:
                    report.fail(path, f"x-contract.name must be {name!r}")
                if contract.get("version") != version:
                    report.fail(path, f"x-contract.version must be {version}")
                if contract.get("status") not in ("implemented", "proposed"):
                    report.fail(path, "x-contract.status must be implemented or proposed")
                if not contract.get("owner"):
                    report.fail(path, "x-contract.owner is required")
            try:
                Draft202012Validator.check_schema(schema)
            except Exception as exc:  # jsonschema.SchemaError
                report.fail(path, f"not a valid 2020-12 schema: {exc}")
                continue
            schemas.setdefault(name, {})[version] = schema
            report.ok()
        if name not in schemas:
            report.fail(entry, "directory holds no valid schema")
    return schemas


def build_registry(schemas: dict[str, dict[int, dict]]) -> Registry:
    resources = []
    for versions in schemas.values():
        for schema in versions.values():
            resources.append((schema["$id"], Resource.from_contents(schema)))
    return Registry().with_resources(resources)


def validator(schema: dict, registry: Registry) -> Draft202012Validator:
    return Draft202012Validator(schema, registry=registry)


def check_fixtures(root: Path, schemas, registry, report: Report) -> None:
    fixture_root = root / "fixtures"
    seen = set()
    for entry in sorted(fixture_root.iterdir()):
        if not entry.is_dir():
            if entry.name != "README.md":
                report.fail(entry, "unexpected file under fixtures/")
            continue
        name = entry.name
        seen.add(name)
        if name not in schemas:
            report.fail(entry, f"no schema named {name!r}")
            continue
        latest = max(schemas[name])
        v = validator(schemas[name][latest], registry)
        for sub in sorted(entry.iterdir()):
            if sub.name not in ("valid", "invalid") or not sub.is_dir():
                report.fail(sub, "fixture sets contain only valid/ and invalid/")
        for kind in ("valid", "invalid"):
            files = sorted((entry / kind).glob("*.json")) if (entry / kind).is_dir() else []
            if not files:
                report.fail(entry, f"needs at least one {kind} fixture")
            for path in files:
                instance = load_json(path, report)
                if instance is None:
                    continue
                error = first_error(v, instance)
                if kind == "valid" and error:
                    report.fail(path, f"valid fixture fails {name} v{latest} {error}")
                elif kind == "invalid" and not error:
                    report.fail(path, f"invalid fixture passes {name} v{latest}")
                else:
                    report.ok()
                    if kind == "invalid":
                        print(f"  ok (rejected) {path.relative_to(root)}: {error}")
    for name in schemas:
        if name not in seen:
            report.fail(f"fixtures/{name}", "schema has no fixture set")


def check_cross(root: Path, schemas, registry, report: Report) -> None:
    for fixture_set, target, fragment in CROSS_CHECKS:
        if target not in schemas:
            report.fail(f"cross-check {fixture_set}->{target}", "target schema missing")
            continue
        target_id = schemas[target][max(schemas[target])]["$id"]
        v = validator({"$ref": target_id + fragment}, registry)
        for path in sorted((root / "fixtures" / fixture_set / "valid").glob("*.json")):
            instance = load_json(path, report)
            if instance is None:
                continue
            error = first_error(v, instance)
            if error:
                report.fail(path, f"valid {fixture_set} fixture fails {target}{fragment} {error}")
            else:
                report.ok()


def check_vocabularies(root: Path, schemas, registry, report: Report) -> dict[str, dict]:
    vocabularies: dict[str, dict] = {}
    for path in sorted((root / "vocabularies").iterdir()):
        if path.suffix != ".json":
            report.fail(path, "vocabularies/ holds only <name>.json files")
            continue
        name = path.stem
        doc = load_json(path, report)
        if doc is None:
            continue
        if not isinstance(doc, dict):
            report.fail(path, "a vocabulary is a JSON object")
            continue
        schema_name = f"vocabulary-{name}"
        version = doc.get("version")
        if schema_name not in schemas or version not in schemas[schema_name]:
            report.fail(path, f"no schema {schema_name} v{version}")
            continue
        schema = schemas[schema_name][version]
        if doc.get("$schema") != schema["$id"]:
            report.fail(path, f"$schema must be {schema['$id']}")
        if doc.get("vocabulary") != name:
            report.fail(path, f"vocabulary must be {name!r}")
        error = first_error(validator(schema, registry), doc)
        if error:
            report.fail(path, f"fails {schema_name} v{version} {error}")
            continue
        vocabularies[name] = doc
        report.ok()
    for schema_name, versions in schemas.items():
        if schema_name.startswith("vocabulary-"):
            name = schema_name.removeprefix("vocabulary-")
            instance = versions[max(versions)]["x-contract"].get("instance")
            if instance != f"vocabularies/{name}.json":
                report.fail(f"schemas/{schema_name}", "x-contract.instance must name its file")
            if not (root / "vocabularies" / f"{name}.json").is_file():
                report.fail(f"schemas/{schema_name}", f"missing vocabularies/{name}.json")
    return vocabularies


def unique(report: Report, where: str, values: list[str], label: str) -> None:
    seen = set()
    for value in values:
        key = value.lower()
        if key in seen:
            report.fail(where, f"duplicate {label} {value!r}")
        seen.add(key)


def check_vocabulary_consistency(vocabularies: dict[str, dict], report: Report) -> None:
    errors = vocabularies.get("gateway-errors")
    if errors:
        where = "vocabularies/gateway-errors.json"
        classes = [c["value"] for c in errors["error_classes"]]
        tokens = [t["token"] for t in errors["x_gateway_error_tokens"]]
        unique(report, where, classes, "error class")
        unique(report, where, [c["rust_variant"] for c in errors["error_classes"]], "variant")
        unique(report, where, tokens, "token")
        for c in errors["error_classes"]:
            named = [c["x_gateway_error"]]
            named += [o["token"] for o in c.get("x_gateway_error_overrides", [])]
            for token in named:
                if token not in tokens:
                    report.fail(where, f"class {c['value']} maps to unknown token {token!r}")
        surfaces = {s["values"]: s["cardinality"] for s in errors["surfaces"]}
        if surfaces.get("x_gateway_error_tokens") not in (None, len(tokens)):
            report.fail(where, "X-Gateway-Error cardinality does not match the token list")
        if surfaces.get("error_classes") not in (None, len(classes)):
            report.fail(where, "error_class cardinality does not match the class list")
        report.ok()
    headers = vocabularies.get("gateway-headers")
    if headers:
        where = "vocabularies/gateway-headers.json"
        unique(report, where, [h["name"] for h in headers["headers"]], "header")
        for h in headers["headers"]:
            ref = h.get("values", {}).get("vocabulary")
            if ref and ref not in vocabularies:
                report.fail(where, f"{h['name']} names unknown vocabulary {ref!r}")
        report.ok()
    provisioned = vocabularies.get("provisioned-by")
    if provisioned:
        where = "vocabularies/provisioned-by.json"
        unique(report, where, [v["value"] for v in provisioned["values"]], "value")
        limit = provisioned["header"]["max_length_bytes"]
        for v in provisioned["values"]:
            if len(v["value"].encode("utf-8")) > limit:
                report.fail(where, f"{v['value']!r} exceeds {limit} bytes")
        report.ok()
    catalog = vocabularies.get("plugin-catalog")
    if catalog:
        where = "vocabularies/plugin-catalog.json"
        names = [p["name"] for p in catalog["plugins"]]
        removed = [p["name"] for p in catalog["removed_plugins"]]
        unique(report, where, names + removed, "plugin name")
        report.ok()


def fetch_openapi(vocabularies: dict[str, dict], report: Report) -> bytes | None:
    catalog = vocabularies.get("plugin-catalog")
    if not catalog:
        report.fail("vocabularies/plugin-catalog.json", "missing or invalid; cannot fetch openapi")
        return None
    doc = catalog["config_schema_document"]
    repo, commit, path = doc["repo"], doc["commit"], doc["path"]
    if not (
        re.fullmatch(r"ferrum-edge/[A-Za-z0-9._-]+", repo)
        and re.fullmatch(r"[0-9a-f]{40}", commit)
        and re.fullmatch(r"[A-Za-z0-9._/-]+", path)
        and ".." not in path
    ):
        report.fail("vocabularies/plugin-catalog.json", "config_schema_document is not fetchable")
        return None
    url = f"https://raw.githubusercontent.com/{repo}/{commit}/{path}"
    print(f"  fetching {url}")
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            return response.read()
    except OSError as exc:
        report.fail(url, f"download failed: {exc}")
        return None


def check_openapi(
    openapi: str, data: bytes, vocabularies: dict[str, dict], report: Report
) -> None:
    catalog = vocabularies.get("plugin-catalog")
    if not catalog:
        report.fail(openapi, "no plugin catalog to check against")
        return
    expected = catalog["config_schema_document"]["sha256"]
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        report.fail(openapi, f"sha256 {actual} does not match the catalog's {expected}")
        return
    text = data.decode("utf-8")
    start = re.search(r"^components:\n(?:.*\n)*?^  schemas:\n", text, re.M)
    if not start:
        report.fail(openapi, "no components.schemas section")
        return
    section = text[start.end():]
    end = re.search(r"^  [A-Za-z]", section, re.M)
    section = section[: end.start()] if end else section
    components = set(re.findall(r"^    ([A-Za-z0-9]+):\s*$", section, re.M))
    for plugin in catalog["plugins"]:
        pointer = plugin["config_schema"]["pointer"]
        component = pointer.removeprefix("#/components/schemas/")
        if component not in components:
            report.fail(openapi, f"{plugin['name']}: {pointer} does not resolve")
    report.ok()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--openapi", type=Path, help="local copy of the pinned Edge openapi.yaml")
    source.add_argument(
        "--fetch-openapi",
        action="store_true",
        help="download the pinned Edge openapi.yaml from raw.githubusercontent.com",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    report = Report()

    print("schemas")
    schemas = load_schemas(root, report)
    registry = build_registry(schemas)
    print("fixtures")
    check_fixtures(root, schemas, registry, report)
    print("cross-contract fixtures")
    check_cross(root, schemas, registry, report)
    print("vocabularies")
    vocabularies = check_vocabularies(root, schemas, registry, report)
    check_vocabulary_consistency(vocabularies, report)
    if args.openapi or args.fetch_openapi:
        print("plugin config schema pointers")
        if args.openapi:
            data, label = args.openapi.read_bytes(), str(args.openapi)
        else:
            data, label = fetch_openapi(vocabularies, report), "pinned openapi.yaml"
        if data is not None:
            check_openapi(label, data, vocabularies, report)

    if report.errors:
        print(f"\n{len(report.errors)} problem(s):", file=sys.stderr)
        for error in report.errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print(f"\nall {report.checked} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
