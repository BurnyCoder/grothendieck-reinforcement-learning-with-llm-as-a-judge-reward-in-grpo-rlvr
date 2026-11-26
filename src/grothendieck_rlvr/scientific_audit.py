"""Reproduce the dated study review from Git history, locked mathematical tasks and raw CPU inputs."""
import os
from pathlib import Path

from .audit_history import calibration_history, execution_history, generation_history, mathematical_objections, transcript_counts
from .audit_inventory import chronology, inventory
from .audit_math import audit_manifests, replay_generators
from .io import atomic_json, root
from .saved_correctness import ARMS, AUDIT, EXPLORATORY_PREFIX, file_hash, score_saved_correctness


def input_receipts(storage, archives):
    """Record the exact bytes used for each audit observation and dashboard trajectory."""
    generations = {f"generations/{EXPLORATORY_PREFIX}{arm}/{name}": archives/(EXPLORATORY_PREFIX+arm)/name
                   for arm in ARMS for name in ("generation-config.json", "generations.jsonl", "events.jsonl")}
    paths = {}
    for name in ("pilot-theory-seed42", "exploratory-single-v2-pilot-theory-seed42",
                 EXPLORATORY_PREFIX+"pilot-theory-seed42"):
        for item in ("events.jsonl", "checkpoint-1/adapter_model.safetensors", "checkpoint-2/adapter_model.safetensors"):
            key = f"runs/{name}/{item}"
            paths[key] = storage/key
    for name in (EXPLORATORY_PREFIX+"theory-seed42", EXPLORATORY_PREFIX+"pilot-cache-release-v1-theory-seed42"):
        for item in ("events.jsonl", "run.json"):
            key = f"runs/{name}/{item}"
            paths[key] = storage/key
    for path in sorted((storage/"runs").glob("*/metrics.jsonl")):
        paths[path.relative_to(storage).as_posix()] = path
    return {name: {"sha256": file_hash(path), "bytes": path.stat().st_size}
            for name, path in sorted((paths | generations).items())}


def rebuild_evidence(storage, archives, output):
    """Rebuild each independent result from its primary records."""
    for name, function in (("manifests", audit_manifests), ("generator-replay", replay_generators), ("calibration", calibration_history),
                           ("execution", lambda: execution_history(storage)), ("objections", mathematical_objections),
                           ("transcripts", transcript_counts), ("generation", lambda: generation_history(archives)),
                           ("inventory", inventory), ("chronology", chronology),
                           ("raw-inputs", lambda: input_receipts(storage, archives))):
        print(f"Checking {name}", flush=True)
        atomic_json(output/(name+".json"), function())


def reproduce_scientific_audit(storage=None, archives=None, workers=2):
    """One offline command for all new numerical records, figures and publications."""
    storage = Path(storage).resolve() if storage else root()
    archives = Path(archives) if archives else (storage/"generations" if (storage/"generations").is_dir()
                                              else storage/"evaluations")
    os.environ["GROTH_ROOT"] = str(storage)
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    result = score_saved_correctness(archives, AUDIT, workers)
    if result["status"] != "complete":
        raise RuntimeError("Unresolved verifier failures; inspect per-answer records before publishing")
    rebuild_evidence(storage, archives, AUDIT)
    from .reporting import report
    return report()
