"""
Run the Stage 3 final Java test set through Token Trail and report scores.

Steps:
1. Sign up / log in
2. Create a course + assignment (java)
3. Import TestSetJava.zip
4. Queue analysis run
5. Poll until complete
6. Fetch similarity results
7. Report scores organised by category
"""

import json
import sys
import time
import requests
from pathlib import Path

BASE = "http://localhost:8000/api"
FINAL_DIR = Path(__file__).resolve().parent / "test_repos" / "final"
ZIP_FILE = FINAL_DIR / "TestSetJava.zip"

EMAIL = f"final_eval_{int(time.time())}@test.com"
PASSWORD = "TestPass123!"

# Expected categories (from MANIFEST)
PAIR_A = {"S01", "S02"}           # LinkedList clone pair
TRIPLE_B = {"S03", "S04", "S05"} # MatrixOps triple
HARD_C = {"S11", "S12"}          # HashTable hard pair (open-addr vs chaining)
CONTROLS = {"S06", "S07", "S08", "S09", "S10", "S13", "S14", "S15"}


def api(method, path, token=None, **kwargs):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = requests.request(method, f"{BASE}{path}", headers=headers, **kwargs)
    if resp.status_code >= 400:
        print(f"  ERROR {resp.status_code}: {resp.text[:300]}")
    return resp


def signup_and_login():
    r = api("POST", "/auth/signup", json={
        "email": EMAIL, "password": PASSWORD, "name": "Final Eval"
    })
    if r.status_code == 409:
        r = api("POST", "/auth/login", json={
            "email": EMAIL, "password": PASSWORD
        })
    data = r.json()
    return data.get("accessToken") or data.get("token")


def create_course_and_assignment(token):
    r = api("POST", "/instructor/courses", token=token, json={
        "name": "Final Java Eval",
        "term": "2026W",
    })
    course = r.json()
    course_id = course["id"]

    r = api("POST", "/instructor/assignments", token=token, json={
        "courseId": course_id,
        "title": "Stage 3 Final Java",
        "language": "java",
    })
    assignment = r.json()
    return course_id, assignment["id"]


def import_zip(token, assignment_id):
    with open(ZIP_FILE, "rb") as f:
        r = api(
            "POST",
            f"/instructor/assignments/{assignment_id}/submissions/import",
            token=token,
            files={"zipFile": (ZIP_FILE.name, f, "application/zip")},
        )
    return r.json()


def queue_analysis(token, assignment_id):
    r = api("POST", f"/instructor/assignments/{assignment_id}/analysis-runs",
            token=token)
    return r.json()["runId"]


def poll_run(token, run_id, timeout=300):
    start = time.time()
    while time.time() - start < timeout:
        r = api("GET", f"/instructor/analysis-runs/{run_id}", token=token)
        if r.status_code == 404:
            # Might be a timing issue, retry
            time.sleep(3)
            continue
        data = r.json()
        status = data.get("status", "unknown")
        print(f"    status={status} ({int(time.time()-start)}s)")
        if status in ("completed", "failed"):
            return data
        time.sleep(3)
    return {"status": "timeout"}


def get_results(token, run_id):
    r = api("GET", f"/instructor/analysis-runs/{run_id}/similarity-results",
            token=token)
    return r.json()


def categorize_pair(left, right):
    """Return category label for a pair of student IDs."""
    pair = {left, right}
    if pair <= PAIR_A:
        return "Pair A (clone)"
    if pair <= TRIPLE_B:
        return "Triple B (clone)"
    if pair <= HARD_C:
        return "Hard C"
    if pair <= CONTROLS:
        return "Control-Control"
    # Mixed: one is a control, one is a clone source
    clone_ids = PAIR_A | TRIPLE_B | HARD_C
    if pair & clone_ids and pair & CONTROLS:
        return "Control-Clone"
    return "Other"


