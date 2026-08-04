# Operator submission checklist

This checklist records the completed wallet work and the remaining public
account actions. ClawLedger intentionally never automates wallet custody.

Submission deadline: **2026-08-07 10:59 Asia/Shanghai**

## 0. Connect a real channel and model — completed

- Preferred: Telegram; Discord is also acceptable.
- Configure the bot token through ZeroClaw's encrypted config surface. Never
  commit it and never expose it in the video or submission form.
- Bind only the operator's user/chat identity, then run `zeroclaw channel doctor`.
- Configure a model provider locally. Existing Codex authentication may be
  imported only with the operator's explicit approval.

## 1. Validate with the stock ZeroClaw binary — completed

```powershell
zeroclaw skills audit .\zeroclaw\skills\clawledger
zeroclaw config set sop.sops_dir <ABSOLUTE_PATH_TO_REPO>\zeroclaw\sops
zeroclaw sop validate clawledger-anchor
```

These commands have passed with the SHA-256-verified v0.8.3 binary. Re-run them
from the public clean clone and save the terminal output for the video.

## 2. Create a disposable devnet anchor — completed

The final 200-event Telegram checkpoint was anchored after the exact preview
checks in `docs/ANCHOR_HANDOFF.md`. The finalized public evidence is stored in
`docs/FINALIZED_ANCHOR.json`.

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

## 3. Record the demo — completed

Follow `docs/DEMO.md`. Keep the recording under three minutes and show:

- the private JSONL fixture locally;
- checkpoint creation and local verification;
- wallet review and explicit human signature;
- the finalized Solana transaction;
- tamper detection after changing one event.

## 4. Publish and submit

- Public repository: `https://github.com/leafwithered/clawledger`.
- Demo: `https://github.com/leafwithered/clawledger/blob/main/docs/clawledger-demo.mp4`.
- Explorer: `https://explorer.solana.com/tx/N3mzTr1YAWw84b2irzd9Cr4cmPd9JHZSmZaUq3PPTr9xYPLfbJZZEqCMP417164U6exTiBA9kjXZ7pf4PHSQviU?cluster=devnet`.
- Publish the build-in-public X post.
- Post the showcase in ZeroClaw Discord `#solana-bounty`.
- Use the reviewed copy in `docs/SHOWCASE_POST.md`, replacing only the
  showcase-post link.
- Submit the required video and supporting-material links on Superteam Earn.
- Re-run every command in `docs/VALIDATION.md` from a clean clone.
