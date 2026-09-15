from backend.utils import AnswerAccuracy, PointDeduction, AdvancedSettings, Feedback


class StoreConfigurations:
    """Holds the global settings of a test.

    An instance of this class is returned by ``TestFacade.get_settings()``
    and is used to configure test-wide behavior such as the title,
    navigation mode, answer accuracy, point distribution/deduction, the
    pass score, and the test-level feedback texts.
    """
    def __init__(self):
        self.title = "Test"
        self.path_excel_files = []
        self.path_export = ""
        self.answer_acc = AnswerAccuracy()
        self.point_deduction = PointDeduction()

        self.point_distribution = {
            "gap": "1",
            "selection": "2",
            "matching": "2"
        }

        self.advanced_settings = AdvancedSettings()
        self.feedback = {
            "feedback_correct": Feedback("FEEDBACK_CORRECT", "feedback_correct"),
            "feedback_incorrect": Feedback("FEEDBACK_INCORRECT", "feedback_incorrect")
        }
        self.pass_score_percentage = 40

    def set_title(self, title):
        """Set the title of the test.
        Args:
            title: The new title of the test.
        """
        self.title = title

    def set_answer_acc(self, type, value=None):
        """Set the accepted deviation for numerical responses.
        Args:
            type: The type of accuracy. Possible values are ``"relative"``,
                ``"absolute"`` and ``"exact"``.
            value: The allowed deviation. For ``"relative"`` this is a
                percentage, for ``"absolute"`` an absolute value. Not
                required for ``"exact"``.
        """
        self.answer_acc.set_answer_acc(type, value)

    def set_navigation_mode(self, navigation_mode):
        """Set how learners can navigate through the test.
        Args:
            navigation_mode: The navigation mode. Possible values are
                ``"test_path_control"`` (visibility of tasks is restricted,
                required for variant-dependent tables), ``"linear"``
                (tasks must be answered in order) and ``"nonlinear"``
                (tasks can be answered in any order).
        """
        self.advanced_settings.set_navigation_mode(navigation_mode)

    def keep_responses(self, bool):
        """Set whether previously entered responses are kept between attempts.
        Args:
            bool: ``True`` to keep previously entered responses visible on a
                new attempt (default), ``False`` to clear them.
        """
        self.advanced_settings.keep_responses = bool

    def set_point_deduction(self, point_deduction_per_attempt, min_score_percentage):
        """Set an automatic point deduction for repeated response attempts.
        Args:
            point_deduction_per_attempt: Number of points deducted for each
                new attempt.
            min_score_percentage: Minimum percentage of points still
                awarded when the task is eventually answered completely
                correctly.
        """
        self.point_deduction.is_used = True
        self.point_deduction.point_deduction_per_attempt = point_deduction_per_attempt
        self.point_deduction.min_score_percentage = min_score_percentage

    def set_point_distribution(self, type, value):
        """Set the default number of points per task type for the whole test.
        Args:
            type: The task type. Possible values are ``"gap"``,
                ``"selection"`` and ``"matching"``.
            value: The number of points awarded per task of this type. Can
                be overridden per task with
                ``TaskFacade.set_point_distribution()``.
        """
        if type in ["gap", "selection", "matching"]:
            self.point_distribution[type] = str(value)
        else:
            raise ValueError(f"unknown task-type: {type}")

    def set_pass_score_percentage(self, value):
        """Set the percentage of points required to pass the test.
        Args:
            value: The required percentage, between 0 and 100.
        """
        if 0 <= value < 100:
            self.pass_score_percentage = value
        else:
            raise ValueError(
                "value of 'pass_score_percentage' must be between 0 and 100"
            )

    def set_feedback(self, type, value):
        """Set the feedback text shown at the end of the test.
        Args:
            type: The type of feedback. Possible values are ``"correct"``
                (test passed) and ``"incorrect"`` (test not passed).
            value: The feedback text. May contain the placeholders
                ``{SCORE}`` and (unless ``"test_path_control"`` is the
                navigation mode) ``{MAXSCORE}``.
        """
        if type == "incorrect":
            self.feedback["feedback_incorrect"].value = value
        elif type == "correct":
            self.feedback["feedback_correct"].value = value
        else:
            raise ValueError(f"unknown feedback-type: {type}")

    def to_dict(self):
        return {
            "test_title": self.title,
            "path_excel_files": self.path_excel_files,
            "path_export": self.path_export,
            "answer_acc": self.answer_acc.to_dict(),
            "point_deduction": self.point_deduction.to_dict(),
            "point_distribution": self.point_distribution,
            "advanced_settings": self.advanced_settings.to_dict(),
            "feedback": {
                k: v.to_dict()
                for k, v in self.feedback.items()
            },
            "pass_score_percentage": self.pass_score_percentage
        }

    @classmethod
    def from_dict(cls, data):
        store = cls()

        store.title = data.get("test_title", "Test")
        store.path_excel_files = data.get("path_excel_files", [])
        store.path_export = data.get("path_export", "")
        store.answer_acc = AnswerAccuracy.from_dict(data.get("answer_acc", {}))
        store.point_deduction = PointDeduction.from_dict(
            data.get("point_deduction", {})
        )

        point_distribution_default = {
            "gap": "1",
            "selection": "2",
            "matching": "2"
        }

        loaded_point_distribution = data.get(
            "point_distribution",
            point_distribution_default
        )

        store.point_distribution = {
            **point_distribution_default,
            **loaded_point_distribution
        }

        store.advanced_settings = AdvancedSettings.from_dict(
            data.get("advanced_settings", {})
        )

        feedback_default = {
            "feedback_correct": Feedback(
                "FEEDBACK_CORRECT",
                "feedback_correct"
            ).to_dict(),
            "feedback_incorrect": Feedback(
                "FEEDBACK_INCORRECT",
                "feedback_incorrect"
            ).to_dict()
        }

        feedback_data = data.get("feedback", feedback_default)

        store.feedback = {
            k: Feedback.from_dict(v)
            for k, v in feedback_data.items()
        }

        store.pass_score_percentage = data.get("pass_score_percentage", 40)

        return store