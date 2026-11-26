# Experiment summary

Generated from saved artifacts at 2026-11-26T12:51:39.883466+00:00.

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
| exploratory-small-gpu-v2-ordinary | 400 | 0.3700 | Pending | Pending |
| exploratory-small-gpu-v2-prompted | 400 | 0.3275 | Pending | Pending |
| exploratory-small-gpu-v2-theory-seed42 | Pending | Pending | Pending | Pending |
| exploratory-small-gpu-v2-correctness-seed42 | Pending | Pending | Pending | Pending |

## Retrospective prompt comparison

The ordinary prompt passed 148/400 problems (37.00%) and the rising-sea prompt passed 131/400 (32.75%). Prompted minus ordinary accuracy was -4.25 percentage points (paired 95% percentile interval -8.50 to +0.00). Both prompts passed 99 problems, ordinary alone 49, prompted alone 32 and neither 220. Invalid formats accounted for 177 ordinary and 189 prompted answers. The stricter form check retained 148/400 and 131/400 respectively (zero changes for reduced fractions, expanded products and rounded roots in both arms). Its paired difference was -4.25 points (95% interval -8.50 to +0.00). All 400 problems retained their original stratum weights in 10,000 paired resamples. This retrospective prompt contrast is conditional on these strata, one checkpoint and one decoding setup. The primary interval includes zero. Theory and novelty are unmeasured.

## Generation execution

exploratory-small-gpu-v2-ordinary: 400/400 unique task outputs saved; mean recorded generation time 11.25 seconds per answer; last saved response 2026-11-16T04:21:45.066423+00:00. exploratory-small-gpu-v2-prompted: 400/400 unique task outputs saved; mean recorded generation time 11.98 seconds per answer; last saved response 2026-11-16T07:43:39.780525+00:00. These receipts verify saved task coverage and configuration, not answer correctness or theory quality. Mean times exclude startup, interrupted attempts and downtime. Sources: reports/generation/.

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
    "id": "exploratory-small-gpu-v2",
    "amendment": "reports/amendments/2026-11-16-compact-gpu-judge.md",
    "authorization": "User requested prioritizing smaller/quantized Qwen3.5 models fully on GPU on 2026-11-16; earlier authorization for exploratory single-call judging despite failed qualification remains in effect.",
    "calibration_required": false,
    "interpretation": "Exploratory small-model GPU study with unqualified same-family judges; prior larger-model runs are deferred and not pooled.",
    "judge_protocol": "single-compact-v1",
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
        "quoted": "5a42dfae5ed77aa8f39c08e68d61f3cee6ece0a6038848dd9f91e11bf86948dc",
        "rubric": "3d0a631c8910f56dba0a111bd0c86565a0f875a2bd9c0fd1a2977b65a19807bb"
      },
      "evaluation_judge": {
        "quoted": "f99f76537c11d98dff3653e4076644d8d3f3f62fa4c6e8f194526ad485a342e0"
      }
    },
    "evidence_protocol": "compact-evidence-v1",
    "logging_protocol": "persistent-append-flush-each-event-v1"
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
    "interpretation": "exploratory; source-clustered, unadjusted paired intervals",
    "status": "pending"
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
  "interpretation": "exploratory; source-clustered, unadjusted paired intervals",
  "status": "pending"
}
```

## Interrupted training execution

The exploratory-small-gpu-v2-theory-seed42 attempt stopped at optimizer boundary 13 with peak allocated/reserved policy memory 2.46/8.98 GiB. The pinned generated configuration's cache-clearing interval was 250 steps. Checkpoint state and partial outputs are preserved. This is an incomplete execution attempt, not a completed comparison or evidence that mathematical performance improved or worsened.
