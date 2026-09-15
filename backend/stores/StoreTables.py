from dataclasses import dataclass, field
from typing import List, Dict

from backend.utils import ExcelTable, CustomTable, Response, ExcelVariable

def type_number(s):
    try:
        int(s)
        return True
    except:
        try:
            float(s)
            return True
        except:
            return False

@dataclass
class StoreTables:
    items: Dict[str, dict] = field(default_factory=dict)
    tabletype: str = ""

    def add_item(self, item_id: str, show_tables: bool = True):
        self.items[item_id] = {"tables": [], "show_tables": show_tables}

    def delete_item(self, id_map: Dict[str, str]):
        new_items = {}
        for old_id, entry in self.items.items():
            new_id = id_map.get(old_id, old_id)
            if new_id is None:
                continue
            new_items[new_id] = entry
        self.items = new_items

    def add_table(self, item_id: str, table_type):
        table = None
        if table_type not in ["excelTable", "customTable"]:
            raise ValueError("table_type muss entweder 'excelTable' oder 'customTable' sein.")
        id = "TABELLE_"+str(len(self.get_tables(item_id)))
        if table_type == "excelTable": table = ExcelTable(id)
        elif table_type == "customTable": table = CustomTable(id)
        if item_id not in self.items:
            self.items[item_id] = {"tables": [], "show_tables": True}
        self.items[item_id]["tables"].append(table)
        return table

    def delete_table(self, item_id: str, table_index: int):
        if item_id in self.items:
            if 0 <= table_index < len(self.items[item_id]["tables"]):
                self.items[item_id]["tables"].pop(table_index)

    def get_tables(self, item_id: str) -> List[ExcelTable]:
        return self.items.get(item_id, {}).get("tables", [])

    def set_show_tables(self, item_id: str, show: bool):
        if item_id in self.items:
            self.items[item_id]["show_tables"] = show

    def get_show_tables(self, item_id: str) -> bool:
        return self.items.get(item_id, {}).get("show_tables", True)

    def set_tabletype(self, item_id: str, tabletype: str):
        self.tabletype = tabletype

    def get_tabletype(self, item_id: str) -> str:
        return self.tabletype

    def create_tables(self, task, responses):
        merged_tables=[]
        if "task" in task.id: identifier = task.parent_id or task.id
        else: identifier = task.id
        tables = self.get_tables(identifier)
        for i, table in enumerate(tables):
            allowed_area_ids = set()
            if "task" in task.id:
                for vdt in task.variant_dependent_tables:
                    for _, t in vdt.tables.items():
                        if t.get("task_id") == task.id:
                            allowed_area_ids.add(t.get("table_id"))

            if isinstance(table, ExcelTable):
                for j, area in enumerate(table.list_areas):
                    if getattr(task, "parent_id", None) is not None and area.id not in allowed_area_ids:
                        continue
                    table.create_excel_table(area.id)
                    if responses is not None and table.automatic_responses:
                        for row in area.cells:
                            for cell in row:
                                if type_number(cell.value):
                                    id = "T_" + str(i + 1) + "_" + str(j + 1) + "_RESPONSE_" + str(len(responses) + 1)
                                    responses.append(Response(id, str(cell.value)))
                                    cell.value = Response(id, str(cell.value))
                    merged_tables.append(area)

            elif isinstance(table, CustomTable):
                j = 0
                while j < len(table.cells):
                    row = table.cells[j]
                    k = 0
                    while k < len(row):
                        cell = row[k]

                        if responses is not None and table.automatic_responses and type_number(cell.value):
                            id = "T_" + str(i + 1) + "_RESPONSE_" + str(len(responses) + 1)
                            resp_obj = Response(id, str(cell.value))
                            responses.append(resp_obj)
                            cell.value = resp_obj
                            k += 1
                            continue

                        if responses is not None and isinstance(cell.value, str) and "RESPONSE" in cell.value:
                            response = next((r for r in responses if r.id == cell.value), None)
                            cell.value = response
                            k += 1
                            continue

                        if isinstance(cell.value, str) and getattr(task, "excel_variables", None) and task.excel_variables.variables:
                            excel_variable = next(
                                (
                                    variable for variable in task.excel_variables.variables
                                    if isinstance(variable, ExcelVariable) and variable.variable_id == cell.value
                                ),
                                None
                            )
                            if excel_variable is not None:
                                cell.value = excel_variable
                                k += 1
                                continue

                        if cell.value == ">>":
                            if k == 0:
                                del row[k]
                                continue

                            colspan = 1
                            while k + colspan < len(row) and row[k + colspan].value == ">>":
                                colspan += 1

                            row[k - 1].colspan += colspan
                            del row[k:k + colspan]
                            continue

                        if cell.value == "vv":
                            if j == 0:
                                k += 1
                                continue

                            rowspan = 1
                            while j + rowspan < len(table.cells) and k < len(table.cells[j + rowspan]) \
                                    and table.cells[j + rowspan][k].value == "vv":
                                rowspan += 1

                            table.cells[j - 1][k].rowspan += rowspan

                            for r in range(j, j + rowspan):
                                if k < len(table.cells[r]):
                                    del table.cells[r][k]
                            continue

                        k += 1
                    j += 1

                merged_tables.append(table)
        return merged_tables

    def to_dict(self) -> Dict[str, dict]:
        return {
            "tabletype": self.tabletype,
            "items": {
                item_id: {
                    "tables": [
                        {"type": "ExcelTable" if isinstance(t, ExcelTable) else "CustomTable" if isinstance(t, CustomTable) else None, **t.to_dict()}
                        for t in entry["tables"]],
                    "show_tables": entry["show_tables"]
                }
                for item_id, entry in self.items.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, dict]) -> "StoreTables":
        items = {}
        for item_id, entry in data.get("items", {}).items():
            tables = []
            for t_dict in entry["tables"]:
                t_type = t_dict.get("type")
                if t_type == "ExcelTable":
                    tables.append(ExcelTable.from_dict(t_dict))
                elif t_type == "CustomTable":
                    tables.append(CustomTable.from_dict(t_dict))
            items[item_id] = {
                "tables": tables,
                "show_tables": entry.get("show_tables", True)
            }
        tabletype = data.get("tabletype", "")
        return cls(items=items, tabletype=tabletype)

    def __str__(self):
        return str({
            eid: {
                "tables": [t.id for t in entry["tables"]],
                "show_tables": entry["show_tables"]
            }
            for eid, entry in self.items.items()
        })