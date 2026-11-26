"""Offline scientific controls for preregistered scoring and eligibility."""
import pytest

from grothendieck_rlvr.analysis import h1_decision, primary_comparison
from grothendieck_rlvr.saved_correctness import form_failure


@pytest.mark.parametrize("family,answer,gold,violation", [
    ("dice", "2 / 4", "1/2", "fraction_form"),
    ("dice", "1 / 2", "1/2", None),
    ("polynomial_multiplication", "(x+2)*(x-2)", "x**2-4", "polynomial_form"),
    ("polynomial_multiplication", "-4 + (1/2)*2*x**2", "x**2-4", None),
    ("polynomial_equations", "0.49999", "0.5", "rounded_roots"),
    ("polynomial_equations", "1.00,-2", "-2.0,1.0", None),
    ("polynomial_equations", "", "", None),
])
def test_frozen_form_controls(family, answer, gold, violation):
    assert form_failure(family, answer, gold) == violation


def test_registered_decision_boundaries():
    import math
    def decide(point=.05, low=.01, high=.1, acc_low=-.029, acc_high=.02):
        return h1_decision({"difference": point, "ci95": [low, high]}, {"ci95": [acc_low, acc_high]})
    assert decide() == "criteria_met"
    assert decide(point=.049) == "inconclusive"
    assert decide(low=0) == "inconclusive"
    assert decide(acc_low=-.03) == "inconclusive"
    assert decide(point=.02, high=.049) == "useful_gain_ruled_out"
    assert decide(acc_low=-.09, acc_high=-.031) == "accuracy_inferior"
    assert decide(point=math.nextafter(.05, 0)) == "inconclusive"
    assert decide(low=math.nextafter(0, 1)) == "criteria_met"
    assert decide(acc_low=math.nextafter(-.03, 0)) == "criteria_met"


def test_off_manifest_inputs_never_confirm():
    cfg = {"training_seeds": [42, 43, 44], "bootstrap_samples": 20, "data_seed": 1,
           "test_fresh_size": 1, "test_hard_size": 1, "test_unseen_size": 1}
    rows = [{"task_id": k, "family": "gcd", "split": k, "correct": True,
             "metric": .25, "judge_identity": "fixture"} for k in ("test_fresh", "test_hard", "test_unseen")]
    evaluations = {f"{arm}-seed{s}": rows for arm in ("theory", "correctness") for s in cfg["training_seeds"]}
    assert primary_comparison(evaluations, cfg)["status"] == "incomplete"


def test_comparison_requires_full_matched_evidence(monkeypatch):
    from types import SimpleNamespace
    import grothendieck_rlvr.analysis as analysis
    tasks = [SimpleNamespace(id=str(i), split=s, family="gcd")
             for i, s in enumerate(("test_fresh", "test_hard", "test_unseen"))]
    monkeypatch.setattr(analysis, "locked_tasks", lambda secondary: tasks)
    cfg = {"training_seeds": [42, 43, 44], "bootstrap_samples": 20, "data_seed": 1,
           **{t.split + "_size": 1 for t in tasks}}
    data = {f"{arm}-seed{s}": [{"task_id": t.id, "split": t.split, "family": t.family,
                                "metric": val, "theory": val, "correct": True,
                                "verification": {"status": "correct"}, "judge_identity": "fixture"} for t in tasks]
            for arm, val in (("theory", .5), ("correctness", 0)) for s in cfg["training_seeds"]}
    assert primary_comparison(data, cfg)["status"] == "unqualified"
    assert primary_comparison(data, cfg, exploratory=True)["criteria_met"] is None
    monkeypatch.setattr(analysis, "qualified_evidence", lambda *args: None)
    assert primary_comparison(data, cfg)["criteria_met"] is True
    data["theory-seed42"][0]["judge_identity"] = "different"
    with pytest.raises(ValueError, match="identical"):
        primary_comparison(data, cfg)
    data["theory-seed42"].pop(0)
    assert primary_comparison(data, cfg)["status"] == "incomplete"


def test_transfer_rejects_substituted_probes_and_missing_conditions(tmp_path, monkeypatch):
    import json
    import grothendieck_rlvr.analysis_evidence as evidence
    from grothendieck_rlvr.analysis import transfer_analysis
    from grothendieck_rlvr.io import atomic_json, digest
    from grothendieck_rlvr.prompts import policy_messages
    sources = evidence.load_tasks("transfer_source")
    targets = evidence.load_tasks("transfer_target")
    cfg = {"bootstrap_samples": 10, "transfer_sources": len(sources)}
    frozen = {"model": "fixture"}
    monkeypatch.setattr("grothendieck_rlvr.evaluation.inference_identity", lambda: frozen)
    config = {"source_runs": ["ordinary"], "source_configs": {"ordinary": {}}, "inference": frozen,
              "note_token_limit": 1024, "tasks": digest([t.model_dump() for t in sources+targets]),
              "prompts": digest([[policy_messages(t), policy_messages(t, notes="")] for t in targets])}
    atomic_json(tmp_path/"config.json", config)
    assert evidence.registered_transfer(tmp_path, cfg, transfer_analysis)["status"] == "pending"
    rows = [{"task_id": t.id, "source_id": t.source_id, "family": t.family, "correct": False,
             "verification": {"status": "incorrect"}, "condition": condition} for t in targets
            for condition in ("no_notes", "ordinary:notes", "ordinary:unrelated")]
    def check(sample):
        (tmp_path/"scores.jsonl").write_text("\n".join(map(json.dumps, sample)))
        return evidence.registered_transfer(tmp_path, cfg, transfer_analysis)
    assert check(rows[:-1])["status"] == "incomplete"
    assert check([{**rows[0], "task_id": "unregistered"}, *rows[1:]])["status"] == "incomplete"
    assert "note condition" in check(rows)["reason"]


