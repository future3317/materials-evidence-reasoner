#!/usr/bin/env python3
"""Run deterministic adversarial regression tests for the 4.6 Skill package."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
EXAMPLE = ROOT / "examples" / "synthetic-closed-loop.json"
VIEWER = ROOT / "viewer" / "index.html"


class Harness:
    def __init__(self) -> None:
        self.passed = 0
        self.failed: list[str] = []

    def check(self, condition: bool, name: str, detail: str = "") -> None:
        if condition:
            self.passed += 1
            print(f"PASS {name}")
        else:
            self.failed.append(f"{name}: {detail}")
            print(f"FAIL {name}: {detail}", file=sys.stderr)


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_output", SCRIPTS / "validate_output.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    schema = module.load_json(ROOT / "references" / "output-schema.json")
    adapter_schemas, _ = module.load_adapter_schemas(ROOT / "references")
    registry, _ = module.load_adapter_registry(ROOT / "references")
    contracts, _ = module.load_field_contracts(ROOT / "references", registry)
    lexicon = module.load_json(ROOT / "references" / "adapter-routing-lexicon.json")
    return module, schema, adapter_schemas, registry, contracts, lexicon


def validation_errors(document: dict, resources) -> list[str]:
    module, schema, adapter_schemas, registry, contracts, lexicon = resources
    errors, _ = module.validate_document(document, schema, adapter_schemas, registry, contracts, lexicon)
    return errors


def run(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd or ROOT, text=True, capture_output=True, encoding="utf-8")


def main() -> int:
    h = Harness()
    resources = load_validator()
    base = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    h.check(not validation_errors(base, resources), "valid-example", "reference example should validate")

    collision = copy.deepcopy(base)
    collision["condition_registry"].append(copy.deepcopy(collision["condition_registry"][0]))
    collision["condition_registry"][-1]["id"] = "COND-B"
    collision["condition_registry"][-1]["condition_signature"]["temperature_C"] = 80
    errors = validation_errors(collision, resources)
    h.check(any("multiple condition signatures" in error for error in errors), "condition-alias-collision", "same alias must not hide different conditions")

    not_comparable = copy.deepcopy(base)
    not_comparable["comparability_assessments"][0]["result"] = "not-comparable"
    errors = validation_errors(not_comparable, resources)
    h.check(any("not-comparable assessment" in error for error in errors), "presentation-overclaim", "not-comparable data must not be shown as a material deviation")

    residual = copy.deepcopy(base)
    residual["comparability_assessments"][0]["result"] = "not-comparable"
    residual["deviation_episodes"][0]["classification"] = "not-comparable"
    errors = validation_errors(residual, resources)
    h.check(any("residual must be omitted" in error for error in errors), "not-comparable-residual", "residual must be suppressed")

    broken_artifact = copy.deepcopy(base)
    broken_artifact["artifact_manifest"][1]["depends_on"] = ["ART-NOT-FOUND"]
    errors = validation_errors(broken_artifact, resources)
    h.check(any("unknown artifact" in error for error in errors), "artifact-reference-integrity", "artifact dependency should resolve")

    mixed_basis = copy.deepcopy(base)
    mixed_basis["error_budgets"][0]["components"][1]["contribution_basis"] = "standard-uncertainty"
    errors = validation_errors(mixed_basis, resources)
    h.check(any("one common quantitative contribution basis" in error for error in errors), "error-budget-common-basis", "fractions must not mix variance and uncertainty bases")

    bad_fraction = copy.deepcopy(base)
    bad_fraction["error_budgets"][0]["components"][0]["fraction_of_total"] = 0.55
    errors = validation_errors(bad_fraction, resources)
    h.check(any("sum to approximately 1.0" in error for error in errors), "error-budget-fraction-closure", "complete fractions must close")

    uncertainty_override = copy.deepcopy(base)
    uncertainty_override["error_budgets"][0]["effect_comparison"]["relation"] = "uncertainty-dominates"
    errors = validation_errors(uncertainty_override, resources)
    h.check(any("cannot support 'material-process-deviation'" in error for error in errors), "uncertainty-gate", "uncertainty-dominated effects must not be promoted to material deviations")

    broken_chain = copy.deepcopy(base)
    broken_chain["anomaly_propagation_chains"][0]["edges"][0]["to_node_id"] = "NODE-NOT-FOUND"
    errors = validation_errors(broken_chain, resources)
    h.check(any("endpoints must name local nodes" in error for error in errors), "anomaly-chain-local-edges", "chain edges must resolve locally")

    unsupported_chain = copy.deepcopy(base)
    unsupported_chain["anomaly_propagation_chains"][0]["status"] = "supported"
    for edge in unsupported_chain["anomaly_propagation_chains"][0]["edges"]:
        edge["evidence_strength"] = "inferred"
        edge["evidence_ids"] = []
    errors = validation_errors(unsupported_chain, resources)
    h.check(any("supported chains require at least one directly evidenced edge" in error for error in errors), "anomaly-chain-upgrade-gate", "supported status requires direct evidence")

    orphan_gap = copy.deepcopy(base)
    orphan_gap["verification_plan"][0]["information_gap_ids"] = ["IG2"]
    errors = validation_errors(orphan_gap, resources)
    h.check(any("high-impact planned measurement is not linked" in error for error in errors), "information-gap-orphan", "high-impact gaps must be linked to a verification item")

    coverage_gap = copy.deepcopy(base)
    coverage_gap["experiment_sets"][0]["coverage_matrix"][0]["information_gap_ids"] = ["IG1"]
    errors = validation_errors(coverage_gap, resources)
    h.check(any("are not covered by the matrix" in error for error in errors), "experiment-set-coverage", "minimum experiment sets must cover every declared gap")

    broken_pspp = copy.deepcopy(base)
    broken_pspp["pspp_maps"][0]["relationships"][0]["to_node_id"] = "PSPP-NOT-FOUND"
    errors = validation_errors(broken_pspp, resources)
    h.check(any("endpoints must name local PSPP nodes" in error for error in errors), "pspp-local-relations", "PSPP relations must resolve inside the graph")

    orphan_experience = copy.deepcopy(base)
    orphan_experience["experience_updates"][0]["pspp_map_ids"] = []
    orphan_experience["experience_updates"][0].pop("pspp_exception_reason", None)
    errors = validation_errors(orphan_experience, resources)
    h.check(any("reusable updates require pspp_map_ids" in error for error in errors), "experience-pspp-binding", "reusable experience must bind to PSPP or document an exception")

    edge_without_evidence = copy.deepcopy(base)
    edge_without_evidence["mechanism_edges"][0]["support_evidence_ids"] = []
    errors = validation_errors(edge_without_evidence, resources)
    h.check(any("support_evidence_ids" in error for error in errors), "mechanism-edge-evidence-required", "reusable mechanism edges must retain source evidence")

    inference_upgrade = copy.deepcopy(base)
    inference_upgrade["mechanism_edges"][1]["validation_status"] = "supported"
    errors = validation_errors(inference_upgrade, resources)
    h.check(any("domain-inference edges must remain hypotheses" in error for error in errors), "mechanism-inference-upgrade-gate", "domain knowledge alone must not become a supported mechanism")

    local_without_validation = copy.deepcopy(base)
    local_without_validation["mechanism_edges"][0]["validation_status"] = "locally-validated"
    errors = validation_errors(local_without_validation, resources)
    h.check(any("locally-validated status requires validation_evidence_ids" in error for error in errors), "mechanism-local-validation-evidence", "local validation must identify intervention or matched validation evidence")

    cross_material_upgrade = copy.deepcopy(base)
    cross_material_upgrade["mechanism_edges"][0]["transferability"]["level"] = "cross-material-proposed"
    cross_material_upgrade["mechanism_edges"][0]["validation_status"] = "supported"
    errors = validation_errors(cross_material_upgrade, resources)
    h.check(any("cross-material transfer proposals cannot be marked" in error for error in errors), "mechanism-cross-material-transfer-gate", "analogy across material systems must remain a proposal")

    broken_graph_backlink = copy.deepcopy(base)
    broken_graph_backlink["mechanism_nodes"][0]["graph_ids"] = []
    errors = validation_errors(broken_graph_backlink, resources)
    h.check(any("does not link back to the graph" in error for error in errors), "mechanism-bidirectional-membership", "graph and node membership must be bidirectional")

    wrong_edge_graph = copy.deepcopy(base)
    wrong_edge_graph["mechanism_edges"][0]["graph_id"] = "MG-NOT-FOUND"
    errors = validation_errors(wrong_edge_graph, resources)
    h.check(any("belongs to 'MG-NOT-FOUND'" in error or "unknown mechanism_graph" in error for error in errors), "mechanism-edge-graph-integrity", "an edge cannot silently move outside its declared graph")

    no_match_with_edge = copy.deepcopy(base)
    no_match_with_edge["hypotheses"][1]["linked_mechanism_edge_ids"] = ["ME1"]
    errors = validation_errors(no_match_with_edge, resources)
    h.check(any("no-match cannot retain linked mechanism edges" in error for error in errors), "mechanism-hypothesis-match-integrity", "a no-match result cannot cite a graph edge as a match")

    applied_without_write = copy.deepcopy(base)
    applied_without_write["mechanism_updates"][0]["status"] = "applied"
    errors = validation_errors(applied_without_write, resources)
    h.check(any("applied update requires a confirmed artifact or external write" in error for error in errors), "mechanism-update-write-governance", "applied status requires a verifiable write")

    support_without_proposal_evidence = copy.deepcopy(base)
    support_without_proposal_evidence["mechanism_updates"][0]["proposed_support_evidence_ids"] = []
    errors = validation_errors(support_without_proposal_evidence, resources)
    h.check(any("support-edge requires proposed_support_evidence_ids" in error for error in errors), "mechanism-update-evidence-gate", "support operations must name the evidence to add")

    viewer_text = VIEWER.read_text(encoding="utf-8")
    h.check("fetch(" not in viewer_text and "<script src=" not in viewer_text, "viewer-offline", "viewer must not use remote resources")
    h.check(".innerHTML" not in viewer_text and ".textContent" in viewer_text, "viewer-safe-dom", "untrusted content should use textContent")
    h.check(all(label in viewer_text for label in ("偏差与误差", "异常传播链", "机理图谱", "信息缺口与实验", "PSPP 经验")), "viewer-4.6-tabs", "viewer must expose the diagnostic structures")

    h.check("prefers-reduced-motion" in viewer_text and "prefers-reduced-transparency" in viewer_text, "viewer-accessibility-preferences", "viewer must respect reduced motion and transparency preferences")
    h.check("graph-edge-hit" in viewer_text and "tabindex" in viewer_text and "aria-label" in viewer_text, "viewer-keyboard-graph-audit", "mechanism nodes and edges must be keyboard-auditable")
    h.check("<script src=" not in viewer_text and "cdn.jsdelivr" not in viewer_text, "viewer-no-external-design-dependency", "visual design must remain offline")

    with tempfile.TemporaryDirectory(prefix="materials-adversarial-") as temp_name:
        temp = Path(temp_name)

        malicious = copy.deepcopy(base)
        malicious["sources"][0]["title"] = "</script><script>alert('xss')</script>"
        malicious["mechanism_edges"][0]["mechanism_description"] = "</script><script>alert('mechanism-xss')</script>"
        malicious_path = temp / "malicious.json"
        malicious_path.write_text(json.dumps(malicious, ensure_ascii=False, indent=2), encoding="utf-8")
        dashboard_path = temp / "malicious.html"
        result = run([sys.executable, str(SCRIPTS / "render_dashboard.py"), str(malicious_path), "-o", str(dashboard_path)])
        rendered = dashboard_path.read_text(encoding="utf-8") if dashboard_path.exists() else ""
        h.check(result.returncode == 0, "dashboard-render-valid", result.stderr or result.stdout)
        h.check("</script><script>alert" not in rendered and "<\\/script><script>alert" in rendered, "dashboard-script-escape", "embedded JSON must escape closing script tags")
        h.check("mechanism-xss" in rendered and "</script><script>alert('mechanism-xss')" not in rendered, "mechanism-dashboard-injection", "mechanism text must remain inert inside the embedded artifact")

        graph_summary = run([sys.executable, str(SCRIPTS / "mechanism_graph.py"), "summary", str(EXAMPLE), "--json"])
        summary_doc = json.loads(graph_summary.stdout) if graph_summary.returncode == 0 else {}
        h.check(graph_summary.returncode == 0 and summary_doc.get("graph_count") == 1 and summary_doc.get("edge_count") == 4, "mechanism-cli-summary", graph_summary.stderr or graph_summary.stdout)

        graph_query = run([sys.executable, str(SCRIPTS / "mechanism_graph.py"), "query", str(EXAMPLE), "--text", "surface", "--json"])
        query_doc = json.loads(graph_query.stdout) if graph_query.returncode == 0 else {}
        h.check(graph_query.returncode == 0 and query_doc.get("edges"), "mechanism-cli-query", graph_query.stderr or graph_query.stdout)

        graph_export = temp / "mechanism-export"
        result = run([sys.executable, str(SCRIPTS / "mechanism_graph.py"), "export", str(EXAMPLE), "-o", str(graph_export)])
        h.check(result.returncode == 0 and all((graph_export / name).is_file() for name in ("mechanism-graph.json", "mechanism-nodes.csv", "mechanism-edges.csv", "mechanism-graph.dot")), "mechanism-cli-export", result.stderr or result.stdout)

        graph_audit = temp / "mechanism-audit.json"
        graph_audit_md = temp / "mechanism-audit.md"
        result = run([sys.executable, str(SCRIPTS / "audit_mechanism_graph.py"), str(EXAMPLE), "-o", str(graph_audit), "--report", str(graph_audit_md)])
        audit_doc = json.loads(graph_audit.read_text(encoding="utf-8")) if graph_audit.exists() else {}
        h.check(result.returncode == 0 and audit_doc.get("pass") is True and not audit_doc.get("findings"), "mechanism-cli-audit", result.stderr or result.stdout)

        rejected_apply = run([sys.executable, str(SCRIPTS / "mechanism_graph.py"), "apply", str(EXAMPLE), "-o", str(temp / "should-not-write.json")])
        h.check(rejected_apply.returncode != 0 and "no approved updates" in (rejected_apply.stderr + rejected_apply.stdout), "mechanism-apply-approval-gate", rejected_apply.stderr or rejected_apply.stdout)

        graph_index = temp / "mechanism-index.json"
        result = run([sys.executable, str(SCRIPTS / "mechanism_graph.py"), "index", str(EXAMPLE), "-o", str(graph_index)])
        index_doc = json.loads(graph_index.read_text(encoding="utf-8")) if graph_index.exists() else {}
        h.check(result.returncode == 0 and index_doc.get("postings") and index_doc.get("summary", {}).get("edge_count") == 4, "mechanism-cli-index", result.stderr or result.stdout)

        approved = copy.deepcopy(base)
        approved["mechanism_updates"][0]["status"] = "approved"
        approved_path = temp / "approved.json"
        approved_path.write_text(json.dumps(approved, ensure_ascii=False, indent=2), encoding="utf-8")
        applied_path = temp / "applied.json"
        result = run([sys.executable, str(SCRIPTS / "mechanism_graph.py"), "apply", str(approved_path), "--update-id", "MU1", "-o", str(applied_path)])
        applied_doc = json.loads(applied_path.read_text(encoding="utf-8")) if applied_path.exists() else {}
        applied_edge = next((x for x in applied_doc.get("mechanism_edges", []) if x.get("id") == "ME1"), {})
        applied_update = next((x for x in applied_doc.get("mechanism_updates", []) if x.get("id") == "MU1"), {})
        h.check(result.returncode == 0 and applied_edge.get("validation_status") == "supported" and applied_update.get("status") == "applied" and applied_update.get("persistence_status") == "artifact-written", "mechanism-approved-apply", result.stderr or result.stdout)

        diff_path = temp / "mechanism-diff.json"
        result = run([sys.executable, str(SCRIPTS / "mechanism_graph.py"), "diff", str(approved_path), str(applied_path), "-o", str(diff_path)])
        diff_doc = json.loads(diff_path.read_text(encoding="utf-8")) if diff_path.exists() else {}
        changed_edges = {x.get("id") for x in diff_doc.get("edges", {}).get("changed", [])}
        changed_updates = {x.get("id") for x in diff_doc.get("updates", {}).get("changed", [])}
        h.check(result.returncode == 0 and "ME1" in changed_edges and "MU1" in changed_updates, "mechanism-cli-diff", result.stderr or result.stdout)

        report_path = temp / "report.md"
        result = run([sys.executable, str(SCRIPTS / "render_report.py"), str(malicious_path), "-o", str(report_path)])
        report_text = report_path.read_text(encoding="utf-8") if report_path.exists() else ""
        h.check(result.returncode == 0, "report-render-valid", result.stderr or result.stdout)
        h.check(report_text.find("## 现在该做什么") < report_text.find("## 基准、可比性与偏差"), "report-action-first", "actions must precede technical detail")
        h.check("机器记录：`malicious.json`" in report_text, "report-source-link", "report should identify its source JSON")
        h.check(all(heading in report_text for heading in ("## 误差预算", "## 异常传播链", "## 证据约束机理图谱", "## 信息缺口", "## 最小实验集与验证方案", "## PSPP 经验图与更新")), "report-4.6-sections", "report must render all new diagnostic sections")

        incomparable_doc = copy.deepcopy(base)
        incomparable_doc["comparability_assessments"][0]["result"] = "not-comparable"
        incomparable_doc["deviation_episodes"][0]["classification"] = "not-comparable"
        incomparable_doc["deviation_episodes"][0].pop("residual", None)
        incomparable_path = temp / "not-comparable.json"
        incomparable_path.write_text(json.dumps(incomparable_doc, ensure_ascii=False, indent=2), encoding="utf-8")
        incomparable_report = temp / "not-comparable.md"
        result = run([sys.executable, str(SCRIPTS / "render_report.py"), str(incomparable_path), "-o", str(incomparable_report), "--skip-validation"])
        incomparable_text = incomparable_report.read_text(encoding="utf-8") if incomparable_report.exists() else ""
        h.check(result.returncode == 0 and "因不可比而不计算" in incomparable_text, "report-not-comparable-guard", result.stderr or incomparable_text)

        malformed = temp / "malformed.json"
        malformed.write_text('{"schema_version":', encoding="utf-8")
        result_report = run([sys.executable, str(SCRIPTS / "render_report.py"), str(malformed), "-o", str(temp / "bad.md")])
        result_dashboard = run([sys.executable, str(SCRIPTS / "render_dashboard.py"), str(malformed), "-o", str(temp / "bad.html")])
        h.check(result_report.returncode != 0 and result_dashboard.returncode != 0, "malformed-json-rejected", "renderers must fail closed")

        csv_missing = temp / "missing-unit.csv"
        csv_missing.write_text("sample_id,material,property_name,property_value,rate\nS1,Epoxy composite,thermal conductivity,2.1,5\n", encoding="utf-8")
        out_missing = temp / "out-missing"
        result = run([sys.executable, str(SCRIPTS / "prepare_intake.py"), str(csv_missing), "--output", str(out_missing), "--decision", "Compare this sample with literature"])
        packet = json.loads((out_missing / "intake-packet.json").read_text(encoding="utf-8"))
        h.check(result.returncode == 0, "intake-missing-unit-runs", result.stderr)
        h.check(any(item["field"] == "unit" and item["priority"] == "blocker" for item in packet["missing_information"]), "unit-blocker", "numeric values without units must block quantitative comparison")
        rate_col = next(col for col in packet["normalized_tables"][0]["columns"] if col["raw_name"] == "rate")
        h.check(rate_col["mapping_status"] == "contextual-candidate", "ambiguous-rate", "generic rate must not map silently")
        raw = packet["normalized_tables"][0]["rows"][0]["raw"]
        h.check(raw.get("property_name") == "thermal conductivity" and raw.get("property_value") == "2.1", "raw-preservation", "normalization must preserve original cells")

        csv_complete = temp / "complete.csv"
        csv_complete.write_text("sample_id,material_name,property_name,property_value,unit,measurement_method,normalization_basis,replicate_count\nS1,Alloy A,yield strength,450,MPa,tensile test,cross-section,3\n", encoding="utf-8")
        out_complete = temp / "out-complete"
        result = run([sys.executable, str(SCRIPTS / "prepare_intake.py"), str(csv_complete), "--output", str(out_complete), "--decision", "Check batch deviation"])
        complete_packet = json.loads((out_complete / "intake-packet.json").read_text(encoding="utf-8"))
        h.check(result.returncode == 0, "intake-complete-runs", result.stderr)
        h.check(not any(item["field"] == "unit" for item in complete_packet["missing_information"]), "unit-recognized", "dedicated unit column should clear the blocker")
        h.check(complete_packet["summary"]["readiness"] != "blocked", "missingness-ranking", "optional process history must not block a valid measurement record")

        diagnostic_missing = {item["field"]: item["priority"] for item in complete_packet["missing_information"]}
        h.check("batch_id_for_error_budget" in diagnostic_missing and "instrument_and_calibration_provenance" in diagnostic_missing, "diagnostic-intake-reminders", str(diagnostic_missing))

        error_csv = temp / "error-budget.csv"
        error_csv.write_text("batch_id,sample_id,measurement_repeat_id,value,unit\nB1,S1,R1,10.0,MPa\nB1,S1,R2,10.2,MPa\nB1,S2,R1,10.5,MPa\nB1,S2,R2,10.6,MPa\nB2,S3,R1,11.0,MPa\nB2,S3,R2,11.1,MPa\n", encoding="utf-8")
        error_json = temp / "error-budget.json"
        error_md = temp / "error-budget.md"
        result = run([sys.executable, str(SCRIPTS / "analyze_error_budget.py"), str(error_csv), "--value", "value", "--unit", "MPa", "-o", str(error_json), "--report", str(error_md)])
        error_doc = json.loads(error_json.read_text(encoding="utf-8")) if error_json.exists() else {}
        h.check(result.returncode == 0 and error_doc.get("components"), "error-budget-helper-runs", result.stderr or result.stdout)
        h.check("not a GUM-compliant" in error_md.read_text(encoding="utf-8") if error_md.exists() else False, "error-budget-helper-boundary", "helper must disclose metrology limits")

        formula_csv = temp / "formula.csv"
        formula_csv.write_text("sample_id,property_name,property_value,unit,notes\nS1,capacity,=1+1,mAh/g,=HYPERLINK(\"http://example.invalid\",\"click\")\n", encoding="utf-8")
        out_formula = temp / "out-formula"
        result = run([sys.executable, str(SCRIPTS / "prepare_intake.py"), str(formula_csv), "--output", str(out_formula)])
        formula_packet = json.loads((out_formula / "intake-packet.json").read_text(encoding="utf-8"))
        formula_raw = formula_packet["normalized_tables"][0]["rows"][0]["raw"]
        h.check(formula_raw["property_value"] == "=1+1", "csv-formula-not-executed", "formula-like CSV cells must remain text")

        chinese_csv = temp / "中文实验记录.csv"
        chinese_csv.write_text("样品编号,材料名称,性能,性能值,单位,测试方法,重复数\n样1,氧化铝陶瓷,抗弯强度,420,MPa,三点弯曲,5\n", encoding="utf-8")
        out_chinese = temp / "out-chinese"
        result = run([sys.executable, str(SCRIPTS / "prepare_intake.py"), str(chinese_csv), "--output", str(out_chinese)])
        chinese_packet = json.loads((out_chinese / "intake-packet.json").read_text(encoding="utf-8"))
        canonical = chinese_packet["normalized_tables"][0]["rows"][0]["canonical"]
        h.check(result.returncode == 0, "chinese-intake-runs", result.stderr)
        h.check(canonical.get("sample_id") == "样1" and canonical.get("property_value") == "420" and canonical.get("unit") == "MPa", "chinese-header-aliases", str(canonical))

        chinese_ambiguous = temp / "中文歧义列.csv"
        chinese_ambiguous.write_text("样品编号,性能,性能值,单位,温度,速率\n样1,电导率,3.2,S/cm,25,5\n", encoding="utf-8")
        out_chinese_ambiguous = temp / "out-chinese-ambiguous"
        result = run([sys.executable, str(SCRIPTS / "prepare_intake.py"), str(chinese_ambiguous), "--output", str(out_chinese_ambiguous)])
        ambiguous_packet = json.loads((out_chinese_ambiguous / "intake-packet.json").read_text(encoding="utf-8"))
        ambiguous_columns = {item["raw_name"]: item["mapping_status"] for item in ambiguous_packet["normalized_tables"][0]["columns"]}
        h.check(result.returncode == 0 and ambiguous_columns.get("温度") == "contextual-candidate" and ambiguous_columns.get("速率") == "contextual-candidate", "chinese-ambiguous-context", str(ambiguous_columns))

        fake_pdf = temp / "fake.pdf"
        fake_pdf.write_text("This is not a PDF", encoding="utf-8")
        out_fake = temp / "out-fake-pdf"
        result = run([sys.executable, str(SCRIPTS / "prepare_intake.py"), str(fake_pdf), "--output", str(out_fake)])
        fake_packet = json.loads((out_fake / "intake-packet.json").read_text(encoding="utf-8"))
        fake_warnings = " ".join(fake_packet["received_inputs"][0]["warnings"])
        h.check(result.returncode == 0 and "PDF magic bytes are missing" in fake_warnings, "fake-pdf-warning", fake_warnings)

        try:
            import openpyxl
        except ImportError:
            print("SKIP xlsx-formula-warning: openpyxl unavailable")
        else:
            workbook_path = temp / "formula.xlsx"
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.append(["sample_id", "property_name", "property_value", "unit"])
            ws.append(["S1", "density", "=1+1", "g/cm3"])
            ws.row_dimensions[2].hidden = True
            wb.save(workbook_path)
            out_xlsx = temp / "out-xlsx"
            result = run([sys.executable, str(SCRIPTS / "prepare_intake.py"), str(workbook_path), "--output", str(out_xlsx)])
            xpacket = json.loads((out_xlsx / "intake-packet.json").read_text(encoding="utf-8"))
            warnings = " ".join(xpacket["normalized_tables"][0]["warnings"])
            h.check(result.returncode == 0, "xlsx-intake-runs", result.stderr)
            h.check("formula cells" in warnings and "hidden rows=1" in warnings, "xlsx-formula-hidden-warning", warnings)

    skill_lines = (ROOT / "SKILL.md").read_text(encoding="utf-8").splitlines()
    h.check(len(skill_lines) <= 500, "progressive-disclosure-size", f"SKILL.md has {len(skill_lines)} lines")
    h.check((ROOT / "README.md").is_file() and (ROOT / "references" / "report-contract.md").is_file(), "three-layer-docs", "human and execution documents must be separate")

    total = h.passed + len(h.failed)
    if h.failed:
        print(f"ADVERSARIAL TESTS FAILED: {len(h.failed)}/{total}", file=sys.stderr)
        for item in h.failed:
            print(f"- {item}", file=sys.stderr)
        return 1
    print(f"ADVERSARIAL TESTS PASSED: {h.passed}/{total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
