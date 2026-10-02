"""
DMC Conflict Detection Module

Detects potential conflicts between AMRs using:
1. Distance to a shared conflict zone
2. Estimated time of arrival (ETA)
3. A configurable temporal conflict window

This module is a prototype component for SIH26123.
"""

from dataclasses import dataclass
from math import hypot


@dataclass
class RobotState:
    robot_id: str
    x: float
    y: float
    speed: float
    conflict_zone: str
    destination: str


@dataclass
class ConflictResult:
    conflict: bool
    robot_a: str
    robot_b: str
    zone: str
    eta_a: float
    eta_b: float
    time_difference: float


class ConflictDetector:
    """
    Detects whether two AMRs are likely to require
    the same conflict zone at approximately the same time.
    """

    def __init__(self, time_window: float = 2.0):
        self.time_window = time_window

    @staticmethod
    def distance_to_zone(robot_x, robot_y, zone_x, zone_y):
        """Calculate Euclidean distance to a conflict zone."""
        return hypot(zone_x - robot_x, zone_y - robot_y)

    @staticmethod
    def calculate_eta(distance, speed):
        """
        Calculate estimated time of arrival.

        ETA = distance / speed

        If speed is zero or negative, ETA cannot be calculated.
        """
        if speed <= 0:
            return float("inf")

        return distance / speed

    def check_conflict(
        self,
        robot_a: RobotState,
        robot_b: RobotState,
        zone_x: float,
        zone_y: float,
    ) -> ConflictResult:
        """Check whether two robots may conflict at the same zone."""

        eta_a = self.calculate_eta(
            self.distance_to_zone(
                robot_a.x,
                robot_a.y,
                zone_x,
                zone_y,
            ),
            robot_a.speed,
        )

        eta_b = self.calculate_eta(
            self.distance_to_zone(
                robot_b.x,
                robot_b.y,
                zone_x,
                zone_y,
            ),
            robot_b.speed,
        )

        time_difference = abs(eta_a - eta_b)

        same_zone = (
            robot_a.conflict_zone == robot_b.conflict_zone
        )

        conflict = (
            same_zone
            and time_difference < self.time_window
        )

        return ConflictResult(
            conflict=conflict,
            robot_a=robot_a.robot_id,
            robot_b=robot_b.robot_id,
            zone=robot_a.conflict_zone,
            eta_a=eta_a,
            eta_b=eta_b,
            time_difference=time_difference,
        )


if __name__ == "__main__":

    detector = ConflictDetector(time_window=2.0)

    robot_1 = RobotState(
        robot_id="AMR_1",
        x=0.0,
        y=0.0,
        speed=1.0,
        conflict_zone="Z1",
        destination="Pickup_A",
    )

    robot_2 = RobotState(
        robot_id="AMR_2",
        x=4.0,
        y=0.0,
        speed=1.0,
        conflict_zone="Z1",
        destination="Pickup_B",
    )

    result = detector.check_conflict(
        robot_1,
        robot_2,
        zone_x=2.0,
        zone_y=0.0,
    )

    print("DMC Conflict Detection")
    print("----------------------")
    print(f"Robots: {result.robot_a} vs {result.robot_b}")
    print(f"Conflict Zone: {result.zone}")
    print(f"ETA {result.robot_a}: {result.eta_a:.2f}s")
    print(f"ETA {result.robot_b}: {result.eta_b:.2f}s")
    print(f"ETA Difference: {result.time_difference:.2f}s")
    print(f"Conflict Detected: {result.conflict}")
