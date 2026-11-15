"""One artifact-driven entry point for tables, figures, Markdown, PDF and website snapshots."""
import html
import json
from datetime import datetime, timezone
from pathlib import Path

from .analysis import primary_comparison, summarize, transfer_analysis
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
        assessments = [e for e in events if e["kind"] == "judge_assessment"]
        requests = sum(e["kind"] == "model_request" for e in events)
        records.append({"artifact": str(path.relative_to(PROJECT)), "requests": requests,
                        "completed_responses": len(responses), "incomplete_requests": requests-len(responses),
                        "response_seconds": [e["seconds"] for e in responses],
                        "assessments": assessments,
                        "interpretation": "Development evidence only; not a completed calibration or evaluation."})
    return records


def collect() -> dict:
    """Missing artifacts remain missing; they never become fabricated zero results."""
    evaluations = {p.parent.name: read_jsonl(p) for p in (root() / "evaluations").glob("*/scores.jsonl")}
    cfg = read_json(PROJECT / "configs/study.json")
    training = {p.parent.name: read_jsonl(p) for p in (root() / "runs").glob("*/metrics.jsonl")}
    calibration = [read_json(p) for p in (root() / "calibration").glob("*.json")
                   if ".lock." not in p.name and ".progress." not in p.name]
    examples = {name: sorted(rows, key=lambda r: r["task_id"])[:12] for name, rows in evaluations.items()}
    feasibility_paths = sorted((PROJECT / "reports/development").glob("feasibility-*.json")) + list(
        (root() / "feasibility").glob("*.json"))
    feasibility = {digest(record): record for record in map(read_json, feasibility_paths)}
    return {"generated_at": datetime.now(timezone.utc).isoformat(), "study": cfg,
            "summaries": {name: summarize(rows) for name, rows in evaluations.items()},
            "strata": {name: {split: summarize([r for r in rows if r["split"] == split])
                              for split in sorted({r["split"] for r in rows})}
                       for name, rows in evaluations.items()},
            "primary": primary_comparison(evaluations, cfg), "training": training,
            "secondary_ood": primary_comparison(evaluations, cfg, suffix="-ood", secondary=True),
            "families": {name: {family: summarize([r for r in rows if r["family"] == family])
                                for family in sorted({r["family"] for r in rows})}
                         for name, rows in evaluations.items()},
            "calibration": calibration, "development": development_records(), "examples": examples,
            "transfer": transfer_analysis(read_jsonl(root() / "transfer/scores.jsonl"), cfg["bootstrap_samples"],
                                          cfg["transfer_sources"]),
            "feasibility": list(feasibility.values())}


def feasibility_text(snapshot) -> str:
    """Memory evidence is distinct from mathematical accuracy and GRPO throughput."""
    probes = [r for r in snapshot["feasibility"] if r.get("kind") == "maximum_length_backward"]
    if not probes:
        return "No completed maximum-length backward probe is recorded."
    first = probes[0]
    text = (f"A recorded BF16 LoRA backward probe completed at {first['length']} tokens and microbatch "
            f"{first['microbatch']}, with peak allocated GPU memory "
            f"{first['peak_gpu_allocated_bytes']/2**30:.2f} GiB and reserved memory "
            f"{first['peak_gpu_reserved_bytes']/2**30:.2f} GiB. The measured forward/backward interval was "
            f"{first['seconds']:.2f} seconds, including first-use compilation. The synthetic repeated-token "
            "input checks execution and memory, not mathematical ability or steady-state throughput. "
            "It does not establish four-completion GRPO or checkpoint-resumption feasibility.")
    if any(r.get("kind") == "grpo_initial_generation_failure" for r in snapshot["feasibility"]):
        text += (" The initial GRPO attempt failed during generation prefill when a carriage return "
                 "entered the compiler-cache path. No optimizer update completed in that attempt; "
                 "its failure record is preserved separately from the successful backward probe.")
    return text


def display(value, digits=4) -> str:
    """A single formatter prevents tables from disagreeing about missing results."""
    return "Pending" if value is None else (f"{value:.{digits}f}" if isinstance(value, float) else str(value))


def table_rows(snapshot):
    """Include every planned arm, even before that arm has an evaluated model."""
    rows = [["Arm", "Problems", "Accuracy", "C × theory", "C × novelty"]]
    for arm in dict.fromkeys(ARMS + sorted(snapshot["summaries"])):
        s = snapshot["summaries"].get(arm, {})
        rows.append([arm, display(s.get("n")), display(s.get("accuracy")),
                     display(s.get("metric")), display(s.get("correctness_weighted_novelty"))])
    return rows


def markdown_table(rows) -> str:
    """Render the same computed rows in README, reports and the paper source."""
    return "\n".join(["| " + " | ".join(rows[0]) + " |", "|" + "---|" * len(rows[0])] +
                     ["| " + " | ".join(row) + " |" for row in rows[1:]])


