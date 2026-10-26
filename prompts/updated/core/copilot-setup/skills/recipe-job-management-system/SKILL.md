---
name:  recipe-job-management-system
description: "Implementation guide for a reusable job management system for asynchronous operations."
argument-hint: "Implementation details for a reusable job management system for asynchronous operations"
user-invocable: true
disable-model-invocation: false
---

# Job Management System — Implementation Guide

## 1. Overview

Implement a reusable job management system for asynchronous operations, particularly long-running AI tasks.

The system should allow clients to submit operations, receive a unique job ID, and poll for status and completion. Jobs must execute independently of HTTP requests.

**Design principles:**

- **Generic lifecycle:** All job types share the same execution states, timestamps, progress reporting, and retry mechanisms.
- **Separation of concerns:** Job management tracks execution; application-specific code handles inputs, processing, and results.
- **Flexible data storage:** The system tracks optional references to request and result data, rather than storing their contents.
- **Relational extensibility:** Applications may define additional tables with one-to-one relationships to individual jobs.
- **Durable execution:** Jobs must survive API restarts and worker failures.
- **Minimal dependencies:** Prefer PostgreSQL and existing Python infrastructure without requiring a separate message broker initially.

## 2. Database architecture

Create two tables:

| Table | Purpose |
|---|---|
| `jobs` | One record per logical job. Tracks lifecycle, progress, scheduling, and final outcome. |
| `job_attempts` | One record per execution attempt. Tracks execution history, worker identity, and failures. |

**Database placement:** Use the application's existing PostgreSQL database. Prefer a dedicated `job_management` schema, but make this configurable.

The job management component owns these tables. Application-specific tables remain under the application's control.

### 2.1. `jobs` table

```sql
CREATE SCHEMA IF NOT EXISTS job_management;

CREATE TABLE job_management.jobs (
    -- Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type TEXT NOT NULL,
    scope_id TEXT NOT NULL,

    -- Lifecycle
    status TEXT NOT NULL DEFAULT 'queued'
        CHECK (status IN (
            'queued',
            'running',
            'succeeded',
            'failed',
            'canceled'
        )),

    -- Optional references to application data
    request_ref TEXT,
    result_ref TEXT,

    -- Progress
    progress_percent SMALLINT
        CHECK (progress_percent BETWEEN 0 AND 100),
    progress_stage TEXT,

    -- Final error information
    error_code TEXT,
    error_message TEXT,

    -- Execution management
    attempt_count INTEGER NOT NULL DEFAULT 0
        CHECK (attempt_count >= 0),
    max_attempts INTEGER NOT NULL DEFAULT 3
        CHECK (max_attempts >= 1),
    available_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    lease_token UUID,
    lease_expires_at TIMESTAMPTZ,
    cancel_requested_at TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,

    CONSTRAINT job_lease_pair CHECK (
        (lease_token IS NULL) =
        (lease_expires_at IS NULL)
    )
);

CREATE INDEX ix_jobs_scope_created
    ON job_management.jobs (scope_id, created_at DESC);

CREATE INDEX ix_jobs_ready
    ON job_management.jobs (available_at, created_at)
    WHERE status = 'queued';

CREATE INDEX ix_jobs_expired_leases
    ON job_management.jobs (lease_expires_at)
    WHERE status = 'running';
```

**Important implementation details:**

| Field | Expected behavior |
|---|---|
| `id` | Unique identifier used across APIs and application-specific tables. |
| `job_type` | Stable, ideally versioned identifier such as `analysis.v1`. Maps to an execution handler. |
| `scope_id` | Identifies the authorization scope that owns the job. Derived from authenticated context. |
| `request_ref` | Optional reference to request information stored elsewhere. |
| `result_ref` | Optional reference to output stored elsewhere. Set on successful completion when applicable. |
| `attempt_count` | Incremented whenever a worker begins a new attempt. |
| `available_at` | Controls when a queued job is eligible for execution or retry. |
| `lease_token` | Identifies the worker's current execution claim and prevents stale workers from updating the job. |
| `lease_expires_at` | Enables recovery of abandoned jobs. |
| `cancel_requested_at` | Records a cancellation request before the worker has confirmed cancellation. |
| `started_at` | Set when the first execution attempt begins. |
| `finished_at` | Set when a job reaches a terminal state. |

