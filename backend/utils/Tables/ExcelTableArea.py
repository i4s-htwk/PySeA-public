from backend.utils.Tables.Cell import Cell

class ExcelTableArea:
    """A rectangular cell range of an ``ExcelTable``.

    Returned by ``ExcelTable.add_area()``, with ``cell_tl`` and ``cell_br``
    as the top-left and bottom-right corner of the range. The object can be
    embedded directly into an item body to display the area's content.
    """
    def __init__(self, id, cell_tl = "", cell_br= ""):
        self.id = id
        self.cells = []
        self.cell_tl = Cell(cell_tl, 1, 1)
        self.cell_br = Cell(cell_br, 1, 1)

    def to_dict(self):
        return {
            "id": self.id,
            "cell_tl": self.cell_tl.to_dict(),
            "cell_br": self.cell_br.to_dict()
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(data["id"])
        obj.cell_tl = Cell.from_dict(data.get("cell_tl", ""))
        obj.cell_br = Cell.from_dict(data.get("cell_br", ""))
        return obj

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