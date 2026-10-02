"""
DMC Integrated Coordination Controller
SIH26123 - Dynamic Movement Contract Protocol

Integrates the prototype DMC modules into one coordination
pipeline:

    SENSE
       ↓
    COMMUNICATE
       ↓
    DETECT
       ↓
    NEGOTIATE
       ↓
    RESERVE
       ↓
    EXECUTE
       ↓
    ADAPT

This controller is intended to become the bridge between
the DMC logic and the future CoppeliaSim / ROS simulation.

Important:
    This is a software prototype. It does not claim physical
    robot safety or achievement of the official SIH metrics.
"""

from typing import Dict, Optional, Tuple

from models import (
    RobotState,
    MovementIntent,
    MovementContract,
    ContractState,
)
from communication import CommunicationManager
from conflict_detection import (
    ConflictDetector,
    ConflictZone,
)
from priority import PriorityFactors
from negotiation import NegotiationEngine
from reservation import (
    ReservationManager,
)
from rerouting import (
    ReroutingEngine,
)


class DMCController:
    """
    Integrated controller for one decentralized AMR node.

    The controller keeps local coordination information and
    interacts with peer AMR messages.
    """

    def __init__(
        self,
        robot: RobotState,
        warehouse_grid,
        communication_threshold: float = 2.0,
        conflict_time_window: float = 2.0,
    ):
        self.robot = robot

        # Communication
        self.communication = CommunicationManager(
            freshness_threshold=communication_threshold
        )

        # Conflict detection
        self.conflict_detector = ConflictDetector(
            safety_time_window=conflict_time_window
        )

        # DMC negotiation
        self.negotiation = NegotiationEngine()

        # Conflict-zone reservation
        self.reservation_manager = ReservationManager()

        # Route planning / shadow-route recovery
        self.rerouting = ReroutingEngine(
            warehouse_grid
        )

        # Current contract
        self.active_contract: Optional[
            MovementContract
        ] = None

    # =====================================================
    # SENSE
    # =====================================================

    def sense(
        self,
        robot_state: RobotState,
    ) -> RobotState:
        """
        Update the local robot state.

        In the final simulator, this information will come
        from localization and sensor interfaces.
        """

        self.robot = robot_state

        return self.robot

    # =====================================================
    # COMMUNICATE
    # =====================================================

    def broadcast_intent(
        self,
        intent: MovementIntent,
    ):
        """
        Create a P2P state + intent message.

        In the prototype this is handled by the local
        communication abstraction.
        """

        message = self.communication.create_message(
            robot_state=self.robot,
            movement_intent=intent,
        )

        return message

    def receive_peer(
        self,
        message,
    ):
        """
        Receive and store a peer AMR message.
        """

        self.communication.receive_message(
            message
        )

    # =====================================================
    # DETECT
    # =====================================================

    def detect_peer_conflict(
        self,
        peer_robot: RobotState,
        peer_intent: MovementIntent,
        local_intent: MovementIntent,
        zone: ConflictZone,
    ):
        """
        Detect a potential conflict between this robot
        and a peer robot.
        """

        return self.conflict_detector.detect(
            self.robot,
            local_intent,
            peer_robot,
            peer_intent,
            zone,
        )

    # =====================================================
    # NEGOTIATE
    # =====================================================

    def negotiate(
        self,
        zone_id: str,
        local_intent: MovementIntent,
        local_priority: PriorityFactors,
        peer_intent: MovementIntent,
        peer_priority: PriorityFactors,
    ) -> MovementContract:
        """
        Create a DMC movement contract for a detected conflict.
        """

        contract = self.negotiation.propose_contract(
            zone_id=zone_id,
            intent_a=local_intent,
            factors_a=local_priority,
            intent_b=peer_intent,
            factors_b=peer_priority,
        )

        self.negotiation.accept_contract(
            contract
        )

        return contract

    # =====================================================
    # RESERVE
    # =====================================================

    def reserve_zone(
        self,
        contract: MovementContract,
    ) -> bool:
        """
        Attempt to reserve the conflict zone.

        Returns True if reservation succeeds.
        """

        reservation = (
            self.reservation_manager.reserve(
                contract
            )
        )

        if reservation is None:
            return False

        self.active_contract = contract

        return True

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute_contract(
        self,
    ) -> bool:
        """
        Activate the accepted movement contract.

        Actual robot movement will be connected later
        to the CoppeliaSim/ROS execution layer.
        """

        if self.active_contract is None:
            return False

        self.negotiation.activate_contract(
            self.active_contract
        )

        return (
            self.active_contract.state
            == ContractState.ACTIVE
        )

    # =====================================================
    # ADAPT
    # =====================================================

    def revoke_and_reroute(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        blocked_cells=None,
    ):
        """
        Revoke the current contract and generate a
        shadow route when the current route becomes invalid.
        """

        if self.active_contract is not None:

            self.negotiation.revoke_contract(
                self.active_contract
            )

            self.reservation_manager.revoke(
                self.active_contract.zone_id,
                self.active_contract.contract_id,
            )

            self.active_contract = None

        new_route = (
            self.rerouting.generate_shadow_route(
                start=start,
                goal=goal,
                blocked_cells=blocked_cells,
            )
        )

        return new_route

    # =====================================================
    # STATUS
    # =====================================================

    def status(self) -> Dict:
        """
        Return a compact local controller status.
        """

        contract_state = None

        if self.active_contract is not None:
            contract_state = (
                self.active_contract.state.value
            )

        return {
            "robot_id": self.robot.robot_id,
            "position": (
                self.robot.x,
                self.robot.y,
            ),
            "task": self.robot.current_task,
            "destination": self.robot.destination,
            "contract_state": contract_state,
        }


# =========================================================
# Demonstration
# =========================================================

if __name__ == "__main__":

    warehouse = [
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
    ]

    robot_1 = RobotState(
        robot_id="AMR_1",
        x=0.0,
        y=0.0,
        heading=0.0,
        speed=1.0,
        current_task="Pickup_A",
        destination="Drop_A",
        conflict_zone="Z1",
    )

    controller = DMCController(
        robot=robot_1,
        warehouse_grid=warehouse,
    )

    print("\nDMC INTEGRATED CONTROLLER")
    print("=========================")

    print("Pipeline:")
    print(
        "SENSE → COMMUNICATE → DETECT → "
        "NEGOTIATE → RESERVE → EXECUTE → ADAPT"
    )

    print("\nLocal status:")
    print(controller.status())

    # Example shadow-route recovery.
    route = controller.revoke_and_reroute(
        start=(0, 0),
        goal=(4, 4),
        blocked_cells={(0, 2)},
    )

    print("\nShadow route:")
    print(route)
