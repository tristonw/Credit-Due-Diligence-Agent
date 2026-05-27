def test_full_loop(client):
    # health reports mock mode (no API key in tests)
    h = client.get("/api/health").json()
    assert h["llm"] == "mock"

    # 1) generate a digital employee from a natural-language brief
    emp = client.post(
        "/api/employees",
        json={"description": "负责信贷尽职调查，分析企业财务与风险", "name": "信贷调查员"},
    ).json()
    eid = emp["id"]
    assert emp["level"] == 1 and emp["experience"] == 0
    assert emp["outline"] is not None
    assert len(emp["skills"]) >= 1
    assert emp["avatar"]["style"] and emp["avatar"]["seed"]  # real avatar config

    # 3a) baseline evaluation
    base = client.post(f"/api/employees/{eid}/evaluate", json={"phase": "baseline"}).json()
    assert base["phase"] == "baseline"

    # 2) upload corpus + train (4 triggers hard deposits)
    client.post(f"/api/employees/{eid}/corpus", json={"title": "信贷手册", "text": "段落一。\n\n段落二，关键质量要求。"})
    train = client.post(f"/api/employees/{eid}/train").json()
    assert train["deposits"]["skills"] >= 1

    # 4) deposits are versioned and tagged
    deposits = client.get(f"/api/employees/{eid}/deposits").json()
    assert any(s["source"] == "deposited" for s in deposits["skills"])

    # 3b) post-training evaluation should improve
    client.post(f"/api/employees/{eid}/evaluate", json={"phase": "post_training"})
    cmp = client.get(f"/api/employees/{eid}/evaluations/compare").json()
    assert cmp["improved"] is True
    assert cmp["delta"] > 0

    # 5) run tasks + human labels move experience
    task = client.post(f"/api/employees/{eid}/tasks", json={"prompt": "评估某企业信贷风险"}).json()
    assert 0 < task["quality"] <= 1
    assert task["exp_gained"] >= 10
    assert task["experience"] == task["exp_gained"]  # first experience event
    assert "applied_sop" in task and "dq_findings" in task
    good = client.post(f"/api/tasks/{task['task_id']}/label", json={"rating": "good"}).json()
    assert good["exp_delta"] == 40
    bad = client.post(f"/api/tasks/{task['task_id']}/label", json={"rating": "bad"}).json()
    assert bad["exp_delta"] == -25

    # leveling state is exposed
    lv = client.get(f"/api/employees/{eid}/leveling").json()
    assert 0.0 <= lv["progress"] <= 1.0


def test_expert_gated_promotion(client):
    # Big experience grant should push the employee toward an expert-gated level.
    emp = client.post("/api/employees", json={"description": "测试升级", "name": "升级测试"}).json()
    eid = emp["id"]

    # Hammer tasks + good labels until a pending promotion request appears.
    promo_id = None
    for _ in range(40):
        t = client.post(f"/api/employees/{eid}/tasks", json={"prompt": "做事"}).json()
        if t.get("promotion_request_id"):
            promo_id = t["promotion_request_id"]
            break
        lab = client.post(f"/api/tasks/{t['task_id']}/label", json={"rating": "good"}).json()
        if lab.get("promotion_request_id"):
            promo_id = lab["promotion_request_id"]
            break

    assert promo_id is not None, "expected an expert-gated promotion request"

    pending = client.get("/api/promotions", params={"status": "pending"}).json()
    assert any(p["id"] == promo_id for p in pending)

    before = client.get(f"/api/employees/{eid}").json()["level"]
    decided = client.post(
        f"/api/promotions/{promo_id}/decide", json={"approve": True, "expert": "张专家"}
    ).json()
    assert decided["status"] == "approved"

    after = client.get(f"/api/employees/{eid}").json()["level"]
    assert after > before
