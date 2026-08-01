# ZeroClaw integration

## Install the Skill

Keep the Python project in a fixed absolute directory. The installer
materializes the `<CLAWLEDGER>` placeholder in a temporary copy, audits it, and
installs it into the selected agent bundle:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File .\scripts\install_zeroclaw_skill.ps1 `
  -ConfigDir <ZEROCLAW_CONFIG_DIR> `
  -ZeroClawExe <PATH_TO_ZEROCLAW_EXE> `
  -Agent clawledger_demo
```

Alternatively, copy `skills/clawledger` into the selected agent's configured
skills directory and replace every placeholder manually. Install the reviewed
Python package if commands will be invoked outside the included wrapper:

```text
python -m pip install -e <CLAWLEDGER>
```

The Skill invokes a fixed Python script rather than `python -m`, matching
ZeroClaw's interpreter safety policy.

Start from `config.example.toml` for the tested agent, risk-profile, receipt,
model, and SOP structure. Replace every placeholder with an absolute path and
keep provider authentication and channel tokens outside the repository.

The tested risk profile is intentionally narrow: supervised,
workspace-only, no delegation, only Python on the command allow-list, and only
shell plus SOP control tools available to the agent. The stock v0.8.3 binary
audited this Skill successfully with all four files scanned.

## Install the SOP

Point `[sop].sops_dir` at this repository's `zeroclaw/sops` directory or copy
`sops/clawledger-anchor` into the configured directory.

The supplied SOP has both a daily UTC cron trigger and a manual trigger. Cron
execution requires `zeroclaw daemon` or `zeroclaw channel start`; standalone
gateway mode does not run the SOP maintenance tick.

Validate before enabling:

```text
zeroclaw sop validate clawledger-anchor
```

The procedure deliberately pauses before serving an anchor transaction. A
human chooses whether and when to open the signing Action.
