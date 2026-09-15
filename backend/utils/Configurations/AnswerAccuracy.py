class AnswerAccuracy:
    def __init__(self):
        self.selection = "relative"
        self.relative = 2
        self.absolute = 0.1

    def set_answer_acc(self, type, value = None):
        if type == "relative":
            self.selection = type
            self.relative = value
        elif type == "absolute":
            self.selection = type
            self.absolute = value
        elif type == "exact":
            self.selection = type
        else:
            raise ValueError(f"unknown answer-accuracy type: {type}")

    @staticmethod
    def from_dict(data):
        if not data:
            return AnswerAccuracy()
        answeracc_obj = AnswerAccuracy()
        answeracc_obj.selection = data["selection"]
        answeracc_obj.relative = data["relative"]
        answeracc_obj.absolute = data["absolute"]
        return answeracc_obj

    def to_dict(self):
        return {
            "selection": self.selection,
            "relative": self.relative,
            "absolute": self.absolute
        }

