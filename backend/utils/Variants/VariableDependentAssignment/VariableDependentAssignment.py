from itertools import product
from backend.utils import VariableVariants

class VariableDependentAssignment:
    """Variant assignment based on self-defined rules for the student ID.

    Accessible via ``StoreVariants.assignment`` after calling
    ``TestFacade.variants("variable_dependent_assignment")``. Variables are
    created with ``add_variable()``, which returns a ``VariableVariants``
    object used to define how specific digits of the student ID map onto
    values of that variable.
    """
    def __init__(self):
        self.list_variables = []
        self.list_variants = []

    def add_variable(self):
        """Add a new variable whose value depends on a digit of the student ID.
        Returns:
            The created ``VariableVariants`` object, used to configure
            which digit of the student ID it reads and which conditions
            map that digit to a value.
        """
        variable = VariableVariants("VARIABLE_"+str(len(self.list_variables)+1))
        self.list_variables.append(variable)
        self.update_variants()
        return variable

    def get_variable(self, variable_id):
        for variable in self.list_variables:
            if variable.id == variable_id:
                return variable
        return None

    def get_variable_name(self, variable_name):
        for variable in self.list_variables:
            for v in variable.variables:
                if v == variable_name:
                    return v
        return None

    def update_variants(self):
        if not self.list_variables:
            self.list_variants = []
            return
        if len(self.list_variables) == 1:
            variable = self.list_variables[0]
            self.list_variants = [[cond] for cond in variable.list_conditions]
            return
        conditions_lists = [variable.list_conditions for variable in self.list_variables]
        self.list_variants = [
            [variant[i] for i in range(len(variant))]
            for variant in product(*conditions_lists)]

    def get_count_variants(self):
        self.update_variants()
        return len(self.list_variants)

    def maxima_code_variants(self):
        self.update_variants()
        if not self.list_variants:
            return "float($(1));"

        blocks = []
        for i, variant in enumerate(self.list_variants, start=1):
            condition_parts = []
            for j, cond in enumerate(variant):
                lb = cond.lower_bound
                ub = cond.upper_bound
                condition_parts.append(f"$({j + 1}) >= {lb} and $({j + 1}) <= {ub}")

            joined = " and ".join(condition_parts)
            if i == 1:
                blocks.append(f"if {joined} then {i}")
            else:
                blocks.append(f"else if {joined} then {i}")

        maxima_code = "float(\n    " + "\n    ".join(blocks) + "\n);"
        return maxima_code

    def to_dict(self):
        return {
            "list_variables": [v.to_dict() for v in self.list_variables],
        }

    @classmethod
    def from_dict(cls, data):
        assignment = cls()
        assignment.list_variables = [VariableVariants.from_dict(v) for v in data.get("list_variables", [])]
        assignment.update_variants()
        return assignment