import io
from datetime import date, timedelta

import pytest
from task_controller import TaskController
from task_list import TaskList
from task_web import app


@pytest.fixture
def task_list() -> TaskList:
    TaskList.reset_instance()
    return TaskList.get_instance()


@pytest.fixture
def controller(task_list: TaskList) -> TaskController:
    input_stream = io.StringIO()
    output_stream = io.StringIO()
    return TaskController(task_list, input_stream, output_stream)


@pytest.fixture
def client(task_list: TaskList):
    app.testing = True
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def output_stream(controller: TaskController) -> io.StringIO:
    return controller._output_stream


def clear_output(output_stream: io.StringIO) -> None:
    output_stream.seek(0)
    output_stream.truncate(0)


def get_output(output_stream: io.StringIO) -> str:
    return output_stream.getvalue()


def test_show_empty_task_list(controller: TaskController, output_stream: io.StringIO) -> None:
    
    clear_output(output_stream)
    controller.execute("show")
    
    assert get_output(output_stream) == ""


def test_add_single_project(controller: TaskController, output_stream: io.StringIO) -> None:

    controller.execute("add project secrets")
    clear_output(output_stream)
    
    controller.execute("show")
    output = get_output(output_stream)
    lines = output.strip().split('\n')
    
    expected_lines = [
        "secrets",
    ]
    
    assert lines == expected_lines


def test_add_tasks_to_project(controller: TaskController, output_stream: io.StringIO) -> None:

    controller.execute("add project secrets")
    controller.execute("add task secrets Eat more donuts.")
    controller.execute("add task secrets Destroy all humans.")
    clear_output(output_stream)
    
    controller.execute("show")
    output = get_output(output_stream)
    lines = output.strip().split('\n')
    
    expected_lines = [
        "secrets",
        "    [ ] 1: Eat more donuts.",
        "    [ ] 2: Destroy all humans.",
    ]
    
    assert lines == expected_lines


def test_check_task_marks_as_done(controller: TaskController, output_stream: io.StringIO) -> None:

    controller.execute("add project secrets")
    controller.execute("add task secrets Eat more donuts.")
    controller.execute("check 1")
    clear_output(output_stream)
    
    controller.execute("show")
    output = get_output(output_stream)
    lines = output.strip().split('\n')
    
    expected_lines = [
        "secrets",
        "    [x] 1: Eat more donuts.",
    ]
    
    assert lines == expected_lines


def test_uncheck_task_marks_as_not_done(controller: TaskController, output_stream: io.StringIO) -> None:

    controller.execute("add project secrets")
    controller.execute("add task secrets Eat more donuts.")
    controller.execute("check 1")
    controller.execute("uncheck 1")
    clear_output(output_stream)
    
    controller.execute("show")
    output = get_output(output_stream)
    lines = output.strip().split('\n')
    
    expected_lines = [
        "secrets",
        "    [ ] 1: Eat more donuts.",
    ]
    
    assert lines == expected_lines


def test_multiple_projects_with_tasks(controller: TaskController, output_stream: io.StringIO) -> None:

    # Add first project with tasks
    controller.execute("add project secrets")
    controller.execute("add task secrets Eat more donuts.")
    controller.execute("add task secrets Destroy all humans.")
    
    # Add second project with tasks
    controller.execute("add project training")
    controller.execute("add task training Four Elements of Simple Design")
    controller.execute("add task training SOLID")
    controller.execute("add task training Coupling and Cohesion")
    controller.execute("add task training Primitive Obsession")
    controller.execute("add task training Outside-In TDD")
    controller.execute("add task training Interaction-Driven Design")
    
    clear_output(output_stream)
    controller.execute("show")
    output = get_output(output_stream)
    lines = output.strip().split('\n')
    
    # Verify output order and content
    expected_lines = [
        "secrets",
        "    [ ] 1: Eat more donuts.",
        "    [ ] 2: Destroy all humans.",
        "",
        "training",
        "    [ ] 3: Four Elements of Simple Design",
        "    [ ] 4: SOLID",
        "    [ ] 5: Coupling and Cohesion",
        "    [ ] 6: Primitive Obsession",
        "    [ ] 7: Outside-In TDD",
        "    [ ] 8: Interaction-Driven Design",
    ]
    
    assert lines == expected_lines