def transfer_rows(snapshot):
    """Recipient results come from the same records as the clustered comparisons."""
    rows = [["Note condition", "Probes", "Recipient accuracy"]]
    rows.extend([condition, display(metrics["n"]), display(metrics["accuracy"])]
                for condition, metrics in snapshot["transfer"]["summaries"].items())
    return rows if len(rows) > 1 else rows + [["Registered transfer conditions", "Pending", "Pending"]]


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
             (5.8, 1.8, "Answer verifier\ncorrectness gate"), (8.6, 1.8, "Frozen Qwen\nrubric judgment"),
             (3.0, .15, "TRL Dr. GRPO\nLoRA updates"), (5.8, .15, "C × (1 + 0.5T)\ncomposite reward"),
             (8.6, .15, "Frozen Gemma\nand recipient tests")]
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


def paper_sections(snapshot):
    """Scientific narrative separates protocol, observations and unsupported interpretations."""
    status = snapshot["primary"]["status"]
    return [
        ("Abstract", "We specify a local experiment testing whether correctness-gated rubric rewards "
         "improve useful mathematical theory building. A frozen Qwen judge assesses explanations; "
         "external arithmetic verifies final answers. Independent Gemma judgment and frozen-recipient "
         f"transfer assess behavior. Primary analysis status: {status}. No latent-space mechanism is established."),
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
         "Final-answer verification does not certify surrounding proofs."),
        ("Models and training", "Qwen3.5-2B BF16 LoRA is preferred; Qwen3.5-9B Q4_K_M judges training "
         "on CPU, and Gemma 4 12B UD-Q4_K_XL judges evaluation separately. Exact revisions and dependencies "
         "are locked. Unsloth's documented non-vLLM route [8] and TRL [9] implement training. The preregistration "
         "fixes group size, optimizer settings, sample budgets and fallback criteria. Failed feasibility or "
         "calibration is development evidence, not a negative test of the behavioral hypothesis."),
        ("Experimental design and analysis", "Compare ordinary and prompted unmodified models, correctness-only "
         "training, the proposed bonus, shuffled bonuses and a rubric-only ablation. The main trained comparison "
         "uses matched seeds. The primary measure is mean C*T from frozen Gemma, with paired stratified "
         "problem-level bootstrap intervals and an accuracy noninferiority condition. Transfer resamples source "
         "problems while retaining their related probes. Single-seed findings are exploratory. No adaptive "
         "sample extension is allowed to obtain significance. A pre-judgment amendment adds a separate locked "
         "secondary set for graph connectivity, polygon geometry, rational matrix rank and modular inverses; "
         "it does not replace the primary split. Valid novelty is also reported separately. OOD means held "
         "out from project training, not necessarily from model pretraining."),
        ("Results and claims", "All tables and figures in this paper are generated from saved records. "
         "Pending cells indicate experiments without saved evaluation evidence. The machine-readable primary "
         f"analysis reports {status}. Implementation checks do not establish mathematical performance. "
         "Calibration cases are constructed expectations, not human preference evidence."),
        ("Development execution", f"Preserved development logs contain "
         f"{sum(r['completed_responses'] for r in snapshot['development'])} completed judge responses and "
         f"{sum(r['incomplete_requests'] for r in snapshot['development'])} requests without a completed response. "
         "These counts are generated from reports/development logs. An interrupted CPU judging attempt and "
         "runtime changes are documented in the dated judge-runtime amendment. Partial judgments do not "
         "establish calibration reliability. The first conventional proof received nonzero novelty credit; "
         "dedicated contrasts must test whether novelty is measured consistently. No comparative conclusion follows. "
         + feasibility_text(snapshot)),
        ("Transfer evaluation", "Recipient accuracy is compared with no notes, unrelated notes of matched "
         "length, and notes from other frozen source policies. Paired uncertainty resamples source problems "
         "with all four targets retained. Comparisons require complete matching source and target coverage. "
         "The machine-readable report publishes each source policy's related-minus-unrelated contrast "
         "and all pairs of note-source policies, with unadjusted exploratory intervals."),
        ("Discussion and limitations", "Judge scores are imperfect proxies and the two model families may "
         "share biases or training data. Quantization can change judgments. Synthetic elementary tasks limit "
         "external validity, and fixed small-seed comparisons may be inconclusive. Reusable exposition is not "
         "equivalent to historically novel mathematics. Higher training scores without independent or transfer "
         "improvement are consistent with proxy optimization. Do not infer a latent mechanism from behavioral "
         "scores alone. Development/test separation and scoped claims follow methodological guidance [10,11]."),
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
]
AI_STATEMENT = ("AI statement: Codex wrote this codebase and paper from the exact specification provided "
                "by a human. Human cleanup and rewriting are in progress.")


