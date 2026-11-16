"""One artifact-driven entry point for tables, figures, Markdown, PDF and website snapshots."""
import html
import json
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from zoneinfo import ZoneInfo

from .analysis import primary_comparison, summarize, transfer_analysis
from .budget import training_budget, budget_markdown
from .experiments import EXPLORATORY_ID, EXPLORATORY_PREFIX, experiment_profile
from .io import PROJECT, atomic_json, digest, read_json, read_jsonl, root

ARMS = ["ordinary", "prompted", "correctness-seed42", "theory-seed42",
        "correctness-seed43", "theory-seed43", "correctness-seed44", "theory-seed44",
        "shuffled-seed42", "rubric-seed42"]


def development_records() -> list[dict]:
    """Summarize preserved development logs without treating partial runs as audits."""
    records = []
    for path in sorted((PROJECT / "reports/development").glob("*.jsonl")):
        events = read_jsonl(path)
        responses = [e for e in events if e["kind"] == "model_response"]
        assessments, candidate = [], {}
        for event in events:
            if event["kind"] == "model_request":
                candidate = {}
                messages = event["request"].get("messages", [])
                try:
                    payload = json.loads(messages[-1]["content"]) if messages else {}
                except (json.JSONDecodeError, TypeError):
                    payload = {}  # Some preserved runtime probes use plain-text input.
                if isinstance(payload, dict):
                    candidate = {key: payload[key] for key in
                                 ("problem", "conventional_reference", "candidate_response") if key in payload}
                    for key in ("conventional_reference", "candidate_response"):
                        if isinstance(candidate.get(key), dict):
                            candidate[key] = "".join(candidate[key].values())
            elif event["kind"] == "judge_assessment":
                assessments.append({**event, **candidate})
                candidate = {}  # Never attach stale text to a later unpaired record.
            elif event["kind"] == "judge_cache_hit":
                candidate = {}
        requests = sum(e["kind"] == "model_request" for e in events)
        records.append({"artifact": str(path.relative_to(PROJECT)), "requests": requests,
                        "completed_responses": len(responses), "incomplete_requests": requests-len(responses),
                        "judge_failures": sum(e["kind"] == "judge_failure" for e in events),
                        "response_seconds": [e["seconds"] for e in responses],
                        "assessments": assessments,
                        "stages": [{key: event[key] for key in
                                    ("time", "protocol", "stage", "seconds", "task_id", "finding") if key in event}
                                   for event in events if event["kind"] == "judge_stage_assessment"],
                        "interpretation": "Development evidence only; not a completed calibration or evaluation."})
    return records


def calibration_records() -> list[dict]:
    """Retain failed development results after archival and when cloning without local runs."""
    paths = sorted((PROJECT / "reports/development").glob("calibration-*.json"))
    paths += sorted((root() / "calibration").rglob("*.json"))
    records = [read_json(p) for p in paths if ".lock." not in p.name and ".progress." not in p.name]
    return list({digest(record): record for record in records}.values())


def calibration_text(snapshot) -> str:
    """Separate early failure, full-suite outcomes and unmeasured false-theory suppression."""
    if not snapshot["calibration"]:
        return "No completed or early-stopped calibration result is recorded."
    descriptions = []
    for result in snapshot["calibration"]:
        name = f"{result['role']}/{result['variant']} ({result['split']}, {result['identity']['judge'][:8]})"
        status = "passed" if result["passed"] else "failed"
        observed = len(result["ordering"])
        passed = sum(row["passed"] for row in result["ordering"])
        detail = f"{name} {status}: {passed}/{observed} observed preference contracts passed; "
        false = result["suppression"]
        detail += (f"{sum(row['passed'] for row in false)}/{len(false)} false-theory cases had their bonus suppressed."
                   if false else "false-theory suppression was not measured.")
        if not result["complete"]:
            preference = min(stratum["preference_upper_bound"] for stratum in result["strata"].values())
            suppression = min(stratum["suppression_upper_bound"] for stratum in result["strata"].values())
            detail += (f" Incomplete suite; lowest stratum-wise final upper bounds: "
                       f"preference {preference:.1%}, false-theory suppression {suppression:.1%}.")
        descriptions.append(detail)
    if any(not result["complete"] for result in snapshot["calibration"]):
        descriptions.append("Incomplete development suites stopped under the fixed futility rule. "
                            "Upper bounds assume every remaining case succeeds solely to test attainability. "
                            "Unobserved cases are not counted as measured successes or errors; no early pass is allowed.")
    return "\n\n".join(descriptions)


def collect() -> dict:
    """Missing artifacts remain missing; they never become fabricated zero results."""
    evaluations = {p.parent.name: read_jsonl(p) for p in (root() / "evaluations").glob("*/scores.jsonl")}
    cfg = read_json(PROJECT / "configs/study.json")
    exploratory = {name.removeprefix(EXPLORATORY_PREFIX): rows for name, rows in evaluations.items()
                   if name.startswith(EXPLORATORY_PREFIX)}
    training = {p.parent.name: read_jsonl(p) for p in (root() / "runs").glob("*/metrics.jsonl")}
    calibration = calibration_records()
    examples = {name: sorted(rows, key=lambda r: r["task_id"])[:12] for name, rows in evaluations.items()}
    feasibility_paths = sorted((PROJECT / "reports/development").glob("feasibility-*.json")) + list(
        (root() / "feasibility").glob("*.json"))
    feasibility = {digest(record): record for record in map(read_json, feasibility_paths)}
    return {"generated_at": datetime.now(timezone.utc).isoformat(), "study": cfg,
            "models": read_json(PROJECT / "configs/models.lock.json"),
            "summaries": {name: summarize(rows) for name, rows in evaluations.items()},
            "strata": {name: {split: summarize([r for r in rows if r["split"] == split])
                              for split in sorted({r["split"] for r in rows})}
                       for name, rows in evaluations.items()},
            "primary": primary_comparison(evaluations, cfg), "training": training,
            "exploratory_single": {
                "profile": experiment_profile(True),
                "primary": primary_comparison(exploratory, cfg, exploratory=True),
                "secondary_ood": primary_comparison(exploratory, cfg, suffix="-ood", secondary=True,
                                                     exploratory=True),
                "transfer": transfer_analysis(read_jsonl(root() / "transfer" / EXPLORATORY_ID / "scores.jsonl"),
                                              cfg["bootstrap_samples"], cfg["transfer_sources"])},
            "secondary_ood": primary_comparison(evaluations, cfg, suffix="-ood", secondary=True),
            "families": {name: {family: summarize([r for r in rows if r["family"] == family])
                                for family in sorted({r["family"] for r in rows})}
                         for name, rows in evaluations.items()},
            "calibration": calibration, "development": development_records(), "examples": examples,
            "generation_completions": [read_json(path) for path in sorted(
                (PROJECT / "reports/generation").glob("*.json"))],
            "budget": training_budget(list(feasibility.values()), cfg),
            "transfer": transfer_analysis(read_jsonl(root() / "transfer/scores.jsonl"), cfg["bootstrap_samples"],
                                          cfg["transfer_sources"]),
            "feasibility": list(feasibility.values())}


