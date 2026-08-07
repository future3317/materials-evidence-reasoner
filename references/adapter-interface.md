# Domain Adapter Interface

Domain adapters add specialized detection, terminology, measurement fields, and validation rules while keeping the materials core stable. This file defines the shared envelope; `adapter-execution-standard.md` defines the normative execution algorithm.

Before routing, read `adapter-registry.json`, `adapter-execution-standard.md`, and `adapter-routing-lexicon.json`. The registry is authoritative for IDs, layers, operational status, verification status, references, and contracts. An adapter marked `specified` or `planned` may be discussed as a candidate scope but must not produce `domain_records[]`.

## 1. Boundary

An adapter may:

- define candidate signals and exclusions;
- define domain property and mechanism records;
- define controlled vocabularies and condition requirements;
- add domain-specific cross-field validators;
- provide positive, negative, ambiguous, and boundary examples.

An adapter must not:

- add domain-specific keys to the core top level;
- weaken evidence, entity, missingness, confidence, or comparability rules;
- infer properties from material-family names alone;
- overwrite records produced by another adapter;
- treat adapter loading as proof that the target entity has the domain property.

## 2. Adapter Declaration

Document each adapter with:

```json
{
  "adapter_id": "example-domain",
  "ruleset_version": "2.0.0",
  "description": "Domain and intended decisions.",
  "applies_when": [],
  "excludes_when": [],
  "paper_profiles": [],
  "domain_entities": [],
  "property_catalog": [],
  "measurement_conditions": [],
  "controlled_vocabularies": {},
  "record_types": [],
  "validation_rules": [],
  "benchmark_cases": []
}
```

Keep this declaration in the adapter reference. Do not copy the entire rule catalog into every extraction result.

Register every adapter in `adapter-registry.json`. Use these composable layers instead of treating all adapters as mutually exclusive material classes:

- `material-family`: metallic, polymeric, ceramic, glass, cementitious, or other family identity;
- `physical-form`: liquid, powder, film, porous body, dispersion, or another state that cuts across families;
- `process`: synthesis, forming, joining, heat treatment, coating, additive manufacturing, and other lineage-changing operations;
- `application`: battery, photovoltaic, hydrogen storage, catalysis, thermoelectric, or other system-level use;
- `measurement-technique`: diffraction, microscopy, spectroscopy, thermal, mechanical, transport, electrochemical, or compositional measurement;
- `simulation-method`: DFT, MD, Monte Carlo, CALPHAD, phase field, FEM, ML, or other computational method;
- `phenomenon`: superconductivity, topology, magnetic order, phase transition, degradation, and other evidence-gated interpretations.

The same source and entity may load multiple layers. For example, a battery paper may load a polymer material-family adapter, a materials-processing adapter, an electrochemical-testing adapter, and a battery application adapter. Shared facts remain in core records; adapters add only their specialized semantics.

## 3. Three-Level Routing

Route at skill, article, and entity level. Skill-level activation decides whether this Skill is relevant at all; it never selects a domain adapter. Article routing retrieves candidate adapters by layer. Entity routing decides which named target may receive specialized records.

Before article routing, determine which layer is being evaluated. A term such as `liquid`, `battery`, `annealed`, or `Raman` does not compete for a single label because each belongs to a different layer.

### Article level

Determine whether the domain is:

- `primary`: central question, results, or conclusions;
- `secondary`: meaningful analysis but not the main question;
- `incidental`: background, apparatus, cited comparison, or passing mention;
- `unclear`: insufficient accessible evidence.

Classify `paper_profile` separately, for example:

- `experimental-materials`
- `theoretical-materials`
- `simulation-screening`
- `device-or-application`
- `review-or-commentary`
- `standard-or-technical-document`
- `mixed`
- `unknown`

### Entity level

Bind candidate signals to target entities. The same paper may contain a target material, control, substrate, electrode, reference material, and cited literature. Loading an adapter for one entity does not authorize domain records for all entities.

## 4. Routing Status

- `load`: the adapter may emit domain records for named target entities;
- `candidate`: inspect routing evidence and seek a discriminating signal, but do not emit domain records;
- `skip`: do not load domain extraction rules.

Use `candidate` when one ambiguous signal exists, full text is unavailable, entity attachment is unresolved, or the domain appears only in an uncertain context.

## 5. Decision Gates

Every adapter defines its own signals, but evaluate these universal gates:

| Gate | Question |
|---|---|
| `direct_domain_term` | Is a domain term used affirmatively rather than cited, negated, or hypothetical? |
| `target_entity_binding` | Are signals attached to a named target entity? |
| `centrality_supported` | Is the domain present in title, abstract, methods, results, figures, or conclusions as required? |
| `independent_signal_count` | How many meaningfully independent domain signals exist? |
| `results_evidence_present` | Is there result-level evidence rather than background only? |
| `background_only` | Are all matches confined to introduction, references, or quoted comparisons? |
| `apparatus_only` | Is the domain term only an instrument or facility description? |
| `negated_claim` | Does the source explicitly say the property was absent or unsupported? |
| `conflicting_entity_assignment` | Could the signal belong to a control, neighboring layer, or different sample? |
| `source_access_sufficient` | Is accessible content sufficient for the routing decision? |

