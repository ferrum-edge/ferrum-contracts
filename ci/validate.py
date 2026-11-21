#!/usr/bin/env python3
"""Validate the ferrum-contracts repository.

Checks, in order:

1. Layout: every schema lives at schemas/<name>/v<N>.schema.json, its `$id`
   is BASE/<name>/v<N>.schema.json, and its `x-contract` block names the same
   <name> and <N>, a status and an owner. A schema whose owner is not this
   repository also lists its `provenance`: repo, path and full commit SHA.
   No Edge `ref` in `x-contract` names an unpublished Edge tag.
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
   `$schema` names, which must be schemas/vocabulary-<v>/v<version>, and
   every major of schemas/vocabulary-<v> names vocabularies/<v>.json as its
   `x-contract.instance`.
5. Vocabulary consistency checks that JSON Schema cannot express (unique
   values, cross-references between vocabularies, required cardinality
   surfaces, a gateway-headers availability that is a published Edge
   release no later than edge_release, no `edge_release`,
   `available_since` or Edge source `ref` naming an unpublished Edge tag),
   and values copied from a vocabulary into a schema (the diagnostic-ref
   gateway_error enum, detail.rejection_phase enum and ref / replica_id
   patterns).
6. Cross-contract fixture checks (for example: every valid Anvil
   DiagnosticFinding fixture is also a valid Alloy diagnostic_report Finding).
   The valid fixtures of every major are checked, wherever the layout of
   step 3 puts them; a cross-check with no valid fixture fails.
7. Qualification cases: every qualification/<name>/v<N>/<case-set>.json
   names contract <name> and integer contract_version <N> (a schema that
   exists), the producer revision it was derived from (repo, paths and a
   full commit SHA), a known `rule`, and a non-empty list of cases with
   unique ids. Each case's `instance` must pass schema <name> v<N> exactly
   when `schema_valid` is true. For the `alloy-derived-resource-id-limit`
   rule, every case is schema-valid and equals the set's `base` (the one
   reviewed exportable fixture for that contract major) except for gateway proxy_id and correlation_id (and the
   optional removal of otel_endpoint and otel_root_sampling_ratio);
   the effective proxy ID must match Alloy's valid_id grammar,
   `derived_resource_ids` must be exactly the IDs Alloy derives from the
   instance, `edge_resource_id_max_length` must be 254, and
   `producer_exports` must be true exactly when every derived ID fits.
   These cases record producer outcomes the schema cannot express; they are
   not fixtures.
8. Optional (--openapi PATH or --fetch-openapi): the Edge openapi.yaml the
   plugin catalog pins has the recorded sha256, and every plugin's
   config_schema pointer is the component that Edge's PluginConfigBase
   if/then block for that plugin_name references (and the component
   exists). --fetch-openapi downloads that file from
   raw.githubusercontent.com at the pinned commit. Each plugin's
   config_required_when_enabled and scope_constraint must also match what
   PluginConfigBase requires of it; every if/then item is read on its own.
   The download refuses redirects and stops at MAX_OPENAPI_BYTES, so an
   oversized response fails before it is buffered whole or hashed;
   --openapi applies the same cap.

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
# Pinned Edge openapi.yaml structure (plugin_config_rules, check_openapi).
_SCHEMA_ENTRY_RE = re.compile(r"^    [A-Za-z]")
_PLUGIN_NAME_CONST_RE = re.compile(r"const: ([A-Za-z0-9_]+)")
_COMPONENT_REF_RE = re.compile(r'\$ref: "#/components/schemas/([A-Za-z0-9]+)"')
_COMPONENTS_SCHEMAS_RE = re.compile(r"^components:\n(?:.*\n)*?^  schemas:\n", re.M)
_NEXT_COMPONENTS_KEY_RE = re.compile(r"^  [A-Za-z]", re.M)
_SCHEMA_NAME_RE = re.compile(r"^    ([A-Za-z0-9]+):\s*$", re.M)
# config_schema_document fields that may be fetched (fetch_openapi).
_FETCH_REPO_RE = re.compile(r"ferrum-edge/[A-Za-z0-9._-]+")
_FETCH_COMMIT_RE = re.compile(r"[0-9a-f]{40}")
_FETCH_PATH_RE = re.compile(r"[A-Za-z0-9._/-]+")
EXPECTATIONS = "invalid-expectations.json"
# Edge tags with no published release (docs/versioning.md). A gateway-headers
# `availability` names the first published release, never one of these, and
# no other Edge release field (EDGE_TAG_KEYS) names one either.
UNPUBLISHED_EDGE_TAGS = frozenset(
    {"v0.9.0", "v0.9.1", "v0.9.2", "v0.9.3", "v0.9.6", "v0.9.16", "v0.9.18"}
)
EDGE_REPO = "ferrum-edge/ferrum-edge"
# Keys whose tag-shaped value names an Edge release: the release a vocabulary
# was read from, the first release that has a value, and the tag a source was
# read at (a `ref` inside an object naming another `repo` is that repo's tag).
# A gateway-headers `availability` is checked by check_header_availability.
EDGE_TAG_KEYS = frozenset({"edge_release", "available_since", "ref"})
_EDGE_TAG_RE = re.compile(r"v[0-9]+\.[0-9]+\.[0-9]+")
# Schemas this repository owns (the vocabulary shapes) transcribe no other
# repository; every other schema records where its content was read.
CONTRACTS_REPO = "ferrum-edge/ferrum-contracts"
_PROVENANCE_COMMIT_RE = re.compile(r"[0-9a-f]{40}")
# Upper bound for the pinned Edge openapi.yaml, downloaded or local. The real
# file is a small fraction of this; a response that reaches it is not the
# pinned document, and reading it whole would only exhaust the runner.
MAX_OPENAPI_BYTES = 32 * 1024 * 1024
DOWNLOAD_CHUNK_BYTES = 64 * 1024
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
                check_provenance(path, contract, report)
                check_edge_tags(path, contract, report, "/x-contract")
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


def check_provenance(path: Path, contract: dict, report: Report) -> None:
    """A schema owned by another repository names the sources it was read from.

    `x-contract.provenance` is a non-empty list; each entry names `repo`,
    `path` and the full 40-hex `commit`. Schemas owned by this repository
    may carry provenance and are not required to.
    """
    if contract.get("owner") == CONTRACTS_REPO:
        return
    provenance = contract.get("provenance")
    if not isinstance(provenance, list) or not provenance:
        report.fail(path, "x-contract.provenance must be a non-empty list")
        return
    for index, entry in enumerate(provenance):
        where = f"x-contract.provenance[{index}]"
        if not isinstance(entry, dict):
            report.fail(path, f"{where} must be an object")
            continue
        for key in ("repo", "path"):
            if not isinstance(entry.get(key), str) or not entry[key]:
                report.fail(path, f"{where}.{key} is required")
        commit = entry.get("commit")
        if not isinstance(commit, str) or not _PROVENANCE_COMMIT_RE.fullmatch(commit):
            report.fail(path, f"{where}.commit must be a full 40-hex commit SHA")


def edge_tags(node, location: str = ""):
    """(JSON pointer, tag) for every EDGE_TAG_KEYS value that names an Edge tag.

    Values that are not tag-shaped (`main`, a commit) are skipped, and so is
    the `ref` of an object whose `repo` is not Edge: that is another
    repository's tag.
    """
    if isinstance(node, dict):
        other_repo = "repo" in node and node["repo"] != EDGE_REPO
        for key, value in node.items():
            here = f"{location}/{key}"
            if (
                key in EDGE_TAG_KEYS
                and isinstance(value, str)
                and _EDGE_TAG_RE.fullmatch(value)
                and not (key == "ref" and other_repo)
            ):
                yield here, value
            else:
                yield from edge_tags(value, here)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from edge_tags(value, f"{location}/{index}")


def check_edge_tags(where: Path | str, node, report: Report, location: str = "") -> None:
    """No Edge release field names a tag that was never published."""
    for here, tag in edge_tags(node, location):
        if tag in UNPUBLISHED_EDGE_TAGS:
            report.fail(where, f"{here} names Edge {tag}, which was never published")


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


def check_fixtures(
    root: Path, schemas, registry, report: Report
) -> dict[str, list[tuple[Path, int]]]:
    """Check every fixture set; return each set's (directory, major) pairs for check_cross."""
    fixture_root = root / "fixtures"
    expectations = load_expectations(root, report)
    used = set()
    seen = set()
    sets_by_name: dict[str, list[tuple[Path, int]]] = {}
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
        sets_by_name[name] = fixture_sets(entry, name, schemas[name], report)
        for fixture_dir, version in sets_by_name[name]:
            v = validator(schemas[name][version], registry)
            check_fixture_dir(
                fixture_root, fixture_dir, name, version, v, expectations, used, report
            )
    for key in sorted(set(expectations) - used):
        report.fail(fixture_root / EXPECTATIONS, f"{key} names no invalid fixture")
    for name in schemas:
        if name not in seen:
            report.fail(f"fixtures/{name}", "schema has no fixture set")
    return sets_by_name


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


