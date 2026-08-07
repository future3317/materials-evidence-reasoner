#!/usr/bin/env python3
"""Build the normative adapter routing lexicon and generated reference blocks."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_DIR = ROOT / "references"
LEXICON_PATH = REFERENCE_DIR / "adapter-routing-lexicon.json"
REGISTRY_PATH = REFERENCE_DIR / "adapter-registry.json"

DEFAULT_VALID = ["title", "abstract", "methods", "results", "figure-or-table", "conclusion"]
DEFAULT_INVALID = ["references", "cited-comparison", "future-work", "negated-claim"]


def signal(
    signal_id: str,
    concept: str,
    strength: str,
    terms_en: list[str],
    terms_zh: list[str],
    *,
    abbreviations: list[str] | None = None,
    symbols: list[str] | None = None,
    valid_contexts: list[str] | None = None,
    invalid_contexts: list[str] | None = None,
    requires_entity_binding: bool = True,
    independence_group: str | None = None,
) -> dict[str, Any]:
    return {
        "signal_id": signal_id,
        "concept": concept,
        "strength": strength,
        "terms_en": terms_en,
        "terms_zh": terms_zh,
        "abbreviations": abbreviations or [],
        "symbols": symbols or [],
        "valid_contexts": valid_contexts or DEFAULT_VALID,
        "invalid_contexts": invalid_contexts or DEFAULT_INVALID,
        "requires_entity_binding": requires_entity_binding,
        "independence_group": independence_group or signal_id,
    }


def adapter(
    label_zh: str,
    label_en: str,
    signals: list[dict[str, Any]],
    ambiguous_terms: list[tuple[str, list[str], str]],
    load_any_of: list[str],
    co_load: list[str],
) -> dict[str, Any]:
    prefix = signals[0]["signal_id"].split("-")[0].upper()
    return {
        "ruleset_version": "2.0.0",
        "canonical_label_zh": label_zh,
        "canonical_label_en": label_en,
        "signals": signals,
        "ambiguous_terms": [
            {"term": term, "possible_senses": senses, "resolution_rule": rule}
            for term, senses, rule in ambiguous_terms
        ],
        "load_gate": {
            "all_of": [
                "source identity is resolved",
                "at least one target entity is resolved",
                "at least one method-level or result-level signal is bound to the target",
                "all positive evidence is not fully explained by exclusion context",
            ],
            "any_of": load_any_of,
            "minimum_independent_groups": 1,
        },
        "candidate_gate": [
            "only weak or supporting vocabulary is available",
            "target entity binding is unresolved",
            "the accessible source is insufficient to resolve centrality or polarity",
            "a strong-looking term has an unresolved alternate sense",
        ],
        "skip_gate": [
            "all matches are apparatus, consumable, substrate, container, cited, negated, or future-work mentions",
            "the source is sufficiently complete and the studied target is outside this adapter scope",
        ],
        "co_load_suggestions": co_load,
        "reason_codes": {
            f"{prefix}-LOAD-TARGET": "Target-bound method or result evidence satisfies the load gate.",
            f"{prefix}-CANDIDATE-UNRESOLVED": "Domain possibility exists but binding, polarity, or centrality is unresolved.",
            f"{prefix}-SKIP-EXCLUDED": "All matched occurrences are explained by exclusion context.",
        },
    }


ADAPTERS: dict[str, dict[str, Any]] = {
    "superconductivity": adapter(
        "超导", "Superconductivity",
        [
            signal("sc-superconducting-claim", "direct superconducting claim", "strong", ["superconductivity", "superconductor", "superconducting behavior", "superconducting state", "superconducting transition", "bulk superconductivity", "supercurrent"], ["超导", "超导体", "超导行为", "超导态", "超导转变", "体超导", "超电流"], independence_group="sc-claim"),
            signal("sc-zero-resistance", "zero-resistance transport", "strong", ["zero resistance", "zero resistivity", "resistance below the noise floor"], ["零电阻", "零电阻率", "电阻低于噪声底"], symbols=["R=0", "rho=0"], independence_group="sc-transport"),
            signal("sc-diamagnetic-response", "Meissner or diamagnetic response", "strong", ["Meissner effect", "diamagnetic shielding", "flux expulsion"], ["迈斯纳效应", "抗磁屏蔽", "磁通排斥"], abbreviations=["ZFC", "FC"], independence_group="sc-magnetic"),
            signal("sc-thermodynamic-anomaly", "thermodynamic superconducting transition", "supporting", ["specific-heat jump", "heat-capacity anomaly"], ["比热跃变", "热容异常"], symbols=["Delta C"], independence_group="sc-thermodynamic"),
            signal("sc-characteristic-property", "superconducting characteristic property", "weak", ["critical field", "critical current", "superconducting gap", "vortex pinning"], ["临界场", "临界电流", "超导能隙", "磁通钉扎"], abbreviations=["Hc1", "Hc2", "Jc"], symbols=["Tc"], independence_group="sc-property"),
            signal("sc-apparatus-or-other-tc", "apparatus or alternate-symbol use", "exclusion", ["superconducting magnet", "Curie temperature", "crystallization temperature"], ["超导磁体", "居里温度", "结晶温度"], abbreviations=["Tc"], valid_contexts=["apparatus", "methods", "results"], invalid_contexts=[], requires_entity_binding=False, independence_group="sc-exclusion"),
        ],
        [("Tc", ["superconducting transition temperature", "Curie temperature", "crystallization temperature", "critical temperature in another domain"], "Resolve from the named phenomenon, measurement channel, units, and target entity; the symbol alone is weak."),
         ("Hc", ["thermodynamic critical field", "coercive field"], "Require superconducting context and field-temperature or Meissner evidence."),
         ("Jc", ["critical current density of a superconductor", "generic current density"], "Require an explicit superconducting criterion and geometry or model.")],
        ["an explicit target-bound superconducting claim appears in a result-bearing context", "two compatible independent evidence groups support the same target", "a theoretical paper explicitly predicts superconductivity for the target and is labeled theoretical"],
        ["electrical-magnetic-transport", "thermal-analysis", "quantum-materials", "materials-simulation"],
    ),
    "metallic-materials": adapter(
        "金属与合金", "Metallic materials",
        [
            signal("met-alloy-identity", "metal or alloy identity", "strong", ["metallic material", "metal specimen", "printed metal", "alloy grade", "steel grade", "superalloy", "intermetallic", "metallic glass"], ["金属材料", "金属试样", "打印金属", "合金牌号", "钢号", "高温合金", "金属间化合物", "金属玻璃"], abbreviations=["UNS"], independence_group="met-identity"),
            signal("met-metallurgical-state", "metallurgical state or microstructure", "strong", ["temper condition", "austenite", "martensite", "precipitation hardened", "recrystallized"], ["状态代号", "奥氏体", "马氏体", "沉淀强化", "再结晶"], independence_group="met-state"),
            signal("met-heat-or-melt", "heat, melt, or product lineage", "supporting", ["heat number", "melt number", "cast billet", "wrought plate", "forged bar"], ["炉号", "熔炼批次", "铸锭", "轧板", "锻棒"], independence_group="met-lineage"),
            signal("met-generic-metal", "generic metallic vocabulary", "weak", ["metal", "alloy", "foil", "wire", "steel"], ["金属", "合金", "箔", "丝", "钢"], independence_group="met-generic"),
            signal("met-apparatus", "incidental metallic component", "exclusion", ["sample holder", "copper wire", "stainless-steel fixture", "current collector", "metal substrate"], ["样品架", "铜导线", "不锈钢夹具", "集流体", "金属基底"], valid_contexts=["apparatus", "sample-mounting", "device-component"], invalid_contexts=[], requires_entity_binding=False, independence_group="met-exclusion"),
        ],
        [("steel", ["target engineering alloy", "apparatus or structural support", "figurative adjective"], "Load only when the steel entity itself has composition, process, structure, or property evidence."),
         ("foil", ["target metallic product", "current collector", "substrate or electrode component"], "Resolve the foil role in the entity hierarchy.")],
        ["target metal/alloy identity plus a target-bound composition, process, microstructure, or property result", "a target-bound metallurgical state is a study variable or conclusion"],
        ["materials-processing", "mechanical-testing", "electron-microscopy-microanalysis", "diffraction-scattering", "materials-simulation"],
    ),
    "polymers": adapter(
        "高分子材料", "Polymers",
        [
            signal("pol-polymer-identity", "polymer identity or architecture", "strong", ["polymer composite", "polymeric nanocomposite", "polymer film", "polymer matrix", "homopolymer", "copolymer", "thermoplastic", "thermoset", "elastomer", "polymer network"], ["聚合物复合材料", "高分子纳米复合材料", "聚合物薄膜", "聚合物基体", "均聚物", "共聚物", "热塑性塑料", "热固性树脂", "弹性体", "聚合物网络"], independence_group="pol-identity"),
            signal("pol-polymerization", "polymerization or curing", "strong", ["polymerization", "crosslinking", "curing reaction", "degree of conversion"], ["聚合", "交联", "固化反应", "转化率"], independence_group="pol-reaction"),
            signal("pol-molar-distribution", "molar-mass distribution", "supporting", ["number-average molar mass", "weight-average molar mass", "molar-mass dispersity", "gel permeation chromatography"], ["数均摩尔质量", "重均摩尔质量", "摩尔质量分散度", "凝胶渗透色谱"], abbreviations=["Mn", "Mw", "SEC", "GPC"], independence_group="pol-molar"),
            signal("pol-generic", "generic polymer vocabulary", "weak", ["polymer", "resin", "plastic", "binder", "film", "gel"], ["高分子", "树脂", "塑料", "粘结剂", "薄膜", "凝胶"], independence_group="pol-generic"),
            signal("pol-consumable", "incidental polymer component", "exclusion", ["polymer vial", "adhesive tape", "glove", "encapsulant only", "incidental binder"], ["塑料瓶", "胶带", "手套", "仅作封装", "非目标粘结剂"], valid_contexts=["apparatus", "sample-mounting", "consumable", "secondary-component"], invalid_contexts=[], requires_entity_binding=False, independence_group="pol-exclusion"),
        ],
        [("resin", ["target thermoset precursor", "generic trade-name material", "mounting resin"], "Require target role and formulation, cure, structure, or property evidence."),
         ("film", ["polymer specimen", "thin-film form of another material", "protective consumable"], "Resolve composition and target role before loading.")],
        ["target polymer identity plus formulation, polymerization, cure, morphology, or property evidence", "molar-mass or polymer-state evidence is bound to the target polymer"],
        ["materials-processing", "thermal-analysis", "mechanical-testing", "spectroscopy", "composition-particle-surface"],
    ),
    "ceramics-glass-cement": adapter(
        "陶瓷、玻璃与胶凝材料", "Ceramics, glass, and cementitious materials",
        [
            signal("cer-inorganic-product", "target inorganic nonmetallic product", "strong", ["advanced ceramic", "glass-ceramic", "refractory", "cement paste", "mortar", "concrete"], ["先进陶瓷", "玻璃陶瓷", "耐火材料", "水泥浆体", "砂浆", "混凝土"], independence_group="cer-identity"),
            signal("cer-forming-firing-curing", "ceramic, glass, or cement process", "strong", ["powder pressing", "sintering", "glass melting", "annealing point", "cement hydration", "curing age"], ["粉体压制", "烧结", "玻璃熔制", "退火点", "水泥水化", "养护龄期"], independence_group="cer-process"),
            signal("cer-state", "inorganic microstructure or state", "supporting", ["green body", "fired body", "vitreous phase", "clinker phase", "water-cement ratio"], ["生坯", "烧结体", "玻璃相", "熟料相", "水灰比"], abbreviations=["w/c", "w/b"], independence_group="cer-state"),
            signal("cer-generic", "generic ceramic vocabulary", "weak", ["ceramic", "glass", "cement", "oxide", "carbide", "nitride", "pellet"], ["陶瓷", "玻璃", "水泥", "氧化物", "碳化物", "氮化物", "陶瓷片"], independence_group="cer-generic"),
            signal("cer-apparatus", "incidental inorganic component", "exclusion", ["alumina crucible", "glass slide", "ceramic holder", "quartz window"], ["氧化铝坩埚", "玻璃载片", "陶瓷样品架", "石英窗口"], valid_contexts=["apparatus", "container", "substrate", "sample-mounting"], invalid_contexts=[], requires_entity_binding=False, independence_group="cer-exclusion"),
        ],
        [("glass", ["target amorphous material", "glass substrate or window", "glass fiber reinforcement"], "Resolve product role and whether glass-specific composition, process, state, or property is studied."),
         ("cement", ["hydraulic binder", "dental cement", "adhesive cement", "verb"], "Require a material entity and application-consistent evidence.")],
        ["target ceramic/glass/cement identity plus batch, forming, thermal history, curing, structure, or property evidence", "a domain-specific state such as green body, glass network, clinker/hydrate, or refractory is a study object"],
        ["materials-processing", "thermal-analysis", "mechanical-testing", "diffraction-scattering", "electron-microscopy-microanalysis"],
    ),
    "liquid-materials": adapter(
        "液体材料", "Liquid materials",
        [
            signal("liq-composition", "target liquid composition", "strong", ["ionic liquid", "molten salt", "liquid metal", "mixed solvent", "electrolyte formulation"], ["离子液体", "熔盐", "液态金属", "混合溶剂", "电解液配方"], independence_group="liq-composition"),
            signal("liq-state-property", "liquid state or transport property", "strong", ["liquid-liquid equilibrium", "viscosity", "rheology", "surface tension", "vapor pressure"], ["液液平衡", "黏度", "流变", "表面张力", "蒸气压"], independence_group="liq-state"),
            signal("liq-dispersion", "dispersion or slurry state", "supporting", ["dispersion stability", "slurry", "sedimentation", "zeta potential"], ["分散稳定性", "浆料", "沉降", "Zeta 电位"], independence_group="liq-dispersion"),
            signal("liq-generic", "generic liquid vocabulary", "weak", ["solution", "solvent", "liquid", "electrolyte", "melt"], ["溶液", "溶剂", "液体", "电解液", "熔体"], independence_group="liq-generic"),
            signal("liq-incidental-fluid", "incidental fluid", "exclusion", ["cleaning solvent", "water bath", "pressure medium", "carrier liquid", "immersion oil", "electrochemical test electrolyte not studied"], ["清洗溶剂", "水浴", "传压介质", "载液", "浸油", "仅作测试环境而未研究的电解液"], valid_contexts=["cleaning", "apparatus", "environment", "sample-preparation-only"], invalid_contexts=[], requires_entity_binding=False, independence_group="liq-exclusion"),
        ],
        [("solution", ["target formulated liquid", "temporary preparation medium", "mathematical solution"], "Require a liquid entity with composition, state, process, or property evidence."),
         ("electrolyte", ["target liquid material", "battery component", "electrochemical environment", "solid electrolyte"], "Route liquid form here and co-load application/measurement adapters as appropriate; solid electrolytes do not load this adapter.")],
        ["target liquid formulation or phase state is explicitly resolved", "a target-bound liquid thermophysical, transport, interfacial, or stability result is reported"],
        ["battery", "electrochemical-testing", "composition-particle-surface", "thermal-analysis", "polymers"],
    ),
    "two-dimensional-materials": adapter(
        "二维材料", "Two-dimensional materials",
        [
            signal("twod-layer-count", "defined one-to-few-layer material", "strong", ["monolayer", "bilayer", "few-layer", "single-layer graphene", "two-dimensional material"], ["单层", "双层", "少层", "单层石墨烯", "二维材料"], abbreviations=["1LG", "2LG", "FLG", "2D"], independence_group="twod-identity"),
            signal("twod-production-stack", "2D production or stacking", "strong", ["mechanical exfoliation", "liquid-phase exfoliation", "layer transfer", "van der Waals heterostructure", "twist angle"], ["机械剥离", "液相剥离", "层转移", "范德华异质结构", "扭转角"], independence_group="twod-production"),
            signal("twod-dimension-evidence", "thickness or layer-resolved evidence", "supporting", ["layer number", "flake thickness", "Raman layer identification", "atomic layer"], ["层数", "片层厚度", "拉曼层数判定", "原子层"], independence_group="twod-dimension"),
            signal("twod-generic", "generic dimensional vocabulary", "weak", ["2D", "layered", "nanosheet", "flake", "ultrathin"], ["二维", "层状", "纳米片", "薄片", "超薄"], independence_group="twod-generic"),
            signal("twod-false-sense", "non-material two-dimensional use", "exclusion", ["two-dimensional plot", "2D image", "two-dimensional simulation", "2D detector", "bulk layered crystal only"], ["二维图", "二维图像", "二维模拟", "二维探测器", "仅块体层状晶体"], valid_contexts=["data-visualization", "simulation-dimensionality", "instrument", "bulk-material"], invalid_contexts=[], requires_entity_binding=False, independence_group="twod-exclusion"),
        ],
        [("2D", ["two-dimensional material", "plot or image dimensionality", "simulation dimensionality", "detector geometry"], "Require a physical sheet/flake/layer entity or explicit material definition."),
         ("graphene", ["single-layer graphene", "few-layer graphene", "graphene oxide", "graphitic additive"], "Preserve the source term and layer evidence; do not normalize all graphene-related materials to graphene.")],
        ["a target physical sheet, flake, layer, heterostructure, or 2D device entity is resolved with layer/form evidence", "production or layer-dependent properties are central results"],
        ["quantum-materials", "materials-processing", "electron-microscopy-microanalysis", "spectroscopy", "electrical-magnetic-transport"],
    ),
    "quantum-materials": adapter(
        "量子材料", "Quantum materials",
        [
            signal("qmat-emergent-phase", "emergent quantum phase", "strong", ["quantum spin liquid", "heavy fermion", "Mott insulator", "quantum critical point", "Kondo lattice"], ["量子自旋液体", "重费米子", "莫特绝缘体", "量子临界点", "近藤晶格"], abbreviations=["QSL", "QCP"], independence_group="qmat-phase"),
            signal("qmat-topological", "topological electronic phase", "strong", ["topological insulator", "Weyl semimetal", "Dirac semimetal", "quantum anomalous Hall", "quantum spin Hall"], ["拓扑绝缘体", "外尔半金属", "狄拉克半金属", "量子反常霍尔", "量子自旋霍尔"], abbreviations=["QAHE", "QAH", "QSH"], independence_group="qmat-topology"),
            signal("qmat-quantized-transport", "quantized electronic transport state", "strong", ["quantum Hall effect", "Shubnikov-de-Haas oscillation", "Landau level quantization", "fractional quantum Hall"], ["量子霍尔效应", "舒勃尼科夫-德哈斯振荡", "朗道能级量子化", "分数量子霍尔"], abbreviations=["QHE", "SdH", "FQHE"], independence_group="qmat-quantized-transport"),
            signal("qmat-signature", "quantum-state signature", "supporting", ["topological invariant", "Berry phase", "edge state", "surface state", "non-Fermi liquid", "moiré correlated state"], ["拓扑不变量", "贝里相位", "边缘态", "表面态", "非费米液体", "莫尔关联态"], independence_group="qmat-signature"),
            signal("qmat-generic", "generic quantum vocabulary", "weak", ["quantum", "spin", "band inversion", "low-temperature anomaly", "correlated"], ["量子", "自旋", "能带反转", "低温异常", "关联"], independence_group="qmat-generic"),
            signal("qmat-other-quantum", "non-material quantum use", "exclusion", ["quantum chemistry method", "quantum efficiency", "quantum yield", "quantum computer", "instrument quantum limit"], ["量子化学方法", "量子效率", "量子产率", "量子计算机", "仪器量子极限"], valid_contexts=["method-name", "device-metric", "photochemistry", "instrument"], invalid_contexts=[], requires_entity_binding=False, independence_group="qmat-exclusion"),
        ],
        [("quantum", ["emergent material state", "calculation method", "optical efficiency/yield", "instrument principle"], "The word alone is weak; require a named phase/signature and target-bound evidence."),
         ("topological", ["electronic topology", "geometric morphology", "network topology"], "Require an electronic/magnetic invariant, state, or corresponding probe.")],
        ["a named quantum phase or topological class is a target-bound result with measurement or calculation evidence", "multiple probes or a probe-plus-model constrain an ordered state, excitation, topology, coherence, or phase diagram"],
        ["superconductivity", "two-dimensional-materials", "electrical-magnetic-transport", "spectroscopy", "materials-simulation"],
    ),
    "materials-processing": adapter(
        "材料加工", "Materials processing",
        [
            signal("proc-parameterized-step", "parameterized transformation step", "strong", ["heat treatment schedule", "solution treatment", "quenching", "hot rolling", "cold working", "sintering cycle", "spark plasma sintering", "slurry mixing", "electrode coating", "calendering"], ["热处理制度", "固溶处理", "淬火", "热轧", "冷加工", "烧结制度", "放电等离子烧结", "浆料混合", "电极涂布", "辊压"], abbreviations=["SPS"], independence_group="proc-step"),
            signal("proc-additive-or-joining", "additive manufacturing or joining process", "strong", ["additive manufacturing", "micro-scale additive manufacturing", "3D printing", "powder bed fusion", "directed energy deposition", "material extrusion", "welding", "brazing", "diffusion bonding"], ["增材制造", "微尺度增材制造", "三维打印", "粉末床熔融", "定向能量沉积", "材料挤出", "焊接", "钎焊", "扩散连接"], abbreviations=["PBF-LB", "DED", "AM"], independence_group="proc-special"),
            signal("proc-lineage", "input-output process lineage", "supporting", ["process route", "process chain", "feedstock to specimen", "post-processing", "build orientation"], ["工艺路线", "工艺链", "原料到试样", "后处理", "构建方向"], independence_group="proc-lineage"),
            signal("proc-generic", "generic preparation vocabulary", "weak", ["prepared", "fabricated", "treated", "processed", "synthesized"], ["制备", "制造", "处理", "加工", "合成"], independence_group="proc-generic"),
            signal("proc-not-executed", "non-executed or inaccessible process", "exclusion", ["as received", "procedure reported elsewhere", "future processing", "manufacturer proprietary process"], ["原样使用", "方法见其他文献", "未来加工", "厂家保密工艺"], valid_contexts=["methods", "cited-procedure", "future-work", "supplier-description"], invalid_contexts=[], requires_entity_binding=False, independence_group="proc-exclusion"),
        ],
        [("annealing", ["material transformation process", "instrument thermal equilibration", "data-algorithm annealing"], "Require a physical material input/output and actual temperature-time history."),
         ("fabricated", ["actual documented process", "unsupported summary verb"], "Without steps, parameters, or an accessible referenced procedure, remain candidate.")],
        ["an ordered target-material process with at least one reported parameter and input/output entity is present", "a process variable or lineage is required to interpret a target result"],
        ["metallic-materials", "polymers", "ceramics-glass-cement", "two-dimensional-materials", "materials-simulation"],
    ),
    "battery": adapter(
        "电池", "Battery",
        [
            signal("bat-cell-hierarchy", "battery cell or component hierarchy", "strong", ["battery cell", "battery electrode", "lithium-ion battery", "metal-ion battery", "half-cell", "full cell", "coin cell", "pouch cell", "positive electrode", "negative electrode", "separator"], ["电池单体", "电池电极", "锂离子电池", "金属离子电池", "半电池", "全电池", "扣式电池", "软包电池", "正极", "负极", "隔膜"], abbreviations=["LIB"], independence_group="bat-cell"),
            signal("bat-cycling", "battery cycling protocol and result", "strong", ["galvanostatic charge-discharge", "cycle life", "capacity retention", "C-rate", "state of charge", "state of health"], ["恒流充放电", "循环寿命", "容量保持率", "倍率", "荷电状态", "健康状态"], abbreviations=["GCD", "SOC", "SOH"], independence_group="bat-cycling"),
            signal("bat-practical-context", "battery balancing or inactive-material context", "supporting", ["N/P ratio", "electrolyte-to-capacity ratio", "areal loading", "formation cycle", "calendar ageing"], ["负正极容量比", "电解液容量比", "面载量", "化成循环", "日历老化"], abbreviations=["E/C"], independence_group="bat-context"),
            signal("bat-generic", "generic battery-component vocabulary", "weak", ["cathode", "anode", "electrolyte", "electrode", "capacity"], ["正极", "负极", "电解液", "电极", "容量"], independence_group="bat-generic"),
            signal("bat-other-use", "non-target battery mention", "exclusion", ["battery powered", "battery of tests", "cited battery electrode", "backup battery"], ["电池供电", "一系列测试", "引用的电池电极", "备用电池"], valid_contexts=["apparatus", "figurative-language", "cited-comparison"], invalid_contexts=[], requires_entity_binding=False, independence_group="bat-exclusion"),
        ],
        [("capacity", ["battery charge capacity", "adsorption capacity", "heat capacity", "production capacity"], "Require charge/discharge context, units, electrode/cell basis, and cycle index."),
         ("anode/cathode", ["battery electrode", "electrochemical cell electrode", "vacuum-tube/electronic component"], "Require a rechargeable/primary cell hierarchy or battery objective.")],
        ["a target battery cell/component hierarchy and a cycling, assembly, performance, ageing, or safety result are bound", "cell configuration plus battery-specific protocol is central to the source"],
        ["electrochemical-testing", "liquid-materials", "polymers", "materials-processing", "thermal-analysis"],
    ),
    "photovoltaic-device": adapter(
        "光伏器件", "Photovoltaic device",
        [
            signal("pv-device", "photovoltaic cell or module", "strong", ["solar cell", "photovoltaic device", "single-junction cell", "tandem solar cell", "PV module"], ["太阳电池", "光伏器件", "单结电池", "叠层太阳电池", "光伏组件"], abbreviations=["PV"], independence_group="pv-device"),
            signal("pv-jv-performance", "illuminated photovoltaic performance", "strong", ["current-voltage under illumination", "power conversion efficiency", "open-circuit voltage", "short-circuit current density", "fill factor"], ["光照电流电压", "光电转换效率", "开路电压", "短路电流密度", "填充因子"], abbreviations=["PCE", "Voc", "Jsc", "FF"], independence_group="pv-performance"),
            signal("pv-calibration-stability", "PV calibration or stability protocol", "supporting", ["AM1.5G", "solar simulator class", "stabilized power output", "external quantum efficiency", "maximum power point tracking"], ["AM1.5G", "太阳模拟器等级", "稳定功率输出", "外量子效率", "最大功率点跟踪"], abbreviations=["EQE", "MPPT"], independence_group="pv-protocol"),
            signal("pv-generic", "generic photovoltaic vocabulary", "weak", ["photovoltaic", "solar absorber", "photoactive layer", "solar energy"], ["光伏", "太阳能吸收层", "光活性层", "太阳能"], independence_group="pv-generic"),
            signal("pv-other-photo", "non-PV optical or power context", "exclusion", ["photocatalysis", "photoelectrochemical fuel production", "photoanode for water oxidation", "photodetector", "quantum yield", "solar panel powers the experiment", "future PV application"], ["光催化", "光电化学燃料制备", "用于水氧化的光阳极", "光探测器", "量子产率", "太阳能板供电", "未来光伏应用"], valid_contexts=["other-application", "apparatus", "future-work"], invalid_contexts=[], requires_entity_binding=False, independence_group="pv-exclusion"),
        ],
        [("efficiency", ["PV power conversion efficiency", "quantum efficiency", "energy efficiency of another device"], "Require PV device stack, illumination, area basis, and the named metric."),
         ("solar", ["photovoltaic device", "solar-thermal use", "photocatalysis", "illumination source"], "Require electrical power generation by a resolved device.")],
        ["a resolved PV device stack and illuminated electrical performance are reported", "PV calibration, stabilized output, or device stability is a central target result"],
        ["spectroscopy", "electrical-magnetic-transport", "materials-processing", "two-dimensional-materials"],
    ),
    "electrochemical-energy": adapter(
        "电化学能源转换", "Electrochemical energy conversion",
        [
            signal("ece-reaction", "energy-conversion electrochemical reaction", "strong", ["hydrogen evolution reaction", "oxygen evolution reaction", "oxygen reduction reaction", "carbon dioxide reduction", "nitrogen reduction reaction"], ["析氢反应", "析氧反应", "氧还原反应", "二氧化碳还原", "氮还原反应"], abbreviations=["HER", "OER", "ORR", "CO2RR", "NRR"], independence_group="ece-reaction"),
            signal("ece-reactor", "electrolyzer or fuel-cell reactor", "strong", ["water electrolyzer", "fuel cell", "membrane electrode assembly", "flow cell", "gas diffusion electrode"], ["水电解槽", "燃料电池", "膜电极组件", "流动电解池", "气体扩散电极"], abbreviations=["MEA", "GDE"], independence_group="ece-reactor"),
            signal("ece-performance", "electrocatalytic performance", "supporting", ["overpotential", "Tafel slope", "Faradaic efficiency", "turnover frequency", "mass activity"], ["过电位", "塔菲尔斜率", "法拉第效率", "转换频率", "质量活性"], abbreviations=["FE", "TOF"], independence_group="ece-performance"),
            signal("ece-generic", "generic electrocatalysis vocabulary", "weak", ["electrocatalyst", "electrochemical energy", "catalytic electrode", "activity"], ["电催化剂", "电化学能源", "催化电极", "活性"], independence_group="ece-generic"),
            signal("ece-other-electrochem", "non-energy-conversion electrochemical use", "exclusion", ["battery cycling only", "hydrogen storage only", "electroplating", "corrosion test", "electrochemical cleaning", "electrochemical sensor"], ["仅电池循环", "仅储氢", "电镀", "腐蚀测试", "电化学清洗", "电化学传感器"], valid_contexts=["other-application", "sample-preparation"], invalid_contexts=[], requires_entity_binding=False, independence_group="ece-exclusion"),
        ],
        [("activity", ["electrocatalytic rate metric", "chemical activity", "generic performance adjective"], "Require a named reaction, normalization basis, potential scale, and target electrode."),
         ("fuel cell", ["target energy device", "commercial power source used as apparatus"], "Require reactor/component/performance evidence for the studied device.")],
        ["a named energy-conversion reaction and target catalyst/electrode performance are bound", "a fuel-cell or electrolyzer reactor and its operating result are central"],
        ["electrochemical-testing", "composition-particle-surface", "liquid-materials", "materials-processing"],
    ),
    "hydrogen-storage": adapter(
        "储氢材料", "Hydrogen storage",
        [
            signal("h2s-storage-material", "materials-based hydrogen storage", "strong", ["hydrogen storage material", "hydrogen storage capacity", "metal hydride", "complex hydride", "chemical hydrogen storage", "hydrogen sorbent"], ["储氢材料", "储氢容量", "金属氢化物", "复杂氢化物", "化学储氢", "储氢吸附剂"], independence_group="h2s-material"),
            signal("h2s-sorption", "hydrogen sorption measurement", "strong", ["pressure-composition-temperature isotherm", "hydrogen absorption", "hydrogen desorption", "reversible hydrogen capacity", "van't Hoff analysis"], ["压力组成温度等温线", "吸氢", "放氢", "可逆储氢容量", "范特霍夫分析"], abbreviations=["PCT", "PCI"], independence_group="h2s-sorption"),
            signal("h2s-performance", "storage performance context", "supporting", ["gravimetric capacity", "volumetric capacity", "sorption kinetics", "equilibrium pressure", "cycle stability"], ["质量储氢容量", "体积储氢容量", "吸放氢动力学", "平衡压力", "循环稳定性"], independence_group="h2s-performance"),
            signal("h2s-generic", "generic hydrogen vocabulary", "weak", ["hydrogen", "hydride", "adsorption", "desorption", "uptake"], ["氢", "氢化物", "吸附", "脱附", "吸收量"], independence_group="h2s-generic"),
            signal("h2s-other-hydrogen", "non-storage hydrogen use", "exclusion", ["hydrogen carrier gas", "hydrogen evolution catalyst", "hydrogen embrittlement", "hydrogen atmosphere", "storage tank alloy only"], ["氢载气", "析氢催化剂", "氢脆", "氢气氛", "仅储罐合金"], valid_contexts=["environment", "other-application", "degradation", "apparatus"], invalid_contexts=[], requires_entity_binding=False, independence_group="h2s-exclusion"),
        ],
        [("uptake", ["hydrogen storage capacity", "generic gas adsorption", "biological uptake"], "Require hydrogen identity, pressure/temperature, capacity basis, and target material."),
         ("hydride", ["storage phase", "intermediate reaction product", "hydrogen embrittlement feature"], "Require storage objective or sorption/thermodynamic evidence.")],
        ["a target storage material and hydrogen sorption/capacity result are bound", "storage thermodynamics, kinetics, reversibility, or cycling is a central result"],
        ["composition-particle-surface", "thermal-analysis", "diffraction-scattering", "materials-simulation"],
    ),
    "thermoelectric": adapter(
        "热电材料与器件", "Thermoelectric materials and devices",
        [
            signal("te-zt", "thermoelectric figure of merit", "strong", ["thermoelectric figure of merit", "dimensionless figure of merit"], ["热电优值", "无量纲热电优值"], abbreviations=["zT", "ZT"], independence_group="te-figure"),
            signal("te-coupled-transport", "coupled thermoelectric transport", "strong", ["Seebeck coefficient and electrical conductivity", "power factor", "thermal conductivity and Seebeck"], ["塞贝克系数与电导率", "功率因子", "热导率与塞贝克系数"], symbols=["S", "sigma", "kappa"], independence_group="te-transport"),
            signal("te-device", "thermoelectric device performance", "supporting", ["thermoelectric module", "thermoelectric leg", "temperature difference power generation", "cooling coefficient of performance"], ["热电模块", "热电臂", "温差发电", "制冷性能系数"], abbreviations=["TEG", "TEC", "COP"], independence_group="te-device"),
            signal("te-generic", "generic thermoelectric vocabulary", "weak", ["thermoelectric", "Seebeck", "thermal transport", "electrical transport"], ["热电", "塞贝克", "热输运", "电输运"], independence_group="te-generic"),
            signal("te-instrument-or-other", "non-target thermoelectric use", "exclusion", ["thermocouple temperature sensor", "Peltier cooler used as apparatus", "spin Seebeck only", "single thermal conductivity result"], ["热电偶温度传感器", "帕尔贴制冷器作为设备", "仅自旋塞贝克", "单独热导率结果"], valid_contexts=["apparatus", "other-phenomenon", "single-property"], invalid_contexts=[], requires_entity_binding=False, independence_group="te-exclusion"),
        ],
        [("Seebeck", ["thermoelectric material property", "thermocouple principle", "spin Seebeck phenomenon"], "A single mention is supporting only; load when thermoelectric performance or a target thermoelectric state is central."),
         ("ZT", ["thermoelectric figure of merit", "unrelated acronym"], "Require the defining transport quantities or an explicit thermoelectric definition.")],
        ["zT or power factor is reported with target and temperature context", "at least two coupled transport quantities or a thermoelectric device result are central"],
        ["electrical-magnetic-transport", "thermal-analysis", "materials-processing", "materials-simulation"],
    ),
    "diffraction-scattering": adapter(
        "衍射与散射", "Diffraction and scattering",
        [
            signal("dif-actual-measurement", "actual diffraction or scattering measurement", "strong", ["powder X-ray diffraction", "single-crystal diffraction", "neutron diffraction", "small-angle X-ray scattering", "total scattering"], ["粉末 X 射线衍射", "单晶衍射", "中子衍射", "小角 X 射线散射", "总散射"], abbreviations=["XRD", "PXRD", "SAXS", "WAXS", "PDF"], independence_group="dif-measurement"),
            signal("dif-analysis", "diffraction/scattering analysis", "strong", ["Rietveld refinement", "Le Bail refinement", "Pawley refinement", "pair distribution function", "reciprocal-space map"], ["Rietveld 精修", "Le Bail 精修", "Pawley 精修", "对分布函数", "倒易空间图"], abbreviations=["RSM"], independence_group="dif-analysis"),
            signal("dif-data-feature", "target-bound scattering data", "supporting", ["diffraction peak", "scattering vector", "diffractogram", "structure factor", "phase fraction"], ["衍射峰", "散射矢量", "衍射图谱", "结构因子", "相分数"], symbols=["2theta", "q"], independence_group="dif-data"),
            signal("dif-generic", "generic diffraction vocabulary", "weak", ["diffraction", "scattering", "XRD confirmed", "peak"], ["衍射", "散射", "XRD 证实", "峰"], independence_group="dif-generic"),
            signal("dif-nonmaterial", "non-material diffraction use", "exclusion", ["diffraction grating", "diffraction-limited resolution", "XRD sample holder", "cited diffraction pattern"], ["衍射光栅", "衍射极限分辨率", "XRD 样品架", "引用的衍射图"], valid_contexts=["apparatus", "optics", "cited-comparison"], invalid_contexts=[], requires_entity_binding=False, independence_group="dif-exclusion"),
        ],
        [("PDF", ["pair distribution function", "portable document format", "probability density function"], "Resolve from scattering context, q/r ranges, and structural analysis."),
         ("peak", ["diffraction feature", "spectral feature", "thermal-analysis feature", "generic maximum"], "Require method and axis context.")],
        ["an actual target-bound diffraction/scattering run or data artifact is reported", "a structure, phase, size, correlation, or refinement result is derived from target-bound scattering data"],
        ["ceramics-glass-cement", "metallic-materials", "two-dimensional-materials", "materials-simulation"],
    ),
    "electron-microscopy-microanalysis": adapter(
        "电子显微与微区分析", "Electron microscopy and microanalysis",
        [
            signal("em-imaging", "actual electron microscopy imaging", "strong", ["scanning electron microscopy", "transmission electron microscopy", "scanning transmission electron microscopy", "high-resolution TEM"], ["扫描电子显微镜", "透射电子显微镜", "扫描透射电子显微镜", "高分辨透射电镜"], abbreviations=["SEM", "TEM", "STEM", "HRTEM"], independence_group="em-imaging"),
            signal("em-microanalysis", "electron-beam microanalysis", "strong", ["energy-dispersive X-ray spectroscopy", "electron energy-loss spectroscopy", "electron backscatter diffraction", "selected-area electron diffraction"], ["能量色散 X 射线谱", "电子能量损失谱", "电子背散射衍射", "选区电子衍射"], abbreviations=["EDS", "EDX", "EELS", "EBSD", "SAED"], independence_group="em-analysis"),
            signal("em-quantification", "image or map quantification", "supporting", ["orientation map", "elemental map", "segmentation", "particle-size distribution", "grain map"], ["取向图", "元素面分布", "图像分割", "粒径分布", "晶粒图"], independence_group="em-quant"),
            signal("em-generic", "generic microscopy vocabulary", "weak", ["micrograph", "electron image", "microscopy", "mapping"], ["显微图", "电子图像", "显微观察", "面扫描"], independence_group="em-generic"),
            signal("em-support", "microscopy support or apparatus", "exclusion", ["TEM grid", "SEM stub", "carbon coating for imaging", "electron microscope cited only"], ["TEM 载网", "SEM 样品台", "仅用于成像的喷碳", "仅引用电子显微镜"], valid_contexts=["sample-mounting", "apparatus", "cited-method"], invalid_contexts=[], requires_entity_binding=False, independence_group="em-exclusion"),
        ],
        [("mapping", ["elemental/orientation map", "generic spatial mapping", "mathematical mapping"], "Require an electron microscopy modality and target-bound artifact."),
         ("carbon coating", ["target coating", "conductive preparation layer"], "Do not assign the preparation coating to target composition unless explicitly studied.")],
        ["a target-bound electron image, spectrum, diffraction pattern, or map is available with an actual run", "quantification or interpretation derives from target-bound electron microscopy data"],
        ["composition-particle-surface", "diffraction-scattering", "metallic-materials", "two-dimensional-materials"],
    ),
    "spectroscopy": adapter(
        "光谱与能谱", "Spectroscopy",
        [
            signal("spec-actual-technique", "actual spectroscopy measurement", "strong", ["Raman spectroscopy", "infrared spectroscopy", "X-ray photoelectron spectroscopy", "X-ray absorption spectroscopy", "nuclear magnetic resonance"], ["拉曼光谱", "红外光谱", "X 射线光电子能谱", "X 射线吸收谱", "核磁共振"], abbreviations=["Raman", "FTIR", "XPS", "XAS", "NMR"], independence_group="spec-measurement"),
            signal("spec-feature-analysis", "spectral feature analysis", "strong", ["peak fitting", "binding-energy calibration", "chemical shift", "absorption edge", "photoluminescence lifetime"], ["峰拟合", "结合能校准", "化学位移", "吸收边", "光致发光寿命"], independence_group="spec-analysis"),
            signal("spec-data", "target-bound spectrum or assignment", "supporting", ["spectrum", "band assignment", "vibrational mode", "oxidation-state assignment", "optical transition"], ["光谱", "谱带归属", "振动模式", "氧化态归属", "光学跃迁"], independence_group="spec-data"),
            signal("spec-generic", "generic spectral vocabulary", "weak", ["spectroscopy", "spectral", "band", "peak", "signal"], ["光谱学", "谱学", "谱带", "峰", "信号"], independence_group="spec-generic"),
            signal("spec-apparatus", "spectroscopy apparatus or cited result", "exclusion", ["spectrometer window", "optical filter", "laser specification", "literature spectrum"], ["光谱仪窗口", "滤光片", "激光器参数", "文献光谱"], valid_contexts=["apparatus", "source-description", "cited-comparison"], invalid_contexts=[], requires_entity_binding=False, independence_group="spec-exclusion"),
        ],
        [("band", ["spectral band", "electronic band", "mechanical band", "range"], "Resolve from the measurement axis, technique, and analysis object."),
         ("NMR", ["nuclear magnetic resonance", "unrelated acronym"], "Require a spectroscopy method, nucleus, field, or spectrum.")],
        ["an actual target-bound spectrum or spectroscopy run is reported", "a target chemical, vibrational, electronic, optical, or magnetic-state result derives from spectral data"],
        ["composition-particle-surface", "quantum-materials", "two-dimensional-materials", "materials-simulation"],
    ),
    "thermal-analysis": adapter(
        "热分析", "Thermal analysis",
        [
            signal("ta-actual-technique", "actual thermal-analysis run", "strong", ["differential scanning calorimetry", "thermogravimetric analysis", "thermomechanical analysis", "dynamic mechanical analysis", "dilatometry"], ["差示扫描量热", "热重分析", "热机械分析", "动态力学分析", "膨胀法"], abbreviations=["DSC", "TGA", "TG", "TMA", "DMA"], independence_group="ta-measurement"),
            signal("ta-transition", "thermal-analysis transition or mass-loss result", "strong", ["glass-transition onset", "melting enthalpy", "crystallization peak", "mass-loss step", "residue fraction"], ["玻璃化转变起始", "熔融焓", "结晶峰", "失重台阶", "残余质量分数"], independence_group="ta-result"),
            signal("ta-protocol", "thermal-analysis program", "supporting", ["heating rate", "cooling cycle", "purge gas", "baseline correction", "isoconversional analysis"], ["升温速率", "降温循环", "吹扫气体", "基线校正", "等转化率分析"], independence_group="ta-protocol"),
            signal("ta-generic", "generic thermal vocabulary", "weak", ["thermal analysis", "Tg", "decomposition temperature", "thermal stability"], ["热分析", "玻璃化温度", "分解温度", "热稳定性"], symbols=["Tg"], independence_group="ta-generic"),
            signal("ta-process-heating", "non-thermal-analysis heating or thermal property", "exclusion", ["furnace heat treatment", "synthesis heating schedule", "reactor temperature control", "thermocouple calibration", "thermal conductivity measurement only", "service temperature only"], ["炉内热处理", "合成升温程序", "反应器控温", "热电偶校准", "仅热导率测量", "仅服役温度"], valid_contexts=["materials-processing", "synthesis", "apparatus", "transport-property"], invalid_contexts=[], requires_entity_binding=False, independence_group="ta-exclusion"),
        ],
        [("Tg", ["glass-transition temperature by DSC", "glass-transition temperature by DMA", "unresolved literature value"], "Preserve method and criterion; DMA and DSC values are not interchangeable."),
         ("thermal stability", ["TGA mass-loss resistance", "service-temperature claim", "generic adjective"], "Require a defined measurand, method, and temperature/time criterion.")],
        ["an actual target-bound DSC/TG/TMA/DMA/dilatometry run is reported", "a thermal transition, mass-loss, thermomechanical, dynamic-mechanical, or kinetic result derives from that run"],
        ["polymers", "ceramics-glass-cement", "materials-processing", "thermoelectric"],
    ),
    "mechanical-testing": adapter(
        "力学测试", "Mechanical testing",
        [
            signal("mech-actual-test", "actual mechanical test", "strong", ["tensile test", "compression test", "flexural test", "hardness test", "nanoindentation"], ["拉伸试验", "压缩试验", "弯曲试验", "硬度试验", "纳米压痕"], independence_group="mech-test"),
            signal("mech-durability-test", "fatigue, creep, fracture, or wear test", "strong", ["fatigue test", "creep rupture", "fracture toughness", "crack-growth test", "wear test"], ["疲劳试验", "蠕变断裂", "断裂韧度", "裂纹扩展试验", "磨损试验"], independence_group="mech-durability"),
            signal("mech-curve-property", "mechanical curve or criterion", "supporting", ["stress-strain curve", "yield criterion", "S-N curve", "load-displacement curve", "runout"], ["应力应变曲线", "屈服判据", "S-N 曲线", "载荷位移曲线", "未失效截止"], independence_group="mech-data"),
            signal("mech-generic", "generic mechanical vocabulary", "weak", ["strength", "modulus", "hardness", "load", "strain"], ["强度", "模量", "硬度", "载荷", "应变"], independence_group="mech-generic"),
            signal("mech-nontest", "non-test mechanical context", "exclusion", ["clamping load", "stack pressure", "computed elastic constant only", "mechanical support", "mixing shear"], ["夹紧载荷", "堆叠压力", "仅计算弹性常数", "机械支撑", "混合剪切"], valid_contexts=["apparatus", "environment", "simulation-only", "processing"], invalid_contexts=[], requires_entity_binding=False, independence_group="mech-exclusion"),
        ],
        [("strength", ["measured mechanical strength", "signal intensity", "qualitative performance adjective"], "Require test mode, specimen, geometry, conditions, and a property result."),
         ("load", ["mechanical test load", "material loading fraction", "electrical load", "process charge"], "Resolve units and method context.")],
        ["an actual target-bound mechanical test and specimen are resolved", "a target mechanical property or failure result derives from a defined test mode"],
        ["metallic-materials", "polymers", "ceramics-glass-cement", "materials-processing", "electron-microscopy-microanalysis"],
    ),
    "electrical-magnetic-transport": adapter(
        "电学、磁学与输运", "Electrical, magnetic, and transport measurements",
        [
            signal("emt-electrical-run", "actual electrical or Hall transport run", "strong", ["four-probe resistivity", "van der Pauw", "Hall measurement", "quantum Hall effect", "Shubnikov-de-Haas oscillation", "magnetoresistance", "current-voltage characteristic"], ["四探针电阻率", "范德堡法", "霍尔测量", "量子霍尔效应", "舒勃尼科夫-德哈斯振荡", "磁阻", "电流电压特性"], abbreviations=["I-V", "MR", "QHE", "SdH"], independence_group="emt-electrical"),
            signal("emt-magnetic-run", "actual magnetic measurement", "strong", ["SQUID magnetometry", "vibrating sample magnetometry", "magnetic susceptibility", "magnetization loop", "zero-field-cooled"], ["SQUID 磁测量", "振动样品磁强计", "磁化率", "磁滞回线", "零场冷却"], abbreviations=["SQUID", "VSM", "ZFC", "FC"], independence_group="emt-magnetic"),
            signal("emt-transport-result", "transport result and geometry", "supporting", ["resistivity versus temperature", "carrier concentration", "mobility", "thermal conductivity", "Seebeck coefficient"], ["电阻率温度曲线", "载流子浓度", "迁移率", "热导率", "塞贝克系数"], independence_group="emt-result"),
            signal("emt-generic", "generic transport vocabulary", "weak", ["resistance", "conductivity", "magnetic", "transport", "current"], ["电阻", "电导", "磁性", "输运", "电流"], independence_group="emt-generic"),
            signal("emt-apparatus", "electrical or magnetic apparatus component", "exclusion", ["copper lead wire", "superconducting magnet supplies field", "electrical heater", "contact metal only"], ["铜引线", "超导磁体供场", "电加热器", "仅接触金属"], valid_contexts=["apparatus", "sample-mounting", "environment"], invalid_contexts=[], requires_entity_binding=False, independence_group="emt-exclusion"),
        ],
        [("conductivity", ["electrical conductivity", "ionic conductivity", "thermal conductivity"], "Resolve the transported quantity, geometry, frequency, and conditions."),
         ("magnetic", ["target magnetic property", "applied magnetic field", "magnetic apparatus"], "Require a measured target response for magnetic records.")],
        ["an actual target-bound electrical, Hall, magnetic, dielectric, thermal, or thermoelectric transport run is reported", "a transport property is derived with geometry and condition context"],
        ["superconductivity", "thermoelectric", "quantum-materials", "two-dimensional-materials"],
    ),
    "electrochemical-testing": adapter(
        "电化学测试", "Electrochemical testing",
        [
            signal("echem-sweep-step", "actual voltammetric or chrono method", "strong", ["cyclic voltammetry", "linear sweep voltammetry", "chronoamperometry", "chronopotentiometry", "rotating disk electrode"], ["循环伏安", "线性扫描伏安", "计时电流", "计时电位", "旋转圆盘电极"], abbreviations=["CV", "LSV", "CA", "CP", "RDE", "RRDE"], independence_group="echem-dc"),
            signal("echem-impedance-pulse", "actual impedance or intermittent-titration method", "strong", ["electrochemical impedance spectroscopy", "galvanostatic intermittent titration", "potentiostatic intermittent titration", "corrosion polarization"], ["电化学阻抗谱", "恒流间歇滴定", "恒电位间歇滴定", "腐蚀极化"], abbreviations=["EIS", "GITT", "PITT"], independence_group="echem-impedance"),
            signal("echem-cell-context", "electrochemical cell and potential context", "supporting", ["working electrode", "reference electrode", "counter electrode", "potential scale", "iR compensation"], ["工作电极", "参比电极", "对电极", "电位标尺", "iR 补偿"], independence_group="echem-context"),
            signal("echem-generic", "generic electrochemical vocabulary", "weak", ["electrochemical", "impedance", "polarization", "electrode", "potential"], ["电化学", "阻抗", "极化", "电极", "电位"], independence_group="echem-generic"),
            signal("echem-not-test", "non-test electrochemical use", "exclusion", ["electrochemical cleaning", "electropolishing preparation", "potentiostat listed for future work", "cited EIS result"], ["电化学清洗", "电解抛光制样", "未来使用电化学工作站", "引用的 EIS 结果"], valid_contexts=["sample-preparation", "future-work", "cited-comparison"], invalid_contexts=[], requires_entity_binding=False, independence_group="echem-exclusion"),
        ],
        [("CV", ["cyclic voltammetry", "coefficient of variation", "curriculum vitae"], "Require an electrochemical potential-current scan and cell context."),
         ("EIS", ["electrochemical impedance spectroscopy", "unrelated acronym"], "Require frequency-dependent complex impedance or an explicit electrochemical method.")],
        ["an actual target-bound electrochemical run with cell/electrode context is reported", "a property or fit derives from target-bound electrochemical data"],
        ["battery", "electrochemical-energy", "liquid-materials", "composition-particle-surface"],
    ),
    "composition-particle-surface": adapter(
        "组成、颗粒与表界面常规分析", "Composition, particle, and surface analysis",
        [
            signal("cps-composition", "actual composition or separation analysis", "strong", ["inductively coupled plasma mass spectrometry", "X-ray fluorescence", "elemental analysis", "size-exclusion chromatography", "gas chromatography"], ["电感耦合等离子体质谱", "X 射线荧光", "元素分析", "体积排阻色谱", "气相色谱"], abbreviations=["ICP-MS", "ICP-OES", "XRF", "SEC", "GC", "LC"], independence_group="cps-composition"),
            signal("cps-particle-surface", "actual particle or surface measurement", "strong", ["dynamic light scattering", "laser diffraction particle size", "gas adsorption", "BET surface area", "contact angle"], ["动态光散射", "激光衍射粒度", "气体吸附", "BET 比表面积", "接触角"], abbreviations=["DLS", "BET"], independence_group="cps-particle"),
            signal("cps-quantification", "quantitative analysis context", "supporting", ["calibration curve", "detection limit", "recovery", "particle-size distribution", "adsorption isotherm"], ["校准曲线", "检出限", "回收率", "粒径分布", "吸附等温线"], abbreviations=["LOD", "LOQ"], independence_group="cps-quant"),
            signal("cps-generic", "generic composition or surface vocabulary", "weak", ["composition", "particle size", "surface area", "porosity", "density", "wetting"], ["组成", "粒径", "比表面积", "孔隙", "密度", "润湿"], independence_group="cps-generic"),
            signal("cps-nontarget", "calibration or environmental composition", "exclusion", ["carrier gas composition", "instrument calibration standard only", "supplier nominal composition only", "contact liquid not studied"], ["载气组成", "仅仪器校准标准", "仅供应商名义成分", "非目标接触液"], valid_contexts=["apparatus", "calibration-only", "secondary-source", "environment"], invalid_contexts=[], requires_entity_binding=False, independence_group="cps-exclusion"),
        ],
        [("BET", ["Brunauer-Emmett-Teller surface-area analysis", "unrelated acronym"], "Require a gas adsorption isotherm, fit range, and target powder/porous entity."),
         ("composition", ["target measured composition", "nominal recipe", "gas/environment composition"], "Preserve measurement status and bind to the correct entity or environment.")],
        ["an actual target-bound composition, chromatography, particle, adsorption, density, or wetting run is reported", "a quantitative result derives from a named method with calibration/model context"],
        ["liquid-materials", "polymers", "battery", "electron-microscopy-microanalysis"],
    ),
    "materials-simulation": adapter(
        "材料模拟", "Materials simulation",
        [
            signal("sim-electronic-atomistic", "executed electronic or atomistic simulation", "strong", ["density functional theory calculation", "ab initio molecular dynamics", "classical molecular dynamics", "Monte Carlo simulation"], ["密度泛函理论计算", "第一性原理分子动力学", "经典分子动力学", "蒙特卡洛模拟"], abbreviations=["DFT", "AIMD", "MD", "MC"], independence_group="sim-atomistic"),
            signal("sim-meso-continuum", "executed thermodynamic, mesoscale, or continuum simulation", "strong", ["CALPHAD calculation", "phase-field simulation", "finite-element simulation", "finite-volume simulation", "discrete-element simulation"], ["CALPHAD 计算", "相场模拟", "有限元模拟", "有限体积模拟", "离散元模拟"], abbreviations=["FEM", "FVM", "DEM"], independence_group="sim-continuum"),
            signal("sim-provenance", "simulation execution provenance", "supporting", ["input file", "code version", "convergence criterion", "boundary condition", "training split", "random seed"], ["输入文件", "代码版本", "收敛判据", "边界条件", "训练集划分", "随机种子"], independence_group="sim-provenance"),
            signal("sim-generic", "generic calculation vocabulary", "weak", ["calculated", "simulated", "modeled", "predicted", "machine learning"], ["计算得到", "模拟", "建模", "预测", "机器学习"], abbreviations=["ML"], independence_group="sim-generic"),
            signal("sim-not-executed", "non-executed or non-simulation model", "exclusion", ["future simulation", "software capability", "cited calculation", "analytic fit only", "schematic model"], ["未来模拟", "软件功能", "引用的计算", "仅解析拟合", "示意模型"], valid_contexts=["future-work", "software-description", "cited-comparison", "analysis-only"], invalid_contexts=[], requires_entity_binding=False, independence_group="sim-exclusion"),
        ],
        [("model", ["executed numerical simulation", "analytical fit", "conceptual mechanism", "machine-learning model"], "Classify the model role and require actual inputs, execution, and outputs for simulation records."),
         ("calculated", ["current-source simulation output", "derived arithmetic value", "cited result"], "Require method, target, and execution provenance; arithmetic derivation belongs to property derivation, not simulation.")],
        ["an actual simulation job has target-bound inputs, method details, and outputs", "a materials-ML model has a defined dataset, split, task, validation, and target property"],
        ["metallic-materials", "quantum-materials", "materials-processing", "diffraction-scattering"],
    ),
}


# The large object above is retained as a bootstrap fallback for older
# checkouts. From 4.7 onward the editable, normative source is the JSON
# lexicon itself; the build step must never overwrite it from Python literals.
NORMATIVE_ADAPTERS: dict[str, dict[str, Any]] = {}


def load_normative_lexicon() -> dict[str, Any]:
    try:
        lexicon = json.loads(LEXICON_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read normative routing lexicon: {exc}") from exc
    if not isinstance(lexicon, dict) or not isinstance(lexicon.get("adapters"), dict):
        raise ValueError("normative routing lexicon must contain adapters object")
    for adapter_id, spec in lexicon["adapters"].items():
        if not isinstance(adapter_id, str) or not isinstance(spec, dict):
            raise ValueError("routing lexicon adapter IDs and definitions must be objects")
        if not spec.get("signals") or not spec.get("load_gate"):
            raise ValueError(f"routing lexicon adapter is incomplete: {adapter_id}")
    return lexicon


def _compact_terms(signal_def: dict[str, Any]) -> str:
    terms = signal_def["terms_zh"] + signal_def["terms_en"]
    terms += signal_def.get("abbreviations", []) + signal_def.get("symbols", [])
    return "、".join(f"`{term}`" for term in terms)


def render_routing_block(adapter_id: str, *, heading_level: int, adapters: dict[str, dict[str, Any]] | None = None) -> str:
    spec = (adapters or NORMATIVE_ADAPTERS or ADAPTERS)[adapter_id]
    begin = f"<!-- BEGIN GENERATED ROUTING CONTRACT: {adapter_id} -->"
    end = f"<!-- END GENERATED ROUTING CONTRACT: {adapter_id} -->"
    hashes = "#" * heading_level
    strength_zh = {
        "strong": "强",
        "supporting": "辅助",
        "weak": "弱/召回",
        "exclusion": "排除",
    }
    lines = [
        begin,
        f"{hashes} 机器可执行路由合同",
        "",
        f"本节由 `scripts/build_adapter_assets.py` 生成，与 `adapter-routing-lexicon.json` 中 "
        f"`{adapter_id}` / `{spec['ruleset_version']}` 同步。关键词命中只负责召回；最终判定必须完成语境、极性、目标实体和文章中心性检查。",
        "",
        "| 等级 | signal_id / 概念 | 术语与符号 | 有效证据要求 |",
        "|---|---|---|---|",
    ]
    for signal_def in spec["signals"]:
        binding = "必须绑定目标实体" if signal_def["requires_entity_binding"] else "用于排除或消歧"
        contexts = "、".join(signal_def["valid_contexts"])
        lines.append(
            f"| {strength_zh[signal_def['strength']]} | `{signal_def['signal_id']}` / "
            f"{signal_def['concept']} | {_compact_terms(signal_def)} | {binding}；有效语境：{contexts} |"
        )

    lines += [
        "",
        "**歧义词消解**",
        "",
    ]
    for item in spec["ambiguous_terms"]:
        senses = " / ".join(item["possible_senses"])
        lines.append(f"- `{item['term']}`：候选含义为 {senses}。判定规则：{item['resolution_rule']}")

    lines += [
        "",
        "**状态门控**",
        "",
        "- `load`：来源与目标实体已解析；至少一个方法级或结果级信号绑定目标；排除语境不能解释全部阳性证据；并满足下列任一领域条件：",
    ]
    lines.extend(f"  - {condition}" for condition in spec["load_gate"]["any_of"])
    lines += [
        "- `candidate`：只有弱/辅助词、实体绑定不清、全文不可得、极性未决，或强术语仍有未消除的异义；只保留路由证据，不生成领域记录。",
        "- `skip`：完整来源足以判定该领域不是目标，或全部命中均属于仪器、耗材、基底、容器、引文、否定及未来工作语境。",
        f"- 推荐组合加载：{', '.join(f'`{item}`' for item in spec['co_load_suggestions']) or '无'}。每个适配器仍须独立满足门控。",
        "",
        "**记录生成门**：只有 `load` 才能按本文件的记录类型创建 `domain_records[]`；字段必须符合 `adapter-field-contracts.json`，引用已有核心实体/工艺/测量/产物/属性 ID，并提供字段级证据。未报告值保持缺失，不用典型值补齐。",
        end,
    ]
    return "\n".join(lines)


def synchronize_registry() -> dict[str, Any]:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    source_catalog_path = REFERENCE_DIR / "source-backed-routing-cases.json"
    source_coverage: set[str] = set()
    if source_catalog_path.is_file():
        source_catalog = json.loads(source_catalog_path.read_text(encoding="utf-8"))
        source_coverage = set(source_catalog.get("adapter_coverage", []))
    registry["registry_version"] = "2.0.0"
    registry["updated_at"] = "2026-08-06"
    registry["execution_standard"] = "adapter-execution-standard.md"
    registry["routing_lexicon"] = "adapter-routing-lexicon.json"
    registry["routing_lexicon_schema"] = "adapter-routing-lexicon.schema.json"
    registry["field_contract_catalog"] = "adapter-field-contracts.json"
    registry["field_contract_schema"] = "adapter-field-contracts.schema.json"
    registry["registry_schema"] = "adapter-registry.schema.json"
    registry["source_backed_catalog"] = "source-backed-routing-cases.json"
    registry["standards_and_sources"] = "standards-and-sources.md"
    registry["status_definitions"] = {
        "implemented": (
            "The reference, routing lexicon, semantic field or payload contract, package validation, "
            "and regression cases are present. Domain records may be emitted after a load decision."
        ),
        "specified": (
            "The scope is documented but one or more executable assets are incomplete; do not emit domain records."
        ),
        "planned": "Candidate scope only; do not emit domain records.",
    }
    registry["verification_status_definitions"] = {
        "provisional": "Machine and synthetic checks only; no claim of human-adjudicated gold accuracy.",
        "source-backed": "At least one accessible real source has been run and audited, without independent gold adjudication.",
        "human-adjudicated": "A frozen source set and expected outputs were independently adjudicated under the benchmark protocol.",
    }
    for entry in registry["adapters"]:
        adapter_id = entry["adapter_id"]
        entry["status"] = "implemented"
        if entry.get("verification_status") != "human-adjudicated":
            entry["verification_status"] = (
                "source-backed" if adapter_id in source_coverage else "provisional"
            )
        entry["ruleset_version"] = "2.0.0"
        entry["routing_lexicon_ref"] = f"adapter-routing-lexicon.json#/adapters/{adapter_id}"
        if adapter_id != "superconductivity":
            entry["field_contract_ref"] = f"adapter-field-contracts.json#/adapters/{adapter_id}"
    REGISTRY_PATH.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return registry


def synchronize_reference_ruleset(text: str, adapter_id: str) -> str:
    if adapter_id == "superconductivity":
        return re.sub(r"^(Ruleset version:\s*)`[^`]+`", r"\g<1>`2.0.0`", text, count=1, flags=re.MULTILINE)
    return re.sub(
        rf"^(.*适配器：`{re.escape(adapter_id)}`.*规则版本：)`[^`]+`",
        r"\g<1>`2.0.0`",
        text,
        count=1,
        flags=re.MULTILINE,
    )


def update_reference_blocks(adapters: dict[str, dict[str, Any]]) -> tuple[int, int]:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    references: dict[str, list[str]] = {}
    for entry in registry["adapters"]:
        references.setdefault(entry["reference"], []).append(entry["adapter_id"])

    changed = 0
    inserted = 0
    for reference_name, adapter_ids in references.items():
        path = REFERENCE_DIR / reference_name
        text = path.read_text(encoding="utf-8")
        for adapter_id in adapter_ids:
            text = synchronize_reference_ruleset(text, adapter_id)
            block = render_routing_block(
                adapter_id,
                heading_level=3 if len(adapter_ids) > 1 else 2,
                adapters=adapters,
            )
            pattern = re.compile(
                rf"<!-- BEGIN GENERATED ROUTING CONTRACT: {re.escape(adapter_id)} -->.*?"
                rf"<!-- END GENERATED ROUTING CONTRACT: {re.escape(adapter_id)} -->",
                flags=re.DOTALL,
            )
            if pattern.search(text):
                new_text = pattern.sub(lambda _: block, text, count=1)
            else:
                anchor = re.compile(
                    rf"^(.*(?:适配器：|Adapter ID:\s*)`{re.escape(adapter_id)}`.*)$",
                    flags=re.MULTILINE,
                )
                if not anchor.search(text):
                    raise ValueError(f"routing block anchor not found: {reference_name}/{adapter_id}")
                new_text = anchor.sub(lambda match: f"{match.group(1)}\n\n{block}", text, count=1)
                inserted += 1
            if new_text != text:
                changed += 1
                text = new_text
        path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return changed, inserted


def main() -> int:
    lexicon = load_normative_lexicon()
    NORMATIVE_ADAPTERS.update(lexicon["adapters"])
    synchronize_registry()
    changed, inserted = update_reference_blocks(NORMATIVE_ADAPTERS)
    print(
        f"WROTE {LEXICON_PATH.name}: {len(NORMATIVE_ADAPTERS)} adapters, "
        f"{sum(len(item['signals']) for item in NORMATIVE_ADAPTERS.values())} signals; "
        f"updated {changed} reference blocks ({inserted} new)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
