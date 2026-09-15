from collections import Counter
import matplotlib.pyplot as plt

class StudentIdToVariantAssignment:
    """Variant assignment that derives the variant from the student ID.

    Accessible via ``StoreVariants.assignment`` after calling
    ``TestFacade.variants("student_id_to_variant_assignment")``.
    ``count_variants`` sets how many variants exist in total; the variant
    is then computed automatically and evenly from the entered student ID
    number, which OPAL can also verify.
    """
    def __init__(self, count_variants=0):
        self.count_variants = count_variants
        self.multiplier = 2654435761
        self.increment = 1013904223
        self.modulus = 2**32

    def get_count_variants(self):
        return self.count_variants

    def assign_variant(self, student_id):
        if self.count_variants <= 0:
            raise ValueError("count_variants must be greater than 0")

        matrikel = int(student_id)
        mixed = (self.multiplier * matrikel + self.increment) % self.modulus
        variant = (mixed * self.count_variants) // self.modulus + 1
        return variant

    def plot_variant_distribution(self, student_ids):
        assigned_variants = [self.assign_variant(student_id) for student_id in student_ids]

        counts = Counter(assigned_variants)

        x_values = list(range(1, self.count_variants + 1))
        y_values = [counts.get(v, 0) for v in x_values]

        plt.figure(figsize=(12, 6))
        plt.bar(x_values, y_values)
        plt.xlabel("Variante")
        plt.ylabel("Anzahl")
        plt.title( "Verteilung der Varianten\n")
        plt.xticks(x_values if self.count_variants <= 20 else x_values[::10])
        plt.tight_layout()
        plt.show()

    def maxima_code_variants(self):
        if self.count_variants <= 0:
            raise ValueError("count_variants must be greater than 0")

        return (
                "float(\n"
                "  block([\n"
                "    matrikel, mixed, variant\n"
                "  ],\n"
                "    matrikel: floor($(1)),\n"
                "    mixed: mod(" + str(self.multiplier) + " * matrikel + " + str(self.increment) + ", " + str(self.modulus) + "),\n"
                            "    variant: floor((mixed * " + str(self.count_variants) + ") / " + str(self.modulus) + ") + 1,\n"
                            "    variant\n"
                            "  )\n"
                            ");"
        )

    def to_dict(self):
        return {
            "count_variants": self.count_variants,
            "multiplier": self.multiplier,
            "increment": self.increment,
            "modulus": self.modulus
        }

    @staticmethod
    def from_dict(data):
        return StudentIdToVariantAssignment(
            count_variants=data["count_variants"]
        )