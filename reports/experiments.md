# Experiment summary

Generated from saved artifacts at 2026-11-16T00:37:22.015342+00:00.

Correctness is verified final-answer accuracy. Theory is a frozen judge's rubric assessment, not a proof certificate. C × theory weights that assessment by answer correctness. Pending means no result, not zero performance.

| Arm | Problems | Accuracy | C × theory | C × novelty |
|---|---|---|---|---|
| ordinary | Pending | Pending | Pending | Pending |
| prompted | Pending | Pending | Pending | Pending |
| correctness-seed42 | Pending | Pending | Pending | Pending |
| theory-seed42 | Pending | Pending | Pending | Pending |
| correctness-seed43 | Pending | Pending | Pending | Pending |
| theory-seed43 | Pending | Pending | Pending | Pending |
| correctness-seed44 | Pending | Pending | Pending | Pending |
| theory-seed44 | Pending | Pending | Pending | Pending |
| shuffled-seed42 | Pending | Pending | Pending | Pending |
| rubric-seed42 | Pending | Pending | Pending | Pending |
| exploratory-single-v2-ordinary | Pending | Pending | Pending | Pending |
| exploratory-single-v2-prompted | Pending | Pending | Pending | Pending |
| exploratory-single-v2-theory-seed42 | Pending | Pending | Pending | Pending |
| exploratory-single-v2-correctness-seed42 | Pending | Pending | Pending | Pending |

## Judge calibration

evaluation_judge/quoted (dev, ef8a300c) failed: 2/4 observed preference contracts passed; false-theory suppression was not measured. Incomplete suite; lowest stratum-wise final upper bounds: preference 75.0%, false-theory suppression 100.0%.

training_judge/quoted (dev, 08145e59) failed: 1/3 observed preference contracts passed; false-theory suppression was not measured. Incomplete suite; lowest stratum-wise final upper bounds: preference 75.0%, false-theory suppression 100.0%.

training_judge/quoted (dev, ebe93e9d) failed: 6/9 observed preference contracts passed; false-theory suppression was not measured. Incomplete suite; lowest stratum-wise final upper bounds: preference 75.0%, false-theory suppression 100.0%.

training_judge/quoted (dev, a3fa911e) failed: 4/7 observed preference contracts passed; false-theory suppression was not measured. Incomplete suite; lowest stratum-wise final upper bounds: preference 75.0%, false-theory suppression 100.0%.

training_judge/quoted (dev, b33cb353) failed: 0/3 observed preference contracts passed; false-theory suppression was not measured. Incomplete suite; lowest stratum-wise final upper bounds: preference 75.0%, false-theory suppression 100.0%.

training_judge/rubric (dev, c07b8d14) failed: 0/3 observed preference contracts passed; false-theory suppression was not measured. Incomplete suite; lowest stratum-wise final upper bounds: preference 75.0%, false-theory suppression 100.0%.

training_judge/quoted (dev, 66721e0e) failed: 2/5 observed preference contracts passed; false-theory suppression was not measured. Incomplete suite; lowest stratum-wise final upper bounds: preference 75.0%, false-theory suppression 100.0%.

Incomplete development suites stopped under the fixed futility rule. Upper bounds assume every remaining case succeeds solely to test attainability. Unobserved cases are not counted as measured successes or errors; no early pass is allowed.

## Primary analysis

```json
{
  "status": "pending",
  "reason": "No matched trained arms have been evaluated"
}
```

## Exploratory single-call experiment

The user authorized training with unqualified judges. These analyses cannot establish that the original calibration-qualified criteria were met.

```json
{
  "profile": {
    "id": "exploratory-single-v2",
    "amendment": "reports/amendments/2026-11-16-indexed-evidence.md",
    "authorization": "User explicitly requested single-call judge training despite failed acceptance thresholds on 2026-11-16 Europe/Berlin.",
    "calibration_required": false,
    "interpretation": "Exploratory learning with unqualified, potentially systematically biased judges; not the calibration-qualified study.",
    "judge_protocol": "single-indexed-v1",
    "rubric_version": "v7",
    "reference_version": "v3",
    "initial_arms": [
      "ordinary",
      "prompted",
      "theory-seed42",
      "correctness-seed42"
    ],
    "input_hashes": {
      "configs/study.json": "f6ff5203056f5f5eeb555f4c69f608dd3dc746562f2ee2a783668ab5292225e6",
      "configs/models.lock.json": "19665fe0a0e451deccaa0ea52662b21a2056bdd335b79cc5e9efc58a28fa8495",
      "configs/policy-selection.json": "698f3ed0cbab3e3a0a307fb0a721d46b7bb0636fe2f633632b2ba69e4a0576bd",
      "data/manifest.lock.json": "d68e3c4c8759bc298f51aa9d4758e7701ae58374aca1733226a4db7387157a7c",
      "data/ood.lock.json": "11d75a026b7aab76c1e154a8172846c4735962f370fca2191606c4bff82eb062"
    },
    "judge_identities": {
      "training_judge": {
        "quoted": "b6add1897e852493e0cbea6a16a15a6bce81d2b1ef7e487b97386518ee6c545a",
        "rubric": "369ecf0cbc00b592c5897ea33485091b9dd5fecbed4f622fa18676a93caebc89"
      },
      "evaluation_judge": {
        "quoted": "368baea56bdf984b0554899338734fcdb4eb48071bda3d5d4219ec3700c70464"
      }
    },
    "evidence_protocol": "indexed-evidence-v1"
  },
  "primary": {
    "status": "pending",
    "reason": "No matched trained arms have been evaluated"
  },
  "secondary_ood": {
    "status": "pending",
    "reason": "No matched trained arms have been evaluated"
  },
  "transfer": {
    "summaries": {},
    "versus_no_notes": {},
    "versus_unrelated": {},
    "between_note_sources": {},
    "interpretation": "exploratory; source-clustered, unadjusted paired intervals"
  }
}
```

## Secondary OOD analysis

Descriptive paired intervals; not a replacement success criterion.

```json
{
  "status": "pending",
  "reason": "No matched trained arms have been evaluated"
}
```

## Frozen-recipient transfer

| Note condition | Probes | Recipient accuracy |
|---|---|---|
| Registered transfer conditions | Pending | Pending |

```json
{
  "summaries": {},
  "versus_no_notes": {},
  "versus_unrelated": {},
  "between_note_sources": {},
  "interpretation": "exploratory; source-clustered, unadjusted paired intervals"
}
```
