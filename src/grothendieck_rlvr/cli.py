"""Thin CLI: each phase delegates to one independently testable module."""
import argparse
import json
import os
import traceback
from pathlib import Path

from .io import EventLog, root


def parser():
    """Keep phase selection explicit so generation never implicitly starts training."""
    p = argparse.ArgumentParser(description="Local Grothendieck-inspired RLVR research environment")
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("prepare", "prepare-ood", "doctor", "hash-models", "report", "memory-probe"):
        sub.add_parser(name)
    benchmark = sub.add_parser("benchmark-judge")
    benchmark.add_argument("--sweep", choices=["threads", "offload"], default="threads")
    download = sub.add_parser("download")
    download.add_argument("--role", default="all", choices=["all", "policy", "training_judge", "evaluation_judge"])
    serve = sub.add_parser("serve")
    serve.add_argument("--role", default="training_judge", choices=["training_judge", "evaluation_judge"])
    serve.add_argument("--gpu-layers", type=int, help="Must agree with the registered judge runtime")
    calibration = sub.add_parser("calibrate")
    calibration.add_argument("--role", default="training_judge", choices=["training_judge", "evaluation_judge"])
    calibration.add_argument("--variant", default="quoted", choices=["quoted", "rubric"])
    calibration.add_argument("--split", default="dev", choices=["dev", "audit"])
    calibration.add_argument("--restart-development", action="store_true",
                             help="Archive changed development inputs after a dated amendment; never resets audits")
    train = sub.add_parser("train")
    train.add_argument("--arm", default="theory", choices=["theory", "correctness", "shuffled", "rubric"])
    train.add_argument("--seed", type=int, default=42)
    train.add_argument("--resume", action="store_true")
    train.add_argument("--pilot", action="store_true")
    train.add_argument("--runtime-diagnostic", choices=["cache-release-v1"],
                       help="Registered development-only runtime probe; requires --pilot --exploratory")
    train.add_argument("--stop-after", type=int)
    generate = sub.add_parser("generate")
    generate.add_argument("--run-id", required=True)
    generate.add_argument("--adapter", type=Path)
    generate.add_argument("--rising", action="store_true")
    generate.add_argument("--split", default="test", choices=["test", "test_ood", "dev", "transfer_source"])
    generate.add_argument("--seed", type=int, default=42)
    evaluate = sub.add_parser("evaluate")
    evaluate.add_argument("--run-id", required=True)
    scored = sub.add_parser("score-saved-correctness", help="Audit frozen baseline text on CPU")
    scored.add_argument("--archives", type=Path)
    scored.add_argument("--output", type=Path)
    scored.add_argument("--workers", type=int, default=2)
    audit = sub.add_parser("reproduce-scientific-audit", help="Rebuild the independent review from frozen CPU inputs")
    audit.add_argument("--storage", type=Path)
    audit.add_argument("--archives", type=Path)
    audit.add_argument("--workers", type=int, default=2)
    transfer = sub.add_parser("transfer")
    transfer.add_argument("--source-runs", nargs="+", required=True)
    for phase in (train, generate, evaluate, transfer):
        phase.add_argument("--exploratory", action="store_true",
                           help="Explicitly select the amended single-call experiment with unqualified judges")
    dashboard = sub.add_parser("dashboard")
    dashboard.add_argument("--port", type=int, default=8765)
    return p


def main():
    """Record actionable infrastructure failures with tracebacks instead of rewarding them."""
    args = vars(parser().parse_args())
    command = args.pop("command")
    try:
        if command == "prepare":
            from .data import prepare
            result = prepare()
        elif command == "prepare-ood":
            from .ood import prepare_ood
            result = prepare_ood()
        elif command in ("doctor", "download", "serve", "hash-models"):
            from . import models
            result = getattr(models, "artifact_hashes" if command == "hash-models" else command)(**args)
        elif command == "score-saved-correctness":
            from .saved_correctness import score_saved_correctness
            result = score_saved_correctness(**args)
        elif command == "reproduce-scientific-audit":
            from .scientific_audit import reproduce_scientific_audit
            result = reproduce_scientific_audit(**args)
        elif command == "calibrate":
            from .calibration import calibrate
            from .judge import Judge
            role = args.pop("role")
            url = os.environ.get("GROTH_EVAL_URL", "http://127.0.0.1:8082") if role == "evaluation_judge" \
                else os.environ.get("GROTH_JUDGE_URL", "http://127.0.0.1:8081")
            result = calibrate(Judge(url, role, args.pop("variant")), **args)
        elif command in ("train", "memory-probe"):
            from .training import train, memory_probe
            result = train(**args) if command == "train" else memory_probe()
        elif command == "benchmark-judge":
            from .benchmark import benchmark_judge
            result = benchmark_judge(**args)
        elif command == "generate":
            from .evaluation import generate
            result = generate(**args)
        elif command == "evaluate":
            from .evaluation import evaluate
            from .experiments import experiment_profile
            from .judge import Judge
            profile = experiment_profile(args["exploratory"], args["run_id"])
            result = evaluate(judge=Judge(os.environ.get("GROTH_EVAL_URL", "http://127.0.0.1:8082"),
                                          "evaluation_judge", protocol=profile["judge_protocol"] if profile else None),
                              **args)
        elif command == "transfer":
            from .evaluation import transfer
            result = transfer(args["source_runs"], exploratory=args["exploratory"])
        elif command == "report":
            from .reporting import report
            result = report()
        else:
            from .dashboard import serve_dashboard
            result = serve_dashboard(**args)
        if result is not None:
            print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)
    except Exception:
        EventLog(root() / "logs/failures.jsonl").emit("phase_failure", phase=command,
                                                     arguments={k: str(v) for k, v in args.items()},
                                                     traceback=traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
