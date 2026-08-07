#!/usr/bin/env python3
"""Build source-backed, non-gold routing audit cases."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "references" / "source-backed-routing-cases.json"
LEXICON_PATH = ROOT / "references" / "adapter-routing-lexicon.json"
REGISTRY_PATH = ROOT / "references" / "adapter-registry.json"


CASES = [
    {
        "case_id": "source-sc-ruthenate-eutectic",
        "source": {
            "title": "Superconductivity in Sr2RuO4-Sr3Ru2O7 eutectic crystals",
            "url": "https://arxiv.org/abs/0712.1847",
            "source_kind": "primary-research-preprint",
            "audit_locators": ["title", "page 1 abstract", "pages 1-2 methods"],
        },
        "audited_text": "Source-grounded synopsis: superconducting behavior and supercurrent are tested by current-voltage measurements; SEM, TEM, EDS and WDS resolve the eutectic domains.",
        "decisions": [
            ["superconductivity", "load", ["sc-superconducting-claim"]],
            ["electrical-magnetic-transport", "load", ["emt-electrical-run"]],
            ["electron-microscopy-microanalysis", "load", ["em-imaging", "em-microanalysis"]],
        ],
    },
    {
        "case_id": "source-metal-microscale-am",
        "source": {
            "title": "Metals by micro-scale additive manufacturing: comparison of microstructure and mechanical properties",
            "url": "https://arxiv.org/abs/1912.03581",
            "source_kind": "primary-research-preprint",
            "audit_locators": ["title", "abstract"],
        },
        "audited_text": "Source-grounded synopsis: metallic materials made by micro-scale additive manufacturing are compared using electron microscopy, nanoindentation and microcompression.",
        "decisions": [
            ["metallic-materials", "load", ["met-alloy-identity"]],
            ["materials-processing", "load", ["proc-additive-or-joining"]],
            ["electron-microscopy-microanalysis", "load", ["em-imaging"]],
            ["mechanical-testing", "load", ["mech-actual-test"]],
        ],
    },
    {
        "case_id": "source-polymer-nanocomposite-multimodal",
        "source": {
            "title": "Silver-titanium polymeric nanocomposite non ecotoxic with bactericide activity",
            "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC8753336/",
            "source_kind": "primary-research-article",
            "audit_locators": ["methods: DSC/TG", "methods: Raman", "methods: mechanical properties"],
        },
        "audited_text": "Source-grounded synopsis: polymeric nanocomposite films undergo DSC, thermogravimetric analysis, Raman spectroscopy and tensile testing with reported specimen replication.",
        "decisions": [
            ["polymers", "load", ["pol-polymer-identity"]],
            ["thermal-analysis", "load", ["ta-actual-technique"]],
            ["spectroscopy", "load", ["spec-actual-technique"]],
            ["mechanical-testing", "load", ["mech-actual-test"]],
        ],
    },
    {
        "case_id": "source-b4c-sps-multimodal",
        "source": {
            "title": "Spark Plasma Sintered B4C - Structural, Thermal, Electrical and Mechanical Properties",
            "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC7178422/",
            "source_kind": "primary-research-article",
            "audit_locators": ["abstract", "conclusions"],
        },
        "audited_text": "Source-grounded synopsis: B4C ceramic is made by spark plasma sintering and analyzed by XRD, Raman, SEM, nanoindentation and electrical transport measurements.",
        "decisions": [
            ["ceramics-glass-cement", "load", ["cer-forming-firing-curing"]],
            ["materials-processing", "load", ["proc-parameterized-step"]],
            ["diffraction-scattering", "load", ["dif-actual-measurement"]],
            ["spectroscopy", "load", ["spec-actual-technique"]],
            ["electron-microscopy-microanalysis", "load", ["em-imaging"]],
            ["mechanical-testing", "load", ["mech-actual-test"]],
            ["thermal-analysis", "skip", ["ta-process-heating"]],
        ],
    },
    {
        "case_id": "source-battery-electrolyte-formulation",
        "source": {
            "title": "From Additive to Cosolvent: How Fluoroethylene Carbonate Concentrations Influence Solid-Electrolyte Interphase Properties and Electrochemical Performance of Si/Gr Anodes",
            "url": "https://pubs.acs.org/doi/10.1021/acsaem.2c01454",
            "source_kind": "primary-research-article",
            "audit_locators": ["materials and methods", "electrode preparation", "cycling protocol"],
        },
        "audited_text": "Source-grounded synopsis: lithium-ion battery electrodes are slurry-prepared; liquid electrolyte formulations vary FEC concentration; formation and charge-discharge cycling are reported.",
        "decisions": [
            ["battery", "load", ["bat-cell-hierarchy", "bat-cycling"]],
            ["liquid-materials", "load", ["liq-composition"]],
            ["materials-processing", "load", ["proc-parameterized-step"]],
            ["electrochemical-energy", "skip", ["ece-other-electrochem"]],
        ],
    },
    {
        "case_id": "source-battery-eis-cell-design",
        "source": {
            "title": "Cell Design for Electrochemical Characterizations of Metal-Ion Batteries in Organic and Aqueous Electrolyte",
            "url": "https://pubs.acs.org/doi/10.1021/acs.analchem.6b02138",
            "source_kind": "primary-research-article",
            "audit_locators": ["abstract", "cell design", "electrochemical methods"],
        },
        "audited_text": "Source-grounded synopsis: a metal-ion battery cell is designed for electrochemical impedance spectroscopy and differential electrochemical mass spectrometry.",
        "decisions": [
            ["battery", "load", ["bat-cell-hierarchy"]],
            ["electrochemical-testing", "load", ["echem-impedance-pulse"]],
        ],
    },
    {
        "case_id": "source-tellurene-quantum-transport",
        "source": {
            "title": "Quantum Transport and Band Structure Evolution under High Magnetic Field in Few-Layer Tellurene",
            "url": "https://arxiv.org/abs/1806.08229",
            "source_kind": "primary-research-preprint",
            "audit_locators": ["title", "abstract"],
        },
        "audited_text": "Source-grounded synopsis: few-layer tellurene exhibits quantum Hall and Shubnikov-de-Haas transport; density functional theory calculations support band-structure interpretation.",
        "decisions": [
            ["two-dimensional-materials", "load", ["twod-layer-count"]],
            ["quantum-materials", "load", ["qmat-quantized-transport"]],
            ["electrical-magnetic-transport", "load", ["emt-electrical-run"]],
            ["materials-simulation", "load", ["sim-electronic-atomistic"]],
        ],
    },
    {
        "case_id": "source-photoanode-water-oxidation",
        "source": {
            "title": "Performance and Failure Modes of Si Anodes Patterned with Thin-Film Ni Catalyst Islands for Water Oxidation",
            "url": "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=923743",
            "doi": "10.1039/C7SE00583K",
            "source_kind": "primary-research-article",
            "audit_locators": ["abstract", "pages 11-13 methods", "results"],
        },
        "audited_text": "Source-grounded synopsis: oxygen-evolution photoanodes are evaluated by cyclic voltammetry and Faradaic efficiency, with SEM, TEM and XPS failure analysis.",
        "decisions": [
            ["electrochemical-energy", "load", ["ece-reaction", "ece-performance"]],
            ["electrochemical-testing", "load", ["echem-sweep-step"]],
            ["electron-microscopy-microanalysis", "load", ["em-imaging"]],
            ["spectroscopy", "load", ["spec-actual-technique"]],
            ["photovoltaic-device", "skip", ["pv-other-photo"]],
        ],
    },
    {
        "case_id": "source-mof-hydrogen-storage",
        "source": {
            "title": "Record High Hydrogen Storage Capacity in the Metal-Organic Framework Ni2(m-dobdc) at Near-Ambient Temperatures",
            "url": "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=925465",
            "doi": "10.1021/acs.chemmater.8b03276",
            "source_kind": "primary-research-article",
            "audit_locators": ["results: high-pressure isotherms", "usable capacity definition", "methods"],
        },
        "audited_text": "Source-grounded synopsis: hydrogen storage capacity is determined from calibrated high-pressure gas adsorption isotherms with temperature, pressure and usable-capacity bases.",
        "decisions": [
            ["hydrogen-storage", "load", ["h2s-storage-material", "h2s-performance"]],
            ["composition-particle-surface", "load", ["cps-particle-surface", "cps-quantification"]],
            ["electrochemical-energy", "skip", ["ece-other-electrochem"]],
        ],
    },
    {
        "case_id": "source-thermoelectric-multitransport-metrology",
        "source": {
            "title": "Apparatus for the measurement of electrical resistivity, Seebeck coefficient, and thermal conductivity of thermoelectric materials between 300 K and 12 K",
            "url": "https://www.nist.gov/publications/apparatus-measurement-electrical-resistivity-seebeck-coefficient-and-thermal",
            "doi": "10.1063/1.4939555",
            "source_kind": "primary-metrology-article",
            "audit_locators": ["abstract", "measurement protocol"],
        },
        "audited_text": "Source-grounded synopsis: thermoelectric materials undergo four-probe resistivity, Seebeck coefficient and thermal conductivity measurements with uncertainty assessment.",
        "decisions": [
            ["thermoelectric", "load", ["te-coupled-transport"]],
            ["electrical-magnetic-transport", "load", ["emt-electrical-run", "emt-transport-result"]],
            ["thermal-analysis", "skip", ["ta-process-heating"]],
        ],
    },
    {
        "case_id": "source-pv-performance-metrology",
        "source": {
            "title": "PV Cell and Module Performance Measurement Capabilities at NREL",
            "url": "https://www.nrel.gov/docs/legosti/old/25411.pdf",
            "source_kind": "primary-metrology-conference-paper",
            "audit_locators": ["abstract", "I-V measurements", "spectral responsivity methods"],
        },
        "audited_text": "Source-grounded synopsis: photovoltaic cells and modules are calibrated by current-voltage and spectral-responsivity measurements under controlled temperature and irradiance.",
        "decisions": [
            ["photovoltaic-device", "load", ["pv-device", "pv-calibration-stability"]],
            ["electrical-magnetic-transport", "load", ["emt-electrical-run"]],
        ],
    },
]


def main() -> int:
    lexicon = json.loads(LEXICON_PATH.read_text(encoding="utf-8"))["adapters"]
    registry_ids = {
        item["adapter_id"]
        for item in json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))["adapters"]
    }
    covered: set[str] = set()
    output_cases = []
    for case in CASES:
        decisions = []
        for adapter_id, status, signal_ids in case["decisions"]:
            known_signals = {
                item["signal_id"]: item for item in lexicon[adapter_id]["signals"]
            }
            if set(signal_ids) - set(known_signals):
                raise ValueError(f"unknown signal in {case['case_id']}/{adapter_id}")
            if status == "skip" and any(
                known_signals[signal_id]["strength"] != "exclusion"
                for signal_id in signal_ids
            ):
                raise ValueError(f"skip case lacks exclusion signal: {case['case_id']}/{adapter_id}")
            if status == "load" and not any(
                known_signals[signal_id]["strength"] == "strong"
                for signal_id in signal_ids
            ):
                raise ValueError(f"load case lacks strong signal: {case['case_id']}/{adapter_id}")
            covered.add(adapter_id)
            decisions.append(
                {
                    "adapter_id": adapter_id,
                    "ruleset_version": lexicon[adapter_id]["ruleset_version"],
                    "expected_status": status,
                    "expected_signal_ids": signal_ids,
                    "expected_reason_codes": [
                        code
                        for code in lexicon[adapter_id]["reason_codes"]
                        if f"-{status.upper()}-" in code
                    ],
                }
            )
        output_case = {key: value for key, value in case.items() if key != "decisions"}
        output_case["decisions"] = decisions
        output_case["review_status"] = "source-backed"
        output_case["review_note"] = (
            "Audited by the package authoring agent against accessible source text; "
            "not independently human-adjudicated gold."
        )
        output_cases.append(output_case)

    missing = sorted(registry_ids - covered)
    if missing:
        raise ValueError(f"source-backed catalog does not cover adapters: {missing}")
    output = {
        "catalog_version": "1.0.0",
        "created_at": "2026-08-06",
        "gold_status": "not-gold",
        "text_policy": "auditor paraphrase with source locators; consult the source for extraction",
        "adapter_coverage": sorted(covered),
        "cases": output_cases,
    }
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"WROTE {OUTPUT_PATH.name}: {len(output_cases)} sources covering {len(covered)} adapters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