def test_check_multiple_tasks_across_projects(controller: TaskController, output_stream: io.StringIO) -> None:

    # Setup projects and tasks
    controller.execute("add project secrets")
    controller.execute("add task secrets Eat more donuts.")
    controller.execute("add task secrets Destroy all humans.")
    
    controller.execute("add project training")
    controller.execute("add task training Four Elements of Simple Design")
    controller.execute("add task training SOLID")
    controller.execute("add task training Coupling and Cohesion")
    controller.execute("add task training Primitive Obsession")
    controller.execute("add task training Outside-In TDD")
    controller.execute("add task training Interaction-Driven Design")
    
    # Check specific tasks
    controller.execute("check 1")
    controller.execute("check 3")
    controller.execute("check 5")
    controller.execute("check 6")
    
    clear_output(output_stream)
    controller.execute("show")
    output = get_output(output_stream)
    lines = output.strip().split('\n')
    
    # Verify output order with checked/unchecked status
    expected_lines = [
        "secrets",
        "    [x] 1: Eat more donuts.",
        "    [ ] 2: Destroy all humans.",
        "",
        "training",
        "    [x] 3: Four Elements of Simple Design",
        "    [ ] 4: SOLID",
        "    [x] 5: Coupling and Cohesion",
        "    [x] 6: Primitive Obsession",
        "    [ ] 7: Outside-In TDD",
        "    [ ] 8: Interaction-Driven Design",
    ]
    
    assert lines == expected_lines


def test_add_task_to_nonexistent_project(controller: TaskController, output_stream: io.StringIO) -> None:

    clear_output(output_stream)
    controller.execute("add task nonexistent Some task")
    output = get_output(output_stream)
    lines = output.strip().split('\n')
    
    expected_lines = [
        'Could not find a project with the name "nonexistent".',
    ]
    
    assert lines == expected_lines


def test_check_nonexistent_task(controller: TaskController, output_stream: io.StringIO) -> None:

    controller.execute("add project secrets")
    controller.execute("add task secrets Eat more donuts.")
    clear_output(output_stream)
    
    controller.execute("check 999")
    output = get_output(output_stream)
    lines = output.strip().split('\n')
    
    expected_lines = [
        "Could not find a task with an ID of 999.",
    ]
    
    assert lines == expected_lines


def test_task_id_increments_across_projects(controller: TaskController, output_stream: io.StringIO) -> None:

    controller.execute("add project project1")
    controller.execute("add task project1 Task 1")
    controller.execute("add project project2")
    controller.execute("add task project2 Task 2")
    controller.execute("add task project1 Task 3")
    clear_output(output_stream)
    
    controller.execute("show")
    output = get_output(output_stream)
    lines = output.strip().split('\n')
    
    # Verify task IDs increment across projects in order
    expected_lines = [
        "project1",
        "    [ ] 1: Task 1",
        "    [ ] 3: Task 3",
        "",
        "project2",
        "    [ ] 2: Task 2",
    ]
    
    assert lines == expected_lines


def test_add_deadline_shows_under_task(controller: TaskController, output_stream: io.StringIO) -> None:
    controller.execute("add project secrets")
    controller.execute("add task secrets Eat more donuts.")
    controller.execute("deadline 1 24-03-2026")
    clear_output(output_stream)

    controller.execute("show")
    output = get_output(output_stream)
    lines = output.strip().split("\n")

    expected_lines = [
        "secrets",
        "    [ ] 1: Eat more donuts.",
        "           2026-03-24",
    ]

    assert lines == expected_lines


def test_add_deadline_for_missing_task_returns_error(controller: TaskController, output_stream: io.StringIO) -> None:
    controller.execute("add project secrets")
    clear_output(output_stream)

    controller.execute("deadline 99 24-03-2026")

    assert get_output(output_stream).strip() == "Could not find a task with an ID of 99."


