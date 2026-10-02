"""
DMC Peer-to-Peer Communication Module
SIH26123 - Dynamic Movement Contract Protocol

Purpose:
    Provide a lightweight prototype communication layer for
    decentralized AMR coordination.

Functions:
    - Publish local robot state
    - Exchange movement intent
    - Track peer messages
    - Check message freshness
    - Detect stale communication
    - Provide a conservative communication state

This is a local simulation/message-bus abstraction.
It does not represent a real wireless networking stack.

Freshness thresholds are prototype parameters and must
be validated during simulation.
"""

import time
from typing import Dict, List, Optional

from models import (
    RobotState,
    MovementIntent,
    MovementContract,
    PeerMessage,
)


class CommunicationManager:
    """
    Lightweight peer-to-peer communication manager.

    Each robot can publish a message and receive messages
    from other simulated AMRs.
    """

    def __init__(
        self,
        freshness_threshold: float = 2.0,
    ):
        """
        freshness_threshold:
            Maximum acceptable message age in seconds.

        This is a prototype parameter, not an official
        SIH requirement.
        """

        if freshness_threshold <= 0:
            raise ValueError(
                "freshness_threshold must be positive."
            )

        self.freshness_threshold = freshness_threshold

        # Latest known message from each peer.
        self.peer_messages: Dict[
            str,
            PeerMessage
        ] = {}

    # -----------------------------------------------------
    # Publish message
    # -----------------------------------------------------

    def create_message(
        self,
        robot_state: RobotState,
        movement_intent: Optional[MovementIntent] = None,
        contract_id: Optional[str] = None,
    ) -> PeerMessage:
        """
        Create a coordination message containing local
        state, optional intent and optional contract ID.
        """

        message_type = "STATE"

        if movement_intent is not None:
            message_type = "STATE_INTENT"

        if contract_id is not None:
            message_type = "CONTRACT_UPDATE"

        return PeerMessage(
            sender_id=robot_state.robot_id,
            message_type=message_type,
            robot_state=robot_state,
            movement_intent=movement_intent,
            contract_id=contract_id,
            timestamp=time.time(),
        )

    # -----------------------------------------------------
    # Receive message
    # -----------------------------------------------------

    def receive_message(
        self,
        message: PeerMessage,
    ) -> None:
        """
        Store the latest message received from a peer.

        A message from a robot replaces its previous state.
        """

        self.peer_messages[
            message.sender_id
        ] = message

    # -----------------------------------------------------
    # Message freshness
    # -----------------------------------------------------

    def is_fresh(
        self,
        message: PeerMessage,
        current_time: Optional[float] = None,
    ) -> bool:
        """
        Determine whether a peer message is fresh enough
        for normal coordination.
        """

        if current_time is None:
            current_time = time.time()

        age = current_time - message.timestamp

        return age <= self.freshness_threshold

    # -----------------------------------------------------
    # Communication state
    # -----------------------------------------------------

    def communication_state(
        self,
        robot_id: str,
        current_time: Optional[float] = None,
    ) -> str:
        """
        Return a simple communication state.

        FRESH:
            Peer information is recent.

        STALE:
            Information exists but is older than the
            configured freshness threshold.

        LOST:
            No message is currently available.
        """

        message = self.peer_messages.get(robot_id)

        if message is None:
            return "LOST"

        if self.is_fresh(
            message,
            current_time,
        ):
            return "FRESH"

        return "STALE"

    # -----------------------------------------------------
    # Get usable peer information
    # -----------------------------------------------------

    def get_peer_message(
        self,
        robot_id: str,
        allow_stale: bool = False,
    ) -> Optional[PeerMessage]:
        """
        Retrieve peer information.

        By default, stale information is not returned for
        normal coordination.
        """

        message = self.peer_messages.get(robot_id)

        if message is None:
            return None

        if allow_stale:
            return message

        if not self.is_fresh(message):
            return None

        return message

    # -----------------------------------------------------
    # Get all fresh peers
    # -----------------------------------------------------

    def get_fresh_peers(self) -> List[PeerMessage]:
        """
        Return all currently fresh peer messages.
        """

        return [
            message
            for message in self.peer_messages.values()
            if self.is_fresh(message)
        ]

    # -----------------------------------------------------
    # Remove stale information
    # -----------------------------------------------------

    def remove_stale_messages(self) -> int:
        """
        Remove stale peer information.

        Returns:
            Number of removed messages.
        """

        stale_robot_ids = [
            robot_id
            for robot_id, message
            in self.peer_messages.items()
            if not self.is_fresh(message)
        ]

        for robot_id in stale_robot_ids:
            del self.peer_messages[robot_id]

        return len(stale_robot_ids)


# =========================================================
# Demonstration
# =========================================================

if __name__ == "__main__":

    communication = CommunicationManager(
        freshness_threshold=2.0
    )

    robot_1 = RobotState(
        robot_id="AMR_1",
        x=2.0,
        y=4.0,
        heading=0.0,
        speed=1.0,
        current_task="Pickup_A",
        destination="Drop_A",
        conflict_zone="Z1",
    )

    intent_1 = MovementIntent(
        robot_id="AMR_1",
        conflict_zone="Z1",
        eta=3.0,
        expected_entry_time=10.0,
        expected_exit_time=14.0,
        planned_path=[
            (2.0, 4.0),
            (3.0, 4.0),
            (4.0, 4.0),
        ],
        destination="Drop_A",
    )

    # Create a P2P coordination message.
    message = communication.create_message(
        robot_state=robot_1,
        movement_intent=intent_1,
    )

    # Simulate another AMR receiving it.
    communication.receive_message(message)

    print("\nDMC COMMUNICATION MANAGER")
    print("=========================")

    print(f"Sender       : {message.sender_id}")
    print(f"Message type : {message.message_type}")
    print(
        f"Communication: "
        f"{communication.communication_state('AMR_1')}"
    )

    peer = communication.get_peer_message(
        "AMR_1"
    )

    if peer:
        print(
            f"Received ETA : "
            f"{peer.movement_intent.eta:.2f}s"
        )

    print(
        f"Fresh peers  : "
        f"{len(communication.get_fresh_peers())}"
    )
