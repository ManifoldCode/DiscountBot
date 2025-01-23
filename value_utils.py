from typing import TypeVar

_T = TypeVar("_T")


class NoneValueError(Exception):
    def __init__(self) -> None:
        super().__init__("value should not be None")


def unwrap(value: _T | None) -> _T:
    if value is None:
        raise NoneValueError
    return value
