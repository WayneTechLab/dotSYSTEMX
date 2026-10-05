"""Agent Z: fixed 10-by-10 evidence review, immutable scorecards, explicit deltas."""

import project_memory as memory
import agent_standards as records
from versions import version_id

RESULTS = ("pass", "partial", "fail", "unknown", "not_applicable")
STAGES = ("planned", "implemented", "checked", "deployed", "live_verified")
STAGE_ORDER = {stage: index for index, stage in enumerate(STAGES)}


def validate_policy(policy):
    memory.fields(policy, ("schemaVersion", "policyId", "version", "categories"), "Review policy")
    if type(policy["schemaVersion"]) is not int or policy["schemaVersion"] != 1:
        raise ValueError("Review policy schemaVersion must be 1")
    memory.string(policy["policyId"], "Policy ID")
    version_id(policy["version"])
    if not isinstance(policy["categories"], list) or len(policy["categories"]) != 10:
        raise ValueError("Agent Z requires exactly 10 categories")
    for index, category in enumerate(policy["categories"], 1):
        memory.fields(category, ("id", "name", "questions"), "Review category")
        if category["id"] != "C{:02d}".format(index):
            raise ValueError("Keep stable category IDs C01 through C10 in order")
        memory.string(category["name"], "Category name")
        if not isinstance(category["questions"], list) or len(category["questions"]) != 10:
            raise ValueError("Each Agent Z category requires exactly 10 questions")
        for number, question in enumerate(category["questions"], 1):
            memory.fields(question, ("id", "question"), "Review question")
            if question["id"] != "Z{:02d}.{:02d}".format(index, number):
                raise ValueError("Keep stable question IDs and ordering")
            memory.string(question["question"], "Question")
    return policy


def policy_path(policy):
    identity = {key: policy[key] for key in ("policyId", "version")}
    return "REVIEWS/policies/POL-" + records.fingerprint(identity)[:20] + ".json"


def request_path(identifier):
    return "REVIEWS/requests/" + records.token(identifier, "R") + ".json"


def report_path(identifier):
    return "REVIEWS/reports/" + records.token(identifier, "Z") + ".json"


def questions(policy):
    return [question for category in policy["categories"] for question in category["questions"]]


def validate_subject(subject):
    memory.fields(subject, ("kind", "id", "revision", "evidenceRevision", "stage", "task"), "Review subject")
    if subject["kind"] not in ("prompt", "task", "change", "project") or subject["stage"] not in STAGES:
        raise ValueError("Unknown review kind or evidence stage")
    for name in ("id", "revision", "evidenceRevision"):
        memory.string(subject[name], "Review subject " + name)
    memory.string(subject["task"], "Review task", nonempty=False)


def validate_answers(answers, policy):
    if not isinstance(answers, list) or len(answers) != 100:
        raise ValueError("Every review must retain all 100 answers, including unknowns and justified N/A")
    for answer, question in zip(answers, questions(policy)):
        memory.fields(answer, ("id", "result", "note", "evidence"), "Review answer")
        if answer["id"] != question["id"] or answer["result"] not in RESULTS:
            raise ValueError("Invalid answer ID, order, or result")
        memory.string(answer["note"], "Answer note", nonempty=answer["result"] != "unknown")
        memory.strings(answer["evidence"], "Answer evidence",
                       nonempty=answer["result"] in ("pass", "partial", "not_applicable"))


def load_request(root, identifier):
    request = records.read(root, request_path(identifier))
    memory.fields(request, ("schemaVersion", "id", "preparedAt", "subject", "policy", "policyHash", "answers"), "Review request")
    if type(request["schemaVersion"]) is not int or request["schemaVersion"] != 1:
        raise ValueError("Unsupported review request schema")
    policy = validate_policy(request["policy"])
    validate_subject(request["subject"])
    memory.timestamp(request["preparedAt"])
    validate_answers(request["answers"], policy)
    key = {"subject": request["subject"], "policyHash": records.fingerprint(policy)}
    if (request["id"] != identifier or identifier != "R-" + records.fingerprint(key)[:20] or
            request["policyHash"] != key["policyHash"]):
        raise ValueError("Review identity or policy snapshot was changed; prepare a new review")
    if records.read(root, policy_path(policy)) != policy:
        raise ValueError("Frozen policy version was changed; restore it or create a new policy version")
    return request