The application must maintain `updated_at` whenever it modifies a job.

The `request_ref` and `result_ref` fields are deliberately generic. They may store resource identifiers, storage keys, or references to external systems.

Neither is required when application-specific tables already represent the relevant relationships.

### 2.2. `job_attempts` table

```sql
CREATE TABLE job_management.job_attempts (
    job_id UUID NOT NULL
        REFERENCES job_management.jobs(id)
        ON DELETE CASCADE,

    attempt_no INTEGER NOT NULL
        CHECK (attempt_no >= 1),

    worker_id TEXT,

    status TEXT NOT NULL
        CHECK (status IN (
            'running',
            'succeeded',
            'failed',
            'interrupted',
            'canceled'
        )),

    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ,

    error_code TEXT,
    error_message TEXT,

    PRIMARY KEY (job_id, attempt_no)
);
```

Every time execution begins, create a new attempt record.

The attempt number corresponds to the parent job's `attempt_count`.

A job may have multiple failed or interrupted attempts but only one overall final outcome.

For example:

| Job | Attempt | Status |
|---|---|---|
| Job A | 1 | failed |
| Job A | 2 | failed |
| Job A | 3 | succeeded |

The parent `jobs` record would have `status = 'succeeded'` and `attempt_count = 3`.

Retain attempt-level errors even when the overall job eventually succeeds.

## 3. Integrating application-specific job tables

Applications may define specialized tables when jobs need additional relationships, parameters, or results.

For example:

```sql
CREATE TABLE public.analysis_jobs (
    job_id UUID PRIMARY KEY
        REFERENCES job_management.jobs(id)
        ON DELETE CASCADE,

    source_id UUID NOT NULL,
    configuration_id UUID,
    output_id UUID
);
```

This is an illustrative table, not a required schema. Its fields would be adapted to the application's actual domain model.

Where the referenced entities exist in the same database, use proper foreign keys.

**Relationship:**

```text
job_management.jobs
    |
    | 1:0..1
    |
    +---- public.analysis_jobs
              |
              +-- source_id
              +-- configuration_id
              +-- output_id

job_management.jobs
    |
    | 1:many
    |
    +---- job_management.job_attempts
```

Each specialized job record uses the generic job ID as both its primary key and a foreign key.

The generic job management component should not query or require knowledge of these specialized tables.

**Creating jobs:** When using the same database, insert the generic job record and specialized record within a single transaction. A job must not become visible to a worker before the specialized record has been committed.

**Execution:** The application-specific handler receives the job ID and loads any required application data.

**Results:** The handler persists output in application-owned storage. It may populate `result_ref` on the parent job, or use an application-specific relationship such as `output_id`.

Avoid maintaining redundant references unless there is a specific reason.

**Consistency:** Application logic must ensure that each job type has the appropriate specialized record when its handler requires one.

## 4. Job lifecycle and execution

Use the following lifecycle:

```text
queued
   |
   v
running ----> succeeded
   |
   +--------> failed
   |
   +--------> queued (retry)
   |
   +--------> canceled

queued -----> canceled
```

Implement these behaviors:

1. **Submission:** Validate application inputs, create a `queued` job, and return its ID. Commit all associated database records before making the job eligible for execution.
2. **Claiming:** Workers atomically select eligible queued jobs using PostgreSQL `FOR UPDATE SKIP LOCKED`. Update the job to `running`, assign a lease token, increment `attempt_count`, and insert the attempt record within one transaction.
3. **Execution:** Dispatch work to the application-specific handler registered for the job's `job_type`. Do not keep database transactions open during AI execution.
4. **Progress:** Allow handlers to report optional progress percentages and stage identifiers. Renew worker leases periodically during long-running operations.
5. **Completion:** Persist application results and mark both the attempt and job as succeeded. Where possible, commit application-owned result records and the job's final state atomically. Only the worker holding the current valid lease may finalize a job.
6. **Failures and retries:** Record attempt-level errors. Retry transient failures with configurable backoff, returning the job to `queued`. Once attempts are exhausted or an error is permanent, mark the job `failed`. Recover expired leases by marking abandoned attempts `interrupted` and rescheduling or failing the parent job.
7. **Cancellation:** Support cooperative cancellation. A running worker should check `cancel_requested_at` and stop when safe. Mark a job `canceled` only when execution has stopped or the queued job has been prevented from starting.

