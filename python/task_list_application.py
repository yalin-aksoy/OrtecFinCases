import sys
import threading

from task_controller import TaskController
from task_list import TaskList
from task_web import app


def run_web() -> None:
    app.run(host="localhost", port=8000, debug=False, use_reloader=False)


def run_console() -> None:
    controller = TaskController(TaskList.get_instance(), sys.stdin, sys.stdout)
    controller.run()


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "console"

    if mode == "console":
        print("Starting console application")
        run_console()
    elif mode == "web":
        print("Starting web application")
        print("http://localhost:8000/projects")
        run_web()
    elif mode == "both":
        print("Starting console and web application")
        print("http://localhost:8000/projects")
        web_thread = threading.Thread(target=run_web, daemon=True)
        web_thread.start()
        run_console()
    else:
        print("Usage: python task_list_application.py [console|web|both]")


if __name__ == "__main__":
    main()
