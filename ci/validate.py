#!/usr/bin/env python3
"""Validate the ferrum-contracts repository.

Checks, in order:

1. Layout: every schema lives at schemas/<name>/v<N>.schema.json, its `$id`
   is BASE/<name>/v<N>.schema.json, and its `x-contract` block names the same
   <name> and <N>.
2. Every schema is valid against the JSON Schema 2020-12 meta-schema.
3. Fixtures: every file under fixtures/<name>/valid/ must validate against
   schema <name>, and every file under fixtures/<name>/invalid/ must fail it
   with exactly one top-level error whose instance path and keyword (or
   those of an error nested under it) match the entry in
   fixtures/invalid-expectations.json; an entry may also pin the top-level
   keyword with `top_keyword`. A schema with several majors keeps its
   fixtures in fixtures/<name>/v<N>/{valid,invalid}/, one directory per
   major, each checked against that major. Each fixture set needs at least
   one of each; any other file in valid/ or invalid/ fails.
   Formats are asserted (date-time needs the pinned rfc3339-validator).
4. Vocabularies: every vocabularies/<v>.json validates against the schema its
   `$schema` names, which must be schemas/vocabulary-<v>/v<version>.
5. Vocabulary consistency checks that JSON Schema cannot express (unique
   values, cross-references between vocabularies, required cardinality
   surfaces), and values copied from a vocabulary into a schema (the
   diagnostic-ref gateway_error enum and ref / replica_id patterns).
6. Cross-contract fixture checks (for example: every valid Anvil
   DiagnosticFinding fixture is also a valid Alloy diagnostic_report Finding).
7. Optional (--openapi PATH or --fetch-openapi): the Edge openapi.yaml the
   plugin catalog pins has the recorded sha256, and every plugin's
   config_schema pointer is the component that Edge's PluginConfigBase
   if/then block for that plugin_name references (and the component
   exists). --fetch-openapi downloads that file from
   raw.githubusercontent.com at the pinned commit.

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
VERSION_DIR = re.compile(r"^v([1-9][0-9]*)$")
NAME = re.compile(r"^[a-z][a-z0-9-]*$")
EXPECTATIONS = "invalid-expectations.json"
FORMAT_CHECKER = Draft202012Validator.FORMAT_CHECKER
# Every format the JSON Schema 2020-12 validation spec defines. A schema may
# use a standard format only if this validator has a checker for it; otherwise
# the keyword silently degrades to an annotation. Formats outside this set
# (Anvil's generated `uint32`, for example) are annotations by design. The
# formats the schemas actually use are collected and checked in
# check_formats().
STANDARD_FORMATS = frozenset(
    {
        "date",
        "date-time",
        "duration",
        "email",
        "hostname",
        "idn-email",
        "idn-hostname",
        "ipv4",
        "ipv6",
        "iri",
        "iri-reference",
        "json-pointer",
        "regex",
        "relative-json-pointer",
        "time",
        "uri",
        "uri-reference",
        "uri-template",
        "uuid",
    }
)

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


def describe(errors) -> str:
    errors = sorted(errors, key=lambda e: list(map(str, e.absolute_path)))
    err = errors[0]
    location = pointer(err.absolute_path) or "(root)"
    more = f" (+{len(errors) - 1} more)" if len(errors) > 1 else ""
    return f"{err.validator} at {location}: {err.message}{more}"


def first_error(validator: Draft202012Validator, instance) -> str | None:
    errors = list(validator.iter_errors(instance))
    return describe(errors) if errors else None


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


def collect_formats(node) -> set[str]:
    """Every `format` keyword value anywhere in a schema."""
    formats: set[str] = set()
    if isinstance(node, dict):
        value = node.get("format")
        if isinstance(value, str):
            formats.add(value)
        for child in node.values():
            formats |= collect_formats(child)
    elif isinstance(node, list):
        for child in node:
            formats |= collect_formats(child)
    return formats


def check_formats(schemas: dict[str, dict[int, dict]], report: Report) -> None:
    """Fail closed on a standard format this validator cannot assert."""
    files: dict[str, set[str]] = {}
    for name, versions in schemas.items():
        for version, schema in versions.items():
            where = f"schemas/{name}/v{version}.schema.json"
            for fmt in collect_formats(schema):
                files.setdefault(fmt, set()).add(where)
    for fmt in sorted(set(files) & STANDARD_FORMATS):
        if fmt in FORMAT_CHECKER.checkers:
            report.ok()
            continue
        for where in sorted(files[fmt]):
            report.fail(
                where,
                f"format {fmt!r} is a JSON Schema 2020-12 format but no checker is "
                f"registered; install the dependency that provides it (ci/requirements.txt)",
            )


def build_registry(schemas: dict[str, dict[int, dict]]) -> Registry:
    resources = []
    for versions in schemas.values():
        for schema in versions.values():
            resources.append((schema["$id"], Resource.from_contents(schema)))
    return Registry().with_resources(resources)


def validator(schema: dict, registry: Registry) -> Draft202012Validator:
    return Draft202012Validator(schema, registry=registry, format_checker=FORMAT_CHECKER)


def pointer(path) -> str:
    """JSON Pointer (RFC 6901) for a jsonschema error path; "" is the root."""
    return "".join("/" + str(p).replace("~", "~0").replace("/", "~1") for p in path)


def error_tree(error):
    yield error
    for child in error.context or ():
        yield from error_tree(child)


def load_expectations(root: Path, report: Report) -> dict[str, dict]:
    path = root / "fixtures" / EXPECTATIONS
    data = load_json(path, report) if path.is_file() else None
    if not isinstance(data, dict):
        report.fail(path, "missing or not a JSON object")
        return {}
    required = {"instance_path", "keyword"}
    allowed = required | {"top_keyword"}
    for key, value in data.items():
        if (
            not isinstance(value, dict)
            or not required <= set(value)
            or not set(value) <= allowed
            or not all(isinstance(v, str) for v in value.values())
        ):
            report.fail(
                path,
                f"{key}: needs instance_path and keyword strings, "
                f"and an optional top_keyword string",
            )
    return data


def fixture_sets(entry: Path, name: str, versions, report: Report) -> list[tuple[Path, int]]:
    """(directory holding valid/ and invalid/, schema major) pairs for one fixture set.

    A schema with one major keeps fixtures/<name>/{valid,invalid}/, checked
    against that major. A schema with several majors keeps
    fixtures/<name>/v<N>/{valid,invalid}/ for every major N.
    """
    if len(versions) == 1:
        for sub in sorted(entry.iterdir()):
            if sub.name not in ("valid", "invalid") or not sub.is_dir():
                report.fail(sub, "fixture sets contain only valid/ and invalid/")
        return [(entry, max(versions))]
    sets = []
    for sub in sorted(entry.iterdir()):
        match = VERSION_DIR.match(sub.name)
        if not (sub.is_dir() and match and int(match.group(1)) in versions):
            report.fail(sub, f"{name} has several majors; fixtures live only in v<N>/ per major")
            continue
        for kind in sorted(sub.iterdir()):
            if kind.name not in ("valid", "invalid") or not kind.is_dir():
                report.fail(kind, "fixture sets contain only valid/ and invalid/")
        sets.append((sub, int(match.group(1))))
    for version in sorted(set(versions) - {major for _, major in sets}):
        report.fail(entry / f"v{version}", f"{name} v{version} has no fixtures")
    return sets


def check_fixtures(root: Path, schemas, registry, report: Report) -> None:
    fixture_root = root / "fixtures"
    expectations = load_expectations(root, report)
    used = set()
    seen = set()
    for entry in sorted(fixture_root.iterdir()):
        if not entry.is_dir():
            if entry.name not in ("README.md", EXPECTATIONS):
                report.fail(entry, "unexpected file under fixtures/")
            continue
        name = entry.name
        seen.add(name)
        if name not in schemas:
            report.fail(entry, f"no schema named {name!r}")
            continue
        for fixture_dir, version in fixture_sets(entry, name, schemas[name], report):
            v = validator(schemas[name][version], registry)
            check_fixture_dir(
                fixture_root, fixture_dir, name, version, v, expectations, used, report
            )
    for key in sorted(set(expectations) - used):
        report.fail(fixture_root / EXPECTATIONS, f"{key} names no invalid fixture")
    for name in schemas:
        if name not in seen:
            report.fail(f"fixtures/{name}", "schema has no fixture set")


def check_fixture_dir(
    fixture_root: Path,
    entry: Path,
    name: str,
    version: int,
    v: Draft202012Validator,
    expectations: dict[str, dict],
    used: set[str],
    report: Report,
) -> None:
    for kind in ("valid", "invalid"):
        directory = entry / kind
        files = []
        if directory.is_dir():
            for path in sorted(directory.iterdir()):
                if path.is_file() and path.suffix == ".json":
                    files.append(path)
                else:
                    report.fail(path, f"{kind}/ holds only *.json fixture files")
        if not files:
            report.fail(entry, f"needs at least one {kind} fixture")
        for path in files:
            instance = load_json(path, report)
            if instance is None:
                continue
            errors = list(v.iter_errors(instance))
            rel = path.relative_to(fixture_root).as_posix()
            if kind == "valid":
                if errors:
                    detail = describe(errors)
                    report.fail(path, f"valid fixture fails {name} v{version} {detail}")
                else:
                    report.ok()
                continue
            used.add(rel)
            expected = expectations.get(rel)
            if not errors:
                report.fail(path, f"invalid fixture passes {name} v{version}")
            elif expected is None:
                detail = describe(errors)
                report.fail(path, f"no entry in fixtures/{EXPECTATIONS}; got {detail}")
            elif len(errors) != 1:
                report.fail(path, f"expected one error, got {len(errors)}: {describe(errors)}")
            elif not any(
                pointer(e.absolute_path) == expected["instance_path"]
                and e.validator == expected["keyword"]
                for e in error_tree(errors[0])
            ):
                report.fail(
                    path,
                    f"expected {expected['keyword']!r} at {expected['instance_path']!r}, "
                    f"got {describe(errors)}",
                )
            elif (
                expected.get("top_keyword") is not None
                and errors[0].validator != expected["top_keyword"]
            ):
                report.fail(
                    path,
                    f"expected top-level {expected['top_keyword']!r}, "
                    f"got {errors[0].validator!r}: {describe(errors)}",
                )
            else:
                report.ok()
                print(f"  ok (rejected) {rel}: {describe(errors)}")


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
        surfaces: dict[str, int] = {}
        for entry in errors["surfaces"]:
            surface = entry["surface"]
            if surface in surfaces:
                report.fail(where, f"duplicate cardinality surface {surface!r}")
                continue
            surfaces[surface] = entry["cardinality"]
        metric_tokens = [
            t for t in errors["x_gateway_error_tokens"] if t["metric_label_without_error_class"]
        ]
        required = {
            "X-Gateway-Error response header": len(tokens),
            "access-log error_class": len(classes),
            "ferrum_requests_total{error_class}": len(classes) + len(metric_tokens),
        }
        for surface, count in required.items():
            if surface not in surfaces:
                report.fail(where, f"missing cardinality surface {surface!r}")
            elif surfaces[surface] != count:
                report.fail(where, f"{surface} cardinality {surfaces[surface]} != {count}")
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


def check_copied_values(schemas, vocabularies: dict[str, dict], report: Report) -> None:
    """Values a schema copies from a vocabulary must match it exactly."""
    ref_schema = schemas.get("diagnostic-ref", {}).get(1)
    errors = vocabularies.get("gateway-errors")
    headers = vocabularies.get("gateway-headers")
    where = "schemas/diagnostic-ref/v1.schema.json"
    if not (ref_schema and errors and headers):
        report.fail(where, "diagnostic-ref v1, gateway-errors or gateway-headers is missing")
        return
    props = ref_schema["properties"]
    tokens = [t["token"] for t in errors["x_gateway_error_tokens"]]
    enum = props["gateway_error"].get("enum", [])
    if None not in enum:
        report.fail(where, "gateway_error enum must allow null")
    if sorted(e for e in enum if e is not None) != sorted(tokens):
        report.fail(where, f"gateway_error enum {enum} != gateway-errors tokens {tokens}")
    by_name = {h["name"].lower(): h for h in headers["headers"]}
    pairs = [
        ("ref", "x-ferrum-diagnostic-ref"),
        ("replica_id", "x-ferrum-diagnostic-owner-replica"),
    ]
    for prop, header in pairs:
        expected = by_name.get(header, {}).get("values", {}).get("pattern")
        if expected is None:
            report.fail("vocabularies/gateway-headers.json", f"{header} has no values.pattern")
        elif props[prop].get("pattern") != expected:
            report.fail(where, f"{prop} pattern != {header} pattern {expected!r}")
    report.ok()


def plugin_config_refs(text: str, report: Report, label: str) -> dict[str, str]:
    """plugin_name -> component referenced by Edge's PluginConfigBase if/then blocks."""
    lines = text.split("\n")
    try:
        start = lines.index("    PluginConfigBase:")
    except ValueError:
        report.fail(label, "no components.schemas.PluginConfigBase")
        return {}
    refs: dict[str, str] = {}
    current = None
    previous = ""
    for line in lines[start + 1 :]:
        if re.match(r"^    [A-Za-z]", line):
            break
        stripped = line.strip()
        const = re.fullmatch(r"const: ([A-Za-z0-9_]+)", stripped)
        if const and previous == "plugin_name:":
            current = [const.group(1), None]
        ref = re.fullmatch(r'\$ref: "#/components/schemas/([A-Za-z0-9]+)"', stripped)
        if ref and current and current[1] is None:
            current[1] = ref.group(1)
            name = current[0]
            if name in refs and refs[name] != current[1]:
                report.fail(label, f"{name} references both {refs[name]} and {current[1]}")
            refs.setdefault(name, current[1])
        if stripped:
            previous = stripped
    if not refs:
        report.fail(label, "PluginConfigBase has no plugin_name if/then blocks")
    return refs


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
    refs = plugin_config_refs(text, report, openapi)
    names = set()
    for plugin in catalog["plugins"]:
        names.add(plugin["name"])
        target = plugin["config_schema"]["pointer"]
        component = target.removeprefix("#/components/schemas/")
        if component not in components:
            report.fail(openapi, f"{plugin['name']}: {target} does not resolve")
        if refs.get(plugin["name"]) != component:
            report.fail(
                openapi,
                f"{plugin['name']}: PluginConfigBase references {refs.get(plugin['name'])!r}, "
                f"catalog has {component!r}",
            )
    for name in sorted(set(refs) - names):
        report.fail(openapi, f"PluginConfigBase names {name!r}, which the catalog lacks")
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
    check_formats(schemas, report)
    registry = build_registry(schemas)
    print("fixtures")
    check_fixtures(root, schemas, registry, report)
    print("cross-contract fixtures")
    check_cross(root, schemas, registry, report)
    print("vocabularies")
    vocabularies = check_vocabularies(root, schemas, registry, report)
    check_vocabulary_consistency(vocabularies, report)
    check_copied_values(schemas, vocabularies, report)
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
