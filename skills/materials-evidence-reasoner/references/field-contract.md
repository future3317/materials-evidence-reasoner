# Universal Field Contract

Use this contract for every materials domain. Domain adapters may add property catalogs and validation rules, but must preserve these representations.

## 0. 决策上下文 / Decision Context

- `decision_profile` 表示证据任务类型：`literature`、`local-experiment`、`hybrid`、`audit` 或 `benchmark`；
- `decision_perspective` 表示排序与风险解释视角：`research`、`industrial` 或 `balanced`；它不能改变来源事实、字段状态或证据强度；
- `loop_state` 表示当前闭环阶段。三者不能互相替代。

## 1. Field Specification Template

Define each reusable or adapter-specific field with:

| Item | Requirement |
|---|---|
| `field_path` | Stable semantic path; avoid opaque names such as `section1` |
| `definition` | What the field means and what it does not mean |
| `applies_to` | Entity, process, measurement, property, source, or domain record |
| `include_when` | Positive evidence required to include the field |
| `exclude_when` | Background, control, cited comparison, negation, or other disqualifying contexts |
| `type` | JSON type and allowed multiplicity |
| `required_when_present` | Required child keys once the parent record exists |
| `controlled_vocabulary` | Closed values only when the concept is genuinely closed |
| `normalization` | Raw-to-canonical mapping and unit conversion rules |
| `evidence_requirement` | Minimum locator and evidence directness |
| `missing_policy` | Omit, record in `missing_information[]`, or mark conflicting |
| `validation` | Structural, semantic, range, cross-field, and reference checks |
| `examples` | At least one valid, invalid, ambiguous, and missing example for high-risk fields |

Do not enumerate every possible material, process, phase, instrument, or property value. Use controlled vocabularies for closed states and retain open terminology through `raw_term` plus `canonical_term`.

## 2. Entity Scope

Every property-bearing record must resolve its scope:

```json
{
  "system_signature": "Li6.6La3Zr1.6Nb0.4O12",
  "entity_ids": ["MAT-01", "SAMPLE-03"],
  "primary_entity_id": "SAMPLE-03",
  "role": "measured-sample",
  "scope_status": "resolved",
  "evidence_ids": ["S1:E2"]
}
```

`system_signature` is a label for routing and identity resolution, not proof that two records are the same material. Process, phase, geometry, state, and measurement scope remain part of identity.

Allowed `scope_status` values:

- `resolved`
- `partially-resolved`
- `ambiguous`
- `conflicting`
- `out-of-scope`

Exclude background examples, literature comparisons, references, substrates, crucibles, electrodes, controls, and adjacent layers unless they are explicitly part of the target record. Retain them as separate entities when they affect process or measurement interpretation.

## 3. Raw and Normalized Values

Use a value record for numerical and categorical results:

```json
{
  "raw_value": "1.2 x 10^-3 S cm-1",
  "raw_unit": "S cm-1",
  "normalized_value": 0.12,
  "normalized_unit": "S/m",
  "value_status": "reported",
  "approximation": "exact-as-reported",
  "extraction_method": "table",
  "derivation": {
    "operation": "unit-conversion",
    "formula": "1 S cm-1 = 100 S m-1",
    "input_evidence_ids": ["S1:E7"]
  },
  "uncertainty": {
    "raw": "+/- 0.1 x 10^-3 S cm-1",
    "kind": "reported-standard-deviation",
    "lower": 0.11,
    "upper": 0.13,
    "unit": "S/m"
  },
  "condition_signature": {
    "temperature": "25 degC",
    "method": "AC impedance",
    "electrode": "Au"
  },
  "evidence_ids": ["S1:E7"],
  "confidence": {
    "level": "high",
    "basis": ["direct-table", "unit-explicit", "entity-explicit"]
  }
}
```

Rules:

