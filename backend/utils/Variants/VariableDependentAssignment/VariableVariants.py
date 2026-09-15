from dataclasses import dataclass, field
from backend.utils.Variants.VariableDependentAssignment.Condition import Condition

@dataclass
class VariableVariants:
    """A single variable of a ``VariableDependentAssignment``.

    Returned by ``VariableDependentAssignment.add_variable()``.
    ``value_response`` selects which digit of the student ID is used as the
    value source, ``add_variable()`` registers the variable's name, and
    ``add_condition()`` adds a ``Condition`` that maps a digit range to a
    concrete value of this variable.
    """
    id: str
    variables : list[str] = field(default_factory=list)
    list_conditions: list[Condition] = field(default_factory=list)
    value_response: int = 1

    def add_condition(self):
        """Add a condition that maps a digit range to a value.

        The returned ``Condition`` object still needs its
        ``lower_bound``, ``upper_bound`` and ``values`` set.
        Returns:
            The created ``Condition``.
        """
        cond = Condition()
        for v in self.variables:
            cond.values[v] = 0.0
        self.list_conditions.append(cond)
        return cond

    def add_variable(self, id=None):
        """Register a variable name for use in this variant's conditions.
        Args:
            id: The name under which the variable can later be referenced
                (e.g. in a section or task text). Auto-generated if
                omitted.
        """
        if id:  new_var=id
        else:   new_var = f"variable_{len(self.variables) + 1}"
        self.variables.append(new_var)
        for cond in self.list_conditions:
            cond.values[new_var] = 0.0

    def set_variable_name(self, index, new_name):
        old_key = self.variables[index]
        self.variables[index] = new_name

        for cond in self.list_conditions:
            value = cond.values[old_key]
            del cond.values[old_key]
            cond.values[new_name] = value

    def maxima_code_id(self):
        return "float($(1)["+str(self.value_response)+"]);"

    def maxima_code_variable(self, variable):
        if not self.list_conditions:
            return 'float($(1));'

        blocks = []
        for i, cond in enumerate(self.list_conditions):
            lb = cond.lower_bound
            ub = cond.upper_bound
            val = cond.values[variable]
            if i == 0:
                blocks.append(f"if $(1) >= {lb} and $(1) <= {ub} then {val}")
            else:
                blocks.append(f"else if $(1) >= {lb} and $(1) <= {ub} then {val}")

        maxima_code = "float(\n    " + "\n    ".join(blocks) + "\n);"
        return maxima_code

    def to_dict(self):
        return {
            "id": self.id,
            "variables": self.variables,
            "value_response": self.value_response,
            "list_conditions": [c.to_dict() for c in self.list_conditions]
        }

    @classmethod
    def from_dict(cls, data):
        if isinstance(data, cls):
            return data
        conditions = [Condition.from_dict(c) for c in data.get("list_conditions", [])]
        return cls(id=data.get("id"), variables=data.get("variables"), value_response=data.get("value_response", 1), list_conditions=conditions)