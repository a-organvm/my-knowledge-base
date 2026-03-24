# Idempotent Write Semantics in Checkpoint-Based State Machines

**Origin:** Backflow from `contrib--langchain-langgraph` (ORGAN-IV contribution engine)
**Deposited:** 2026-03-23
**Organ:** I (Theoria)
**Type:** Theory extraction

---

## Abstract

LangGraph's `put_writes` checkpoint primitive guarantees that replaying a write with the same `(task_id, idx)` pair produces no duplicate entries. This is not an implementation detail — it is a **formal property** required for restart-safety in any checkpoint-based execution system. This note extracts the mathematical invariant, proves its necessity, and generalizes it beyond LangGraph to any system where execution may be interrupted and retried.

## 1. The Concrete Implementation

### 1.1 LangGraph's put_writes Contract

In LangGraph's checkpointer interface, `put_writes` persists intermediate state produced during graph node execution:

```python
def put_writes(config: RunnableConfig, writes: Sequence[tuple[str, Any]], task_id: str) -> None
```

Each write is identified by the tuple `(task_id, idx)` where `idx` is the positional index within the `writes` sequence. The contract states:

**If `put_writes` is called twice with the same `(config, writes, task_id)`, the resulting checkpoint state is identical to a single invocation.**

### 1.2 The Contributed Test (PR #7237)

The test `test_put_writes_idempotent_across_restart` verifies:

1. Execute `put_writes(config, writes, task_id)` — checkpoint state after first call is *S1*
2. Execute `put_writes(config, writes, task_id)` again (simulating replay after crash) — checkpoint state is *S2*
3. Assert *S1 = S2*

This is the idempotency test: *f(f(x)) = f(x)*.

## 2. Formal Property

### 2.1 Definition

Let *C* be a checkpoint store and *w = (config, writes, task_id)* be a write operation. Let *C(w)* denote the state of the store after applying *w*. The **idempotent write property** states:

```
For all w: C(w) = C(w; w)
```

where *C(w; w)* denotes applying *w* twice sequentially.

More precisely, let *apply: Store x Write -> Store* be the state transition function. Then:

```
apply(apply(S, w), w) = apply(S, w)    for all S, w
```

This is the standard algebraic definition of idempotence for the operation *apply(-, w)*.

### 2.2 The Deduplication Key

Idempotence requires a **deduplication key** — a function *k: Write -> K* such that:

- If *k(w1) = k(w2)*, the store treats *w1* and *w2* as the same logical write
- The second application is suppressed (upsert semantics) rather than appended

In LangGraph: *k(w) = (task_id, idx)*. This is a composite natural key derived from the execution context (which task produced the write) and the write's position within the task's output.

### 2.3 Why Natural Keys, Not UUIDs

A common alternative is to assign a UUID to each write and use it for deduplication. This fails for restart safety:

- After a crash, the retried process generates a **new UUID** for the same logical write
- The store sees two distinct keys and creates a duplicate
- The checkpoint now contains phantom state

Natural keys derived from the execution context (task identity + position) survive process restarts because they are **deterministic functions of the computation**, not of the process instance.

## 3. Necessity Proof

### 3.1 Claim

In any system where:
1. Execution is divided into discrete tasks
2. Tasks produce writes to a persistent store
3. A task may be interrupted and retried from the beginning

idempotent writes are **necessary** for correctness.

### 3.2 Proof

Assume writes are not idempotent. Then there exists some write *w* such that *apply(apply(S, w), w) != apply(S, w)*.

Consider the execution sequence:
1. Task *T* begins, produces write *w*, calls `put_writes`
2. The write succeeds: store transitions from *S* to *apply(S, w)*
3. Process crashes before *T* records its completion
4. On restart, *T* is retried from the beginning (it has no record of having completed)
5. *T* produces write *w* again, calls `put_writes`
6. Store transitions from *apply(S, w)* to *apply(apply(S, w), w)*

By assumption, *apply(apply(S, w), w) != apply(S, w)*. The store now holds state that would never have been produced by a single clean execution of *T*. This is **phantom state** — an artifact of the retry, not of the computation.

Downstream consumers of the checkpoint observe state that no correct execution could produce. The system is inconsistent. QED.

### 3.3 Corollary

The idempotent write property is equivalent to requiring that the `put_writes` operation is an **idempotent element** in the monoid of store transformations. The identity element (no-op) is trivially idempotent; `put_writes` must be as well.

## 4. Generalization

### 4.1 Beyond LangGraph

Any checkpoint system exhibits this pattern:

| System | Write operation | Deduplication key |
|--------|----------------|-------------------|
| LangGraph | `put_writes` | `(task_id, idx)` |
| ORGANVM promotion | `promote(repo, target_state)` | `(repo_id, target_state)` |
| Database WAL | `write(page_id, data, LSN)` | `(page_id, LSN)` |
| Event sourcing | `append(stream, event, expected_version)` | `(stream_id, version)` |
| Saga orchestrator | `complete_step(saga_id, step_id)` | `(saga_id, step_id)` |

In each case:
- The deduplication key is a **deterministic function** of the computation context
- The write operation is idempotent with respect to that key
- Retry safety follows directly

### 4.2 Connection to Forward-Only FSMs

Idempotent writes and forward-only state machines are **dual properties** of the same governance principle:

- **Forward-only FSMs** ensure that state transitions are monotonic (no rollbacks)
- **Idempotent writes** ensure that state transitions are confluent (retries produce no duplicates)

Together they guarantee: **the state of any entity is a deterministic function of the set of intended transitions, regardless of the order or multiplicity of their application.** This is the CRDT (conflict-free replicated data type) property applied to lifecycle governance.

### 4.3 The Design Decision

When building a checkpoint or state persistence layer, the choice is:

1. **Application-level idempotence:** The caller is responsible for not calling `put_writes` twice. This is fragile — it requires the caller to track its own completion state, which is the very state that may be lost in a crash.

2. **Store-level idempotence:** The store itself enforces deduplication via natural keys. This is robust — the store absorbs retries transparently.

LangGraph chose option 2. This is the correct choice for any system where the execution environment is unreliable (process crashes, OOM kills, network partitions). The contributed test (PR #7237) makes this implicit contract explicit and verifiable.

---

**References:**
- LangGraph checkpointer interface: `libs/checkpoint/langgraph/checkpoint/base/__init__.py`
- PR #7237: `feat: add restart-safety coverage for put_writes idempotency`
- Issue #7201: checkpoint restart-safety gap
- Contribution workspace: `contrib--langchain-langgraph`, session 01 (2026-03-21)
- ORGANVM `governance-rules.json`, Article VI (promotion state machine — dual property)