def main():
    print("=" * 60)
    print("  Stage 3 Final Java Evaluation")
    print("=" * 60)
    print(f"Email: {EMAIL}")

    # Health
    try:
        r = requests.get(f"{BASE}/health", timeout=5)
        print(f"Health: {r.json()}")
    except Exception as e:
        print(f"Cannot reach API: {e}")
        sys.exit(1)

    # Auth
    token = signup_and_login()
    if not token:
        print("FATAL: Could not get auth token")
        sys.exit(1)
    print(f"Token: {token[:20]}...")

    # Course + assignment
    course_id, assignment_id = create_course_and_assignment(token)
    print(f"Course: {course_id}")
    print(f"Assignment: {assignment_id}")

    # Import
    print(f"Importing {ZIP_FILE.name}...")
    imp = import_zip(token, assignment_id)
    print(f"  imported={imp.get('imported')}, skipped={imp.get('skipped')}")
    if imp.get("skippedDetails"):
        for d in imp["skippedDetails"][:10]:
            print(f"    SKIP: {d}")

    # Queue
    print("Queuing analysis...")
    run_id = queue_analysis(token, assignment_id)
    print(f"  Run ID: {run_id}")

    # Poll
    print("Waiting for completion (timeout 5 min)...")
    result = poll_run(token, run_id, timeout=300)
    final_status = result.get("status")
    print(f"Final status: {final_status}")
    if result.get("errorMessage"):
        print(f"  Error: {result['errorMessage']}")

    if final_status != "completed":
        print("FAILED — cannot fetch results")
        sys.exit(1)

    # Fetch results
    results_data = get_results(token, run_id)
    results = results_data.get("results", [])
    print(f"Total pairs returned: {len(results)}")

    # Organise by category
    categories = {}
    for r in results:
        left = r.get("leftStudentIdentifier", "?")
        right = r.get("rightStudentIdentifier", "?")
        score = r.get("similarityScore", 0)
        confidence = r.get("confidence", 0)
        method = r.get("analysisMethod", "?")

        cat = categorize_pair(left, right)
        categories.setdefault(cat, [])
        categories[cat].append({
            "left": left, "right": right,
            "score": score, "confidence": confidence,
            "method": method,
        })

    # Report
    print("\n" + "=" * 70)
    print("  RESULTS BY CATEGORY")
    print("=" * 70)

    for cat_name in ["Pair A (clone)", "Triple B (clone)", "Hard C",
                     "Control-Clone", "Control-Control"]:
        pairs = categories.get(cat_name, [])
        if not pairs:
            print(f"\n  {cat_name}: no pairs")
            continue
        print(f"\n  {cat_name} ({len(pairs)} pairs):")
        print(f"  {'Left':<8} {'Right':<8} {'Score':>7}  {'Conf':>6}  Method")
        print(f"  {'-'*50}")
        pairs.sort(key=lambda p: p["score"], reverse=True)
        for p in pairs:
            pct = round(p["score"] * 100)
            cpct = round(p["confidence"] * 100)
            print(f"  {p['left']:<8} {p['right']:<8} {pct:>6}%  {cpct:>5}%  {p['method']}")
        scores = [p["score"] for p in pairs]
        avg = sum(scores) / len(scores)
        print(f"  avg={round(avg*100)}%  max={round(max(scores)*100)}%  min={round(min(scores)*100)}%")

    # Summary verdict
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)

    pair_a_scores = [p["score"] for p in categories.get("Pair A (clone)", [])]
    triple_b_scores = [p["score"] for p in categories.get("Triple B (clone)", [])]
    hard_c_scores = [p["score"] for p in categories.get("Hard C", [])]
    control_scores = [p["score"] for p in categories.get("Control-Control", [])]
    cross_scores = [p["score"] for p in categories.get("Control-Clone", [])]

    def stat(label, scores):
        if not scores:
            print(f"  {label}: NO DATA")
            return
        avg = round(sum(scores)/len(scores)*100)
        mx = round(max(scores)*100)
        mn = round(min(scores)*100)
        print(f"  {label}: avg={avg}%  max={mx}%  min={mn}%  (n={len(scores)})")

    stat("Pair A (expect HIGH)", pair_a_scores)
    stat("Triple B (expect HIGH)", triple_b_scores)
    stat("Hard C (expect MODERATE)", hard_c_scores)
    stat("Control-Control (expect LOW)", control_scores)
    stat("Control-Clone (expect LOW)", cross_scores)

    # Pass/fail criteria
    ok = True
    if pair_a_scores and max(pair_a_scores) < 0.80:
        print("  FAIL: Pair A max score < 80%")
        ok = False
    if triple_b_scores and max(triple_b_scores) < 0.80:
        print("  FAIL: Triple B max score < 80%")
        ok = False
    if control_scores and max(control_scores) > 0.50:
        print("  WARN: Control-Control max score > 50%")
    if cross_scores and max(cross_scores) > 0.50:
        print("  WARN: Control-Clone max score > 50%")

    print(f"\n  VERDICT: {'PASS — Java test set ready' if ok else 'NEEDS REVIEW'}")


if __name__ == "__main__":
    main()