def feasibility_text(snapshot) -> str:
    """Memory evidence is distinct from mathematical accuracy and GRPO throughput."""
    probes = [r for r in snapshot["feasibility"] if r.get("kind") == "maximum_length_backward"]
    if not probes:
        return "No completed maximum-length backward probe is recorded."
    text = " ".join(
        f"A {probe.get('model', {}).get('repo', 'historical')} BF16 LoRA backward probe completed at "
        f"{probe['length']} tokens and microbatch {probe['microbatch']}, with peak allocated GPU memory "
        f"{probe['peak_gpu_allocated_bytes']/2**30:.2f} GiB and reserved memory "
        f"{probe['peak_gpu_reserved_bytes']/2**30:.2f} GiB. The measured forward/backward interval was "
        f"{probe['seconds']:.2f} seconds, including first-use compilation. The synthetic repeated-token "
        "input checks execution and memory, not mathematical ability or steady-state throughput."
        for probe in probes)
    if any(r.get("kind") == "grpo_initial_generation_failure" for r in snapshot["feasibility"]):
        text += (" The initial GRPO attempt failed during generation prefill when a carriage return "
                 "entered the compiler-cache path, before any optimizer update. Its failure log is preserved.")
    boundaries = [r for r in snapshot["feasibility"] if r.get("kind") == "grpo_first_saved_boundary"]
    if boundaries:
        saved = boundaries[0]
        text += (f" A repaired GRPO pilot reached optimizer boundary {saved['step']} and saved its checkpoint, "
                 f"with peak allocated memory {saved['peak_gpu_allocated_bytes']/2**30:.2f} GiB and "
                 f"reserved memory {saved['peak_gpu_reserved_bytes']/2**30:.2f} GiB. "
                 f"Its recorded learning rate was {saved['step_metrics']['learning_rate']:g}; "
                 f"the sampled batch had verified accuracy {saved['reward_batch']['accuracy']:.1%} and "
                 f"mean supported theory {saved['reward_batch']['theory']:g}. "
                 "A warmup boundary does not demonstrate learning.")
    resumed = [r for r in snapshot["feasibility"] if r.get("kind") == "grpo_resumed_completion"]
    if resumed:
        saved = resumed[0]
        text += (f" The resumed pilot completed boundary {saved['step']} at learning rate "
                 f"{saved['step_metrics']['learning_rate']:g}, with a recorded step interval of "
                 f"{saved['step_metrics']['step_time']:.2f} seconds. "
                 f"Peak allocated memory was {saved['peak_gpu_allocated_bytes']/2**30:.2f} GiB and "
                 f"reserved memory {saved['peak_gpu_reserved_bytes']/2**30:.2f} GiB. "
                 f"Its batch accuracy was {saved['reward_batch']['accuracy']:.1%}, and mean supported "
                 f"theory was {saved['reward_batch']['theory']:g}. "
                 "Checkpoint recovery and a parameter change are feasibility evidence, not an "
                 "improvement estimate. A single resumed interval is not a stable throughput benchmark. "
                 "Pilot adapters are excluded from comparative initialization.")
    benchmarks = [r for r in snapshot["feasibility"] if r.get("kind") == "synthetic_judge_runtime_benchmark"]
    for benchmark in benchmarks:
        if benchmark["timings"]:
            offload = benchmark.get("sweep") == "offload"
            key, unit = ("n_gpu_layers", "GPU layers") if offload else ("n_threads", "threads")
            rates = "; ".join(f"{t[key]} {unit}: {t['avg_ts']:.2f} tokens/s"
                              for t in benchmark["timings"])
            best = max(benchmark["timings"], key=lambda t: t["avg_ts"])
            text += (f" A synthetic Gemma decoding diagnostic recorded {rates}. "
                     f"The fastest measured setting used {best[key]} {unit}. "
                     "These short upstream llama-bench measurements omit structured-output sampling. "
                     + ("The offload sweep allocates the registered maximum context. " if offload else
                        "The thread sweep uses a smaller allocated context than the server. ") +
                     "They do not establish end-to-end judgment latency or calibration quality.")
    for failure in (r for r in snapshot["feasibility"] if r.get("kind") == "exploratory_single_grpo_contract_failure"):
        text += (f" The {failure['experiment']} pilot generated {failure['policy_completions']} policy completions "
                 f"but stopped after {failure['judge_requests']} requests failed the evidence contract, with "
                 f"{failure['accepted_assessments']} accepted judgments and {failure['optimizer_boundaries']} "
                 "saved optimizer boundaries. Reproducing mathematical typography in exact quotations failed "
                 "despite bounded validation feedback. This is an execution failure, not a learning result.")
    for failure in (r for r in snapshot["feasibility"] if r.get("kind") == "exploratory_grpo_truncation_failure"):
        text += (f" The {failure['experiment']} pilot generated {failure['policy_completions']} completions "
                 f"and exhausted {failure['judge_requests']} judge attempts on repetitive, truncated JSON. "
                 f"It accepted {failure['accepted_assessments']} assessments and saved "
                 f"{failure['optimizer_boundaries']} optimizer boundaries. Sampled whole-device usage peaked "
                 f"at {failure['sampled_device_peak_mib']} MiB of {failure['device_capacity_mib']} MiB. "
                 "This was an output-contract failure, not a GPU OOM or a learning result.")
    current = sorted((r for r in snapshot["feasibility"] if r.get("kind") == "exploratory_single_grpo_boundary"),
                     key=lambda r: r["step"])
    for saved in current:
        text += (f" The {saved['experiment']} exploratory pilot saved boundary {saved['step']} "
                 f"{'after resumption' if saved['resumed_from'] else 'from the selected base'}, with a "
                 f"step interval of {saved['step_metrics']['step_time']:.2f} seconds, learning rate "
                 f"{saved['step_metrics']['learning_rate']:g}, batch accuracy "
                 f"{saved['reward_batch']['accuracy']:.1%}, mean theory "
                 f"{saved['reward_batch']['theory']:.4f}, mean novelty "
                 f"{saved['reward_batch']['novelty']:.4f}, and {saved['judge_failures']} contract/transport retries. "
                 f"Peak allocated/reserved GPU memory was {saved['peak_gpu_allocated_bytes']/2**30:.2f}/"
                 f"{saved['peak_gpu_reserved_bytes']/2**30:.2f} GiB.")
        if saved["judge_seconds"]:
            text += (f" Completed judge requests took {min(saved['judge_seconds']):.2f}–"
                     f"{max(saved['judge_seconds']):.2f} seconds, including unsuccessful contracts.")
        if "changed_tensors" in saved:
            text += (f" Resumption changed {saved['changed_tensors']}/{saved['adapter_tensors']} adapter "
                     "tensors. These discarded pilot updates demonstrate execution, not improved mathematical ability.")
    for record in (r for r in snapshot["feasibility"] if r.get("kind") == "sampled_gpu_memory"):
        for invocation in record["invocations"]:
            text += (f" During {record['experiment']} boundary {invocation['step']}, "
                     f"{invocation['samples']} whole-device samples recorded a peak of "
                     f"{invocation['peak_mib']} MiB out of {invocation['capacity_mib']} MiB. "
                     "This includes the judge and other GPU users; sampling can miss shorter peaks.")
    return text


def display(value, digits=4) -> str:
    """A single formatter prevents tables from disagreeing about missing results."""
    return "Pending" if value is None else (f"{value:.{digits}f}" if isinstance(value, float) else str(value))


def table_rows(snapshot):
    """Include every planned arm, even before that arm has an evaluated model."""
    rows = [["Arm", "Problems", "Accuracy", "C × theory", "C × novelty"]]
    exploratory = [EXPLORATORY_PREFIX + arm for arm in
                   snapshot.get("exploratory_single", {}).get("profile", {}).get("initial_arms", [])]
    for arm in dict.fromkeys(ARMS + exploratory + sorted(snapshot["summaries"])):
        s = snapshot["summaries"].get(arm, {})
        rows.append([arm, display(s.get("n")), display(s.get("accuracy")),
                     display(s.get("metric")), display(s.get("correctness_weighted_novelty"))])
    return rows


