# Problem Analysis — SIH26123

## Problem Statement

SIH26123 focuses on decentralized coordination of Autonomous Mobile Robots (AMRs) operating in smart warehouse environments.

The objective is to coordinate a fleet of at least three AMRs in a dynamic warehouse while handling overlapping paths, conflict zones, blocked aisles and communication limitations.

## 1. Core Problem

A multi-robot warehouse environment can contain several robots moving simultaneously through shared spaces.

When two or more robots require the same narrow intersection or conflict zone, independent movement decisions can result in:

- Collision risk
- Deadlock
- Unnecessary waiting
- Increased task completion time
- Re-routing requirements
- Coordination problems during communication loss or delay

## 2. Root Cause

The core coordination challenge is that multiple AMRs may independently plan movements while sharing the same physical warehouse space.

A robot needs awareness of:

- Its current position
- Its intended movement
- Estimated arrival time
- Nearby robot movements
- Shared conflict zones
- Available alternate routes

Without timely coordination, multiple robots may compete for the same space.

## 3. Users and Operating Environment

### Primary Environment

- Smart warehouses
- Aisles
- Narrow intersections
- Shared movement zones
- Pickup and delivery locations
- Dynamic obstacles or blocked paths

### Main System Actors

- AMR 1
- AMR 2
- AMR 3 and additional AMRs
- Edge coordination modules
- Fleet monitoring dashboard

## 4. Official Requirements

The official problem statement specifies the following major capabilities:

### Decentralized Communication

AMRs should support peer-to-peer communication for sharing localization information.

### Dynamic Multi-Agent Conflict Resolution

The system should handle conflicts such as deadlocks and collisions at narrow intersections or choke points in real time.

### Task Allocation and Re-routing

The system should support reassignment of pickup points or route changes when an aisle becomes blocked.

### Edge-Based Processing

Multi-agent path planning should execute on edge hardware such as Raspberry Pi or Jetson Nano-class platforms.

### Fleet Dashboard

The expected solution includes a lightweight dashboard showing real-time robot positions and battery information.

## 5. Official Success Criteria

The problem statement specifies:

- Zero inter-robot collisions
- Minimum 20% reduction in total task completion time compared with traditional stop-and-wait coordination

These are evaluation criteria and are not claimed as achieved results in the current project.

## 6. Proposed Interpretation

The proposed DMC approach addresses the coordination problem by allowing nearby AMRs to exchange movement intent and negotiate temporary access to shared conflict zones.

Instead of:

Conflict → Stop → Wait → Move

the proposed approach follows:

Conflict Prediction → Negotiation → Reservation → Movement → Adaptation

## 7. Key Scenarios

### Scenario A — Shared Intersection

Two AMRs approach the same intersection.

The system detects overlapping movement intentions and coordinates access to the conflict zone.

### Scenario B — Three-Robot Conflict

Three AMRs approach a shared zone with different task priorities and arrival times.

The coordination layer evaluates the local situation and establishes an execution order.

### Scenario C — Blocked Aisle

An AMR detects that its planned route is unavailable.

The route is recalculated and the affected movement contract can be modified or revoked.

### Scenario D — Communication Delay

A robot receives stale or delayed information from another AMR.

The coordination layer should avoid relying on outdated movement information and switch to a conservative local decision when required.

## 8. Proposed System Requirements

The following are proposed engineering requirements for the prototype, not additional official SIH requirements:

- Support at least three simulated AMRs
- Detect shared conflict zones
- Exchange robot state and movement intent
- Calculate estimated arrival time
- Create temporary movement contracts
- Reserve shared zones
- Handle contract revocation
- Generate alternate routes
- Record validation metrics

## 9. Validation Metrics

The prototype will record:

| Metric | Purpose |
|---|---|
| Collision Count | Safety evaluation |
| Task Completion Time | Overall performance |
| Waiting Time | Coordination efficiency |
| Re-routing Events | Dynamic recovery |
| Contract Conflicts | Coordination behaviour |

## 10. Baseline Comparison

### Traditional Stop-and-Wait

```text
Conflict Detected
       ↓
      STOP
       ↓
      WAIT
       ↓
      MOVE
