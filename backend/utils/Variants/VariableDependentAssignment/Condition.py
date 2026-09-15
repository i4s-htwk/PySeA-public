class Condition:
    """A single value rule of a ``VariableVariants`` variable.

    Returned by ``VariableVariants.add_condition()``. ``lower_bound`` and
    ``upper_bound`` define the digit range for which this condition
    applies, and ``values`` maps variable names to the value assigned when
    the condition matches.
    """
    def __init__(self, lower_bound=0, upper_bound=9, values={}):
        self.values = values
        self.lower_bound: int = lower_bound
        self.upper_bound: int = upper_bound

    def to_dict(self):
        return {
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
            "values": self.values
        }

    @classmethod
    def from_dict(cls, data):
        if isinstance(data, Condition):
            return data
        return cls(
            lower_bound=data.get("lower_bound", 0),
            upper_bound=data.get("upper_bound", 9),
            values=data.get("values", {})
        )