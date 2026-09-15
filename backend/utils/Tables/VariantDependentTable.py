class VariantDependentTable:
    """A table that shows different content depending on the variant.

    An instance of this class is returned by
    ``TaskFacade.variant_dependent_table()``. ``add_table()`` assigns a
    previously created table area (its ``id``) to a range of variants. The
    object can be embedded directly into an item body.
    """
    def __init__(self, id):
        self.id = id
        self.tables = {}

    def add_table(self, table_id: str= "TABELLE_1", lower: int=0, upper: int=0):
        """Assign a table area to a range of variants.
        Args:
            table_id: The ``id`` of the table area to display (e.g.
                ``area.id`` from ``ExcelTable.add_area()``).
            lower: The first variant number for which this table is shown.
            upper: The last variant number for which this table is shown.
        """
        self.tables["value_"+str(len(self.tables)+1)] = {"table_id": table_id, "lower": lower, "upper": upper, "task_id": ""}

    def set_table_id(self, value:str, table_id: str):
        self.tables[value]["table_id"] = table_id

    def set_table_bounds(self, value: str, lb:int = None, ub:int = None):
        if lb is not None: self.tables[value]["lower"] = lb
        if ub is not None: self.tables[value]["upper"] = ub

    def to_dict(self):
        return {
            "id": self.id,
            "tables": self.tables
        }

    @staticmethod
    def from_dict(data):
        v = VariantDependentTable(data["id"])
        v.tables = data["tables"]
        return v

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