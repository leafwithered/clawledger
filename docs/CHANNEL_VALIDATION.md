# Real Telegram channel validation

Validation date: 2026-08-02 (Asia/Shanghai)

This was a real Telegram-to-ZeroClaw run, not a mocked transcript. A Telegram
bot was configured through ZeroClaw's encrypted configuration surface, the
operator identity was explicitly bound, and the official ZeroClaw v0.8.3
daemon reported the channel healthy.

## Checkpoint result

The operator asked the agent to checkpoint an exact local trace path using the
reviewed ClawLedger Skill. Each shell tool call contained one explicit Python
command: no variables, discovery, pipes, redirection, or chaining.

The first attempt used the live rolling trace. New runtime events displaced
the original range before verification, so verification failed closed. This
is the intended behavior; the root is never reported as valid for a changed
source range.

The operator then named an exact stable snapshot path. ZeroClaw created and
verified the checkpoint, and Telegram returned:

```text
event_count: 200
root: df25687ed19a6ec87a4ee025ce8d0d9b03e4809d6257a215865e0f17a4447e29
```

An independent local process verified the same manifest against the same
snapshot:

```json
{
  "valid": true,
  "reason": "ok",
  "expected_root": "df25687ed19a6ec87a4ee025ce8d0d9b03e4809d6257a215865e0f17a4447e29",
  "actual_root": "df25687ed19a6ec87a4ee025ce8d0d9b03e4809d6257a215865e0f17a4447e29",
  "event_count": 200
}
```

## Credential and daemon health

After rotating the Telegram credential, the new value was validated with
Telegram's read-only bot identity endpoint, written through ZeroClaw's
encrypted config command, and removed from the clipboard. `channel doctor`
reported one healthy Telegram channel and zero unhealthy channels. A fresh
Telegram message then traversed the restarted daemon and returned the unique
reply `ROTATION_HEALTHY_3`.

## Privacy boundary

The bot token, Telegram account identifiers, model authentication, raw trace,
and uncensored screenshots are not committed. The final demo masks the local
path and avatar column while retaining the non-secret event count, Merkle root,
validation outcome, and health result.