def write_paper(snapshot, rows, destination: Path):
    """Render one source of numerical truth into a paginated, linked ReportLab paper."""
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    font = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    font_name = "Helvetica"
    if font.exists():
        pdfmetrics.registerFont(TTFont("DejaVu", str(font)))
        font_name = "DejaVu"
    styles = getSampleStyleSheet()
    for style in styles.byName.values():
        style.fontName = font_name
    styles["BodyText"].fontSize = 9
    styles["BodyText"].leading = 13
    title = "Correctness-gated mathematical theory building"
    date = datetime.now(timezone.utc).date().isoformat()
    story = [Paragraph(title, styles["Title"]),
             Paragraph(f"Libor “Burny” Burian · {date}", styles["Normal"]), Spacer(1, .15*inch)]
    markdown = [f"# {title}", f"Libor “Burny” Burian · {date}"]
    for heading, body in paper_sections(snapshot):
        markdown.extend([f"## {heading}", body])
        story.extend([Paragraph(heading, styles["Heading2"]), Paragraph(html.escape(body), styles["BodyText"])])
        if heading == "Method":
            story.append(Image(str(PROJECT / "site/figures/architecture.png"), width=6.7*inch, height=2.01*inch))
        if heading == "Results and claims":
            formatted = [[Paragraph(html.escape(cell), styles["BodyText"]) for cell in row] for row in rows]
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
        if heading == "Transfer evaluation":
            transfer_table = transfer_rows(snapshot)
            formatted = [[Paragraph(html.escape(cell), styles["BodyText"]) for cell in row] for row in transfer_table]
            table = Table(formatted, colWidths=[3.8*inch, .8*inch, 1.0*inch], repeatRows=1)
            table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#edf5f5")),
                                      ("VALIGN", (0,0), (-1,-1), "TOP"),
                                      ("LINEBELOW", (0,0), (-1,0), .5, colors.grey)]))
            story.extend([Spacer(1, 8), table])
            markdown.append(markdown_table(transfer_table))
    story.append(Paragraph("References", styles["Heading2"]))
    markdown.append("## References")
    for i, (title, url) in enumerate(REFERENCES, 1):
        story.append(Paragraph(f'[{i}] <link href="{html.escape(url)}" color="#225d69">{html.escape(title)}</link>', styles["BodyText"]))
        markdown.append(f"[{i}] [{title}]({url})")
    story.extend([Spacer(1, 12), Paragraph(html.escape(AI_STATEMENT), styles["BodyText"])])
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
    atomic_json(PROJECT / "site/snapshot.json", snapshot)
    atomic_json(PROJECT / "reports/results.json", snapshot)
    rows = table_rows(snapshot)
    table = markdown_table(rows)
    figures(snapshot, PROJECT / "site/figures")
    summary = ("# Experiment summary\n\nGenerated from saved artifacts at " + snapshot["generated_at"] +
               ".\n\nCorrectness is verified final-answer accuracy. Theory is a frozen judge's rubric "
               "assessment, not a proof certificate. C × theory weights that assessment by answer correctness. "
               "Pending means no result, not zero performance.\n\n" + table +
               "\n\n## Primary analysis\n\n```json\n" + json.dumps(snapshot["primary"], indent=2) + "\n```\n" +
               "\n## Secondary OOD analysis\n\nDescriptive paired intervals; not a replacement success criterion.\n\n```json\n" +
               json.dumps(snapshot["secondary_ood"], indent=2) + "\n```\n" +
               "\n## Frozen-recipient transfer\n\n" + markdown_table(transfer_rows(snapshot)) +
               "\n\n```json\n" + json.dumps(snapshot["transfer"], indent=2) + "\n```\n")
    (PROJECT / "reports/experiments.md").write_text(summary, encoding="utf-8")
    folder = PROJECT / "reports/experiments"
    folder.mkdir(exist_ok=True)
    (folder / "development-runtime.md").write_text(
        "# Development execution records\n\nGenerated from preserved timestamped logs. "
        "These are incomplete development attempts, not calibrated judges or comparative results. "
        "See the dated runtime amendment for rationale, interruptions and next checks.\n\n" +
        feasibility_text(snapshot) + "\n\n```json\n" +
        json.dumps({"judging": snapshot["development"], "feasibility": snapshot["feasibility"]},
                   indent=2, ensure_ascii=False) + "\n```\n", encoding="utf-8")
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
        content = content.split(start)[0] + start + "\n\n" + table + "\n\n" + end + content.split(end)[1]
    else:
        content += "\n## Recorded evaluation results\n\n" + start + "\n\n" + table + "\n\n" + end + "\n"
    readme.write_text(content, encoding="utf-8")
    write_paper(snapshot, rows, PROJECT / "reports/paper.pdf")
    return {"snapshot": str(PROJECT / "site/snapshot.json"), "paper": str(PROJECT / "reports/paper.pdf")}
