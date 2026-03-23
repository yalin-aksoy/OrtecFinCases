import io
import pytest
from task_controller import TaskController
from task_list import TaskList


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
