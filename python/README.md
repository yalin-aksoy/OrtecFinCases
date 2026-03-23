# Python Task List Application

This project is an in-memory task management application with two interfaces:

- a command-line interface
- a Flask REST API

Both interfaces use the same `TaskList` singleton. When the application is started in `both` mode, the console and the web API share the same in-memory projects and tasks.

## What Changed

The application was completed to cover the deadline feature and refactored to separate core task management logic from input/output handling.

- `TaskList` now contains the shared application state and domain operations
- `TaskController` handles command parsing and console output
- `task_web.py` exposes the REST API
- `task_list_application.py` is the entry point for console, web, or both modes

Deadlines were also added to tasks, together with:

- `deadline <task_id> <dd-mm-yyyy>`
- `today`
- `view-by-deadline`

The REST API was extended with project and task endpoints, including deadline updates and grouped deadline views.

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the Application

Run from the `python/` directory.

### Console Mode

```bash
python task_list_application.py console
```

If no argument is provided, the application also starts in console mode:

```bash
python task_list_application.py
```

### Web Mode

```bash
python task_list_application.py web
```

The API will be available at:

```text
http://localhost:8000
```

### Shared Console + Web Mode

```bash
python task_list_application.py both
```

This starts:

- the Flask API in a background thread
- the console in the main thread

In this mode, both interfaces operate on the same in-memory `TaskList` instance.

## Console Commands

- `show`
- `today`
- `add project <project name>`
- `add task <project name> <task description>`
- `check <task id>`
- `uncheck <task id>`
- `deadline <task id> <dd-mm-yyyy>`
- `view-by-deadline`
- `help`
- `quit`

## REST API

### Projects

- `POST /projects`
- `GET /projects`

Example:

```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{"name":"secrets"}'
```

### Tasks

- `POST /projects/<project_id>/tasks`
- `PUT /projects/<project_id>/tasks/<task_id>?deadline=<dd-mm-yyyy>`

Note: `project_id` currently maps to the project name in the in-memory model.

Example:

```bash
curl -X POST http://localhost:8000/projects/secrets/tasks \
  -H "Content-Type: application/json" \
  -d '{"description":"Eat more donuts."}'
```

```bash
curl -X PUT "http://localhost:8000/projects/secrets/tasks/1?deadline=24-03-2026"
```

### Deadline View

- `GET /projects/view_by_deadline`

## Running Tests

Run all Python tests with:

```bash
pytest test_application.py
```

You can also run the test file directly:

```bash
python test_application.py
```

## Project Structure

- `task.py`: task entity
- `task_list.py`: shared singleton state and core task logic
- `task_controller.py`: console interface
- `task_web.py`: Flask routes
- `task_list_application.py`: application entry point
- `test_application.py`: CLI and API tests
- `task_analytics.py`: analytics-related exercises

## Notes

- Data is stored in memory only
- restarting the process clears all projects and tasks
- shared state only exists when console and web run in the same process, for example with `both` mode
