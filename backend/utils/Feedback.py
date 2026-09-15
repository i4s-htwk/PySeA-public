from backend.utils import ExcelResponse, Response


class Feedback:
    def __init__(self, id, type, condition=None):
        self.id = id
        self.value = ""
        self.type = type
        self.condition = condition

    def to_dict(self):
        return {
            "id": self.id,
            "value": self.value,
            "type": self.type,
            "condition": self.condition_to_dict(self.condition)
        }

    @staticmethod
    def from_dict(data):
        condition = Feedback.condition_from_dict(data.get("condition"))

        fb = Feedback(
            data["id"],
            data["type"],
            condition
        )

        fb.value = data.get("value", "")
        return fb

    @staticmethod
    def condition_to_dict(condition):
        if condition is None:
            return {
                "kind": "none",
                "value": None
            }

        if isinstance(condition, int):
            return {
                "kind": "int",
                "value": condition
            }

        if isinstance(condition, list):
            return {
                "kind": "list",
                "value": [
                    Feedback.condition_to_dict(item)
                    for item in condition
                ]
            }

        if isinstance(condition, ExcelResponse):
            return {
                "kind": "excel_response",
                "value": condition.to_dict()
            }

        if isinstance(condition, Response):
            return {
                "kind": "response",
                "value": condition.to_dict()
            }

        raise TypeError(
            f"Nicht unterstützter condition-Typ: {type(condition).__name__}"
        )

    @staticmethod
    def condition_from_dict(data):
        if data is None:
            return None

        kind = data.get("kind")
        value = data.get("value")

        if kind == "none":
            return None

        if kind == "int":
            return value

        if kind == "list":
            return [
                Feedback.condition_from_dict(item)
                for item in value
            ]

        if kind == "excel_response":
            return ExcelResponse.from_dict(value)

        if kind == "response":
            return Response.from_dict(value)

        raise ValueError(
            f"Unbekannter condition-Typ beim Laden: {kind}"
        )