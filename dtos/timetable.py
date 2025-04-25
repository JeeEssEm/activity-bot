from dataclasses import dataclass


@dataclass
class ActivityInfo:
    activity_id: int
    user_id: int
    full_stream: str
    email: str


@dataclass
class Notification:
    user_id: int
    message: str
