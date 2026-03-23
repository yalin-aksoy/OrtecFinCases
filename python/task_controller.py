import sys
from datetime import datetime
from typing import TextIO

from task_list import TaskList


class TaskController:
    QUIT = "quit"

    def __init__(self, task_list: TaskList, input_stream: TextIO, output_stream: TextIO):
        self._task_list = task_list
        self._input_stream = input_stream
        self._output_stream = output_stream

    @staticmethod
    def start_console() -> None:
        controller = TaskController(TaskList.get_instance(), sys.stdin, sys.stdout)
        controller.run()

    def run(self) -> None:
        self._output_stream.write("Welcome to TaskList! Type 'help' for available commands.\n")
        self._output_stream.flush()

        while True:
            self._output_stream.write("> ")
            self._output_stream.flush()
            command = self._input_stream.readline().strip()

            if command == self.QUIT:
                break

            self.execute(command)

    def execute(self, command_line: str) -> None:
        parts = command_line.split(" ", 1)
        command = parts[0]

        if command == "show":
            self._show()
        elif command == "today":
            self._today()
        elif command == "add":
            self._add(parts[1] if len(parts) > 1 else "")
        elif command == "check":
            self._set_done(parts[1] if len(parts) > 1 else "", True)
        elif command == "uncheck":
            self._set_done(parts[1] if len(parts) > 1 else "", False)
        elif command == "deadline":
            self._add_deadline(parts[1] if len(parts) > 1 else "")
        elif command == "view-by-deadline":
            self._view_by_deadline()
        elif command == "help":
            self._help()
        else:
            self._error(command)

    def _show(self) -> None:
        for project_name, tasks in self._task_list.list_tasks().items():
            self._output_stream.write(f"{project_name}\n")
            for task in tasks:
                status = "x" if task.done else " "
                self._output_stream.write(f"    [{status}] {task.id}: {task.description}\n")
                if task.deadline is not None:
                    self._output_stream.write(f"           {task.deadline}\n")
            self._output_stream.write("\n")
        self._output_stream.flush()

    def _today(self) -> None:
        for project_name, tasks in self._task_list.get_today_tasks().items():
            self._output_stream.write(f"{project_name}\n")
            for task in tasks:
                status = "x" if task.done else " "
                self._output_stream.write(f"    [{status}] {task.id}: {task.description}\n")
                self._output_stream.write(f"           {task.deadline}\n")
            self._output_stream.write("\n")
        self._output_stream.flush()

    def _add(self, command_line: str) -> None:
        parts = command_line.split(" ", 1)
        subcommand = parts[0]

        if subcommand == "project":
            self._task_list.add_project(parts[1] if len(parts) > 1 else "")
        elif subcommand == "task":
            task_parts = parts[1].split(" ", 1) if len(parts) > 1 else []
            if len(task_parts) >= 2 and not self._task_list.add_task(task_parts[0], task_parts[1]):
                self._output_stream.write(f'Could not find a project with the name "{task_parts[0]}".\n')
                self._output_stream.flush()

    def _set_done(self, id_string: str, done: bool) -> None:
        try:
            task_id = int(id_string)
        except ValueError:
            return

        if not self._task_list.set_done(task_id, done):
            self._output_stream.write(f"Could not find a task with an ID of {task_id}.\n")
            self._output_stream.flush()

    def _add_deadline(self, command_line: str) -> None:
        parts = command_line.split(" ", 1)
        try:
            task_id = int(parts[0])
        except (IndexError, ValueError):
            self._output_stream.write("ID shall be given as int\n")
            self._output_stream.flush()
            return

        try:
            deadline = datetime.strptime(parts[1], "%d-%m-%Y").date()
        except (IndexError, ValueError):
            self._output_stream.write("Date format shall be dd-mm-yyyy\n")
            self._output_stream.flush()
            return

        if not self._task_list.add_deadline(task_id, deadline):
            self._output_stream.write(f"Could not find a task with an ID of {task_id}.\n")
            self._output_stream.flush()

    def _view_by_deadline(self) -> None:
        deadlines_dict = self._task_list.get_by_deadline()
        for deadline, project_map in sorted(
            deadlines_dict.items(),
            key=lambda item: (item[0] is None, str(item[0])),
        ):
            if deadline is None:
                self._output_stream.write("No Deadline:\n")
            else:
                self._output_stream.write(f"{deadline}:\n")
            for project, tasks in project_map.items():
                self._output_stream.write(f"   {project}:\n")
                for task in tasks:
                    self._output_stream.write(f"        {task.id}:{task.description}\n")
        self._output_stream.flush()

    def _help(self) -> None:
        self._output_stream.write("Commands:\n")
        self._output_stream.write("  show\n")
        self._output_stream.write("  today\n")
        self._output_stream.write("  add project <project name>\n")
        self._output_stream.write("  add task <project name> <task description>\n")
        self._output_stream.write("  check <task ID>\n")
        self._output_stream.write("  uncheck <task ID>\n")
        self._output_stream.write("  deadline <task ID> <datetime dd-mm-yyyy>\n")
        self._output_stream.write("\n")
        self._output_stream.flush()

    def _error(self, command: str) -> None:
        self._output_stream.write(f'I don\'t know what the command "{command}" is.\n')
        self._output_stream.flush()
