# Operator submission checklist

These actions require the operator's wallet or public accounts. ClawLedger
intentionally does not automate them.

Submission deadline: **2026-08-07 10:59 Asia/Shanghai**

## 0. Connect a real channel and model

- Preferred: Telegram; Discord is also acceptable.
- Configure the bot token through ZeroClaw's encrypted config surface. Never
  commit it and never expose it in the video or submission form.
- Bind only the operator's user/chat identity, then run `zeroclaw channel doctor`.
- Configure a model provider locally. Existing Codex authentication may be
  imported only with the operator's explicit approval.

## 1. Validate with the stock ZeroClaw binary

```powershell
zeroclaw skills audit .\zeroclaw\skills\clawledger
zeroclaw config set sop.sops_dir <ABSOLUTE_PATH_TO_REPO>\zeroclaw\sops
zeroclaw sop validate clawledger-anchor
```

These commands have passed with the SHA-256-verified v0.8.3 binary. Re-run them
from the public clean clone and save the terminal output for the video.

## 2. Create a disposable devnet anchor

For the final 200-event Telegram checkpoint, follow the exact values and
preview checks in `docs/ANCHOR_HANDOFF.md`.

1. Use a wallet containing devnet SOL only.
2. Start the Action server with the command in `docs/DEMO.md`.
3. Review that the transaction contains exactly one Memo instruction.
4. Sign and broadcast from the wallet.
5. Copy the finalized signature and run:

```powershell
python -m clawledger verify-anchor `
  --manifest sample-checkpoint.json `
  --signature <DEVNET_SIGNATURE> `
  --rpc https://api.devnet.solana.com
```

Do not use a mainnet wallet for the demo.

## 3. Record the demo

Follow `docs/DEMO.md`. Keep the recording under three minutes and show:

- the private JSONL fixture locally;
- checkpoint creation and local verification;
- wallet review and explicit human signature;
- the finalized Solana transaction;
- tamper detection after changing one event.

## 4. Publish and submit

- Public repository: `https://github.com/leafwithered/clawledger`.
- Upload the demo and replace `<VIDEO_URL>`.
- Add the explorer transaction and replace `<SOLANA_EXPLORER_URL>`.
- Add the build-in-public post and replace `<X_POST_URL>`.
- Post the showcase in ZeroClaw Discord `#solana-bounty`.
- Submit the required video and supporting-material links on Superteam Earn.
- Re-run every command in `docs/VALIDATION.md` from a clean clone.
