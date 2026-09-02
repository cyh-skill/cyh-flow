#!/usr/bin/env python3
"""Validate compact review artifacts and build a master input manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
ROLES = {
    "codex-correctness",
    "ponytail-complexity",
    "differential-security",
    "integration-reliability",
}
STATUSES = {"completed", "blocked"}
DISPOSITIONS = {"verified", "known_deferred", "advisory", "rejected", "unresolved"}
CATEGORIES = {"correctness", "complexity", "security", "performance", "integration"}
CLAIM_TYPES = {
    "local-behavior",
    "state-dependent",
    "cross-boundary",
    "authorization",
    "performance",
    "complexity",
}
SPECIALIST_FIELDS = {
    "schema_version",
    "reviewer",
    "target",
    "status",
    "terminal_reason",
    "coverage",
    "candidates",
    "open_questions",
}
CANDIDATE_FIELDS = {
    "id",
    "title",
    "category",
    "claim_type",
    "path",
    "line_start",
    "line_end",
    "introduced",
    "trigger",
    "impact",
    "authority",
    "evidence_refs",
    "counterevidence",
}
MASTER_FIELDS = {
    "schema_version",
    "target",
    "status",
    "terminal_reason",
    "verified_findings",
    "dispositions",
    "impact_unexplained",
    "coverage_limits",
    "clean_eligible",
}
FINDING_FIELDS = {
    "id",
    "source_ids",
    "title",
    "priority",
    "category",
    "path",
    "line_start",
    "line_end",
    "root_cause",
    "trigger",
    "impact",
    "evidence_refs",
    "counterevidence",
    "fix_boundary",
    "reported_by",
}


class ArtifactError(ValueError):
    pass


def read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ArtifactError(f"cannot read JSON object {path}: {error}") from error
    if not isinstance(value, dict):
        raise ArtifactError(f"artifact must be a JSON object: {path}")
    return value


def require_string(value: dict[str, Any], key: str, *, nullable: bool = False) -> None:
    item = value.get(key)
    if nullable and item is None:
        return
    if not isinstance(item, str) or not item.strip():
        raise ArtifactError(f"{key} must be a non-empty string")


def require_list(value: dict[str, Any], key: str) -> list[Any]:
    item = value.get(key)
    if not isinstance(item, list):
        raise ArtifactError(f"{key} must be an array")
    return item


def reject_unknown(value: dict[str, Any], fields: set[str], label: str) -> None:
    unexpected = sorted(set(value) - fields)
    if unexpected:
        raise ArtifactError(f"{label} has unexpected fields: {unexpected}")


def require_string_list(
    value: dict[str, Any], key: str, *, allow_empty: bool = True
) -> list[str]:
    items = require_list(value, key)
    if not all(isinstance(item, str) and item.strip() for item in items):
        raise ArtifactError(f"{key} must contain non-empty strings")
    if not allow_empty and not items:
        raise ArtifactError(f"{key} cannot be empty")
    if len(items) != len(set(items)):
        raise ArtifactError(f"{key} cannot contain duplicates")
    return items


def validate_candidate(candidate: Any, reviewer: str) -> str:
    if not isinstance(candidate, dict):
        raise ArtifactError("candidate must be an object")
    reject_unknown(candidate, CANDIDATE_FIELDS, "candidate")
    for key in ("id", "title", "category", "claim_type", "path", "introduced", "trigger", "impact"):
        require_string(candidate, key)
    identifier = str(candidate["id"])
    if not identifier.startswith(f"{reviewer}:") or not identifier.removeprefix(
        f"{reviewer}:"
    ):
        raise ArtifactError(f"candidate id must start with {reviewer}:")
    if candidate["category"] not in CATEGORIES:
        raise ArtifactError("candidate category is unknown")
    if candidate["claim_type"] not in CLAIM_TYPES:
        raise ArtifactError("candidate claim_type is unknown")
    if reviewer == "ponytail-complexity" and (
        candidate["category"] != "complexity"
        or candidate["claim_type"] != "complexity"
    ):
        raise ArtifactError("ponytail candidates must be complexity claims")
    for key in ("line_start", "line_end"):
        if (
            isinstance(candidate.get(key), bool)
            or not isinstance(candidate.get(key), int)
            or candidate[key] < 1
        ):
            raise ArtifactError(f"candidate {key} must be a positive integer")
    if candidate["line_end"] < candidate["line_start"]:
        raise ArtifactError("candidate line_end precedes line_start")
    require_string_list(candidate, "evidence_refs", allow_empty=False)
    require_string_list(candidate, "counterevidence", allow_empty=False)
    authority = candidate.get("authority")
    if authority is not None and (not isinstance(authority, str) or not authority.strip()):
        raise ArtifactError("candidate authority must be a string or null")
    if candidate["claim_type"] in {"cross-boundary", "authorization"} and authority is None:
        raise ArtifactError("cross-boundary and authorization candidates require authority")
    return identifier


def validate_specialist(value: dict[str, Any]) -> dict[str, Any]:
    reject_unknown(value, SPECIALIST_FIELDS, "specialist artifact")
    if value.get("schema_version") != SCHEMA_VERSION:
        raise ArtifactError(f"schema_version must be {SCHEMA_VERSION}")
    role = value.get("reviewer")
    if role not in ROLES:
        raise ArtifactError(f"unknown reviewer role: {role}")
    require_string(value, "target")
    if value.get("status") not in STATUSES:
        raise ArtifactError("status must be completed or blocked")
    terminal = value.get("terminal_reason")
    if value["status"] == "completed" and terminal is not None:
        raise ArtifactError("completed artifact must have terminal_reason null")
    if value["status"] == "blocked" and (
        not isinstance(terminal, str) or not terminal.strip()
    ):
        raise ArtifactError("blocked artifact must include terminal_reason")
    coverage = value.get("coverage")
    if not isinstance(coverage, dict):
        raise ArtifactError("coverage must be an object")
    reject_unknown(coverage, {"inspected", "limits"}, "coverage")
    inspected = require_string_list(coverage, "inspected")
    require_string_list(coverage, "limits")
    if value["status"] == "completed" and not inspected:
        raise ArtifactError("completed artifact must record inspected coverage")
    identifiers: set[str] = set()
    for candidate in require_list(value, "candidates"):
        identifier = validate_candidate(candidate, str(role))
        if identifier in identifiers:
            raise ArtifactError(f"duplicate specialist item id: {identifier}")
        identifiers.add(identifier)
    for question in require_list(value, "open_questions"):
        if not isinstance(question, dict):
            raise ArtifactError("open question must be an object")
        reject_unknown(
            question,
            {"id", "claim", "missing", "material", "evidence_refs"},
            "open question",
        )
        for key in ("id", "claim", "missing"):
            require_string(question, key)
        identifier = str(question["id"])
        if not identifier.startswith(f"{role}:") or not identifier.removeprefix(
            f"{role}:"
        ):
            raise ArtifactError(f"open question id must start with {role}:")
        if identifier in identifiers:
            raise ArtifactError(f"duplicate specialist item id: {identifier}")
        identifiers.add(identifier)
        if question.get("material") is not True:
            raise ArtifactError("only material open questions belong in the artifact")
        require_string_list(question, "evidence_refs", allow_empty=False)
    return value


def validate_finding(value: Any) -> frozenset[str]:
    if not isinstance(value, dict):
        raise ArtifactError("verified finding must be an object")
    reject_unknown(value, FINDING_FIELDS, "verified finding")
    for key in (
        "id",
        "title",
        "priority",
        "category",
        "path",
        "root_cause",
        "trigger",
        "impact",
        "fix_boundary",
    ):
        require_string(value, key)
    if value["priority"] not in {"P0", "P1", "P2", "P3"}:
        raise ArtifactError("verified finding priority must be P0, P1, P2, or P3")
    if value["category"] not in CATEGORIES:
        raise ArtifactError("verified finding category is unknown")
    for key in ("line_start", "line_end"):
        if (
            isinstance(value.get(key), bool)
            or not isinstance(value.get(key), int)
            or value[key] < 1
        ):
            raise ArtifactError(f"verified finding {key} must be a positive integer")
    if value["line_end"] < value["line_start"]:
        raise ArtifactError("verified finding line_end precedes line_start")
    source_ids = require_string_list(value, "source_ids", allow_empty=False)
    require_string_list(value, "evidence_refs", allow_empty=False)
    require_string_list(value, "counterevidence", allow_empty=False)
    reported_by = require_string_list(value, "reported_by", allow_empty=False)
    if not set(reported_by).issubset(ROLES):
        raise ArtifactError("verified finding reported_by contains an unknown role")
    source_roles = {identifier.split(":", 1)[0] for identifier in source_ids}
    if source_roles != set(reported_by):
        raise ArtifactError("verified finding reported_by does not match source_ids")
    return frozenset(source_ids)


def validate_master(
    value: dict[str, Any],
    *,
    expected_source_ids: set[str] | None = None,
    expected_coverage_limits: set[tuple[str, str]] | None = None,
    all_lanes_completed: bool = True,
    expected_target: str | None = None,
) -> dict[str, Any]:
    reject_unknown(value, MASTER_FIELDS, "master artifact")
    if value.get("schema_version") != SCHEMA_VERSION:
        raise ArtifactError(f"schema_version must be {SCHEMA_VERSION}")
    require_string(value, "target")
    if expected_target is not None and value["target"] != expected_target:
        raise ArtifactError("master target differs from specialist manifest")
    if value.get("status") not in STATUSES:
        raise ArtifactError("status must be completed or blocked")
    terminal = value.get("terminal_reason")
    if value["status"] == "completed" and terminal is not None:
        raise ArtifactError("completed master artifact must have terminal_reason null")
    if value["status"] == "blocked" and (
        not isinstance(terminal, str) or not terminal.strip()
    ):
        raise ArtifactError("blocked master artifact must include terminal_reason")
    for key in ("verified_findings", "dispositions", "impact_unexplained", "coverage_limits"):
        require_list(value, key)
    finding_groups: list[frozenset[str]] = []
    finding_ids: set[str] = set()
    for finding in value["verified_findings"]:
        group = validate_finding(finding)
        if finding["id"] in finding_ids:
            raise ArtifactError(f"duplicate verified finding id: {finding['id']}")
        finding_ids.add(finding["id"])
        finding_groups.append(group)

    disposition_groups: list[frozenset[str]] = []
    disposition_ids: list[str] = []
    for item in value["dispositions"]:
        if not isinstance(item, dict) or item.get("disposition") not in DISPOSITIONS:
            raise ArtifactError("master disposition is malformed")
        allowed = {"source_ids", "disposition", "reason"}
        if item["disposition"] == "known_deferred":
            allowed.update({"decision_provenance", "revisit_condition"})
        reject_unknown(item, allowed, "master disposition")
        ids = require_string_list(item, "source_ids", allow_empty=False)
        if len(ids) != len(set(ids)):
            raise ArtifactError("master disposition repeats a source id")
        disposition_ids.extend(ids)
        disposition_groups.append(frozenset(ids))
        require_string(item, "reason")
        if item["disposition"] == "known_deferred":
            require_string_list(item, "decision_provenance", allow_empty=False)
            require_string(item, "revisit_condition")
    if len(disposition_ids) != len(set(disposition_ids)):
        raise ArtifactError("a source id appears in more than one master disposition")
    if expected_source_ids is not None:
        actual_source_ids = set(disposition_ids)
        if value["status"] == "completed" and actual_source_ids != expected_source_ids:
            missing = sorted(expected_source_ids - actual_source_ids)
            extra = sorted(actual_source_ids - expected_source_ids)
            raise ArtifactError(
                f"master source ids mismatch; missing={missing}, extra={extra}"
            )
        if value["status"] == "blocked" and not actual_source_ids.issubset(
            expected_source_ids
        ):
            extra = sorted(actual_source_ids - expected_source_ids)
            raise ArtifactError(f"blocked master has unknown source ids: {extra}")

    verified_groups = [
        group
        for item, group in zip(value["dispositions"], disposition_groups, strict=True)
        if item["disposition"] == "verified"
    ]
    if sorted(map(sorted, verified_groups)) != sorted(map(sorted, finding_groups)):
        raise ArtifactError("verified dispositions and verified findings do not match")

    require_string_list(value, "impact_unexplained")
    material_limits = False
    actual_coverage_limits: set[tuple[str, str]] = set()
    for limit in value["coverage_limits"]:
        if not isinstance(limit, dict):
            raise ArtifactError("coverage limit must be an object")
        reject_unknown(
            limit,
            {"source", "item", "material", "reason"},
            "coverage limit",
        )
        require_string(limit, "source")
        require_string(limit, "item")
        require_string(limit, "reason")
        if limit["source"] not in {*ROLES, "master"}:
            raise ArtifactError("coverage limit source is unknown")
        identity = (str(limit["source"]), str(limit["item"]))
        if identity in actual_coverage_limits:
            raise ArtifactError("coverage limit is duplicated")
        actual_coverage_limits.add(identity)
        if not isinstance(limit.get("material"), bool):
            raise ArtifactError("coverage limit material must be boolean")
        material_limits = material_limits or limit["material"]
    if expected_coverage_limits is not None:
        missing_limits = expected_coverage_limits - actual_coverage_limits
        if value["status"] == "completed" and missing_limits:
            raise ArtifactError(
                f"master omitted specialist coverage limits: {sorted(missing_limits)}"
            )
    if not isinstance(value.get("clean_eligible"), bool):
        raise ArtifactError("clean_eligible must be boolean")
    computed_clean = (
        value["status"] == "completed"
        and all_lanes_completed
        and not value["verified_findings"]
        and not any(
            item["disposition"] in {"verified", "unresolved"}
            for item in value["dispositions"]
        )
        and not value["impact_unexplained"]
        and not material_limits
    )
    if value["clean_eligible"] != computed_clean:
        raise ArtifactError(f"clean_eligible must be {str(computed_clean).lower()}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("x", encoding="utf-8") as handle:
            os.chmod(temporary, 0o600)
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()
def read_specialist_manifest(
    path: Path,
) -> tuple[set[str], set[tuple[str, str]], bool, str]:
    manifest = read_object(path)
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise ArtifactError(f"specialist manifest schema_version must be {SCHEMA_VERSION}")
    target = manifest.get("target")
    if not isinstance(target, str) or not target:
        raise ArtifactError("specialist manifest target is missing")
    records = require_list(manifest, "specialists")
    roles: set[str] = set()
    identifiers: set[str] = set()
    coverage_limits: set[tuple[str, str]] = set()
    all_completed = True
    for record in records:
        if not isinstance(record, dict) or record.get("reviewer") not in ROLES:
            raise ArtifactError("specialist manifest record is malformed")
        role = str(record["reviewer"])
        if role in roles:
            raise ArtifactError(f"duplicate reviewer role: {role}")
        roles.add(role)
        artifact_path = Path(str(record.get("artifact", "")))
        if not artifact_path.is_absolute():
            raise ArtifactError("specialist artifact path must be absolute")
        if sha256(artifact_path) != record.get("sha256"):
            raise ArtifactError(f"specialist artifact digest changed: {role}")
        artifact = validate_specialist(read_object(artifact_path))
        if artifact["reviewer"] != role or artifact["target"] != target:
            raise ArtifactError(f"specialist manifest identity mismatch: {role}")
        all_completed = all_completed and artifact["status"] == "completed"
        for item in [*artifact["candidates"], *artifact["open_questions"]]:
            identifier = str(item["id"])
            if identifier in identifiers:
                raise ArtifactError(f"duplicate source id across specialists: {identifier}")
            identifiers.add(identifier)
        for item in artifact["coverage"]["limits"]:
            coverage_limits.add((role, str(item)))
    if roles != ROLES:
        raise ArtifactError(f"specialist manifest roles mismatch: {sorted(roles)}")
    return identifiers, coverage_limits, all_completed, target


def validate_file(
    path: Path,
    kind: str,
    role: str | None = None,
    specialist_manifest: Path | None = None,
) -> dict[str, Any]:
    value = read_object(path)
    if kind == "specialist":
        validate_specialist(value)
        if role is not None and value["reviewer"] != role:
            raise ArtifactError(f"expected reviewer {role}, got {value['reviewer']}")
        identity = value["reviewer"]
    else:
        expected_ids: set[str] | None = None
        expected_limits: set[tuple[str, str]] | None = None
        all_completed = True
        expected_target: str | None = None
        if specialist_manifest is not None:
            (
                expected_ids,
                expected_limits,
                all_completed,
                expected_target,
            ) = read_specialist_manifest(specialist_manifest)
        validate_master(
            value,
            expected_source_ids=expected_ids,
            expected_coverage_limits=expected_limits,
            all_lanes_completed=all_completed,
            expected_target=expected_target,
        )
        identity = "master"
    return {
        "status": "valid",
        "kind": kind,
        "identity": identity,
        "artifact": str(path.resolve()),
        "sha256": sha256(path),
    }


def build_manifest(paths: list[Path], output: Path) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    roles: set[str] = set()
    target: str | None = None
    identifiers: set[str] = set()
    for path in paths:
        value = validate_specialist(read_object(path))
        role = str(value["reviewer"])
        if role in roles:
            raise ArtifactError(f"duplicate reviewer role: {role}")
        roles.add(role)
        if target is None:
            target = str(value["target"])
        elif value["target"] != target:
            raise ArtifactError("specialist target locators differ")
        for item in [*value["candidates"], *value["open_questions"]]:
            identifier = str(item["id"])
            if identifier in identifiers:
                raise ArtifactError(f"duplicate source id across specialists: {identifier}")
            identifiers.add(identifier)
        records.append(
            {
                "reviewer": role,
                "status": value["status"],
                "artifact": str(path.resolve()),
                "sha256": sha256(path),
            }
        )
    if roles != ROLES:
        missing = sorted(ROLES - roles)
        extra = sorted(roles - ROLES)
        raise ArtifactError(f"manifest roles mismatch; missing={missing}, extra={extra}")
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "target": target,
        "specialists": sorted(records, key=lambda item: item["reviewer"]),
    }
    atomic_write(output, manifest)
    return {
        "status": "ready",
        "manifest": str(output.resolve()),
        "sha256": sha256(output),
        "roles": sorted(roles),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    specialist = subparsers.add_parser("validate-specialist")
    specialist.add_argument("artifact", type=Path)
    specialist.add_argument("--role", choices=sorted(ROLES), required=True)
    master = subparsers.add_parser("validate-master")
    master.add_argument("artifact", type=Path)
    master.add_argument("--specialist-manifest", type=Path, required=True)
    manifest = subparsers.add_parser("manifest")
    manifest.add_argument("artifacts", nargs="+", type=Path)
    manifest.add_argument("--output", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "validate-specialist":
            result = validate_file(args.artifact, "specialist", args.role)
        elif args.command == "validate-master":
            result = validate_file(
                args.artifact,
                "master",
                specialist_manifest=args.specialist_manifest,
            )
        else:
            result = build_manifest(args.artifacts, args.output)
    except (ArtifactError, OSError) as error:
        print(json.dumps({"status": "invalid", "error": str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
