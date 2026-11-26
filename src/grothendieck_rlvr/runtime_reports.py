"""Describe interrupted execution from saved measurements, without learning claims."""
from .io import PROJECT

GROWTH_KIND = "cuda_allocator_growth_interruption"


def growth_text(record):
    """Separate allocator reservation from occupied tensor memory and completed arms."""
    summary = record["summary"]
    return (
        f"The {record['run_id']} attempt stopped at optimizer boundary {summary['step']} "
        f"with peak allocated/reserved policy memory {summary['peak_gpu_allocated_bytes']/2**30:.2f}/"
        f"{summary['peak_gpu_reserved_bytes']/2**30:.2f} GiB. "
        f"The pinned generated configuration's cache-clearing interval was "
        f"{record['effective_default_empty_cache_steps']} steps. "
        "Checkpoint state and partial outputs are preserved. This is an incomplete execution attempt, "
        "not a completed comparison or evidence that mathematical performance improved or worsened."
    )


def write_runtime_reports(snapshot, markdown_table):
    """Regenerate the runtime table and plots from the recorded optimizer intervals."""
    import matplotlib.pyplot as plt

    for record in snapshot["feasibility"]:
        if record.get("kind") != GROWTH_KIND:
            continue
        updates = record["updates"]
        steps = [row["step"] for row in updates]
        rows = [["Update", "Step seconds", "Peak allocated GiB", "Peak reserved GiB"]]
        rows.extend([str(row["step"]), f"{row['metrics']['step_time']:.2f}",
                     f"{row['peak_gpu_allocated_bytes']/2**30:.2f}",
                     f"{row['peak_gpu_reserved_bytes']/2**30:.2f}"] for row in updates)
        figure, axes = plt.subplots(1, 2, figsize=(10, 3.5))
        for field, label in (("peak_gpu_allocated_bytes", "Allocated tensors"),
                             ("peak_gpu_reserved_bytes", "Reserved allocator memory")):
            axes[0].plot(steps, [row[field]/2**30 for row in updates], marker="o", label=label)
        axes[0].set_ylabel("Cumulative peak GiB")
        axes[0].legend(fontsize=8)
        axes[1].plot(steps, [row["metrics"]["step_time"] for row in updates], marker="o")
        axes[1].set_ylabel("Recorded step seconds")
        for axis in axes:
            axis.set_xlabel("Optimizer update")
            axis.set_ylim(bottom=0)
            axis.grid(alpha=.2)
        figure.suptitle("Interrupted training: memory growth and step timing\nAssociation within one run; no isolated causal estimate", fontsize=10)
        figure.tight_layout()
        filename = record["experiment"] + "-memory-growth"
        figure.savefig(PROJECT / "site/figures" / (filename + ".png"), dpi=160)
        plt.close(figure)
        (PROJECT / "reports/experiments" / (filename + ".md")).write_text(
            "# Interrupted training: CUDA allocator growth\n\n" + growth_text(record) +
            "\n\n![Recorded policy memory and step times](../../site/figures/" + filename + ".png)\n\n" +
            markdown_table(rows) + "\n\n"
            "Source: [saved execution evidence](../development/feasibility-small-gpu-v2-cache-growth.json). "
            "Steps have different sampled completions and judge workloads. Peaks are cumulative within "
            "the policy process and exclude the separate judge's allocator. No OOM or isolated causal "
            "mechanism is established by this trajectory.\n\n"
            f"[Preserved checkpoints and full logs](https://huggingface.co/datasets/BurnyCoder/grothendieck-rlvr/tree/main/runs/{record['run_id']}) "
            "include optimizer, scheduler, RNG, data position and judge-cache state.\n\n"
            "The [registered development intervention](../amendments/2026-11-16-cuda-cache-diagnostic.md) "
            "tests the existing Trainer cache-release option. Its updates are discarded. "
            + snapshot.get("audit_conclusions", "") + "\n", encoding="utf-8")
