"""
DMC Context-Aware Priority Module
SIH26123 - Dynamic Movement Contract Protocol

Priority model proposed in the SIH submission:

    P_i = w1*U_i + w2*D_i + w3*R_i

Where:
    U = Task urgency
    D = Delay impact
    R = Re-routing difficulty

The weights are prototype parameters and must be validated
experimentally. They are not official SIH requirements.
"""

from dataclasses import dataclass


@dataclass
class PriorityFactors:
    """
    Context used to calculate a robot's local priority.

    All factor values are expected to be normalized to
    the range 0.0 to 1.0.
    """

    urgency: float
    delay_impact: float
    rerouting_difficulty: float

    # Prototype weights.
    w_urgency: float = 1.0
    w_delay: float = 1.0
    w_reroute: float = 1.0

    def __post_init__(self):
        """
        Validate factor and weight values.
        """

        factors = {
            "urgency": self.urgency,
            "delay_impact": self.delay_impact,
            "rerouting_difficulty": self.rerouting_difficulty,
        }

        for name, value in factors.items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{name} must be between 0.0 and 1.0"
                )

        weights = {
            "w_urgency": self.w_urgency,
            "w_delay": self.w_delay,
            "w_reroute": self.w_reroute,
        }

        for name, value in weights.items():
            if value < 0.0:
                raise ValueError(
                    f"{name} cannot be negative"
                )

    def score(self) -> float:
        """
        Calculate the DMC priority score.

        P = w1*U + w2*D + w3*R
        """

        return (
            self.w_urgency * self.urgency
            + self.w_delay * self.delay_impact
            + self.w_reroute * self.rerouting_difficulty
        )


class PriorityEngine:
    """
    Calculates and compares local AMR priorities.
    """

    def calculate(
        self,
        robot_id: str,
        factors: PriorityFactors,
    ) -> tuple[str, float]:

        return robot_id, factors.score()

    @staticmethod
    def select_higher_priority(
        robot_a: tuple[str, float],
        robot_b: tuple[str, float],
    ) -> tuple[str, float]:
        """
        Select the robot with the higher priority score.

        If scores are equal, the result is deterministic using
        robot ID ordering. This avoids nondeterministic behaviour
        in the prototype.
        """

        id_a, score_a = robot_a
        id_b, score_b = robot_b

        if score_a > score_b:
            return robot_a

        if score_b > score_a:
            return robot_b

        return min(robot_a, robot_b, key=lambda item: item[0])


if __name__ == "__main__":

    engine = PriorityEngine()

    # Example values for demonstration only.
    # These are NOT measured warehouse values.

    amr_1 = PriorityFactors(
        urgency=0.8,
        delay_impact=0.7,
        rerouting_difficulty=0.3,
    )

    amr_2 = PriorityFactors(
        urgency=0.5,
        delay_impact=0.6,
        rerouting_difficulty=0.9,
    )

    priority_1 = engine.calculate(
        "AMR_1",
        amr_1,
    )

    priority_2 = engine.calculate(
        "AMR_2",
        amr_2,
    )

    winner = engine.select_higher_priority(
        priority_1,
        priority_2,
    )

    print("\nDMC PRIORITY ENGINE")
    print("===================")

    print(
        f"{priority_1[0]} priority: "
        f"{priority_1[1]:.2f}"
    )

    print(
        f"{priority_2[0]} priority: "
        f"{priority_2[1]:.2f}"
    )

    print(
        f"Selected robot: {winner[0]}"
    )

    print(
        f"Priority score: {winner[1]:.2f}"
    )
