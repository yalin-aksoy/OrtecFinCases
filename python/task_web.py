from datetime import datetime

from flask import Flask, jsonify, request

from task_list import TaskList

app = Flask(__name__)


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(["Task 1", "Task 2", "Task 3"])


def _serialize_task(task):
    return {
        "id": task.id,
        "description": task.description,
        "done": task.done,
        "deadline": None if task.deadline is None else task.deadline.isoformat(),
    }


def _serialize_projects(task_list: TaskList):
    return {
        "projects": [
            {
                "name": project_name,
                "tasks": [_serialize_task(task) for task in tasks],
            }
            for project_name, tasks in task_list.list_tasks().items()
        ]
    }


def _serialize_deadlines(task_list: TaskList):
    grouped = []
    for deadline, project_map in sorted(
        task_list.get_by_deadline().items(),
        key=lambda item: (item[0] is None, str(item[0])),
    ):
        grouped.append(
            {
                "deadline": None if deadline is None else deadline.isoformat(),
                "projects": [
                    {
                        "name": project_name,
                        "tasks": [_serialize_task(task) for task in tasks],
                    }
                    for project_name, tasks in project_map.items()
                ],
            }
        )
    return {"deadlines": grouped}


@app.route("/projects", methods=["POST"])
def create_project():
    payload = request.get_json(silent=True) or {}
    project_name = payload.get("name", "").strip()

    if not project_name:
        return jsonify({"error": "Project name is required."}), 400

    task_list = TaskList.get_instance()
    if task_list.has_project(project_name):
        return jsonify({"error": f'Project "{project_name}" already exists.'}), 409

    task_list.add_project(project_name)
    return jsonify({"name": project_name, "tasks": []}), 201


@app.route("/projects", methods=["GET"])
def get_projects():
    task_list = TaskList.get_instance()
    return jsonify(_serialize_projects(task_list))


@app.route("/projects/<project_id>/tasks", methods=["POST"])
def create_task(project_id: str):
    payload = request.get_json(silent=True) or {}
    description = payload.get("description", "").strip()
    if not description:
        return jsonify({"error": "Task description is required."}), 400

    task_list = TaskList.get_instance()
    if not task_list.has_project(project_id):
        return jsonify({"error": f'Project "{project_id}" not found.'}), 404

    task_list.add_task(project_id, description)
    task = task_list.get_project_tasks(project_id)[-1]
    return jsonify(_serialize_task(task)), 201


@app.route("/projects/<project_id>/tasks/<int:task_id>", methods=["PUT"])
def update_task_deadline(project_id: str, task_id: int):
    deadline_arg = request.args.get("deadline", "").strip()
    if not deadline_arg:
        return jsonify({"error": "Deadline query parameter is required."}), 400

    try:
        deadline = datetime.strptime(deadline_arg, "%d-%m-%Y").date()
    except ValueError:
        return jsonify({"error": "Deadline format shall be dd-mm-yyyy."}), 400

    task_list = TaskList.get_instance()
    project_tasks = task_list.get_project_tasks(project_id)
    if project_tasks is None:
        return jsonify({"error": f'Project "{project_id}" not found.'}), 404

    task = next((project_task for project_task in project_tasks if project_task.id == task_id), None)
    if task is None:
        return jsonify({"error": f'Task "{task_id}" not found in project "{project_id}".'}), 404

    task_list.add_deadline(task_id, deadline)
    return jsonify(_serialize_task(task))


@app.route("/projects/view_by_deadline", methods=["GET"])
def get_projects_view_by_deadline():
    task_list = TaskList.get_instance()
    return jsonify(_serialize_deadlines(task_list))
