from backend.facades.TaskFacade import TaskFacade
from backend.utils import ExcelVariables
from backend.utils.Tables import ExcelTable, CustomTable


class SectionFacade:
    """Provides an interface for editing a section and adding new tasks.
        """
    def __init__(self, test_store, id):
        self.test_store = test_store
        self.id = id

    def add_task(self, title=None) -> TaskFacade:
        """Create a new task in the section.
                Args:
                    title: Optional title of the task.
                Returns:
                    A ``TaskFacade`` object that can be used as an interface for
                    editing the newly created task.
                """
        section = self.test_store.test_structure.get_object(self.id)
        task = section.add_task(title)
        self.test_store.store_item_body.add_item(task.id)
        self.test_store.store_responses.add_item(task.id)
        self.test_store.store_tables.add_item(task.id)
        return TaskFacade(self.test_store, task.id)

    def item_body(self, text):
        """Set the item body of the section.

        This method is used to define the content of the task.

        The given text may include the following embedded selection elements:
            ``ExcelVariables``, ``Image``, ``CustomTable``, ``ExcelTable``
        Args:
            text: The text to be stored as the item body.
        """
        self.test_store.store_item_body.update_item(self.id, text)

    def add_excel_variables(self) -> ExcelVariables:
        """Adds Excel variables to the section.

        This method creates and attaches an ``ExcelVariables`` object to the
        current section. The returned object can be used to define variables
        whose values are read from an Excel file and later embedded in the
        item body.

        Returns:
            An ``ExcelVariables`` object for configuring the Excel-based
            variables of this section.
        """
        section = self.test_store.test_structure.get_object(self.id)
        return section.add_excel_variables()

    def table(self, table_type) -> ExcelTable | CustomTable:
        """Add a table to the section.
        Args:
            table_type: The type of the table.  Possible values are
                ``"excelTable"`` and ``"customTable"``.
        Returns:
            An ``ExcelTable`` or ``CustomTable`` object that can be used editing the created table.
        """
        return self.test_store.store_tables.add_table(self.id, table_type)
