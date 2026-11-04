# RB-JOB-RESTART — Restarting Failed Batch Jobs (SYNTHETIC)

## Principles
Restart from the job's **last checkpoint**, never from the top.
Restarting a posting job from the top re-applies records it already
wrote: balances are double-posted and keyed writes fail with file
status 22 (duplicate key). A checkpoint restart is always safe; a
from-the-top restart is safe only for read-only jobs.

## Checkpoints
- **JOBLD01** checkpoints every 10,000 records loaded to TXNFILE.
- **JOBCALC02** checkpoints per account-range processed.
- **JOBPOST03** checkpoints every 5,000 records posted to ACCTFILE.
- **JOBRPT04** is read-only and may restart from the top.

## Procedure
1. Fix the root cause first (bad data, file definition, or abend —
   see RB-ABEND-S0C7 and RB-VSAM-STATUS).
2. Confirm the checkpoint dataset shows the last committed checkpoint.
3. Resubmit the job with the RESTART parameter set to that checkpoint.
4. Watch the first checkpoint after restart commit before walking away.

## Verification After Restart
Compare the job's record counts (read, written, rejected) against the
extract totals, and confirm ACCT-BALANCE totals in JOBRPT04 output
match the pre-failure run's control totals. A restart is not done when
the job ends — it is done when the counts reconcile.