Use pass/fail/unknown and a count where appropriate. Do not hide unknown gates inside a confidence score.

## 6. Decision Record

Record only rules matched or material to the decision. Keep the complete rule catalog in the adapter reference.

```json
{
  "adapter_id": "example-domain",
  "ruleset_version": "2.0.0",
  "status": "load",
  "decision_mode": "rule-gated",
  "source_ids": ["S1"],
  "paper_profile": "experimental-materials",
  "article_centrality": "primary",
  "target_entities": [
    {
      "entity_id": "SAMPLE-01",
      "role": "measured-sample",
      "scope_status": "resolved"
    }
  ],
  "matched_signals": [
    {
      "signal_id": "domain-direct-result",
      "signal_type": "direct-domain-term",
      "raw_term": "domain phrase",
      "canonical_concept": "domain-concept",
      "strength": "strong",
      "independence_group": "domain-result",
      "polarity": "affirmed",
      "section": "results",
      "valid_context": true,
      "locator": {"page": 4},
      "entity_ids": ["SAMPLE-01"],
      "evidence_id": "S1:E8"
    }
  ],
  "decision_gates": {
    "direct_domain_term": "pass",
    "target_entity_binding": "pass",
    "centrality_supported": "pass",
    "independent_signal_count": 2,
    "background_only": "pass",
    "apparatus_only": "pass",
    "negated_claim": "pass"
  },
  "exclusion_matches": [],
  "ambiguities": [],
  "reason_codes": ["DOMAIN-DIRECT", "DOMAIN-SAME-ENTITY"],
  "evidence_ids": ["S1:E8"],
  "decision_reason": "Two independent signals are attached to the target entity."
}
```

Signal fields:

- `signal_id`: exact identifier from `adapter-routing-lexicon.json`; free-form substitutes are invalid when a registered signal applies;
- `signal_type`: lexical, measurement, structural, mechanism, exclusion, or adapter-defined type;
- `raw_term`: exact term or short source-grounded representation;
- `canonical_concept`: adapter vocabulary;
- `strength`: `strong`, `supporting`, `weak`, or `exclusion`, matching the lexicon;
- `independence_group`: prevents lexical variants of one observation from being counted as independent evidence;
- `polarity`: `affirmed`, `negated`, `hypothetical`, `cited`, or `unclear`;
- `valid_context`: whether section, discourse role, polarity, and entity binding satisfy the signal definition;
- `section` and `locator`: source context;
- `entity_ids`: entities the signal supports;
- `evidence_id`: traceable evidence record.

Create separate decisions when article centrality, profile, or routing status differs by source. `source_ids` may contain more than one source only for inseparable source parts or a deliberate corpus-level decision that is identified as such.

Do not add a numeric probability or weighted score until a benchmark has calibrated it. Rule gates and evidence are authoritative.

## 7. Domain Records

When status is `load`, emit specialized records through the core `domain_records[]` envelope:

```json
{
  "id": "DOMAIN-01",
  "adapter_id": "example-domain",
  "record_type": "domain-property",
  "source_ids": ["S1"],
  "entity_ids": ["SAMPLE-01"],
  "measurement_run_ids": ["MEAS-01"],
  "property_record_ids": [],
  "fields": {"classification": "adapter-defined"},
  "evidence_ids": ["S1:E8"],
  "status": "reported",
  "confidence": {
    "level": "high",
    "basis": ["direct-table", "entity-explicit"]
  }
}
```

The adapter defines `record_type` and `fields`; the core validates IDs, evidence, status, and confidence. A domain record is invalid when no corresponding adapter decision has status `load`.

## 8. Multiple Adapters

Load more than one adapter when the paper genuinely spans domains. Keep records independent and use shared core entity and measurement IDs.

When adapters disagree:

1. retain both interpretations with adapter provenance;
2. record the conflict in `ambiguities` or `missing_information[]`;
3. do not select a winner without an explicit cross-domain rule or evidence;
4. core evidence and scope rules override adapter convenience.

## 9. Operational And Verification Gates

Set registry `status` to `implemented` only after all operational items pass:

- a clear domain boundary and exclusions;
- at least two positive, two negative, and two ambiguous routing cases;
- machine-readable strong, supporting, weak, and exclusion signals;
- semantic field contracts for every record type;
- evidence and condition requirements;
- routing, extraction, and schema tests;
- proof that domain fields remain outside the core top level.

Track evidentiary maturity independently in `verification_status`:

- `provisional`: machine and synthetic checks only;
- `source-backed`: one or more real accessible sources have been run and audited, without independent gold adjudication;
- `human-adjudicated`: frozen sources and expected outputs were independently reviewed under `benchmark-protocol.md`.

Never relabel synthetic cases or an agent's own answer as human-adjudicated gold.
