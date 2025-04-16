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
    id: int | None


@dataclass
class ScheduleDto:
    schedule: list[dict]


@dataclass
class StreamDto:
    type: str
    full_stream: str

    @staticmethod
    def truncate(string: str, ln: int) -> str:
        if len(string) > ln:
            return string[:ln] + '...'
        return string

    def truncated(self) -> str:
        return self.truncate(self.title, 30) + ' ' + self.emoji_type

    def get_callback(self, page: int) -> str:
        return f'modify_subjs|{page}|{self.short_stream}'

    @property
    def title(self) -> str:
        return self.full_stream.split('#')[-1]

    @property
    def short_stream(self) -> str:
        return ''.join(self.full_stream.split('#')[:2])

    @property
    def emoji_type(self):
        return StreamType.from_string(self.type)

    def __hash__(self):
        return hash(self.full_stream)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.full_stream == other
        return self.full_stream == other.full_stream


@dataclass
class StreamDtoDB(StreamDto):
    id: int

    def get_callback(self, page: int) -> str:  # накостылил
        return f'get_subj|{page}|{self.short_stream}'

    def __hash__(self):
        return hash(self.full_stream)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.full_stream == other
        return self.full_stream == other.full_stream


@dataclass
class StreamsDto:
    streams: list[StreamDto]


@dataclass
class ChooseStreams:
    content: list[list[StreamDto | StreamDtoDB]]
    chosen_streams: dict[str, [bool, StreamDto | StreamDtoDB]]

    def delete_stream_by_id(self, stream_id: int):
        flag = False
        to_delete: StreamDtoDB | None = None
        for page in self.content:
            if flag:
                break
            for stream in page:
                if isinstance(stream, StreamDtoDB) and stream.id == stream_id:
                    to_delete = stream
                    page.remove(stream)
                    flag = True
                    break
        del self.chosen_streams[to_delete.short_stream]
