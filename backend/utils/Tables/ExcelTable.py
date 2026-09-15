from openpyxl import load_workbook
from backend.utils.Tables.Cell import Cell
from backend.utils.Tables.ExcelTableArea import ExcelTableArea

class ExcelTable:
    """A table whose content is read from a range of an Excel file.

    An instance of this class is returned by ``SectionFacade.table("excelTable")``
    / ``TaskFacade.table("excelTable")``. ``excel_file`` and ``page`` select
    the data source, ``add_area()`` defines the used cell range and returns
    the corresponding ``ExcelTableArea``, and ``automatic_responses``
    controls whether numeric cells become response fields.
    """
    def __init__(self, id=""):
        self.id = id
        self.excel_file = ""
        self.page = ""
        self.list_areas = []
        self.automatic_responses = False

    def _format_display_value(self, cell):
        v = cell.value
        if v is None:
            return ""
        if not isinstance(v, (int, float)):
            return str(v)
        fmt = str(cell.number_format or "General")
        if cell.coordinate == "G6":
            print("format:")
            print(fmt)

        if "." in fmt:
            decimals = sum(1 for ch in fmt.split(".")[1] if ch in "0#")
        elif "," in fmt:
            decimals = sum(1 for ch in fmt.split(",")[1] if ch in "0#")
        else:
            decimals = 0
        v = round(v, decimals)

        if "%" in fmt:
            return f"{v * 100:.{decimals}f}%"

        value = f"{v:.{decimals}f}" if decimals else str(int(round(v)))
        return value.replace(".", ",") if "," in fmt else value

    def create_excel_table(self, area_id):
        area_obj = self.get_area(area_id)

        file = load_workbook(self.excel_file, data_only=True)
        sheet = file[self.page]
        area = area_obj.cell_tl.value + ":" + area_obj.cell_br.value
        values = sheet[area]

        for row in values:
            area_obj.cells.append([])
            for cell in row:
                colspan = 1
                rowspan = 1
                for merged_range in sheet.merged_cells.ranges:
                    if cell.coordinate == merged_range.start_cell.coordinate:
                        colspan = merged_range.size["columns"]
                        rowspan = merged_range.size["rows"]
                        break

                if cell.value is not None or cell.coordinate == area_obj.cell_tl.value:
                    value = self._format_display_value(cell)
                    area_obj.cells[-1].append(Cell(value, colspan, rowspan))

    def get_area(self, area_id):
        for area in self.list_areas:
            if area.id == area_id:
                return area
        return None

    def add_area(self, cell_tl="", cell_br=""):
        """Add a cell range of the Excel file as a displayable table area.
        Args:
            cell_tl: The top-left cell of the range (e.g. ``"C4"``).
            cell_br: The bottom-right cell of the range (e.g. ``"H8"``).
        Returns:
            The created ``ExcelTableArea``, which can be embedded directly
            into an item body.
        """
        area_id = self.id + f"_{len(self.list_areas) + 1}"
        area = ExcelTableArea(area_id, cell_tl, cell_br)
        self.list_areas.append(area)
        return area

    def to_dict(self):
        return {
            "id" : self.id,
            "excel_file" : self.excel_file,
            "page" : self.page,
            "list_areas" : [area.to_dict() for area in self.list_areas],
            "automatic_responses": self.automatic_responses
        }

    @staticmethod
    def from_dict(data):
        table = ExcelTable()
        table.id = data["id"]
        table.excel_file = data["excel_file"]
        table.page = data["page"]
        table.list_areas = [ExcelTableArea.from_dict(a) for a in data["list_areas"]]
        table.automatic_responses = data["automatic_responses"]
        return table