# Dynamic Movement Contract (DMC)

## Overview

DMC (Dynamic Movement Contract) is a proposed decentralized coordination protocol for Autonomous Mobile Robots (AMRs) operating in smart warehouse environments.

The system focuses on local robot-to-robot coordination, conflict resolution, temporary movement contracts, and dynamic re-routing.

## Problem

In a multi-AMR warehouse, robots may encounter:

- Overlapping paths
- Narrow intersections
- Shared conflict zones
- Blocked aisles
- Communication delays or temporary communication loss
- Unnecessary stopping and waiting

Traditional centralized or stop-and-wait coordination can introduce delays and coordination dependencies.

## Proposed Approach

DMC enables nearby AMRs to exchange their current state and short-horizon movement intent.

Before entering a shared conflict zone, robots can negotiate a temporary movement contract.

### Coordination Flow

Sense → Communicate → Detect → Negotiate → Reserve → Execute → Adapt

## Core Components

- Peer-to-peer robot communication
- Robot state exchange
- Movement intent sharing
- Conflict-zone detection
- Dynamic movement contracts
- Temporary zone reservation
- Contract renewal and revocation
- Dynamic path re-routing
- Fleet monitoring

## Target Scenario

The proposed prototype targets a dynamic warehouse scenario containing at least three AMRs with overlapping paths and shared intersections.

## Validation Approach

The proposed DMC approach will be compared with a traditional stop-and-wait baseline.

The evaluation will consider:

- Inter-robot collision count
- Total task completion time
- Waiting time
- Re-routing events

## SIH Success Criteria

The official problem statement specifies:

- Zero inter-robot collisions
- Minimum 20% reduction in total task completion time compared with traditional stop-and-wait

These are official success criteria. They are not claimed as achieved results until the prototype is measured.

## Project Status

Prototype development in progress.

Simulation and measured results will be added after implementation and testing.
