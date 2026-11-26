"""Publish the dated review and baseline statistics directly from the independent CPU records."""
from .io import PROJECT, atomic_json, read_json

FOLDER = PROJECT / "results/scientific-audit"
REVIEW = "2026-11-26-scientific-audit.md"


def baseline_text(snapshot, short=False):
    """Make the sampling unit, denominator, direction and missing measurements explicit."""
    data = snapshot.get("cpu_baseline", {})
    if data.get("status") != "complete":
        return "A complete paired CPU estimate is unavailable."
    a, b = [data["arms"][arm] for arm in ("ordinary", "prompted")]
    pair, strict = data["paired"]["correct"], data["paired"]["strict"]
    lo, hi = pair["ci95"]
    text = (f"The ordinary prompt passed {a['correct']}/{a['n']} problems ({a['accuracy']:.2%}) and the "
            f"rising-sea prompt passed {b['correct']}/{b['n']} ({b['accuracy']:.2%}). Prompted minus "
            f"ordinary accuracy was {100*pair['difference']:+.2f} percentage points "
            f"(paired 95% percentile interval {100*lo:+.2f} to {100*hi:+.2f}).")
    if short:
        return text
    labels = {"fraction_form": "reduced fractions", "polynomial_form": "expanded products",
              "rounded_roots": "rounded roots"}
    sensitivity = ("zero changes for reduced fractions, expanded products and rounded roots in both arms"
                   if not (a["form_failures"] or b["form_failures"]) else
                   ", ".join(f"{label} {a['form_failures'].get(k, 0)}/{b['form_failures'].get(k, 0)}"
                             for k, label in labels.items()) + " ordinary/prompted losses")
    return (text + f" Both prompts passed {pair['both']} problems, ordinary alone {pair['ordinary_only']}, "
            f"prompted alone {pair['prompted_only']} and neither {pair['neither']}. Invalid formats accounted "
            f"for {a['invalid_format']} ordinary and {b['invalid_format']} prompted answers. The stricter form "
            f"check retained {a['strict_correct']}/{a['n']} and {b['strict_correct']}/{b['n']} respectively "
            f"({sensitivity}). Its paired difference was "
            f"{100*strict['difference']:+.2f} points (95% interval {100*strict['ci95'][0]:+.2f} to "
            f"{100*strict['ci95'][1]:+.2f}). All {pair['problems']} problems retained their original stratum "
            f"weights in {pair['bootstrap_samples']:,} paired resamples. This retrospective prompt contrast is "
            "conditional on these strata, one checkpoint and one decoding setup. " +
            ("The primary interval includes zero. " if lo <= 0 <= hi else "") + "Theory and novelty are unmeasured.")


def baseline_plot(ax, data):
    """Show paired problem outcomes, including the disagreements that determine the contrast."""
    pair = data["paired"]["correct"]
    names = ["Both prompts", "Ordinary only", "Rising-sea only", "Neither"]
    counts = [pair[k] for k in ("both", "ordinary_only", "prompted_only", "neither")]
    bars = ax.barh(names, counts, color=["#337770", "#b57340", "#3979a3", "#9aa7ad"])
    ax.invert_yaxis()
    ax.bar_label(bars, padding=4)
    ax.set_xlim(0, pair["problems"])
    ax.set_xlabel("Number of paired problems")
    ax.set_title("Which prompts produced a verifier-correct final answer?")


def baseline_examples(storage):
    """Use the first twelve locked IDs in each archive, the same display rule as judged runs."""
    from .experiments import EXPLORATORY_PREFIX
    from .io import digest, read_jsonl
    directory = storage/"generations" if (storage/"generations").is_dir() else storage/"evaluations"
    examples = {}
    for arm in ("ordinary", "prompted"):
        name = EXPLORATORY_PREFIX + arm
        if not (FOLDER/(arm+".json")).is_file() or not (directory/name/"generations.jsonl").is_file():
            continue
        records = {r["task_id"]: r for r in read_json(FOLDER/(arm+".json"))["records"][:12]}
        selected = []
        for r in read_jsonl(directory/name/"generations.jsonl"):
            item = records.get(r["task_id"])
            if item and digest(r) == item["generation_digest"]:
                selected.append({"task_id": r["task_id"], "prompt": r["prompt"], "response": r["response"],
                                 "verification": {k: item[k] for k in ("status","answer","detail","strict","form_failure")},
                                 "theory": None, "assessment": None})
        examples[name] = sorted(selected,key=lambda r:r["task_id"])
    return examples


