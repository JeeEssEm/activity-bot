from dataclasses import dataclass


@dataclass
class ActivityDto:
    stream_id: int
    user_id: int
    score: int
    notify: bool


@dataclass
class QueueActivityElementDto:
    user_id: int
    fullname: str
    activities: int
