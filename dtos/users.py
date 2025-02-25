from dataclasses import dataclass


@dataclass
class UserDto:
    fullname: str
    email: str
