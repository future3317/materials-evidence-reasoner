# Superconductivity Adapter

Adapter ID: `superconductivity`

<!-- BEGIN GENERATED ROUTING CONTRACT: superconductivity -->
## 机器可执行路由合同

本节由 `scripts/build_adapter_assets.py` 生成，与 `adapter-routing-lexicon.json` 中 `superconductivity` / `2.0.0` 同步。关键词命中只负责召回；最终判定必须完成语境、极性、目标实体和文章中心性检查。

| 等级 | signal_id / 概念 | 术语与符号 | 有效证据要求 |
|---|---|---|---|
| 强 | `sc-superconducting-claim` / direct superconducting claim | `超导`、`超导体`、`超导行为`、`超导态`、`超导转变`、`体超导`、`超电流`、`superconductivity`、`superconductor`、`superconducting behavior`、`superconducting state`、`superconducting transition`、`bulk superconductivity`、`supercurrent` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 强 | `sc-zero-resistance` / zero-resistance transport | `零电阻`、`零电阻率`、`电阻低于噪声底`、`zero resistance`、`zero resistivity`、`resistance below the noise floor`、`R=0`、`rho=0` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 强 | `sc-diamagnetic-response` / Meissner or diamagnetic response | `迈斯纳效应`、`抗磁屏蔽`、`磁通排斥`、`Meissner effect`、`diamagnetic shielding`、`flux expulsion`、`ZFC`、`FC` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 辅助 | `sc-thermodynamic-anomaly` / thermodynamic superconducting transition | `比热跃变`、`热容异常`、`specific-heat jump`、`heat-capacity anomaly`、`Delta C` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 弱/召回 | `sc-characteristic-property` / superconducting characteristic property | `临界场`、`临界电流`、`超导能隙`、`磁通钉扎`、`critical field`、`critical current`、`superconducting gap`、`vortex pinning`、`Hc1`、`Hc2`、`Jc`、`Tc` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 排除 | `sc-apparatus-or-other-tc` / apparatus or alternate-symbol use | `超导磁体`、`居里温度`、`结晶温度`、`superconducting magnet`、`Curie temperature`、`crystallization temperature`、`Tc` | 用于排除或消歧；有效语境：apparatus、methods、results |

**歧义词消解**

- `Tc`：候选含义为 superconducting transition temperature / Curie temperature / crystallization temperature / critical temperature in another domain。判定规则：Resolve from the named phenomenon, measurement channel, units, and target entity; the symbol alone is weak.
- `Hc`：候选含义为 thermodynamic critical field / coercive field。判定规则：Require superconducting context and field-temperature or Meissner evidence.
- `Jc`：候选含义为 critical current density of a superconductor / generic current density。判定规则：Require an explicit superconducting criterion and geometry or model.

**状态门控**

- `load`：来源与目标实体已解析；至少一个方法级或结果级信号绑定目标；排除语境不能解释全部阳性证据；并满足下列任一领域条件：
  - an explicit target-bound superconducting claim appears in a result-bearing context
  - two compatible independent evidence groups support the same target
  - a theoretical paper explicitly predicts superconductivity for the target and is labeled theoretical
- `candidate`：只有弱/辅助词、实体绑定不清、全文不可得、极性未决，或强术语仍有未消除的异义；只保留路由证据，不生成领域记录。
- `skip`：完整来源足以判定该领域不是目标，或全部命中均属于仪器、耗材、基底、容器、引文、否定及未来工作语境。
- 推荐组合加载：`electrical-magnetic-transport`, `thermal-analysis`, `quantum-materials`, `materials-simulation`。每个适配器仍须独立满足门控。

**记录生成门**：只有 `load` 才能按本文件的记录类型创建 `domain_records[]`；字段必须符合 `adapter-field-contracts.json`，引用已有核心实体/工艺/测量/产物/属性 ID，并提供字段级证据。未报告值保持缺失，不用典型值补齐。
<!-- END GENERATED ROUTING CONTRACT: superconductivity -->
Ruleset version: `2.0.0`

Use this adapter to route and extract superconductivity-specific evidence without adding superconductivity fields to the materials core.

## 1. Scope

Supported profiles:

