from dataclasses import dataclass

@dataclass
class ExcelResponse:
    """A single response field whose correct value is read from Excel.

    Instances are held in ``ExcelResponses.responses`` and created via
    ``ExcelResponses.add_response()``. ``cell`` is the cell containing the
    correct value for variant 1; ``points`` can override the default point
    value for this response field. The object can be embedded directly
    into an item body or table cell.
    """
    id: str
    cell: str
    points: str = None

    def set_points(self, value):
        self.points = str(value)

    def to_dict(self) -> dict:
        return {"id": self.id, "cell": self.cell, "points": self.points}

    @staticmethod
    def from_dict(data: dict) -> "ExcelResponse":
        return ExcelResponse(id=data["id"], cell=data["cell"], points=data.get("points"))

    def __str__(self) -> str:
        return "{" + self.id + "}"

    def __radd__(self, other: object) -> str:
        if isinstance(other, str):
            return other + str(self)
        return NotImplemented

    def __add__(self, other: object) -> str:
        if isinstance(other, str):
            return str(self) + other
        return NotImplemented