def audit_snapshot():
    """Optional for pre-audit checkouts or live runs with no archived baseline set."""
    result = {}
    if (FOLDER / "baseline-summary.json").is_file():
        result["cpu_baseline"] = read_json(FOLDER / "baseline-summary.json")
        result["baseline_description"] = baseline_text(result)
    if (FOLDER / "execution.json").is_file():
        runs = read_json(FOLDER / "execution.json")["trajectories"]
        counts = {("cache" if "cache-release" in k else "comparative"): f"{v['last_step']}/{v['required']}"
                  for k,v in runs.items()}
        result["audit_conclusions"] = (
            f"The comparative attempt logged {counts['comparative']} updates and the cache-release diagnostic "
            f"logged {counts['cache']}. The diagnostic stopped before the required save/resume boundary. "
            "The records cannot establish a cache-release benefit. The qualified reward comparison and "
            "frozen-recipient transfer experiment lack outcome data. The project-specific correctness-gated "
            "rubric measures a judge's opinion. The training loss uses Dr. GRPO length and variance choices "
            "with a separate positive KL penalty. See the dated scientific review for raw evidence and errata.")
    return result


def write_review(snapshot):
    """Integrate reproducible numbers with source-level determinations and mathematical derivations."""
    from .reporting import markdown_table
    inputs = {k: read_json(FOLDER / (k+".json")) for k in
              ("manifests", "calibration", "transcripts", "execution", "chronology", "inventory", "objections", "generation")}
    cal, execution, manifest = inputs["calibration"], inputs["execution"], inputs["manifests"]
    link = "../../results/scientific-audit/"
    report = ["# Independent scientific audit", "Libor “Burny” Burian · 26 November 2026",
              "## Research verdict",
              "H1 remains pending. The archive has no completed, matched three-seed comparison between "
              "the qualified theory-bonus and correctness-only arms. H2 remains untested. There are no "
              "frozen-recipient outcomes under the registered note conditions. The available behavioral "
              "comparison concerns two prompts applied to the same frozen pretrained policy.",
              "## Baseline scoring", baseline_text(snapshot),
              f"[Scoring protocol](../amendments/2026-11-26-cpu-baseline-audit.md) · "
              f"[Paired and per-family results]({link}baseline-summary.json) · [Ordinary records]({link}ordinary.json) "
              f"· [Prompted records]({link}prompted.json) · [Raw generation receipts](../generation/README.md)"]
    d = snapshot["cpu_baseline"]
    table = [["Locked stratum", "Ordinary correct / total", "Prompted correct / total"]]
    for split, ordinary in d["arms"]["ordinary"]["split"].items():
        prompted = d["arms"]["prompted"]["split"][split]
        table.append([split, f"{ordinary['correct']}/{ordinary['n']}", f"{prompted['correct']}/{prompted['n']}"])
    report += [markdown_table(table), "The protocol was publicly merged after the responses existed and before "
               "scoring. Exposure of this holdout now matters for subsequent adaptive choices. An initial run "
               "under system Python lacked symbolic dependencies, recorded infrastructure failures and withheld "
               "the paired estimate. The frozen verifier in the locked environment resolved the answers. Its "
               "terminal-tag and supported-grammar checks can reject mathematically intelligible text. The "
               "strict sensitivity addresses only the three prespecified form rules. Neither scorer checks the proof. "
               f"[Incomplete attempt]({link}attempts/system-python/baseline-summary.json) · "
               "[Math-Verify](https://github.com/huggingface/Math-Verify) · "
               "[Reasoning Gym polynomial prompt](https://github.com/open-thought/reasoning-gym/blob/v0.1.25/reasoning_gym/algebra/polynomial_multiplication.py)",
               "## Data and generalization",
               f"Independent exact checks covered {manifest['records']:,} locked tasks. The audit used prime "
               "valuations, bounded-sum inclusion–exclusion, polynomial interpolation, rational isolation "
               "of real roots, grid flood fill, polygon angle sums, exact rank and modular inverses. "
               "Replaying generation in an empty directory reproduced the locked task and rejection records. "
               "The overall study configuration hash changed with later amendments, while the task records stayed identical. "
              "The manifests list each split and family. Canonicalization checks equality under the "
               "documented within-family transformations, including polynomial variable renaming, common "
               "equation scale and grid symmetries. Shared templates, mathematical skills, possible semantic "
               "similarities beyond those keys, and pretraining exposure remain possible. Harder settings "
               "test parameter ranges. Unseen families and secondary OOD are defined relative to project training. "
               f"[Independent checks and exceptions]({link}manifests.json) · [Generator replay]({link}generator-replay.json) · [Audit implementation](../../src/grothendieck_rlvr/audit_math.py) · "
               "[Generator implementation](https://github.com/open-thought/reasoning-gym/tree/v0.1.25)",
               "## Instrument qualification",
               "Each row is one terminal development record. A tie fails strict preference. The attainable "
               "ceiling credits every unobserved novelty pair with a hypothetical pass. Hashes, case versions "
               "and adaptive reuse prevent treating these partly repeated examples as independent trials."]
    table = [["Development log", "Passed / observed", "Quality ties", "Scheduled novelty pairs", "Ceiling", "Suppression cases observed"]]
    for r in cal:
        table.append([r["log"], f"{r['passes']}/{r['observed']}", str(r["quality_ties"]), str(r["scheduled"]),
                      f"{r['attainable_rate']:.3f}", str(r["suppression_observed"])])
    report += [markdown_table(table), f"[Component reanalysis]({link}calibration.json) · "
              f"[Distinct and overlapping transcript events]({link}transcripts.json). Unreached suppression "
              "rates are undefined. Other interrupted versions have partial records and no terminal gate result.",
              "## Method and mathematical claims",
              "For correct solutions the theory-arm reward is 1 + 0.5T, where T is the weighted six-criterion "
              "rubric after the validity and applicable reference-relative novelty gates. Other solutions "
              "earn zero. A correctness-only arm gives C. The shuffled control permutes bonuses among eligible "
              "completions and can leave assignments fixed. TRL subtracts the prompt-group mean, omits "
              "standard-deviation scaling when scale_rewards is disabled, and divides the masked token sum by "
              "the fixed completion length times the batch size for dr_grpo. The configured reference-policy "
              "KL penalty remains active. This implements the two normalization changes described by Liu et al. "
              "The original paper's beta-zero experiment and the project's positive-beta run have different "
              "objectives. Rubrics as Rewards motivates graded feedback. This project selected its own items, "
              "weights and correctness gate. A separate same-family evaluator does not supply independent human labels. "
              "[Training code](../../src/grothendieck_rlvr/training.py) · [Reward code](../../src/grothendieck_rlvr/reward.py) · "
              "[DeepSeekMath §4](https://arxiv.org/html/2402.03300v3) · [Dr. GRPO §3 and Appendix G](https://arxiv.org/html/2503.20783v2) · "
              "[Pinned TRL trainer](https://github.com/huggingface/trl/blob/v1.15.0/trl/trainer/grpo_trainer.py) · "
              "[Rubrics as Rewards](https://arxiv.org/html/2507.17746v1)",
              "For positive n the subgroup generated by 2n and 3n is nℤ because 3n − 2n = n. It contains n+1 "
              "exactly when n = 1. The subgroup intersection 2nℤ ∩ 3nℤ is 6nℤ. Any nonempty intersection "
              "of their translates is a translate of 6nℤ. Over the reals the algebra with e² = 1 has "
              "multiplication matrix [[a,b],[b,a]] for a+be. Its determinant a²−b² is multiplicative and "
              "equals (a+b)(a−b). No additional isomorphism premise is needed for that equality. "
              "For noncommuting a and b the extra term in (a+b)(a−b) is ba−ab. Merely computing the "
              "commutative expansion does not apply the proposed noncommutative observation. For independent "
              "dice the parity character factors in expectation. Taking the two dice equal shows why "
              "dependence can invalidate the product. These derivations adjudicate the actual saved cases. "
              "An objection about missing exposition can still be reasonable when the algebra is correct. "
              f"[Candidates, objection text and symbolic checks]({link}objections.json) · [Case definitions](../../src/grothendieck_rlvr/novelty_cases.py)",
              "## Execution and chronology", snapshot["audit_conclusions"]]
    table = [["Discarded pilot", "Step", "Rollouts", "Accuracy", "C × theory", "Mean reward", "Step seconds"]]
    for pilot in execution["pilots"]:
        for s in pilot["steps"]:
            table.append([pilot["run"], str(s["step"]), str(s["rollouts"]), f"{s['accuracy']:.3f}",
                          f"{s['metric']:.4f}", f"{s['reward']:.4f}", f"{s['step_seconds']:.2f}"])
    report.append(markdown_table(table))
    cache = next(v for k,v in execution["trajectories"].items() if "cache-release" in k)
    peak = max(row["peak_gpu_reserved_bytes"] for row in cache["updates"])/2**30
    report.append(f"The diagnostic's observed peak reserved memory was {peak:.3f} GiB. This prefix stayed below "
                  "the registered 4.5 GiB ceiling. Its final four scheduled updates and the 0.5 GiB range "
                  "criterion were never observed. No checkpoint or resumed invocation is recorded for the diagnostic. "
                  "[Registered resource criteria](../amendments/2026-11-16-cuda-cache-diagnostic.md)")
    for number, window in enumerate(execution["device_windows"], 1):
        report.append(f"Pilot monitoring window {number} contains {window['samples']} whole-device samples "
                      f"with a maximum of {window['peak_mib']} MiB.")
    for r in execution["pilots"]:
        report.append(f"{r['run']} changed {r['changed_tensors']}/{r['adapter_tensors']} tensors between "
                      f"the first two checkpoints. The maximum absolute parameter change was {r['maximum_parameter_change']:.8g}.")
    history = inputs["chronology"]
    events = [["Milestone", "Recorded timestamp", "Evidence"]]
    original = history["original_registration"]
    events.append(["Original registration commit", original["committer_time"], original["commit"][:12]])
    for arm, observation in inputs["generation"].items():
        events.append([arm + " baseline, last saved answer", observation["last_saved"], "generation log"])
    comparative = next(v for k,v in execution["trajectories"].items() if "cache-release" not in k)
    events.append(["Last comparative optimizer update", comparative["updates"][-1]["time"], "training log"])
    amended = history["amendments"]["reports/amendments/2026-11-16-cuda-cache-diagnostic.md"]
    events.append(["Cache-release registration commit", amended["committer_time"], amended["commit"][:12]])
    events.append(["First cache diagnostic update", cache["updates"][0]["time"], "training log"])
    events.append(["Last cache diagnostic update", cache["updates"][-1]["time"], "training log"])
    protocol = history["audit_registration"]
    events.append(["CPU scoring protocol commit", protocol["committer_time"], protocol["commit"][:12]])
    report += [markdown_table(events),
               f"Times retain their recorded UTC offsets. [Generation events and save timestamps]({link}generation.json) · "
               "[Public scoring protocol merge](https://github.com/BurnyCoder/grothendieck-reinforcement-learning-with-llm-as-a-judge-reward-in-grpo-rlvr/pull/56)",
               "The checkpoints establish that parameters changed. Different development batches, optimizer "
               "state and KL regularization preclude a learning-effect estimate. Reserved allocator bytes, "
               "allocated tensor bytes and sampled whole-device use measure different quantities. Time "
               "comparisons also confound task difficulty, decoding length, judge latency and host load. "
               f"[Per-update events and device windows]({link}execution.json) · "
               "[PyTorch allocator definitions](https://docs.pytorch.org/docs/2.14/notes/cuda.html#memory-management) · "
               f"[Git chronology and dated amendments]({link}chronology.json)",
               "## Decision rules, corrections and evidence limits",
               "H1 requires a mean C × theory gain ≥ 0.05, a strictly positive lower 95% bound and an accuracy "
               "lower bound strictly above −0.03. Average matched seeds within problem for the primary "
               "interval. Hierarchical seed resampling is a sensitivity check with only three seed pairs. "
               "A theory upper bound below 0.05 rules out the target gain on this interval. A lower bound at "
               "or below zero alone leaves positive gains possible. A missed noninferiority criterion alone "
               "cannot establish inferiority. The previous analyzer could accept invented IDs with correct "
               "counts. The repaired entry point matches the locked problems, seeds, checkpoint provenance "
               "and qualification. H2 uses matched note conditions and resamples source problems with their "
               "four target probes together. Targets are assigned by family and generation order. Unrelated "
               "notes come from another family, so any eventual contrast could reflect topical relevance "
               "rather than reuse of a source-specific construction. The ordinary-note and correctness-policy "
               "conditions address different comparisons. Cross-source intervals are exploratory and unadjusted. "
               f"[Registration](../preregistration.md) · [Synthetic defect replay]({link}eligibility-regression.json) · [Regression tests](../../tests/test_scientific_audit.py) · "
               "[Paired resampling](https://aclanthology.org/W04-3250/)",
               f"The [file and passage index]({link}inventory.json) identifies the original Git blobs and "
               "the public dataset card. The [claim register](2026-11-26-claim-register.json) records evidence, "
               f"corrections and implications. The [original Hub inventory]({link}hub-inventory.json) exposed missing "
               "adapter tensors and a trainer card that named its base model as None. The archived bytes and "
               f"[corrected checkpoint cards]({link}checkpoint-cards.json) restore the evidence and attribution. "
               f"[Dated source-access receipts]({link}source-access.json) record URL reachability. A source establishing how an algorithm works cannot validate "
               "a local effect size. The archive cannot resolve unlogged activity, pretraining exposure, "
               "general human agreement, historical novelty or the exact provenance of all supplied social "
               "and video wording. These remain unverified. Dated registrations and raw model utterances "
               "remain available as historical evidence. [Source provenance](../../docs/rising-sea-quotations.md)"]
    (PROJECT/"reports/reviews"/REVIEW).write_text("\n\n".join(report)+"\n", encoding="utf-8")


