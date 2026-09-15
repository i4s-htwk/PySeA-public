from dataclasses import dataclass
from typing import Optional

def normalize_match_text(value):
    if value is None:
        return ""

    if hasattr(value, "id"):
        return value.id

    return str(value)

@dataclass
class MatchChoice:
    id: str
    text: str
    fixed: bool = False
    match_max: int = 1

    def to_dict(self) -> dict:
        return {
            "identifier": self.id,
            "text": self.text,
            "fixed": self.fixed,
            "match_max": self.match_max}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data["identifier"],
            text=data["text"],
            fixed=data.get("fixed", False),
            match_max=data.get("match_max", 1))


@dataclass
class MatchPair:
    source_id: str
    target_id: str

    def to_dict(self) -> dict:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            source_id=data["source_id"],
            target_id=data["target_id"])


class Matching:
    """A matching task element for assigning source elements to target elements.

    An instance of this class is returned by ``TaskFacade.matching()``.
    ``add_pair()`` adds a correct source/target pair (plain text or
    ``Image`` objects) and automatically creates the corresponding source
    and target choices. The object can be embedded directly into an item
    body.
    """
    def __init__(self, response_identifier: str = "RESPONSE_1"):
        self.id = response_identifier

        self.source_choices: list[MatchChoice] = []
        self.target_choices: list[MatchChoice] = []
        self.correct_pairs: list[MatchPair] = []

        self.shuffle = True
        self.max_associations = 0

    def add_source(self, text, identifier: Optional[str] = None) -> str:
        if identifier is None:
            identifier = f"ID_{len(self.source_choices) + 1}"

        self.source_choices.append(
            MatchChoice(
                id=identifier,
                text=normalize_match_text(text)
            )
        )

        return identifier

    def add_target(self, text, identifier: Optional[str] = None) -> str:
        if identifier is None:
            identifier = f"IDT_{len(self.target_choices) + 1}"

        self.target_choices.append(
            MatchChoice(
                id=identifier,
                text=normalize_match_text(text)
            )
        )

        return identifier

    def add_pair(self, source_text, target_text):
        """Add a correct source/target matching pair.

        The source and target choices are created automatically.
        Args:
            source_text: The source element. Plain text or an ``Image``
                object.
            target_text: The target element that ``source_text`` should be
                matched to. Plain text or an ``Image`` object.
        Returns:
            A tuple ``(source_id, target_id)`` with the identifiers of the
            created source and target choices.
        """
        source_id = self.add_source(source_text)
        target_id = self.add_target(target_text)

        self.correct_pairs.append(
            MatchPair(
                source_id=source_id,
                target_id=target_id
            )
        )

        return source_id, target_id
    def to_dict(self) -> dict:
        return {
            "response_identifier": self.id,
            "source_choices": [choice.to_dict() for choice in self.source_choices],
            "target_choices": [choice.to_dict() for choice in self.target_choices],
            "correct_pairs": [pair.to_dict() for pair in self.correct_pairs],
            "shuffle": self.shuffle,
            "max_associations": self.max_associations}

    @classmethod
    def from_dict(cls, data: dict):
        matching = cls(response_identifier=data.get("response_identifier", "RESPONSE_1"))
        matching.source_choices = [MatchChoice.from_dict(choice_data)
            for choice_data in data.get("source_choices", [])]
        matching.target_choices = [
            MatchChoice.from_dict(choice_data)
            for choice_data in data.get("target_choices", [])]

        matching.correct_pairs = [
            MatchPair.from_dict(pair_data)
            for pair_data in data.get("correct_pairs", [])]
        matching.shuffle = data.get("shuffle", True)
        matching.max_associations = data.get("max_associations", 0)

        return matching

    def __radd__(self, other: object) -> str:
        if isinstance(other, str):
            return other + "{MATCHING}"
        return NotImplemented

    def __add__(self, other: object) -> str:
        if isinstance(other, str):
            return "{MATCHING}" + other
        return NotImplemented