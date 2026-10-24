---
name: repository-documentation
description: 'Create, revise, review, or audit Python repository documentation. Use when writing or updating README files, setup instructions, .env.example files, configuration documentation, developer onboarding, runbooks, API documentation, or Architecture Decision Records. Ensures documentation follows CODING_GUIDE.md.'
argument-hint: 'Describe the repository documentation to create, update, or audit'
user-invocable: true
disable-model-invocation: false
---

# Repository Documentation

Create and maintain documentation that lets a new contributor configure, run,
test, and operate a repository without private verbal instructions.

## When To Use

Use this skill when the task involves:

- `README.md`, developer onboarding, installation, or local development setup.
- `.env.example`, configuration settings, secrets, authentication modes, or
  environment variables such as `DISABLE_AUTH` and `FAKE_USER`.
- Runbooks, deployment notes, operational procedures, or external dependencies.
- Public API documentation or compatibility notes.
- Architecture Decision Records (ADRs).
- Reviewing whether repository documentation is complete or current.

Use the repository's `CODING_GUIDE.md` when present; otherwise use
`~/.copilot/CODING_GUIDE.md`. Read its `Documentation` and `Configuration and
Environment Variables` sections before editing. Also read the sections relevant
to the specific documentation being changed, such as `Web APIs`, `Data and
Persistence`, or `Security and Observability`.

## Procedure

1. Locate the existing documentation, application settings model, `.env.example`,
   package configuration, `Justfile`, CI workflow, and relevant tests.
2. Treat the typed settings model and executable project configuration as the
   source of truth. Do not document inferred behavior without verifying it.
3. Identify omissions, stale instructions, ambiguous configuration, undocumented
   prerequisites, and examples that might expose secrets or weaken security.
4. Make the smallest documentation change that accurately describes the current
   repository behavior. Update code only when the task explicitly includes a
   behavior or configuration fix.
5. Keep commands executable, paths accurate, and examples safe to copy locally.
6. Validate all documented commands and configuration examples that the local
   environment can run. State clearly what could not be validated.

## README Requirements

When creating or materially revising a `README.md`, include the applicable items:

- Project purpose and supported use cases.
- Prerequisites, supported Python version, and installation command.
- Local commands to run, format, lint, type-check, and test the project.
- Configuration precedence and a link to `.env.example`.
- Common local configuration modes, particularly authentication.
- External service dependencies and how a contributor obtains non-secret access.
- Links to deployment, operations, API, or architecture documentation when they
  exist.

Do not copy configuration tables or example values that will drift from the
settings model. Link to `.env.example` for the complete inventory.

## Environment Variable Contract

Repositories using runtime environment variables must maintain a committed
`.env.example` with safe, non-secret values. For every application-owned variable,
document immediately above it:

- Its purpose.
- Type and allowed values.
- Whether it is required and its default, if any.
- Environments where it is permitted.
- Whether it is secret.
- Dependencies or conflicts with other settings.

Use one explicit mode rather than several interacting flags when possible. For
example, prefer `AUTH_MODE=oidc|fake|disabled` to a combination of
`DISABLE_AUTH` and `FAKE_USER`.

Document fake or disabled authentication precisely: who it impersonates, when it
is enabled, and why it cannot start in staging or production. Do not recommend
or document insecure production workarounds.

Use this template when adding an environment variable:

```dotenv
# Human-readable purpose.
# Type: string | integer | boolean | enum
# Allowed: value-a, value-b
# Required: yes | no
# Default: safe-default | none
# Environments: local, test
# Secret: yes | no
# Required when: OTHER_SETTING=value-a
SETTING_NAME=safe-example
```

For variables that are absent rather than optional, say so explicitly. Do not
invent a default merely to make the example look complete.

## Documentation Quality Rules

- Explain intent, constraints, and consequences; do not restate source code.
- Use consistent names with the settings model, CLI, API, and `Justfile`.
- Keep setup instructions linear and copyable.
- Do not include real credentials, internal URLs that are not intended for new
  contributors, personally identifying sample data, or production identifiers.
- State platform-specific steps only when they are truly required.
- Update documentation in the same change as configuration, behavior, setup, or
  operational changes.
- Add an ADR for significant, durable architectural decisions. Record context,
  decision, consequences, and alternatives considered.

## Audit Checklist

For a documentation review, report findings by severity and include the affected
file and missing or stale information. Check:

- README setup works from a clean checkout.
- Every settings field is represented in `.env.example`.
- `.env.example` includes no secrets and no production-only values.
- Authentication, fake-user, debug, and disablement modes are documented and
  blocked in staging and production.
- README commands agree with `Justfile`, `pyproject.toml`, and CI.
- Required external services and access paths are documented.
- Public behavior, API, migration, deployment, and operational changes have
  matching documentation.
- Runbooks contain observable symptoms, safe actions, escalation details, and
  rollback guidance where appropriate.

## Completion

Before finishing, verify the changed Markdown has no diagnostics. Run the
relevant documented commands when they are available. In the final summary,
state which sources of truth were checked and which command or configuration
examples were validated.
