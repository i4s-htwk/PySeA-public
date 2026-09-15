from dataclasses import dataclass
from typing import Optional


@dataclass
class Response:
    """A single response field (gap) with a fixed correct value.

    An instance of this class is returned by ``TaskFacade.response()``.
    ``value`` is the correct answer and ``points`` can be set to override
    the default point value for this specific response field. The object
    can be embedded directly into an item body or table cell.
    """
    id: str
    value: Optional[str]
    points: str = None

    def set_points(self, value):
        self.points = str(value)

    def to_dict(self) -> dict:
        return {"id": self.id, "value": self.value, "points": self.points}

    @staticmethod
    def from_dict(data: dict) -> "Response":
        return Response(id=data["id"], value=data.get("value"), points=data.get("points"))

    def __str__(self) -> str:
        return "{"+self.id+"}"

    def __radd__(self, other: object) -> str:
        if isinstance(other, str):
            return other + str(self)
        return NotImplemented

    def __add__(self, other: object) -> str:
        if isinstance(other, str):
            return str(self) + other
        return NotImplemented