1. Preserve spelling, symbols, approximate signs, inequalities, ranges, significant figures, and original units in raw fields.
2. Add normalized values for comparison; never overwrite raw values.
3. Record every calculation, conversion, interpolation, fit, or digitization as a derivation.
4. Do not calculate a missing result merely because a formula exists unless the user requests derivation and all inputs are evidenced.
5. Keep nominal, setpoint, controller-measured, sample-measured, fitted, and predicted values as different roles.
6. Do not convert units when the definition or denominator is unresolved. Set `value_status` to `ambiguous` or `conflicting` and describe the blocker.

Allowed `value_status` values:

- `reported`: explicitly reported for the scoped entity;
- `derived`: deterministically calculated from evidenced inputs;
- `inferred`: interpretation requiring a stated assumption;
- `secondary`: current source attributes the value to another source;
- `ambiguous`: multiple plausible meanings or attachments;
- `conflicting`: incompatible values or definitions remain unresolved;
- `invalid`: source payload, label, calibration, or calculation failed validation.

## 4. Terminology Normalization

Use this shape for open vocabulary:

```json
{
  "raw_term": "high-Ni NCM",
  "canonical_term": "Ni-rich layered oxide cathode",
  "ontology_id": null,
  "mapping_status": "normalized-with-ambiguity",
  "mapping_reason": "The exact Ni fraction is not reported.",
  "evidence_ids": ["S1:E4"]
}
```

Allowed `mapping_status` values:

- `exact`
- `normalized`
- `normalized-with-ambiguity`
- `unmapped`
- `conflicting`

Never discard the raw term. Do not assign an ontology identifier without an exact or documented mapping.

## 5. Evidence and Locators

An evidence record must identify:

- source and source part;
- target entity or entities;
- modality: text, table, figure, image, curve, equation, metadata, raw data, or user observation;
- locator appropriate to the modality;
- raw representation or a compliant short excerpt;
- directness and extraction method;
- interpretation, limitation, and confidence basis.

Use available locator fields rather than encoding locations in one string:

```json
{
  "page": 7,
  "page_label": "S4",
  "section": "Experimental Methods",
  "paragraph": 3,
  "figure": "Fig. 2",
  "panel": "b",
  "table": "Table S3",
  "row": "Sample B",
  "column": "Ionic conductivity"
}
```

Page number and printed page label are different fields. For HTML, use section, paragraph, element identifier, or stable URL fragment. For figures, attach the caption evidence and any separately digitized region.

Allowed `directness` values:

- `direct-primary`
- `direct-user`
- `derived-from-primary`
- `secondary-claim`
- `interpretive`

Allowed `extraction_method` values:

- `metadata`
- `text`
- `table`
- `figure-caption`
- `figure-digitized`
- `image-observation`
- `ocr`
- `spreadsheet`
- `raw-data`
- `user-provided`
- `calculated`
- `model-derived`

## 6. Confidence

Confidence describes evidence support, not model feelings. Do not emit an uncalibrated probability.

- `high`: direct source location, explicit entity, explicit value or statement, and explicit critical conditions;
- `medium`: direct source but one non-blocking attachment or normalization uncertainty remains;
- `low`: OCR, figure reading, indirect attachment, unresolved terminology, or assumption materially affects extraction;
- `unassessed`: the evidence has not been audited.

Each confidence record requires one or more observable `basis` codes. Suggested codes:

- `direct-table`
- `direct-text`
- `figure-caption`
- `figure-digitized`
- `ocr-noisy`
- `unit-explicit`
- `unit-inferred`
- `entity-explicit`
- `entity-ambiguous`
- `condition-complete`
- `condition-incomplete`
- `cross-source-confirmed`
- `source-conflict`

Confidence does not replace `value_status`, missingness, or comparability.

## 7. Missing Information

Do not put missing facts into value records as invented defaults. Add a record to `missing_information[]`:

