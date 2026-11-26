"""Index the audited Git tree by immutable blob and source location, including historical versions."""
import ast
import hashlib
import json
import posixpath
import re
import subprocess
from pathlib import Path

from .io import PROJECT

START = "fac5d9e788c33d066e1e92289fbf220e11e26625"
HUB_BEFORE = "53ff4ae5ef4a1a3da4ca01fb889af0518310fa13"
LINK = re.compile(r"https?://[^\s<>()\]\"'`]+")
TOPICS = {
    "registration": r"preregist|noninferior|bootstrap|transfer|seed pairs|hypothes|confirmatory",
    "datasets": r"manifest|generator|overlap|deduplic|dataset|out.of.distribution|held.out famil",
    "answers": r"verif|final.answer|accuracy|rounding|fraction|invalid.format",
    "generation": r"generat|ordinary|prompted|receipt|decoding",
    "calibration": r"calibrat|threshold|suppression|futility|judg|rubric|specialist",
    "mathematics": r"coset|subgroup|commut|quadratic algebra|parity|norm map|objection",
    "objective": r"optimizer|learning rate|train|reward|GRPO|LoRA|normaliz|advantage",
    "runtime": r"GPU|CPU|CUDA|latency|memory|seconds|checkpoint|pilot|resum|timeout|offload|thread",
    "literature": r"arxiv|empirical|prior work|FERMAT|G-Eval|benchmark|literature",
    "history": r"quotation|Grothendieck wrote|McLarty|transcript|social.media|supplied wording",
    "scope": r"proposal|defer|future|unmeasured|limitation|not establish|pretrain|latent",
}


def git(*args):
    return subprocess.check_output(["git", "-C", str(PROJECT), *args])


def claim_lines(path, data):
    """Keep verbatim text and offsets. Classify data and instructions separately from author conclusions."""
    ext = Path(path).suffix
    if ext == ".py":
        source = data.splitlines()
        tree = ast.parse(data)
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and len(node.value.split()) >= 5:
                yield node.lineno, node.value.strip()
        for i, line in enumerate(source, 1):
            if line.lstrip().startswith("#"):
                yield i, line.strip()
    elif ext == ".json":
        # Report prose stored inside JSON. Raw model responses and synthetic task inputs are observations.
        fields = {"interpretation", "decision", "remaining_gates", "qualification", "hypothesis", "initialization",
                  "conclusion", "limitations", "rationale", "scope", "description", "reason", "notes"}
        for i,line in enumerate(data.splitlines(),1):
            m = re.match(r'^\s*"([^"]+)"\s*:\s*(".*")\s*,?\s*$', line)
            if m and m[1] in fields:
                yield i, json.loads(m[2])
    else:
        for match in re.finditer(r"[^\n].*?(?=\n\s*\n|\Z)", data, re.S):
            content = match.group().strip()
            if content and not content.startswith(("```", "<!--", "![", "# ")):
                yield data.count("\n", 0, match.start())+1, content


def disposition(path, content, topics):
    """Map dated corrections and quotations at passage level, with explicit evidential limits."""
    s = " ".join(content.lower().split())
    if "correctness and theory scores remain unmeasured" in s or "mathematical scoring remains pending" in s or "independent scoring remains pending" in s:
        return "superseded", "CPU final-answer scores now exist for both archived prompts. Theory remains unmeasured.", "answers"
    if "independent-family judgment" in s or "preferred policy is" in s:
        return "chronology clarified", "The cross-family design predates the active same-family experiment.", "objective"
    if "cache-release" in s and ("diagnostic" in s or "intervention" in s):
        return "dated update", "The intervention produced a partial trajectory before its required resumption.", "runtime"
    if "removing its assignment" in s or "breaks the association" in s:
        return "qualified", "A random permutation can preserve individual assignments and repeated values.", "objective"
    if path == "docs/rising-sea-quotations.md" or "rising-sea-" in path and path.endswith(".txt"):
        return "attributed material", "The historical analogy has a scholarly source. Exact supplied wording requires its own provenance.", "history"
    if path.startswith("tests/") or "/prompts/" in path or "novelty_cases.py" in path:
        return "test input or instrument", "Instructions, candidate text and synthetic expectations are specifications or stored inputs.", None
    if path.startswith(("reports/amendments/", "configs/")) or path.endswith("preregistration.md"):
        return "historical design or recorded rationale", "Read the dated identity with its contemporaneous records and amendments.", None
    if path.startswith("reports/experiments/") or path.startswith("reports/development/"):
        return "historical observation or interpretation", "Recomputed instrument and runtime evidence qualifies the historical observation.", None
    if "future" in path or path in ("AGENTS.md", "docs/runbook.md") or s.startswith(("#","bash ","uv ")):
        return "instruction or plan", "An intended procedure supplies no empirical effect estimate.", None
    if topics:
        return "reviewed in companion register", "Use the linked sources and stated evidence limits for each applicable claim.", None
    return "non-scientific or unattributed text", "No empirical assertion is independently certified by this passage.", None


