# Operator submission checklist

This checklist records the completed validation, publication, and submission
work. ClawLedger intentionally never automates wallet custody.

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

## 2. Create and verify a disposable devnet anchor — completed

The final 200-event Telegram checkpoint was finalized with a disposable devnet
signer for chain verification. The public evidence is stored in
`docs/FINALIZED_ANCHOR.json`. This record is not claimed as a Phantom UI
approval; the local Action remains unsigned until an operator reviews it.

1. Use a wallet containing devnet SOL only.
2. Start the Action server with the command in `docs/DEMO.md`.
3. Review that the transaction contains exactly one Memo instruction.
4. If reproducing the wallet flow, review, sign, and broadcast from the wallet.
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
- the unsigned wallet-review boundary and strict transaction shape;
- the finalized Solana transaction;
- tamper detection after changing one event.

## 4. Publish and submit — completed

- Public repository: `https://github.com/leafwithered/clawledger`.
- Demo: `https://youtu.be/CfBIr49QbJI` (GitHub MP4 backup:
  `https://github.com/leafwithered/clawledger/blob/main/docs/clawledger-demo.mp4`).
- Explorer: `https://explorer.solana.com/tx/N3mzTr1YAWw84b2irzd9Cr4cmPd9JHZSmZaUq3PPTr9xYPLfbJZZEqCMP417164U6exTiBA9kjXZ7pf4PHSQviU?cluster=devnet`.
- Published X showcase: `https://x.com/leafmyx/status/2084590054178181156`.
- Published ZeroClaw Discord `#solana-bounty` showcase:
  https://discord.com/channels/1472154792351760419/1527427886410109029/1534230225951523038
- The reviewed publication copy remains in `docs/SHOWCASE_POST.md`.
- Superteam Earn contains the Discord showcase as the primary submission plus
  the public video, one-pager, repository, release, devnet proof, and validation
  links.
- The validation commands in `docs/VALIDATION.md` were re-run on 2026-08-05.
