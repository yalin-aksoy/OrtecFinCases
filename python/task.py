import datetime


class Task:
    def __init__(self, id: int, description: str,  done: bool = False, deadline: datetime.datetime = None):
        self._id = id
        self._description = description
        self._done = done
        self._deadline = deadline

    @property
    def id(self) -> int:
        return self._id

    @property
    def description(self) -> str:
        return self._description

    @property
    def done(self) -> bool:
        return self._done

    @property
    def deadline(self) -> datetime.datetime:
        return self._deadline

    @done.setter
    def done(self, done: bool):
        self._done = done

    @deadline.setter
    def deadline(self, value):
        self._deadline = value