def markdown_table(rows) -> str:
    """Render the same computed rows in README, reports and the paper source."""
    return "\n".join(["| " + " | ".join(rows[0]) + " |", "|" + "---|" * len(rows[0])] +
                     ["| " + " | ".join(row) + " |" for row in rows[1:]])


def generation_text(snapshot) -> str:
    """Publish checked coverage/timing receipts without implying mathematical success."""
    records = snapshot.get("generation_completions", [])
    if not records:
        return "No completed generation receipts have been published."
    descriptions = []
    for record in records:
        descriptions.append(
            f"{record['run_id']}: {record['saved']}/{record['expected']} unique task outputs saved; "
            f"mean recorded generation time {record['generation_seconds_mean']:.2f} seconds per answer; "
            f"last saved response {record['last_response_at']}."
        )
    return " ".join(descriptions) + (
        " These receipts verify saved task coverage and configuration, not answer correctness or theory quality. "
        "Mean times exclude startup, interrupted attempts and downtime. Sources: reports/generation/."
    )


def readme_results(snapshot) -> str:
    """Show every active comparison while leaving qualification history in the full report."""
    available = {row[0]: row for row in table_rows(snapshot)[1:]}
    rows = [["Arm", "Problems scored", "Accuracy", "C × theory", "C × novelty"]]
    for arm in ARMS:
        saved = available.get(EXPLORATORY_PREFIX + arm, [arm, *["Pending"] * 4])
        rows.append([arm, *saved[1:]])
    return markdown_table(rows) + "\n\nGeneration execution: " + generation_text(snapshot)


def readme_example(snapshot):
    """Select the first accepted repaired-pilot assessment, without ranking by score."""
    artifact = "reports/development/exploratory-single-pilot-step1.jsonl"
    for record in snapshot.get("development", []):
        if record["artifact"] == artifact and record["assessments"]:
            return record["assessments"][0]
    return None


def example_figure(snapshot, destination: Path) -> None:
    """Illustrate a real development output; visibly label excerpts and unqualified opinions."""
    import matplotlib.pyplot as plt
    example = readme_example(snapshot)
    fig, axes = plt.subplots(1, 2, figsize=(13, 7))
    for axis in axes:
        axis.axis("off")
    if example is None:
        axes[0].text(0, .9, "No archived development example available.", va="top")
    else:
        response = example["candidate_response"]
        paragraphs = response.split("\n\n")
        excerpt = response if len(paragraphs) <= 4 else (
            paragraphs[0] + "\n\n[Middle omitted for display]\n\n" + "\n\n".join(paragraphs[-3:]))
        wrapped = "\n".join(textwrap.fill(line, width=61) for line in excerpt.splitlines())
        axes[0].text(0, 1, "POLICY RESPONSE · DISPLAY EXCERPT", weight="bold", va="top")
        axes[0].text(0, .94, textwrap.fill(example["problem"], width=61) + "\n\n" + wrapped,
                     va="top", fontsize=9, parse_math=False, linespacing=1.3)
        assessment = example["assessment"]
        axes[1].text(0, 1, "QWEN JUDGE · UNQUALIFIED OPINION", weight="bold", va="top")
        axes[1].text(0, .93, f"Declared validity: {assessment['theory_validity']}\n"
                     f"Gated theory: {example['theory']:.4f}   Novelty: {example['novelty']:.4f}", va="top")
        rows = [[name.replace("_", " ").capitalize(), str(criterion["score"])]
                for name, criterion in assessment["criteria"].items()]
        table = axes[1].table(cellText=rows, colLabels=["Criterion", "Raw score / 4"],
                              colWidths=[.75, .25], bbox=[0, .43, 1, .37], cellLoc="left")
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        rationale = assessment["criteria"]["constructive_novelty"]["rationale"]
        axes[1].text(0, .36, "Saved novelty rationale:\n\n" + textwrap.fill(rationale, width=61),
                     va="top", fontsize=9, parse_math=False)
        fig.text(.04, .035, f"Source: exploratory-single-pilot-step1.jsonl · {example['task_id']} · {example['time']}",
                 fontsize=8)
    fig.suptitle("Development pilot: first accepted assessment in recorded order\n"
                 "Discarded pilot updates; this is not a trained-versus-baseline comparison", fontsize=12)
    fig.subplots_adjust(left=.04, right=.96, bottom=.11, top=.85, wspace=.14)
    fig.savefig(destination / "judge-example.png", dpi=160)
    plt.close(fig)


def transfer_rows(snapshot):
    """Recipient results come from the same records as the clustered comparisons."""
    rows = [["Note condition", "Probes", "Recipient accuracy"]]
    rows.extend([condition, display(metrics["n"]), display(metrics["accuracy"])]
                for condition, metrics in snapshot["transfer"]["summaries"].items())
    rows.extend(["exploratory: " + condition.removeprefix(EXPLORATORY_PREFIX),
                 display(metrics["n"]), display(metrics["accuracy"])]
                for condition, metrics in snapshot.get("exploratory_single", {}).get(
                    "transfer", {}).get("summaries", {}).items())
    return rows if len(rows) > 1 else rows + [["Registered transfer conditions", "Pending", "Pending"]]


def comparison_text(result):
    """The paper uses the saved paired estimates, including uncertainty and missing seed variation."""
    if "metric" not in result:
        return f"Analysis status: {result['status']}. {result.get('reason', '')}".rstrip(" .") + "."
    pieces = [f"Analysis status: {result['status']}."]
    for metric, name in (("metric", "C times theory"), ("correct", "accuracy")):
        row = result[metric]
        pieces.append(f"Theory-minus-correctness {name} difference {row['difference']:.4f}, "
                      f"paired 95% interval [{row['ci95'][0]:.4f}, {row['ci95'][1]:.4f}].")
    row = result["metric"]
    seed_sd = display(row["between_seed_sd"]) if row["between_seed_sd"] is not None else "not estimable from one seed"
    pieces.append(f"Matched problems: {row['problems']}; seeds: {row['seeds']}; "
                  f"between-seed SD of the theory difference: {seed_sd}.")
    return " ".join(pieces)


def request_latency_rows(records):
    """Describe completed calls separately from retries and censored requests.

    Full-request seconds include prefill and decoding. Do not pool different
    protocols or infer an unfinished call's latency from its missing response.
    """
    rows = [["Development artifact", "Completed calls", "Accepted opinions", "Judge failures",
             "Unfinished calls", "Median seconds/call", "Observed seconds/call range"]]
    for record in records:
        seconds = record["response_seconds"]
        rows.append([Path(record["artifact"]).stem, str(record["completed_responses"]),
                     str(len(record["assessments"])), str(record["judge_failures"]),
                     str(record["incomplete_requests"]), display(median(seconds) if seconds else None, 2),
                     f"{min(seconds):.2f}–{max(seconds):.2f}" if seconds else "Pending"])
    return rows


