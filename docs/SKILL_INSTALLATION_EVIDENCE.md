# Official ZeroClaw Skill Installation Evidence

Last validated: 2026-08-05

The stock Windows release used for validation is `zeroclaw 0.8.3`. The
following commands were run against a fresh temporary `--config-dir`:

```text
zeroclaw agents create clawledger_demo
zeroclaw skills bundle add clawledger
zeroclaw skills install ./plugins/clawledger/skills/clawledger --bundle clawledger
zeroclaw skills audit clawledger
zeroclaw config set --no-interactive agents.clawledger_demo.skill_bundles clawledger
zeroclaw skills list --agent clawledger_demo
```

Observed results:

- the local Skill installed and passed the security audit;
- the bundle contained `clawledger v0.1.3`;
- `skills list --agent clawledger_demo` showed ClawLedger as loaded by that
  agent;
- the Skill used the real reviewed wrapper and the same Python verifier as the
  production validation path.

The release binary reports `No TEST.sh found for skill 'clawledger'`. A trial
`TEST.sh` was intentionally not kept: the same v0.8.3 security audit rejects
script-like Skill files with `script-like files are blocked by skill security
policy`, which would make the official installation path fail. The repository
instead validates the Skill wrapper through the 19-test Python suite, the
submission-validation CI, the ZeroClaw Skill audit, and SOP validation.
