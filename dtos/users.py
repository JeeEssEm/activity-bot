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
    id: int


@dataclass
class ScheduleDto:
    schedule: list[dict]


@dataclass
class StreamDto:
    type: str
    title: str
    full_stream: str

    @staticmethod
    def truncate(string: str, ln: int) -> str:
        if len(string) > ln:
            return string[:ln] + '...'
        return string

    def truncated(self) -> str:
        return self.truncate(self.title, 30) + ' ' + self.type

    def get_callback(self, page: int):
        return f'modify_subjs|{page}|{self.short_stream}'

    @property
    def short_stream(self) -> str:
        return ''.join(self.full_stream.split('#')[:2])

    def __hash__(self):
        return hash(self.full_stream)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.full_stream == other
        return self.full_stream == other.full_stream


@dataclass
class StreamState:
    full_stream: str
    is_chosen: bool
    id: int | None = None


@dataclass
class StreamsDto:
    streams: list[StreamDto]


@dataclass
class ChooseStreams:
    content: list[list[StreamDto]]
    chosen_streams: dict[str, StreamState]
