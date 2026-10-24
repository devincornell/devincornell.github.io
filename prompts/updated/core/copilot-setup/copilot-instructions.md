# Copilot Instructions

These are the always-on team rules. The full standard is
[CODING_GUIDE.md](./CODING_GUIDE.md), located at `~/.copilot/CODING_GUIDE.md`.

- Read `CODING_GUIDE.md` in full once at the start of each session.
- Re-read the relevant section before changing architecture, domain models,
  configuration, serialization, persistence, public APIs, or repository setup.
- Documented, enforced repository conventions take precedence over the guide.

## Tooling

- Use UV, Ruff, Pyright, Pytest, and Just.
- Before finishing, run `just check` or the equivalent format, lint, type-check,
  and test commands.

## Code

- Annotate every function, method, and class attribute. Use `T | None`, built-in
  generics, and `Self`.
- Validate untrusted input with Pydantic models whose fields use
  `Annotated[T, Field(description=...)]`.
- Model domain values with `@dataclass(frozen=True, slots=True)`. Keep domain code
  free of framework and infrastructure imports.
- Put parsing and conversion in `@classmethod` factories named `from_*`; name
  serializers `to_*`.
- Fail fast: index required keys directly, reject invalid input with specific
  exceptions, and never swallow errors.
- Prefer composition, `Protocol`, and `pathlib`. Apply DDD patterns only when the
  domain is complex enough to need them.
- Prefer FastAPI, pydantic-settings, pydantic-ai, Polars, SQLAlchemy Core, and
  PyMongo.
- Write Google-style docstrings for public or non-obvious APIs without repeating
  types.

## Configuration

- Define all settings in a pydantic-settings model; do not call `os.getenv`
  elsewhere.
- Add every new environment variable to `.env.example` with its purpose, type,
  allowed values, default, and permitted environments, and update the README.
- Never commit secrets. Development bypasses such as `AUTH_MODE=fake` must fail
  startup in staging and production.

## Tests

- Add tests for new behavior and bug fixes, including failure paths and invalid
  configuration.