def check_cross(
    schemas, registry, fixture_sets_by_name: dict[str, list[tuple[Path, int]]], report: Report
) -> None:
    """Every valid fixture of every major of a set must also pass the target fragment.

    Fixture directories come from check_fixtures (fixture_sets owns the layout),
    and a cross-check that finds no valid fixture fails rather than passing vacuously.
    """
    for fixture_set, target, fragment in CROSS_CHECKS:
        where = f"cross-check {fixture_set}->{target}"
        if target not in schemas:
            report.fail(where, "target schema missing")
            continue
        target_id = schemas[target][max(schemas[target])]["$id"]
        v = validator({"$ref": target_id + fragment}, registry)
        paths = [
            path
            for fixture_dir, _ in fixture_sets_by_name.get(fixture_set, [])
            for path in sorted((fixture_dir / "valid").glob("*.json"))
        ]
        if not paths:
            report.fail(where, f"no valid {fixture_set} fixture to check")
            continue
        for path in paths:
            instance = load_json(path, report)
            if instance is None:
                continue
            error = first_error(v, instance)
            if error:
                report.fail(path, f"valid {fixture_set} fixture fails {target}{fragment} {error}")
            else:
                report.ok()


QUALIFICATION_DIR = "qualification"

# Alloy's derived resource ID rule (ferrum-alloy crates/ferrum-alloy-edge at
# db412da37564ffbe869e2b40530dbebf5afe7ac8: manifest.rs
# EDGE_RESOURCE_ID_MAX_LENGTH and ServiceManifest::validate, export.rs
# resources and the *_SUFFIX constants). Edge's MAX_ID_LENGTH is the same 254.
# The export generates, in this order, `<proxy_id>-upstream` when `health` is
# set, `<proxy_id>-correlation-id` when `gateway.correlation_id` is true (the
# default), and `<proxy_id>-otel-tracing` always.
ALLOY_DERIVED_ID_RULE = "alloy-derived-resource-id-limit"
ALLOY_RESOURCE_ID_MAX_LENGTH = 254