def stage_latency_rows(records):
    """Expose every objection while keeping protocol/role latency measurements separate."""
    rows = [["Development artifact", "Protocol", "Stage", "Accepted calls", "Calls with issues",
             "Issue declarations", "Supported validity with issues", "Median seconds"]]
    for record in records:
        groups = {}
        for stage in record.get("stages", []):
            finding = stage["finding"]
            # The two-call records nest the same specialist contracts under these keys.
            parts = [finding] + [finding[key] for key in ("reference", "development", "validity")
                                 if key in finding]
            issues = sum(len(part.get("issues", [])) for part in parts)
            conflict = any(part.get("verdict") == "supported" and part.get("issues") for part in parts)
            groups.setdefault((stage["protocol"], stage["stage"]), []).append(
                (stage["seconds"], issues, conflict))
        for (protocol, stage), findings in groups.items():
            rows.append([Path(record["artifact"]).stem, protocol, stage, str(len(findings)),
                         str(sum(issues > 0 for _, issues, _ in findings)),
                         str(sum(issues for _, issues, _ in findings)),
                         str(sum(conflict for _, _, conflict in findings)),
                         display(median(seconds for seconds, _, _ in findings), 2)])
    return rows


def withheld_novelty_rows(result):
    """Publish stored gate applications without reinterpreting historical assessments."""
    rows = [["Case", "Response", "Pre-gate novelty (0–4)", "Credited novelty (0–4)", "Gate reasons"]]
    records = [(row["id"], side, row.get(f"{side}_novelty_credit"))
               for row in result["ordering"] for side in ("preferred", "dispreferred")]
    records += [(row["id"], "false theory", row.get("novelty_credit")) for row in result["suppression"]]
    for case, side, credit in records:
        if credit and credit["withheld"]:
            rows.append([case, side, str(credit["raw_score"]), str(credit["effective_score"]),
                         ", ".join(credit["gate_reasons"])])
    return rows


def calibration_component_rows(result):
    """Separate score ranking from the registered control-credit condition.

    These descriptive checks explain a composite failure; they never replace
    the stored acceptance decision or invent labels absent from older records.
    """
    pairs = result["ordering"]
    novelty = [row for row in pairs if row["stratum"] == "novelty"]
    labeled = [row for row in novelty if row.get("expected_control_novelty") in ("none", "modest")]
    checks = {
        "Higher theory score": [row["preferred"] > row["dispreferred"] for row in pairs],
        "Higher novelty score": [row["preferred_novelty"] > row["dispreferred_novelty"] for row in novelty],
        "Control-credit condition (recorded labels only)": [
            row["dispreferred_novelty"] > 0 if row["expected_control_novelty"] == "modest"
            else row["dispreferred_novelty"] == 0 for row in labeled],
        "Complete preference contract (stored decision)": [row["passed"] for row in pairs],
    }
    return [["Observed check", "Passed", "Assessed", "Rate"]] + [
        [name, str(sum(values)), str(len(values)), display(sum(values)/len(values) if values else None)]
        for name, values in checks.items()]


