---
name: api-evaluator
description: 'Evaluate a Python or FastAPI API for security vulnerabilities, bugs, breaking points, architecture, code quality, and alignment with Domain-Driven Design and CODING_GUIDE.md. Use when asked to review, audit, assess, or evaluate an API, backend service, codebase, architecture, security posture, or DDD and coding-guideline compliance, and to suggest prioritized edits.'
argument-hint: 'Optional scope, such as a package, router, endpoint, or concern to emphasize'
user-invocable: true
disable-model-invocation: false
---

# API Evaluator

Evaluate an API in two strictly ordered phases:

1. **Risk triage:** vulnerabilities, breaking points, and bugs.
2. **Alignment:** architecture, DDD fit, and conformance with the coding guide.

Produce a prioritized report with evidence and concrete suggested edits. Do not
modify files unless the user explicitly asks for the fixes to be applied.

## Ground Rules

- Use the repository's `CODING_GUIDE.md` when present; otherwise use
  `~/.copilot/CODING_GUIDE.md`. Documented, enforced repository conventions take
  precedence over the guide.
- Every finding MUST cite file and line evidence. Label each finding as
  **Verified** (reproduced by a tool, test, or unambiguous code path),
  **Likely** (strong code-reading evidence), or **Needs confirmation**.
- Do not report speculation as fact, and do not inflate style issues into
  security or correctness findings.
- Perform static analysis and local, read-only checks only. Do not send requests
  to deployed environments, exploit vulnerabilities, or run code with staging or
  production credentials.
- If secrets are discovered, report their location and type only. Never repeat
  secret values.
- Ask before installing tools, running commands that require network access, or
  running tests that may contact external services.
- Recommend architecture in proportion to domain complexity. Do not propose DDD
  aggregates, repositories, or events for simple CRUD or utility code.

## Procedure

### 1. Establish Scope

1. Read the guide sections `Configuration and Environment Variables`, `Types and
   Data Modeling`, `Error Handling`, `Architecture`, `Web APIs`, `Data and
   Persistence`, `Testing`, and `Security and Observability`.
2. Identify the application entry point, routers, dependencies, settings model,
   domain modules, persistence adapters, external clients, and tests.
3. Build an endpoint inventory: method, path, authentication and authorization,
   request model, response model, and called use case.
4. Map imports between layers to identify dependency direction.

### 2. Run Available Checks

Run the repository's supported checks in non-mutating form when available:

```sh
just check
```

Otherwise use the equivalents that exist in the project:

```sh
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
```

Never run formatters or fixers that modify files during evaluation. Record
failures as evidence and note any check that could not run.

### 3. Phase 1: Risk Triage

Complete this phase before evaluating style or architecture. Phase 1 findings
always outrank Phase 2 findings.

**Security vulnerabilities** (aligned with the OWASP API Security Top 10):

- Missing object-level authorization: callers can access or modify resources
  they do not own by changing an identifier.
- Broken authentication: weak token validation, missing expiry or audience
  checks, or fake and disabled authentication modes reachable outside local and
  test environments.
- Property-level exposure: response models leaking internal or sensitive fields,
  or request models permitting mass assignment of protected fields.
- Missing function-level authorization on administrative or privileged routes.
- Unrestricted resource consumption: unbounded pagination, uploads, payloads,
  loops, or downstream calls; missing rate or quota protection.
- Injection: SQL built with string formatting, MongoDB filters accepting raw
  request dictionaries or operators, shell commands, templates, or unsafe paths.
- Server-side request forgery from user-controlled URLs.
- Unsafe deserialization such as `pickle`, unsafe YAML loading, or `eval`.
- Security misconfiguration: wildcard CORS with credentials, debug features,
  exposed internal documentation, verbose errors, or permissive defaults.
- Secrets in source, logs, fixtures, committed environment files, or examples.
- Weak cryptography, predictable tokens, or `random` used for security values.
- Unsafe consumption of third-party APIs: unvalidated responses, missing timeouts,
  or trust in external data without boundary validation.

**Breaking points:**

- Blocking I/O, synchronous clients, or CPU-heavy work inside `async` endpoints.
- Missing timeouts, unbounded retries, or retries of non-idempotent operations.
- Clients, sessions, or connections created per request or never closed.
- Unsafe shared mutable state, race conditions, or non-thread-safe singletons.
- Missing transaction boundaries, partial writes, or non-idempotent retries.
- External quota or rate-limit exhaustion without backoff or clear failure.
- Startup that succeeds with missing or invalid configuration.
- N+1 queries and operations whose cost grows with unbounded input.

