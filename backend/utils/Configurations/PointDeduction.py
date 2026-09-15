class PointDeduction:
    def __init__(self):
        self.is_used = False
        self.point_deduction_per_attempt = 0.5
        self.min_score_percentage = 40

    def to_dict(self):
        return {
            "is_used": self.is_used,
            "point_deduction_per_attempt": self.point_deduction_per_attempt,
            "min_score_percentage": self.min_score_percentage
        }

    @staticmethod
    def from_dict(data: dict):
        pd = PointDeduction()
        pd.is_used = data.get("is_used", False)
        pd.point_deduction_per_attempt = data.get("point_deduction_per_attempt", 0.5)
        pd.min_score_percentage = data.get("min_score_percentage", 40)

        return pd