def test_add_deadline_with_invalid_id_returns_error(controller: TaskController, output_stream: io.StringIO) -> None:
    clear_output(output_stream)

    controller.execute("deadline nope 24-03-2026")

    assert get_output(output_stream).strip() == "ID shall be given as int"


def test_add_deadline_with_invalid_date_returns_error(controller: TaskController, output_stream: io.StringIO) -> None:
    controller.execute("add project secrets")
    controller.execute("add task secrets Eat more donuts.")
    clear_output(output_stream)

    controller.execute("deadline 1 2026-03-24")

    assert get_output(output_stream).strip() == "Date format shall be dd-mm-yyyy"


def test_today_shows_only_tasks_due_today(controller: TaskController, output_stream: io.StringIO) -> None:
    today_string = date.today().strftime("%d-%m-%Y")
    tomorrow_string = (date.today() + timedelta(days=1)).strftime("%d-%m-%Y")

    controller.execute("add project secrets")
    controller.execute("add task secrets Eat more donuts.")
    controller.execute("add task secrets Destroy all humans.")
    controller.execute("deadline 1 " + today_string)
    controller.execute("deadline 2 " + tomorrow_string)

    controller.execute("add project training")
    controller.execute("add task training SOLID")
    controller.execute("deadline 3 " + today_string)
    clear_output(output_stream)

    controller.execute("today")
    output = get_output(output_stream)
    lines = output.strip().split("\n")

    expected_lines = [
        "secrets",
        "    [ ] 1: Eat more donuts.",
        f"           {date.today()}",
        "",
        "training",
        "    [ ] 3: SOLID",
        f"           {date.today()}",
    ]

    assert lines == expected_lines


def test_today_returns_empty_when_nothing_is_due_today(controller: TaskController, output_stream: io.StringIO) -> None:
    tomorrow_string = (date.today() + timedelta(days=1)).strftime("%d-%m-%Y")

    controller.execute("add project secrets")
    controller.execute("add task secrets Eat more donuts.")
    controller.execute("deadline 1 " + tomorrow_string)
    clear_output(output_stream)

    controller.execute("today")

    assert get_output(output_stream) == ""


def test_view_by_deadline_groups_none_and_dates(controller: TaskController, output_stream: io.StringIO) -> None:
    controller.execute("add project secrets")
    controller.execute("add task secrets Eat more donuts.")
    controller.execute("add task secrets Destroy all humans.")
    controller.execute("deadline 2 24-03-2026")

    controller.execute("add project training")
    controller.execute("add task training SOLID")
    controller.execute("deadline 3 23-03-2026")
    clear_output(output_stream)

    controller.execute("view-by-deadline")
    output = get_output(output_stream)
    lines = output.strip().split("\n")

    expected_lines = [
        "2026-03-23:",
        "   training:",
        "        3:SOLID",
        "2026-03-24:",
        "   secrets:",
        "        2:Destroy all humans.",
        "No Deadline:",
        "   secrets:",
        "        1:Eat more donuts.",
    ]

    assert lines == expected_lines


def test_create_project_route(client) -> None:
    response = client.post("/projects", json={"name": "secrets"})

    assert response.status_code == 201
    assert response.get_json() == {"name": "secrets", "tasks": []}


def test_get_projects_route_returns_projects_and_tasks(client, task_list: TaskList) -> None:
    task_list.add_project("secrets")
    task_list.add_task("secrets", "Eat more donuts.")
    task_list.add_project("training")
    task_list.add_task("training", "SOLID")
    task_list.add_deadline(2, date(2026, 3, 23))

    response = client.get("/projects")

    assert response.status_code == 200
    assert response.get_json() == {
        "projects": [
            {
                "name": "secrets",
                "tasks": [
                    {
                        "id": 1,
                        "description": "Eat more donuts.",
                        "done": False,
                        "deadline": None,
                    }
                ],
            },
            {
                "name": "training",
                "tasks": [
                    {
                        "id": 2,
                        "description": "SOLID",
                        "done": False,
                        "deadline": "2026-03-23",
                    }
                ],
            },
        ]
    }


