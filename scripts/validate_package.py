#!/usr/bin/env python3
"""Rebuild and validate the complete materials-evidence-reasoner skill package."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_DIR = ROOT / "references"
SCRIPTS = ROOT / "scripts"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(errors="replace")


def run(script_name: str, *args: str, stream: bool = False) -> None:
    command = [sys.executable, str(SCRIPTS / script_name), *args]
    if stream:
        result = subprocess.run(command, cwd=ROOT, text=True, encoding="utf-8", errors="replace", timeout=180)
    else:
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, encoding="utf-8", errors="replace", timeout=180)
        if result.stdout:
            print(result.stdout.rstrip())
    if result.returncode:
        if not stream and result.stderr:
            print(result.stderr.rstrip(), file=sys.stderr)
        raise RuntimeError(f"{script_name} failed with exit code {result.returncode}")


def run_path(path: Path, *args: str) -> None:
    result = subprocess.run([sys.executable, str(path), *args], cwd=ROOT, text=True, capture_output=True, encoding="utf-8", errors="replace", timeout=180)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.returncode:
        if result.stderr:
            print(result.stderr.rstrip(), file=sys.stderr)
        raise RuntimeError(f"{path.name} failed with exit code {result.returncode}")


def load_json(name: str) -> dict:
    return json.loads((REFERENCE_DIR / name).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--with-adversarial", action="store_true", help="Also run the slower nested adversarial suite")
    args = parser.parse_args()
    errors: list[str] = []
    for script_name in (
        "build_adapter_assets.py",
        "build_field_contracts.py",
        "build_adapter_benchmarks.py",
        "build_source_backed_cases.py",
    ):
        run(script_name)

    # Rebuild deterministic human-facing artifacts from the validated example.
    run("render_report.py", "examples/synthetic-closed-loop.json", "-o", "examples/synthetic-closed-loop-report.md")
    run("render_dashboard.py", "examples/synthetic-closed-loop.json", "-o", "examples/synthetic-closed-loop-dashboard.html")
    run("mechanism_graph.py", "export", "examples/synthetic-closed-loop.json", "-o", "examples/mechanism-export")
    run("mechanism_graph.py", "index", "examples/synthetic-closed-loop.json", "-o", "examples/mechanism-index.json")
    run("audit_mechanism_graph.py", "examples/synthetic-closed-loop.json", "-o", "examples/mechanism-audit.json", "--report", "examples/mechanism-audit.md")

    for path in sorted(ROOT.rglob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON {path.relative_to(ROOT)}: {exc}")
    for path in sorted(ROOT.rglob("*.py")):
        if path.name.startswith("._") or path.name.lower() in {".ds_store", "thumbs.db"} or any(part.casefold() == "__macosx" for part in path.parts):
            continue
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except (UnicodeDecodeError, SyntaxError) as exc:
            errors.append(f"invalid Python {path.relative_to(ROOT)}: {exc}")

    # The checked-in active-learning example must be runnable as delivered and
    # must keep its source records immutable by default.
    for update_script in sorted(ROOT.rglob("run_sample_and_update.py")):
        if "__MACOSX" in update_script.parts:
            continue
        active_dir = update_script.parent
        if not (active_dir / "test_function.py").is_file():
            errors.append(f"active-learning example is missing {active_dir.relative_to(ROOT) / 'test_function.py'}")
        update_text = update_script.read_text(encoding="utf-8")
        if "output_file = os.path.join('labeled.csv')" in update_text:
            errors.append(f"active-learning update still overwrites labeled.csv: {update_script.relative_to(ROOT)}")
        if "--output-dir" not in update_text or "def run(" not in update_text:
            errors.append(f"active-learning update lacks explicit safe output contract: {update_script.relative_to(ROOT)}")

    skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if len(skill_text.splitlines()) > 500:
        errors.append("SKILL.md exceeds 500 lines")
    if not skill_text.startswith("---\nname: materials-evidence-reasoner\n"):
        errors.append("SKILL.md frontmatter name is missing or invalid")
    if 'version: "4.6.12"' not in skill_text or 'schema-version: "4.6"' not in skill_text:
        errors.append("SKILL.md version declarations are stale")

    # Submission scanners expect the Agent Skills layout even though the
    # repository keeps a root copy for backwards-compatible local commands.
    submission_skill = ROOT / "skills" / "materials-evidence-reasoner" / "SKILL.md"
    if not submission_skill.is_file():
        errors.append("submission skill entry is missing: skills/materials-evidence-reasoner/SKILL.md")
    else:
        submission_text = submission_skill.read_text(encoding="utf-8")
        if submission_text.rstrip() != skill_text.rstrip():
            errors.append("submission skill entry differs from root SKILL.md")

    aliases = load_json("output-field-aliases.json")
    if aliases.get("spec_version") != "1.0" or aliases.get("canonical_schema") != "output-schema.json":
        errors.append("output-field-aliases.json has an invalid canonical contract reference")
    for group_name in ("collections", "hypotheses", "verification_plan"):
        group = aliases.get(group_name, {})
        if not isinstance(group, dict) or not group:
            errors.append(f"output-field-aliases.json: {group_name} alias group is empty")
        field_groups = [
            (f"{group_name}.{name}", fields)
            for name, fields in group.items()
        ] if group_name == "collections" else [(group_name, group)]
        for field_group_name, fields in field_groups:
            if not isinstance(fields, dict) or not fields:
                errors.append(f"output-field-aliases.json: {field_group_name} alias group is empty")
                continue
            for field_name, names in fields.items():
                if not isinstance(names, list) or not names or len(names) != len(set(names)):
                    errors.append(f"output-field-aliases.json: {field_group_name}.{field_name} must be a unique non-empty list")

    required_files = (
        "README.md",
        "skills/materials-evidence-reasoner/SKILL.md",
        "references/input-contract.md",
        "references/report-contract.md",
        "references/error-anomaly-pspp-contract.md",
        "references/mechanism-graph-contract.md",
        "references/source-extraction-contract.md",
        "references/literature-user-workflow.md",
        "references/source-extraction-schema.json",
        "references/input-schema.json",
        "references/intake-field-aliases.json",
        "references/output-field-aliases.json",
        "references/output-field-aliases.schema.json",
        "references/adapter-routing-lexicon.json",
        "references/adapter-routing-lexicon.schema.json",
        "references/routing-maintenance-contract.md",
        "references/task-intent-lexicon.json",
        "references/task-intent-lexicon.schema.json",
        "references/agent-output-contract.md",
        "references/active-learning-contract.md",
        "references/active-learning-field-lexicon.json",
        "scripts/prepare_intake.py",
        "scripts/profile_active_learning.py",
        "scripts/normalize_output.py",
        "scripts/extract_sources.py",
        "scripts/render_source_dashboard.py",
        "scripts/validate_knowledge_assets.py",
        "scripts/analyze_error_budget.py",
        "scripts/mechanism_graph.py",
        "scripts/audit_mechanism_graph.py",
        "scripts/validate_skill_spec.py",
        "scripts/render_report.py",
        "scripts/render_dashboard.py",
        "scripts/smoke_test_viewer.py",
        "scripts/smoke_test_source_dashboard.py",
        "scripts/run_adversarial_tests.py",
        "viewer/index.html",
        "tests/test_source_extraction.py",
        "tests/test_active_learning_profile.py",
        "tests/test_output_aliases.py",
        "templates/experiment-record-template.csv",
        "examples/synthetic-closed-loop.json",
        "examples/literature-only-request.md",
        "examples/active-learning-request.md",
        "examples/synthetic-closed-loop-report.md",
        "examples/synthetic-closed-loop-dashboard.html",
        "examples/error-budget-demo.csv",
        "examples/error-budget-demo.json",
        "examples/error-budget-demo.md",
        "examples/mechanism-audit.json",
        "examples/mechanism-audit.md",
        "examples/mechanism-index.json",
        "examples/mechanism-export/mechanism-graph.json",
        "examples/mechanism-export/mechanism-nodes.csv",
        "examples/mechanism-export/mechanism-edges.csv",
        "examples/mechanism-export/mechanism-graph.dot",
    )
    for relative in required_files:
        if not (ROOT / relative).is_file():
            errors.append(f"required 4.6 asset missing: {relative}")


    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
    for required_phrase in (
        "scripts/prepare_intake.py",
        "scripts/normalize_output.py",
        "scripts/extract_sources.py",
        "scripts/render_source_dashboard.py",
        "scripts/validate_knowledge_assets.py",
        "references/routing-maintenance-contract.md",
        "references/task-intent-lexicon.json",
        "references/task-intent-lexicon.schema.json",
        "references/output-field-aliases.json",
        "references/literature-user-workflow.md",
        "references/source-extraction-contract.md",
        "references/agent-output-contract.md",
        "references/active-learning-contract.md",
        "references/active-learning-field-lexicon.json",
        "scripts/profile_active_learning.py",
        "scripts/analyze_error_budget.py",
        "scripts/mechanism_graph.py",
        "scripts/audit_mechanism_graph.py",
        "scripts/render_report.py",
        "scripts/render_dashboard.py",
        "scripts/smoke_test_viewer.py",
        "scripts/smoke_test_source_dashboard.py",
        "viewer/index.html",
        "L1：README",
    ):
        if required_phrase not in readme_text:
            errors.append(f"README does not document required workflow asset: {required_phrase}")

    report_path = ROOT / "examples/synthetic-closed-loop-report.md"
    if report_path.is_file():
        report_text = report_path.read_text(encoding="utf-8")
        if report_text.find("## 现在该做什么") > report_text.find("## 基准、可比性与偏差"):
            errors.append("human report is not action-first")
        if "机器记录：`synthetic-closed-loop.json`" not in report_text:
            errors.append("human report does not link back to its source JSON")
        for heading in ("## 误差预算", "## 异常传播链", "## 证据约束机理图谱", "## 信息缺口", "## 最小实验集与验证方案", "## PSPP 经验图与更新"):
            if heading not in report_text:
                errors.append(f"human report is missing 4.6 section: {heading}")

    viewer_path = ROOT / "viewer/index.html"
    if viewer_path.is_file():
        viewer_text = viewer_path.read_text(encoding="utf-8")
        if "fetch(" in viewer_text or "<script src=" in viewer_text:
            errors.append("viewer must remain offline and self-contained")
        if ".innerHTML" in viewer_text:
            errors.append("viewer uses innerHTML; untrusted data must use safe DOM APIs")
        if "artifact_manifest" not in viewer_text:
            errors.append("viewer is missing artifact manifest navigation")
        for phrase in ("偏差与误差", "异常传播链", "机理图谱", "信息缺口与实验", "PSPP 经验"):
            if phrase not in viewer_text:
                errors.append(f"viewer is missing 4.6 navigation: {phrase}")

    output_schema = load_json("output-schema.json")
    required_46 = {"error_budgets", "anomaly_propagation_chains", "information_gaps", "experiment_sets", "pspp_maps", "mechanism_graphs", "mechanism_nodes", "mechanism_edges", "mechanism_updates"}
    if not required_46.issubset(set(output_schema.get("required", []))):
        errors.append("output Schema does not require all 4.6 diagnostic and mechanism structures")
    example = json.loads((ROOT / "examples" / "synthetic-closed-loop.json").read_text(encoding="utf-8"))
    if example.get("schema_version") != "4.6":
        errors.append("synthetic closed-loop example is not schema 4.6")
    for key in required_46:
        if not example.get(key):
            errors.append(f"synthetic closed-loop example has no {key}")

    mechanism_audit = json.loads((ROOT / "examples" / "mechanism-audit.json").read_text(encoding="utf-8"))
    if mechanism_audit.get("pass") is not True or mechanism_audit.get("findings"):
        errors.append("example mechanism graph audit did not pass cleanly")
    if not all((ROOT / "examples" / "mechanism-export" / name).is_file() for name in ("mechanism-graph.json", "mechanism-nodes.csv", "mechanism-edges.csv", "mechanism-graph.dot")):
        errors.append("mechanism graph export set is incomplete")

    registry = load_json("adapter-registry.json")
    lexicon = load_json("adapter-routing-lexicon.json")
    contracts = load_json("adapter-field-contracts.json")
    benchmarks = load_json("adapter-benchmark-cases.json")
    source_cases = load_json("source-backed-routing-cases.json")
    registry_ids = {item["adapter_id"] for item in registry["adapters"]}
    if len(registry_ids) != 22:
        errors.append(f"expected 22 adapters, found {len(registry_ids)}")
    verification_statuses = {item.get("verification_status") for item in registry["adapters"]}
    if verification_statuses != {"source-backed"}:
        errors.append(f"expected source-backed adapter verification, found {sorted(verification_statuses)}")
    if registry_ids != set(lexicon["adapters"]):
        errors.append("registry and routing lexicon adapter sets differ")
    if registry_ids - set(contracts["adapters"]) != {"superconductivity"}:
        errors.append("field-contract coverage differs from the expected schema-backed adapter")

    required_strengths = {"strong", "supporting", "weak", "exclusion"}
    for adapter_id, spec in lexicon["adapters"].items():
        strengths = {item["strength"] for item in spec["signals"]}
        if strengths != required_strengths:
            errors.append(f"{adapter_id}: incomplete signal-strength coverage")
        registry_entry = next(item for item in registry["adapters"] if item["adapter_id"] == adapter_id)
        reference_text = (REFERENCE_DIR / registry_entry["reference"]).read_text(encoding="utf-8")
        begin = f"<!-- BEGIN GENERATED ROUTING CONTRACT: {adapter_id} -->"
        end = f"<!-- END GENERATED ROUTING CONTRACT: {adapter_id} -->"
        if reference_text.count(begin) != 1 or reference_text.count(end) != 1:
            errors.append(f"{adapter_id}: generated routing block is missing or duplicated")

    metallic_fields = contracts["adapters"]["metallic-materials"]["record_types"]["metallic-identity"]["allowed_fields"]
    if {"alloy", "intermetallic", "unknown", "pure-metal"} & set(metallic_fields):
        errors.append("enum values leaked into metallic field names")
    record_count = sum(len(item["record_types"]) for item in contracts["adapters"].values())
    if record_count != 97:
        errors.append(f"expected 97 field-contract record types, found {record_count}")
    if len(benchmarks["cases"]) != 132:
        errors.append(f"expected 132 synthetic cases, found {len(benchmarks['cases'])}")
    if benchmarks.get("gold_status") != "not-gold":
        errors.append("synthetic benchmark incorrectly claims gold status")
    if source_cases.get("gold_status") != "not-gold":
        errors.append("source-backed catalog incorrectly claims gold status")
    if set(source_cases.get("adapter_coverage", [])) != registry_ids:
        errors.append("source-backed adapter coverage is incomplete")

    for asset_key in (
        "execution_standard",
        "routing_lexicon",
        "routing_lexicon_schema",
        "field_contract_catalog",
        "field_contract_schema",
        "registry_schema",
        "benchmark_catalog",
        "source_backed_catalog",
        "standards_and_sources",
    ):
        asset_name = registry.get(asset_key)
        if not isinstance(asset_name, str) or not (REFERENCE_DIR / asset_name).is_file():
            errors.append(f"registry asset missing: {asset_key}")

    if errors:
        print(f"PACKAGE INVALID: {len(errors)} issue(s)", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    run("validate_skill_spec.py", ".")
    run("validate_output.py", "--self-test")
    run("validate_output.py", "examples/synthetic-closed-loop.json")
    run("evaluate_routing.py", "--self-test")
    run("validate_knowledge_assets.py")
    run("extract_sources.py", "--check-environment")
    run_path(ROOT / "tests" / "test_source_extraction.py")
    run_path(ROOT / "tests" / "test_active_learning_profile.py")
    if args.with_adversarial:
        # Some constrained runners handle nested subprocess trees poorly; keep this opt-in.
        run("run_adversarial_tests.py", stream=True)
    else:
        print("ADVERSARIAL SUITE NOT RUN: execute python scripts/run_adversarial_tests.py separately")
    print(
        "PACKAGE VALID 4.6.12: 22 adapters, 112 routing signals, 97 record contracts, "
        "132 synthetic cases, 11 source-backed cases, input normalization, descriptive error budgeting, "
        "error/anomaly/information-gap/PSPP contracts, evidence-grounded mechanism graph tooling, report rendering, and offline visualization"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
