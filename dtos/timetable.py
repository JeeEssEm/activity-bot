from datetime import datetime
from dataclasses import dataclass


@dataclass
class ActivityInfo:
    stream_id: int
    user_id: int
    full_stream: str
    # email: str


@dataclass
class Notification:
    user_id: int
    message: str
    stream_id: int


@dataclass
class TimeTableDTO:
    full_stream: str
    time_end: datetime