def test_create_project_route_rejects_missing_name(client) -> None:
    response = client.post("/projects", json={})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Project name is required."}


def test_create_project_route_rejects_duplicate_project(client, task_list: TaskList) -> None:
    task_list.add_project("secrets")

    response = client.post("/projects", json={"name": "secrets"})

    assert response.status_code == 409
    assert response.get_json() == {"error": 'Project "secrets" already exists.'}


def test_create_task_route(client, task_list: TaskList) -> None:
    task_list.add_project("secrets")

    response = client.post("/projects/secrets/tasks", json={"description": "Eat more donuts."})

    assert response.status_code == 201
    assert response.get_json() == {
        "id": 1,
        "description": "Eat more donuts.",
        "done": False,
        "deadline": None,
    }


def test_create_task_route_rejects_missing_project(client) -> None:
    response = client.post("/projects/secrets/tasks", json={"description": "Eat more donuts."})

    assert response.status_code == 404
    assert response.get_json() == {"error": 'Project "secrets" not found.'}


def test_update_task_deadline_route(client, task_list: TaskList) -> None:
    task_list.add_project("secrets")
    task_list.add_task("secrets", "Eat more donuts.")

    response = client.put("/projects/secrets/tasks/1?deadline=24-03-2026")

    assert response.status_code == 200
    assert response.get_json() == {
        "id": 1,
        "description": "Eat more donuts.",
        "done": False,
        "deadline": "2026-03-24",
    }


def test_update_task_deadline_route_rejects_missing_deadline(client, task_list: TaskList) -> None:
    task_list.add_project("secrets")
    task_list.add_task("secrets", "Eat more donuts.")

    response = client.put("/projects/secrets/tasks/1")

    assert response.status_code == 400
    assert response.get_json() == {"error": "Deadline query parameter is required."}


def test_update_task_deadline_route_rejects_invalid_deadline(client, task_list: TaskList) -> None:
    task_list.add_project("secrets")
    task_list.add_task("secrets", "Eat more donuts.")

    response = client.put("/projects/secrets/tasks/1?deadline=2026-03-24")

    assert response.status_code == 400
    assert response.get_json() == {"error": "Deadline format shall be dd-mm-yyyy."}


def test_get_projects_view_by_deadline_route(client, task_list: TaskList) -> None:
    task_list.add_project("secrets")
    task_list.add_task("secrets", "Eat more donuts.")
    task_list.add_task("secrets", "Destroy all humans.")
    task_list.add_project("training")
    task_list.add_task("training", "SOLID")
    task_list.add_deadline(2, date(2026, 3, 24))
    task_list.add_deadline(3, date(2026, 3, 23))

    response = client.get("/projects/view_by_deadline")

    assert response.status_code == 200
    assert response.get_json() == {
        "deadlines": [
            {
                "deadline": "2026-03-23",
                "projects": [
                    {
                        "name": "training",
                        "tasks": [
                            {
                                "id": 3,
                                "description": "SOLID",
                                "done": False,
                                "deadline": "2026-03-23",
                            }
                        ],
                    }
                ],
            },
            {
                "deadline": "2026-03-24",
                "projects": [
                    {
                        "name": "secrets",
                        "tasks": [
                            {
                                "id": 2,
                                "description": "Destroy all humans.",
                                "done": False,
                                "deadline": "2026-03-24",
                            }
                        ],
                    }
                ],
            },
            {
                "deadline": None,
                "projects": [
                    {
                        "name": "secrets",
                        "tasks": [
                            {
                                "id": 1,
                                "description": "Eat more donuts.",
                                "done": False,
                                "deadline": None,
                            }
                        ],
                    }
                ],
            },
        ]
    }


def main() -> int:
    return pytest.main([__file__])


if __name__ == "__main__":
    raise SystemExit(main())
