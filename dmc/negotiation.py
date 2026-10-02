"""
DMC Negotiation Engine
SIH26123 - Dynamic Movement Contract Protocol

Purpose:
    Convert a detected AMR conflict into a temporary
    Dynamic Movement Contract.

Flow:

    Conflict
       ↓
    Priority Evaluation
       ↓
    Contract Proposal
       ↓
    Accept / Reject
       ↓
    Contract State

The contract can later be activated, modified,
revoked or expired by the coordination controller.

Priority factors and weights are prototype parameters.
"""

from typing import Optional
from uuid import uuid4

from models import (
    MovementIntent,
    MovementContract,
    ContractState,
)
from priority import PriorityFactors, PriorityEngine


class NegotiationEngine:
    """
    Handles local negotiation between AMRs competing
    for the same conflict zone.
    """

    def __init__(self):
        self.priority_engine = PriorityEngine()

    # -----------------------------------------------------
    # Contract ID
    # -----------------------------------------------------

    @staticmethod
    def generate_contract_id(
        zone_id: str,
    ) -> str:
        """
        Generate a unique identifier for a movement contract.
        """

        return f"DMC-{zone_id}-{uuid4().hex[:8]}"

    # -----------------------------------------------------
    # Priority
    # -----------------------------------------------------

    def compare_priority(
        self,
        robot_a_id: str,
        factors_a: PriorityFactors,
        robot_b_id: str,
        factors_b: PriorityFactors,
    ) -> tuple[str, float]:

        priority_a = self.priority_engine.calculate(
            robot_a_id,
            factors_a,
        )

        priority_b = self.priority_engine.calculate(
            robot_b_id,
            factors_b,
        )

        return self.priority_engine.select_higher_priority(
            priority_a,
            priority_b,
        )

    # -----------------------------------------------------
    # Contract Proposal
    # -----------------------------------------------------

    def propose_contract(
        self,
        zone_id: str,
        intent_a: MovementIntent,
        factors_a: PriorityFactors,
        intent_b: MovementIntent,
        factors_b: PriorityFactors,
    ) -> MovementContract:
        """
        Compare two competing movement intents and create
        a temporary movement contract.

        The higher-priority robot receives the proposed
        access order.

        This is a local prototype negotiation mechanism.
        """

        selected_robot, selected_score = self.compare_priority(
            intent_a.robot_id,
            factors_a,
            intent_b.robot_id,
            factors_b,
        )

        # Determine the access time of the selected robot.
        if selected_robot == intent_a.robot_id:
            entry_time = intent_a.expected_entry_time
            exit_time = intent_a.expected_exit_time
        else:
            entry_time = intent_b.expected_entry_time
            exit_time = intent_b.expected_exit_time

        contract_id = self.generate_contract_id(
            zone_id
        )

        contract = MovementContract(
            contract_id=contract_id,
            zone_id=zone_id,
            participants=[
                intent_a.robot_id,
                intent_b.robot_id,
            ],
            granted_robot=selected_robot,
            expected_entry_time=entry_time,
            expected_exit_time=exit_time,
            state=ContractState.PROPOSED,
        )

        return contract

    # -----------------------------------------------------
    # Accept Contract
    # -----------------------------------------------------

    @staticmethod
    def accept_contract(
        contract: MovementContract,
    ) -> MovementContract:
        """
        Accept a proposed movement contract.
        """

        if contract.state != ContractState.PROPOSED:
            raise ValueError(
                "Only PROPOSED contracts can be accepted."
            )

        contract.state = ContractState.ACCEPTED

        return contract

    # -----------------------------------------------------
    # Activate Contract
    # -----------------------------------------------------

    @staticmethod
    def activate_contract(
        contract: MovementContract,
    ) -> MovementContract:
        """
        Activate an accepted movement contract.
        """

        if contract.state != ContractState.ACCEPTED:
            raise ValueError(
                "Only ACCEPTED contracts can be activated."
            )

        contract.state = ContractState.ACTIVE

        return contract

    # -----------------------------------------------------
    # Modify Contract
    # -----------------------------------------------------

    @staticmethod
    def modify_contract(
        contract: MovementContract,
        new_entry_time: float,
        new_exit_time: float,
    ) -> MovementContract:
        """
        Modify timing when the warehouse situation changes.
        """

        if contract.state not in (
            ContractState.ACCEPTED,
            ContractState.ACTIVE,
        ):
            raise ValueError(
                "Contract cannot be modified in its current state."
            )

        if new_exit_time <= new_entry_time:
            raise ValueError(
                "Exit time must be greater than entry time."
            )

        contract.expected_entry_time = new_entry_time
        contract.expected_exit_time = new_exit_time
        contract.state = ContractState.MODIFIED

        return contract

    # -----------------------------------------------------
    # Revoke Contract
    # -----------------------------------------------------

    @staticmethod
    def revoke_contract(
        contract: MovementContract,
    ) -> MovementContract:
        """
        Revoke an existing contract.

        Used when a planned route becomes invalid,
        for example because of a blocked aisle or
        changing warehouse conditions.
        """

        if contract.state in (
            ContractState.REVOKED,
            ContractState.EXPIRED,
        ):
            return contract

        contract.state = ContractState.REVOKED

        return contract


# =========================================================
# Demonstration
# =========================================================

if __name__ == "__main__":

    engine = NegotiationEngine()

    intent_1 = MovementIntent(
        robot_id="AMR_1",
        conflict_zone="Z1",
        eta=3.0,
        expected_entry_time=10.0,
        expected_exit_time=14.0,
        planned_path=[
            (1.0, 2.0),
            (2.0, 2.0),
            (3.0, 2.0),
        ],
        destination="Pickup_A",
    )

    intent_2 = MovementIntent(
        robot_id="AMR_2",
        conflict_zone="Z1",
        eta=3.5,
        expected_entry_time=11.0,
        expected_exit_time=15.0,
        planned_path=[
            (5.0, 2.0),
            (4.0, 2.0),
            (3.0, 2.0),
        ],
        destination="Pickup_B",
    )

    factors_1 = PriorityFactors(
        urgency=0.8,
        delay_impact=0.7,
        rerouting_difficulty=0.4,
    )

    factors_2 = PriorityFactors(
        urgency=0.5,
        delay_impact=0.6,
        rerouting_difficulty=0.9,
    )

    contract = engine.propose_contract(
        zone_id="Z1",
        intent_a=intent_1,
        factors_a=factors_1,
        intent_b=intent_2,
        factors_b=factors_2,
    )

    print("\nDMC NEGOTIATION")
    print("===============")
    print(f"Contract ID : {contract.contract_id}")
    print(f"Zone        : {contract.zone_id}")
    print(f"Participants: {contract.participants}")
    print(f"Access robot: {contract.granted_robot}")
    print(f"Entry time  : {contract.expected_entry_time}")
    print(f"Exit time   : {contract.expected_exit_time}")
    print(f"State       : {contract.state.value}")

    engine.accept_contract(contract)
    engine.activate_contract(contract)

    print(f"Active state: {contract.state.value}")

    # Example of contract revocation after a route change.
    engine.revoke_contract(contract)

    print(f"Final state : {contract.state.value}")