- `experimental-materials`: full routing and extraction for synthesized, processed, or measured material systems;
- `theoretical-materials`: predicted superconducting state, gap, pairing, and calculation records without claiming experimental confirmation;
- `simulation-screening`: candidate rankings and predicted properties with model applicability and validation;
- `device-or-application`: load only when the user's target includes superconducting material properties, interfaces, or fabrication rather than device function alone;
- `review-or-commentary`: use for discovery or synthesis only; do not treat summarized values as primary experimental evidence;
- `mixed`: separate experimental, theoretical, and device claims by evidence and entity.

The adapter does not prove superconductivity merely by loading. It records what the source reports, how the claim is supported, and which entity carries it.

## 2. Candidate Vocabulary

Vocabulary is a recall mechanism, not the final decision.

### 2.1 Direct domain terms

English:

- `superconductivity`
- `superconducting`
- `superconductor`
- `superconducting state`
- `superconducting transition`
- `high-temperature superconductivity`
- `unconventional superconductivity`
- `bulk superconductivity`
- `filamentary superconductivity`
- `interface superconductivity`
- `proximity-induced superconductivity`

Chinese:

- `超导`
- `超导态`
- `超导体`
- `超导转变`
- `高温超导`
- `非常规超导`
- `体超导`
- `丝状超导`
- `界面超导`
- `近邻诱导超导`

An affirmed direct term in a title, abstract, results heading, figure caption, or conclusion is a strong candidate signal. A term in an introduction, cited comparison, reference title, apparatus description, or negated sentence is not sufficient.

### 2.2 Hallmark transport signals

- zero resistance or zero resistivity tied to a target sample;
- a resistive transition identified by the authors as superconducting;
- transition suppression or broadening under magnetic field;
- current-dependent destruction of a zero-resistance state;
- superconducting critical current or switching current in a scoped superconducting sample;
- Andreev-reflection features explicitly interpreted as superconducting.

Zero resistance alone is not definitive. Some non-superconducting systems can show a zero-resistance state, and contact or analysis artifacts can mimic a transition.

### 2.3 Hallmark magnetic and thermodynamic signals

- Meissner effect or magnetic-flux expulsion;
- diamagnetic shielding or screening assigned to superconductivity;
- ZFC/FC susceptibility transition assigned to superconductivity;
- superconducting volume or shielding fraction;
- specific-heat jump or entropy anomaly at the same transition;
- superfluid density or phase stiffness associated with the superconducting state;
- reversible magnetization or mixed-state behavior interpreted as superconducting.

ZFC/FC, diamagnetism, and susceptibility anomalies also occur in non-superconducting magnetic systems. Require author context, entity binding, and compatible temperature behavior.

### 2.4 Characteristic properties and mechanisms

- `Tc`, `T_c`, onset, midpoint, zero-resistance temperature;
- `Hc`, `Hc1`, `Hc2`, `Hc3`, upper or lower critical field;
- `Jc`, critical current density, depairing current;
- superconducting gap, `Delta`, gap ratio, coherence peak;
- gap symmetry, nodes, order parameter, pairing symmetry;
- Cooper pair, pairing interaction, pairing mechanism;
- penetration depth `lambda`, coherence length `xi`, Ginzburg-Landau parameter `kappa`;
- flux pinning, vortex lattice, vortex liquid, vortex melting, irreversibility field;
- BCS, Eliashberg, WHH, Ginzburg-Landau, Bogoliubov-de Gennes;
- Josephson effect, proximity effect, flux quantization when attached to the target system.

These terms are strong only in superconductivity context. Symbols and method names alone are weak.

### 2.5 Family hints

Family names improve recall but never establish a property:

- cuprate, iron pnictide, iron chalcogenide, nickelate;
- heavy-fermion, organic superconductor, hydride superconductor;
- MgB2, NbN, NbTi, Nb3Sn, YBCO, BSCCO, FeSe and related families;
- infinite-layer, kagome, twisted-graphene, Chevrel-phase, A15 when used in superconductivity context.

A paper may study synthesis, magnetism, normal-state transport, degradation, or a non-superconducting composition in one of these families. Do not load from family name alone.

## 3. Ambiguity and Exclusion Rules

Do not treat these as superconductivity evidence without explicit context:

