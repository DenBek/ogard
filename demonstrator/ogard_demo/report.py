"""A standalone, offline walkthrough generated from actual processing outputs."""

from html import escape
import json


def render_report(processed, evaluation, comparison=None):
    e = escape
    cards = []
    labels = {r["case_id"]: r for r in evaluation["cases"]}
    names = {"accepted_automatic": "Accepted automatically", "accepted_review": "Accepted by scripted review",
             "review_required": "Review required", "unresolved": "Unresolved", "rejected": "Rejected"}
    for case in processed["cases"]:
        result = labels[case["case_id"]]
        rows = []
        for d in case["decisions"]:
            codes = ", ".join(c["code"].replace("_", " ").lower() for c in d["contradictions"]) or "No conflict surfaced"
            rows.append(f'<tr><td>{e(d["subject_record_id"])}</td><td>{e(names[d["disposition"]])}</td><td>{e(d["accepted_equipment_id"] or "No accepted association")}</td><td>{e(codes)}</td></tr>')
        wrong = any(not t["agrees_with_hidden_truth"] for t in result["accepted_mapping_truth_checks"])
        flag = '<p class="warning"><strong>Observed limitation:</strong> an incorrect equipment association was accepted. The conflicting physical truth is absent from the processing inputs.</p>' if wrong else ""
        history = [{"when": a["processed_at"], "trigger": a["trigger_record_id"],
                    "record": a["subject_record_id"], "outcome": names[a["decision"]["disposition"]],
                    "equipment": a["decision"]["accepted_equipment_id"]}
                   for a in case["audit"] if a["event"] == "decision_updated"]
        cards.append(f'''<section class="case"><p class="eyebrow">{e(case["case_id"])}</p><h2>{e(case["title"])}</h2>
<p>{e(case["description"])}</p><div class="tablewrap"><table><thead><tr><th>Record</th><th>Actual outcome</th><th>Equipment association</th><th>Conflicting evidence</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>
<p class="finding">{e(result["interpretation"])}</p>{flag}
<details><summary>Inspect the decision timeline</summary><pre>{e(json.dumps(history, indent=2))}</pre></details>
<details><summary>Inspect the synthetic source records</summary><pre>{e(json.dumps(case["source_records"], indent=2))}</pre></details></section>''')
    case_count = len(processed["cases"])
    decision_count = sum(len(c["decisions"]) for c in processed["cases"])
    document = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OGARD Reference Implementation Results</title><style>
