# GitHub Copilot Team Setup

This folder documents a possible GitHub Copilot setup the team could use. The
distributable files are in [../team/copilot-setup](../team/copilot-setup):

- `CODING_GUIDE.md`: the complete engineering standard. It is the durable reference for our Python, API, testing, configuration, and architecture rules.
- `copilot-instructions.md`: a short, always-on set of rules that tells Copilot to apply the standard and use our required tooling.
- `skills/repository-documentation/SKILL.md`: an on-demand procedure for creating and reviewing repository documentation.
- `skills/api-evaluator/SKILL.md`: an on-demand procedure for evaluating a Python or FastAPI API for vulnerabilities, bugs, and alignment with our architecture and coding standards.
- `copilot-setup-mac.md`: the macOS installation guide.

## What Each File Does

### `CODING_GUIDE.md`

This is the team's complete engineering standard. It defines the reasoning and
implementation rules behind our code: type modelling, validation, domain
boundaries, API design, persistence, tests, configuration, and security. It is
deliberately detailed, so it is a reference rather than context Copilot must
receive in full for every request.

The always-on instructions and both skills tell Copilot when it must read this
guide. Repository-specific rules take precedence when they conflict with it.

### `copilot-instructions.md`

This is the short set of rules that Copilot loads into every personal chat
session. It establishes the baseline: read the guide at the beginning of a
session, use UV, Ruff, Pyright, Pytest, and Just, enforce our typing and
validation conventions, keep domain code independent of infrastructure, and
test new behavior and failures.

It stays concise because it affects every request. The detailed rationale and
exceptions belong in `CODING_GUIDE.md` so the common prompt context is not
overloaded.

### `skills/repository-documentation/SKILL.md`

This skill is for documentation work: README files, onboarding, setup guides,
runbooks, API documentation, `.env.example`, and Architecture Decision
Records. It tells Copilot to verify documentation against the settings model,
project configuration, CI, and tests rather than document assumptions. It also
defines the information that environment-variable documentation must include
and how to validate documentation changes.

Use it explicitly with `/repository-documentation`, or describe a documentation
task in chat and Copilot can load it when the request matches its description.

### `skills/api-evaluator/SKILL.md`

This skill provides a read-only API review workflow. It first assesses concrete
risk: vulnerabilities, breaking points, and functional bugs. Only after that
does it assess DDD, architecture, code quality, and conformance with the coding
guide. Its report format requires severity, evidence, confidence, and specific
recommended edits; it does not modify code unless asked.

Use it explicitly with `/api-evaluator`, or ask Copilot to evaluate an API,
router, endpoint, backend service, or security posture.

### `copilot-setup-mac.md`

This is the installation runbook for macOS. It lists the required paths under
`~/.copilot`, provides Terminal and Finder installation steps, explains how to
verify that skills appear in Copilot Chat, and covers the most common discovery
and update problems.

## How Copilot Uses These Files

GitHub Copilot in VS Code loads customizations from defined locations. Their location determines when and where Copilot applies them.

| Customization | Location | Behavior |
| --- | --- | --- |
| Personal instructions | `~/.copilot/copilot-instructions.md` | Loaded for the user's Copilot sessions. Use this for concise, broadly applicable working rules. It's part of the context for every GH Copilot chat session, regardless of whether you're connected to a repo or a folder.|
| Personal coding guide | `~/.copilot/CODING_GUIDE.md` | A detailed reference read when the instructions or a skill direct Copilot to it. |
| Personal skill | `~/.copilot/skills/<skill-name>/SKILL.md` | Discovered by Copilot for that user. Copilot can load it when the request matches its description, and users can invoke it from any GH Copilot chat. |
| Repository instructions | `.github/copilot-instructions.md` | Loaded when Copilot works in that repository. Everyone receives the same version through Git when they clone the repo, unless the .github folder is gitignored. |
| Repository skill | `.github/skills/<skill-name>/SKILL.md` | Available while working in that repository, and shared through Git when they clone the repo, unless the .github folder is gitignored. |

`~` is the current macOS user's home directory, such as
`/Users/Santiago`. The `.copilot` folder is hidden in Finder because its name begins
with a period.

## Why the Locations Matter

Copilot does not search arbitrary folders for instructions or skills. It, by design, relies
on these known locations to distinguish a user's personal defaults from rules
that belong to a specific repository.

- Put cross-project preferences and reusable skills in `~/.copilot`. They are
  available when a user opens any repository in VS Code.
- Put rules that must travel with a repository in `.github`. They are versioned,
  reviewed, and updated with the codebase rather than separately on each Mac. *And don't gitignore the folder.*
- Keep always-on instructions brief. They guide every request; detailed
  material belongs in a guide or a skill so Copilot loads it only when relevant.

The personal setup in this repository is useful when someone wants these two
skills and the engineering guide across many projects. A repository should
still keep its own `.github` customizations when a rule is project-specific.

## How Skills Work

A skill is a Markdown file with YAML frontmatter and a repeatable working
procedure. Its description tells Copilot when the skill is relevant. For
example, a request to review an API can cause Copilot to load `api-evaluator`;
a request to improve a README can cause it to load `repository-documentation`.

For a skill to be discovered correctly:

1. The file must be named `SKILL.md`.
2. It must be placed in `~/.copilot/skills/<skill-name>/` for a personal skill,
   or `.github/skills/<skill-name>/` for a repository skill.
3. The folder name must exactly match the frontmatter `name` value.

After installation, typing `/` in Copilot Chat should show the available skills.
If a newly added skill does not appear, restart VS Code.

### Example

`/repository-documentation Write the README for this repo, including Mermaid diagrams of the API Architeture.`

This will use the skill `repository-documentation` and Copilot will know it's instructions from it. The mac setup file in this repo shows how the other context files must be used for the skill to work.

## Installation and Updates

Follow [../team/copilot-setup/copilot-setup-mac.md](../team/copilot-setup/copilot-setup-mac.md)
to install the shared setup on macOS. It contains copy commands, Finder steps,
and troubleshooting.

Personal files in `~/.copilot` are not updated by Git. When this repository's
setup changes, we'll all need to copy the revised files to our personal locations
and restart VS Code. 

## CAUTION: Avoid placing secrets, tokens, or credentials in any instruction, guide, or skill file.