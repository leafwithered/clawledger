# ClawLedger skill-only plugin

This directory is a protocol-shaped ZeroClaw skill-only bundle. It uses the
official `capabilities = ["skill"]` manifest capability, so it deliberately
contains no WASM component and requests no permissions.

The production evidence in this repository uses the stock ZeroClaw v0.8.3
release and the compatible `zeroclaw/skills/clawledger` installation path. The
published v0.8.3 Windows binary does not include the optional `plugin` command;
use a plugin-enabled source build to install this bundle through the official
plugin host. Keeping both paths makes the custody and runtime boundary
explicit instead of claiming that the stock binary loads WASM plugins.

From a plugin-enabled ZeroClaw checkout:

```text
zeroclaw plugin install ./plugins/clawledger
```

The skill is then namespaced by the host as `plugin:clawledger/clawledger`.
Keep the ClawLedger source checkout at a fixed absolute path and install the
Python package as described in `zeroclaw/README.md` before invoking the skill.