def check_qualifications(root: Path, schemas, registry, report: Report) -> None:
    """Check qualification/<name>/v<N>/*.json case sets (step 7 of the module docstring)."""
    qualification_root = root / QUALIFICATION_DIR
    if not qualification_root.is_dir():
        report.fail(qualification_root, f"missing {QUALIFICATION_DIR}/ directory")
        return
    entries = sorted(qualification_root.iterdir())
    if not any(entry.is_dir() for entry in entries):
        report.fail(qualification_root, "no qualification case sets")
    for entry in entries:
        if not entry.is_dir():
            if entry.name != "README.md":
                report.fail(entry, f"unexpected file under {QUALIFICATION_DIR}/")
            continue
        name = entry.name
        if name not in schemas:
            report.fail(entry, f"no schema named {name!r}")
            continue
        subs = sorted(entry.iterdir())
        if not subs:
            report.fail(entry, "an empty qualification directory")
        for sub in subs:
            match = VERSION_DIR.match(sub.name)
            if not (sub.is_dir() and match and int(match.group(1)) in schemas[name]):
                report.fail(sub, f"{name} qualification cases live only in v<N>/ for an existing major")
                continue
            version = int(match.group(1))
            paths = sorted(sub.iterdir())
            if not paths:
                report.fail(sub, "an empty qualification directory")
            for path in paths:
                if path.suffix != ".json" or not path.is_file():
                    report.fail(path, "qualification directories hold only <case-set>.json files")
                    continue
                check_qualification_file(root, path, name, version, schemas, registry, report)


