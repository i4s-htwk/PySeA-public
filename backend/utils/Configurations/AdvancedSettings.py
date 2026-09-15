class AdvancedSettings:
    def __init__(self):
        self.navigation_mode = "nonlinear"
        self.keep_responses = True

    def set_navigation_mode(self, navigation_mode):
        if navigation_mode in ["test_path_control", "nonlinear", "linear"]:
            self.navigation_mode = navigation_mode
        else:
            raise ValueError(f"unknown navigation_mode: {navigation_mode}")

    def to_dict(self):
        return {
            "navigation_mode": self.navigation_mode,
            "keep_responses": self.keep_responses
        }

    @staticmethod
    def from_dict(data):
        as_obj = AdvancedSettings()
        as_obj.navigation_mode = data.get("navigation_mode", "nonlinear")
        as_obj.keep_responses = data.get("keep_responses", True)
        return as_obj