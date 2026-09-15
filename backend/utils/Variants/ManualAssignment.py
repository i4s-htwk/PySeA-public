class ManualAssignment:
    """Variant assignment where the learner enters their own variant number.

    Accessible via ``StoreVariants.assignment`` after calling
    ``TestFacade.variants("manual_assignment")``. ``count_variants`` sets
    how many variants exist in total; the test itself does not verify that
    the entered variant is the one that was actually assigned to the
    learner.
    """
    def __init__(self):
        self.count_variants = 0

    def get_count_variants(self):
        return self.count_variants

    def to_dict(self):
        return {
            "count_variants": self.count_variants
        }

    @staticmethod
    def from_dict(data):
        ms = ManualAssignment()
        ms.count_variants = data["count_variants"]
        return ms