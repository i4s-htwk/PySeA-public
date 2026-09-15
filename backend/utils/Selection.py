from dataclasses import dataclass, field
from typing import List
from itertools import combinations


@dataclass
class Selection:
    """A single-choice or multiple-choice selection task element.

    An instance of this class is returned by ``TaskFacade.selection()``.
    ``set_correct()`` and ``set_incorrect()`` define the answer options,
    which may be plain text, ``Image`` or ``VariantDependentImage``
    objects, and ``set_wrong_count()`` limits how many incorrect options
    are shown. The object can be embedded directly into an item body.
    """
    id: str = "SELECTION"
    type: str = "singleChoice"
    correct: List[str] = field(default_factory=list)
    incorrect: List[str] = field(default_factory=list)
    adjust_visibility: bool = False
    visible_wrong_count: int = 0

    def set_correct(self, correct):
        """Set the correct answer option(s).
        Args:
            correct: A list of correct options. Each entry may be plain
                text or an ``Image`` / ``VariantDependentImage`` object.
                For a single-choice selection, provide exactly one entry.
        """
        self.correct = [v.id if hasattr(v, "id") else str(v) for v in correct]

    def set_incorrect(self, incorrect):
        """Set the incorrect answer option(s).
        Args:
            incorrect: A list of incorrect options. Each entry may be
                plain text or an ``Image`` / ``VariantDependentImage``
                object.
        """
        self.incorrect = [v.id if hasattr(v, "id") else str(v) for v in incorrect]

    def set_wrong_count(self, wrong_count):
        """Limit how many incorrect options are shown to the learner.

        The visible incorrect options are chosen at random from all
        options set via ``set_incorrect()``.
        Args:
            wrong_count: The number of incorrect options to display.
        """
        self.adjust_visibility = True
        self.visible_wrong_count = wrong_count

    def get_visible_wrong_combinations(self):
        if self.adjust_visibility:
            wrong_answers = self.incorrect
            visible_count = self.visible_wrong_count
            return list(combinations(wrong_answers, visible_count))
        else:
            raise Exception(
                "selection.adjust_visibility must be set to True for adjusting the number of wrong answers"
            )

    def get_slot_ids(self):
        if not self.adjust_visibility:
            raise Exception(
                "selection.adjust_visibility must be set to True for using selection slots"
            )

        return [
            f"SELECTION_SLOT_{i + 1}"
            for i in range(self.visible_wrong_count)
        ]

    def to_dict(self):
        return {
            "id": self.id,
            "type":self.type,
            "correct": self.correct,
            "incorrect": self.incorrect,
            "adjust_visibility": self.adjust_visibility,
            "visible_wrong_count": self.visible_wrong_count,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            type= data["type"],
            correct=data["correct"],
            incorrect=data["incorrect"],
            adjust_visibility=data.get("adjust_visibility", False),
            visible_wrong_count=data.get("visible_wrong_count", 0)
        )

    def __radd__(self, other: object) -> str:
        if isinstance(other, str):
            return other + "{SELECTION}"
        return NotImplemented

    def __add__(self, other: object) -> str:
        if isinstance(other, str):
            return "{SELECTION}" + other
        return NotImplemented