- `Tc`: Curie temperature, crystallization temperature, crossover temperature, or generic critical temperature;
- `Hc`: coercive field in magnetism;
- `Jc`: generic current density, solar-cell short-circuit current, or device limit;
- `gap`: semiconductor band gap, pseudogap, spin gap, or generic energy gap;
- `SC`: sample code, short circuit, single crystal, or unrelated abbreviation;
- `lambda` and `xi`: generic wavelength, eigenvalue, correlation length, or fitting parameter;
- `critical field`: breakdown, coercive, switching, or phase-transition field unrelated to superconductivity;
- `zero resistance`: quantum Hall, microwave-induced, contact-short, percolative, or undefined zero-resistance state;
- `SQUID`: magnetometer or device name without a superconducting-material claim;
- `superconducting magnet`: field-generation apparatus;
- `cryogenic`, `low temperature`, `diamagnetic`, `ZFC`, or `FC` alone.

Exclusion contexts:

- all matches occur only in introduction, references, related-work tables, or quoted literature;
- the only superconducting material is an electrode, magnet, sensor, substrate, or facility component outside target scope;
- the source explicitly reports no superconductivity and the task is not to capture negative evidence;
- the source only predicts a possibility but the current profile is experimental confirmation;
- the paper is quantum computing, circuit engineering, or device operation with no requested material-property extraction;
- accessible content is too incomplete to bind the signal to an entity.

Negative results remain useful. A target material reported as non-superconducting down to a measured lower temperature may produce a domain record only when the adapter is loaded for a superconductivity-focused question and the measurement boundary is explicit.

## 4. Routing Algorithm

Apply in order:

1. **User intent gate.** An explicit superconductivity request opens candidate evaluation but does not force `load` for every source.
2. **Candidate scan.** Search title, abstract, keywords, section headings, results, captions, and conclusion for direct, hallmark, weak, and exclusion signals.
3. **Polarity and context.** Mark each signal `affirmed`, `negated`, `hypothetical`, `cited`, or `unclear`.
4. **Entity binding.** Attach signals to the exact material, sample, interface, film, device region, or control.
5. **Centrality.** Classify superconductivity as primary, secondary, incidental, or unclear.
6. **Independence.** Count independent evidence channels, not merely multiple values derived from one curve.
7. **Profile.** Separate experimental evidence from theoretical prediction and device behavior.
8. **Decision.** Return `load`, `candidate`, or `skip` with gates, reason codes, and evidence IDs.

### 4.1 Load

Use `load` when either condition is satisfied:

- an affirmed direct superconductivity term is central and linked to target-entity result evidence; or
- at least two compatible, independent hallmark evidence channels are linked to the same target entity.

Examples of independent combinations:

- transport transition plus magnetic shielding;
- transport transition plus specific-heat anomaly;
- magnetic response plus a spectroscopic superconducting gap;
- phase-coherent Josephson or flux-quantization evidence plus another target-bound superconducting signal.

Not independent:

- onset and zero temperatures from the same resistivity curve;
- `Tc` and `Hc2` when `Hc2` is fitted only from that same transition dataset;
- a text claim and figure caption describing the same measurement;
- two model outputs sharing the same inputs and assumption.

### 4.2 Candidate

Use `candidate` when:

- a direct term is present but only abstract or snippet evidence is accessible;
- one hallmark signal exists but entity binding or interpretation is incomplete;
- the article is central to superconductivity but the target sample is unclear;
- a family hint and weak signal co-occur without decisive result evidence;
- theory predicts superconductivity but the requested classification is experimental.

Candidate mode may output the routing decision and missing information. It must not emit superconductivity `domain_records[]`.

### 4.3 Skip

Use `skip` when all signals are incidental, apparatus-only, background-only, cited-only, outside target scope, or explained by a non-superconducting meaning.

## 5. Routing Reason Codes

Positive:

- `SC-DIRECT-TERM`
- `SC-TRANSPORT-TRANSITION`
- `SC-ZERO-RESISTANCE`
- `SC-MEISSNER`
- `SC-DIAMAGNETIC-SHIELDING`
- `SC-THERMODYNAMIC-ANOMALY`
- `SC-SPECTROSCOPIC-GAP`
- `SC-CRITICAL-FIELD`
- `SC-CRITICAL-CURRENT`
- `SC-PHASE-COHERENCE`
- `SC-SAME-ENTITY`
- `SC-PRIMARY-CENTRALITY`

