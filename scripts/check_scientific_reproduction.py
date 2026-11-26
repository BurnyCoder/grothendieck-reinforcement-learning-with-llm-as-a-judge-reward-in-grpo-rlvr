"""Compare a clean CPU rebuild to the published records, text and figures using only the standard library."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCORES = Path("results/scientific-audit")
RAW_REVISION = "c691b4eb6a83ca732a71d65cccda9e2fe8074937"


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def comparable(path):
    """Report timestamps may differ. PDF text is extracted independently from its Markdown source."""
    if path.suffix == ".pdf":
        return subprocess.check_output(["pdftotext", "-layout", "-enc", "UTF-8", str(path), "-"]).replace(b"\r\n", b"\n")
    if path.suffix == ".json" and path.name in ("results.json", "snapshot.json"):
        value = json.loads(path.read_bytes())
        del value["generated_at"]
        return canonical(value)
    if path.suffix == ".md":
        content = path.read_text(encoding="utf-8")
        # The first line below dates an export; all scientific dates and raw event times are retained.
        return re.sub(r"(Generated from saved artifacts at )\d{4}-\d\d-\d\dT[^\s]+\.",
                      r"\1[export time].", content).encode()
    return path.read_bytes()


def compare(rebuild):
    names = ("ordinary", "prompted", "baseline-summary", "manifests", "generator-replay", "calibration",
             "execution", "transcripts", "generation", "objections", "inventory", "chronology", "raw-inputs",
             "checkpoint-cards")
    files = [SCORES/(name+".json") for name in names]
    files += [Path(p) for p in ("README.md", "docs/dataset-card.md", "reports/paper.md", "reports/paper.pdf",
              "reports/experiments.md", "reports/summary.md", "reports/results.json", "site/snapshot.json",
              "reports/generation/README.md", "reports/reviews/2026-11-26-scientific-audit.md")]
    files += sorted(p.relative_to(ROOT) for p in (ROOT/"site/figures").glob("*") if p.is_file())
    hashes = {}
    for path in files:
        expected, actual = comparable(ROOT/path), comparable(rebuild/path)
        if expected != actual:
            raise ValueError(f"Clean reproduction differs: {path}")
        hashes[path.as_posix()] = digest(expected)
    # Also require agreement across surfaces in each checkout. A jointly stale publication would otherwise pass.
    for tree in (ROOT, rebuild):
        baseline = json.loads((tree/SCORES/"baseline-summary.json").read_bytes())
        snap = json.loads((tree/"site/snapshot.json").read_bytes())
        if snap["cpu_baseline"] != baseline or snap != json.loads((tree/"reports/results.json").read_bytes()):
            raise ValueError("Site and report do not publish the item-derived estimates")
        rendered = [tree/p for p in ("README.md","docs/dataset-card.md","reports/paper.md","reports/summary.md",
                    "reports/experiments.md","reports/reviews/2026-11-26-scientific-audit.md")]
        if any(snap["baseline_description"] not in p.read_text(encoding="utf-8") for p in rendered):
            raise ValueError("A published narrative differs from the paired results")
    return {"status": "matched", "raw_dataset_revision": RAW_REVISION, "sha256": hashes,
            "comparison": "Exact audit JSON bytes and figures, normalized snapshot JSON, Markdown with export timestamp excluded, PDF extracted text. Dated HTTP observations and the failed system-Python attempt are preserved inputs."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("clean_checkout", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    result = compare(args.clean_checkout.resolve())
    if args.receipt:
        args.receipt.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(result["status"], len(result["sha256"]), "artifacts")