**Bugs:**

- Failing tests, type errors, or lint findings that indicate incorrect behavior.
- Swallowed exceptions, broad handlers that hide failures, or lost causes.
- Incorrect status codes or error responses that disagree with documented
  contracts.
- Timezone-naive datetimes, unsafe float arithmetic for money, and incorrect
  pagination or boundary handling.
- Logic that contradicts tests, documentation, or the declared API schema.

### 4. Phase 2: Guideline and DDD Alignment

First decide whether DDD is warranted. Evaluate the domain's rules, state
transitions, invariants, and vocabulary, and state the conclusion explicitly.

Then assess:

- **Layering:** domain code importing FastAPI, database clients, HTTP clients, or
  settings; route handlers or dependencies containing business rules.
- **Domain model:** anemic models, missing value objects for meaningful
  primitives, unclear entity identity, aggregates that cannot protect their
  invariants, or interior objects referenced directly from outside the root.
- **Repositories and ports:** persistence exposed to application code, missing
  `Protocol` contracts where substitution or testing needs them, or repositories
  returning storage records instead of aggregate roots.
- **Ubiquitous language:** names in code that disagree with domain terminology
  or with each other.
- **Types:** missing annotations, broad `Any`, unexplained casts, missing
  `Annotated[T, Field(description=...)]`, or missing semantic types.
- **Construction and immutability:** parsing in constructors, absent `from_*`
  factories, mutable value objects, or shared mutable collections.
- **Validation and serialization:** rules placed in the wrong layer, missing
  `to_*` and `from_*` conversions, or schema constraints that do not hold for every
  construction path.
- **Errors:** missing exception hierarchy, translation without `raise ... from`, or
  domain errors leaking transport details.
- **Configuration:** `os.getenv` outside settings, undocumented variables, an
  outdated `.env.example`, or insecure modes not blocked at startup.
- **Testing:** missing failure-path tests, domain logic tested only through HTTP,
  or nondeterministic tests.
- **Tooling:** missing or inconsistent `pyproject.toml`, Ruff, Pyright, Justfile,
  or CI configuration.

Documentation gaps belong in this report briefly. Recommend the
`repository-documentation` skill for detailed documentation remediation.

### 5. Suggest Edits

- For localized fixes, provide a minimal patch or before-and-after snippet.
- For structural changes, provide an incremental migration plan in which each
  step leaves tests passing and preserves the public API unless a breaking change
  is explicitly justified.
- Add or update tests that would catch each Phase 1 finding.
- Do not recommend refactoring code paths that still contain unresolved Critical
  or High Phase 1 findings until those findings are fixed.

## Severity

| Severity | Meaning |
| --- | --- |
| Critical | Exploitable security issue, data loss, or authentication bypass reachable outside local and test environments |
| High | Likely outage, incorrect data, privilege issue, or serious defect under realistic use |
| Medium | Defect or risk with limited impact, or a significant violation of the guide |
| Low | Maintainability improvement or minor guide deviation |
| Info | Observation with no immediate action required |

## Report Format

Present the report in chat. Write it to a file only when asked, using
`docs/reviews/api-evaluation-YYYY-MM-DD.md`.

```markdown
# API Evaluation: <repository or scope>

## Summary
- Overall risk: <Critical | High | Medium | Low>
- DDD fit: <warranted | partially warranted | not warranted> - <one-line reason>
- Top actions: <three highest-value actions>

## Scope and Method
<Files and areas reviewed, checks run and results, and limitations.>

## Phase 1: Vulnerabilities, Breaking Points, and Bugs
| ID | Severity | Category | Location | Finding | Status |
| --- | --- | --- | --- | --- | --- |

### P1-1: <title>
- Evidence:
- Impact:
- Suggested edit:
- Test to add:

## Phase 2: Guideline and DDD Alignment
### Current Architecture
<Brief layer and dependency map; a Mermaid diagram is optional.>

| ID | Priority | Guide Section | Location | Finding |
| --- | --- | --- | --- | --- |

### P2-1: <title>
- Evidence:
- Why it matters:
- Suggested edit or migration step:

## Recommended Sequence
1. <Ordered remediation plan starting with Phase 1>

## Not Evaluated
<Areas not reviewed, checks that could not run, and assumptions.>
```

Finish by asking whether the user wants the suggested edits applied, starting
with Phase 1 findings.