:root{color-scheme:light;font-family:Arial,sans-serif;color:#203042;background:#f2f5f8}*{box-sizing:border-box}body{margin:0}main{max-width:1080px;margin:0 auto;padding:40px 24px 64px}h1{font-size:36px;line-height:1.15;margin:10px 0 18px}h2{font-size:23px;line-height:1.3;margin:6px 0 16px}p,li{font-size:16px;line-height:1.65}.eyebrow{font-size:12px;font-weight:bold;letter-spacing:.12em;color:#376d7e;text-transform:uppercase}.intro,.case{background:white;border:1px solid #d9e2e9;border-radius:12px;padding:28px;margin:22px 0}.summary{background:#eaf2f5;border-left:4px solid #376d7e;padding:16px 20px}.warning{background:#fff1d9;border-left:4px solid #ac6500;padding:14px 18px}.finding{font-weight:bold}.tablewrap{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px;line-height:1.5}th{text-align:left;background:#eaf0f5}td,th{padding:12px;border-bottom:1px solid #dce4eb;vertical-align:top;overflow-wrap:anywhere}details{margin-top:12px;border-top:1px solid #e3e8ed;padding-top:12px}summary{cursor:pointer;color:#285e71;font-weight:bold}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f5f7f9;padding:16px;font-size:12px;line-height:1.5}footer{font-size:13px;line-height:1.6;color:#536373}a{color:#285e71}@media(max-width:640px){main{padding:18px 12px}.case,.intro{padding:18px}h1{font-size:28px}}@media print{body{background:white}main{padding:0}.case{break-inside:avoid}details{display:none}}
</style></head><body><main><p class="eyebrow">OGARD | Executable reference implementation | 0.2.0</p>
<h1>Which transformer does the record concern?</h1>
<section class="intro"><p>A utility replaces a transformer while retaining its location number. Maintenance records and telemetry references may describe different equipment or different moments in its history. This demonstrator processes those records and makes the resulting associations, unresolved questions and review decisions inspectable.</p>
<p class="summary"><strong>What was executed:</strong> CASE_COUNT selected synthetic cases, producing DECISION_COUNT equipment-association decisions. The walkthrough below is generated from the resulting files.</p>
<p><strong>What the results show:</strong> the implementation handles the stated historical-mapping and review cases, while preserving conflicting evidence. It also accepts a wrong association in a constructed case where sources repeat the same upstream error.</p>
<p><strong>How to read this:</strong> “accepted by scripted review” means a predeclared synthetic review event was replayed. This report records automated execution and scripted synthetic review. It does not record an independent external review. These selected cases do not establish utility adoption, operational performance or national impact.</p></section>
''' + "".join(cards) + f'''
<section class="intro"><h2>Results and interpretation</h2><p>The run produced {evaluation["automatic_accepts"]} automatic acceptances; {evaluation["incorrect_automatic_accepts"]} disagreed with the separately stored synthetic physical truth. There was {evaluation["scripted_review_accepts"]} acceptance through scripted review. Counts describe these selected examples and are not an accuracy estimate for utility data.</p><p>The next useful review is whether the records, decision rules and review responsibilities represent a meaningful electricity-network workflow, and whether another engineer can reproduce the outputs.</p><p><strong>Current boundary:</strong> this reference implementation implements explicit identity, installation intervals and review records. It does not implement the full published benchmark, similarity scoring, derived asset statuses or operational control.</p></section>
<footer>Underlying methodology: OGARD, Deniz Bektas. Development provenance is recorded in the repository. This execution report does not represent a third-party evaluation. Original methodology and structured example: <a href="https://github.com/DenBek/ogard">OGARD repository</a>. Rule version: {e(processed["rule_version"])}. Input SHA-256: {e(processed["input_hash"])}.</footer></main></body></html>'''
    if comparison is not None:
        metrics = [("Accepted links", "accepted"), ("Correct accepted links", "accepted_correct"),
                   ("Incorrect accepted links", "accepted_incorrect"), ("Review required", "review_required"),
                   ("Unresolved", "unresolved")]
        methods = [comparison[k]["counts"] for k in ("baseline_automatic", "ogard_automatic", "ogard_with_scripted_review")]
        metric_rows = "".join("<tr><th scope=\"row\">" + label + "</th>" + "".join("<td>" + str(m[key]) + "</td>" for m in methods) + "</tr>" for label, key in metrics)
        panel = '<section class="intro"><h2>Comparison on six decisions</h2><div class="tablewrap"><table><thead><tr><th>Measure</th><th>Baseline automatic</th><th>OGARD automatic</th><th>After scripted review</th></tr></thead><tbody>' + metric_rows + '</tbody></table></div><p>The baseline uses an explicit equipment identifier, or a unique current installation at receipt time when that identifier is missing. Both automatic runs exclude all review events and use identical inputs. The final column is a separate scripted-review demonstration.</p><p>Five decisions have known synthetic physical truth. The competing-installation case has no single truth label. Unaccepted decisions do not count as correct equipment matches. These selected cases do not estimate accuracy on utility data.</p><p>OGARD avoids the baseline’s wrong automatic telemetry association while referring more records for review. Both methods accept the shared-source identity error. The baseline correctly accepts the identifier-free work order in this example; OGARD requires review, showing the workload trade-off.</p></section>'
        document = document.replace("<section class=\"case\">", panel + "<section class=\"case\">", 1)
    document = document.replace("footer{font-size", "footer{overflow-wrap:anywhere;font-size")
    return document.replace("CASE_COUNT", str(case_count)).replace("DECISION_COUNT", str(decision_count))