def prepare(root, args):
    policy = validate_policy(records.read(root, "REVIEWS/POLICY.json"))
    subject = {"kind": args.kind, "id": args.subject, "revision": args.revision,
               "evidenceRevision": args.evidence_revision, "stage": args.stage, "task": args.task or ""}
    validate_subject(subject)
    records.task_ids(root, [args.task] if args.task else [])
    policy_hash = records.fingerprint(policy)
    identifier = "R-" + records.fingerprint({"subject": subject, "policyHash": policy_hash})[:20]
    request = {"schemaVersion": 1, "id": identifier, "preparedAt": memory.now(),
               "subject": subject, "policy": policy, "policyHash": policy_hash,
               "answers": [{"id": q["id"], "result": "unknown", "note": "", "evidence": []} for q in questions(policy)]}
    path = request_path(identifier)
    snapshot = policy_path(policy)
    def check_existing():
        if records.safe(root, snapshot).exists() and records.read(root, snapshot) != policy:
            raise ValueError("This policy ID/version already has different questions; bump the policy version")
        if records.safe(root, path).exists():
            return load_request(root, identifier)
        return None
    existing = check_existing()
    if existing:
        return {"created": False, "reused": True, "requestPath": path, "request": existing}
    if args.apply:
        with memory.coordination_lock(root):
            existing = check_existing()
            if existing:
                return {"created": False, "reused": True, "requestPath": path, "request": existing}
            if not records.safe(root, snapshot).exists():
                records.write(root, snapshot, policy)
            records.write(root, path, request)
    return {"created": args.apply, "reused": False, "requestPath": path, "request": request,
            "instruction": "Evaluate the same 100 questions against this subject and evidence; edit answers only, then score. No checks were executed."}


def score_answers(answers, policy):
    validate_answers(answers, policy)
    totals = {result: 0 for result in RESULTS}
    categories = []
    for index, category in enumerate(policy["categories"]):
        counts = {result: 0 for result in RESULTS}
        for answer in answers[index * 10:(index + 1) * 10]:
            counts[answer["result"]] += 1
            totals[answer["result"]] += 1
        points = counts["pass"] + counts["partial"] * 0.5
        applicable = 10 - counts["not_applicable"]
        categories.append({"id": category["id"], "name": category["name"], "points": points,
                           "maximum": 10, "applicableMaximum": applicable, "counts": counts})
    points = totals["pass"] + totals["partial"] * 0.5
    applicable = 100 - totals["not_applicable"]
    return {"points": points, "maximum": 100, "applicableMaximum": applicable,
            "applicablePercent": round(100 * points / applicable, 2) if applicable else None,
            "coveragePercent": round(100 * (applicable - totals["unknown"]) / applicable, 2) if applicable else None,
            "counts": totals, "categories": categories,
            "decision": "advisory-only; score does not accept tasks or authorize deployment"}


def substance(value):
    return {key: value[key] for key in ("subject", "policy", "answers")}


def load_report(root, identifier):
    report = records.read(root, report_path(identifier))
    memory.fields(report, ("schemaVersion", "id", "requestId", "scoredAt", "subject", "policy",
                           "policyHash", "answers", "sourceHash", "score"), "Review report")
    if type(report["schemaVersion"]) is not int or report["schemaVersion"] != 1:
        raise ValueError("Unsupported report schema")
    validate_policy(report["policy"])
    validate_subject(report["subject"])
    validate_answers(report["answers"], report["policy"])
    memory.timestamp(report["scoredAt"])
    key = {"subject": report["subject"], "policyHash": records.fingerprint(report["policy"])}
    if (report["requestId"] != "R-" + records.fingerprint(key)[:20] or
            report["policyHash"] != key["policyHash"] or report["sourceHash"] != records.fingerprint(substance(report)) or
            report["id"] != identifier or identifier != "Z-" + report["sourceHash"][:20] or
            report["score"] != score_answers(report["answers"], report["policy"])):
        raise ValueError("Report contents or score changed; preserve original reports and create a new review")
    return report


def score(root, identifier, apply=False):
    request = load_request(root, identifier)
    data = substance(request)
    digest = records.fingerprint(data)
    report_id = "Z-" + digest[:20]
    path = report_path(report_id)
    report = {"schemaVersion": 1, "id": report_id, "requestId": identifier, "scoredAt": memory.now(),
              **data, "policyHash": request["policyHash"], "sourceHash": digest,
              "score": score_answers(request["answers"], request["policy"])}
    if records.safe(root, path).exists():
        return {"created": False, "reused": True, "reportPath": path, "report": load_report(root, report_id)}
    if apply:
        with memory.coordination_lock(root):
            # Refuse to publish a score after an editor changed its inputs during review.
            if records.fingerprint(substance(load_request(root, identifier))) != digest:
                raise ValueError("Review answers changed while preparing the score; inspect the latest request")
            if records.safe(root, path).exists():
                return {"created": False, "reused": True, "reportPath": path, "report": load_report(root, report_id)}
            records.write(root, path, report)
    return {"created": apply, "reused": False, "reportPath": path, "report": report}


