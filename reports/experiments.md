# Experiment summary

Generated from saved artifacts at 2026-11-16T02:18:23.943572+00:00.

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
| exploratory-small-gpu-v1-ordinary | Pending | Pending | Pending | Pending |
| exploratory-small-gpu-v1-prompted | Pending | Pending | Pending | Pending |
| exploratory-small-gpu-v1-theory-seed42 | Pending | Pending | Pending | Pending |
| exploratory-small-gpu-v1-correctness-seed42 | Pending | Pending | Pending | Pending |

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
    "id": "exploratory-small-gpu-v1",
    "amendment": "reports/amendments/2026-11-16-small-qwen-gpu.md",
    "authorization": "User requested prioritizing smaller/quantized Qwen3.5 models fully on GPU on 2026-11-16; earlier authorization for exploratory single-call judging despite failed qualification remains in effect.",
    "calibration_required": false,
    "interpretation": "Exploratory small-model GPU study with unqualified same-family judges; prior larger-model runs are deferred and not pooled.",
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
      "configs/models.lock.json": "29a7152a84fea4d2b86e5229c1140e80685c583c07a7c6a5a352faba3af223d9",
      "configs/policy-selection.json": "0c841de481c145140df1c2b78bb820eb3174033994fea365294616e7105e44af",
      "configs/judge-runtime.json": "24a881eb8dba6760208b3eb1f928429a054a710c68e344b786e5fbae51fcc434",
      "data/manifest.lock.json": "d68e3c4c8759bc298f51aa9d4758e7701ae58374aca1733226a4db7387157a7c",
      "data/ood.lock.json": "11d75a026b7aab76c1e154a8172846c4735962f370fca2191606c4bff82eb062",
      "configs/artifacts.lock.json": "7fce628b3e3786c6c39b3ecb82a281b3f6c197cd1c38a44762fed06a55957b21"
    },
    "judge_identities": {
      "training_judge": {
        "quoted": "bd257f656acb3e1d30c28676a160807e279d4313b7a4b7a116be89bc587d936f",
        "rubric": "65581b55e3539247b0368ce36fb16873d5ff9e405d6fc1eb328f352bc86520f6"
      },
      "evaluation_judge": {
        "quoted": "7f50c54ec6f08eb5ecf44b1ed5316199900681fb5bbf5eb66022901d0cb84ea5"
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
