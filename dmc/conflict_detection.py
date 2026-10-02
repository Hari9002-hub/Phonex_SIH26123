"""
DMC Conflict Detection Module
SIH26123 - Dynamic Movement Contract Protocol

Purpose:
    Detect potential conflicts between AMRs before they enter
    a shared warehouse conflict zone.

Detection uses:
    1. Same conflict zone
    2. ETA information
    3. Temporal occupancy overlap

This is a prototype implementation based on the DMC
architecture proposed in the SIH submission.

Important:
    Thresholds used here are prototype parameters and must
    be validated through simulation.
"""

from dataclasses import dataclass
from typing import Optional

from models import RobotState, MovementIntent


@dataclass
class ConflictZone:
    """
    Represents a shared warehouse conflict zone.

    x, y:
        Approximate centre of the conflict zone.

    radius:
        Prototype spatial influence radius.
    """

    zone_id: str
    x: float
    y: float
    radius: float = 1.0


@dataclass
class ConflictResult:
    """
    Result returned by the conflict detector.
    """

    conflict: bool
    reason: str

    robot_a: str
    robot_b: str

    zone_id: Optional[str]

    eta_a: float
    eta_b: float

    entry_overlap: bool
    exit_overlap: bool
    temporal_overlap: bool


class ConflictDetector:
    """
    Detects spatial and temporal conflicts between two AMRs.
    """

    def __init__(self, safety_time_window: float = 2.0):
        """
        safety_time_window:
            Additional temporal margin used by the prototype.

        This is NOT an official SIH value.
        It must be validated experimentally.
        """

        if safety_time_window < 0:
            raise ValueError(
                "safety_time_window cannot be negative"
            )

        self.safety_time_window = safety_time_window

    # -----------------------------------------------------
    # Spatial checks
    # -----------------------------------------------------

    @staticmethod
    def distance(
        x1: float,
        y1: float,
        x2: float,
        y2: float,
    ) -> float:
        """Calculate 2D Euclidean distance."""

        dx = x2 - x1
        dy = y2 - y1

        return (dx * dx + dy * dy) ** 0.5

    def robot_near_zone(
        self,
        robot: RobotState,
        zone: ConflictZone,
    ) -> bool:
        """
        Check whether an AMR is within the conflict-zone
        influence radius.
        """

        distance = self.distance(
            robot.x,
            robot.y,
            zone.x,
            zone.y,
        )

        return distance <= zone.radius

    # -----------------------------------------------------
    # Temporal checks
    # -----------------------------------------------------

    @staticmethod
    def intervals_overlap(
        start_a: float,
        end_a: float,
        start_b: float,
        end_b: float,
        margin: float = 0.0,
    ) -> bool:
        """
        Check whether two time intervals overlap.

        Example:

            Robot A: |---------|
            Robot B:       |---------|

        If their occupancy intervals overlap, both robots
        may require the shared zone simultaneously.
        """

        a_start = start_a - margin
        a_end = end_a + margin

        b_start = start_b - margin
        b_end = end_b + margin

        return (
            a_start < b_end
            and b_start < a_end
        )

    # -----------------------------------------------------
    # Main conflict detection
    # -----------------------------------------------------

    def detect(
        self,
        robot_a: RobotState,
        intent_a: MovementIntent,
        robot_b: RobotState,
        intent_b: MovementIntent,
        zone: ConflictZone,
    ) -> ConflictResult:
        """
        Detect whether two AMRs have a potential conflict
        at the same shared zone.
        """

        # ---------------------------------------------
        # 1. Check zone identity
        # ---------------------------------------------

        same_zone = (
            intent_a.conflict_zone == zone.zone_id
            and intent_b.conflict_zone == zone.zone_id
        )

        if not same_zone:
            return ConflictResult(
                conflict=False,
                reason="Different conflict zones",
                robot_a=robot_a.robot_id,
                robot_b=robot_b.robot_id,
                zone_id=zone.zone_id,
                eta_a=intent_a.eta,
                eta_b=intent_b.eta,
                entry_overlap=False,
                exit_overlap=False,
                temporal_overlap=False,
            )

        # ---------------------------------------------
        # 2. Check spatial proximity
        # ---------------------------------------------

        spatial_a = self.robot_near_zone(
            robot_a,
            zone,
        )

        spatial_b = self.robot_near_zone(
            robot_b,
            zone,
        )

        spatially_relevant = spatial_a or spatial_b

        if not spatially_relevant:
            return ConflictResult(
                conflict=False,
                reason="Robots are outside zone influence",
                robot_a=robot_a.robot_id,
                robot_b=robot_b.robot_id,
                zone_id=zone.zone_id,
                eta_a=intent_a.eta,
                eta_b=intent_b.eta,
                entry_overlap=False,
                exit_overlap=False,
                temporal_overlap=False,
            )

        # ---------------------------------------------
        # 3. Check entry-time overlap
        # ---------------------------------------------

        entry_difference = abs(
            intent_a.expected_entry_time
            - intent_b.expected_entry_time
        )

        entry_overlap = (
            entry_difference
            <= self.safety_time_window
        )

        # ---------------------------------------------
        # 4. Check occupancy interval overlap
        # ---------------------------------------------

        temporal_overlap = self.intervals_overlap(
            intent_a.expected_entry_time,
            intent_a.expected_exit_time,
            intent_b.expected_entry_time,
            intent_b.expected_exit_time,
            margin=self.safety_time_window,
        )

        # ---------------------------------------------
        # 5. Final decision
        # ---------------------------------------------

        conflict = (
            spatially_relevant
            and temporal_overlap
        )

        if conflict:
            reason = (
                "Same conflict zone with overlapping "
                "occupancy windows"
            )
        elif entry_overlap:
            reason = (
                "Entry times are close but occupancy "
                "windows do not overlap"
            )
        else:
            reason = (
                "Same zone but no temporal conflict"
            )

        return ConflictResult(
            conflict=conflict,
            reason=reason,
            robot_a=robot_a.robot_id,
            robot_b=robot_b.robot_id,
            zone_id=zone.zone_id,
            eta_a=intent_a.eta,
            eta_b=intent_b.eta,
            entry_overlap=entry_overlap,
            exit_overlap=temporal_overlap,
            temporal_overlap=temporal_overlap,
        )