def inventory():
    """Use one batch git-object read; the original checkout is sufficient even after later corrections."""
    raw = git("ls-tree", "-r", "-z", START).split(b"\0")
    files, scan = [], []
    for entry in filter(None, raw):
        desc, path = entry.decode().split("\t", 1)
        sha = desc.split()[-1]
        ext = Path(path).suffix
        typ = ("primary record or configuration" if ext in (".json", ".jsonl", ".csv", ".log", ".xml", ".lock")
               else "published rendering" if ext in (".png", ".svg", ".pdf") else
               "verification code" if path.startswith("tests/") else "source or narrative")
        files.append({"path": path, "git_blob": sha, "role": typ})
        if (ext in (".md", ".py", ".sh", ".html", ".js", ".mjs", ".cpp") or path in ("NOTICE", "LICENSE")
                or "/prompts/" in path or ext == ".json" and (path.startswith("configs/") or
                path.startswith(("reports/development/", "reports/generation/")))):
            scan.append((path, sha))
    payload = "\n".join(sha for _, sha in scan).encode()+b"\n"
    batch = subprocess.check_output(["git", "-C", str(PROJECT), "cat-file", "--batch"], input=payload)
    texts, offset = [], 0
    for path, _ in scan:
        end = batch.index(b"\n", offset)
        size = int(batch[offset:end].split()[-1])
        texts.append((path, batch[end+1:end+1+size].decode("utf-8-sig")))
        offset = end+size+2
    files.append({"path": "Hugging Face dataset card", "revision": HUB_BEFORE, "role": "public narrative"})
    # The pinned remote README and the original Git card were independently downloaded and byte-compared.
    card = git("show", START + ":docs/dataset-card.md")
    if hashlib.sha256(card).hexdigest() != "4ed8ee633954087976a775bda688db244e5f2fe03ad8bd74ea7917cf3869fdda":
        raise ValueError("Archived Hub card differs from its verified bytes")
    texts.append(("Hugging Face dataset card", card.decode()))
    paragraphs, urls = [], set()
    for path, data in texts:
        for line, content in claim_lines(path, data):
            topics = [name for name, regex in TOPICS.items() if re.search(regex, content, re.I)]
            external = sorted(set(LINK.findall(content)))
            urls.update(u.rstrip(".,;:") for u in external)
            state, meaning, corrected_topic = disposition(path, content, topics)
            local = [posixpath.normpath(posixpath.join(posixpath.dirname(path), x.split("#")[0]))
                     for x in re.findall(r"\]\(([^)]+)\)", content)
                     if x and not x.startswith(("http", "#"))]
            if corrected_topic and corrected_topic not in topics:
                topics.insert(0, corrected_topic)
            paragraphs.append({"path": path, "line": line, "text": content, "topics": topics,
                               "cited_urls": external, "local_references": local, "disposition": state, "review": meaning})
    return {"git_revision": START, "files": files, "passages": paragraphs, "cited_urls": sorted(urls),
            "interpretation": "Index of original files and claim-bearing passages. Topic links refer to the reviewed claims in the companion register; matching a topic or resolving a URL does not verify each sentence."}


def chronology():
    """Record original branch history, every dated amendment's introduction, and the audit registration."""
    def history(*args):
        lines = git("log", "--reverse", "--format=%H%x09%cI%x09%s", *args).decode().splitlines()
        return [dict(zip(("commit", "committer_time", "subject"), line.split("\t", 2))) for line in lines]
    amendments = sorted(git("ls-tree", "-r", "--name-only", START, "reports/amendments").decode().splitlines())
    return {"original_registration": history(START, "--", "reports/preregistration.md")[0],
            "audit_registration": history("3e2d4be", "--", "reports/amendments/2026-11-26-cpu-baseline-audit.md")[0],
            "original_first_parent": history("--first-parent", START),
            "amendments": {name: history("--diff-filter=A", START, "--", name)[0] for name in amendments},
            "qualification": "Git timestamps describe recorded chronology. The baseline scoring protocol was publicly merged in PR 56 before scoring."}