```json
{
  "field_path": "measurement_runs[MEAS-03].conditions.temperature",
  "entity_ids": ["SAMPLE-03"],
  "reason": "not-reported",
  "impact": "Blocks direct comparison with temperature-dependent conductivity data.",
  "expected_source_parts": ["Methods", "Figure 4 caption"],
  "resolution": "Check supplementary methods or request the raw run metadata."
}
```

Allowed reasons:

- `not-reported`
- `not-measured`
- `not-applicable`
- `inaccessible`
- `withheld-by-design`
- `ambiguous`
- `conflicting`
- `below-detection-limit`
- `invalid-source`
- `not-yet-audited`

Use omission for optional fields that truly do not apply. Use `missing_information[]` when absence affects interpretation, extraction completeness, comparison, compliance, or the next decision.

## 8. Process and Measurement Records

Processes are ordered. Each process step records sequence, raw and canonical method, parameters as value records, atmosphere, equipment, input and output entities, evidence, and unresolved conditions.

Measurements are separate runs. Record method, instrument, geometry, environment, calibration, acquisition conditions, data processing, exclusion rules, fitting window, software version, raw-file reference, and evidence.

Do not use a catch-all `characteristics` string for facts that have stable semantics. Use structured conditions and reserve `notes` for short residual context.

## 9. Property Records

Each property record requires:

- stable ID;
- target entity ID;
- measurement run ID when measured;
- raw and canonical property name;
- one value record;
- reporting role such as representative, best-reported, full-series, range, or single-case;
- evidence IDs;
- applicability and limitations.

Split records when entity, method, criterion, direction, temperature, pressure, field, normalization, or other meaning-changing conditions differ.

## 10. Adapter Extension Records

Domain-specific fields live in `domain_records[]`:

```json
{
  "id": "DOMAIN-01",
  "adapter_id": "superconductivity",
  "record_type": "superconducting-transition",
  "source_ids": ["S1"],
  "entity_ids": ["SAMPLE-03"],
  "measurement_run_ids": ["MEAS-02"],
  "property_record_ids": [],
  "fields": {"classification": "adapter-defined"},
  "evidence_ids": ["S1:E12"],
  "status": "reported",
  "confidence": {
    "level": "high",
    "basis": ["direct-text", "entity-explicit"]
  }
}
```

The adapter defines `record_type` and `fields`. Core IDs, evidence, confidence, raw-value, missingness, and entity rules still apply.

## 11. CSV Contract

Nested JSON is authoritative. CSV export is a normalized table set, not one flattened table:

| File | Primary key | Purpose |
|---|---|---|
| `sources.csv` | `source_id` | Bibliographic identity, access, version, and hash |
| `evidence.csv` | `evidence_id` | Source location, modality, directness, and confidence |
| `entities.csv` | `entity_id` | Material/sample identity, parentage, and state |
| `entity_relations.csv` | composite | Parent, split, treatment, and temporal relations |
| `process_runs.csv` | `process_run_id` | Process identity and ordered lineage |
| `process_parameters.csv` | composite | One parameter value per row |
| `measurement_runs.csv` | `measurement_run_id` | Protocol, geometry, calibration, and processing |
| `measurement_conditions.csv` | composite | One condition per row |
| `property_records.csv` | `property_record_id` | Raw and normalized property values |
| `adapter_decisions.csv` | composite | Adapter routing result and reason |
| `domain_records.csv` | `domain_record_id` | Adapter-specific records; serialize `fields` as JSON |
| `missing_information.csv` | composite | Missing field, reason, impact, and resolution |

CSV rules:

1. UTF-8 encoding and one header row.
2. Stable IDs preserve joins; never join by material name alone.
3. Keep raw and normalized values in separate columns.
4. Serialize lists and nested residual payloads as valid JSON strings, not delimiter-joined text.
5. Preserve empty string for absent optional cells; do not use `0`, `ambient`, `unknown`, or `N/A` unless they are actual reported values or controlled statuses.
6. Include `schema_version` in every exported table or an accompanying manifest.
