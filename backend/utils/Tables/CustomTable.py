from backend.utils.Tables.Cell import Cell

class CustomTable:
    """A table built directly in Python code out of ``Cell`` objects.

    An instance of this class is returned by ``SectionFacade.table("customTable")``
    / ``TaskFacade.table("customTable")``. Rows are appended to ``cells`` as
    lists of ``Cell`` objects, and ``automatic_responses`` controls whether
    numeric cells become response fields. The object can be embedded
    directly into an item body.
    """
    def __init__(self, id=""):
        self.id = id
        self.cells = []
        self.automatic_responses = False

    def update_table(self, row_count, column_count):
        old_cells = self.cells
        self.cells = []

        for r in range(row_count):
            row = []
            for c in range(column_count):
                if r < len(old_cells) and c < len(old_cells[r]):
                    row.append(old_cells[r][c])
                else:
                    row.append(Cell("", 1, 1))
            self.cells.append(row)

    def to_dict(self):
        return {
            "id": self.id,
            "rows": len(self.cells),
            "columns": len(self.cells[0]) if self.cells else 0,
            "cells": [[cell.to_dict() for cell in row] for row in self.cells],
            "automatic_responses": self.automatic_responses
        }

    @classmethod
    def from_dict(cls, data):
        instance = cls()
        cell_data = data.get("cells", [])
        instance.cells = [
            [Cell.from_dict(cell_dict) for cell_dict in row]
            for row in cell_data
        ]
        instance.id = data.get("id", "")
        instance.automatic_responses = data.get("automatic_responses", {})
        return instance

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