def update_audit_documents(snapshot):
    if snapshot.get("cpu_baseline", {}).get("status") != "complete" or "audit_conclusions" not in snapshot:
        return
    write_review(snapshot)
    execution = read_json(FOLDER/"execution.json")
    run, trajectory = next((name,r) for name,r in execution["trajectories"].items() if "cache-release" not in name)
    model = snapshot["models"]["policy"]
    cards = {}
    boundaries = {"": trajectory["last_step"], "adapter/": trajectory["last_step"]}
    boundaries.update({f"checkpoint-{step}/": step for step in trajectory["checkpoints"]})
    for subdir, step in boundaries.items():
        cards[f"runs/{run}/{subdir}README.md"] = (
            f"---\nbase_model: {model['repo']}\nlibrary_name: peft\nlicense: apache-2.0\n---\n\n"
            f"# Interrupted theory-reward run, update {step}\n\n"
            f"This archived LoRA adapter belongs to the exploratory run `{run}`. The run used "
            f"[{model['repo']} at the recorded revision](https://huggingface.co/{model['repo']}/tree/{model['revision']}). "
            f"The archive reached update {trajectory['last_step']} of {trajectory['required']}. "
            "The judge was unqualified. Comparative accuracy, theory quality and recipient transfer for these "
            "weights remain unmeasured.\n\nThe 26 November 2026 audit corrected the trainer-generated card's "
            "base-model attribution. The adapter configuration preserves the original runtime path. "
            "[Execution record](https://huggingface.co/datasets/BurnyCoder/grothendieck-rlvr/blob/main/results/scientific-audit/execution.json)\n")
    atomic_json(FOLDER/"checkpoint-cards.json", cards)
    body = baseline_text(snapshot) + "\n\n" + snapshot["audit_conclusions"]
    (PROJECT/"reports/summary.md").write_text("# Scientific results\n\n" + body +
        f"\n\n[Independent audit](reviews/{REVIEW})\n", encoding="utf-8")
    card = PROJECT/"docs/dataset-card.md"
    content = card.read_text(encoding="utf-8")
    start, end = "<!-- CPU-AUDIT:START -->", "<!-- CPU-AUDIT:END -->"
    if start in content:
        before, after = content.split(start,1)[0], content.split(end,1)[1]
        card.write_text(before + start + "\n\n" + body + "\n\n" + end + after, encoding="utf-8")
