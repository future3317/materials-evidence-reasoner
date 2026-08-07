#!/usr/bin/env python3
"""Build synthetic adapter-routing regression cases."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "references" / "adapter-registry.json"
OUTPUT_PATH = ROOT / "references" / "adapter-benchmark-cases.json"
LEXICON_PATH = ROOT / "references" / "adapter-routing-lexicon.json"


CASES = {
    "superconductivity": {
        "load": [
            ("The target pellet reaches zero resistance and shows diamagnetic shielding below 18 K.", "superconductivity-assessment"),
            ("For the named phase, electron-phonon calculations predict a superconducting state under 120 GPa.", "superconducting-calculation"),
        ],
        "skip": [
            "A superconducting magnet supplies the field; the target is a normal-state semiconductor.",
            "Tc denotes the Curie temperature of the target ferromagnet.",
        ],
        "candidate": [
            "A resistance drop approaches the noise floor, but no second signal or interpretation is available.",
            "The abstract calls the family superconducting without binding evidence to the studied composition.",
        ],
    },
    "metallic-materials": {
        "load": [
            ("The target alloy composition, solution treatment, aging schedule and tensile response are reported.", "metallic-identity"),
            ("Powder lot, additive build parameters and grain texture are resolved for the nickel alloy specimens.", "metal-feedstock-state"),
        ],
        "skip": [
            "A stainless-steel sample holder supports the target ceramic and is not analyzed.",
            "Copper tape provides electrical contact but is outside the target scope.",
        ],
        "candidate": [
            "An unspecified commercial alloy was tested, but its role and grade are absent.",
            "The text names AA7075 only in a comparison sentence with no accessible method or result.",
        ],
    },
    "polymers": {
        "load": [
            ("Monomer ratio, catalyst, conversion and molecular-weight distribution are reported for the target polymer.", "polymerization-record"),
            ("The resin formulation, cure cycle, glass transition and tensile state are linked to cured specimens.", "polymer-state"),
        ],
        "skip": [
            "A polymer vial stores the target powder and is not part of the experiment.",
            "PVDF is an incidental binder while only the active inorganic particles are studied.",
        ],
        "candidate": [
            "A trade-name resin is mentioned without grade, composition or target role.",
            "The sample is called a polymer composite, but the accessible abstract has no formulation or specimen identity.",
        ],
    },
    "ceramics-glass-cement": {
        "load": [
            ("Batch oxides, powder forming, sintering schedule, phases and porosity are reported for the ceramic.", "inorganic-batch-composition"),
            ("Water-binder ratio, curing humidity, age and compressive strength are linked to the cement paste.", "cementitious-state"),
        ],
        "skip": [
            "An alumina crucible contains the target metal and is not analyzed.",
            "A glass slide is only the substrate for a polymer coating.",
        ],
        "candidate": [
            "The specimen is described only as a technical ceramic with no composition or role.",
            "Concrete performance is cited from another paper but the source boundary is unresolved.",
        ],
    },
    "liquid-materials": {
        "load": [
            ("Ionic-liquid composition, water content, temperature and viscosity are measured for the target mixture.", "liquid-composition-state"),
            ("The molten alloy oxygen activity, crucible, superheat and wetting behavior are reported.", "liquid-metal-state"),
        ],
        "skip": [
            "A water bath controls temperature but water is not a target material.",
            "Ethanol is used only to clean the specimen before testing.",
        ],
        "candidate": [
            "The word solution appears without composition, target binding or physical state.",
            "A commercial electrolyte is named but the accessible source does not identify formulation or role.",
        ],
    },
    "two-dimensional-materials": {
        "load": [
            ("Monolayer MoS2 thickness, substrate, transfer and device geometry are linked to the target channel.", "two-dimensional-identity"),
            ("Graphene flake size, layer distribution, defect mapping and assembled-film processing are reported.", "two-dimensional-structure-quality"),
        ],
        "skip": [
            "A two-dimensional plot displays bulk steel data; no 2D material is present.",
            "Bulk graphite is called layered, but no sheet, flake or 2D state is studied.",
        ],
        "candidate": [
            "The abstract says nanosheet without layer count, thickness or target-entity resolution.",
            "A 2D heterostructure is claimed, but the layer sequence and source evidence are inaccessible.",
        ],
    },
    "quantum-materials": {
        "load": [
            ("A topological invariant, band inversion and target-bound surface-state measurement support the claimed phase.", "topological-assessment"),
            ("Neutron and thermodynamic probes constrain a spin-liquid candidate and preserve competing explanations.", "ordered-state-assessment"),
        ],
        "skip": [
            "Quantum chemistry is used only as a calculation method for an ordinary molecule.",
            "Quantum efficiency refers to a photovoltaic device metric, not a quantum material phase.",
        ],
        "candidate": [
            "A single low-temperature anomaly is called quantum critical without scaling or phase-boundary evidence.",
            "The introduction labels the family topological, but no result is bound to the studied sample.",
        ],
    },
    "materials-processing": {
        "load": [
            ("The complete heating, hold, cooling and deformation sequence defines the target specimen state.", "thermal-history"),
            ("Machine, feedstock, build orientation, scan strategy and post-treatment are reported for the additive build.", "additive-manufacturing-process"),
        ],
        "skip": [
            "The purchased material is tested as received and no processing fact is reported.",
            "A preparation method appears only in an external citation outside the accessible source.",
        ],
        "candidate": [
            "Samples were prepared conventionally, with no ordered steps or referenced procedure.",
            "A heat treatment is mentioned but temperature, duration and target specimen are unresolved.",
        ],
    },
    "battery": {
        "load": [
            ("Coin-cell electrodes, loading, electrolyte, formation and cycling limits are linked to capacity retention.", "battery-test-protocol"),
            ("Pouch-cell hierarchy, pressure, reference capacity and calendar-aging conditions are reported.", "battery-component-hierarchy"),
        ],
        "skip": [
            "A battery powers the field sensor but is not a studied material or device.",
            "The target catalyst is compared with a cited battery electrode outside source scope.",
        ],
        "candidate": [
            "The electrode shows good cycling, but cell type, counter electrode and protocol are unavailable.",
            "A battery-material claim appears in the abstract without target component hierarchy or result evidence.",
        ],
    },
    "photovoltaic-device": {
        "load": [
            ("Layer stack, active area, illumination calibration and stabilized efficiency are reported for the solar cell.", "pv-device-stack"),
            ("The target module architecture and temperature-dependent J-V stability protocol are resolved.", "pv-measurement-protocol"),
        ],
        "skip": [
            "A photovoltaic panel powers the experiment and is not the target device.",
            "Optical absorption is discussed as future photovoltaic potential without fabricating a device.",
        ],
        "candidate": [
            "A high-efficiency solar cell is claimed without area, stack or measurement protocol.",
            "The material is screened for photovoltaics, but device fabrication and target centrality are unclear.",
        ],
    },
    "electrochemical-energy": {
        "load": [
            ("Catalyst loading, three-electrode geometry, reference scale and OER activity are reported.", "electrocatalyst-electrode"),
            ("Fuel-cell membrane, feeds, humidity, pressure and durability are linked to device performance.", "electrochemical-reactor"),
        ],
        "skip": [
            "Electrochemical polishing is only a specimen-preparation step and no energy conversion is studied.",
            "Battery cycling is the sole application and is routed to the battery adapter.",
        ],
        "candidate": [
            "The target is called an electrocatalyst without reaction, loading, reactor or result evidence.",
            "Energy conversion is mentioned, but the working entity and electrochemical configuration are unresolved.",
        ],
    },
    "hydrogen-storage": {
        "load": [
            ("Hydride activation, PCT isotherms, equilibrium criteria and reversible capacity are reported.", "hydrogen-sorption-assessment"),
            ("Adsorbent packing density, temperature range and usable volumetric hydrogen capacity are linked.", "hydrogen-storage-material"),
        ],
        "skip": [
            "Hydrogen is only the carrier gas during thermal processing.",
            "A structural alloy is used in a storage tank but hydrogen uptake is not investigated.",
        ],
        "candidate": [
            "Hydrogen uptake is stated without pressure, temperature, equilibrium rule or capacity basis.",
            "A storage-material family is cited, but the studied target and measurement are inaccessible.",
        ],
    },
    "thermoelectric": {
        "load": [
            ("Seebeck coefficient, conductivity and thermal conductivity on the same specimen yield ZT versus temperature.", "thermoelectric-performance"),
            ("Module contacts, orientation, power factor and stability are reported for the target thermoelectric leg.", "thermoelectric-state"),
        ],
        "skip": [
            "A thermocouple measures furnace temperature and is not the target material.",
            "Thermal conductivity alone is reported without a thermoelectric claim or device context.",
        ],
        "candidate": [
            "A Seebeck value is shown, but specimen identity and the thermoelectric objective are unclear.",
            "The abstract claims promising ZT without exposing derivation inputs or temperature conditions.",
        ],
    },
    "diffraction-scattering": {
        "load": [
            ("Target powder XRD acquisition and Rietveld refinement parameters support the phase assignment.", "structure-refinement"),
            ("SAXS q-range, background, model and size distribution are reported for the target dispersion.", "scattering-size-or-correlation-analysis"),
        ],
        "skip": [
            "An optical diffraction grating is part of the spectrometer apparatus.",
            "Diffraction-limited image resolution is discussed without a material scattering measurement.",
        ],
        "candidate": [
            "The text says XRD confirmed the phase but provides no pattern, method or target-bound result.",
            "Several peaks appear in an unlabeled figure whose sample identity cannot be resolved.",
        ],
    },
    "electron-microscopy-microanalysis": {
        "load": [
            ("STEM-EDS maps, acquisition settings and quantified composition are linked to a target grain.", "eds-composition-analysis"),
            ("EBSD indexing, cleanup, map resolution and grain statistics are reported for the specimen.", "ebsd-analysis"),
        ],
        "skip": [
            "The aluminum SEM stub is mounting hardware and not a target material.",
            "A carbon TEM grid supports the specimen but is not analyzed.",
        ],
        "candidate": [
            "An SEM image is mentioned with no accessible panel, scale or sample binding.",
            "Local composition is claimed from EDS, but the region and target phase are unresolved.",
        ],
    },
    "spectroscopy": {
        "load": [
            ("Raman excitation, spectral resolution, peak fit and target-mode assignments are reported.", "spectral-feature-analysis"),
            ("XPS calibration, background, line-shape constraints and oxidation-state alternatives are preserved.", "chemical-state-assessment"),
        ],
        "skip": [
            "A quartz spectrometer window is named only as apparatus.",
            "A literature spectrum is cited without measurement or extraction from the current source.",
        ],
        "candidate": [
            "Spectroscopy confirms bonding, but no technique, spectrum or target-bound feature is accessible.",
            "A peak assignment is stated without calibration, fit or sample identity.",
        ],
    },
    "thermal-analysis": {
        "load": [
            ("DSC cycle, rate, atmosphere, baseline and onset criterion define the target transition.", "thermal-transition-analysis"),
            ("TGA mass, gas program, blank correction and residue are reported for the specimen.", "mass-loss-analysis"),
        ],
        "skip": [
            "A furnace heating schedule is a synthesis step, not a thermal-analysis measurement.",
            "A thermocouple calibration checks the reactor and produces no target-material analysis.",
        ],
        "candidate": [
            "A DSC glass-transition value is quoted without trace, cycle, rate or source boundary.",
            "Mass loss is mentioned, but TGA use and target specimen are unresolved.",
        ],
    },
    "mechanical-testing": {
        "load": [
            ("Specimen geometry, strain measurement, rate and yield criterion are reported for tensile tests.", "monotonic-mechanical-test"),
            ("Fatigue waveform, R ratio, runout rule and censored cycle counts are resolved.", "fatigue-test"),
        ],
        "skip": [
            "A clamp applies pressure during another measurement and is not a mechanical property test.",
            "Elastic constants are computed by DFT only and belong to the simulation adapter.",
        ],
        "candidate": [
            "High strength is claimed without specimen geometry, test mode or result trace.",
            "Hardness is quoted from a supplier sheet whose method and target lot are unresolved.",
        ],
    },
    "electrical-magnetic-transport": {
        "load": [
            ("Four-probe geometry, current, dimensions and resistivity versus field are reported for the target.", "electrical-transport-analysis"),
            ("SQUID protocol, field direction, ZFC/FC history and magnetic moment normalization are resolved.", "magnetic-measurement-analysis"),
        ],
        "skip": [
            "Copper wire is used only as an electrical lead and is outside target scope.",
            "A superconducting magnet supplies field but no magnetic property of the target is measured.",
        ],
        "candidate": [
            "Resistance was measured, but contact geometry, target specimen and conditions are unavailable.",
            "A magnetic anomaly is shown without normalization, field history or entity binding.",
        ],
    },
    "electrochemical-testing": {
        "load": [
            ("CV potential scale, scan rate, electrode geometry and background correction are reported.", "voltammetry-analysis"),
            ("EIS frequency range, amplitude, equilibration, raw impedance and equivalent-circuit fit are preserved.", "eis-analysis"),
        ],
        "skip": [
            "A potentiostat model is listed for future work but no measurement was run.",
            "Electrochemical cleaning is only specimen preparation and produces no test result.",
        ],
        "candidate": [
            "Impedance improved, but frequency, amplitude, circuit and target run are missing.",
            "A polarization curve is mentioned without potential scale or electrode configuration.",
        ],
    },
    "composition-particle-surface": {
        "load": [
            ("ICP digestion, standards, calibration, interferences and target composition are reported.", "elemental-composition-analysis"),
            ("BET degassing, isotherm range, consistency checks and surface area are linked to the powder.", "gas-adsorption-and-porosity-analysis"),
        ],
        "skip": [
            "Carrier-gas composition is an instrument setting and not a target composition analysis.",
            "A calibration standard is measured only to check the instrument and is outside target scope.",
        ],
        "candidate": [
            "Elemental analysis agrees with nominal values, but method and quantitative results are inaccessible.",
            "Particle size is quoted without method, basis, dispersion state or target lot.",
        ],
    },
    "materials-simulation": {
        "load": [
            ("DFT code, functional, pseudopotentials, k mesh and convergence are reported for the target structure.", "electronic-structure-method"),
            ("Phase-field geometry, mesh, boundary conditions, solver and convergence outputs are preserved.", "continuum-and-mesoscale-method"),
        ],
        "skip": [
            "Simulation is proposed as future work and no actual run or output exists.",
            "A cited calculation is summarized without inputs, execution or current-source result.",
        ],
        "candidate": [
            "The property was calculated, but method, target entity and execution details are unresolved.",
            "A model curve is shown without distinguishing a fitted analytic model from a simulation run.",
        ],
    },
}


def match_signal_ids(text: str, spec: dict[str, object], expected_status: str) -> list[str]:
    normalized = text.casefold()
    matches: list[dict[str, object]] = []
    for signal_def in spec["signals"]:
        terms = (
            signal_def.get("terms_en", [])
            + signal_def.get("terms_zh", [])
            + signal_def.get("abbreviations", [])
            + signal_def.get("symbols", [])
        )
        if any(str(term).casefold() in normalized for term in terms):
            matches.append(signal_def)

    preferred = {
        "load": {"strong", "supporting"},
        "skip": {"exclusion"},
        "candidate": {"strong", "supporting", "weak"},
    }[expected_status]
    selected = [item for item in matches if item.get("strength") in preferred]
    if not selected:
        fallback_strengths = {
            "load": ("strong", "supporting"),
            "skip": ("exclusion",),
            "candidate": ("weak", "supporting", "strong"),
        }[expected_status]
        for strength in fallback_strengths:
            selected = [item for item in spec["signals"] if item.get("strength") == strength]
            if selected:
                break
    return [str(item["signal_id"]) for item in selected[:2]]


def reason_code(spec: dict[str, object], expected_status: str) -> str:
    token = {"load": "-LOAD-", "candidate": "-CANDIDATE-", "skip": "-SKIP-"}[expected_status]
    for code in spec["reason_codes"]:
        if token in code:
            return code
    raise ValueError(f"no reason code for {expected_status}")


def main() -> int:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    lexicon = json.loads(LEXICON_PATH.read_text(encoding="utf-8"))
    registry_ids = [adapter["adapter_id"] for adapter in registry["adapters"]]
    if set(registry_ids) != set(CASES):
        missing = sorted(set(registry_ids) - set(CASES))
        extra = sorted(set(CASES) - set(registry_ids))
        raise ValueError(f"benchmark/registry mismatch; missing={missing}, extra={extra}")

    cases: list[dict[str, object]] = []
    for adapter_id in registry_ids:
        adapter_cases = CASES[adapter_id]
        for expected_status in ("load", "skip", "candidate"):
            for index, item in enumerate(adapter_cases[expected_status], start=1):
                if expected_status == "load":
                    text, record_type = item
                    expected_record_types = [record_type]
                else:
                    text = item
                    expected_record_types = []
                routing_spec = lexicon["adapters"][adapter_id]
                expected_signal_ids = match_signal_ids(text, routing_spec, expected_status)
                signal_index = {
                    signal_def["signal_id"]: signal_def
                    for signal_def in routing_spec["signals"]
                }
                cases.append(
                    {
                        "case_id": f"{adapter_id}-{expected_status}-{index}",
                        "adapter_id": adapter_id,
                        "case_kind": "positive" if expected_status == "load" else (
                            "negative" if expected_status == "skip" else "ambiguous"
                        ),
                        "synthetic_source_text": text,
                        "source_type": "synthetic-regression",
                        "ruleset_version": routing_spec["ruleset_version"],
                        "expected_status": expected_status,
                        "expected_signal_ids": expected_signal_ids,
                        "expected_independence_groups": sorted(
                            {
                                signal_index[signal_id]["independence_group"]
                                for signal_id in expected_signal_ids
                            }
                        ),
                        "expected_reason_codes": [reason_code(routing_spec, expected_status)],
                        "expected_target_binding": True if expected_status == "load" else (
                            False if expected_status == "skip" else None
                        ),
                        "boundary_dimension": {
                            "load": "target-bound-method-or-result",
                            "skip": "excluded-role-or-context",
                            "candidate": "ambiguous-sense-binding-or-access",
                        }[expected_status],
                        "expected_record_types": expected_record_types,
                        "review_status": "provisional",
                    }
                )

    output = {
        "benchmark_version": "2.0.0",
        "purpose": "Synthetic routing regression; not a substitute for source-backed adjudicated gold.",
        "gold_status": "not-gold",
        "cases": cases,
    }
    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"WROTE {OUTPUT_PATH.name}: {len(cases)} cases for {len(registry_ids)} adapters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