# =========================================================
# Simple standalone demonstration
# =========================================================

if __name__ == "__main__":

    detector = ConflictDetector(
        safety_time_window=2.0
    )

    zone = ConflictZone(
        zone_id="Z1",
        x=5.0,
        y=5.0,
        radius=3.0,
    )

    robot_1 = RobotState(
        robot_id="AMR_1",
        x=3.0,
        y=5.0,
        heading=0.0,
        speed=1.0,
        current_task="Pickup_A",
        destination="Drop_A",
        conflict_zone="Z1",
    )

    robot_2 = RobotState(
        robot_id="AMR_2",
        x=7.0,
        y=5.0,
        heading=3.14,
        speed=1.0,
        current_task="Pickup_B",
        destination="Drop_B",
        conflict_zone="Z1",
    )

    intent_1 = MovementIntent(
        robot_id="AMR_1",
        conflict_zone="Z1",
        eta=2.0,
        expected_entry_time=10.0,
        expected_exit_time=14.0,
        planned_path=[
            (3.0, 5.0),
            (5.0, 5.0),
        ],
        destination="Drop_A",
    )

    intent_2 = MovementIntent(
        robot_id="AMR_2",
        conflict_zone="Z1",
        eta=3.0,
        expected_entry_time=11.0,
        expected_exit_time=15.0,
        planned_path=[
            (7.0, 5.0),
            (5.0, 5.0),
        ],
        destination="Drop_B",
    )

    result = detector.detect(
        robot_1,
        intent_1,
        robot_2,
        intent_2,
        zone,
    )

    print("\nDMC CONFLICT DETECTION")
    print("======================")
    print(f"Robots       : {result.robot_a} vs {result.robot_b}")
    print(f"Zone         : {result.zone_id}")
    print(f"ETA A        : {result.eta_a:.2f}s")
    print(f"ETA B        : {result.eta_b:.2f}s")
    print(f"Entry overlap: {result.entry_overlap}")
    print(f"Time overlap : {result.temporal_overlap}")
    print(f"Conflict     : {result.conflict}")
    print(f"Reason       : {result.reason}")
