"""
Traditional Stop-and-Wait Baseline
SIH26123

Purpose:
    Provide a simple baseline for comparison with the
    proposed DMC coordination approach.

Behaviour:

    Conflict detected
          ↓
        STOP
          ↓
        WAIT
          ↓
        MOVE

This baseline is intentionally simple. It is used to
measure task completion time and waiting behaviour under
the same simulation scenarios used for DMC.

This implementation does not represent an official SIH
algorithm. It is a proposed experimental baseline.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class RobotTask:
    robot_id: str
    task_id: str
    travel_time: float
    conflict_wait_time: float = 0.0


class StopAndWaitBaseline:
    """
    Simple stop-and-wait coordination model.

    When multiple robots require the same shared zone,
    conflicting robots wait until the zone becomes available.
    """

    def __init__(self):
        self.completed_tasks: List[str] = []

    def resolve_conflict(
        self,
        robots: List[RobotTask],
    ) -> Dict[str, float]:
        """
        Apply stop-and-wait behaviour.

        The first robot proceeds.
        Other conflicting robots wait.

        For this baseline model, the first robot in the
        supplied ordering receives the zone first.

        This ordering is only a simulation policy.
        """

        if not robots:
            return {}

        waiting_times = {}

        # First robot proceeds.
        first_robot = robots[0]

        waiting_times[first_robot.robot_id] = (
            first_robot.conflict_wait_time
        )

        # Remaining robots wait for the preceding robot.
        cumulative_time = first_robot.travel_time

        for robot in robots[1:]:

            robot.conflict_wait_time = cumulative_time

            waiting_times[robot.robot_id] = (
                robot.conflict_wait_time
            )

            cumulative_time += robot.travel_time

        return waiting_times

    def calculate_completion_time(
        self,
        robot: RobotTask,
    ) -> float:
        """
        Calculate total task completion time.

        T = travel time + conflict waiting time
        """

        return (
            robot.travel_time
            + robot.conflict_wait_time
        )

    def run_scenario(
        self,
        robots: List[RobotTask],
    ) -> Dict[str, float]:
        """
        Execute one baseline scenario.
        """

        self.resolve_conflict(robots)

        completion_times = {}

        for robot in robots:

            completion_times[
                robot.robot_id
            ] = self.calculate_completion_time(
                robot
            )

        return completion_times


# =========================================================
# Demonstration
# =========================================================

if __name__ == "__main__":

    robots = [
        RobotTask(
            robot_id="AMR_1",
            task_id="TASK_A",
            travel_time=10.0,
        ),
        RobotTask(
            robot_id="AMR_2",
            task_id="TASK_B",
            travel_time=8.0,
        ),
        RobotTask(
            robot_id="AMR_3",
            task_id="TASK_C",
            travel_time=9.0,
        ),
    ]

    baseline = StopAndWaitBaseline()

    results = baseline.run_scenario(
        robots
    )

    print("\nSTOP-AND-WAIT BASELINE")
    print("======================")

    for robot_id, completion_time in results.items():

        print(
            f"{robot_id}: "
            f"{completion_time:.2f} time units"
        )

    total_time = max(
        results.values()
    )

    total_waiting = sum(
        robot.conflict_wait_time
        for robot in robots
    )

    print(
        f"\nTotal completion time: "
        f"{total_time:.2f}"
    )

    print(
        f"Total waiting time: "
        f"{total_waiting:.2f}"
    )
