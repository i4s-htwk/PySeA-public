from backend.stores.StoreResponses import ExcelResponses
from backend.utils import Response, Selection, ExcelTable, CustomTable, VariantDependentImage, VariantDependentTable, \
    Matching, GraphicalAssignment, ExcelVariables


class TaskFacade:
    """Provides an interface for editing a task.

    The class offers a way to access task-related functionality
    without directly interacting with the underlying stores.
    """
    def __init__(self, test_store, id):
        self.test_store = test_store
        self.id = id

    def response(self, value) -> Response:
        """Add a response to the task.
        Args:
            value: The value of the response.
        Returns:
            An ``Response`` object representing the created response.
        """
        response_item = self.test_store.store_responses.get_item(self.id)
        return response_item.add_response(value)

    def excel_responses(self) -> ExcelResponses:
        """Add Excel-based responses to the task.
        Returns:
            An ``ExcelResponses`` object that can be used editing or adding ``ExcelResponse`` objects to the task.
        """
        response_item = self.test_store.store_responses.get_item(self.id)
        return response_item.add_excel_responses()

    def add_excel_variables(self) -> ExcelVariables:
        """Adds Excel variables to the task.

        This method creates and attaches an ``ExcelVariables`` object to the
        current task. The returned object can be used to define variables
        whose values are read from an Excel file and later embedded in the
        item body.

        Returns:
            An ``ExcelVariables`` object for configuring the Excel-based
            variables of this task.
        """
        item = self.test_store.test_structure.get_object(self.id)
        return item.add_excel_variables()

    def selection(self, type) -> Selection:
        """Add a selection element to the task.
        Args:
            type: The type of the selection element. Possible values are
                ``"simpleChoice"`` and ``"multipleChoice"``.
        Returns:
            A ``Selection`` object that can be used editing the selection.
        """
        return self.test_store.store_selections.add_item(self.id, type)

    def matching(self) -> Matching:
        """Add a matching element to the task.
                Returns:
                    A ``Matching`` object that can be used editing the matching.
                """
        return self.test_store.store_matchings.add_item(self.id)

    def graphical_assignment(self) -> GraphicalAssignment:
        """Add a graphical_assignment element to the task.
                        Returns:
                            A ``GraphicalAssignment`` object that can be used editing the graphical assignment.
                        """
        return self.test_store.store_graphical_assignment.add_item(self.id)

    def table(self, table_type) -> ExcelTable | CustomTable:
        """Add a table to the task.
        Args:
            table_type: The type of the table.  Possible values are
                ``"excelTable"`` and ``"customTable"``.
        Returns:
            An ``ExcelTable`` or ``CustomTable`` object that can be used editing the created table.
        """
        return self.test_store.store_tables.add_table(self.id, table_type)

    def variant_dependent_image(self) -> VariantDependentImage:
        """Add a variant-dependent image to the task.
        Returns:
            An ``VariantDependentImage`` object that can be used editing the created variant-dependent image.
        """
        task = self.test_store.test_structure.get_object(self.id)
        return task.add_variant_dependent_image()

    def variant_dependent_table(self) -> VariantDependentTable:
        """Add a variant-dependent table to the task.
        Returns:
            An ``VariantDependentTable`` object that can be used editing the created variant-dependent table.
        """
        task = self.test_store.test_structure.get_object(self.id)
        return task.add_variant_dependent_table()

    def item_body(self, text):
        """Set the item body of the task.

        This method is used to define the content of the task.

        The given text may include the following embedded task elements:
            ``Response``, ``ExcelResponse``, ``Selection``, ``Image``,
            ``CustomTable``, ``ExcelTable``, ``VariantDependentImage``, ``VariantDependentTable``
        Args:
            text: The text to be stored as the item body.
        """
        self.test_store.store_item_body.update_item(self.id, text)

    def feedback(self, type, text, condition=None):
        """Add feedback for correct or incorrect answers to the task.

        For ``"correct"`` feedback, ``condition`` is ignored and the text
        is shown whenever the task was answered fully correctly. This
        method can be called multiple times with ``"incorrect"`` feedback
        to define several incorrect-feedback texts for different attempts
        or response fields.

        The given text may include the following embedded elements:
            ``Image``, ``VariantDependentImage``
        Args:
            type: The type of feedback. Possible values are
                ``"correct"`` and ``"incorrect"``.
            text: The feedback text.
            condition: Only relevant for ``"incorrect"`` feedback; decides
                when the feedback is shown. Possible values are:

                - ``None`` the feedback is shown on every incorrect attempt.
                - ``int`` the feedback is shown from this attempt number
                    onward, e.g. ``2`` means from the second attempt on.
                - ``list`` of two ``int`` values ``[first, last]``; the
                    feedback is shown only for attempts in this range,
                    e.g. ``[1, 1]`` means only on the first attempt.
                - ``Response`` or ``ExcelResponse`` the feedback is shown
                    when that specific response field did not receive
                    full points.
        """
        if type not in ["correct", "incorrect"]:
            raise ValueError("feedback type muss 'correct' oder 'incorrect' sein.")
        if not isinstance(text, str):
            raise TypeError("feedback text muss ein String sein.")
        if type == "incorrect":
            self.test_store.store_feedback.add_feedback_incorrect(self.id, text, condition)
        elif type == "correct":
            self.test_store.store_feedback.set_feedback_correct(self.id, text)

    def set_point_distribution(self, type, value):
        """Set the point distribution for this task.

        Args:
            type: The type of point distribution.
                ``"task"`` means that ``value`` is the total number of points for the whole task.
                ``"gap"`` means that ``value`` is the number of points awarded per gap/response.
            value: The number of points to assign.
        """
        if type not in ["task", "gap"]:
            raise ValueError("type muss 'task' oder 'gap' sein.")
        if not isinstance(value, (int, float, str)):
            raise TypeError("value muss int, float oder numerischer String sein.")
        task = self.test_store.test_structure.get_object(self.id)
        if type in ["task", "gap"]:
            task.point_distribution[type] = value