def check_qualification_file(
    root: Path, path: Path, name: str, version: int, schemas, registry, report: Report
) -> None:
    failures = len(report.errors)
    doc = load_json(path, report)
    if not isinstance(doc, dict):
        if len(report.errors) == failures:
            report.fail(path, "a qualification case set is a JSON object")
        return
    contract_version = doc.get("contract_version")
    if (
        doc.get("contract") != name
        or not isinstance(contract_version, int)
        or isinstance(contract_version, bool)
        or contract_version != version
    ):
        report.fail(path, f"contract and contract_version must be {name!r} and {version}")
    producer = doc.get("producer")
    if not isinstance(producer, dict):
        report.fail(path, "producer is required")
    else:
        if not isinstance(producer.get("repo"), str) or not producer["repo"]:
            report.fail(path, "producer.repo is required")
        paths = producer.get("paths")
        if not isinstance(paths, list) or not paths or not all(
            isinstance(p, str) and p for p in paths
        ):
            report.fail(path, "producer.paths must be a non-empty list of paths")
        commit = producer.get("commit")
        if not isinstance(commit, str) or not _PROVENANCE_COMMIT_RE.fullmatch(commit):
            report.fail(path, "producer.commit must be a full 40-hex commit SHA")
    rule = doc.get("rule")
    if rule != ALLOY_DERIVED_ID_RULE:
        report.fail(path, f"unknown rule {rule!r}; known: {ALLOY_DERIVED_ID_RULE!r}")
        return
    if doc.get("edge_resource_id_max_length") != ALLOY_RESOURCE_ID_MAX_LENGTH:
        report.fail(
            path,
            f"edge_resource_id_max_length must be {ALLOY_RESOURCE_ID_MAX_LENGTH}, Alloy's limit",
        )
        return
    base = load_case_base(root, doc.get("base"), name, version, path, report)
    cases = doc.get("cases")
    if not isinstance(cases, list) or not cases:
        report.fail(path, "cases must be a non-empty list")
    if len(report.errors) != failures:
        # A case set whose envelope is wrong certifies nothing; its cases
        # are not counted.
        return
    v = validator(schemas[name][version], registry)
    seen: set[str] = set()
    for index, case in enumerate(cases):
        where = f"{path}: cases[{index}]"
        if not isinstance(case, dict):
            report.fail(where, "a case is an object")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            report.fail(where, "id is required")
            continue
        if case_id in seen:
            report.fail(where, f"duplicate case id {case_id!r}")
            continue
        seen.add(case_id)
        where = f"{path}: case {case_id}"
        schema_valid = case.get("schema_valid")
        if not isinstance(schema_valid, bool):
            report.fail(where, "schema_valid must be a boolean")
            continue
        if "instance" not in case:
            report.fail(where, "instance is required")
            continue
        instance = case["instance"]
        error = first_error(v, instance)
        if schema_valid and error:
            report.fail(where, f"marked schema_valid but fails {name} v{version} {error}")
            continue
        if not schema_valid and not error:
            report.fail(where, f"marked not schema_valid but passes {name} v{version}")
            continue
        if not schema_valid:
            report.fail(where, f"{ALLOY_DERIVED_ID_RULE} cases are schema-valid manifests")
            continue
        if not check_case_variation(where, instance, base, report):
            continue
        if not check_derived_ids(where, case, report):
            continue
        report.ok()
        print(f"  ok (qualification) {path.name} {case_id}")


# Gateway fields an alloy-derived-resource-id-limit case may change from its
# base fixture. The base is a valid fixture Alloy exports, so with every
# other field equal the only remaining producer refusal is the ID limit.
ALLOY_DERIVED_ID_VARIABLE_FIELDS = ("proxy_id", "correlation_id")
ALLOY_DERIVED_ID_REMOVABLE_FIELDS = ("otel_endpoint", "otel_root_sampling_ratio")


# The one base each contract major may vary for this rule: a valid fixture
# transcribed from an Alloy manifest that Alloy exports at the cited revision
# (ferrum-alloy contracts/fixtures/manifests/plain-http.toml).
ALLOY_DERIVED_ID_BASES = {
    ("service-manifest", 1): "fixtures/service-manifest/valid/plain-http.json",
}
# Alloy's valid_id grammar (manifest.rs), matched against the whole string.
ALLOY_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


def load_case_base(root: Path, base, name: str, version: int, path: Path, report: Report):
    """The reviewed exportable fixture a case set varies (ALLOY_DERIVED_ID_BASES)."""
    allowed = ALLOY_DERIVED_ID_BASES.get((name, version))
    if allowed is None or base != allowed:
        report.fail(path, f"base must be {allowed!r}, the reviewed exportable fixture")
        return None
    doc = load_json(root / allowed, report)
    if not isinstance(doc, dict) or not isinstance(doc.get("gateway"), dict):
        report.fail(path, f"base {allowed!r} has no gateway object")
        return None
    return doc


