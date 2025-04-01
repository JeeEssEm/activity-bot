from dataclasses import dataclass
from enum import Enum


class StreamType(Enum):
    lecture = '📖'
    seminar = '💬'
    science_seminar = '🧪'
    practice = '🔧'

    @staticmethod
    def from_string(tp: str) -> str:
        matches = {
            'Лекция': StreamType.lecture,
            'Семинары': StreamType.seminar,
            'Практические занятия': StreamType.practice,
            'Научно-исследовательский семинар': StreamType.science_seminar,
        }
        found = matches.get(tp)
        if not found:
            return tp
        return found.value


@dataclass
class UserDto:
    fullname: str
    email: str


@dataclass
class ScheduleDto:
    schedule: list[dict]


@dataclass
class StreamDto:
    type: str
    title: str
    full_stream: str

    def __hash__(self):
        return hash(self.full_stream)


@dataclass
class StreamsDto:
    streams: list[StreamDto]