Terminal states are `succeeded`, `failed`, and `canceled`.

Make execution tolerant of duplicate attempts. External AI calls may execute more than once following crashes or lease expiration. Application-specific writes should therefore be idempotent where possible, using the job ID to identify existing output.

## 5. Application-facing API

Expose a minimal, reusable interface.

| Method | Endpoint | Responsibility |
|---|---|---|
| `GET` | `/v1/jobs/{job_id}` | Retrieve status, progress, timestamps, errors, and available references. |
| `GET` | `/v1/jobs` | List jobs accessible to the client, with pagination and optional filters. |
| `POST` | `/v1/jobs/{job_id}/cancel` | Request cancellation. Optional for applications that support it. |

**Job submission should normally use application-specific endpoints**, rather than requiring a generic job creation endpoint.

For example, an application endpoint might create a particular kind of analysis and return:

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "status_url": "/v1/jobs/550e8400-e29b-41d4-a716-446655440000"
}
```

Return HTTP `202 Accepted` when a job has been accepted but is not yet complete.

Polling the status endpoint should return HTTP `200 OK` with a consistent job representation, regardless of whether the job is running, succeeded, or failed.

Example:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "job_type": "analysis.v1",
  "status": "running",
  "progress_percent": 65,
  "progress_stage": "analyzing",
  "request_ref": null,
  "result_ref": null,
  "created_at": "2026-10-23T15:00:00Z",
  "started_at": "2026-10-23T15:00:02Z",
  "finished_at": null,
  "error_code": null,
  "error_message": null
}
```

The generic API does not need to expose worker identifiers, lease tokens, or other internal execution details.

Always enforce authorization through the job's `scope_id`, including when following request and result references.

## 6. Python implementation structure

Separate the job management subsystem from the application's business logic.

| Component | Responsibility |
|---|---|
| `Job` | Typed domain model representing lifecycle state. |
| `JobAttempt` | Typed model representing an execution attempt. |
| `JobRepository` | Database access, atomic claims, updates, and transactions. |
| `JobManager` | Application-facing methods for creating and managing jobs. |
| `JobHandler` | Application-specific execution implementation. |
| `JobWorker` | Claims jobs, invokes handlers, handles retries and failures. |
| FastAPI router | Exposes generic job monitoring endpoints. |

Use SQLAlchemy Core or an equivalent database abstraction, with strongly typed Pydantic models for API requests and responses.

A minimal handler interface could be:

```python
from typing import Protocol
from uuid import UUID

class JobHandler(Protocol):
    async def execute(
        self,
        job_id: UUID,
    ) -> None:
        ...
```

Handlers should load the appropriate application data using the job ID, perform their processing, and persist their results.

The worker remains responsible for managing generic job lifecycle transitions around handler execution.

Additional execution-context capabilities, such as progress reporting and cancellation checks, can be introduced without changing the database architecture.

## 7. Integration requirements

The system should work for both new and existing applications.

**For a new application:** Create the job management tables during initial database setup, register the application's job handlers, and introduce specialized job tables as required.

**For an existing application:** Add the job management tables through database migrations. Connect existing domain entities to job records using application-owned tables or references. Avoid restructuring unrelated application data.

In both cases, reuse the host application's database engine and transaction management. Do not introduce a separate database solely for jobs.

**Minimum acceptance criteria:**

- A submitted job persists and can be retrieved by its ID.
- Application-specific data can be related to a job without being stored in generic payload columns.
- Workers execute jobs independently of API requests.
- Multiple workers cannot simultaneously claim the same queued job.
- Every execution attempt is recorded.
- Failed or abandoned attempts can be retried without corrupting job state.
- A stale worker cannot overwrite a newer execution's state or result.
- Clients can poll until success, failure, or cancellation.
- Job access is restricted to the appropriate authorization scope.
- The system survives API and worker restarts without losing committed jobs.

## 8. Scope and extensibility

Keep the initial implementation focused on job lifecycle management.

Advanced orchestration, job dependencies, webhooks, scheduling priorities, cost tracking, and detailed observability can be introduced later.

The fundamental architectural contract should remain unchanged:

**The generic job management subsystem owns job lifecycle and execution state. The application owns the meaning, inputs, processing logic, and outputs of each job.**

This separation should be preserved even as the application grows or introduces additional AI capabilities.