"""
DMC Core Data Models
SIH26123 - Dynamic Movement Contract Protocol

This module defines the shared data structures used by the
decentralized AMR coordination system.

The fields are proposed implementation structures based on
the project architecture and are not additional SIH requirements.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple
import time


# ---------------------------------------------------------
# Contract States
# ---------------------------------------------------------

class ContractState(Enum):
    PROPOSED = "PROPOSED"
    ACCEPTED = "ACCEPTED"
    ACTIVE = "ACTIVE"
    MODIFIED = "MODIFIED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


# ---------------------------------------------------------
# Robot State
# ---------------------------------------------------------

@dataclass
class RobotState:
    """
    Current local state of an AMR.
    """

    robot_id: str

    # Position
    x: float
    y: float

    # Motion
    heading: float
    speed: float

    # Task information
    current_task: str
    destination: str

    # Planned movement
    planned_path: List[Tuple[float, float]] = field(
        default_factory=list
    )

    # Proposed prototype parameter
    battery_level: float = 100.0

    # Communication freshness
    last_message_time: float = field(
        default_factory=time.time
    )

    # Current conflict zone
    conflict_zone: Optional[str] = None


# ---------------------------------------------------------
# Movement Intent
# ---------------------------------------------------------

@dataclass
class MovementIntent:
    """
    Short-horizon movement information exchanged
    between nearby AMRs.
    """

    robot_id: str

    conflict_zone: Optional[str]

    eta: float

    expected_entry_time: float
    expected_exit_time: float

    planned_path: List[Tuple[float, float]]

    destination: str

    timestamp: float = field(
        default_factory=time.time
    )


# ---------------------------------------------------------
# DMC Priority
# ---------------------------------------------------------

@dataclass
class PriorityFactors:
    """
    Factors used by the proposed context-aware priority model.

    U = Task urgency
    D = Delay impact
    R = Re-routing difficulty
    """

    urgency: float
    delay_impact: float
    rerouting_difficulty: float

    # Proposed weights.
    # These must be tuned during validation.
    w_urgency: float = 1.0
    w_delay: float = 1.0
    w_reroute: float = 1.0

    def score(self) -> float:
        """
        Calculate proposed DMC priority score.

        P = w1*U + w2*D + w3*R
        """

        return (
            self.w_urgency * self.urgency
            + self.w_delay * self.delay_impact
            + self.w_reroute * self.rerouting_difficulty
        )


# ---------------------------------------------------------
# Movement Contract
# ---------------------------------------------------------

@dataclass
class MovementContract:
    """
    Temporary agreement for access to a shared conflict zone.
    """

    contract_id: str

    zone_id: str

    participants: List[str]

    # Robot allowed to enter first
    granted_robot: str

    expected_entry_time: float
    expected_exit_time: float

    state: ContractState = ContractState.PROPOSED

    created_at: float = field(
        default_factory=time.time
    )

    # Validity period of the contract
    valid_until: Optional[float] = None

    def is_valid(self) -> bool:
        """
        Check whether the contract is still temporally valid.
        """

        if self.valid_until is None:
            return True

        return time.time() < self.valid_until


# ---------------------------------------------------------
# Communication Message
# ---------------------------------------------------------

@dataclass
class PeerMessage:
    """
    Message exchanged between AMRs.
    """

    sender_id: str

    message_type: str

    robot_state: RobotState

    movement_intent: Optional[MovementIntent] = None

    contract_id: Optional[str] = None

    timestamp: float = field(
        default_factory=time.time
    )

    def age(self) -> float:
        """
        Return message age in seconds.
        """

        return time.time() - self.timestamp
