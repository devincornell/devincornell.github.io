# Copilot Setup on macOS

This guide explains where to place the team's Copilot instructions, guide, and
skills on a Mac so GitHub Copilot in VS Code can find them.

## What Goes Where

| File | Destination on your Mac | Purpose |
| --- | --- | --- |
| `copilot-instructions.md` | `~/.copilot/copilot-instructions.md` | Always-on team rules |
| `CODING_GUIDE.md` | `~/.copilot/CODING_GUIDE.md` | Full engineering standard |
| `repository-documentation/SKILL.md` | `~/.copilot/skills/repository-documentation/SKILL.md` | Documentation skill |
| `api-evaluator/SKILL.md` | `~/.copilot/skills/api-evaluator/SKILL.md` | API evaluation skill |

`~` is your home folder, for example `/Users/<your-name>`.

Each skill file must be named exactly `SKILL.md`, and its folder name must match
the `name` field at the top of the file.

## Step 1: Show Hidden Folders in Finder

The `.copilot` folder starts with a dot, so Finder hides it by default.

1. Open Finder.
2. Press **Cmd + Shift + .** to show hidden files.

Press the same shortcut again to hide them later.

## Step 2: Create the Folders

Open Terminal and run:

```sh
mkdir -p ~/.copilot/skills/repository-documentation
mkdir -p ~/.copilot/skills/api-evaluator
```

`mkdir -p` creates any missing parent folders and does nothing if the folders
already exist.

## Step 3: Copy the Files

Copy the files from the shared folder or repository into the locations in the
table above. In Terminal, the commands look like this, with `<shared-folder>`
replaced by the folder where you saved the files:

```sh
cp "<shared-folder>/copilot-instructions.md" ~/.copilot/copilot-instructions.md
cp "<shared-folder>/CODING_GUIDE.md" ~/.copilot/CODING_GUIDE.md
cp "<shared-folder>/skills/repository-documentation/SKILL.md" ~/.copilot/skills/repository-documentation/SKILL.md
cp "<shared-folder>/skills/api-evaluator/SKILL.md" ~/.copilot/skills/api-evaluator/SKILL.md
```

Keep the quotes, because folder names can contain spaces.

If you prefer Finder, press **Cmd + Shift + G**, enter `~/.copilot`, and drag the
files into the matching folders.

## Step 4: Confirm the Setup

Check that the files are in place:

```sh
ls -la ~/.copilot ~/.copilot/skills/*
```

Then open VS Code and check Copilot Chat:

1. Type `/` in the chat box. `repository-documentation` and `api-evaluator`
   should appear.
2. Ask Copilot: "What skills do you have available?"

If the skills do not appear, quit and reopen VS Code.

## Team Repository Copies

The repository also contains team copies of these files:

- `.github/copilot-instructions.md` applies to everyone who works in the
  repository.
- `.github/skills/repository-documentation/SKILL.md` makes that skill available
  to everyone who works in the repository.

Changes made to the repository copies reach colleagues through Git. Copies in
`~/.copilot` do not update automatically, so recopy them after a change.

Keep `~/.copilot/CODING_GUIDE.md` identical to the repository's `CODING_GUIDE.md`.
If the two differ, the guide Copilot reads will not match the team's standard.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Skill does not appear after typing `/` | Wrong folder or file name | Check that the path is `~/.copilot/skills/<name>/SKILL.md` |
| Skill appears but Copilot ignores it | Frontmatter `name` differs from folder name | Make both names identical |
| Guide is not read | `CODING_GUIDE.md` is missing or in another folder | Place it at `~/.copilot/CODING_GUIDE.md` |
| Cannot see `.copilot` in Finder | Hidden files are hidden | Press Cmd + Shift + . |
| Changes do not take effect | Old copy still in place | Recopy the file and restart VS Code |

Do not store secrets, tokens, or real credentials in any of these files.
