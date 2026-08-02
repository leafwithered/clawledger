# Devnet anchor handoff

This is the only remaining human-wallet step for the validated Telegram run.
Never provide a private key, seed phrase, keystore, wallet export, or signing
token to ClawLedger, ZeroClaw, an agent, or a submission form.

## Fixed checkpoint

```text
event_count = 200
root        = df25687ed19a6ec87a4ee025ce8d0d9b03e4809d6257a215865e0f17a4447e29
memo        = clawledger:v1:df25687ed19a6ec87a4ee025ce8d0d9b03e4809d6257a215865e0f17a4447e29:200
cluster     = devnet
```

The local manifest was independently verified before the Action was served.
If any of these values differ in the wallet preview, reject the transaction.

## Wallet review gate

1. Use a disposable wallet set to Solana devnet with devnet SOL only.
2. Open the locally served `/api/actions/anchor` through a compatible Action
   client.
3. Confirm the transaction has exactly one instruction for Solana's Memo
   program.
4. Confirm the instruction data is the exact Memo above.
5. Confirm there is no SOL transfer, token transfer, account creation, extra
   signer, or additional instruction.
6. Only then approve signing and broadcasting in the wallet.

ClawLedger constructs the unsigned transaction but cannot sign or broadcast
it. The wallet remains the sole signer.

## Finalized verification

Copy only the public devnet transaction signature and run:

```powershell
$env:PYTHONPATH = "src"
python -m clawledger verify-anchor `
  --manifest <LOCAL_200_EVENT_MANIFEST> `
  --signature <DEVNET_SIGNATURE> `
  --rpc https://api.devnet.solana.com `
  --write-signature
```

`--write-signature` is allowed only when the command first reports
`"valid": true`. The public explorer URL is:

```text
https://explorer.solana.com/tx/<DEVNET_SIGNATURE>?cluster=devnet
```

Capture the wallet preview, success state, verifier output, and Explorer page
for the final video. Do not show the wallet recovery phrase, browser extension
vault, Telegram token, model authentication, or raw audit trace.