def figures(snapshot, destination: Path) -> None:
    """Use zero-based bounded score axes; omit unavailable curves rather than inventing data."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
    destination.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=(11, 3.3))
    ax.set(xlim=(0, 11), ylim=(0, 3.3))
    ax.axis("off")
    boxes = [(0.2, 1.8, "Locked tasks\nReasoning Gym"), (3.0, 1.8, "Qwen policy\nfour completions"),
             (5.8, 1.8, "Answer verifier\ncorrectness gate"), (8.6, 1.8, "Frozen Qwen\nstructured judgment"),
             (3.0, .15, "TRL Dr. GRPO\nLoRA updates"), (5.8, .15, "C × (1 + 0.5T)\ncomposite reward"),
             (8.6, .15, "Frozen evaluator\nand recipient tests")]
    for x, y, label in boxes:
        ax.add_patch(FancyBboxPatch((x, y), 2.1, 1, boxstyle="round,pad=.06", facecolor="#edf5f5", edgecolor="#286667"))
        ax.text(x+1.05, y+.5, label, ha="center", va="center")
    for start, end in [((2.35,2.3),(2.95,2.3)), ((5.15,2.3),(5.75,2.3)), ((7.95,2.3),(8.55,2.3)),
                       ((9.6,1.75),(7.9,.9)), ((5.75,.65),(5.2,.65)), ((4.05,1.2),(4.05,1.75)),
                       ((5.1,1.75),(8.55,1.2))]:
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="->", mutation_scale=14, color="#36595b"))
    fig.tight_layout()
    fig.savefig(destination / "architecture.png", dpi=180)
    fig.savefig(destination / "architecture.svg")
    svg = destination / "architecture.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(10, 4))
    available = [(name, s) for name, s in snapshot["summaries"].items() if s["n"]]
    if available:
        ax.barh([x[0] for x in available], [x[1]["metric"] for x in available], color="#286667")
        ax.set_xlim(0, 1)
        ax.set_xlabel("Mean correctness-weighted independent theory score")
    else:
        ax.text(.5, .5, "No empirical evaluations yet\nPlanned arms remain pending", ha="center", va="center", transform=ax.transAxes)
        ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(destination / "evaluation.png", dpi=160)
    plt.close(fig)
    fig, axes = plt.subplots(2, 2, figsize=(10, 6))
    for axis, key, label in zip(axes.flat, ("accuracy", "theory", "loss", "kl"),
                                 ("Training correctness", "Training-judge theory", "Training loss", "KL"), strict=True):
        for name, events in snapshot["training"].items():
            points = [(e.get("step", e.get("reward_call")), e.get(key, e.get("metrics", {}).get(key))) for e in events]
            points = [(x, y) for x, y in points if x is not None and y is not None]
            if points:
                axis.plot([x for x, _ in points], [y for _, y in points], label=name)
        axis.set_title(label)
        axis.set_xlabel("Optimizer step (loss/KL) or reward batch (correctness/theory)")
        if key in ("accuracy", "theory"):
            axis.set_ylim(0, 1)
        if axis.lines:
            axis.legend(fontsize=7)
        else:
            axis.text(.5, .5, "No recorded data", ha="center", transform=axis.transAxes)
    fig.tight_layout()
    fig.savefig(destination / "training.png", dpi=160)
    plt.close(fig)
    example_figure(snapshot, destination)


def paper_sections(snapshot):
    """Scientific narrative separates protocol, observations and unsupported interpretations."""
    status = snapshot["primary"]["status"]
    return [
        ("Abstract", "We specify a local experiment testing whether correctness-gated rubric rewards "
         "improve useful mathematical theory building. A frozen Qwen judge assesses explanations; "
         "external arithmetic verifies final answers. Separate frozen judging and frozen-recipient "
         f"transfer assess behavior. Qualified-study analysis status: {status}. After calibration failures, "
         "a user-authorized exploratory continuation uses a single judge call despite unqualified rewards. "
         "Its results remain separate. No latent-space mechanism is established."),
        ("Context, motivation and related work", "Grothendieck's rising-sea metaphor motivates building "
         "structures until a specific question becomes a consequence. McLarty's account supplies the "
         "historical attribution [1]. We combine GRPO [2], Dr. GRPO normalization [3], and rubric rewards [4]. "
         "FERMAT [5] studies symbolic theory formation; this study instead scores natural-language explanations. "
         "The contribution is a correctness-gated experimental protocol and reusable environment, not a new optimizer."),
        ("Method", "Tasks come from pinned Reasoning Gym generators [6]. Training families are GCD, LCM, "
         "polynomial multiplication and dice probabilities. Semantic deduplication separates train, development, "
         "fresh, harder and unseen-family evaluation. One terminal final-answer field is checked by restricted "
         "arithmetic and Math-Verify [7]. Correctness C multiplies the entire reward: R=C(1+0.5T). "
         "Theory T is a six-criterion rubric score gated by supported validity. Constructive novelty receives "
         "20% weight, judged relative to published conventional approaches. New objects, definitions, invariants, "
         "frameworks and distant mathematical connections earn that credit only when justified and useful. "
         "Historical originality and pretraining distribution are not inferred. Supporting excerpts are required. "
         "The two-call protocol separated conceptual analysis from overall validity and quality. "
         "Its historical fallback used eight specialist roles. That protocol derived novelty from explicit addition, "
         "application and consequence findings, and withholds novelty unless supported theory is declared "
         "beyond-reference with an excerpt identifying a concrete addition. Brief valid connections can "
         "earn one novelty point without a further worked use; developed mathematics can earn up to four. "
         "A reference argument establishing a connection is not itself a further application. Raw stage "
         "findings are retained; code derives combined scores and any substantive objection vetoes the bonus. "
         "Checklist-based judging [14] and decomposition [15] motivate auditable "
         "prerequisites; the checks do not certify mathematical entailment. "
         "Final-answer verification does not certify surrounding proofs."),
        ("Models and training", "The active smaller-model experiment selects Qwen3.5-0.8B BF16 LoRA, "
         "with a frozen Qwen3.5-2B Q4_K_M training judge resident on the same GPU. A frozen "
         "Qwen3.5-4B Q4_K_M evaluator runs on GPU after policy generation. All policy parameters and "
         "judge layers must fit on CUDA; tokenization, verification and logging remain CPU work. "
         "The earlier 2B-policy/9B-CPU-judge/Gemma-12B setup is postponed and preserved. "
         "Exact revisions and dependencies "
         "are locked. Unsloth's documented non-vLLM route [8] and TRL [9] implement training. The preregistration "
         "fixes group size, optimizer settings, sample budgets and fallback criteria. A pre-comparison "
         f"runtime-budget amendment selects {snapshot['study']['max_steps']} optimizer updates for every training arm. "
         f"The deferred qualification protocol is {snapshot['study'].get('judge_protocol', 'legacy')}; per-role prompts, "
         "visible/reasoning budgets and dependencies are locked in its identity. Separate calls reuse the "
         "same frozen model and may share errors. Studies report setting-dependent benefits "
         "and failures of additional judging computation [12,13]; neither validates this novelty rubric. "
         "Failed feasibility or "
         "calibration is development evidence, not a negative test of the behavioral hypothesis."),
        ("Experimental design and analysis", "Compare ordinary and prompted unmodified models, correctness-only "
         "training, the proposed bonus, shuffled bonuses and a rubric-only ablation. The main trained comparison "
         "uses matched seeds. The primary measure is mean C*T from the frozen evaluation judge, with paired stratified "
         "problem-level bootstrap intervals and an accuracy noninferiority condition. Transfer resamples source "
         "problems while retaining their related probes. Single-seed findings are exploratory. No adaptive "
         "sample extension is allowed to obtain significance. A pre-judgment amendment adds a separate locked "
         "secondary set for graph connectivity, polygon geometry, rational matrix rank and modular inverses; "
         "it does not replace the primary split. Valid novelty is also reported separately. OOD means held "
         "out from project training, not necessarily from model pretraining."),
        ("Results and claims", "All tables and figures in this paper are generated from saved records. "
         "Pending cells indicate experiments without saved evaluation evidence. The machine-readable primary "
         f"analysis reports {status}. {comparison_text(snapshot['primary'])} "
         "Implementation checks do not establish mathematical performance. "
         "Calibration cases are constructed expectations, not human preference evidence."),
        ("Generation execution", generation_text(snapshot)),
        ("Development execution", f"Preserved development logs contain "
         f"{sum(r['completed_responses'] for r in snapshot['development'])} completed judge responses and "
         f"{sum(r['incomplete_requests'] for r in snapshot['development'])} requests without a completed response. "
         "These counts are generated from reports/development logs. Interrupted CPU and CUDA judging attempts "
         "and runtime changes are documented in dated amendments. CUDA loading succeeded, but slow decoding "
         "motivated a bounded thread-count diagnostic before recalibration. Partial judgments do not "
         "establish calibration reliability. Conventional arguments received nonzero novelty credit, including "
         "after the v3 clarification. The clean standalone Gemma retry completed judgments, including a "
         "rejected abbreviated quote and an accepted retry. V4 requests evidence before scores and supplies "
         "bounded validation feedback. V4 Gemma contrasts favored valid bridges but also assigned novelty "
         "to some conventional controls. Passive OpenMP waiting completed the observed requests without "
         "a transport failure; that short run does not establish sustained reliability. "
         "Qwen's subsequent partial v4 attempt also assigned no-theory verdicts to conventional "
         "generalized explanations. It was interrupted for a documented reasoning-mode development "
         "revision, without being declared a calibration pass or threshold failure. "
         "The later v5 attempt stopped after bounded retries repeated a contradiction between "
         "the declared reference relation and numerical novelty score; that calibration remained incomplete."
         " V6 demonstrated a logged eligibility gate on that discrepancy, then was interrupted when "
         "the user clarified that brief valid connections should receive modest novelty credit. "
         "V7 implements that changed construct. Its first trial failed the control-credit conditions "
         "despite correct observed framework/control rankings. A later reference-scope amendment "
         "clarified commutative-polynomial and ordinary biased-probability baselines. That trial also "
         "failed: routine probability controls received zero novelty, but brief commutator connections "
         "remained uncredited and a brief subgroup connection tied a developed framework on novelty "
         "while scoring higher overall. A conventional invariant was cited as a use of the added "
         "connection; exact-excerpt validation cannot establish that semantic attribution. "
         "Historical results are retained, and qualification remains unestablished. "
         "The two-call decomposition subsequently failed development: it credited a brief "
         "commutator connection but overcredited conventional GCD/LCM mathematics and missed "
         "developed uses. The preserved stage findings and case report document these errors. "
         "The preregistered specialist fallback also failed quoted-Qwen development. "
         "Its roles emitted mathematical objections to omitted elementary steps, conventionality "
         "and perceived irrelevance, removing bonuses from valid frameworks and a brief connection. "
         "Selected exact checks of the disputed steps are preserved without rescoring the trial. "
         "Rubric-only Qwen specialist development also failed: correct validity findings were "
         "vetoed by other roles, while a conventional calculation was mistaken for use of a brief connection. "
         "Quoted Gemma specialist development was deferred following the user's new execution instruction. "
         "Related proof-verification studies discuss false rejection [16,17], "
         "but use different models and aggregation rules and do not qualify this instrument."
         + "\n\n" + calibration_text(snapshot) + " No comparative conclusion follows.\n\n"
         + feasibility_text(snapshot)),
        ("Exploratory continuation with a single judge", "The dated amendment explicitly permits training "
         "without calibration qualification. It retains the latest published single-call rubric v7, "
         "fixed references, modest connection credit, weights, correctness gate and training settings. "
         "Following an exact-quotation execution failure, a new identity retains context preflight and "
         "replaces quotation copying with constrained passage IDs. Code extracts original source text; "
         "this follows the general source-location citation idea [19], using only local Qwen/Gemma. "
         "After the smaller judge repeatedly exhausted its output budget, a separate identity bounds "
         "rationale length and evidence/problem lists in the wire format without changing scoring rules. "
         "It does not verify that a selected passage entails the judge's claim. Each correct solution "
         "receives one accepted structured assessment; only output or transport failures permit bounded retries. "
         "Separate names and checkpoint identities keep these runs out of the qualified study. "
         "The initial comparison is theory bonus versus correctness-only at seed 42, with ordinary and "
         "rising-sea prompted baselines. The current 4B Qwen evaluator's scores are also unqualified. "
         "Both judges share a model family and may share systematic errors. The larger CPU setup was "
         "postponed at the user's request after a partial ordinary baseline; its saved outputs are not "
         "pooled with the smaller-policy comparison. The model-size change also changes the reward "
         "instrument, so historical timing or scores cannot isolate a CPU-versus-GPU effect. "
         "Held-out correctness and recipient transfer are therefore particularly useful checks, while "
         "judged theory remains a potentially biased proxy. Reward-model overoptimization has been observed "
         "in a distinct synthetic reward-model setting [18]; it does not determine this experiment's outcome. "
         "All uncertainty remains exploratory even if later seeds or nominal targets agree. Larger, better "
         "judges are future experiments requiring new frozen identities and fresh held-out confirmation. "
         + comparison_text(snapshot['exploratory_single']['primary'])),
        ("Transfer evaluation", "Recipient accuracy is compared with no notes, unrelated notes of matched "
         "length, and notes from other frozen source policies. Paired uncertainty resamples source problems "
         "with all four targets retained. Comparisons require complete matching source and target coverage. "
         "The machine-readable report publishes each source policy's related-minus-unrelated contrast "
         "and all pairs of note-source policies, with unadjusted exploratory intervals."),
        ("Discussion and limitations", "Judge scores are imperfect proxies. The current training and evaluation judges "
         "share the Qwen family and may share biases or training data; the cross-family comparison is deferred. "
         "Quantization can change judgments. Synthetic elementary tasks limit "
         "external validity. The constructed audit changes numerical instances while sharing mathematical "
         "templates with development; it does not establish generalization to unseen failure types. "
         "Fixed small-seed comparisons may be inconclusive. Reusable exposition is not "
         "equivalent to historically novel mathematics. Higher training scores without independent or transfer "
         "improvement are consistent with proxy optimization. Do not infer a latent mechanism from behavioral "
         "scores alone. Development/test separation and scoped claims follow methodological guidance [10,11]."),
        ("Postponed research directions", "After the current experiment sequence, the user requests trials with "
         "10B+, 100B+ and 1T+ parameter models, advanced agentic RL, Lean-based formal feedback, and explicit "
         "quantitative rewards replacing LLM judging where feasible. These are future research intentions, "
         "not implemented methods or results. Candidate measures include token/compute costs, checked "
         "consequences, dependency-based reuse and held-out transfer. Exact calculation does not establish "
         "that a metric captures conceptual novelty, generality or understanding. docs/future-research.md "
         "documents candidate measures, source links and required controls. Each direction needs a new "
         "registered protocol; the current small-model experiment and reward remain unchanged. "
         "If prespecified development diagnostics find that the small policy cannot solve the current "
         "tasks, a separate easier-mathematics experiment is authorized, preserving the present tasks "
         "for larger models. Difficulty must not be selected on held-out scores or changed within a "
         "comparison. The current pilot contains correct completions, so this fallback is not activated. "
         "The dated task-difficulty amendment records the diagnosis and separation requirements."),
        ("Conclusion", "The protocol tests whether an explicit interpretation of rising-sea theory building "
         "can supply useful training feedback while preserving mathematical accuracy. Its outcome must be read "
         "from the recorded comparisons; the motivating philosophical analogy is not itself evidence."),
        ("Appendix: reproducibility and unfinished work", "The repository contains the dated preregistration, "
         "model and data locks, full prompts, configurations, tests, and commands. reports/plan.md tracks "
         "unfinished experiments. Complete prompts and outputs are retained in timestamped logs. Checkpoints "
         "preserve optimizer, scheduler, RNG, data position and judge-cache state. No candidate code is executed."),
    ]


REFERENCES = [
    ("McLarty, The Rising Sea", "https://ncatlab.org/nlab/files/McLartyRisingSea.pdf"),
    ("DeepSeekMath", "https://arxiv.org/abs/2402.03300"),
    ("Understanding R1-Zero-Like Training", "https://arxiv.org/abs/2503.20783"),
    ("Rubrics as Rewards", "https://arxiv.org/abs/2507.17746"),
    ("Learning Interestingness in Automated Mathematical Theory Formation", "https://arxiv.org/abs/2511.14778"),
    ("Reasoning Gym", "https://github.com/open-thought/reasoning-gym"),
    ("Math-Verify", "https://github.com/huggingface/Math-Verify"),
    ("Unsloth Qwen3.5 guide", "https://unsloth.ai/docs/models/qwen3.5/fine-tune"),
    ("TRL GRPO", "https://huggingface.co/docs/trl/grpo_trainer"),
    ("Lones, How to avoid machine learning pitfalls", "https://arxiv.org/abs/2108.02497"),
    ("Lipton and Steinhardt, Troubling Trends", "https://arxiv.org/abs/1807.03341"),
    ("Explicit Reasoning Makes Better Judges", "https://arxiv.org/abs/2509.13332"),
    ("SLMJury", "https://arxiv.org/abs/2606.07810"),
    ("RULERS: Locked Rubrics and Evidence-Anchored Scoring", "https://arxiv.org/abs/2601.08654"),
    ("DnA-Eval: Decomposition and Aggregation", "https://aclanthology.org/2025.coling-main.156/"),
    ("Naik et al., Do We Need Frontier Models to Verify Mathematical Proofs?", "https://arxiv.org/abs/2604.02450v1"),
    ("Huang et al., Pessimistic Verification for Open Ended Math Questions", "https://arxiv.org/abs/2511.21522v1"),
    ("Gao, Schulman and Hilton, Scaling Laws for Reward Model Overoptimization", "https://proceedings.mlr.press/v202/gao23h.html"),
    ("Anthropic, source-location citation representation (documentation only)", "https://platform.claude.com/docs/en/build-with-claude/citations"),
]
AI_STATEMENT = ("AI statement: Codex wrote this codebase and paper from the exact specification provided "
                "by a human. Human cleanup and rewriting are in progress.")


def write_paper(snapshot, rows, destination: Path):
    """Render one source of numerical truth into a paginated, linked ReportLab paper."""
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, KeepTogether
    font = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    font_name = "Helvetica"
    if font.exists():
        pdfmetrics.registerFont(TTFont("DejaVu", str(font)))
        font_name = "DejaVu"
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("Reference", parent=styles["BodyText"], fontSize=9,
                              leading=11, spaceBefore=0, spaceAfter=1))
    for style in styles.byName.values():
        style.fontName = font_name
    styles["BodyText"].fontSize = 9
    styles["BodyText"].leading = 13
    styles["Heading2"].keepWithNext = True  # Keep section headings with their first paragraph after pagination.
    title = "Correctness-gated mathematical theory building"
    date = datetime.fromisoformat(snapshot["generated_at"]).astimezone(ZoneInfo("Europe/Berlin")).date().isoformat()
    story = [Paragraph(title, styles["Title"]),
             Paragraph(f"Libor “Burny” Burian · {date}", styles["Normal"]), Spacer(1, .15*inch)]
    markdown = [f"# {title}", f"Libor “Burny” Burian · {date}"]
    for heading, body in paper_sections(snapshot):
        markdown.extend([f"## {heading}", body])
        section = [Paragraph(heading, styles["Heading2"])] + [
            Paragraph(html.escape(paragraph), styles["BodyText"]) for paragraph in body.split("\n\n")]
        story.extend([KeepTogether(section)] if heading == "Conclusion" else section)
        if heading == "Method":
            story.append(Image(str(PROJECT / "site/figures/architecture.png"), width=6.7*inch, height=2.01*inch))
        if heading == "Results and claims":
            paper_rows = [[row[0].replace(EXPLORATORY_PREFIX, "exploratory: ", 1), *row[1:]] for row in rows]
            formatted = [[Paragraph(html.escape(cell), styles["BodyText"]) for cell in row] for row in paper_rows]
            formatted[0][1] = Paragraph("n", styles["BodyText"])
            table = Table(formatted, colWidths=[2.1*inch, .7*inch, .8*inch, .9*inch, 1.05*inch], repeatRows=1)
            table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#edf5f5")),
                                      ("VALIGN", (0,0), (-1,-1), "TOP"),
                                      ("LINEBELOW", (0,0), (-1,0), .5, colors.grey),
                                      ("BOTTOMPADDING", (0,0), (-1,-1), 5)]))
            story.extend([Spacer(1, 8), table, Spacer(1, 8)])
            if snapshot["summaries"]:
                story.append(Image(str(PROJECT / "site/figures/evaluation.png"), width=6.5*inch, height=2.6*inch))
            markdown.append(markdown_table(rows))
            markdown.append("```json\n" + json.dumps(snapshot["primary"], indent=2) + "\n```")
        if heading == "Exploratory continuation with a single judge":
            markdown.append("```json\n" + json.dumps(snapshot["exploratory_single"], indent=2) + "\n```")
        if heading == "Transfer evaluation":
            transfer_table = transfer_rows(snapshot)
            formatted = [[Paragraph(html.escape(cell), styles["BodyText"]) for cell in row] for row in transfer_table]
            table = Table(formatted, colWidths=[3.8*inch, .8*inch, 1.0*inch], repeatRows=1)
            table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#edf5f5")),
                                      ("VALIGN", (0,0), (-1,-1), "TOP"),
                                      ("LINEBELOW", (0,0), (-1,0), .5, colors.grey)]))
            story.extend([Spacer(1, 8), table])
            markdown.append(markdown_table(transfer_table))
    references = [Paragraph("References", styles["Heading2"])]
    markdown.append("## References")
    for i, (title, url) in enumerate(REFERENCES, 1):
        references.append(Paragraph(f'[{i}] <link href="{html.escape(url)}" color="#225d69">{html.escape(title)}</link>', styles["Reference"]))
        markdown.append(f"[{i}] [{title}]({url})")
    references.extend([Spacer(1, 12), Paragraph(html.escape(AI_STATEMENT), styles["BodyText"])])
    story.append(KeepTogether(references))
    markdown.append(AI_STATEMENT)
    def footer(canvas, doc):
        canvas.setFont(font_name, 8)
        canvas.drawString(.7*inch, .4*inch, "Grothendieck RLVR — protocol and artifact-driven results")
        canvas.drawRightString(7.6*inch, .4*inch, str(doc.page))
    SimpleDocTemplate(str(destination), title="Grothendieck RLVR research report",
                      author="Libor Burny Burian", leftMargin=.7*inch, rightMargin=.7*inch,
                      topMargin=.65*inch, bottomMargin=.65*inch).build(story, onFirstPage=footer, onLaterPages=footer)
    destination.with_suffix(".md").write_text("\n\n".join(markdown)+"\n", encoding="utf-8")


def report() -> dict:
    """The only command that regenerates numerical publications and the PDF paper."""
    snapshot = collect()
    (PROJECT / "reports/training-budget.md").write_text(budget_markdown(snapshot["budget"]), encoding="utf-8")
    atomic_json(PROJECT / "site/snapshot.json", snapshot)
    atomic_json(PROJECT / "reports/results.json", snapshot)
    generation_folder = PROJECT / "reports/generation"
    generation_folder.mkdir(exist_ok=True)
    (generation_folder / "README.md").write_text(
        "# Generation execution\n\nGenerated from the checked completion receipts in this folder.\n\n" +
        generation_text(snapshot) + "\n\n" + "\n\n".join(
            f"[{record['run_id']} artifacts]({record['artifact_url']})"
            for record in snapshot["generation_completions"]) + "\n", encoding="utf-8")
    rows = table_rows(snapshot)
    table = markdown_table(rows)
    figures(snapshot, PROJECT / "site/figures")
    summary = ("# Experiment summary\n\nGenerated from saved artifacts at " + snapshot["generated_at"] +
               ".\n\nCorrectness is verified final-answer accuracy. Theory is a frozen judge's rubric "
               "assessment, not a proof certificate. C × theory weights that assessment by answer correctness. "
               "Pending means no result, not zero performance.\n\n" + table +
               "\n\n## Generation execution\n\n" + generation_text(snapshot) +
               "\n\n## Judge calibration\n\n" + calibration_text(snapshot) +
               "\n\n## Primary analysis\n\n```json\n" + json.dumps(snapshot["primary"], indent=2) + "\n```\n" +
               "\n## Exploratory single-call experiment\n\nThe user authorized training with unqualified judges. " +
               "These analyses cannot establish that the original calibration-qualified criteria were met.\n\n```json\n" +
               json.dumps(snapshot["exploratory_single"], indent=2) + "\n```\n" +
               "\n## Secondary OOD analysis\n\nDescriptive paired intervals; not a replacement success criterion.\n\n```json\n" +
               json.dumps(snapshot["secondary_ood"], indent=2) + "\n```\n" +
               "\n## Frozen-recipient transfer\n\n" + markdown_table(transfer_rows(snapshot)) +
               "\n\n```json\n" + json.dumps(snapshot["transfer"], indent=2) + "\n```\n")
    (PROJECT / "reports/experiments.md").write_text(summary, encoding="utf-8")
    folder = PROJECT / "reports/experiments"
    folder.mkdir(exist_ok=True)
    for failure in (r for r in snapshot["feasibility"] if r.get("kind") == "exploratory_grpo_truncation_failure"):
        table = [["Measure", "Recorded value"],
                 ["Policy completions", str(failure["policy_completions"])],
                 ["Judge attempts", str(failure["judge_requests"])],
                 ["Accepted assessments", str(failure["accepted_assessments"])],
                 ["Saved optimizer boundaries", str(failure["optimizer_boundaries"])],
                 ["Sampled whole-device peak / capacity MiB",
                  f"{failure['sampled_device_peak_mib']} / {failure['device_capacity_mib']}"]]
        table += [[f"Request {i} seconds", f"{seconds:.2f}"]
                  for i, seconds in enumerate(failure["judge_seconds"], 1)]
        (folder / f"{failure['experiment']}-failure.md").write_text(
            f"# {failure['experiment']}: judge output-budget failure\n\nGenerated from "
            "`reports/development/feasibility-small-gpu-v1-truncation.json`.\n\n" + markdown_table(table) +
            "\n\nThe frozen small judge repeated rationale text until its unchanged token budget ended "
            "inside a JSON string. Existing retries exhausted; invalid output was not converted to a "
            "reward. No optimizer boundary was reached. Full prompts, responses and failures remain "
            f"in [{failure['event_log']}](../../{failure['event_log']}).\n\n"
            "The memory number samples the whole device, including the judge and other GPU users. "
            "It is not the policy allocator peak. No GPU OOM was observed; a successful backward "
            "probe does not establish full GRPO recovery. Request time includes transport and logging, "
            "not only model decoding.\n\n"
            "The [dated repair](../amendments/2026-11-16-compact-gpu-judge.md) adds bounded output "
            "fields and persistent append logging under a separate identity. It preserves the rubric, "
            "modest connection credit and qualification thresholds. Whether that repair completes "
            "training is a subsequent measurement, not a conclusion from this failed attempt.\n",
            encoding="utf-8")
    boundaries = [r for r in snapshot["feasibility"] if r.get("kind") == "exploratory_single_grpo_boundary"]
    for experiment in sorted({r["experiment"] for r in boundaries}):
        pilots = sorted((r for r in boundaries if r["experiment"] == experiment), key=lambda r: r["step"])
        behavior = [["Boundary", "Learning rate", "Accuracy", "C × theory", "C × novelty", "Mean reward"]]
        execution = [["Boundary", "Resumed", "Step seconds", "Peak allocated GiB", "Completed judge calls", "Retries"]]
        for pilot in pilots:
            batch, metrics = pilot["reward_batch"], pilot["step_metrics"]
            behavior.append([str(pilot["step"]), f"{metrics['learning_rate']:g}", display(batch["accuracy"]),
                             display(batch["theory"]), display(batch["novelty"]), display(metrics["reward"])])
            execution.append([str(pilot["step"]), str(bool(pilot["resumed_from"])),
                              display(metrics["step_time"], 2), display(pilot["peak_gpu_allocated_bytes"]/2**30, 2),
                              str(len(pilot["judge_seconds"])), str(pilot["judge_failures"])])
        filename = "exploratory-single-pilot.md" if experiment == "exploratory-single-v2" else f"{experiment}-pilot.md"
        source = "exploratory-single" if experiment == "exploratory-single-v2" else experiment
        (folder / filename).write_text(
            f"# Exploratory single-call save/resume pilot: {experiment}\n\nGenerated from "
            f"`reports/development/feasibility-{source}-step*.json`. "
            "These development updates are excluded from every comparative initialization. "
            "A zero learning rate checks execution but does not demonstrate an adapter update.\n\n" +
            markdown_table(behavior) + "\n\n" + markdown_table(execution) +
            "\n\nTheory and novelty means include zero for incorrect or invalidly formatted answers. "
            "Judge opinions remain unqualified. Request counts include completed invalid contracts; "
            "cache hits are not additional calls. Step intervals include generation, checking, judging "
            "and backward work; they are not stable throughput estimates or learning-effect estimates. "
            "The boundaries use different development batches, so their accuracies do not measure "
            "a learning trend. A parameter update with zero task reward can reflect restored optimizer "
            "momentum and the KL term; it does not establish learning from that batch. "
            "See [runtime scenarios](../training-budget.md) and the "
            "[dated amendments](../amendments/).\n", encoding="utf-8")
    (folder / "development-runtime.md").write_text(
        "# Development execution records\n\nGenerated from preserved timestamped logs. "
        "These are incomplete development attempts, not calibrated judges or comparative results. "
        "See the dated runtime amendment for rationale, interruptions and next checks.\n\n" +
        calibration_text(snapshot) + "\n\n" + feasibility_text(snapshot) +
        "\n\n## Observed request latency\n\n" + markdown_table(request_latency_rows(snapshot["development"])) +
        "\n\nTimings include prefill and decoding for completed calls, including invalid assessments. "
        "Unfinished calls have no completed latency and are counted separately, not assigned zero. "
        "Accepted opinions are combined assessments, excluding failed validations and cache hits. "
        "Decomposed protocols require multiple accepted stage calls per combined assessment. Rows use different prompts and "
        "runtime settings; their medians are not controlled speed comparisons, confidence intervals, "
        "or forecasts for training, evaluation, transfer or a complete calibration suite.\n\n" +
        "## Accepted stage findings and latency\n\n" + markdown_table(stage_latency_rows(snapshot["development"])) +
        "\n\nStage timings additionally include template/token checks and validation. Cache hits are excluded. "
        "Issue counts describe stored declarations, not independently verified errors. A supported validity "
        "verdict can coexist with an objection in a model output; the registered veto still applies. "
        "Repeated objections are retained, not treated as independent evidence or averaged away.\n\n```json\n" +
        json.dumps({"judging": snapshot["development"], "calibration": snapshot["calibration"],
                    "feasibility": snapshot["feasibility"]},
                   indent=2, ensure_ascii=False) + "\n```\n", encoding="utf-8")
    for result in snapshot["calibration"]:
        name = f"calibration-{result['role']}-{result['variant']}-{result['split']}-{result['identity']['judge'][:8]}"
        case_rows = [["Case", "Preferred T", "Control T", "Preferred novelty", "Control novelty",
                      "Control novelty expectation", "Passed"]]
        case_rows.extend([row["id"], display(row["preferred"]), display(row["dispreferred"]),
                     display(row["preferred_novelty"]), display(row["dispreferred_novelty"]),
                     ("Positive, below preferred" if row.get("expected_control_novelty") == "modest" else "Zero")
                     if row["stratum"] == "novelty" else "Not applied",
                     str(row["passed"])] for row in result["ordering"])
        credit_rows = withheld_novelty_rows(result)
        credit_text = ("\n\n## Withheld novelty credit\n\n" + markdown_table(credit_rows) +
                       "\n\nThese are recorded gate applications, not independently verified mathematical "
                       "errors. Pre-gate novelty is a model score in legacy protocols and a code-derived "
                       "level in decomposed protocols. Stored opinions remain unchanged; acceptance "
                       "checks use credited scores.") \
            if len(credit_rows) > 1 else ""
        (folder / f"{name}.md").write_text(
            f"# {name}\n\n" + calibration_text({"calibration": [result]}) + "\n\n" +
            markdown_table(calibration_component_rows(result)) +
            "\n\nThe component checks are descriptive. Correct score rankings alone do not satisfy "
            "the full novelty contract, which also checks the control-credit condition. "
            "Older records without an explicit control label are excluded only from that component, "
            "not from their stored acceptance decisions. No thresholds or outcomes are changed.\n\n" +
            markdown_table(case_rows) + credit_text +
            "\n\nThese are fixed constructed expectations, not human preference labels or verified novelty. "
            "Source: the matching identity in `reports/results.json`; full judgments are preserved in "
            "`reports/development/`. Case-level disagreements require interpretation, not silent score repair.\n",
            encoding="utf-8")
    for run, metrics in snapshot["summaries"].items():
        folder = PROJECT / "reports/experiments"
        folder.mkdir(exist_ok=True)
        (folder / f"{run}.md").write_text(
            f"# {run}\n\nGenerated from per-problem evaluation records.\n\n"
            "Method and settings: see the preregistration and the corresponding run configuration.\n\n"
            "```json\n" + json.dumps(metrics, indent=2) + "\n```\n\n"
            "Interpretation: descriptive results; consult the consolidated paired analysis before claiming improvement.\n",
            encoding="utf-8")
    readme = PROJECT / "README.md"
    content = readme.read_text(encoding="utf-8")
    start, end = "<!-- RESULTS:START -->", "<!-- RESULTS:END -->"
    if start in content:
        content = content.split(start)[0] + start + "\n\n" + readme_results(snapshot) + "\n\n" + end + content.split(end)[1]
    else:
        content += "\n## Recorded evaluation results\n\n" + start + "\n\n" + readme_results(snapshot) + "\n\n" + end + "\n"
    readme.write_text(content, encoding="utf-8")
    write_paper(snapshot, rows, PROJECT / "reports/paper.pdf")
    return {"snapshot": str(PROJECT / "site/snapshot.json"), "paper": str(PROJECT / "reports/paper.pdf")}
