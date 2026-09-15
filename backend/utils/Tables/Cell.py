import re

from backend.utils import ExcelResponse, Response
from backend.utils.ExcelVariables import ExcelVariable


class Cell:
    """A single cell of a ``CustomTable``.

    Instantiated directly by the user and appended to
    ``CustomTable.cells``. ``value`` may be plain text, a ``Response``,
    ``ExcelResponse`` or ``ExcelVariable``, or one of the merge markers
    ``">>"`` (merge with the cell to the left) and ``"vv"`` (merge with the
    cell above).
    """
    def __init__(self, value, colspan =1, rowspan =1):
        if isinstance(value, Response) or isinstance(value, ExcelResponse):
            self.value = value.id
        elif isinstance(value, ExcelVariable):
            self.value = value.variable_id
        else:
            self.value = value
        self.colspan = colspan
        self.rowspan = rowspan

    def is_excel_cell(self) -> bool:
        pattern = r"^[A-Z]+[1-9][0-9]*$"
        return re.match(pattern, self.value) is not None

    def to_dict(self):
        return {
            "value": self.value,
            "colspan": self.colspan,
            "rowspan": self.rowspan
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get("value", ""),
            data.get("colspan", 1),
            data.get("rowspan", 1)
        )