def check_case_variation(where: str, instance, base: dict, report: Report) -> bool:
    """A case equals its base except for the gateway fields the rule varies."""
    if not isinstance(instance, dict) or not isinstance(instance.get("gateway"), dict):
        report.fail(where, "instance must be an object with a gateway object")
        return False
    rest = {k: v for k, v in instance.items() if k != "gateway"}
    base_rest = {k: v for k, v in base.items() if k != "gateway"}
    if rest != base_rest:
        report.fail(where, "instance may differ from base only in gateway")
        return False
    gateway, base_gateway = instance["gateway"], base["gateway"]
    for key in set(gateway) | set(base_gateway):
        if key in ALLOY_DERIVED_ID_VARIABLE_FIELDS:
            continue
        if key in ALLOY_DERIVED_ID_REMOVABLE_FIELDS and key not in gateway:
            continue
        if gateway.get(key, ...) != base_gateway.get(key, ...):
            report.fail(where, f"gateway.{key} may not differ from base")
            return False
    return True


def alloy_derived_ids(instance) -> list[str] | None:
    """The resource IDs Alloy derives from a manifest, or None for a shape Alloy cannot parse."""
    if not isinstance(instance, dict):
        return None
    gateway = instance.get("gateway", {})
    service = instance.get("service")
    if not isinstance(gateway, dict) or not isinstance(service, dict):
        return None
    proxy_id = gateway.get("proxy_id", service.get("name"))
    correlation = gateway.get("correlation_id", True)
    if (
        not isinstance(proxy_id, str)
        or not ALLOY_ID_RE.fullmatch(proxy_id)
        or len(proxy_id) > ALLOY_RESOURCE_ID_MAX_LENGTH
        or not isinstance(correlation, bool)
    ):
        return None
    ids = []
    if instance.get("health") is not None:
        ids.append(f"{proxy_id}-upstream")
    if correlation:
        ids.append(f"{proxy_id}-correlation-id")
    ids.append(f"{proxy_id}-otel-tracing")
    return ids


def check_derived_ids(where: str, case: dict, report: Report) -> bool:
    """derived_resource_ids are exactly Alloy's; producer_exports follows from the limit."""
    expected_ids = alloy_derived_ids(case.get("instance"))
    if expected_ids is None:
        report.fail(where, "instance has no service, gateway and valid proxy ID Alloy can derive IDs from")
        return False
    if case.get("derived_resource_ids") != expected_ids:
        report.fail(where, f"derived_resource_ids must be Alloy's {expected_ids!r}")
        return False
    exports = case.get("producer_exports")
    expected = all(len(i) <= ALLOY_RESOURCE_ID_MAX_LENGTH for i in expected_ids)
    if exports is not expected:
        report.fail(
            where,
            f"producer_exports must be {str(expected).lower()}: the longest derived ID "
            f"has {max(map(len, expected_ids))} characters and the limit is "
            f"{ALLOY_RESOURCE_ID_MAX_LENGTH}",
        )
        return False
    return True


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
            for version in sorted(versions):
                instance = versions[version]["x-contract"].get("instance")
                if instance != f"vocabularies/{name}.json":
                    report.fail(
                        f"schemas/{schema_name}/v{version}.schema.json",
                        "x-contract.instance must name its file",
                    )
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


def edge_version(tag: str) -> tuple[int, ...]:
    """`vX.Y.Z` as a comparable tuple (the vocabulary schemas fix the form)."""
    return tuple(int(part) for part in tag.removeprefix("v").split("."))


def check_header_availability(where: str, header: dict, edge_release: str, report: Report) -> None:
    """A header's availability is a published Edge release no later than the
    release the vocabulary was read from, or `unreleased`."""
    availability = header["availability"]
    if availability == "unreleased":
        return
    name = header["name"]
    if availability in UNPUBLISHED_EDGE_TAGS:
        report.fail(where, f"{name} availability {availability} was never published")
    elif edge_version(availability) > edge_version(edge_release):
        report.fail(where, f"{name} availability {availability} is after {edge_release}")


