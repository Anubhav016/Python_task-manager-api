"""
Integration tests hitting the real HTTP routes via FastAPI's TestClient,
confirming the API contract (status codes, response shapes) end to end.
"""


def test_create_task_returns_201_and_payload(client):
    response = client.post("/tasks", json={"title": "Learn FastAPI"})
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Learn FastAPI"
    assert body["status"] == "pending"
    assert "id" in body and "created_at" in body


def test_create_task_rejects_empty_title(client):
    response = client.post("/tasks", json={"title": ""})
    assert response.status_code == 422  # Pydantic validation error


def test_get_nonexistent_task_returns_404(client):
    response = client.get("/tasks/9999")
    assert response.status_code == 404


def test_list_tasks_returns_created_tasks(client):
    client.post("/tasks", json={"title": "Task 1"})
    client.post("/tasks", json={"title": "Task 2"})

    response = client.get("/tasks")
    assert response.status_code == 200
    titles = [t["title"] for t in response.json()]
    assert titles == ["Task 1", "Task 2"]


def test_filter_tasks_by_status(client):
    client.post("/tasks", json={"title": "Stays pending"})
    created = client.post("/tasks", json={"title": "Moves along"}).json()
    client.patch(f"/tasks/{created['id']}", json={"status": "in_progress"})

    response = client.get("/tasks", params={"status": "in_progress"})
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["title"] == "Moves along"


def test_invalid_status_transition_returns_400(client):
    created = client.post("/tasks", json={"title": "Skip ahead"}).json()
    response = client.patch(f"/tasks/{created['id']}", json={"status": "done"})
    assert response.status_code == 400


def test_delete_task_then_404_on_fetch(client):
    created = client.post("/tasks", json={"title": "Temporary"}).json()
    delete_response = client.delete(f"/tasks/{created['id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/tasks/{created['id']}")
    assert get_response.status_code == 404