def compare(root, before_id, after_id):
    before, after = load_report(root, before_id), load_report(root, after_id)
    if before["policyHash"] != after["policyHash"]:
        raise ValueError("Policy changed; start a new baseline instead of claiming a comparable score delta")
    if any(before["subject"][key] != after["subject"][key] for key in ("kind", "id", "task")):
        raise ValueError("Compare the same subject and scope")
    before_time, after_time = memory.timestamp(before["scoredAt"]), memory.timestamp(after["scoredAt"])
    if after_id != before_id and after_time < before_time:
        raise ValueError("The after report must be scored later than the before report; reverse the comparison operands or start a new baseline")
    ordering_verified = after_id == before_id or after_time > before_time
    before_stage, after_stage = before["subject"]["stage"], after["subject"]["stage"]
    if STAGE_ORDER[after_stage] < STAGE_ORDER[before_stage]:
        raise ValueError("The after report uses an earlier evidence stage; start a new baseline or correct the operands")
    changes = [{"id": old["id"], "before": old["result"], "after": new["result"],
                "evidenceChanged": old["evidence"] != new["evidence"], "noteChanged": old["note"] != new["note"]}
               for old, new in zip(before["answers"], after["answers"]) if old != new]
    point_delta = after["score"]["points"] - before["score"]["points"]
    applicable_delta = after["score"]["applicableMaximum"] - before["score"]["applicableMaximum"]
    applicability_changed = any((old["result"] == "not_applicable") != (new["result"] == "not_applicable")
                                for old, new in zip(before["answers"], after["answers"]))
    direction = ("order-unverified" if not ordering_verified else
                 "scope-changed" if applicable_delta or applicability_changed else
                 "improved" if point_delta > 0 else "regressed" if point_delta < 0 else "unchanged")
    return {"before": before_id, "after": after_id, "sameInputs": before["sourceHash"] == after["sourceHash"],
            "beforeScoredAt": before["scoredAt"], "afterScoredAt": after["scoredAt"],
            "orderingVerified": ordering_verified,
            "beforeStage": before_stage, "afterStage": after_stage,
            "beforeSubject": before["subject"], "afterSubject": after["subject"],
            "pointDelta": point_delta, "applicableMaximumDelta": applicable_delta,
            "beforeApplicablePercent": before["score"]["applicablePercent"],
            "afterApplicablePercent": after["score"]["applicablePercent"],
            "direction": direction,
            "changes": changes,
            "categoryDeltas": [{"id": old["id"], "delta": new["points"] - old["points"]}
                               for old, new in zip(before["score"]["categories"], after["score"]["categories"])],
            "automaticWork": False}


def add_cli(subparsers, scope):
    scope(subparsers.add_parser("policy", help="show the fixed policy; no evaluation or checks execute"))
    command = scope(subparsers.add_parser("prepare", help="preview a reusable 100-answer review request"))
    command.add_argument("--kind", choices=("prompt", "task", "change", "project"), required=True)
    for name in ("subject", "revision", "evidence-revision"):
        command.add_argument("--" + name, required=True)
    command.add_argument("--stage", choices=STAGES, required=True)
    command.add_argument("--task")
    command.add_argument("--apply", action="store_true")
    command = scope(subparsers.add_parser("score", help="deterministic arithmetic over recorded judgments; no model or tests"))
    command.add_argument("id")
    command.add_argument("--apply", action="store_true")
    command = scope(subparsers.add_parser("compare", help="compare two immutable reports using the same policy"))
    command.add_argument("before")
    command.add_argument("after")
    command = scope(subparsers.add_parser("validate", help="validate one request or report without traversing past reviews"))
    command.add_argument("id")


def dispatch(root, defaults, args):
    action = args.standard_action
    if action == "policy":
        if records.safe(root, "REVIEWS/POLICY.json").exists():
            policy = validate_policy(records.read(root, "REVIEWS/POLICY.json"))
        else:
            policy = validate_policy(records.read(defaults, "config/agent-z-policy.json"))
        return {"policyHash": records.fingerprint(policy), "policy": policy}
    if action == "prepare":
        return prepare(root, args)
    if action == "score":
        return score(root, args.id, args.apply)
    if action == "compare":
        return compare(root, args.before, args.after)
    report = load_request(root, args.id) if args.id.startswith("R-") else load_report(root, args.id)
    return {"valid": True, "id": report["id"], "limit": "Record integrity only; evidence authenticity requires review"}
