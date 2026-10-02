# Security and Safety Considerations

## 1. Purpose

The DMC prototype considers communication reliability and safe coordination as part of multi-AMR operation.

The objective is to prevent unsafe movement decisions caused by stale, missing, or inconsistent coordination information.

## 2. Communication Integrity

AMR coordination messages should contain identifiable information such as:

- Robot ID
- Message timestamp
- Position
- Movement intent
- ETA
- Conflict zone
- Contract state

Message timestamps can be used to identify stale coordination information.

## 3. Stale Message Handling

A robot should not blindly rely on outdated peer information.

Conceptual flow:

```text
Receive Message
      ↓
Check Robot ID
      ↓
Check Timestamp
      ↓
Fresh?
  ↙       ↘
 YES       NO
  ↓         ↓
Use       Conservative
Data      Local Decision


### Why this is useful

This gives judges a clear answer if they ask:

> **“What happens if communication fails?”**

Instead of saying *“network irundha work aagum”*, we can show:

**Fresh → normal coordination**  
**Stale → conservative decision**  
**Invalid contract → revoke/re-negotiate**  
**Blocked route → re-route**

One important distinction: **these are proposed safety mechanisms**, not claims that the current prototype has already implemented them.

Commit message:

```text
Add security and safety considerations