def check_vocabulary_consistency(vocabularies: dict[str, dict], report: Report) -> None:
    for name, doc in vocabularies.items():
        check_edge_tags(f"vocabularies/{name}.json", doc, report)
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
            check_header_availability(where, h, headers["edge_release"], report)
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
    # detail.rejection_phase carries token_for_rejection_phase(phase): the
    # token of every vocabulary entry that a rejection phase selects.
    phase = ref_schema.get("$defs", {}).get("Detail", {}).get("properties", {})
    phase_enum = phase.get("rejection_phase", {}).get("enum", [])
    phase_tokens = [t["token"] for t in errors["x_gateway_error_tokens"] if t["rejection_phases"]]
    if None not in phase_enum:
        report.fail(where, "detail.rejection_phase enum must allow null")
    if sorted(e for e in phase_enum if e is not None) != sorted(phase_tokens):
        report.fail(
            where,
            f"detail.rejection_phase enum {phase_enum} != gateway-errors tokens "
            f"with rejection_phases {phase_tokens}",
        )
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


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _yaml_block(lines: list[str], indent: int, key: str) -> list[str] | None:
    """Lines nested under the first `key:` line at exactly `indent`, or None."""
    for index, line in enumerate(lines):
        if line == " " * indent + key + ":":
            end = index + 1
            while end < len(lines) and (not lines[end].strip() or _indent(lines[end]) > indent):
                end += 1
            return lines[index + 1 : end]
    return None


def _yaml_scalar(lines: list[str] | None, indent: int, key: str) -> str | None:
    """The value of the first `key: value` line at exactly `indent`, or None."""
    prefix = " " * indent + key + ": "
    for line in lines or ():
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return None


_YAML_KEY_RE = re.compile(r"[A-Za-z0-9_]+")
# A mapping key written in quotes (`"required": [config]`): the reader matches
# bare keys only, so a quoted one would read as absent. It is refused instead.
_QUOTED_YAML_KEY_RE = re.compile(r"""^\s*(?:-\s+)?(?:"[^"]*"|'[^']*')\s*:""")


def _yaml_key_list(lines: list[str], indent: int, key: str) -> tuple[list[str], str | None]:
    """The YAML list of keys under the first `key` at exactly `indent`.

    Returns (keys, error). An absent `key` is an empty list. A flow list
    (`[a, "b", 'c']`) or a block list (`- a` lines, nested or at the same
    indent) is read; any other spelling is an error, never an empty list, so
    a requirement is not lost to a spelling this reader does not know.
    """
    prefix = " " * indent + key + ":"
    for index, line in enumerate(lines):
        if line != prefix and not line.startswith(prefix + " "):
            continue
        value = line[len(prefix) :].strip()
        if value:
            if not (value.startswith("[") and value.endswith("]")):
                return [], f"{key}: {value} is not a list"
            raw = [item.strip() for item in value[1:-1].split(",")]
            if raw == [""]:
                raw = []
        else:
            raw = []
            for follow in lines[index + 1 :]:
                stripped = follow.strip()
                if not stripped:
                    continue
                depth = _indent(follow)
                if depth < indent or (depth == indent and not stripped.startswith("- ")):
                    break
                if not stripped.startswith("- "):
                    return [], f"{key}: unsupported block list line {stripped!r}"
                raw.append(stripped[2:].strip())
            if not raw:
                return [], f"{key}: empty or unsupported list"
        keys = []
        for item in raw:
            if len(item) >= 2 and item[0] == item[-1] and item[0] in "'\"":
                item = item[1:-1]
            if not _YAML_KEY_RE.fullmatch(item):
                return [], f"{key}: unsupported list item {item!r}"
            keys.append(item)
        return keys, None
    return [], None