Exclusion or uncertainty:

- `SC-BACKGROUND-ONLY`
- `SC-APPARATUS-ONLY`
- `SC-CITED-ONLY`
- `SC-NEGATED`
- `SC-HYPOTHETICAL-ONLY`
- `SC-ENTITY-AMBIGUOUS`
- `SC-TERM-AMBIGUOUS`
- `SC-DEVICE-ONLY`
- `SC-SOURCE-INCOMPLETE`
- `SC-INSUFFICIENT-INDEPENDENT-EVIDENCE`

## 6. Superconductivity Assessment

After routing `load`, classify each target entity separately:

- `reported-superconducting`: the source affirmatively reports superconductivity with identified evidence;
- `candidate-superconducting`: evidence is suggestive but incomplete or disputed;
- `non-superconducting-in-measured-range`: no superconducting transition was observed within explicitly reported measurement limits;
- `predicted-superconducting`: theoretical or simulation result without experimental confirmation;
- `conflicting`: source evidence or entity assignments conflict;
- `not-assessable`: accessible evidence cannot support a classification.

Do not convert `reported-superconducting` into independent confirmation by the Skill. Record the authors' claim and the audited evidence state.

Recommended `superconductivity-assessment` fields:

- `classification`
- `evidence_channel_count`
- `evidence_channels`
- `transition_consistency`
- `bulk_or_nonbulk_claim`
- `measurement_lower_bound`
- `limitations`
- `property_record_ids`

## 7. Domain Record Types

Numerical values belong in core `property_records[]`. Domain records reference those IDs and add superconductivity semantics, criteria, and evidence synthesis. In the catalogs below, `property_record_ids` refers to the domain-record envelope, not a duplicate key inside `fields`.

### 7.1 `superconducting-transition`

Use for one scoped transition and one criterion. Split records when criterion, method, field, pressure, direction, sample, or transition branch differs.

Fields:

- `property_record_ids`: transition temperature records;
- `transition_role`: `onset`, `midpoint`, `zero-resistance`, `magnetic-onset`, `thermodynamic`, `gap-closing`, `author-defined`, `unknown`;
- `measurement_channel`: `resistance`, `resistivity`, `conductivity`, `susceptibility`, `magnetization`, `specific-heat`, `spectroscopy`, `microwave`, `mutual-inductance`, `other`;
- `criterion_raw`: exact author criterion;
- `criterion_canonical`: normalized criterion when unambiguous;
- `applied_field`, `field_direction`, `pressure`, `current`, `current_density`, `frequency`, `heating_or_cooling`: value or condition references;
- `transition_width_property_id`;
- `figure_or_table_evidence_ids`;
- `author_interpretation`;
- `limitations`.

Do not assume zero field, ambient pressure, a criterion, or the meaning of `Tc`.

### 7.2 `magnetic-superconducting-response`

Fields:

- `response_type`: `Meissner`, `diamagnetic-screening`, `shielding`, `ZFC-FC-transition`, `reversible-magnetization`, `other`;
- `property_record_ids`: susceptibility, magnetization, shielding fraction, or transition values;
- `protocol`: ZFC, FC, field history, sweep direction, frequency, and demagnetization correction when reported;
- `field_condition`;
- `volume_fraction_basis`;
- `background_subtraction`;
- `same_transition_as`: linked transition record ID when supported;
- `limitations`.

Do not infer bulk superconductivity from a small diamagnetic feature without the authors' basis, volume fraction, geometry, and alternative explanations.

### 7.3 `thermodynamic-superconducting-response`

Fields:

- `response_type`: `specific-heat-jump`, `entropy-anomaly`, `condensation-energy`, `other`;
- `property_record_ids`;
- `background_model`;
- `normalization_basis`;
- `field_condition`;
- `same_transition_as`;
- `limitations`.

### 7.4 `critical-field`

Fields:

- `field_type`: `Hc`, `Hc1`, `Hc2`, `Hc3`, `irreversibility-field`, `other`;
- `property_record_ids`;
- `temperature_condition`;
- `field_direction`;
- `measurement_channel`;
- `criterion_raw`;
- `derivation_model`: WHH, Ginzburg-Landau, extrapolation, fit, or author-defined;
- `measured_or_extrapolated`;
- `fit_range`;
- `limitations`.

An extrapolated `Hc2(0)` is `derived`, not directly reported measurement, even when the paper presents it as a fitted result.

### 7.5 `critical-current-density`

Fields:

- `property_record_ids`;
- `method`: `transport`, `magnetic-Bean-model`, `magneto-optical`, `other`;
- `criterion_raw`;
- `temperature_condition`;
- `field_condition`;
- `field_direction`;
- `current_direction`;
- `sample_geometry`;
- `cross_section_basis`;
- `model_or_formula`;
- `limitations`.

Do not compare `Jc` across transport and magnetic methods, geometries, fields, or temperatures without explicit conditioning.

### 7.6 `superconducting-gap`

Fields:

- `property_record_ids`: gap magnitude, gap ratio, or multiple-gap values;
- `gap_count`;
- `gap_symmetry`: exact author-supported candidates such as s-wave, d-wave, s+/-; retain ambiguity;
- `node_status`: full, nodal, anisotropic, mixed, unknown;
- `measurement_or_calculation_method`: STM/STS, ARPES, point-contact, optical, Raman, specific heat, penetration depth, muSR, DFT, Eliashberg, other;
- `fit_model`;
- `temperature_condition`;
- `momentum_or_direction`;
- `author_claim_strength`: measured, fitted, inferred, proposed, predicted;
- `limitations`.

Do not turn a generic energy gap, pseudogap, or band gap into a superconducting gap.

### 7.7 `superconducting-length-scale`

Fields:

- `quantity`: `penetration-depth`, `coherence-length`, `GL-parameter`, `mean-free-path`, `other`;
- `property_record_ids`;
- `direction`;
- `temperature_condition`;
- `method`;
- `measured_or_derived`;
- `input_property_record_ids`;
- `limitations`.

### 7.8 `vortex-and-pinning`

Fields:

- `phenomenon`: `flux-pinning`, `vortex-lattice`, `vortex-liquid`, `vortex-melting`, `creep`, `irreversibility`, `peak-effect`, `other`;
- `pinning_centers`;
- `property_record_ids`;
- `temperature_condition`;
- `field_condition`;
- `field_direction`;
- `measurement_method`;
- `mechanism_status`: observed, fitted, inferred, proposed;
- `limitations`.

### 7.9 `superconducting-phase-diagram`

Fields:

- `figure_evidence_ids`;
- `control_variables`: doping, pressure, field, strain, thickness, gate voltage, temperature, disorder, or other;
- `phase_boundaries`;
- `superconducting_dome_status`;
- `raw_data_available`;
- `digitization_status`;
- `limitations`.

Do not read exact phase boundaries from a schematic without calibrated axes and explicit digitization status.

### 7.10 `pairing-and-mechanism`

Fields:

- `pairing_mechanism`: phonon-mediated, spin-fluctuation, charge-fluctuation, orbital-fluctuation, excitonic, mixed, unknown, or raw author term;
- `gap_symmetry_claims`;
- `mechanism_chain`;
- `support_evidence_ids`;
- `counterevidence_ids`;
- `unique_predictions`;
- `falsifiers`;
- `claim_status`: measured-support, calculation-support, inferred, proposed, speculative, conflicting;
- `applicability`;
- `limitations`.

Background mechanisms and textbook descriptions do not become claims about the target material. Correlation, fit quality, or agreement with one model is not unique mechanism proof.

### 7.11 `competing-or-coexisting-order`

Fields:

- `order_type`: charge-density-wave, spin-density-wave, nematic, magnetic, structural, pseudogap, pair-density-wave, other;
- `relationship`: competing, coexisting, preceding, induced, uncertain;
- use envelope `entity_ids` for the scoped order or phase;
- `property_record_ids`;
- `support_evidence_ids`;
- `claim_status`;
- `limitations`.

Only include an order when the source explicitly connects it to the superconducting system. A mere fluctuation or generic mention is not a competing order.

