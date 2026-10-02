"""
DMC Conflict-Zone Reservation Module
SIH26123 - Dynamic Movement Contract Protocol

Purpose:
    Manage temporary reservations of shared warehouse
    conflict zones.

Concept:

    Movement Contract
          ↓
    Zone Reservation
          ↓
    Robot Enters
          ↓
    Robot Exits
          ↓
    Reservation Released

The reservation manager prevents two active contracts
from simultaneously owning the same conflict zone.

Reservation timing values are prototype parameters and
must be validated through simulation.
"""

from dataclasses import dataclass
from typing import Dict, Optional
import time

from models import MovementContract, ContractState


@dataclass
class ZoneReservation:
    """
    Temporary ownership of a shared conflict zone.
    """

    zone_id: str
    robot_id: str
    contract_id: str

    entry_time: float
    exit_time: float

    created_at: float

    active: bool = True

    def is_active(self, current_time: Optional[float] = None) -> bool:
        """
        Check whether the reservation is currently active.
        """

        if not self.active:
            return False

        if current_time is None:
            current_time = time.time()

        return (
            self.entry_time
            <= current_time
            <= self.exit_time
        )


class ReservationManager:
    """
    Controls temporary access to shared conflict zones.
    """

    def __init__(self):
        self.reservations: Dict[
            str,
            ZoneReservation
        ] = {}

    # -----------------------------------------------------
    # Check availability
    # -----------------------------------------------------

    def is_zone_available(
        self,
        zone_id: str,
        requested_entry: float,
        requested_exit: float,
    ) -> bool:
        """
        Determine whether a requested time interval conflicts
        with an existing reservation.
        """

        if requested_exit <= requested_entry:
            raise ValueError(
                "Exit time must be greater than entry time."
            )

        existing = self.reservations.get(zone_id)

        if existing is None:
            return True

        if not existing.active:
            return True

        # Time interval overlap check.
        overlap = (
            requested_entry < existing.exit_time
            and existing.entry_time < requested_exit
        )

        return not overlap

    # -----------------------------------------------------
    # Reserve zone
    # -----------------------------------------------------

    def reserve(
        self,
        contract: MovementContract,
    ) -> Optional[ZoneReservation]:
        """
        Create a reservation from an accepted/active contract.

        Returns:
            ZoneReservation if successful.
            None if the zone is already reserved.
        """

        if contract.state not in (
            ContractState.ACCEPTED,
            ContractState.ACTIVE,
            ContractState.MODIFIED,
        ):
            raise ValueError(
                "Only accepted/active/modified contracts "
                "can reserve a zone."
            )

        available = self.is_zone_available(
            contract.zone_id,
            contract.expected_entry_time,
            contract.expected_exit_time,
        )

        if not available:
            return None

        reservation = ZoneReservation(
            zone_id=contract.zone_id,
            robot_id=contract.granted_robot,
            contract_id=contract.contract_id,
            entry_time=contract.expected_entry_time,
            exit_time=contract.expected_exit_time,
            created_at=time.time(),
        )

        self.reservations[
            contract.zone_id
        ] = reservation

        return reservation

    # -----------------------------------------------------
    # Release reservation
    # -----------------------------------------------------

    def release(
        self,
        zone_id: str,
        contract_id: str,
    ) -> bool:
        """
        Release a reservation after the robot leaves
        the conflict zone.
        """

        reservation = self.reservations.get(zone_id)

        if reservation is None:
            return False

        if reservation.contract_id != contract_id:
            return False

        reservation.active = False

        return True

    # -----------------------------------------------------
    # Revoke reservation
    # -----------------------------------------------------

    def revoke(
        self,
        zone_id: str,
        contract_id: str,
    ) -> bool:
        """
        Immediately invalidate a reservation.

        Used when the associated movement contract is revoked.
        """

        return self.release(
            zone_id,
            contract_id,
        )

    # -----------------------------------------------------
    # Current owner
    # -----------------------------------------------------

    def current_owner(
        self,
        zone_id: str,
        current_time: Optional[float] = None,
    ) -> Optional[str]:
        """
        Return the robot currently holding the zone,
        if the reservation is active.
        """

        reservation = self.reservations.get(zone_id)

        if reservation is None:
            return None

        if reservation.is_active(current_time):
            return reservation.robot_id

        return None

    # -----------------------------------------------------
    # Cleanup expired reservations
    # -----------------------------------------------------

    def cleanup_expired(
        self,
        current_time: Optional[float] = None,
    ) -> None:
        """
        Mark expired reservations as inactive.
        """

        if current_time is None:
            current_time = time.time()

        for reservation in self.reservations.values():

            if (
                reservation.active
                and current_time > reservation.exit_time
            ):
                reservation.active = False


# =========================================================
# Demonstration
# =========================================================

if __name__ == "__main__":

    manager = ReservationManager()

    contract = MovementContract(
        contract_id="DMC-Z1-DEMO",
        zone_id="Z1",
        participants=[
            "AMR_1",
            "AMR_2",
        ],
        granted_robot="AMR_1",
        expected_entry_time=10.0,
        expected_exit_time=14.0,
        state=ContractState.ACCEPTED,
    )

    reservation = manager.reserve(contract)

    print("\nDMC RESERVATION MANAGER")
    print("=======================")

    if reservation:
        print("Reservation created")
        print(f"Zone       : {reservation.zone_id}")
        print(f"Robot      : {reservation.robot_id}")
        print(f"Contract   : {reservation.contract_id}")
        print(f"Entry time : {reservation.entry_time}")
        print(f"Exit time  : {reservation.exit_time}")
    else:
        print("Zone is already reserved.")

    owner = manager.current_owner(
        "Z1",
        current_time=12.0,
    )

    print(f"Current owner: {owner}")

    released = manager.release(
        "Z1",
        "DMC-Z1-DEMO",
    )

    print(f"Reservation released: {released}")

    print(
        f"Owner after release: "
        f"{manager.current_owner('Z1', 12.0)}"
    )
