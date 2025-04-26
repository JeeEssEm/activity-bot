from jsonpickle import encode, decode
from dtos import *


def serialize_dataclasses(obj: dict) -> str:
    return encode(obj)


def deserialize_dataclasses(json_string: str):
    return decode(json_string)
