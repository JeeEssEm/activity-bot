from dataclasses import dataclass


@dataclass
class UserDto:
    fullname: str
    email: str


@dataclass
class ScheduleDto:
    schedule: list[dict]


@dataclass
class StreamsDto:
    streams: list[str]
