from typing import Any

from dataclasses import dataclass
from enum import Enum

from .users import UserDto, ScheduleDto, StreamsDto


class ErrorCode(Enum):
    internal = 1
    not_found = 2


@dataclass
class BaseResponse:
    ok: bool
    msg: str


@dataclass
class UserResponse(BaseResponse):
    dto: UserDto
    error_code: ErrorCode | None = None


@dataclass
class ScheduleResponse(BaseResponse):
    dto: ScheduleDto
    error_code: ErrorCode | None = None


@dataclass
class StreamsResponse(BaseResponse):
    dto: StreamsDto
    error_code: ErrorCode | None = None


@dataclass
class Status:
    ok: bool
    msg: str


@dataclass
class DataStatus(Status):
    data: Any
