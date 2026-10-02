"""
DMC Dynamic Re-routing Module
SIH26123 - Dynamic Movement Contract Protocol

Purpose:
    Generate an alternate ("shadow") route when the current
    route becomes unavailable because of a blocked aisle,
    conflict, or changed warehouse condition.

Prototype approach:
    Grid-based shortest-path search using BFS.

The module is simulation-oriented. In a full CoppeliaSim/
ROS implementation, the route planner can be connected to
the simulator's map and robot localization system.
"""

from collections import deque
from typing import Dict, List, Optional, Set, Tuple


Position = Tuple[int, int]
Grid = List[List[int]]


class ReroutingEngine:
    """
    Generates alternate routes through a grid warehouse.

    Grid convention:

        0 = free cell
        1 = blocked cell

    This is a prototype representation of warehouse aisles.
    """

    MOVES = [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
    ]

    def __init__(self, grid: Grid):
        self.grid = grid

        if not grid or not grid[0]:
            raise ValueError(
                "Grid cannot be empty."
            )

        self.rows = len(grid)
        self.cols = len(grid[0])

        for row in grid:
            if len(row) != self.cols:
                raise ValueError(
                    "All grid rows must have equal length."
                )

    # -----------------------------------------------------
    # Grid validation
    # -----------------------------------------------------

    def is_valid_position(
        self,
        position: Position,
    ) -> bool:
        """Check whether a position is inside the grid."""

        x, y = position

        return (
            0 <= x < self.rows
            and 0 <= y < self.cols
        )

    def is_free(
        self,
        position: Position,
    ) -> bool:
        """Check whether a grid cell is traversable."""

        if not self.is_valid_position(position):
            return False

        x, y = position

        return self.grid[x][y] == 0

    # -----------------------------------------------------
    # Neighbour generation
    # -----------------------------------------------------

    def neighbours(
        self,
        position: Position,
    ) -> List[Position]:
        """Return valid neighbouring cells."""

        x, y = position

        result = []

        for dx, dy in self.MOVES:

            next_position = (
                x + dx,
                y + dy,
            )

            if self.is_free(next_position):
                result.append(next_position)

        return result

    # -----------------------------------------------------
    # Route planning
    # -----------------------------------------------------

    def find_route(
        self,
        start: Position,
        goal: Position,
    ) -> Optional[List[Position]]:
        """
        Find a shortest route using Breadth-First Search.

        Returns:
            List of grid positions from start to goal,
            or None if no route exists.
        """

        if not self.is_free(start):
            return None

        if not self.is_free(goal):
            return None

        queue = deque([start])

        parent: Dict[
            Position,
            Optional[Position]
        ] = {
            start: None
        }

        while queue:

            current = queue.popleft()

            if current == goal:
                return self._reconstruct_path(
                    parent,
                    goal,
                )

            for neighbour in self.neighbours(current):

                if neighbour in parent:
                    continue

                parent[neighbour] = current

                queue.append(neighbour)

        return None

    # -----------------------------------------------------
    # Path reconstruction
    # -----------------------------------------------------

    @staticmethod
    def _reconstruct_path(
        parent: Dict[
            Position,
            Optional[Position]
        ],
        goal: Position,
    ) -> List[Position]:
        """Reconstruct path from BFS parent information."""

        path = []

        current = goal

        while current is not None:

            path.append(current)

            current = parent[current]

        path.reverse()

        return path

    # -----------------------------------------------------
    # Block an aisle / cell
    # -----------------------------------------------------

    def block_cell(
        self,
        position: Position,
    ) -> None:
        """
        Mark a warehouse cell as blocked.

        This simulates an obstacle or blocked aisle.
        """

        if not self.is_valid_position(position):
            raise ValueError(
                "Cannot block a position outside the grid."
            )

        x, y = position

        self.grid[x][y] = 1

    # -----------------------------------------------------
    # Shadow-route generation
    # -----------------------------------------------------

    def generate_shadow_route(
        self,
        start: Position,
        goal: Position,
        blocked_cells: Optional[Set[Position]] = None,
    ) -> Optional[List[Position]]:
        """
        Generate an alternate route while avoiding
        temporary blocked cells.

        This represents the proposed DMC shadow-route
        concept.
        """

        blocked_cells = blocked_cells or set()

        original_values = {}

        # Temporarily mark blocked cells.
        for position in blocked_cells:

            if not self.is_valid_position(position):
                continue

            x, y = position

            original_values[position] = self.grid[x][y]

            self.grid[x][y] = 1

        try:

            route = self.find_route(
                start,
                goal,
            )

        finally:

            # Restore original map.
            for position, value in original_values.items():

                x, y = position

                self.grid[x][y] = value

        return route


# =========================================================
# Demonstration
# =========================================================

if __name__ == "__main__":

    # Example warehouse grid.
    #
    # 0 = free
    # 1 = blocked
    #
    # The grid represents a simplified warehouse layout.

    warehouse = [
        [0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0],
    ]

    planner = ReroutingEngine(
        warehouse
    )

    start = (0, 0)
    goal = (4, 5)

    print("\nDMC SHADOW-ROUTE REPLANNING")
    print("===========================")

    primary_route = planner.find_route(
        start,
        goal,
    )

    print(
        f"Primary route: {primary_route}"
    )

    # Simulate a newly blocked aisle.
    blocked = {
        (0, 2),
        (0, 3),
    }

    shadow_route = planner.generate_shadow_route(
        start,
        goal,
        blocked_cells=blocked,
    )

    print(
        f"Blocked cells : {blocked}"
    )

    print(
        f"Shadow route  : {shadow_route}"
    )

    if shadow_route:
        print(
            "Status        : Alternate route found"
        )
    else:
        print(
            "Status        : No alternate route available"
        )