def plugin_config_rules(text: str, report: Report, label: str) -> dict[str, dict]:
    """What Edge's PluginConfigBase if/then items say about each plugin_name.

    Each `- if:` list item is read on its own, so nothing one item says leaks
    into the next. An item whose `if` names a `plugin_name` const contributes:
    `ref`, the component its `then` gives `config`; `config_required`, whether
    its `then` requires `config`; and `scope`, the const its `then` gives
    `scope`. `config` constraints apply only while the config is enabled, so
    `ref` and `config_required` count only inside the `then` of the item whose
    `if` is exactly `properties: {enabled: {not: {const: false}}}`, and an
    ungated item may only constrain `scope`. Any other `if` that tests
    `enabled`, an `else` or other key beside `then`, a quoted mapping key, and
    any `required` spelling the reader does not know, fail.
    """
    lines = text.split("\n")
    try:
        start = lines.index("    PluginConfigBase:")
    except ValueError:
        report.fail(label, "no components.schemas.PluginConfigBase")
        return {}
    end = start + 1
    while end < len(lines) and not _SCHEMA_ENTRY_RE.match(lines[end]):
        end += 1
    lines = lines[start + 1 : end]
    for index, line in enumerate(lines):
        if _QUOTED_YAML_KEY_RE.match(line):
            report.fail(
                label,
                f"PluginConfigBase line {start + 2 + index}: quoted YAML key "
                f"{line.strip()!r} is not supported",
            )

    items = []  # (first body line, end, indent of the "- if:" line)
    for index, line in enumerate(lines):
        if line.strip() == "- if:":
            depth = _indent(line)
            stop = index + 1
            while stop < len(lines) and (not lines[stop].strip() or _indent(lines[stop]) > depth):
                stop += 1
            items.append((index + 1, stop, depth))

    gates = []
    parsed = []
    for first, stop, depth in items:
        body = lines[first:stop]
        then_at = next(
            (i for i, line in enumerate(body) if line == " " * (depth + 2) + "then:"), None
        )
        if then_at is None:
            report.fail(label, f"PluginConfigBase line {start + 1 + first}: if without then")
            continue
        # `then:` is the item's only key beside `if`: an `else:` (or any other
        # sibling) would put constraints in a branch the reader cannot place,
        # so it is refused. The `then` subtree is then the rest of the item.
        siblings = [
            line.strip()
            for i, line in enumerate(body)
            if i != then_at and line.strip() and _indent(line) <= depth + 3
        ]
        if siblings:
            report.fail(
                label,
                f"PluginConfigBase line {start + 1 + first}: unsupported key "
                f"{siblings[0]!r} beside then",
            )
            continue
        condition = _yaml_block(body[:then_at], depth + 4, "properties") or []
        consequence = body[then_at + 1 :]
        if _yaml_block(condition, depth + 6, "enabled") is not None:
            gate = [
                " " * (depth + 4) + "properties:",
                " " * (depth + 6) + "enabled:",
                " " * (depth + 8) + "not:",
                " " * (depth + 10) + "const: false",
            ]
            if [line for line in body[:then_at] if line.strip()] != gate:
                report.fail(
                    label,
                    f"PluginConfigBase line {start + 1 + first}: unsupported enabled "
                    f"predicate; only `enabled: {{not: {{const: false}}}}` is understood",
                )
                continue
            gates.append((first + then_at + 1, stop))
            continue
        name = _yaml_scalar(_yaml_block(condition, depth + 6, "plugin_name"), depth + 8, "const")
        if name is None:
            continue
        if not _PLUGIN_NAME_CONST_RE.fullmatch(f"const: {name}"):
            report.fail(label, f"PluginConfigBase plugin_name const {name!r} is not a plugin name")
            continue
        required_keys, error = _yaml_key_list(consequence, depth + 4, "required")
        if error:
            report.fail(label, f"{name}: unsupported then {error}")
            continue
        props = _yaml_block(consequence, depth + 4, "properties")
        ref_line = _yaml_scalar(_yaml_block(props or [], depth + 6, "config"), depth + 8, "$ref")
        ref = _COMPONENT_REF_RE.fullmatch(f"$ref: {ref_line}") if ref_line else None
        if ref_line and not ref:
            report.fail(label, f"{name}: config $ref {ref_line} is not a component reference")
        scope = _yaml_scalar(_yaml_block(props or [], depth + 6, "scope"), depth + 8, "const")
        parsed.append(
            (first, name, ref.group(1) if ref else None, "config" in required_keys, scope)
        )

    rules: dict[str, dict] = {}
    for first, name, ref, config_required, scope in parsed:
        rule = rules.setdefault(name, {"ref": None, "config_required": False, "scope": None})
        gated = any(gate_first <= first < gate_stop for gate_first, gate_stop in gates)
        if not gated and (ref or config_required):
            report.fail(label, f"{name}: a config constraint outside the enabled gate")
        if ref:
            if rule["ref"] not in (None, ref):
                report.fail(label, f"{name} references both {rule['ref']} and {ref}")
            else:
                rule["ref"] = ref
        rule["config_required"] = rule["config_required"] or (gated and config_required)
        if scope:
            if rule["scope"] not in (None, scope):
                report.fail(label, f"{name} constrains scope to both {rule['scope']} and {scope}")
            else:
                rule["scope"] = scope
    if not rules:
        report.fail(label, "PluginConfigBase has no plugin_name if/then blocks")
    return rules


class DownloadError(OSError):
    """A download refused for its size or a redirect."""


class _RefuseRedirect(urllib.request.HTTPRedirectHandler):
    # The URL names an immutable commit; a redirect means the response is not
    # the pinned file, and following it would leave the allowlisted host.
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise DownloadError(f"refusing HTTP {code} redirect to {newurl}")


