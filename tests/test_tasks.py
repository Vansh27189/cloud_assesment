"""Tests for distributed task queue repository."""


def test_create_and_list_tasks(client):
    """Test 6: Verify task creation, storage, and retrieval."""
    task_payload = {
        "title": "Deploy EC2 cluster",
        "description": "Launch 2 t2.micro instances in us-east-1",
        "priority": "high"
    }
    create_res = client.post("/api/tasks", json=task_payload)
    assert create_res.status_code == 201
    created_task = create_res.json()
    assert created_task["title"] == "Deploy EC2 cluster"
    assert created_task["priority"] == "high"
    assert "id" in created_task
    assert "processed_by" in created_task

    # Verify listing tasks
    list_res = client.get("/api/tasks")
    assert list_res.status_code == 200
    tasks = list_res.json()
    assert len(tasks) >= 1
    assert tasks[0]["id"] == created_task["id"]


def test_delete_task_lifecycle(client):
    """Test 7: Verify task deletion and 404 behavior for invalid ID."""
    # Create a task to delete
    create_res = client.post("/api/tasks", json={"title": "Temporary Task", "priority": "low"})
    task_id = create_res.json()["id"]

    # Delete task
    del_res = client.delete(f"/api/tasks/{task_id}")
    assert del_res.status_code == 200

    # Second delete should return 404 Not Found
    del_res_again = client.delete(f"/api/tasks/{task_id}")
    assert del_res_again.status_code == 404