def test_final_checkpoint_requires_both_matching_files(tmp_path):
    from grothendieck_rlvr.analysis_evidence import matches_checkpoint
    from grothendieck_rlvr.saved_correctness import file_hash
    config, weights = tmp_path/"adapter_config.json", tmp_path/"adapter_model.safetensors"
    config.write_text("{}")
    weights.write_bytes(b"fixture checkpoint bytes")
    frozen = {"files": {p.name: file_hash(p) for p in (config, weights)}}
    assert matches_checkpoint(tmp_path, frozen)
    weights.write_bytes(b"different checkpoint")
    assert not matches_checkpoint(tmp_path, frozen)
    weights.unlink()
    assert not matches_checkpoint(tmp_path, frozen)


def test_complete_transfer_links_note_text_to_source_and_recipient(tmp_path, monkeypatch):
    import json
    import grothendieck_rlvr.analysis_evidence as evidence
    from grothendieck_rlvr.analysis import transfer_analysis
    from grothendieck_rlvr.io import atomic_json, digest
    from grothendieck_rlvr.prompts import policy_messages
    from grothendieck_rlvr.saved_correctness import file_hash
    sources = list({t.family:t for t in evidence.load_tasks("transfer_source")}.values())
    ids = {s.id for s in sources}
    targets = [t for t in evidence.load_tasks("transfer_target") if t.source_id in ids]
    monkeypatch.setattr(evidence,"load_tasks",lambda split: sources if split == "transfer_source" else targets)
    base = {"model": "fixture", "max_new_tokens": 16, "files": {}}
    monkeypatch.setattr("grothendieck_rlvr.evaluation.inference_identity",lambda: base)
    def jsonl(path, rows):
        path.write_text("\n".join(map(json.dumps,rows)))
    directory = tmp_path/"transfer"
    cfg = {"bootstrap_samples": 20, "transfer_sources": len(sources), "training_seeds": [42], "max_steps": 2}
    names = ("ordinary", "prompted", "theory-seed42", "correctness-seed42")
    configs, note_sets = {}, {}
    ordered = sorted(sources,key=lambda t:(t.family,t.id))
    rotation = {s.id: ordered[(i+1)%len(ordered)].id for i,s in enumerate(ordered)}
    for name in names:
        rising, adapter, inference = name == "prompted", None, base
        if "seed" in name:
            run = tmp_path/"runs"/name
            ckpt = run/"checkpoint-2"
            atomic_json(ckpt/"groth-state.json", {"global_step":2,"complete":True})
            atomic_json(run/"summary.json", {"step":2,"completed":True,"pilot":False})
            for f in ("adapter_config.json","adapter_model.safetensors"):
                (ckpt/f).write_bytes((name+f).encode())
            adapter = str(run/"adapter")
            inference = {**base, "files": {p.name:file_hash(p) for p in ckpt.iterdir()}}
        prompts = {s.id:policy_messages(s,rising=rising,request_notes=True) for s in sources}
        configs[name] = {"run_id":name,"rising":rising,"adapter":adapter,"split":"transfer_source","inference":inference,
                         "prompts":digest(prompts),"tasks":digest([s.model_dump() for s in sources])}
        src = tmp_path/"evaluations"/name
        atomic_json(src/"generation-config.json",configs[name])
        note_sets[name] = {s.id:chr(97+i) for i,s in enumerate(sources)}
        jsonl(src/"generations.jsonl",[{"task_id":s.id,"prompt":prompts[s.id],"response":"<notes>"+note_sets[name][s.id]+"</notes>"} for s in sources])
    atomic_json(directory/"config.json",{"source_runs":names,"source_configs":configs,"seed":42,"inference":base,
        "notes":digest(note_sets),"note_token_limit":1024,"tasks":digest([t.model_dump() for t in sources+targets]),
        "prompts":digest([[policy_messages(t),policy_messages(t,notes="")] for t in targets])})
    rows, events = [], []
    for t in targets:
        conditions = [("no_notes", None, None)]
        for name in names:
            other = rotation[t.source_id]
            conditions.extend([(name+":notes",note_sets[name][t.source_id],other),
                               (name+":unrelated",note_sets[name][other],other)])
        for condition, notes, other in conditions:
            rows.append({"task_id":t.id,"source_id":t.source_id,"family":t.family,"condition":condition,
                         "notes":notes,"unrelated_source_id":other,"notes_tokens":int(notes is not None),"correct":False,
                         "verification":{"status":"incorrect"},"response":"fixture","seconds":1.0})
            events.extend([{"kind":"policy_request","messages":policy_messages(t,notes=notes),"seed":42,"max_new_tokens":16},
                           {"kind":"policy_response","response":"fixture","seconds":1.0}])
    jsonl(directory/"scores.jsonl",rows)
    jsonl(directory/"events.jsonl",events)
    result = evidence.registered_transfer(directory,cfg,transfer_analysis)
    assert result["status"] == "exploratory"
    assert result["versus_unrelated"]["theory-seed42"]["problems"] == len(sources)
    rows[1]["notes"] = rows[2]["notes"]
    jsonl(directory/"scores.jsonl",rows)
    assert evidence.registered_transfer(directory,cfg,transfer_analysis)["status"] == "incomplete"