### 7.12 `superconducting-calculation`

Fields:

- `method`: DFT, DFT+U, DMFT, Eliashberg, BCS, BdG, QMC, functional-RG, model-Hamiltonian, other;
- `software_and_version`;
- `model_parameters`;
- use envelope `property_record_ids` for predicted property values;
- `training_or_calibration_domain`;
- `validation_evidence_ids`;
- `assumptions`;
- `prediction_status`;
- `limitations`.

Software capability or a method cited in the introduction is not evidence that the calculation was performed.

## 8. Material Tuning and Sample Splitting

The following are core material/process records, not superconductivity-only top-level fields:

- cation or anion substitution;
- oxygen nonstoichiometry, vacancies, interstitials, and intercalation;
- electrostatic gating and interface charge transfer;
- carrier concentration;
- secondary and impurity phases;
- film, substrate, multilayer, interface, and superlattice structure;
- synthesis and processing conditions.

The adapter may reference these records when interpreting superconductivity. Split entities or runs when composition, doping, oxygen content, pressure, field history, thickness, substrate, anneal, irradiation, aging, or other state-changing conditions differ.

Do not infer carrier type or concentration from nominal substitution unless the source explicitly supports the mapping.

## 9. Figures and Curves

Recognize but do not overinterpret:

- resistance/resistivity versus temperature, field, pressure, or current;
- magnetic susceptibility or magnetization versus temperature or field;
- specific heat and entropy curves;
- `Hc2(T)`, `Jc(B,T)`, penetration-depth, muSR, microwave, thermal-conductivity, Nernst, and Hall data;
- STM/STS, ARPES, Raman, optical conductivity, neutron, XRD, TEM, and phase diagrams.

For each figure or curve record figure and panel, axes, units, legend, variable mapping, conditions, entity assignment, raw-data availability, digitization status, and evidence. Do not infer a legend, field direction, pressure, or criterion from visual similarity.

## 10. Hard Audit

Before accepting superconductivity records, check:

- signals belong to the target entity rather than a control, electrode, substrate, adjacent layer, or cited material;
- a direct term is affirmed rather than negated, hypothetical, or background-only;
- `Tc` criterion and measurement channel are explicit;
- zero field and ambient pressure were not silently inserted;
- onset, midpoint, and zero values were not merged;
- transport, magnetic, thermodynamic, and spectroscopic channels are counted independently;
- fitted or extrapolated values are marked derived;
- `Hc`, `Jc`, gap, `SC`, `lambda`, and `xi` are not ambiguous non-superconducting terms;
- bulk, filamentary, interface, and proximity-induced claims remain distinct;
- theoretical predictions are not written as experimental confirmation;
- negative measurements retain their lower temperature, field, pressure, and sensitivity limits;
- mechanism claims include support, counterevidence, and scope.

Use core audit codes plus:

- `SC01 false-trigger`
- `SC02 missed-trigger`
- `SC03 entity-leakage`
- `SC04 criterion-misattachment`
- `SC05 evidence-double-counting`
- `SC06 prediction-as-observation`
- `SC07 ambient-condition-invention`
- `SC08 ambiguous-symbol-expansion`
- `SC09 bulk-claim-overreach`
- `SC10 mechanism-overclaim`

## 11. Routing Examples

### Load

The abstract calls the target film superconducting. Results show a resistive transition to zero and a diamagnetic response at a compatible temperature for the same film. Load with transport and magnetic signals.

### Candidate

A search snippet says `Tc = 18 K`, but the full text is unavailable and `Tc` is not defined. Return candidate, record `SC-SOURCE-INCOMPLETE` and `SC-TERM-AMBIGUOUS`, and emit no domain records.

### Skip

A battery paper states that impedance was measured in a cryostat using a superconducting magnet. The magnet is apparatus and no target material is claimed to superconduct. Return skip with `SC-APPARATUS-ONLY`.

### Negative record

A superconductivity-focused paper reports no resistive or magnetic transition down to 0.4 K for the target composition. Load the adapter, classify `non-superconducting-in-measured-range`, and preserve the 0.4 K measurement boundary. Do not generalize to all temperatures, pressures, or sample states.