def download_capped(url: str, limit: int, timeout: float = 60) -> bytes:
    """Download `url` into memory, refusing redirects and more than `limit` bytes.

    A declared Content-Length over the limit is refused before the body is
    read. Without one, the body is read in chunks and abandoned as soon as it
    passes the limit, so at most `limit` plus one chunk is read. Memory is
    O(limit): the buffer, plus one immutable copy while it is returned.
    """
    opener = urllib.request.build_opener(_RefuseRedirect)
    with opener.open(url, timeout=timeout) as response:
        declared = (response.headers.get("Content-Length") or "").strip()
        if declared.isdigit() and int(declared) > limit:
            raise DownloadError(f"response declares {declared} bytes; the limit is {limit}")
        data = bytearray()
        while chunk := response.read(DOWNLOAD_CHUNK_BYTES):
            data += chunk
            if len(data) > limit:
                raise DownloadError(f"response exceeds the {limit} byte limit")
        return bytes(data)


def read_capped(path: Path, limit: int) -> bytes:
    """Read a local file, refusing more than `limit` bytes."""
    with path.open("rb") as handle:
        data = handle.read(limit + 1)
    if len(data) > limit:
        raise DownloadError(f"{path} exceeds the {limit} byte limit")
    return data


def fetch_openapi(vocabularies: dict[str, dict], report: Report) -> bytes | None:
    catalog = vocabularies.get("plugin-catalog")
    if not catalog:
        report.fail("vocabularies/plugin-catalog.json", "missing or invalid; cannot fetch openapi")
        return None
    doc = catalog["config_schema_document"]
    repo, commit, path = doc["repo"], doc["commit"], doc["path"]
    if not (
        _FETCH_REPO_RE.fullmatch(repo)
        and _FETCH_COMMIT_RE.fullmatch(commit)
        and _FETCH_PATH_RE.fullmatch(path)
        and ".." not in path
    ):
        report.fail("vocabularies/plugin-catalog.json", "config_schema_document is not fetchable")
        return None
    url = f"https://raw.githubusercontent.com/{repo}/{commit}/{path}"
    print(f"  fetching {url}")
    try:
        return download_capped(url, MAX_OPENAPI_BYTES)
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
    start = _COMPONENTS_SCHEMAS_RE.search(text)
    if not start:
        report.fail(openapi, "no components.schemas section")
        return
    section = text[start.end():]
    end = _NEXT_COMPONENTS_KEY_RE.search(section)
    section = section[: end.start()] if end else section
    components = set(_SCHEMA_NAME_RE.findall(section))
    rules = plugin_config_rules(text, report, openapi)
    names = set()
    for plugin in catalog["plugins"]:
        name = plugin["name"]
        names.add(name)
        config_schema = plugin["config_schema"]
        target = config_schema["pointer"]
        component = target.removeprefix("#/components/schemas/")
        if component not in components:
            report.fail(openapi, f"{name}: {target} does not resolve")
        rule = rules.get(name, {"ref": None, "config_required": False, "scope": None})
        if rule["ref"] != component:
            report.fail(
                openapi,
                f"{name}: PluginConfigBase references {rule['ref']!r}, catalog has {component!r}",
            )
        required = config_schema["config_required_when_enabled"]
        if rule["config_required"] != required:
            report.fail(
                openapi,
                f"{name}: PluginConfigBase config_required_when_enabled is "
                f"{rule['config_required']}, catalog has {required}",
            )
        scope = config_schema.get("scope_constraint")
        if rule["scope"] != scope:
            report.fail(
                openapi,
                f"{name}: PluginConfigBase scope_constraint is {rule['scope']!r}, "
                f"catalog has {scope!r}",
            )
    for name in sorted(set(rules) - names):
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
    fixture_sets_by_name = check_fixtures(root, schemas, registry, report)
    print("cross-contract fixtures")
    check_cross(schemas, registry, fixture_sets_by_name, report)
    print("vocabularies")
    vocabularies = check_vocabularies(root, schemas, registry, report)
    check_vocabulary_consistency(vocabularies, report)
    check_copied_values(schemas, vocabularies, report)
    print("qualification cases")
    check_qualifications(root, schemas, registry, report)
    if args.openapi or args.fetch_openapi:
        print("plugin config schema pointers")
        if args.openapi:
            label = str(args.openapi)
            try:
                data = read_capped(args.openapi, MAX_OPENAPI_BYTES)
            except OSError as exc:
                report.fail(label, f"read failed: {exc}")
                data = None
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
