from dataclasses import dataclass


@dataclass
class ActivityDto:
    stream_id: int
    user_id: int
    score: int
